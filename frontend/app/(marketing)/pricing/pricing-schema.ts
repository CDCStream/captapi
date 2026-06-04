// Product + Offer JSON-LD for the pricing page. Prices mirror the
// cost-based model in components/marketing/pricing-plans.tsx.
import { absoluteUrl } from "@/lib/seo";

const COST_PER_CREDIT = 0.0025;
const PRICE_PER_CREDIT = COST_PER_CREDIT * 1.8; // +80% margin
const priceFor = (credits: number) => Math.round(credits * PRICE_PER_CREDIT);

const PLANS = [
  { name: "Free", credits: 0, price: 0, recurring: false },
  { name: "Starter", credits: 2_000, price: priceFor(2_000), recurring: true },
  { name: "Pro", credits: 6_000, price: priceFor(6_000), recurring: true },
  { name: "Business", credits: 20_000, price: priceFor(20_000), recurring: true },
];

export function pricingJsonLd() {
  const url = absoluteUrl("/pricing");
  return {
    "@context": "https://schema.org",
    "@type": "Product",
    name: "Captapi Social Media Data API",
    description:
      "One REST API for transcripts, AI summaries, comments, followers and engagement metrics from YouTube, TikTok, Instagram and Facebook. Usage-based credit pricing with a free tier.",
    brand: { "@type": "Brand", name: "Captapi" },
    url,
    offers: PLANS.map((p) => ({
      "@type": "Offer",
      name: `${p.name} plan`,
      price: String(p.price),
      priceCurrency: "USD",
      url,
      availability: "https://schema.org/InStock",
      ...(p.recurring
        ? {
            priceSpecification: {
              "@type": "UnitPriceSpecification",
              price: String(p.price),
              priceCurrency: "USD",
              referenceQuantity: {
                "@type": "QuantitativeValue",
                value: 1,
                unitCode: "MON",
              },
              billingDuration: "P1M",
            },
          }
        : {}),
    })),
  };
}
