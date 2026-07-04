import type { Metadata } from "next";
import Link from "next/link";
import { SITE_URL } from "@/lib/api-catalog";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const TITLE = "API Status - Live Endpoint Health";
const DESCRIPTION =
  "Live health for every Captapi platform: success rates, request volumes, and response times over the last 24 hours. If something goes sideways, it shows up here first.";

export const metadata: Metadata = {
  title: `${TITLE} | Captapi`,
  description: DESCRIPTION,
  alternates: { canonical: `${SITE_URL}/status` },
  openGraph: {
    title: TITLE,
    description: DESCRIPTION,
    url: `${SITE_URL}/status`,
    type: "website",
  },
};

export const revalidate = 120;

interface PlatformHealth {
  platform: string;
  status: "operational" | "degraded" | "outage" | "no_data";
  success_rate: number | null;
  requests_24h: number;
  avg_response_ms: number | null;
}

interface StatusData {
  overall: { status: string; success_rate: number | null; requests_24h: number };
  platforms: PlatformHealth[];
  window_hours: number;
  generated_at: string;
}

const STATUS_STYLE: Record<string, { label: string; dot: string; text: string }> = {
  operational: { label: "Operational", dot: "bg-emerald-500", text: "text-emerald-600 dark:text-emerald-400" },
  degraded: { label: "Degraded", dot: "bg-amber-500", text: "text-amber-600 dark:text-amber-400" },
  outage: { label: "Outage", dot: "bg-red-500", text: "text-red-600 dark:text-red-400" },
  no_data: { label: "No data", dot: "bg-muted-foreground/40", text: "text-muted-foreground" },
};

function prettyPlatform(slug: string): string {
  const NAMES: Record<string, string> = {
    youtube: "YouTube",
    tiktok: "TikTok",
    "tiktok-shop": "TikTok Shop",
    tiktok_shop: "TikTok Shop",
    instagram: "Instagram",
    facebook: "Facebook",
    twitter: "X / Twitter",
    reddit: "Reddit",
    threads: "Threads",
    bluesky: "Bluesky",
    pinterest: "Pinterest",
    linkedin: "LinkedIn",
    rumble: "Rumble",
    github: "GitHub",
    google: "Google",
    twitch: "Twitch",
    spotify: "Spotify",
    soundcloud: "SoundCloud",
    linktree: "Linktree",
    snapchat: "Snapchat",
    "truth-social": "Truth Social",
    truth_social: "Truth Social",
    kick: "Kick",
    kwai: "Kwai",
    komi: "Komi",
    pillar: "Pillar",
    linkbio: "Linkbio",
    linkme: "Linkme",
    "amazon-shop": "Amazon Shop",
    amazon_shop: "Amazon Shop",
    "ad-library": "Ad Libraries",
    ad_library: "Ad Libraries",
    "age-gender": "Age & Gender",
    age_gender: "Age & Gender",
    analytics: "Analytics",
    account: "Account",
    other: "Other",
  };
  return NAMES[slug] ?? slug.charAt(0).toUpperCase() + slug.slice(1);
}

async function fetchStatus(): Promise<StatusData | null> {
  try {
    const res = await fetch(`${API_URL}/v1/status`, { next: { revalidate: 120 } });
    if (!res.ok) return null;
    const body = await res.json();
    return body?.data ?? null;
  } catch {
    return null;
  }
}

export default async function StatusPage() {
  const data = await fetchStatus();

  return (
    <div className="py-16">
      <div className="container max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold tracking-tight">API Status</h1>
          <p className="mt-3 text-muted-foreground max-w-2xl mx-auto">
            Live health for every Captapi platform, computed from real production
            traffic over the last 24 hours. Refreshes every 2 minutes.
          </p>
        </div>

        {data === null ? (
          <div className="rounded-xl border bg-card p-8 text-center text-muted-foreground">
            Status data is temporarily unavailable. The API itself may still be
            fine — try{" "}
            <a className="underline" href={`${API_URL}/healthz`}>
              the health check
            </a>{" "}
            or email{" "}
            <a className="underline" href="mailto:support@captapi.com">
              support@captapi.com
            </a>
            .
          </div>
        ) : (
          <>
            <div className="rounded-xl border bg-card p-6 mb-8 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span
                  className={`h-3 w-3 rounded-full ${STATUS_STYLE[data.overall.status]?.dot ?? "bg-muted-foreground/40"}`}
                />
                <span className="text-lg font-semibold">
                  {data.overall.status === "operational"
                    ? "All systems operational"
                    : STATUS_STYLE[data.overall.status]?.label ?? data.overall.status}
                </span>
              </div>
              <div className="text-sm text-muted-foreground">
                {data.overall.success_rate !== null && (
                  <span className="mr-4">
                    {data.overall.success_rate}% success rate
                  </span>
                )}
                <span>
                  {data.overall.requests_24h.toLocaleString()} requests / 24h
                </span>
              </div>
            </div>

            <div className="rounded-xl border bg-card divide-y">
              {data.platforms.map((p) => {
                const style = STATUS_STYLE[p.status] ?? STATUS_STYLE.no_data;
                return (
                  <div
                    key={p.platform}
                    className="flex items-center justify-between gap-4 px-6 py-4"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span className={`h-2.5 w-2.5 rounded-full shrink-0 ${style.dot}`} />
                      <span className="font-medium truncate">
                        {prettyPlatform(p.platform)}
                      </span>
                    </div>
                    <div className="flex items-center gap-6 text-sm text-muted-foreground shrink-0">
                      <span className="hidden sm:inline">
                        {p.requests_24h.toLocaleString()} req
                      </span>
                      {p.avg_response_ms !== null && (
                        <span className="hidden md:inline">
                          {(p.avg_response_ms / 1000).toFixed(2)}s avg
                        </span>
                      )}
                      <span className={`font-medium ${style.text}`}>
                        {p.success_rate !== null ? `${p.success_rate}%` : "—"}
                      </span>
                    </div>
                  </div>
                );
              })}
              {data.platforms.length === 0 && (
                <div className="px-6 py-8 text-center text-muted-foreground">
                  No traffic in the last {data.window_hours} hours.
                </div>
              )}
            </div>

            <p className="mt-6 text-xs text-muted-foreground text-center">
              Success rate counts server-side failures only (HTTP 5xx). Client
              errors such as invalid URLs or insufficient credits do not affect
              platform health. Generated{" "}
              {new Date(data.generated_at).toLocaleString("en-US", {
                timeZone: "UTC",
                dateStyle: "medium",
                timeStyle: "short",
              })}{" "}
              UTC. Raw JSON:{" "}
              <a className="underline" href={`${API_URL}/v1/status`}>
                /v1/status
              </a>
              .
            </p>
          </>
        )}

        <div className="mt-12 rounded-xl border bg-card p-8 text-center">
          <h2 className="text-2xl font-bold">Seeing an issue we missed?</h2>
          <p className="mt-2 text-muted-foreground">
            Email{" "}
            <a className="underline" href="mailto:support@captapi.com">
              support@captapi.com
            </a>{" "}
            and a human will look at it — usually within hours.
          </p>
          <p className="mt-4 text-sm">
            <Link className="underline text-muted-foreground" href="/docs">
              Back to the docs
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
