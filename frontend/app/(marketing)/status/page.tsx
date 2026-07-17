import type { Metadata } from "next";
import Link from "next/link";
import { SITE_URL } from "@/lib/api-catalog";
import { getServiceClient } from "@/lib/supabase/admin";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const TITLE = "API Status - Live Endpoint Health & Incident History";
const DESCRIPTION =
  "Live health for every Captapi platform, judged by the most recent responses. If something goes sideways, it shows up here first — and clears the moment it is fixed.";

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
  overall: { status: string; requests_24h: number };
  platforms: PlatformHealth[];
  window_hours: number;
  generated_at: string;
}

interface IncidentUpdate {
  at: string;
  status: string;
  message: string;
}

interface Incident {
  id: string;
  title: string;
  severity: "minor" | "major";
  status: "investigating" | "monitoring" | "resolved";
  started_at: string;
  resolved_at: string | null;
  updates: IncidentUpdate[];
}

const STATUS_STYLE: Record<string, { label: string; dot: string; text: string }> = {
  operational: { label: "Operational", dot: "bg-emerald-500", text: "text-emerald-600 dark:text-emerald-400" },
  degraded: { label: "Degraded", dot: "bg-amber-500", text: "text-amber-600 dark:text-amber-400" },
  outage: { label: "Outage", dot: "bg-red-500", text: "text-red-600 dark:text-red-400" },
  no_data: { label: "No data", dot: "bg-muted-foreground/40", text: "text-muted-foreground" },
};

const UPDATE_LABELS: Record<string, string> = {
  investigating: "Investigating",
  monitoring: "Monitoring",
  resolved: "Resolved",
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

async function fetchIncidents(): Promise<Incident[]> {
  const sb = getServiceClient();
  if (!sb) return [];
  const { data, error } = await sb
    .from("status_incidents")
    .select("*")
    .order("started_at", { ascending: false })
    .limit(50);
  if (error || !data) return [];
  return (data as Incident[]).map((row) => ({
    ...row,
    updates: Array.isArray(row.updates) ? row.updates : [],
  }));
}

function formatDay(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZone: "UTC",
  });
}

export default async function StatusPage() {
  const [data, incidents] = await Promise.all([fetchStatus(), fetchIncidents()]);
  const activeIncidents = incidents.filter((i) => i.status !== "resolved");

  return (
    <div className="py-16">
      <div className="container max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold tracking-tight">API Status</h1>
          <p className="mt-3 text-muted-foreground max-w-2xl mx-auto">
            Live health for every Captapi platform, judged by the most recent
            responses — not a daily average. If something goes sideways, it
            shows up here first and clears the moment it is fixed.
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
            {(() => {
              const issues = data.platforms.filter(
                (p) => p.status === "degraded" || p.status === "outage",
              );
              const allGood = issues.length === 0 && activeIncidents.length === 0;
              return (
                <>
                  <div
                    className={`rounded-xl border p-8 text-center ${
                      allGood
                        ? "border-emerald-500/25 bg-emerald-500/5"
                        : "border-amber-500/25 bg-amber-500/5"
                    }`}
                  >
                    <div className="flex items-center justify-center gap-3">
                      <span
                        className={`flex size-8 items-center justify-center rounded-full ${
                          allGood ? "bg-emerald-500/15" : "bg-amber-500/15"
                        }`}
                      >
                        <span
                          className={`size-3 rounded-full ${allGood ? "bg-emerald-500" : "bg-amber-500"}`}
                        />
                      </span>
                      <span className="text-xl font-semibold">
                        {allGood
                          ? "All systems running normally"
                          : activeIncidents.length > 0
                            ? "Active incident — see below"
                            : "Some platforms are having issues"}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Live status · refreshes every 2 minutes
                    </p>
                  </div>

                  {issues.length > 0 && (
                    <div className="mt-6 rounded-xl border bg-card divide-y">
                      {issues.map((p) => {
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
                            <span className={`text-sm font-medium shrink-0 ${style.text}`}>
                              {style.label}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </>
              );
            })()}

            <p className="mt-6 text-xs text-muted-foreground text-center">
              Health reflects each platform’s most recent responses: a platform
              only shows an issue while its latest requests are failing, and turns
              green again as soon as a request succeeds. Only server-side failures
              (HTTP 5xx) count — client errors such as invalid URLs or wrong query
              parameters never affect health.
              Last updated{" "}
              {new Date(data.generated_at).toLocaleString("en-US", {
                timeZone: "UTC",
                dateStyle: "medium",
                timeStyle: "short",
              })}{" "}
              UTC.
            </p>
          </>
        )}

        <div className="mt-16">
          <div className="mb-6">
            <p className="text-sm font-medium text-primary">History</p>
            <h2 className="text-2xl font-bold tracking-tight">Past incidents</h2>
            {incidents.length > 0 && (
              <p className="mt-1 text-sm text-muted-foreground">
                {incidents.length} total
              </p>
            )}
          </div>

          {incidents.length === 0 ? (
            <div className="rounded-xl border border-dashed p-10 text-center text-muted-foreground">
              No incidents reported yet — smooth sailing so far. When something
              breaks, the full timeline lands here.
            </div>
          ) : (
            <div className="space-y-6">
              {incidents.map((inc) => (
                <article key={inc.id} className="rounded-xl border bg-card p-6">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <h3 className="font-semibold">{inc.title}</h3>
                    {inc.severity === "major" && (
                      <span className="inline-flex items-center rounded-full border border-red-500/20 bg-red-500/10 px-2.5 py-0.5 text-xs font-medium text-red-600 dark:text-red-400">
                        Major incident
                      </span>
                    )}
                    <span
                      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${
                        inc.status === "resolved"
                          ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                          : "border-amber-500/20 bg-amber-500/10 text-amber-600 dark:text-amber-400"
                      }`}
                    >
                      {UPDATE_LABELS[inc.status] ?? inc.status}
                    </span>
                    <time
                      dateTime={inc.started_at}
                      className="ml-auto text-xs text-muted-foreground"
                    >
                      {formatDay(inc.started_at)}
                    </time>
                  </div>
                  {inc.updates.length > 0 && (
                    <div className="mt-4 space-y-3 border-l pl-4">
                      {[...inc.updates].reverse().map((u, i) => (
                        <div key={i} className="text-sm">
                          <p className="font-medium">
                            {UPDATE_LABELS[u.status] ?? u.status}
                            <span className="ml-2 font-normal text-xs text-muted-foreground">
                              {formatTime(u.at)} UTC
                            </span>
                          </p>
                          <p className="mt-0.5 text-muted-foreground">{u.message}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </article>
              ))}
            </div>
          )}
        </div>

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
            <Link className="underline text-muted-foreground" href="/changelog">
              View changelog →
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
