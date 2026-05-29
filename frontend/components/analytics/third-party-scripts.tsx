"use client";

import Script from "next/script";
import { GA_ID, ADS_ID } from "@/lib/gtag";

const AHREFS_KEY = process.env.NEXT_PUBLIC_AHREFS_KEY || "";

/**
 * Loads third-party analytics/advertising tags. Everything is gated on the
 * presence of its env var, so this component is safe to render unconditionally
 * (locally nothing loads; in production only the configured tags load).
 *
 *   NEXT_PUBLIC_GA_ID                     → GA4 measurement id  (G-XXXXXXXXXX)
 *   NEXT_PUBLIC_GOOGLE_ADS_ID             → Google Ads id       (AW-XXXXXXXXX)
 *   NEXT_PUBLIC_GOOGLE_ADS_SUBSCRIBE_LABEL→ Ads conversion label (subscribe)
 *   NEXT_PUBLIC_AHREFS_KEY                → Ahrefs Web Analytics key
 */
export function ThirdPartyScripts() {
  const primaryId = GA_ID || ADS_ID;

  return (
    <>
      {primaryId && (
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
      )}

      {AHREFS_KEY && (
        <Script
          id="ahrefs-analytics"
          strategy="afterInteractive"
          src="https://analytics.ahrefs.com/analytics.js"
          data-key={AHREFS_KEY}
        />
      )}
    </>
  );
}
