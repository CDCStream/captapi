"use client";

import { useMemo, useState } from "react";
import { Gift, DollarSign } from "lucide-react";

// US web prices as of 2026. Gifted subs cost the same as regular subs.
const TIERS = [
  { id: 1, label: "Tier 1", price: 5.99 },
  { id: 2, label: "Tier 2", price: 9.99 },
  { id: 3, label: "Tier 3", price: 24.99 },
];

const QUICK = [1, 5, 10, 20, 50, 100];
// Standard revenue share; some streamers have 60-70% via the Partner Plus program.
const STREAMER_CUT = 0.5;

const usd = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD" });

export default function GiftedSubCalculatorClient() {
  const [count, setCount] = useState("50");
  const [tierId, setTierId] = useState(1);

  const n = Math.max(0, Math.floor(Number(count.replace(/[,\s]/g, "")) || 0));
  const tier = TIERS.find((t) => t.id === tierId)!;

  const { cost, streamer } = useMemo(
    () => ({ cost: n * tier.price, streamer: n * tier.price * STREAMER_CUT }),
    [n, tier],
  );

  return (
    <div className="mt-8 grid gap-6 lg:grid-cols-2">
      <div className="rounded-2xl border bg-card p-6">
        <h2 className="font-semibold">Gift details</h2>
        <label className="mt-4 block">
          <span className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
            <Gift className="size-4 text-muted-foreground" /> Number of gifted subs
          </span>
          <input
            inputMode="numeric"
            value={count}
            onChange={(e) => setCount(e.target.value)}
            className="w-full rounded-md border bg-background px-3 py-2.5 text-lg font-semibold outline-none focus:ring-2 focus:ring-primary/40"
            placeholder="e.g. 50"
          />
        </label>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {QUICK.map((q) => (
            <button
              key={q}
              type="button"
              onClick={() => setCount(String(q))}
              className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
                n === q ? "border-primary bg-primary/10 text-primary" : "hover:bg-muted"
              }`}
            >
              {q}
            </button>
          ))}
        </div>
        <div className="mt-4">
          <span className="mb-1.5 block text-sm font-medium">Tier</span>
          <div className="flex gap-2">
            {TIERS.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTierId(t.id)}
                className={`flex-1 rounded-xl border p-3 text-center transition-colors ${
                  tierId === t.id ? "border-primary bg-primary/10" : "hover:bg-muted"
                }`}
              >
                <p className="text-sm font-semibold">{t.label}</p>
                <p className="text-xs text-muted-foreground">{usd(t.price)} each</p>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="rounded-2xl border border-primary/25 bg-primary/5 p-6">
          <p className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground">
            <DollarSign className="size-4" /> Total cost to the gifter
          </p>
          <p className="mt-2 text-4xl font-bold tabular-nums">{usd(cost)}</p>
          <p className="mt-1 text-sm text-muted-foreground">
            {n.toLocaleString()} {"\u00d7"} {tier.label} at {usd(tier.price)} each (US web price)
          </p>
        </div>
        <div className="rounded-2xl border border-emerald-500/25 bg-emerald-500/5 p-6">
          <p className="text-sm font-medium text-muted-foreground">What the streamer earns (typical 50% split)</p>
          <p className="mt-2 text-3xl font-bold tabular-nums text-emerald-600 dark:text-emerald-400">{usd(streamer)}</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Partner Plus streamers keep 60{"\u2013"}70%, so the same gift can be worth up to {usd(cost * 0.7)}.
          </p>
        </div>
        <div className="rounded-xl border bg-muted/40 p-4 text-xs text-muted-foreground">
          Prices vary by country since Twitch moved to local pricing; mobile app purchases cost more due to
          app-store fees. Gifted subs never auto-renew.
        </div>
      </div>
    </div>
  );
}
