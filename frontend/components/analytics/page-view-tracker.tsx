"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { useEffect, useRef } from "react";
import { track } from "@/lib/analytics";
import { gaEvent } from "@/lib/gtag";

/**
 * Fires a `page_view` event on every route change, for both landing-page
 * visitors (anonymous) and dashboard users (authenticated). Rendered once in
 * the root layout so it covers the entire app. Also forwards a GA4 page_view
 * so single-page-app navigations are counted in Google Analytics.
 */
export function PageViewTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  // The initial GA4 page_view is sent automatically by gtag('config', ...),
  // so we only forward GA page_views for subsequent client-side navigations
  // to avoid double-counting the first load.
  const gaInitialDone = useRef(false);

  useEffect(() => {
    track("page_view");

    if (!gaInitialDone.current) {
      gaInitialDone.current = true;
      return;
    }
    const query = searchParams?.toString();
    const url = query ? `${pathname}?${query}` : pathname;
    gaEvent("page_view", { page_path: url, page_location: window.location.href });
  }, [pathname, searchParams]);

  return null;
}
