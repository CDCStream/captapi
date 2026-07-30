"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

type TimelineItem =
  | {
      kind: "event";
      id: string;
      at: string;
      event: string;
      path: string | null;
      properties: unknown;
      anonId: string | null;
    }
  | {
      kind: "request";
      id: string;
      at: string;
      endpoint: string;
      method: string | null;
      statusCode: number | null;
      responseTimeMs: number | null;
      creditsUsed: number | null;
      errorMessage: string | null;
      hasSample: boolean;
      truncated: boolean | null;
      responseJson: unknown;
      sampleId: string | null;
    }
  | {
      kind: "payment";
      id: string;
      at: string;
      type: string;
      amount: number;
      description: string | null;
    };

function fmtTime(iso: string) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function JsonBlock({ value }: { value: unknown }) {
  const text =
    typeof value === "string" ? value : JSON.stringify(value, null, 2) ?? "null";
  return (
    <pre className="mt-2 max-h-[28rem] overflow-auto rounded-md bg-zinc-950 p-3 text-xs leading-relaxed text-zinc-100">
      {text}
    </pre>
  );
}

function RequestRow({ item }: { item: Extract<TimelineItem, { kind: "request" }> }) {
  const [open, setOpen] = useState(false);
  const ok = (item.statusCode ?? 0) < 400;
  return (
    <li className="rounded-lg border bg-background">
      <button
        type="button"
        onClick={() => item.hasSample && setOpen((v) => !v)}
        className={cn(
          "flex w-full items-start gap-3 px-3 py-2.5 text-left text-sm",
          item.hasSample ? "cursor-pointer hover:bg-muted/50" : "cursor-default",
        )}
        disabled={!item.hasSample}
      >
        <span className="mt-0.5 text-muted-foreground">
          {item.hasSample ? (
            open ? (
              <ChevronDown className="size-4" />
            ) : (
              <ChevronRight className="size-4" />
            )
          ) : (
            <span className="inline-block size-4" />
          )}
        </span>
        <span className="min-w-0 flex-1">
          <span className="flex flex-wrap items-center gap-2">
            <span className="rounded bg-sky-500/10 px-1.5 py-0.5 text-[11px] font-medium uppercase tracking-wide text-sky-700">
              request
            </span>
            <code className="truncate font-mono text-xs">{item.endpoint}</code>
            <span
              className={cn(
                "rounded px-1.5 py-0.5 text-[11px] font-medium",
                ok ? "bg-emerald-500/10 text-emerald-700" : "bg-red-500/10 text-red-700",
              )}
            >
              {item.statusCode ?? "—"}
            </span>
            {item.responseTimeMs != null && (
              <span className="text-xs text-muted-foreground">{item.responseTimeMs}ms</span>
            )}
            {item.creditsUsed != null && item.creditsUsed > 0 && (
              <span className="text-xs text-muted-foreground">{item.creditsUsed} cr</span>
            )}
            {item.hasSample ? (
              <span className="text-[11px] font-medium text-primary">
                {item.truncated ? "JSON (truncated)" : "View JSON"}
              </span>
            ) : (
              <span className="text-[11px] text-muted-foreground">no sample</span>
            )}
          </span>
          {item.errorMessage && (
            <span className="mt-1 block text-xs text-red-600">{item.errorMessage}</span>
          )}
          <span className="mt-0.5 block text-xs text-muted-foreground">{fmtTime(item.at)}</span>
        </span>
      </button>
      {open && item.hasSample && (
        <div className="border-t px-3 pb-3">
          {item.truncated && !item.responseJson ? (
            <p className="mt-2 text-xs text-muted-foreground">
              Body exceeded size limit — only metadata was stored.
            </p>
          ) : (
            <JsonBlock value={item.responseJson} />
          )}
        </div>
      )}
    </li>
  );
}

export function FunnelJourney({ timeline }: { timeline: TimelineItem[] }) {
  if (!timeline.length) {
    return (
      <p className="text-sm text-muted-foreground">No activity in the last 14 days.</p>
    );
  }

  return (
    <ol className="space-y-2">
      {timeline.map((item) => {
        if (item.kind === "request") {
          return <RequestRow key={`req-${item.id}`} item={item} />;
        }
        if (item.kind === "payment") {
          return (
            <li
              key={`pay-${item.id}`}
              className="rounded-lg border border-amber-200/80 bg-amber-50/50 px-3 py-2.5 text-sm"
            >
              <span className="flex flex-wrap items-center gap-2">
                <span className="rounded bg-amber-500/15 px-1.5 py-0.5 text-[11px] font-medium uppercase tracking-wide text-amber-800">
                  payment
                </span>
                <span className="font-medium">{item.type}</span>
                <span className="text-muted-foreground">+{item.amount} credits</span>
              </span>
              {item.description && (
                <span className="mt-1 block text-xs text-muted-foreground">
                  {item.description}
                </span>
              )}
              <span className="mt-0.5 block text-xs text-muted-foreground">
                {fmtTime(item.at)}
              </span>
            </li>
          );
        }
        return (
          <li
            key={`evt-${item.id}`}
            className="rounded-lg border bg-muted/30 px-3 py-2.5 text-sm"
          >
            <span className="flex flex-wrap items-center gap-2">
              <span className="rounded bg-violet-500/10 px-1.5 py-0.5 text-[11px] font-medium uppercase tracking-wide text-violet-700">
                event
              </span>
              <span className="font-medium">{item.event}</span>
              {item.path && (
                <code className="truncate font-mono text-xs text-muted-foreground">
                  {item.path}
                </code>
              )}
            </span>
            <span className="mt-0.5 block text-xs text-muted-foreground">
              {fmtTime(item.at)}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
