import { type NextRequest, NextResponse } from "next/server";
import { type CookieOptions, createServerClient } from "@supabase/ssr";
import { ensureCreditBalance, hasCreditBalance } from "@/lib/supabase/ensure-account";

type CookieToSet = { name: string; value: string; options: CookieOptions };

function isAuthTokenCookie(name: string): boolean {
  // Real session cookies look like sb-<ref>-auth-token[.N]. Ignore PKCE
  // leftovers such as *-auth-token-code-verifier which are not sessions.
  if (name.includes("code-verifier")) return false;
  return name.includes("-auth-token");
}

function hasSupabaseAuthCookie(request: NextRequest): boolean {
  return request.cookies
    .getAll()
    .some((c) => isAuthTokenCookie(c.name) && Boolean(c.value) && c.value.length > 20);
}

/** Expire any Supabase auth cookies on the response (belt-and-suspenders). */
function expireAuthCookies(request: NextRequest, response: NextResponse) {
  for (const cookie of request.cookies.getAll()) {
    const n = cookie.name;
    if (isAuthTokenCookie(n) || (n.startsWith("sb-") && n.includes("auth"))) {
      response.cookies.set(n, "", {
        path: "/",
        maxAge: 0,
        expires: new Date(0),
      });
    }
  }
}

/**
 * True only when Auth is certain the session is dead.
 * Network blips / 5xx / refresh races must NOT wipe cookies — that was kicking
 * freshly verified users out of /dashboard ~30–60s after api_key_created.
 */
function isDefinitiveAuthFailure(error: { message?: string; code?: string; status?: number } | null): boolean {
  if (!error) {
    // Cookie present but getUser returned null with no error → cookie is empty/junk.
    return true;
  }
  const code = (error.code || "").toLowerCase();
  const msg = (error.message || "").toLowerCase();
  const status = error.status;
  const definitiveCodes = [
    "refresh_token_not_found",
    "refresh_token_already_used",
    "invalid_refresh_token",
    "session_not_found",
    "user_not_found",
    "user_banned",
    "bad_jwt",
    "invalid_jwt",
    "session_expired",
  ];
  if (definitiveCodes.some((c) => code === c || code.includes(c))) return true;
  if (
    msg.includes("refresh token") ||
    msg.includes("session missing") ||
    msg.includes("invalid jwt") ||
    msg.includes("jwt expired") ||
    msg.includes("user not found")
  ) {
    return true;
  }
  // GoTrue auth rejection — not a transport failure.
  if (status === 401 || status === 403) return true;
  return false;
}

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet: CookieToSet[]) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options),
          );
        },
      },
    },
  );

  const {
    data: { user },
    error: userError,
  } = await supabase.auth.getUser();
  const path = request.nextUrl.pathname;
  const authCookie = hasSupabaseAuthCookie(request);
  const isProtected = path.startsWith("/dashboard");
  const isAuthPage = path === "/login" || path === "/signup";

  const copyAuthCookies = (target: NextResponse) => {
    supabaseResponse.cookies.getAll().forEach((cookie) => {
      target.cookies.set(cookie.name, cookie.value);
    });
    return target;
  };

  /** Clear cookies locally — do NOT call Auth signOut (revokes refresh tokens). */
  const clearSessionToLogin = (reason: string, redirectPath?: string) => {
    // Already on login/signup: clear cookies in place — never redirect to self
    // (that caused ERR_TOO_MANY_REDIRECTS when the JWT cookie was stale).
    if (isAuthPage) {
      expireAuthCookies(request, supabaseResponse);
      return supabaseResponse;
    }
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.search = "";
    url.searchParams.set("reason", reason);
    if (redirectPath?.startsWith("/")) {
      url.searchParams.set("redirect", redirectPath);
    }
    const res = copyAuthCookies(NextResponse.redirect(url));
    expireAuthCookies(request, res);
    return res;
  };

  // Cookie present but no user: only wipe when Auth is definitive. Transient
  // getUser failures (network / 5xx / refresh race) used to hard-signOut and
  // end the onboarding journey mid-dashboard.
  if (authCookie && !user) {
    if (!isDefinitiveAuthFailure(userError)) {
      // Leave cookies alone. Soft-bounce protected routes so the client can retry
      // without destroying the session; public pages just continue.
      if (isProtected) {
        const url = request.nextUrl.clone();
        url.pathname = "/login";
        url.search = "";
        url.searchParams.set("reason", "auth-retry");
        url.searchParams.set("redirect", `${path}${request.nextUrl.search}`);
        return copyAuthCookies(NextResponse.redirect(url));
      }
      return supabaseResponse;
    }
    return clearSessionToLogin(
      "session-expired",
      path.startsWith("/dashboard") ? path : undefined,
    );
  }

  // Auth user exists but app row was wiped — heal, or force a clean login.
  // Only on dashboard / auth pages so marketing traffic stays cheap.
  if (user && (isProtected || isAuthPage)) {
    const exists = await hasCreditBalance(user.id);
    if (exists === false) {
      const healed = await ensureCreditBalance(user.id);
      if (!healed) {
        return clearSessionToLogin("account-missing");
      }
    }
  }

  if (isProtected && !user) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    // Keep query string (e.g. ?endpoint=facebook-comments) so deep-links survive login.
    const redirectTo = `${path}${request.nextUrl.search}`;
    url.search = "";
    url.searchParams.set("redirect", redirectTo);
    return NextResponse.redirect(url);
  }

  if (isAuthPage && user) {
    const requested = request.nextUrl.searchParams.get("redirect");
    const next =
      requested && requested.startsWith("/") && !requested.startsWith("//")
        ? requested
        : "/dashboard";
    const url = request.nextUrl.clone();
    // Support deep-links like /dashboard/playground?endpoint=facebook-comments
    const [pathname, qs] = next.split("?");
    url.pathname = pathname || "/dashboard";
    url.search = qs ? `?${qs}` : "";
    return NextResponse.redirect(url);
  }

  return supabaseResponse;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};
