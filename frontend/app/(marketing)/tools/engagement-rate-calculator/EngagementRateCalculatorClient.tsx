"use client";

import { useMemo, useState } from "react";

type Platform = "instagram" | "tiktok" | "youtube";

const PLATFORMS: { id: Platform; label: string; note: string }[] = [
  { id: "instagram", label: "Instagram", note: "(likes + comments) ÷ followers × 100" },
  { id: "tiktok", label: "TikTok", note: "(likes + comments + shares) ÷ views × 100" },
  { id: "youtube", label: "YouTube", note: "(likes + comments) ÷ views × 100" },
];

// Rough industry benchmarks for a "good" engagement rate.
function rating(platform: Platform, rate: number): { label: string; color: string } {
  const good = platform === "tiktok" ? 6 : platform === "youtube" ? 4 : 3;
  const ok = platform === "tiktok" ? 3 : platform === "youtube" ? 2 : 1;
  if (rate >= good) return { label: "Excellent", color: "text-emerald-600 dark:text-emerald-400" };
  if (rate >= ok) return { label: "Good", color: "text-amber-600 dark:text-amber-400" };
  if (rate > 0) return { label: "Below average", color: "text-red-500" };
  return { label: "—", color: "text-muted-foreground" };
}

const numField = (v: string) => Math.max(0, Number(v) || 0);

export default function EngagementRateCalculatorClient() {
  const [platform, setPlatform] = useState<Platform>("instagram");
  const [likes, setLikes] = useState("");
  const [comments, setComments] = useState("");
  const [shares, setShares] = useState("");
  const [followers, setFollowers] = useState("");
  const [views, setViews] = useState("");

  const usesViews = platform === "tiktok" || platform === "youtube";
  const usesShares = platform === "tiktok";

  const rate = useMemo(() => {
    const l = numField(likes);
    const c = numField(comments);
    const sh = numField(shares);
    const denom = usesViews ? numField(views) : numField(followers);
    if (denom <= 0) return 0;
    const interactions = l + c + (usesShares ? sh : 0);
    return (interactions / denom) * 100;
  }, [likes, comments, shares, followers, views, usesViews, usesShares]);

  const r = rating(platform, rate);

  return (
    <div className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,420px)_1fr]">
      <div className="rounded-2xl border bg-card p-6">
        <div className="flex gap-2">
          {PLATFORMS.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => setPlatform(p.id)}
              className={`flex-1 rounded-md border px-3 py-2 text-sm font-medium transition-colors ${
                platform === p.id ? "border-primary bg-primary/10 text-primary" : "hover:bg-muted"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
        <p className="mt-3 text-xs text-muted-foreground">
          Formula: {PLATFORMS.find((p) => p.id === platform)!.note}
        </p>

        <div className="mt-5 space-y-4">
          <Field label="Likes" value={likes} onChange={setLikes} />
          <Field label="Comments" value={comments} onChange={setComments} />
          {usesShares && <Field label="Shares" value={shares} onChange={setShares} />}
          {usesViews ? (
            <Field label="Views" value={views} onChange={setViews} />
          ) : (
            <Field label="Followers" value={followers} onChange={setFollowers} />
          )}
        </div>
      </div>

      <div className="flex flex-col justify-center rounded-2xl border bg-muted/30 p-8 text-center">
        <p className="text-sm text-muted-foreground">Engagement rate</p>
        <p className="mt-2 text-5xl font-bold tabular-nums">{rate.toFixed(2)}%</p>
        <p className={`mt-2 text-lg font-semibold ${r.color}`}>{r.label}</p>
        <div className="mx-auto mt-6 max-w-sm text-left text-sm text-muted-foreground">
          <p className="font-medium text-foreground">What counts as good?</p>
          <ul className="mt-2 space-y-1">
            <li>Instagram: 1–3% is solid, 3%+ is excellent.</li>
            <li>TikTok: 3–6% is solid, 6%+ is excellent (by views).</li>
            <li>YouTube: 2–4% is solid, 4%+ is excellent (by views).</li>
          </ul>
          <p className="mt-3 text-xs">
            Smaller accounts usually see higher rates than large ones, so compare against creators of a
            similar size.
          </p>
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium">{label}</span>
      <input
        type="number"
        min={0}
        inputMode="numeric"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-md border bg-background px-3 py-2.5 outline-none focus:ring-2 focus:ring-primary/40"
        placeholder="0"
      />
    </label>
  );
}
