"use client";

import { useMemo, useState } from "react";
import { ArrowDownUp, Coins, DollarSign, Search } from "lucide-react";

// TikTok sells coins at slightly different rates in-app (Apple/Google take a
// cut) vs on tiktok.com. Creators receive Diamonds worth 50% of the coin
// value and TikTok pays about $0.005 per Diamond.
const COIN_PRICE_WEB = 0.0105; // USD per coin buying on tiktok.com
const COIN_PRICE_APP = 0.0132; // USD per coin buying inside the app
const CREATOR_PER_COIN = 0.005; // USD a creator nets per coin gifted

const GIFTS: { name: string; emoji: string; coins: number }[] = [
  { name: "Rose", emoji: "\u{1F339}", coins: 1 },
  { name: "TikTok", emoji: "\u{1F3B5}", coins: 1 },
  { name: "Ice Cream Cone", emoji: "\u{1F366}", coins: 1 },
  { name: "Heart Me", emoji: "\u{1F497}", coins: 1 },
  { name: "Finger Heart", emoji: "\u{1FAF0}", coins: 5 },
  { name: "Panda", emoji: "\u{1F43C}", coins: 5 },
  { name: "Hi Bear", emoji: "\u{1F43B}", coins: 10 },
  { name: "Friendship Necklace", emoji: "\u{1F4FF}", coins: 10 },
  { name: "Perfume", emoji: "\u{1F9F4}", coins: 20 },
  { name: "Doughnut", emoji: "\u{1F369}", coins: 30 },
  { name: "Paper Crane", emoji: "\u{1F9A2}", coins: 99 },
  { name: "Confetti", emoji: "\u{1F389}", coins: 100 },
  { name: "Hand Hearts", emoji: "\u{1FAF6}", coins: 100 },
  { name: "Marvelous Confetti", emoji: "\u{1F38A}", coins: 199 },
  { name: "Corgi", emoji: "\u{1F436}", coins: 299 },
  { name: "Boxing Gloves", emoji: "\u{1F94A}", coins: 299 },
  { name: "Money Gun", emoji: "\u{1F4B8}", coins: 500 },
  { name: "Swan", emoji: "\u{1F9A2}", coins: 699 },
  { name: "Train", emoji: "\u{1F682}", coins: 899 },
  { name: "Galaxy", emoji: "\u{1F30C}", coins: 1000 },
  { name: "Diamond Ring", emoji: "\u{1F48D}", coins: 1500 },
  { name: "Interstellar", emoji: "\u{1F680}", coins: 10000 },
  { name: "Sports Car", emoji: "\u{1F3CE}\uFE0F", coins: 7000 },
  { name: "Yacht", emoji: "\u{1F6E5}\uFE0F", coins: 9888 },
  { name: "Rocket", emoji: "\u{1F680}", coins: 20000 },
  { name: "Lion", emoji: "\u{1F981}", coins: 26999 },
  { name: "TikTok Universe", emoji: "\u{1FA90}", coins: 44999 },
];

const usd = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: n < 100 ? 2 : 0 });

export default function TikTokCoinCalculatorClient() {
  const [coins, setCoins] = useState("1000");
  const [dollars, setDollars] = useState("");
  const [mode, setMode] = useState<"coins" | "usd">("coins");
  const [query, setQuery] = useState("");

  const coinCount = mode === "coins" ? Number(coins) || 0 : (Number(dollars) || 0) / COIN_PRICE_WEB;

  const gifts = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = q ? GIFTS.filter((g) => g.name.toLowerCase().includes(q)) : GIFTS;
    return [...list].sort((a, b) => a.coins - b.coins);
  }, [query]);

  return (
    <div className="mt-8 space-y-8">
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border bg-card p-6">
          <div className="flex items-center justify-between gap-3">
            <h2 className="font-semibold">
              {mode === "coins" ? "Coins \u2192 US Dollars" : "US Dollars \u2192 Coins"}
            </h2>
            <button
              type="button"
              onClick={() => setMode(mode === "coins" ? "usd" : "coins")}
              className="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-muted"
            >
              <ArrowDownUp className="size-3.5" />
              Switch
            </button>
          </div>

          {mode === "coins" ? (
            <label className="mt-4 block">
              <span className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
                <Coins className="size-4 text-amber-500" /> TikTok coins
              </span>
              <input
                type="number"
                min={0}
                inputMode="numeric"
                value={coins}
                onChange={(e) => setCoins(e.target.value)}
                className="w-full rounded-md border bg-background px-3 py-2.5 text-lg font-semibold outline-none focus:ring-2 focus:ring-primary/40"
                placeholder="e.g. 1000"
              />
            </label>
          ) : (
            <label className="mt-4 block">
              <span className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
                <DollarSign className="size-4 text-emerald-500" /> US Dollars
              </span>
              <input
                type="number"
                min={0}
                inputMode="decimal"
                value={dollars}
                onChange={(e) => setDollars(e.target.value)}
                className="w-full rounded-md border bg-background px-3 py-2.5 text-lg font-semibold outline-none focus:ring-2 focus:ring-primary/40"
                placeholder="e.g. 10"
              />
            </label>
          )}

          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border bg-muted/40 p-4">
              <p className="text-xs text-muted-foreground">Cost on tiktok.com</p>
              <p className="mt-1 text-xl font-bold">{usd(coinCount * COIN_PRICE_WEB)}</p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">{"\u2248"} $1.05 per 100 coins</p>
            </div>
            <div className="rounded-xl border bg-muted/40 p-4">
              <p className="text-xs text-muted-foreground">Cost in the app</p>
              <p className="mt-1 text-xl font-bold">{usd(coinCount * COIN_PRICE_APP)}</p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">{"\u2248"} $1.32 per 100 coins</p>
            </div>
            <div className="rounded-xl border border-emerald-500/25 bg-emerald-500/5 p-4">
              <p className="text-xs text-muted-foreground">Creator receives</p>
              <p className="mt-1 text-xl font-bold text-emerald-600 dark:text-emerald-400">
                {usd(coinCount * CREATOR_PER_COIN)}
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">{"\u2248"} $0.005 per coin gifted</p>
            </div>
          </div>
          {mode === "usd" && (
            <p className="mt-3 text-sm text-muted-foreground">
              {usd(Number(dollars) || 0)} buys about{" "}
              <strong className="text-foreground">{Math.floor(coinCount).toLocaleString()} coins</strong> on
              tiktok.com ({Math.floor(((Number(dollars) || 0) / COIN_PRICE_APP)).toLocaleString()} in the app).
            </p>
          )}
        </div>

        <div className="rounded-2xl border bg-card p-6">
          <h2 className="font-semibold">TikTok gift prices</h2>
          <label className="relative mt-4 block">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full rounded-md border bg-background py-2 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-primary/40"
              placeholder="Search a gift, e.g. Galaxy"
            />
          </label>
          <div className="mt-3 max-h-[340px] overflow-y-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-muted/80 backdrop-blur">
                <tr className="text-left text-xs text-muted-foreground">
                  <th className="px-3 py-2 font-medium">Gift</th>
                  <th className="px-3 py-2 text-right font-medium">Coins</th>
                  <th className="px-3 py-2 text-right font-medium">Costs you</th>
                  <th className="px-3 py-2 text-right font-medium">Creator gets</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {gifts.map((g) => (
                  <tr key={g.name}>
                    <td className="px-3 py-2">
                      <span className="mr-1.5">{g.emoji}</span>
                      {g.name}
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums">{g.coins.toLocaleString()}</td>
                    <td className="px-3 py-2 text-right tabular-nums">{usd(g.coins * COIN_PRICE_WEB)}</td>
                    <td className="px-3 py-2 text-right tabular-nums text-emerald-600 dark:text-emerald-400">
                      {usd(g.coins * CREATOR_PER_COIN)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <p className="text-xs text-muted-foreground">
        Rates are estimates based on TikTok&apos;s published recharge bundles and typical creator payout of
        $0.005 per Diamond. TikTok adjusts regional pricing occasionally, so treat results as close
        approximations rather than exact invoices.
      </p>
    </div>
  );
}
