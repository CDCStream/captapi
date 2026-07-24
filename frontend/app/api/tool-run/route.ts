import { createHash } from "node:crypto";
import { NextResponse } from "next/server";
import { TOOL_LIST } from "@/lib/tools";

export const runtime = "nodejs";
export const maxDuration = 60;

// Endpoints the public free tools are allowed to call (server-side, with our
// own key). Derived from the tools catalog so it stays in sync.
const ALLOWED = new Set(TOOL_LIST.map((t) => t.apiEndpoint));

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://api.captapi.com";

/** Transcript + summarize: prefer shared cache (0 credits on hit). */
function useCacheByDefault(endpoint: string): boolean {
  return /\/(transcript|summarize)$/.test(endpoint);
}

const ANON_COOKIE = "captapi_tool_free";
const ANON_DAILY_LIMIT = 3;

function clientFingerprint(req: Request): string {
  const forwarded = req.headers.get("x-forwarded-for") || "";
  const ip = forwarded.split(",")[0]?.trim() || req.headers.get("x-real-ip") || "unknown";
  const ua = req.headers.get("user-agent") || "";
  return createHash("sha256").update(`${ip}|${ua}`).digest("hex").slice(0, 32);
}

function cookieCount(req: Request): number {
  const raw = req.headers.get("cookie") || "";
  const match = raw.match(new RegExp(`(?:^|;\\s*)${ANON_COOKIE}=(\\d+)`));
  return match ? Math.max(0, parseInt(match[1], 10) || 0) : 0;
}

export async function POST(req: Request) {
  let body: { endpoint?: string; url?: string; language?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const endpoint = (body.endpoint || "").trim();
  const url = (body.url || "").trim();
  const language = (body.language || "").trim();

  if (!ALLOWED.has(endpoint)) {
    return NextResponse.json({ error: "Unknown tool." }, { status: 404 });
  }
  if (!url) {
    return NextResponse.json({ error: "Please paste a video URL." }, { status: 400 });
  }
  if (!/^https?:\/\/.{3,}/i.test(url) || url.length > 600) {
    return NextResponse.json({ error: "That doesn't look like a valid URL." }, { status: 400 });
  }

  if (cookieCount(req) >= ANON_DAILY_LIMIT) {
    return NextResponse.json(
      {
        error:
          "You've used today's free tries. Sign up for an API key — the same tools cost far less with your own credits.",
        code: "soft_paywall",
        upgrade_url: "/signup",
      },
      { status: 429 },
    );
  }

  const apiKey = process.env.CAPTAPI_TOOL_API_KEY;
  if (!apiKey) {
    return NextResponse.json(
      { error: "This tool is temporarily unavailable. Please try again later." },
      { status: 503 },
    );
  }

  const qs = new URLSearchParams({ url });
  if (language) qs.set("language", language);
  qs.set("cache", useCacheByDefault(endpoint) ? "true" : "false");

  const headers: Record<string, string> = {
    Authorization: `Bearer ${apiKey}`,
    Accept: "application/json",
  };
  const toolSecret = process.env.CAPTAPI_TOOL_PROXY_SECRET || "";
  if (toolSecret) {
    headers["X-Captapi-Tool-Secret"] = toolSecret;
    headers["X-Captapi-Client"] = clientFingerprint(req);
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}?${qs.toString()}`, {
      headers,
      cache: "no-store",
    });

    const json = await res.json().catch(() => null);

    if (!res.ok) {
      const detail =
        (json && (typeof json.detail === "string" ? json.detail : json.detail?.error || json.error)) ||
        (res.status === 404
          ? "No result is available for this video."
          : "Request failed. Please try again.");
      const status =
        res.status === 404 ? 404 : res.status === 429 ? 429 : res.status === 402 ? 402 : 502;
      const code =
        typeof json?.detail === "object" && json.detail?.error
          ? String(json.detail.error)
          : res.status === 429
            ? "rate_limited"
            : undefined;
      return NextResponse.json(
        {
          error: String(detail),
          code,
          upgrade_url: "/signup",
        },
        { status },
      );
    }

    const response = NextResponse.json({ data: json?.data ?? json });
    const next = Math.min(ANON_DAILY_LIMIT, cookieCount(req) + 1);
    response.cookies.set(ANON_COOKIE, String(next), {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60 * 24,
    });
    // Migrate away from the older TikTok-only cookie name.
    response.cookies.set("captapi_tool_tt", "", { path: "/", maxAge: 0 });
    response.headers.set("X-Captapi-Free-Tries-Left", String(Math.max(0, ANON_DAILY_LIMIT - next)));
    return response;
  } catch {
    return NextResponse.json({ error: "Couldn't reach the service. Please try again." }, { status: 502 });
  }
}
