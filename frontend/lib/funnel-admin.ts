/** Internal funnel admin helpers (server-only allowlist). */

/**
 * Accounts hidden from the funnel: owner test accounts, the high-volume loyal
 * user, and the tools@captapi.com service account for public free tools.
 * Env vars can add more ids; they never remove these defaults.
 * (Owner ids stay on the admin allowlist so they can still open this page.)
 */
const DEFAULT_FUNNEL_EXCLUDE_USER_IDS = [
  "3f48e876-2044-465a-a517-81a9b34fb830",
  "111dc024-18cf-4a81-8041-827e1c684a41",
  // Owner accounts — keep out of funnel metrics
  "ac4caf34-7fc8-4384-8fdc-60abdd4225ee", // fuatsezer199696@gmail.com
  "adb1b0ea-a48a-43a5-9a3d-334b59b82f1a", // fuats9232@gmail.com
  "62d7b827-28a5-4f6c-bef5-6b085f095a70", // fuatsezer22@gmail.com
];

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

export function funnelExcludeUserIds(): string[] {
  return [
    ...new Set([
      ...DEFAULT_FUNNEL_EXCLUDE_USER_IDS.map((id) => id.toLowerCase()),
      ...parseIdList(process.env.FUNNEL_EXCLUDE_USER_ID),
      ...parseIdList(process.env.FUNNEL_EXCLUDE_USER_IDS),
      ...parseIdList(process.env.RESPONSE_SAMPLE_EXCLUDE_USER_IDS),
    ]),
  ];
}

export function isFunnelExcluded(userId: string | null | undefined): boolean {
  if (!userId) return false;
  return funnelExcludeUserIds().includes(userId.trim().toLowerCase());
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
