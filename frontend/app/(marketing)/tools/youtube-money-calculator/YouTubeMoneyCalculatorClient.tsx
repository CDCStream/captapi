"use client";

import { useMemo, useState } from "react";
import { DollarSign, Eye, PlaySquare } from "lucide-react";

// Creator RPM (what lands in the creator's pocket after YouTube's 45% ad split)
// varies enormously by niche. Ranges reflect commonly reported US long-form RPMs.
const NICHES = [
  { label: "Finance / Investing", rpm: [8, 22] },
  { label: "Tech / Software / SaaS", rpm: [5, 15] },
  { label: "Business / Marketing", rpm: [4, 12] },
  { label: "Education / How-to", rpm: [3, 8] },
  { label: "Health & Fitness", rpm: [2.5, 6] },
  { label: "Lifestyle / Vlogs", rpm: [1.5, 4] },
  { label: "Gaming", rpm: [1, 3] },
  { label: "Entertainment / Reactions", rpm: [0.8, 2.5] },
  { label: "Music", rpm: [0.5, 1.5] },
];

// Shorts pay from a pooled fund: roughly $0.05-$0.10 per 1,000 Shorts views.
const SHORTS_RPM = [0.05, 0.1];

const usd = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: n < 10 ? 2 : 0 });

const parse = (v: string) => Math.max(0, Number(v.replace(/[,\s]/g, "")) || 0);

export default function YouTubeMoneyCalculatorClient() {
  const [views, setViews] = useState("100000");
  const [nicheIdx, setNicheIdx] = useState(3);
  const [format, setFormat] = useState<"long" | "shorts">("long");

  const v = parse(views);
  const niche = NICHES[nicheIdx];

  const est = useMemo(() => {
    const [lo, hi] = format === "long" ? niche.rpm : SHORTS_RPM;
    return { low: (v / 1000) * lo, high: (v / 1000) * hi };
  }, [v, niche, format]);

  const monthly = useMemo(() => ({ low: est.low, high: est.high }), [est]);

  return (
    <div className="mt-8 grid gap-6 lg:grid-cols-2">
      <div className="rounded-2xl border bg-card p-6">
        <h2 className="font-semibold">Your numbers</h2>

        <div className="mt-4 flex gap-2">
          <button
            onClick={() => setFormat("long")}
            className={`flex-1 rounded-md border px-3 py-2 text-sm font-medium transition ${
              format === "long" ? "border-primary bg-primary text-primary-foreground" : "bg-background hover:border-primary/40"
            }`}
          >
            Long-form videos
          </button>
          <button
            onClick={() => setFormat("shorts")}
            className={`flex-1 rounded-md border px-3 py-2 text-sm font-medium transition ${
              format === "shorts" ? "border-primary bg-primary text-primary-foreground" : "bg-background hover:border-primary/40"
            }`}
          >
            Shorts
          </button>
        </div>

        <label className="mt-4 block">
          <span className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
            <Eye className="size-4 text-muted-foreground" /> Monetized views per month
          </span>
          <input
            inputMode="numeric"
            value={views}
            onChange={(e) => setViews(e.target.value)}
            className="w-full rounded-md border bg-background px-3 py-2.5 text-lg font-semibold outline-none focus:ring-2 focus:ring-primary/40"
            placeholder="e.g. 100000"
          />
        </label>

        {format === "long" && (
          <label className="mt-4 block">
            <span className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
              <PlaySquare className="size-4 text-muted-foreground" /> Channel niche
            </span>
            <select
              value={nicheIdx}
              onChange={(e) => setNicheIdx(Number(e.target.value))}
              className="w-full rounded-md border bg-background px-3 py-2.5 text-sm font-medium outline-none focus:ring-2 focus:ring-primary/40"
            >
              {NICHES.map((n, i) => (
                <option key={n.label} value={i}>
                  {n.label} (RPM ${n.rpm[0]}{"\u2013"}${n.rpm[1]})
                </option>
              ))}
            </select>
          </label>
        )}

        <p className="mt-4 text-xs text-muted-foreground">
          Estimates use creator RPM (your share after YouTube keeps 45% of ad revenue; 55% larger cut on
          Shorts). Requires the YouTube Partner Program: 1,000 subscribers + 4,000 watch hours (or 10M
          Shorts views in 90 days).
        </p>
      </div>

      <div className="space-y-4">
        <div className="rounded-2xl border border-emerald-500/25 bg-emerald-500/5 p-6">
          <p className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground">
            <DollarSign className="size-4" /> Estimated ad revenue / month
          </p>
          <p className="mt-2 text-3xl font-bold text-emerald-600 dark:text-emerald-400">
            {usd(monthly.low)} {"\u2013"} {usd(monthly.high)}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            for {v.toLocaleString()} {format === "shorts" ? "Shorts" : "long-form"} views
            {format === "long" ? ` in ${niche.label}` : " (pooled Shorts fund rates)"}
          </p>
        </div>

        <div className="rounded-2xl border bg-card p-6">
          <p className="text-sm font-medium text-muted-foreground">Yearly projection at this pace</p>
          <p className="mt-2 text-2xl font-bold">
            {usd(monthly.low * 12)} {"\u2013"} {usd(monthly.high * 12)}
          </p>
          {format === "long" && (
            <div className="mt-4 space-y-1.5 text-xs text-muted-foreground">
              {NICHES.map((n, i) => (
                <div key={n.label} className={`flex justify-between ${i === nicheIdx ? "font-semibold text-foreground" : ""}`}>
                  <span>{n.label}</span>
                  <span className="tabular-nums">
                    ${n.rpm[0]} {"\u2013"} ${n.rpm[1]} RPM
                  </span>
                </div>
              ))}
            </div>
          )}
          {format === "shorts" && (
            <p className="mt-3 text-xs text-muted-foreground">
              Shorts pay $0.05{"\u2013"}$0.10 per 1,000 views regardless of niche — roughly 50{"\u00d7"} less
              than long-form. Most Shorts creators monetize through brand deals and funneling viewers to
              long-form content instead.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
