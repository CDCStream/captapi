import { createClient } from "@/lib/supabase/server";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatNumber } from "@/lib/utils";
import {
  UsageCharts,
  type DailyPoint,
  type EndpointPoint,
  type PlatformPoint,
} from "@/components/dashboard/usage-charts";

export const dynamic = "force-dynamic";

const DAYS = 30;
const TOP_ENDPOINTS = 6;
const PLATFORMS = ["youtube", "tiktok", "instagram", "facebook", "other"] as const;

function dayKey(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function shortEndpoint(endpoint: string | null): string {
  if (!endpoint) return "unknown";
  return endpoint.replace(/^\/v1\//, "").replace(/^\//, "");
}

export default async function AnalyticsPage() {
  const sb = await createClient();
  const {
    data: { user },
  } = await sb.auth.getUser();

  const start = new Date();
  start.setUTCHours(0, 0, 0, 0);
  start.setUTCDate(start.getUTCDate() - (DAYS - 1));

  const { data: reqs } = await sb
    .from("requests")
    .select("endpoint, platform, credits_used, created_at")
    .eq("user_id", user!.id)
    .gte("created_at", start.toISOString())
    .order("created_at", { ascending: true });

  const rows = reqs ?? [];

  // Build a continuous list of day buckets so charts render a smooth line
  // even on days with no activity.
  const days: string[] = [];
  for (let i = 0; i < DAYS; i++) {
    const d = new Date(start);
    d.setUTCDate(start.getUTCDate() + i);
    days.push(dayKey(d));
  }

  const dailyMap = new Map<string, DailyPoint>();
  const platformMap = new Map<string, PlatformPoint>();
  for (const day of days) {
    dailyMap.set(day, { date: day, credits: 0, requests: 0 });
    platformMap.set(day, {
      date: day,
      youtube: 0,
      tiktok: 0,
      instagram: 0,
      facebook: 0,
      other: 0,
    });
  }

  // Endpoint totals (to pick the top N) + per-day per-endpoint values.
  const endpointTotals = new Map<string, number>();
  const endpointDayValues = new Map<string, Map<string, number>>();

  for (const r of rows) {
    const day = (r.created_at ?? "").slice(0, 10);
    if (!dailyMap.has(day)) continue;
    const credits = r.credits_used ?? 0;

    const d = dailyMap.get(day)!;
    d.credits += credits;
    d.requests += 1;

    const platform: string = String(r.platform ?? "").toLowerCase();
    const p = platformMap.get(day)!;
    if (
      platform === "youtube" ||
      platform === "tiktok" ||
      platform === "instagram" ||
      platform === "facebook"
    ) {
      p[platform] += credits;
    } else if (platform) {
      p.other += credits;
    }

    const ep = shortEndpoint(r.endpoint);
    endpointTotals.set(ep, (endpointTotals.get(ep) ?? 0) + credits);
    if (!endpointDayValues.has(ep)) endpointDayValues.set(ep, new Map());
    const epDays = endpointDayValues.get(ep)!;
    epDays.set(day, (epDays.get(day) ?? 0) + credits);
  }

  const endpointKeys = [...endpointTotals.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, TOP_ENDPOINTS)
    .map(([k]) => k);

  const endpointDaily: EndpointPoint[] = days.map((day) => {
    const point: EndpointPoint = { date: day };
    for (const key of endpointKeys) {
      point[key] = endpointDayValues.get(key)?.get(day) ?? 0;
    }
    return point;
  });

  const daily = days.map((day) => dailyMap.get(day)!);
  const platformDaily = days.map((day) => platformMap.get(day)!);

  const totalCredits = daily.reduce((s, d) => s + d.credits, 0);
  const totalRequests = daily.reduce((s, d) => s + d.requests, 0);
  const activeDays = daily.filter((d) => d.requests > 0).length;
  const avgPerDay = activeDays ? Math.round(totalCredits / activeDays) : 0;

  const platformTotals = PLATFORMS.map((p) => ({
    platform: p,
    total: platformDaily.reduce((s, d) => s + (d[p] as number), 0),
  })).sort((a, b) => b.total - a.total);
  const topPlatform = platformTotals[0]?.total ? platformTotals[0].platform : "—";

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="mt-1 text-muted-foreground">
          Daily usage over the last {DAYS} days — total, by platform (plus Other),
          and by endpoint.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Credits used ({DAYS}d)</CardDescription>
            <CardTitle className="text-3xl">{formatNumber(totalCredits)}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Requests ({DAYS}d)</CardDescription>
            <CardTitle className="text-3xl">{formatNumber(totalRequests)}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Avg credits / active day</CardDescription>
            <CardTitle className="text-3xl">{formatNumber(avgPerDay)}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Top platform</CardDescription>
            <CardTitle className="text-3xl capitalize">{topPlatform}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      <UsageCharts
        daily={daily}
        platformDaily={platformDaily}
        endpointDaily={endpointDaily}
        endpointKeys={endpointKeys}
      />
    </div>
  );
}
