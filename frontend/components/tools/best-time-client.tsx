"use client";

import { useEffect, useMemo, useState } from "react";
import { Clock, Star } from "lucide-react";
import type { BestTimeConfig } from "@/lib/best-time-data";

// Offset (in hours) of America/New_York from UTC for a given date, accounting
// for daylight saving. Positive number = hours to add to UTC to get ET is
// negative, so we compute via Intl for correctness.
function etOffsetHours(): number {
  const now = new Date();
  const et = new Date(now.toLocaleString("en-US", { timeZone: "America/New_York" }));
  const utc = new Date(now.toLocaleString("en-US", { timeZone: "UTC" }));
  return Math.round((et.getTime() - utc.getTime()) / 3_600_000); // e.g. -4 or -5
}

const DAY_INDEX: Record<string, number> = {
  Monday: 1, Tuesday: 2, Wednesday: 3, Thursday: 4, Friday: 5, Saturday: 6, Sunday: 0,
};

function fmtHour(h: number): string {
  const hour = ((h % 24) + 24) % 24;
  const period = hour < 12 ? "AM" : "PM";
  const display = hour % 12 === 0 ? 12 : hour % 12;
  return `${display} ${period}`;
}

export function BestTimeClient({ config }: { config: BestTimeConfig }) {
  const [localOffset, setLocalOffset] = useState<number | null>(null);
  const [tzName, setTzName] = useState<string>("");
  const [todayIdx, setTodayIdx] = useState<number>(-1);

  useEffect(() => {
    const etOff = etOffsetHours();
    const localOff = -new Date().getTimezoneOffset() / 60; // local hours from UTC
    setLocalOffset(localOff - etOff); // hours to add to an ET hour to get local
    setTzName(Intl.DateTimeFormat().resolvedOptions().timeZone || "your local time");
    setTodayIdx(new Date().getDay());
  }, []);

  const shift = (h: number) => (localOffset === null ? h : ((h + localOffset) % 24 + 24) % 24);

  const rows = useMemo(
    () =>
      config.schedule.map((d) => ({
        day: d.day,
        isToday: DAY_INDEX[d.day] === todayIdx,
        top: [...new Set(d.top.map(shift))].sort((a, b) => a - b),
        good: [...new Set(d.good.map(shift))].sort((a, b) => a - b),
      })),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [config.schedule, localOffset, todayIdx],
  );

  const today = rows.find((r) => r.isToday);

  return (
    <div className="mt-8 space-y-6">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Clock className="size-4" />
        {localOffset === null ? (
          <span>Detecting your time zone…</span>
        ) : (
          <span>
            Times shown in <strong className="text-foreground">{tzName}</strong> (your local time zone).
          </span>
        )}
      </div>

      {today && (
        <div className={`rounded-2xl border p-6 ${today.top.length ? "border-primary/25 bg-primary/5" : ""}`}>
          <p className="text-sm font-medium text-muted-foreground">Best times to post today ({today.day})</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {today.top.map((h) => (
              <span
                key={`t${h}`}
                className="inline-flex items-center gap-1.5 rounded-full bg-primary px-3 py-1.5 text-sm font-semibold text-primary-foreground"
              >
                <Star className="size-3.5" />
                {fmtHour(h)}
              </span>
            ))}
            {today.good.map((h) => (
              <span key={`g${h}`} className="inline-flex items-center rounded-full border px-3 py-1.5 text-sm">
                {fmtHour(h)}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="overflow-x-auto rounded-2xl border">
        <table className="w-full text-sm">
          <thead className="bg-muted/60">
            <tr className="text-left">
              <th className="px-4 py-3 font-medium">Day</th>
              <th className="px-4 py-3 font-medium">
                <span className="inline-flex items-center gap-1.5">
                  <Star className={`size-3.5 ${config.accent}`} /> Best slots
                </span>
              </th>
              <th className="px-4 py-3 font-medium">Also good</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {rows.map((r) => (
              <tr key={r.day} className={r.isToday ? "bg-primary/5" : ""}>
                <td className="whitespace-nowrap px-4 py-3 font-medium">
                  {r.day}
                  {r.isToday && <span className="ml-2 rounded bg-primary/15 px-1.5 py-0.5 text-[10px] font-semibold text-primary">TODAY</span>}
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1.5">
                    {r.top.map((h) => (
                      <span key={h} className="rounded-md bg-foreground/90 px-2 py-1 text-xs font-semibold text-background">
                        {fmtHour(h)}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1.5">
                    {r.good.map((h) => (
                      <span key={h} className="rounded-md border px-2 py-1 text-xs text-muted-foreground">
                        {fmtHour(h)}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-muted-foreground">
        These windows are aggregated from public social-media engagement studies and converted from US
        Eastern Time into your local zone. Treat them as a strong starting point, then check your own
        analytics — your specific audience is always the final word.
      </p>
    </div>
  );
}
