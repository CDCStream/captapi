/** Shared HTTP core for the generated Captapi SDK. */

export const DEFAULT_BASE_URL = "https://api.captapi.com";

/** Standard Captapi response envelope: `{ success, data }`. */
export interface ApiEnvelope<T = unknown> {
  success: boolean;
  data: T;
  [key: string]: unknown;
}

export interface CaptapiOptions {
  /** API key. Falls back to the CAPTAPI_API_KEY environment variable. */
  apiKey?: string;
  /** Override the API origin (default https://api.captapi.com). */
  baseUrl?: string;
  /** Per-request timeout in milliseconds (default 120000). */
  timeoutMs?: number;
  /** Custom fetch implementation (defaults to globalThis.fetch). */
  fetch?: typeof globalThis.fetch;
}

/** Raised for every non-2xx response. Never fails silently. */
export class CaptapiError extends Error {
  readonly status: number;
  readonly code?: string;
  readonly detail?: unknown;

  constructor(message: string, status: number, code?: string, detail?: unknown) {
    super(message);
    this.name = "CaptapiError";
    this.status = status;
    this.code = code;
    this.detail = detail;
  }
}

export class HttpCore {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly timeoutMs: number;
  private readonly fetchImpl: typeof globalThis.fetch;

  constructor(options: CaptapiOptions = {}) {
    const key =
      options.apiKey ??
      (typeof process !== "undefined" ? process.env?.CAPTAPI_API_KEY : undefined);
    if (!key) {
      throw new CaptapiError(
        "Missing API key. Pass { apiKey } or set CAPTAPI_API_KEY. Get one at https://captapi.com/dashboard/api-keys",
        401,
        "missing_api_key",
      );
    }
    this.apiKey = key;
    this.baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/+$/, "");
    this.timeoutMs = options.timeoutMs ?? 120_000;
    this.fetchImpl = options.fetch ?? globalThis.fetch;
  }

  async get(path: string, params: object = {}): Promise<ApiEnvelope> {
    const url = new URL(this.baseUrl + path);
    for (const [k, v] of Object.entries(params as Record<string, unknown>)) {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
    }

    let res: Response;
    try {
      res = await this.fetchImpl(url, {
        headers: { authorization: `Bearer ${this.apiKey}`, accept: "application/json" },
        signal: AbortSignal.timeout(this.timeoutMs),
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      throw new CaptapiError(`Request to ${path} failed: ${message}`, 0, "network_error", err);
    }

    let body: any;
    try {
      body = await res.json();
    } catch {
      body = undefined;
    }

    if (!res.ok || body?.success === false) {
      const detail = body?.detail ?? body?.error ?? body;
      const code =
        typeof body?.detail === "object" && body?.detail?.error
          ? String(body.detail.error)
          : typeof body?.error === "string"
            ? body.error
            : undefined;
      throw new CaptapiError(
        `Captapi ${path} returned ${res.status}: ${typeof detail === "string" ? detail : JSON.stringify(detail ?? "unknown error")}`,
        res.status,
        code,
        detail,
      );
    }

    return body as ApiEnvelope;
  }
}
