"use client";

import { createClient } from "@/lib/supabase/client";

const ANON_KEY = "captapi_anon_id";
const GEO_KEY = "captapi_geo";
const GEO_TTL_MS = 24 * 60 * 60 * 1000; // refresh geo at most once per day

interface Geo {
  country?: string | null;
  region?: string | null;
  city?: string | null;
}

let geoPromise: Promise<Geo> | null = null;

/** Stable per-browser id so anonymous activity can be correlated. */
export function getAnonId(): string {
  if (typeof window === "undefined") return "";
  try {
    let id = localStorage.getItem(ANON_KEY);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(ANON_KEY, id);
    }
    return id;
  } catch {
    return "";
  }
}

/**
 * Resolve the visitor's country/region/city via the edge /api/geo endpoint.
 * Cached in localStorage for a day and de-duplicated per page load, so it adds
 * at most one tiny request per session. Never throws.
 */
async function getGeo(): Promise<Geo> {
  if (typeof window === "undefined") return {};
  try {
    const cached = localStorage.getItem(GEO_KEY);
    if (cached) {
      const parsed = JSON.parse(cached) as { geo: Geo; ts: number };
      if (Date.now() - parsed.ts < GEO_TTL_MS) return parsed.geo;
    }
  } catch {
    // ignore malformed cache
  }

  if (!geoPromise) {
    geoPromise = fetch("/api/geo")
      .then((r) => (r.ok ? (r.json() as Promise<Geo>) : {}))
      .catch(() => ({}));
  }

  const geo = (await geoPromise) || {};
  try {
    localStorage.setItem(GEO_KEY, JSON.stringify({ geo, ts: Date.now() }));
  } catch {
    // ignore quota errors
  }
  return geo;
}

/**
 * Record a user-activity event. Works for both signed-in users and anonymous
 * visitors (user_id is left null for the latter). Never throws — analytics
 * must not break the app.
 */
export async function track(
  event: string,
  properties: Record<string, unknown> = {},
): Promise<void> {
  if (typeof window === "undefined") return;
  try {
    const sb = createClient();
    const [{ data }, geo] = await Promise.all([sb.auth.getSession(), getGeo()]);
    const userId = data.session?.user?.id ?? null;

    await sb.from("events").insert({
      user_id: userId,
      anon_id: getAnonId(),
      event,
      path: window.location.pathname,
      referrer: document.referrer || null,
      properties,
      user_agent: navigator.userAgent,
      country: geo.country ?? null,
      region: geo.region ?? null,
      city: geo.city ?? null,
    });
  } catch {
    // swallow — tracking failures should be invisible to users
  }
}
