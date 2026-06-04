// Thin HTTP client around the Captapi REST API + small TTY helpers.
import { loadConfig } from "./config.js";

export const VERSION = "0.1.0";

const useColor = process.stdout.isTTY && !process.env.NO_COLOR;
const wrap = (code: string) => (s: string) =>
  useColor ? `\x1b[${code}m${s}\x1b[0m` : s;

export const c = {
  bold: wrap("1"),
  dim: wrap("2"),
  red: wrap("31"),
  green: wrap("32"),
  yellow: wrap("33"),
  cyan: wrap("36"),
};

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: unknown,
    public hint = "",
  ) {
    super(`HTTP ${status}`);
  }
}

function authHeaders(apiKey: string): Record<string, string> {
  return {
    Authorization: `Bearer ${apiKey}`,
    Accept: "application/json",
    "User-Agent": `captapi-cli/${VERSION}`,
  };
}

export function requireKey(): { apiKey: string; baseUrl: string } {
  const { apiKey, baseUrl } = loadConfig();
  if (!apiKey) {
    console.error(
      c.red("Not logged in.") +
        " Run " +
        c.cyan("captapi login") +
        " or set CAPTAPI_API_KEY.\n" +
        "Get a key at https://captapi.com/dashboard/api-keys",
    );
    process.exit(1);
  }
  return { apiKey, baseUrl };
}

function hintFor(status: number): string {
  if (status === 401) return "Your API key is invalid or revoked. Run `captapi login`.";
  if (status === 402)
    return "Out of credits. Top up at https://captapi.com/dashboard/billing";
  if (status === 429) return "Rate limit reached — slow down or upgrade your plan.";
  return "";
}

/** GET a Captapi endpoint and return the parsed JSON body. Throws ApiError. */
export async function apiGet(
  path: string,
  query: Record<string, string | number | undefined> = {},
): Promise<unknown> {
  const { apiKey, baseUrl } = requireKey();
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(query)) {
    if (v !== undefined && v !== null && String(v) !== "") qs.set(k, String(v));
  }
  const url = `${baseUrl}${path}${qs.toString() ? `?${qs}` : ""}`;

  const res = await fetch(url, { method: "GET", headers: authHeaders(apiKey) });
  const raw = await res.text();
  let body: unknown;
  try {
    body = JSON.parse(raw);
  } catch {
    body = raw;
  }
  if (!res.ok) {
    const detail =
      body && typeof body === "object" && "detail" in body
        ? (body as { detail: unknown }).detail
        : body;
    throw new ApiError(res.status, detail, hintFor(res.status));
  }
  return body;
}

/** Validate a key by calling the lightweight /v1/account/limits endpoint. */
export async function verifyKey(
  apiKey: string,
  baseUrl: string,
): Promise<{ ok: boolean; status: number; data?: unknown }> {
  const res = await fetch(`${baseUrl}/v1/account/limits`, {
    method: "GET",
    headers: authHeaders(apiKey),
  });
  if (!res.ok) return { ok: false, status: res.status };
  return { ok: true, status: res.status, data: await res.json().catch(() => undefined) };
}

export function printJson(value: unknown): void {
  process.stdout.write(JSON.stringify(value, null, 2) + "\n");
}
