"use client";

import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn, formatNumber } from "@/lib/utils";

export interface DailyPoint {
  date: string;
  credits: number;
  requests: number;
}

export interface PlatformPoint {
  date: string;
  youtube: number;
  tiktok: number;
  instagram: number;
  facebook: number;
}

export type EndpointPoint = { date: string } & Record<string, number | string>;

interface UsageChartsProps {
  daily: DailyPoint[];
  platformDaily: PlatformPoint[];
  endpointDaily: EndpointPoint[];
  endpointKeys: string[];
}

const PLATFORM_COLORS: Record<string, string> = {
  youtube: "#ef4444",
  tiktok: "#ec4899",
  instagram: "#d946ef",
  facebook: "#2563eb",
};

const ENDPOINT_PALETTE = [
  "#6366f1",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#06b6d4",
  "#a855f7",
  "#84cc16",
  "#f43f5e",
];

const RANGES = [
  { label: "7 days", value: 7 },
  { label: "14 days", value: 14 },
  { label: "30 days", value: 30 },
];

function fmtDay(date: string): string {
  // "2026-05-31" -> "May 31"
  const d = new Date(date + "T00:00:00Z");
  return d.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
}

const axisProps = {
  stroke: "currentColor",
  tick: { fontSize: 11, fill: "currentColor" },
  tickLine: false,
  axisLine: false,
} as const;

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border bg-background/95 px-3 py-2 text-xs shadow-md backdrop-blur">
      <div className="mb-1 font-medium">{fmtDay(label)}</div>
      {payload
        .filter((p: any) => p.value > 0 || payload.length <= 2)
        .map((p: any) => (
          <div key={p.dataKey} className="flex items-center gap-2">
            <span
              className="inline-block size-2 rounded-full"
              style={{ backgroundColor: p.color }}
            />
            <span className="text-muted-foreground">{p.name}</span>
            <span className="ml-auto font-medium">{formatNumber(p.value)}</span>
          </div>
        ))}
    </div>
  );
}

export function UsageCharts({
  daily,
  platformDaily,
  endpointDaily,
  endpointKeys,
}: UsageChartsProps) {
  const [range, setRange] = useState(30);

  const sliced = useMemo(
    () => ({
      daily: daily.slice(-range),
      platform: platformDaily.slice(-range),
      endpoint: endpointDaily.slice(-range),
    }),
    [daily, platformDaily, endpointDaily, range],
  );

  const hasData = daily.some((d) => d.credits > 0 || d.requests > 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-end gap-1">
        {RANGES.map((r) => (
          <button
            key={r.value}
            onClick={() => setRange(r.value)}
            className={cn(
              "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
              range === r.value
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted",
            )}
          >
            {r.label}
          </button>
        ))}
      </div>

      {!hasData && (
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            No usage recorded yet. Make some API calls and your daily activity
            will appear here.
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Daily credits used</CardTitle>
          <CardDescription>Total credits consumed per day.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-72 w-full text-muted-foreground">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sliced.daily} margin={{ top: 8, right: 12, left: -8, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" strokeOpacity={0.12} vertical={false} />
                <XAxis dataKey="date" tickFormatter={fmtDay} minTickGap={24} {...axisProps} />
                <YAxis allowDecimals={false} width={40} tickFormatter={(v) => formatNumber(v)} {...axisProps} />
                <Tooltip content={<ChartTooltip />} />
                <Line
                  type="monotone"
                  dataKey="credits"
                  name="Credits"
                  stroke="#6366f1"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="requests"
                  name="Requests"
                  stroke="#10b981"
                  strokeWidth={2}
                  strokeDasharray="4 3"
                  dot={false}
                  activeDot={{ r: 4 }}
                />
                <Legend iconType="plainline" wrapperStyle={{ fontSize: 12 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>By platform</CardTitle>
          <CardDescription>Daily credits used per platform.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-72 w-full text-muted-foreground">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sliced.platform} margin={{ top: 8, right: 12, left: -8, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" strokeOpacity={0.12} vertical={false} />
                <XAxis dataKey="date" tickFormatter={fmtDay} minTickGap={24} {...axisProps} />
                <YAxis allowDecimals={false} width={40} tickFormatter={(v) => formatNumber(v)} {...axisProps} />
                <Tooltip content={<ChartTooltip />} />
                {(["youtube", "tiktok", "instagram", "facebook"] as const).map((p) => (
                  <Line
                    key={p}
                    type="monotone"
                    dataKey={p}
                    name={p.charAt(0).toUpperCase() + p.slice(1)}
                    stroke={PLATFORM_COLORS[p]}
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4 }}
                  />
                ))}
                <Legend iconType="plainline" wrapperStyle={{ fontSize: 12 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>By endpoint</CardTitle>
          <CardDescription>
            {endpointKeys.length
              ? "Daily credits used for your most-used endpoints."
              : "Daily credits used per endpoint."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80 w-full text-muted-foreground">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sliced.endpoint} margin={{ top: 8, right: 12, left: -8, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" strokeOpacity={0.12} vertical={false} />
                <XAxis dataKey="date" tickFormatter={fmtDay} minTickGap={24} {...axisProps} />
                <YAxis allowDecimals={false} width={40} tickFormatter={(v) => formatNumber(v)} {...axisProps} />
                <Tooltip content={<ChartTooltip />} />
                {endpointKeys.map((key, i) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    name={key}
                    stroke={ENDPOINT_PALETTE[i % ENDPOINT_PALETTE.length]}
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4 }}
                  />
                ))}
                <Legend iconType="plainline" wrapperStyle={{ fontSize: 12 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
