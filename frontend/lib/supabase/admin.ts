import { createClient, type SupabaseClient } from "@supabase/supabase-js";

// Singleton service-role client for server-side use only (webhooks, blog
// reads/writes). NEVER import this from a client component — it uses the
// service role key which bypasses RLS.
let cached: SupabaseClient | null | undefined;

/**
 * Returns a service-role Supabase client, or null when the required env vars
 * are missing so callers can degrade gracefully instead of throwing.
 */
export function getServiceClient(): SupabaseClient | null {
  if (cached !== undefined) return cached;

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url || !key) {
    cached = null;
    return null;
  }

  cached = createClient(url, key, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
  return cached;
}
