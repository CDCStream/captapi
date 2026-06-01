"use client";

import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import {
  ChevronRight,
  Facebook,
  Instagram,
  Music2,
  ShieldCheck,
  Terminal,
  Youtube,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { createClient } from "@/lib/supabase/client";
import { track } from "@/lib/analytics";
import { cn } from "@/lib/utils";
import {
  PLATFORM_GROUPS,
  creditLabel,
  requestUrl,
  type ApiEndpoint,
  type PlatformId,
} from "@/lib/api-catalog";
import { ApiPlayground, type RunResult } from "@/components/docs/api-playground";

const PLATFORM_ICON: Record<PlatformId, typeof Youtube> = {
  youtube: Youtube,
  tiktok: Music2,
  instagram: Instagram,
  facebook: Facebook,
};

const PLATFORM_BG: Record<PlatformId, string> = {
  youtube: "bg-red-500/10",
  tiktok: "bg-foreground/10",
  instagram: "bg-fuchsia-500/10",
  facebook: "bg-blue-600/10",
};

const PLATFORM_FG: Record<PlatformId, string> = {
  youtube: "text-red-500",
  tiktok: "text-foreground",
  instagram: "text-fuchsia-500",
  facebook: "text-blue-600",
};

const FIRST = PLATFORM_GROUPS[0].endpoints[0];

export default function PlaygroundPage() {
  const [selected, setSelected] = useState<ApiEndpoint>(FIRST);
  const [sessionReady, setSessionReady] = useState(false);

  useEffect(() => {
    const sb = createClient();
    sb.auth.getSession().then(({ data }) => setSessionReady(!!data.session));
  }, []);

  const totalCount = useMemo(
    () => PLATFORM_GROUPS.reduce((n, g) => n + g.endpoints.length, 0),
    [],
  );

  async function handleRun(
    values: Record<string, string>,
  ): Promise<RunResult | null> {
    if (!sessionReady) {
      toast.error("Loading your session — try again in a moment.");
      return null;
    }
    track("api_request", {
      path: selected.path,
      platform: selected.platform,
      source: "playground",
    });
    const started = performance.now();
    try {
      const sb = createClient();
      const {
        data: { session },
      } = await sb.auth.getSession();
      if (!session) {
        toast.error("Session expired. Please sign in again.");
        return null;
      }
      const res = await fetch(requestUrl(selected, values), {
        headers: { Authorization: `Bearer ${session.access_token}` },
      });
      const text = await res.text();
      const ms = Math.round(performance.now() - started);
      let body = text;
      try {
        body = JSON.stringify(JSON.parse(text), null, 2);
      } catch {
        /* keep raw text */
      }
      if (!res.ok) toast.error(`Request failed — HTTP ${res.status}`);
      return { status: res.status, body, ms };
    } catch {
      toast.error("Network error — couldn't reach the API");
      return { status: 0, body: "Network error — couldn't reach the API.", ms: 0 };
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Terminal className="size-4" />
            </span>
            Playground
          </div>
          <h1 className="mt-2 text-3xl font-bold tracking-tight">Try the API live</h1>
          <p className="text-muted-foreground mt-1">
            Run any of our {totalCount} endpoints right from your browser — no key
            needed here.
          </p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-600 dark:text-emerald-400">
          <ShieldCheck className="size-3.5" />
          Authenticated with your account
        </span>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Endpoint picker */}
        <Card className="lg:col-span-1 h-fit lg:sticky lg:top-6">
          <CardContent className="p-4">
            <div className="flex items-center justify-between px-2 pb-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Endpoints
              </p>
              <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                {totalCount}
              </span>
            </div>
            <div className="max-h-[70vh] space-y-4 overflow-y-auto pr-1">
              {PLATFORM_GROUPS.map((group) => {
                const Icon = PLATFORM_ICON[group.id];
                return (
                  <div key={group.id}>
                    <div className="flex items-center gap-2 px-2 py-1.5">
                      <span
                        className={cn(
                          "flex size-5 items-center justify-center rounded-md",
                          PLATFORM_BG[group.id],
                          PLATFORM_FG[group.id],
                        )}
                      >
                        <Icon className="size-3" />
                      </span>
                      <span className="text-xs font-medium text-muted-foreground">
                        {group.name}
                      </span>
                      <span className="ml-auto text-[10px] text-muted-foreground/60">
                        {group.endpoints.length}
                      </span>
                    </div>
                    <div className="space-y-0.5">
                      {group.endpoints.map((e) => {
                        const active = selected.path === e.path;
                        return (
                          <button
                            key={e.slug}
                            onClick={() => setSelected(e)}
                            className={cn(
                              "group flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-sm transition-colors",
                              active
                                ? "bg-primary/10 text-foreground"
                                : "hover:bg-muted text-muted-foreground hover:text-foreground",
                            )}
                          >
                            <span
                              className={cn(
                                "rounded px-1.5 py-0.5 text-[10px] font-bold tracking-wide",
                                active
                                  ? "bg-primary text-primary-foreground"
                                  : "bg-muted text-muted-foreground",
                              )}
                            >
                              {e.method}
                            </span>
                            <span className="flex-1 truncate font-medium">
                              {e.shortName}
                            </span>
                            <span className="text-[10px] text-muted-foreground/70">
                              {e.creditsPerResult ? `~${e.credits} credits` : creditLabel(e)}
                            </span>
                            <ChevronRight
                              className={cn(
                                "size-4 shrink-0 transition-opacity",
                                active
                                  ? "opacity-100 text-primary"
                                  : "opacity-0 group-hover:opacity-50",
                              )}
                            />
                          </button>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Interactive builder + live response */}
        <div className="lg:col-span-2">
          <div className="mb-4 flex items-center gap-2 text-sm">
            <span
              className={cn(
                "flex size-6 items-center justify-center rounded-md",
                PLATFORM_BG[selected.platform],
                PLATFORM_FG[selected.platform],
              )}
            >
              {(() => {
                const Icon = PLATFORM_ICON[selected.platform];
                return <Icon className="size-3.5" />;
              })()}
            </span>
            <span className="font-medium">{selected.name}</span>
            <code className="font-mono text-xs text-muted-foreground">
              {selected.path}
            </code>
            <span className="ml-auto rounded-full bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
              {creditLabel(selected)}
            </span>
          </div>
          <ApiPlayground key={selected.slug} ep={selected} onRun={handleRun} />
        </div>
      </div>
    </div>
  );
}
