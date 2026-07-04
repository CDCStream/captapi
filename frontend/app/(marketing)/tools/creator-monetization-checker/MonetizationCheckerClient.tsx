"use client";

import { useMemo, useState } from "react";
import { CheckCircle2, XCircle, Users, Eye } from "lucide-react";

interface Program {
  name: string;
  followersNeeded: number;
  viewsNeeded: number; // interpreted per viewsLabel
  extra: string;
}

interface PlatformConfig {
  id: string;
  label: string;
  followersLabel: string;
  viewsLabel: string;
  programs: Program[];
}

const PLATFORMS: PlatformConfig[] = [
  {
    id: "tiktok",
    label: "TikTok",
    followersLabel: "Followers",
    viewsLabel: "Video views (last 30 days)",
    programs: [
      { name: "Creator Rewards Program", followersNeeded: 10000, viewsNeeded: 100000, extra: "18+, original videos over 1 minute, eligible country" },
      { name: "LIVE + gifts", followersNeeded: 1000, viewsNeeded: 0, extra: "18+ to go live and receive gifts" },
      { name: "TikTok Shop (creator)", followersNeeded: 1000, viewsNeeded: 0, extra: "18+, good standing; commission per sale" },
      { name: "Subscription", followersNeeded: 10000, viewsNeeded: 0, extra: "18+; or 1,000 followers for LIVE creators" },
    ],
  },
  {
    id: "youtube",
    label: "YouTube",
    followersLabel: "Subscribers",
    viewsLabel: "Public watch hours (last 12 months)",
    programs: [
      { name: "Partner Program (full ads revenue)", followersNeeded: 1000, viewsNeeded: 4000, extra: "OR 10M public Shorts views in 90 days; 2-step verification, no active strikes" },
      { name: "Fan funding tier (memberships, Supers)", followersNeeded: 500, viewsNeeded: 3000, extra: "OR 3M Shorts views in 90 days; plus 3 public uploads in last 90 days" },
    ],
  },
  {
    id: "instagram",
    label: "Instagram",
    followersLabel: "Followers",
    viewsLabel: "Views (last 30 days)",
    programs: [
      { name: "Subscriptions", followersNeeded: 10000, viewsNeeded: 0, extra: "18+, professional account, eligible country (US and select markets)" },
      { name: "Gifts on Reels", followersNeeded: 5000, viewsNeeded: 0, extra: "18+, professional account, eligible country" },
      { name: "Content monetization (bonuses)", followersNeeded: 0, viewsNeeded: 0, extra: "Invite-only — Instagram notifies eligible professional accounts" },
    ],
  },
  {
    id: "twitch",
    label: "Twitch",
    followersLabel: "Followers",
    viewsLabel: "Average concurrent viewers",
    programs: [
      { name: "Affiliate (subs, Bits, ads)", followersNeeded: 50, viewsNeeded: 3, extra: "Plus 500 minutes broadcast on 7 unique days in last 30 days" },
      { name: "Partner (better splits, more emotes)", followersNeeded: 0, viewsNeeded: 75, extra: "Plus 12 hours streamed on 12 different days in last 30 days" },
    ],
  },
];

const parse = (v: string) => Math.max(0, Number(v.replace(/[,\s]/g, "")) || 0);
const fmt = (n: number) => n.toLocaleString("en-US");

export default function MonetizationCheckerClient() {
  const [platformId, setPlatformId] = useState("tiktok");
  const [followers, setFollowers] = useState("");
  const [views, setViews] = useState("");

  const platform = PLATFORMS.find((p) => p.id === platformId)!;
  const f = parse(followers);
  const v = parse(views);
  const hasInput = followers.trim() !== "" || views.trim() !== "";

  const results = useMemo(
    () =>
      platform.programs.map((prog) => {
        const okFollowers = f >= prog.followersNeeded;
        const okViews = v >= prog.viewsNeeded;
        const missing: string[] = [];
        if (!okFollowers) missing.push(`${fmt(prog.followersNeeded - f)} more ${platform.followersLabel.toLowerCase()}`);
        if (!okViews) missing.push(`${fmt(prog.viewsNeeded - v)} more ${platform.viewsLabel.toLowerCase()}`);
        return { prog, qualified: okFollowers && okViews, missing };
      }),
    [platform, f, v],
  );

  return (
    <div className="mt-8">
      <div className="flex flex-wrap gap-2">
        {PLATFORMS.map((p) => (
          <button
            key={p.id}
            type="button"
            onClick={() => { setPlatformId(p.id); setViews(""); }}
            className={`rounded-full border px-4 py-2 text-sm font-medium transition-colors ${
              platformId === p.id ? "border-primary bg-primary/10 text-primary" : "hover:bg-muted"
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <label className="block">
          <span className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
            <Users className="size-4 text-muted-foreground" /> {platform.followersLabel}
          </span>
          <input
            inputMode="numeric"
            value={followers}
            onChange={(e) => setFollowers(e.target.value)}
            className="w-full rounded-md border bg-background px-3 py-2.5 text-lg font-semibold outline-none focus:ring-2 focus:ring-primary/40"
            placeholder="e.g. 5000"
          />
        </label>
        <label className="block">
          <span className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
            <Eye className="size-4 text-muted-foreground" /> {platform.viewsLabel}
          </span>
          <input
            inputMode="numeric"
            value={views}
            onChange={(e) => setViews(e.target.value)}
            className="w-full rounded-md border bg-background px-3 py-2.5 text-lg font-semibold outline-none focus:ring-2 focus:ring-primary/40"
            placeholder="e.g. 50000"
          />
        </label>
      </div>

      <div className="mt-5 space-y-3">
        {results.map(({ prog, qualified, missing }) => (
          <div
            key={prog.name}
            className={`rounded-2xl border p-4 ${
              !hasInput ? "" : qualified ? "border-emerald-500/30 bg-emerald-500/5" : "border-red-500/20 bg-red-500/[0.03]"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-semibold">{prog.name}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  Needs: {prog.followersNeeded > 0 ? `${fmt(prog.followersNeeded)} ${platform.followersLabel.toLowerCase()}` : ""}
                  {prog.followersNeeded > 0 && prog.viewsNeeded > 0 ? " + " : ""}
                  {prog.viewsNeeded > 0 ? `${fmt(prog.viewsNeeded)} ${platform.viewsLabel.toLowerCase()}` : ""}
                  {prog.followersNeeded === 0 && prog.viewsNeeded === 0 ? "No public follower/view threshold" : ""}
                  {" \u00b7 "}{prog.extra}
                </p>
                {hasInput && !qualified && missing.length > 0 && (
                  <p className="mt-1.5 text-xs font-medium text-red-500">Missing: {missing.join(" and ")}</p>
                )}
              </div>
              {hasInput && (
                qualified
                  ? <CheckCircle2 className="size-6 shrink-0 text-emerald-500" />
                  : <XCircle className="size-6 shrink-0 text-red-400" />
              )}
            </div>
          </div>
        ))}
      </div>
      <p className="mt-3 text-xs text-muted-foreground">
        Thresholds are the published 2026 requirements; platforms also apply age, region, originality, and
        community-standing checks noted per program.
      </p>
    </div>
  );
}
