"use client";

import { useEffect } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { adsSignupConversion } from "@/lib/gtag";

/**
 * Fires Google Ads signup conversion when the auth callback redirects with
 * ?ads_signup=1 (new OAuth / email-confirm users). Strips the query param
 * after firing so refreshes do not re-trigger.
 */
export function SignupAdsConversion() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const flag = searchParams.get("ads_signup");

  useEffect(() => {
    if (flag !== "1") return;
    adsSignupConversion();
    const next = new URLSearchParams(searchParams.toString());
    next.delete("ads_signup");
    const qs = next.toString();
    router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
  }, [flag, pathname, router, searchParams]);

  return null;
}
