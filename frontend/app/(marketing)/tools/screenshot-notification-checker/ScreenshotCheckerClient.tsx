"use client";

import { useState } from "react";
import { Bell, BellOff, ShieldAlert } from "lucide-react";
import { SCREENSHOT_RULES, NOTIFY_LABELS, type Notifies } from "@/lib/screenshot-rules";

const BADGE: Record<Notifies, { cls: string; icon: React.ReactNode }> = {
  yes: { cls: "border-red-500/30 bg-red-500/10 text-red-600 dark:text-red-400", icon: <Bell className="size-3.5" /> },
  no: { cls: "border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400", icon: <BellOff className="size-3.5" /> },
  partial: { cls: "border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400", icon: <ShieldAlert className="size-3.5" /> },
};

export default function ScreenshotCheckerClient() {
  const [platformId, setPlatformId] = useState("instagram");
  const platform = SCREENSHOT_RULES.find((p) => p.id === platformId)!;

  return (
    <div className="mt-8">
      <div className="flex flex-wrap gap-2">
        {SCREENSHOT_RULES.map((p) => (
          <button
            key={p.id}
            type="button"
            onClick={() => setPlatformId(p.id)}
            className={`rounded-full border px-4 py-2 text-sm font-medium transition-colors ${
              platformId === p.id ? "border-primary bg-primary/10 text-primary" : "hover:bg-muted"
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      <p className="mt-5 max-w-3xl rounded-xl border bg-muted/40 p-4 text-sm leading-relaxed">
        {platform.summary}
      </p>

      <div className="mt-4 divide-y rounded-2xl border">
        {platform.rules.map((r) => {
          const b = BADGE[r.notifies];
          return (
            <div key={r.action} className="flex flex-col gap-2 p-4 sm:flex-row sm:items-start sm:gap-4">
              <div className="sm:w-64 sm:shrink-0">
                <p className="font-medium">{r.action}</p>
                <span className={`mt-1.5 inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${b.cls}`}>
                  {b.icon}
                  {NOTIFY_LABELS[r.notifies]}
                </span>
              </div>
              <p className="text-sm leading-relaxed text-muted-foreground">{r.detail}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
