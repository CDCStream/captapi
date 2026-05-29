import { NextRequest, NextResponse } from "next/server";

// Runs on Vercel's edge so the request carries IP-geolocation headers.
export const runtime = "edge";
export const dynamic = "force-dynamic";

/**
 * Returns the visitor's approximate location, derived from Vercel's edge
 * geo headers. Used by the client analytics layer to stamp events with a
 * country without relying on any third-party geo service.
 */
export function GET(req: NextRequest) {
  const decode = (v: string | null) => {
    if (!v) return null;
    try {
      return decodeURIComponent(v);
    } catch {
      return v;
    }
  };

  const country = req.headers.get("x-vercel-ip-country") || null;
  const region = req.headers.get("x-vercel-ip-country-region") || null;
  const city = decode(req.headers.get("x-vercel-ip-city"));

  return NextResponse.json(
    { country, region, city },
    { headers: { "cache-control": "no-store" } },
  );
}
