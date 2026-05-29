"use client";

import { createClient } from "@/lib/supabase/client";

const ANON_KEY = "captapi_anon_id";

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
    const { data } = await sb.auth.getSession();
    const userId = data.session?.user?.id ?? null;

    await sb.from("events").insert({
      user_id: userId,
      anon_id: getAnonId(),
      event,
      path: window.location.pathname,
      referrer: document.referrer || null,
      properties,
      user_agent: navigator.userAgent,
    });
  } catch {
    // swallow — tracking failures should be invisible to users
  }
}
