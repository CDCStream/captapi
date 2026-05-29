"use client";

import { usePathname } from "next/navigation";
import { useEffect } from "react";
import { track } from "@/lib/analytics";

/**
 * Fires a `page_view` event on every route change, for both landing-page
 * visitors (anonymous) and dashboard users (authenticated). Rendered once in
 * the root layout so it covers the entire app.
 */
export function PageViewTracker() {
  const pathname = usePathname();

  useEffect(() => {
    track("page_view");
  }, [pathname]);

  return null;
}
