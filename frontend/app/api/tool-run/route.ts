import { NextResponse } from "next/server";
import { TOOL_LIST } from "@/lib/tools";

export const runtime = "nodejs";
export const maxDuration = 60;

// Endpoints the public free tools are allowed to call (server-side, with our
// own key). Derived from the tools catalog so it stays in sync.
const ALLOWED = new Set(TOOL_LIST.map((t) => t.apiEndpoint));

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://api.captapi.com";

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

  const apiKey = process.env.CAPTAPI_TOOL_API_KEY;
  if (!apiKey) {
    return NextResponse.json(
      { error: "This tool is temporarily unavailable. Please try again later." },
      { status: 503 },
    );
  }

  const qs = new URLSearchParams({ url });
  if (language) qs.set("language", language);

  try {
    const res = await fetch(`${API_BASE}${endpoint}?${qs.toString()}`, {
      headers: { Authorization: `Bearer ${apiKey}`, Accept: "application/json" },
      // Server-side responses are cached 24h upstream; no need to cache here.
      cache: "no-store",
    });

    const json = await res.json().catch(() => null);

    if (!res.ok) {
      const detail =
        (json && (json.detail || json.error)) ||
        (res.status === 404 ? "No transcript is available for this video." : "Request failed. Please try again.");
      const status = res.status === 404 ? 404 : res.status === 429 ? 429 : 502;
      return NextResponse.json({ error: String(detail) }, { status });
    }

    return NextResponse.json({ data: json?.data ?? json });
  } catch {
    return NextResponse.json({ error: "Couldn't reach the service. Please try again." }, { status: 502 });
  }
}
