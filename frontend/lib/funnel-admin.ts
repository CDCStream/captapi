/** Internal funnel admin helpers (server-only allowlist). */

export const FUNNEL_EXCLUDE_USER_ID =
  process.env.FUNNEL_EXCLUDE_USER_ID ||
  process.env.RESPONSE_SAMPLE_EXCLUDE_USER_IDS?.split(",")[0]?.trim() ||
  "3f48e876-2044-465a-a517-81a9b34fb830";

/** Always allowed owner accounts. Env can add more; it never removes these. */
const DEFAULT_FUNNEL_ADMIN_USER_IDS = [
  "ac4caf34-7fc8-4384-8fdc-60abdd4225ee",
];

function parseIdList(raw: string | undefined): string[] {
  return (raw || "")
    .split(/[\s,]+/)
    .map((s) => s.trim().toLowerCase())
    .filter(Boolean);
}

export function funnelAdminIds(): string[] {
  return [
    ...new Set([
      ...DEFAULT_FUNNEL_ADMIN_USER_IDS.map((id) => id.toLowerCase()),
      ...parseIdList(process.env.FUNNEL_ADMIN_USER_IDS),
    ]),
  ];
}

export function isFunnelAdmin(userId: string | null | undefined): boolean {
  if (!userId) return false;
  return funnelAdminIds().includes(userId.trim().toLowerCase());
}

export function funnelSinceIso(days = 14): string {
  return new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
}
