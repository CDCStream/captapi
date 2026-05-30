import type { Metadata } from "next";
import { PricingPlans } from "@/components/marketing/pricing-plans";

export const metadata: Metadata = {
  title: "Pricing — Captapi",
  description:
    "Simple, usage-based pricing for the Captapi social media data API. Start free with 100 credits — no credit card required.",
  alternates: { canonical: "/pricing" },
};

export default function PricingPage() {
  return (
    <section className="py-20">
      <PricingPlans />

      <div className="mt-16 text-center text-sm text-muted-foreground space-y-1">
        <p>
          PAYG credits never expire and are spent only after your monthly
          allowance runs out.
        </p>
        <p>
          Rate limits are enforced per minute, per plan. Cached responses
          (within 24h) don&apos;t consume credits or count toward your limit.
        </p>
      </div>
    </section>
  );
}
