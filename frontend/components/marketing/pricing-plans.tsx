"use client";

import { useState } from "react";
import {
  Sparkles,
  Zap,
  Star,
  Rocket,
  Package,
  Boxes,
  Layers,
} from "lucide-react";
import {
  CreativePricing,
  type PricingTier,
} from "@/components/ui/creative-pricing";
import { ENDPOINT_COUNT } from "@/lib/api-catalog";
import { cn } from "@/lib/utils";

type Cycle = "monthly" | "yearly" | "payg";

// ---------------------------------------------------------------------------
// Cost-based pricing model
//
// Real cost per credit (estimate): ~1 Apify scrape (~$0.002) + small
// OpenAI/infra overhead ≈ $0.0025 per credit.
// Selling price = cost + 80% markup -> cost x 1.8 ~= $0.0045 per credit.
// This is markup, not 80% gross margin. Adjust COST_PER_CREDIT /
// MARKUP here to re-price everything.
// ---------------------------------------------------------------------------
const COST_PER_CREDIT = 0.0025;
const MARKUP = 0.8; // +80%
const PRICE_PER_CREDIT = COST_PER_CREDIT * (1 + MARKUP); // $0.0045

/** Monthly price for a credit allowance, rounded to the nearest dollar. */
const priceFor = (credits: number) => Math.round(credits * PRICE_PER_CREDIT);
/** Price for a one-time pack with its own markup, rounded to the nearest dollar. */
const priceForMarkup = (credits: number, markup: number) =>
  Math.round(credits * COST_PER_CREDIT * (1 + markup));
/** "$X.XX per 1k credits" label. */
const per1k = (credits: number, price: number) =>
  `$${((price / credits) * 1000).toFixed(2)} per 1k credits`;

const YEARLY_DISCOUNT = 0.3;
const yearly = (monthly: number) => Math.round(monthly * (1 - YEARLY_DISCOUNT));

// Monthly credit allowances (chosen to land on clean cost+margin prices).
const PLAN_CREDITS = { starter: 2_000, pro: 6_000, business: 20_000 } as const;
// One-time PAYG bundles. Each pack carries its own markup:
// Starter +100%, Growth +110%, Scale +120%.
const PACKS = {
  starter: { credits: 2_000, markup: 1.0 },
  growth: { credits: 10_000, markup: 1.1 },
  scale: { credits: 50_000, markup: 1.2 },
} as const;

function subscriptionTiers(cycle: "monthly" | "yearly"): PricingTier[] {
  const isYearly = cycle === "yearly";
  const period = isYearly ? "/mo billed yearly" : "/month";
  const planParam = (name: string) =>
    `/signup?plan=${name}${isYearly ? "&cycle=yearly" : ""}`;
  const monthly = (credits: number) =>
    isYearly ? yearly(priceFor(credits)) : priceFor(credits);

  return [
    {
      name: "Free",
      icon: <Sparkles className="w-6 h-6" />,
      price: 0,
      period: "forever",
      description: "Perfect for testing",
      color: "emerald",
      cta: "Get started",
      href: "/signup",
      features: [
        "100 lifetime credits",
        "40 requests / minute",
        `All ${ENDPOINT_COUNT} APIs included`,
      ],
    },
    {
      name: "Starter",
      icon: <Zap className="w-6 h-6" />,
      price: monthly(PLAN_CREDITS.starter),
      period,
      description: "For side projects",
      color: "blue",
      cta: "Start Starter",
      href: planParam("starter"),
      features: [
        `${PLAN_CREDITS.starter.toLocaleString("en-US")} credits / month`,
        "120 requests / minute",
        `All ${ENDPOINT_COUNT} APIs included`,
      ],
    },
    {
      name: "Pro",
      icon: <Star className="w-6 h-6" />,
      price: monthly(PLAN_CREDITS.pro),
      period,
      description: "For growing products",
      color: "amber",
      popular: true,
      cta: "Start Pro",
      href: planParam("pro"),
      features: [
        `${PLAN_CREDITS.pro.toLocaleString("en-US")} credits / month`,
        "300 requests / minute",
        "Priority support",
        "Bulk endpoints (beta)",
      ],
    },
    {
      name: "Business",
      icon: <Rocket className="w-6 h-6" />,
      price: monthly(PLAN_CREDITS.business),
      period,
      description: "For data pipelines",
      color: "purple",
      cta: "Start Business",
      href: planParam("business"),
      features: [
        `${PLAN_CREDITS.business.toLocaleString("en-US")} credits / month`,
        "600 requests / minute",
        "Slack support + SLA",
        "Custom rate limits",
      ],
    },
  ];
}

const starterPrice = priceForMarkup(PACKS.starter.credits, PACKS.starter.markup);
const growthPrice = priceForMarkup(PACKS.growth.credits, PACKS.growth.markup);
const scalePrice = priceForMarkup(PACKS.scale.credits, PACKS.scale.markup);

const paygTiers: PricingTier[] = [
  {
    name: "Starter Pack",
    icon: <Package className="w-6 h-6" />,
    price: starterPrice,
    period: " one-time",
    description: `${PACKS.starter.credits.toLocaleString("en-US")} credits`,
    color: "blue",
    cta: "Buy now",
    href: "/signup?pack=starter",
    features: [
      per1k(PACKS.starter.credits, starterPrice),
      "Never expires",
      "Used after monthly credits",
      "All APIs included",
      "No subscription required",
    ],
  },
  {
    name: "Growth Pack",
    icon: <Boxes className="w-6 h-6" />,
    price: growthPrice,
    period: " one-time",
    description: `${PACKS.growth.credits.toLocaleString("en-US")} credits`,
    color: "amber",
    popular: true,
    cta: "Buy now",
    href: "/signup?pack=growth",
    features: [
      per1k(PACKS.growth.credits, growthPrice),
      "Never expires",
      "Used after monthly credits",
      "All APIs included",
      "No subscription required",
    ],
  },
  {
    name: "Scale Pack",
    icon: <Layers className="w-6 h-6" />,
    price: scalePrice,
    period: " one-time",
    description: `${PACKS.scale.credits.toLocaleString("en-US")} credits`,
    color: "purple",
    cta: "Buy now",
    href: "/signup?pack=scale",
    features: [
      per1k(PACKS.scale.credits, scalePrice),
      "Never expires",
      "Used after monthly credits",
      "All APIs included",
      "No subscription required",
    ],
  },
];

const HEADERS: Record<Cycle, { tag: string; title: string; description: string }> = {
  monthly: {
    tag: "Simple, credit-based pricing",
    title: "One key. Every platform.",
    description: "Pay only for what you use — cached results are always free.",
  },
  yearly: {
    tag: "Save 30% with annual billing",
    title: "One key. Every platform.",
    description: "Two months free when you pay yearly. Cancel anytime.",
  },
  payg: {
    tag: "Pay As You Go",
    title: "Top up anytime.",
    description:
      "For occasional usage or topping up credits. One-time purchases that never expire.",
  },
};

export function PricingPlans() {
  const [cycle, setCycle] = useState<Cycle>("monthly");

  const tiers =
    cycle === "payg" ? paygTiers : subscriptionTiers(cycle);
  const header = HEADERS[cycle];

  const options: { id: Cycle; label: string; badge?: string }[] = [
    { id: "monthly", label: "Monthly" },
    { id: "yearly", label: "Yearly", badge: "(30% off)" },
    { id: "payg", label: "PAYG" },
  ];

  return (
    <div>
      <div className="flex justify-center mb-12">
        <div className="inline-flex items-center gap-1 rounded-full border bg-muted/40 p-1">
          {options.map((o) => (
            <button
              key={o.id}
              onClick={() => setCycle(o.id)}
              className={cn(
                "group rounded-full px-4 py-1.5 text-sm transition-colors",
                cycle === o.id
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {o.label}
              {o.badge && (
                <span
                  className={cn(
                    "ml-1 font-semibold",
                    cycle === o.id
                      ? "text-primary-foreground"
                      : "text-primary group-hover:text-primary/80",
                  )}
                >
                  {o.badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <CreativePricing
        key={cycle}
        tag={header.tag}
        title={header.title}
        description={header.description}
        tiers={tiers}
      />
    </div>
  );
}
