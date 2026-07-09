// Thin request runner. Mirrors the CLI/SDK: GET with a Bearer key, drop empty
// params, parse the { success, data } envelope. Times the round-trip with
// performance.now so the recorded latency includes the network.

export type Target = "local" | "prod";

export const TARGETS: Record<Target, { label: string; baseUrl: string }> = {
  // Both targets are proxied by Vite in dev (/local-api, /prod-api) to avoid
  // CORS — prod only whitelists localhost:3000, not the playground port.
  local: { label: "Local (localhost:8000)", baseUrl: "/local-api" },
  prod: { label: "Prod (api.captapi.com)", baseUrl: "/prod-api" },
};

export interface RunResult {
  ok: boolean;
  status: number;
  durationMs: number;
  body: unknown;
  error?: string;
  itemCount?: number;
  /** Real serving path from the X-Captapi-Source header:
   *  direct | apify | cache | unknown. Undefined when the backend predates
   *  the header (then the UI falls back to the catalog-based guess). */
  serverSource?: "direct" | "apify" | "cache" | "unknown";
  /** Real credits billed, from X-Captapi-Credits. */
  serverCredits?: number;
}

/** Parse the billing headers the backend stamps on every /v1 response. */
function readBillingHeaders(res: Response): Pick<RunResult, "serverSource" | "serverCredits"> {
  const src = res.headers.get("x-captapi-source");
  const credits = res.headers.get("x-captapi-credits");
  const out: Pick<RunResult, "serverSource" | "serverCredits"> = {};
  if (src === "direct" || src === "apify" || src === "cache" || src === "unknown") {
    out.serverSource = src;
  }
  if (credits !== null && credits !== "" && !Number.isNaN(Number(credits))) {
    out.serverCredits = Number(credits);
  }
  return out;
}

function buildUrl(target: Target, path: string, params: Record<string, string>): string {
  const base = TARGETS[target].baseUrl;
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && String(v).trim() !== "") qs.set(k, String(v));
  }
  const query = qs.toString();
  return `${base}${path}${query ? `?${query}` : ""}`;
}

/** Count returned rows for list endpoints (drives per-item credit scaling). */
function countItems(body: unknown): number | undefined {
  if (body && typeof body === "object") {
    const data = (body as { data?: unknown }).data;
    const node = (data ?? body) as Record<string, unknown>;
    if (typeof node.totalReturned === "number") return node.totalReturned;
    for (const key of ["results", "items", "comments", "videos", "posts", "episodes"]) {
      const v = node[key];
      if (Array.isArray(v)) return v.length;
    }
  }
  return undefined;
}

export async function runRequest(
  target: Target,
  apiKey: string,
  path: string,
  params: Record<string, string>,
  timeoutMs = 120_000,
): Promise<RunResult> {
  const url = buildUrl(target, path, params);
  const started = performance.now();
  try {
    const res = await fetch(url, {
      method: "GET",
      headers: { Authorization: `Bearer ${apiKey}`, Accept: "application/json" },
      signal: AbortSignal.timeout(timeoutMs),
    });
    const raw = await res.text();
    let body: unknown;
    try {
      body = JSON.parse(raw);
    } catch {
      body = raw;
    }
    const durationMs = Math.round(performance.now() - started);
    return {
      ok: res.ok,
      status: res.status,
      durationMs,
      body,
      itemCount: countItems(body),
      error: res.ok ? undefined : extractError(body),
      ...readBillingHeaders(res),
    };
  } catch (err) {
    const durationMs = Math.round(performance.now() - started);
    const message = err instanceof Error ? err.message : String(err);
    return { ok: false, status: 0, durationMs, body: null, error: message };
  }
}

function extractError(body: unknown): string {
  if (body && typeof body === "object") {
    const b = body as Record<string, unknown>;
    const detail = b.detail ?? b.error;
    if (typeof detail === "string") return detail;
    if (detail && typeof detail === "object") return JSON.stringify(detail);
  }
  return typeof body === "string" ? body.slice(0, 300) : "request failed";
}
