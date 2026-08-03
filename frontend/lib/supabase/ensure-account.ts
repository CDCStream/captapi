import { getServiceClient } from "@/lib/supabase/admin";

/**
 * Ensure ``public.credit_balances`` exists for an Auth user.
 *
 * The signup trigger creates this row on ``auth.users`` insert. After a DB
 * wipe (or a failed trigger) the Auth user can still hold a valid JWT while
 * the app row is gone — recreate it with the free-plan defaults.
 */
export async function ensureCreditBalance(userId: string): Promise<boolean> {
  if (!userId) return false;
  const sb = getServiceClient();
  if (!sb) return false;

  const { data } = await sb
    .from("credit_balances")
    .select("user_id")
    .eq("user_id", userId)
    .maybeSingle();
  if (data?.user_id) return true;

  // Match signup trigger (0008): 0 until email verify grants welcome credits.
  const { error } = await sb.from("credit_balances").upsert(
    {
      user_id: userId,
      subscription_credits: 0,
      topup_credits: 0,
      plan: "free",
    },
    { onConflict: "user_id", ignoreDuplicates: true },
  );
  return !error;
}

export async function hasCreditBalance(userId: string): Promise<boolean | null> {
  /** ``null`` = could not check (no service role). */
  if (!userId) return false;
  const sb = getServiceClient();
  if (!sb) return null;

  const { data, error } = await sb
    .from("credit_balances")
    .select("user_id")
    .eq("user_id", userId)
    .maybeSingle();
  if (error) return null;
  return Boolean(data?.user_id);
}
