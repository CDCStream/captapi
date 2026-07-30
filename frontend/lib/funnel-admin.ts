/** Internal funnel admin helpers (server-only allowlist). */

export const FUNNEL_EXCLUDE_USER_ID =
  process.env.FUNNEL_EXCLUDE_USER_ID ||
  process.env.RESPONSE_SAMPLE_EXCLUDE_USER_IDS?.split(",")[0]?.trim() ||
  "3f48e876-2044-465a-a517-81a9b34fb830";

export function funnelAdminIds(): string[] {
  const raw = process.env.FUNNEL_ADMIN_USER_IDS || "";
  return raw
    .split(/[\s,]+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export function isFunnelAdmin(userId: string | null | undefined): boolean {
  if (!userId) return false;
  const ids = funnelAdminIds();
  // Empty allowlist = nobody (safe default).
  return ids.includes(userId);
}

export function funnelSinceIso(days = 14): string {
  return new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
}
