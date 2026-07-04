"use client";

import { useMemo, useState } from "react";
import { DollarSign, Eye, Users } from "lucide-react";

// Creator Rewards Program pays roughly $0.40-$1.00 per 1,000 *qualified* views
// (60s+ videos, US rates). Brand deal rates scale with follower count.
const RPM_LOW = 0.4;
const RPM_HIGH = 1.0;

const BRAND_TIERS = [
  { label: "Nano (1K–10K)", min: 1_000, per: [20, 150] },
  { label: "Micro (10K–50K)", min: 10_000, per: [150, 500] },
  { label: "Mid (50K–500K)", min: 50_000, per: [500, 3_000] },
  { label: "Macro (500K–1M)", min: 500_000, per: [3_000, 10_000] },
  { label: "Mega (1M+)", min: 1_000_000, per: [10_000, 50_000] },
];

const usd = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: n < 10 ? 2 : 0 });

const parse = (v: string) => Math.max(0, Number(v.replace(/[,\s]/g, "")) || 0);

export default function TikTokMoneyCalculatorClient() {
  const [views, setViews] = useState("100000");
  const [followers, setFollowers] = useState("10000");

  const v = parse(views);
  const f = parse(followers);

  const rewards = useMemo(() => ({ low: (v / 1000) * RPM_LOW, high: (v / 1000) * RPM_HIGH }), [v]);
  const tier = useMemo(() => [...BRAND_TIERS].reverse().find((t) => f >= t.min), [f]);

  return (
    <div className="mt-8 grid gap-6 lg:grid-cols-2">
      <div className="rounded-2xl border bg-card p-6">
        <h2 className="font-semibold">Your numbers</h2>
        <label className="mt-4 block">
          <span className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
            <Eye className="size-4 text-muted-foreground" /> Views per video (or per month)
          </span>
          <input
            inputMode="numeric"
            value={views}
            onChange={(e) => setViews(e.target.value)}
            className="w-full rounded-md border bg-background px-3 py-2.5 text-lg font-semibold outline-none focus:ring-2 focus:ring-primary/40"
            placeholder="e.g. 100000"
          />
        </label>
        <label className="mt-4 block">
          <span className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
            <Users className="size-4 text-muted-foreground" /> Followers
          </span>
          <input
            inputMode="numeric"
            value={followers}
            onChange={(e) => setFollowers(e.target.value)}
            className="w-full rounded-md border bg-background px-3 py-2.5 text-lg font-semibold outline-none focus:ring-2 focus:ring-primary/40"
            placeholder="e.g. 10000"
          />
        </label>
        <p className="mt-4 text-xs text-muted-foreground">
          Creator Rewards requires 10K+ followers, 100K views in the last 30 days, and videos over one
          minute. Rates are US estimates — qualified views only.
        </p>
      </div>

      <div className="space-y-4">
        <div className="rounded-2xl border border-emerald-500/25 bg-emerald-500/5 p-6">
          <p className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground">
            <DollarSign className="size-4" /> Creator Rewards estimate
          </p>
          <p className="mt-2 text-3xl font-bold text-emerald-600 dark:text-emerald-400">
            {usd(rewards.low)} – {usd(rewards.high)}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            for {v.toLocaleString()} qualified views (at $0.40–$1.00 per 1,000)
          </p>
        </div>

        <div className="rounded-2xl border bg-card p-6">
          <p className="text-sm font-medium text-muted-foreground">Brand deal estimate (per sponsored video)</p>
          {tier ? (
            <>
              <p className="mt-2 text-3xl font-bold">
                {usd(tier.per[0])} – {usd(tier.per[1])}
              </p>
              <p className="mt-1 text-sm text-muted-foreground">{tier.label} creator tier</p>
            </>
          ) : (
            <p className="mt-2 text-sm text-muted-foreground">
              Enter at least 1,000 followers to see brand deal benchmarks.
            </p>
          )}
          <div className="mt-4 space-y-1.5 text-xs text-muted-foreground">
            {BRAND_TIERS.map((t) => (
              <div key={t.label} className={`flex justify-between ${tier?.label === t.label ? "font-semibold text-foreground" : ""}`}>
                <span>{t.label}</span>
                <span className="tabular-nums">{usd(t.per[0])} – {usd(t.per[1])}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
