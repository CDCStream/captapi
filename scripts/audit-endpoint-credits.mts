/**
 * Endpoint credit audit.
 *
 * Checks the public endpoint catalog against a configurable upstream-cost model
 * and reports whether each endpoint's current credit price reaches the target
 * gross margin.
 *
 * Important:
 * - The built-in costs are conservative placeholders, not vendor invoices.
 * - Override them with real Apify/OpenAI/infra observations via code edits or
 *   env vars before making final pricing decisions.
 *
 * Run:
 *   npx tsx scripts/audit-endpoint-credits.mts
 *
 * Env:
 *   SELL_PRICE_PER_CREDIT_USD=0.0045
 *   TARGET_GROSS_MARGIN=0.8
 */

import {
  ALL_ENDPOINTS,
  PLATFORM_GROUPS,
  type ApiEndpoint,
  type Category,
  type PlatformId,
} from "../frontend/lib/api-catalog.ts";

const SELL_PRICE_PER_CREDIT_USD = Number(process.env.SELL_PRICE_PER_CREDIT_USD ?? "0.0045");
const TARGET_GROSS_MARGIN = Number(process.env.TARGET_GROSS_MARGIN ?? "0.8");
const UNDER_MARGIN_TOLERANCE = 0.03;

const categoryBaseCostUsd: Record<Category, number> = {
  transcript: 0.006,
  summarize: 0.012,
  details: 0.006,
  comments: 0.02,
  channel: 0.006,
  search: 0.025,
  list: 0.025,
  download: 0.01,
};

const platformCostMultiplier: Partial<Record<PlatformId, number>> = {
  // Low-cost public/direct API style sources.
  account: 0.1,
  github: 0.4,
  linktree: 0.5,
  komi: 0.5,
  pillar: 0.5,
  linkbio: 0.5,
  linkme: 0.5,
  truth_social: 0.6,
  bluesky: 0.6,

  // Paid actor / heavier scraping sources.
  twitch: 1.2,
  spotify: 0.8,
  soundcloud: 1.0,
  snapchat: 1.5,
  kick: 2.0,
  amazon_shop: 2.5,
  kwai: 2.5,
  tiktok_shop: 2.0,
  ad_library: 2.5,
};

// Endpoint-level overrides for newly added/high-value or known heavier routes.
const endpointCostOverrideUsd: Record<string, number> = {
  "facebook-marketplace-location-search": 0.015,
  "facebook-marketplace-item": 0.015,
  "google-ad-library-company-ads": 0.06,
  "google-ad-library-advertiser-search": 0.04,
  "google-ad-library-ad-details": 0.015,
  "facebook-ad-library-ad-transcript": 0.015,
  "tiktok-shop-user-showcase": 0.04,
  "amazon-shop-page": 0.08,
  "kwai-user-posts": 0.04,
  "kwai-profile": 0.015,
  "kwai-post": 0.015,
  "kick-clip": 0.03,
};

function grossMargin(revenue: number, cost: number): number {
  if (revenue <= 0) return -Infinity;
  return (revenue - cost) / revenue;
}

function recommendedCredits(costUsd: number): number {
  const requiredRevenue = costUsd / (1 - TARGET_GROSS_MARGIN);
  return Math.max(1, Math.ceil(requiredRevenue / SELL_PRICE_PER_CREDIT_USD));
}

function estimateCostUsd(ep: ApiEndpoint): { costUsd: number; source: string } {
  const override = endpointCostOverrideUsd[ep.slug];
  if (override !== undefined) return { costUsd: override, source: "endpoint override" };

  const base = categoryBaseCostUsd[ep.category];
  const multiplier = platformCostMultiplier[ep.platform] ?? 1;
  return {
    costUsd: Number((base * multiplier).toFixed(6)),
    source: `${ep.category} base x ${ep.platform} multiplier`,
  };
}

function currentDefaultResults(ep: ApiEndpoint): number | null {
  if (!ep.creditsPerResult) return null;
  return Math.max(1, Math.round(ep.credits / ep.creditsPerResult));
}

const rows = ALL_ENDPOINTS.map((ep) => {
  const { costUsd, source } = estimateCostUsd(ep);
  const currentRevenueUsd = ep.credits * SELL_PRICE_PER_CREDIT_USD;
  const margin = grossMargin(currentRevenueUsd, costUsd);
  const recCredits = recommendedCredits(costUsd);
  const defaultResults = currentDefaultResults(ep);
  const recCreditsPerResult = defaultResults
    ? Number((recCredits / defaultResults).toFixed(3))
    : null;
  const status =
    margin + UNDER_MARGIN_TOLERANCE < TARGET_GROSS_MARGIN
      ? "UNDER"
      : margin > TARGET_GROSS_MARGIN + 0.2
        ? "OVER"
        : "OK";

  return {
    platform: ep.platform,
    slug: ep.slug,
    category: ep.category,
    currentCredits: ep.credits,
    currentCreditsPerResult: ep.creditsPerResult ?? null,
    defaultResults,
    estimatedCostUsd: costUsd,
    currentRevenueUsd,
    currentGrossMargin: margin,
    recommendedCredits: recCredits,
    recommendedCreditsPerResult: recCreditsPerResult,
    deltaCredits: recCredits - ep.credits,
    source,
    status,
  };
});

const under = rows.filter((r) => r.status === "UNDER");
const over = rows.filter((r) => r.status === "OVER");
const ok = rows.filter((r) => r.status === "OK");

console.log("# Captapi Endpoint Credit Audit");
console.log("");
console.log(`- Endpoints audited: ${rows.length}`);
console.log(`- Platform groups: ${PLATFORM_GROUPS.length}`);
console.log(`- Sell price per credit: $${SELL_PRICE_PER_CREDIT_USD.toFixed(4)}`);
console.log(`- Target gross margin: ${(TARGET_GROSS_MARGIN * 100).toFixed(0)}%`);
console.log(`- UNDER: ${under.length}, OK: ${ok.length}, OVER: ${over.length}`);
console.log("");
console.log("## Under target margin (review first)");
console.log("");
console.log("| endpoint | current | recommended | margin | est. cost | basis |");
console.log("| --- | ---: | ---: | ---: | ---: | --- |");

for (const r of under.sort((a, b) => b.deltaCredits - a.deltaCredits).slice(0, 60)) {
  const current = r.currentCreditsPerResult
    ? `${r.currentCredits} (${r.currentCreditsPerResult}/result)`
    : String(r.currentCredits);
  const recommended = r.recommendedCreditsPerResult
    ? `${r.recommendedCredits} (${r.recommendedCreditsPerResult}/result)`
    : String(r.recommendedCredits);
  console.log(
    `| ${r.slug} | ${current} | ${recommended} | ${(r.currentGrossMargin * 100).toFixed(1)}% | $${r.estimatedCostUsd.toFixed(4)} | ${r.source} |`,
  );
}

console.log("");
console.log("## Notes");
console.log("");
console.log("- This is a pricing guardrail, not an automatic repricer.");
console.log("- Replace built-in cost assumptions with actual Apify/OpenAI/infra observed costs before changing production credits.");
console.log("- If you mean +80% markup, current sell price per credit can stay near $0.0045. If you mean 80% gross margin, revenue must be 5x estimated cost.");
