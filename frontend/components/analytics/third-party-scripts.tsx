"use client";

import Script from "next/script";
import { GA_ID, ADS_ID } from "@/lib/gtag";

/**
 * Loads the Google tag (GA4 + Google Ads). Everything is gated on the presence
 * of its env var, so this component is safe to render unconditionally (locally
 * nothing loads; in production only the configured tags load).
 *
 *   NEXT_PUBLIC_GA_ID                     → GA4 measurement id  (G-XXXXXXXXXX)
 *   NEXT_PUBLIC_GOOGLE_ADS_ID             → Google Ads id       (AW-XXXXXXXXX)
 *   NEXT_PUBLIC_GOOGLE_ADS_SUBSCRIBE_LABEL→ Ads conversion label (subscribe)
 *
 * NOTE: Ahrefs Web Analytics is intentionally NOT loaded here. Its analytics.js
 * reads its key from `document.currentScript`, which is null for scripts that
 * next/script injects dynamically. It is rendered as a static <script> tag in
 * the root layout instead, so the attribute is present at parse time.
 */
export function ThirdPartyScripts() {
  const primaryId = GA_ID || ADS_ID;
  if (!primaryId) return null;

  return (
    <>
      <Script
        id="gtag-src"
        strategy="afterInteractive"
        src={`https://www.googletagmanager.com/gtag/js?id=${primaryId}`}
      />
      <Script id="gtag-init" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          window.gtag = gtag;
          gtag('js', new Date());
          ${GA_ID ? `gtag('config', '${GA_ID}');` : ""}
          ${ADS_ID ? `gtag('config', '${ADS_ID}');` : ""}
        `}
      </Script>
    </>
  );
}
