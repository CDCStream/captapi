"use client";

// Google tag (GA4 + Google Ads) configuration, all driven by public env vars.
// Leave any of these unset and the corresponding integration is silently skipped.
export const GA_ID = process.env.NEXT_PUBLIC_GA_ID || "";
export const ADS_ID = process.env.NEXT_PUBLIC_GOOGLE_ADS_ID || "";
export const ADS_SUBSCRIBE_LABEL = process.env.NEXT_PUBLIC_GOOGLE_ADS_SUBSCRIBE_LABEL || "";
/** Google Ads conversion label for account signup (create in Ads → Goals). */
export const ADS_SIGNUP_LABEL = process.env.NEXT_PUBLIC_GOOGLE_ADS_SIGNUP_LABEL || "";

const SIGNUP_FIRED_KEY = "captapi_ads_signup_fired";

declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void;
    dataLayer?: unknown[];
  }
}

/** Send a GA4 event. No-op until gtag.js has loaded. */
export function gaEvent(action: string, params: Record<string, unknown> = {}): void {
  if (typeof window === "undefined" || !window.gtag) return;
  window.gtag("event", action, params);
}

/**
 * Fire a Google Ads conversion. Defaults to the "subscribe" conversion label.
 * Used as an optimisation signal for Google Ads campaigns.
 */
export function adsConversion(opts: {
  label?: string;
  value?: number;
  currency?: string;
  transactionId?: string;
} = {}): void {
  if (typeof window === "undefined" || !window.gtag) return;
  const label = opts.label || ADS_SUBSCRIBE_LABEL;
  if (!ADS_ID || !label) return;
  window.gtag("event", "conversion", {
    send_to: `${ADS_ID}/${label}`,
    value: opts.value,
    currency: opts.currency || "USD",
    transaction_id: opts.transactionId,
  });
}

/**
 * Fire the signup conversion once per browser (deduped via sessionStorage).
 * Call after password signUp succeeds, or after OAuth/email confirm lands
 * with ?ads_signup=1.
 */
export function adsSignupConversion(opts?: {
  value?: number;
  transactionId?: string;
}): void {
  if (typeof window === "undefined") return;
  try {
    if (sessionStorage.getItem(SIGNUP_FIRED_KEY) === "1") return;
  } catch {
    /* private mode */
  }
  if (!ADS_ID || !ADS_SIGNUP_LABEL) {
    gaEvent("sign_up", { method: "ads_label_missing" });
    return;
  }
  adsConversion({
    label: ADS_SIGNUP_LABEL,
    value: opts?.value,
    currency: "USD",
    transactionId: opts?.transactionId,
  });
  gaEvent("sign_up", { method: "ads_conversion" });
  try {
    sessionStorage.setItem(SIGNUP_FIRED_KEY, "1");
  } catch {
    /* ignore */
  }
}
