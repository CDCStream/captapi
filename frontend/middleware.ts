import { type NextRequest, NextResponse } from "next/server";
import { type CookieOptions, createServerClient } from "@supabase/ssr";
import { ensureCreditBalance, hasCreditBalance } from "@/lib/supabase/ensure-account";

type CookieToSet = { name: string; value: string; options: CookieOptions };

function hasSupabaseAuthCookie(request: NextRequest): boolean {
  return request.cookies
    .getAll()
    .some(
      (c) =>
        c.name.includes("-auth-token") ||
        (c.name.startsWith("sb-") && c.name.includes("auth")),
    );
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
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.search = "";
    url.searchParams.set("reason", reason);
    if (redirectPath?.startsWith("/")) {
      url.searchParams.set("redirect", redirectPath);
    }
    return copyAuthCookies(NextResponse.redirect(url));
  };

  // Stale session: browser still has the JWT cookie but Auth user is gone
  // (DB wipe / deleted account). Clear cookies so /login does not bounce
  // the visitor into a ghost dashboard session.
  if (authCookie && !user) {
    return clearSessionToLogin("session-expired", path.startsWith("/dashboard") ? path : undefined);
  }

  const isProtected = path.startsWith("/dashboard");
  const isAuthPage = path === "/login" || path === "/signup";

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
