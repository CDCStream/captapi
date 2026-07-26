import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { getServiceClient } from "@/lib/supabase/admin";

const INITIAL_CREDITS = 100;
const ANON_TOOL_COOKIE = "captapi_tool_free";
const NO_WELCOME_COOKIE = "captapi_no_welcome";
const ANON_DAILY_LIMIT = 3;

const DISPOSABLE_DOMAINS = new Set([
  "web-library.net",
  "mailinator.com",
  "guerrillamail.com",
  "tempmail.com",
  "throwaway.email",
  "temp-mail.org",
  "10minutemail.com",
  "trashmail.com",
  "yopmail.com",
  "sharklasers.com",
  "guerrillamailblock.com",
  "grr.la",
  "dispostable.com",
  "mailnesia.com",
  "maildrop.cc",
  "fakeinbox.com",
  "mailcatch.com",
  "tempail.com",
  "tempr.email",
  "discard.email",
  "tmpmail.net",
  "tmpmail.org",
  "emailondeck.com",
  "mohmal.com",
  "getnada.com",
  "burnermail.io",
  "mailsac.com",
  "inboxkitten.com",
  "33mail.com",
  "mytemp.email",
  "spam4.me",
  "tmail.ws",
  "mt2015.com",
  "jnxjn.com",
  "mailforspam.com",
  "mvrht.net",
]);

function isDisposableEmail(email: string): boolean {
  const domain = email.split("@")[1]?.toLowerCase();
  if (!domain) return false;
  return DISPOSABLE_DOMAINS.has(domain);
}

function parseCookie(cookieHeader: string | null, name: string): string | null {
  if (!cookieHeader) return null;
  const match = cookieHeader.match(new RegExp(`(?:^|;\\s*)${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

/** Free-tool converters: exhausted daily tries or came from /signup?from=tools. */
function shouldSkipWelcome(
  request: Request,
  nextPath: string,
  fromParam: string | null,
): boolean {
  if (fromParam === "tools") return true;
  // Signup from tools sets next=/dashboard/billing
  if (nextPath.startsWith("/dashboard/billing")) return true;
  const cookieHeader = request.headers.get("cookie");
  if (parseCookie(cookieHeader, NO_WELCOME_COOKIE) === "1") return true;
  const tries = parseInt(parseCookie(cookieHeader, ANON_TOOL_COOKIE) || "0", 10);
  if (tries >= ANON_DAILY_LIMIT) return true;
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

/**
 * Zero the trigger's default 100 for free-tool converters (no welcome bonus).
 * Only touches brand-new accounts that still hold the unspent welcome pile —
 * never wipe an existing user's balance if they later hit this callback.
 */
async function revokeWelcomeCredits(userId: string, createdAt: string | undefined) {
  const sb = getServiceClient();
  if (!sb) return;

  if (createdAt) {
    const ageMs = Date.now() - new Date(createdAt).getTime();
    if (Number.isFinite(ageMs) && ageMs > 60 * 60 * 1000) return;
  }

  const { data } = await sb
    .from("credit_balances")
    .select("subscription_credits, topup_credits, plan")
    .eq("user_id", userId)
    .single();

  if (!data) return;
  const sub = data.subscription_credits || 0;
  const top = data.topup_credits || 0;
  const plan = (data.plan || "free").toLowerCase();
  if (top > 0 || sub > INITIAL_CREDITS || plan !== "free") return;

  await sb
    .from("credit_balances")
    .update({ subscription_credits: 0 })
    .eq("user_id", userId);

  await sb
    .from("credit_transactions")
    .delete()
    .eq("user_id", userId)
    .eq("type", "welcome");
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
      const skipWelcome = shouldSkipWelcome(request, next, fromParam);

      if (user?.email && user?.email_confirmed_at) {
        if (skipWelcome) {
          await revokeWelcomeCredits(user.id, user.created_at);
          // Landing flag opens the buy-credits pricing modal on the dashboard.
          next = "/dashboard/billing?from=tools";
        } else {
          await grantWelcomeCredits(user.id, user.email);
        }
      } else if (skipWelcome) {
        // OAuth may confirm immediately; password signup confirms via this link.
        // If somehow unconfirmed + skip, still send them to billing after.
        next = "/dashboard/billing?from=tools";
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
      if (skipWelcome) clearToolCookies(response);
      return response;
    }
    return NextResponse.redirect(
      `${origin}/login?error=${encodeURIComponent(exchangeError.message)}`,
    );
  }

  return NextResponse.redirect(`${origin}/login?error=missing_code`);
}
