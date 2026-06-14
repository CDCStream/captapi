import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { getServiceClient } from "@/lib/supabase/admin";

const INITIAL_CREDITS = 100;

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

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const error = searchParams.get("error_description") || searchParams.get("error");

  let next = searchParams.get("next") || "/dashboard";
  if (!next.startsWith("/")) {
    next = "/dashboard";
  }

  if (error) {
    return NextResponse.redirect(
      `${origin}/login?error=${encodeURIComponent(error)}`,
    );
  }

  if (code) {
    const supabase = await createClient();
    const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);
    if (!exchangeError) {
      const { data: { user } } = await supabase.auth.getUser();
      if (user?.email && user?.email_confirmed_at) {
        await grantWelcomeCredits(user.id, user.email);
      }

      const forwardedHost = request.headers.get("x-forwarded-host");
      const isLocalEnv = process.env.NODE_ENV === "development";
      if (isLocalEnv) {
        return NextResponse.redirect(`${origin}${next}`);
      }
      if (forwardedHost) {
        return NextResponse.redirect(`https://${forwardedHost}${next}`);
      }
      return NextResponse.redirect(`${origin}${next}`);
    }
    return NextResponse.redirect(
      `${origin}/login?error=${encodeURIComponent(exchangeError.message)}`,
    );
  }

  return NextResponse.redirect(`${origin}/login?error=missing_code`);
}
