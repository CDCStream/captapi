"use client";

import { useMemo, useState } from "react";
import { ShieldQuestion, ShieldX, ShieldCheck } from "lucide-react";

interface Sign {
  id: string;
  text: string;
  weight: number; // how strongly this indicates a block
}

const PLATFORMS: { id: string; label: string; signs: Sign[]; tip: string }[] = [
  {
    id: "instagram",
    label: "Instagram",
    tip: "The strongest single test: search their exact @username while logged in, then check the same URL (instagram.com/username) from a logged-out browser. Visible logged-out but not logged-in = you are blocked.",
    signs: [
      { id: "ig1", text: "Their profile doesn't appear when I search their exact username", weight: 2 },
      { id: "ig2", text: "I can open their profile but it says \u201cNo posts yet\u201d even though they post", weight: 3 },
      { id: "ig3", text: "The follower/following counts show but no posts load", weight: 3 },
      { id: "ig4", text: "Our old DM thread is still there but their name is unclickable / posts say unavailable", weight: 3 },
      { id: "ig5", text: "My comments on their posts have disappeared", weight: 2 },
      { id: "ig6", text: "Their profile opens normally in a logged-out/incognito browser", weight: 3 },
      { id: "ig7", text: "I can't tag or mention them anymore", weight: 2 },
    ],
  },
  {
    id: "snapchat",
    label: "Snapchat",
    tip: "The clearest test: search their exact username from a friend's account or a fresh account. If they show up there but not on yours, you are blocked (removed friends still appear in search).",
    signs: [
      { id: "sc1", text: "They vanished from my friends list AND search finds nothing", weight: 3 },
      { id: "sc2", text: "Our chat conversation disappeared from my chat list", weight: 2 },
      { id: "sc3", text: "Messages I send say \u201cpending\u201d or never deliver", weight: 1 },
      { id: "sc4", text: "A friend's account CAN find their username in search", weight: 3 },
      { id: "sc5", text: "Their Bitmoji/story no longer appears anywhere", weight: 1 },
    ],
  },
  {
    id: "whatsapp",
    label: "WhatsApp",
    tip: "No single WhatsApp sign is conclusive — privacy settings can mimic all of them. It's the combination (one check mark forever + no profile photo + no last seen + calls never connect) that points to a block.",
    signs: [
      { id: "wa1", text: "My messages show only one check mark, permanently", weight: 3 },
      { id: "wa2", text: "Their profile photo disappeared or never updates", weight: 2 },
      { id: "wa3", text: "I can't see their last seen or online status anymore", weight: 1 },
      { id: "wa4", text: "My calls to them ring once (or not at all) and never connect", weight: 2 },
      { id: "wa5", text: "I can't add them to a group (\u201ccan't add this contact\u201d error)", weight: 3 },
      { id: "wa6", text: "Status updates from them stopped appearing", weight: 1 },
    ],
  },
];

function verdict(score: number, max: number): { label: string; desc: string; tone: "high" | "mid" | "low" } {
  const pct = max === 0 ? 0 : score / max;
  if (pct >= 0.6) return { label: "Very likely blocked", desc: "Multiple strong signals point to a block. Run the platform tip below to confirm.", tone: "high" };
  if (pct >= 0.3) return { label: "Possibly blocked", desc: "Some signals match, but privacy settings or a deactivated account could also explain them.", tone: "mid" };
  return { label: "Probably not blocked", desc: "Few or no block signals. They may have deactivated, gone private, or simply not replied.", tone: "low" };
}

const TONE_STYLES = {
  high: { cls: "border-red-500/30 bg-red-500/5 text-red-600 dark:text-red-400", icon: <ShieldX className="size-6" /> },
  mid: { cls: "border-amber-500/30 bg-amber-500/5 text-amber-600 dark:text-amber-400", icon: <ShieldQuestion className="size-6" /> },
  low: { cls: "border-emerald-500/30 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400", icon: <ShieldCheck className="size-6" /> },
};

export default function AmIBlockedClient() {
  const [platformId, setPlatformId] = useState("instagram");
  const [checked, setChecked] = useState<Record<string, boolean>>({});

  const platform = PLATFORMS.find((p) => p.id === platformId)!;
  const { score, max } = useMemo(() => {
    const max = platform.signs.reduce((s, x) => s + x.weight, 0);
    const score = platform.signs.reduce((s, x) => s + (checked[x.id] ? x.weight : 0), 0);
    return { score, max };
  }, [platform, checked]);

  const v = verdict(score, max);
  const tone = TONE_STYLES[v.tone];
  const anyChecked = platform.signs.some((s) => checked[s.id]);

  return (
    <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_minmax(0,360px)]">
      <div>
        <div className="flex flex-wrap gap-2">
          {PLATFORMS.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => { setPlatformId(p.id); setChecked({}); }}
              className={`rounded-full border px-4 py-2 text-sm font-medium transition-colors ${
                platformId === p.id ? "border-primary bg-primary/10 text-primary" : "hover:bg-muted"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>

        <p className="mt-4 text-sm text-muted-foreground">Check every sign that matches what you see:</p>
        <div className="mt-3 space-y-2">
          {platform.signs.map((s) => (
            <label
              key={s.id}
              className={`flex cursor-pointer items-start gap-3 rounded-xl border p-3.5 text-sm transition-colors ${
                checked[s.id] ? "border-primary/50 bg-primary/5" : "hover:bg-muted/50"
              }`}
            >
              <input
                type="checkbox"
                checked={!!checked[s.id]}
                onChange={(e) => setChecked((c) => ({ ...c, [s.id]: e.target.checked }))}
                className="mt-0.5 size-4 accent-[var(--primary)]"
              />
              <span>{s.text}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="lg:sticky lg:top-24 h-fit space-y-4">
        <div className={`rounded-2xl border p-6 ${tone.cls}`}>
          <div className="flex items-center gap-3">
            {tone.icon}
            <p className="text-xl font-bold">{anyChecked ? v.label : "Check the signs"}</p>
          </div>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            {anyChecked ? v.desc : "Tick the boxes on the left as you verify each sign in the app."}
          </p>
          {anyChecked && (
            <p className="mt-3 text-xs text-muted-foreground">
              Signal strength: {score}/{max}
            </p>
          )}
        </div>
        <div className="rounded-2xl border bg-muted/40 p-5 text-sm leading-relaxed">
          <p className="font-semibold">Definitive test for {platform.label}</p>
          <p className="mt-1.5 text-muted-foreground">{platform.tip}</p>
        </div>
      </div>
    </div>
  );
}
