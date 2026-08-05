import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { getServiceClient } from "@/lib/supabase/admin";
import { ensureCreditBalance } from "@/lib/supabase/ensure-account";
import { isDisposableEmail } from "@/lib/disposable-email";

const INITIAL_CREDITS = 100;
const ANON_TOOL_COOKIE = "captapi_tool_free";
const NO_WELCOME_COOKIE = "captapi_no_welcome";

async function rejectDisposableSignup(userId: string, origin: string) {
  const admin = getServiceClient();
  if (admin) {
    await admin.auth.admin.deleteUser(userId);
  }
  const supabase = await createClient();
  await supabase.auth.signOut();
  return NextResponse.redirect(
    `${origin}/signup?error=${encodeURIComponent(
      "Disposable email addresses are not allowed. Please use a real email.",
    )}`,
  );
}

function parseCookie(cookieHeader: string | null, name: string): string | null {
  if (!cookieHeader) return null;
  const match = cookieHeader.match(new RegExp(`(?:^|;\\s*)${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

/** Free-tool converters — analytics / billing landing only (still get welcome credits). */
function isFromTools(
  request: Request,
  nextPath: string,
  fromParam: string | null,
  userMeta?: Record<string, unknown> | null,
): boolean {
  if (fromParam === "tools") return true;
  if (userMeta?.from_tools === true || userMeta?.from_tools === "true") return true;
  if (nextPath.startsWith("/dashboard/billing")) return true;
  const cookieHeader = request.headers.get("cookie");
  if (parseCookie(cookieHeader, NO_WELCOME_COOKIE) === "1") return true;
  const tries = parseInt(parseCookie(cookieHeader, ANON_TOOL_COOKIE) || "0", 10);
  if (tries >= 1) return true;
  return false;
}

async function grantWelcomeCredits(userId: string, email: string) {
  if (isDisposableEmail(email)) return;

  const sb = getServiceClient();
  if (!sb) return;

  const { data } = await sb
    .from("credit_balances")
    .select("subscription_credits, topup_credits")
    .eq("user_id", userId)
    .single();

  if (!data) return;

  const total = (data.subscription_credits || 0) + (data.topup_credits || 0);
  if (total > 0) return;

  await sb
    .from("credit_balances")
    .update({ subscription_credits: INITIAL_CREDITS })
    .eq("user_id", userId);

  await sb.from("credit_transactions").insert({
    user_id: userId,
    type: "welcome",
    amount: INITIAL_CREDITS,
    description: "Welcome bonus (email verified)",
  });
}

function clearToolCookies(response: NextResponse) {
  response.cookies.set(NO_WELCOME_COOKIE, "", { path: "/", maxAge: 0 });
  response.cookies.set(ANON_TOOL_COOKIE, "", { path: "/", maxAge: 0 });
  response.cookies.set("captapi_tool_tt", "", { path: "/", maxAge: 0 });
}

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const error = searchParams.get("error_description") || searchParams.get("error");

  let next = searchParams.get("next") || "/dashboard";
  if (!next.startsWith("/")) {
    next = "/dashboard";
  }
  const fromParam = searchParams.get("from");

  if (error) {
    return NextResponse.redirect(
      `${origin}/login?error=${encodeURIComponent(error)}`,
    );
  }

  if (code) {
    const supabase = await createClient();
    const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);
    if (!exchangeError) {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (user?.email && isDisposableEmail(user.email)) {
        return rejectDisposableSignup(user.id, origin);
      }

      const fromTools = isFromTools(
        request,
        next,
        fromParam,
        (user?.user_metadata as Record<string, unknown> | null) ?? null,
      );

      if (user?.id) {
        // Recreate credit_balances if Auth user survived a public-schema wipe.
        await ensureCreditBalance(user.id);
      }

      // Free Tools converters get the same 100 lifetime welcome credits.
      if (user?.email && user?.email_confirmed_at) {
        await grantWelcomeCredits(user.id, user.email);
      }

      if (fromTools) {
        next = "/dashboard/billing?from=tools";
      }

      // New accounts (OAuth or email confirm) → client fires Ads signup conversion.
      const createdMs = user?.created_at
        ? Date.now() - new Date(user.created_at).getTime()
        : Number.POSITIVE_INFINITY;
      if (Number.isFinite(createdMs) && createdMs < 60 * 60 * 1000) {
        const sep = next.includes("?") ? "&" : "?";
        next = `${next}${sep}ads_signup=1`;
      }

      const forwardedHost = request.headers.get("x-forwarded-host");
      const isLocalEnv = process.env.NODE_ENV === "development";
      let redirectUrl: string;
      if (isLocalEnv) {
        redirectUrl = `${origin}${next}`;
      } else if (forwardedHost) {
        redirectUrl = `https://${forwardedHost}${next}`;
      } else {
        redirectUrl = `${origin}${next}`;
      }

      const response = NextResponse.redirect(redirectUrl);
      if (fromTools) clearToolCookies(response);
      return response;
    }
    return NextResponse.redirect(
      `${origin}/login?error=${encodeURIComponent(exchangeError.message)}`,
    );
  }

  return NextResponse.redirect(`${origin}/login?error=missing_code`);
}
