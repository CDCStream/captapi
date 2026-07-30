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

  const clearSessionToLogin = async (reason: string, redirectPath?: string) => {
    try {
      await supabase.auth.signOut();
    } catch {
      // Best-effort — still redirect and attach whatever cookie clears we got.
    }
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

  // Stale session: browser still has the JWT cookie but Auth user is gone.
  if (authCookie && !user) {
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
    url.searchParams.set("redirect", path);
    return NextResponse.redirect(url);
  }

  if (isAuthPage && user) {
    const url = request.nextUrl.clone();
    url.pathname = "/dashboard";
    url.search = "";
    return NextResponse.redirect(url);
  }

  return supabaseResponse;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};
