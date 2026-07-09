// Cost model. Two numbers per call:
//   customerPrice  = what a user is billed  (credits x pricePerCredit)
//   upstreamCost   = what the call costs US  (native ~ $0, Apify ~ credits x costPerCredit)
// The rates mirror frontend/app/(marketing)/pricing/pricing-schema.ts and are
// editable in the UI (persisted), since the "our cost" side is an estimate.

export const DEFAULT_COST_PER_CREDIT = 0.0025; // our cost basis ($/credit)
export const DEFAULT_MARKUP = 1.8; // customer price = cost x 1.8

export interface Rates {
  costPerCredit: number;
  markup: number;
}

export const DEFAULT_RATES: Rates = {
  costPerCredit: DEFAULT_COST_PER_CREDIT,
  markup: DEFAULT_MARKUP,
};

// "cache" only appears when the backend reports it via X-Captapi-Source.
export type SourceGuess = "direct" | "apify" | "cache" | "unknown";

export interface CostBreakdown {
  credits: number;
  customerPrice: number;
  upstreamCost: number;
  source: SourceGuess;
}

/** Customer-facing price for a number of credits. */
export function priceFor(credits: number, rates: Rates): number {
  return credits * rates.costPerCredit * rates.markup;
}

/** Our estimated upstream cost. Native (self-scraped) and cache hits are ~free;
 *  only Apify-backed calls carry the per-credit cost basis. Unknown is treated
 *  as Apify (worst case) so savings aren't overstated. */
export function upstreamFor(credits: number, source: SourceGuess, rates: Rates): number {
  if (source === "direct" || source === "cache") return 0;
  return credits * rates.costPerCredit;
}

export function costBreakdown(credits: number, source: SourceGuess, rates: Rates): CostBreakdown {
  return {
    credits,
    customerPrice: priceFor(credits, rates),
    upstreamCost: upstreamFor(credits, source, rates),
    source,
  };
}

/** Format a USD amount with enough precision for sub-cent per-call costs. */
export function usd(amount: number): string {
  if (amount === 0) return "$0";
  if (amount < 0.01) return `$${amount.toFixed(4)}`;
  return `$${amount.toFixed(3)}`;
}
