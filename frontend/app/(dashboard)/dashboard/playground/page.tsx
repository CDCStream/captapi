"use client";

import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import {
  Check,
  ChevronRight,
  Copy,
  Facebook,
  Instagram,
  Loader2,
  Music2,
  Play,
  ShieldCheck,
  Terminal,
  Youtube,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { createClient } from "@/lib/supabase/client";
import { track } from "@/lib/analytics";
import { cn } from "@/lib/utils";
import {
  PLATFORM_GROUPS,
  type ApiEndpoint,
  type PlatformId,
} from "@/lib/api-catalog";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

function paramKey(ep: ApiEndpoint): "q" | "url" {
  return ep.category === "search" ? "q" : "url";
}

function placeholderFor(ep: ApiEndpoint): string {
  if (ep.category === "search") return "structured data api";
  const group = PLATFORM_GROUPS.find((g) => g.id === ep.platform)!;
  if (ep.category === "channel") {
    return ep.platform === "youtube"
      ? "https://youtube.com/@channel"
      : ep.platform === "tiktok"
        ? "https://tiktok.com/@username"
        : ep.platform === "instagram"
          ? "https://instagram.com/username"
          : "https://facebook.com/page";
  }
  return group.exampleUrl;
}

const FIRST = PLATFORM_GROUPS[0].endpoints[0];

export default function PlaygroundPage() {
  const [selected, setSelected] = useState<ApiEndpoint>(FIRST);
  const [value, setValue] = useState("");
  const [response, setResponse] = useState<string>("");
  const [status, setStatus] = useState<number | null>(null);
  const [elapsed, setElapsed] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [sessionReady, setSessionReady] = useState(false);
  const [copied, setCopied] = useState<"response" | "curl" | null>(null);

  useEffect(() => {
    const sb = createClient();
    sb.auth.getSession().then(({ data }) => setSessionReady(!!data.session));
  }, []);

  const totalCount = useMemo(
    () => PLATFORM_GROUPS.reduce((n, g) => n + g.endpoints.length, 0),
    [],
  );

  const key = paramKey(selected);
  const placeholder = placeholderFor(selected);

  const curl = `curl "${API_URL}${selected.path}?${key}=${encodeURIComponent(value || placeholder)}" \\
  -H "Authorization: Bearer capt_live_..."`;

  async function copy(text: string, which: "response" | "curl") {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(which);
      setTimeout(() => setCopied(null), 1500);
    } catch {
      toast.error("Couldn't copy");
    }
  }

  async function run() {
    if (!value) {
      toast.error(key === "q" ? "Enter a search query first" : "Enter a URL first");
      return;
    }
    setLoading(true);
    setResponse("");
    setStatus(null);
    setElapsed(null);
    track("api_request", { path: selected.path, platform: selected.platform, source: "playground" });
    const started = performance.now();
    try {
      const sb = createClient();
      const { data: { session } } = await sb.auth.getSession();
      if (!session) {
        toast.error("Session expired. Please sign in again.");
        setLoading(false);
        return;
      }
      const params = new URLSearchParams({ [key]: value });
      const res = await fetch(`${API_URL}${selected.path}?${params.toString()}`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      });
      const text = await res.text();
      setStatus(res.status);
      setElapsed(Math.round(performance.now() - started));
      try {
        setResponse(JSON.stringify(JSON.parse(text), null, 2));
      } catch {
        setResponse(text);
      }
      if (!res.ok) toast.error(`Request failed — HTTP ${res.status}`);
    } catch {
      setResponse("Network error — couldn't reach the API.");
      toast.error("Network error — couldn't reach the API");
    } finally {
      setLoading(false);
    }
  }

  const statusTone = (code: number) =>
    code >= 500
      ? "bg-red-500/10 text-red-600 dark:text-red-400"
      : code >= 400
        ? "bg-amber-500/10 text-amber-600 dark:text-amber-400"
        : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400";

  const SelIcon = PLATFORM_ICON[selected.platform];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
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
            Run any of our {totalCount} endpoints right from your browser — no key needed here.
          </p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-600 dark:text-emerald-400">
          <ShieldCheck className="size-3.5" />
          Authenticated with your account
        </span>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Endpoint picker */}
        <Card className="lg:col-span-2 h-fit lg:sticky lg:top-6">
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
                      <span className={cn("flex size-5 items-center justify-center rounded-md", PLATFORM_BG[group.id], PLATFORM_FG[group.id])}>
                        <Icon className="size-3" />
                      </span>
                      <span className="text-xs font-medium text-muted-foreground">{group.name}</span>
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
                            onClick={() => {
                              setSelected(e);
                              setValue("");
                            }}
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
                                active ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground",
                              )}
                            >
                              {e.method}
                            </span>
                            <span className="flex-1 truncate font-medium">{e.shortName}</span>
                            <span className="text-[10px] text-muted-foreground/70">
                              {e.credits} credit{e.credits === 1 ? "" : "s"}
                            </span>
                            <ChevronRight
                              className={cn(
                                "size-4 shrink-0 transition-opacity",
                                active ? "opacity-100 text-primary" : "opacity-0 group-hover:opacity-50",
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

        {/* Request + Response */}
        <div className="lg:col-span-3 space-y-6">
          {/* Request bar */}
          <Card>
            <CardContent className="p-4 space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <span className={cn("flex size-6 items-center justify-center rounded-md", PLATFORM_BG[selected.platform], PLATFORM_FG[selected.platform])}>
                  <SelIcon className="size-3.5" />
                </span>
                <span className="font-medium">{selected.name}</span>
                <span className="ml-auto rounded-full bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
                  {selected.credits} credit{selected.credits === 1 ? "" : "s"}
                </span>
              </div>
              <code className="block font-mono text-xs text-muted-foreground">{selected.path}</code>
              <div className="flex flex-col gap-2 sm:flex-row">
                <div className="flex flex-1 items-center rounded-lg border bg-background focus-within:ring-2 focus-within:ring-ring/40">
                  <span className="select-none border-r px-3 py-2 text-xs font-bold tracking-wide text-emerald-600 dark:text-emerald-400">
                    {selected.method}
                  </span>
                  <Input
                    placeholder={placeholder}
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && run()}
                    className="border-0 bg-transparent font-mono text-xs shadow-none focus-visible:ring-0"
                  />
                </div>
                <Button onClick={run} disabled={loading || !sessionReady} className="sm:w-36">
                  {loading ? (
                    <>
                      <Loader2 className="size-4 mr-2 animate-spin" /> Running…
                    </>
                  ) : (
                    <>
                      <Play className="size-4 mr-2" /> Send request
                    </>
                  )}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Query param: <code className="rounded bg-muted px-1 py-0.5 font-mono">{key}</code>
                {!sessionReady && " · Loading your session…"}
              </p>
            </CardContent>
          </Card>

          {/* Response */}
          <Tabs defaultValue="response">
            <div className="flex items-center justify-between gap-3 flex-wrap">
              <TabsList>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="curl">cURL</TabsTrigger>
              </TabsList>
              {status !== null && (
                <div className="flex items-center gap-2 text-xs">
                  <span className={cn("rounded-full px-2.5 py-1 font-semibold", statusTone(status))}>
                    {status} {status < 400 ? "OK" : "Error"}
                  </span>
                  {elapsed !== null && (
                    <span className="inline-flex items-center gap-1 text-muted-foreground">
                      <Zap className="size-3" />
                      {elapsed} ms
                    </span>
                  )}
                </div>
              )}
            </div>

            <TabsContent value="response" className="mt-3">
              <div className="relative rounded-xl border bg-muted/30">
                {response && (
                  <button
                    onClick={() => copy(response, "response")}
                    className="absolute right-3 top-3 z-10 inline-flex items-center gap-1 rounded-md border bg-background/80 px-2 py-1 text-xs text-muted-foreground backdrop-blur transition-colors hover:text-foreground"
                  >
                    {copied === "response" ? <Check className="size-3" /> : <Copy className="size-3" />}
                    {copied === "response" ? "Copied" : "Copy"}
                  </button>
                )}
                {loading ? (
                  <div className="flex items-center justify-center gap-2 py-16 text-sm text-muted-foreground">
                    <Loader2 className="size-4 animate-spin" /> Fetching response…
                  </div>
                ) : response ? (
                  <pre className="max-h-[520px] overflow-auto whitespace-pre-wrap p-4 text-xs leading-relaxed font-mono">
                    {response}
                  </pre>
                ) : (
                  <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
                    <span className="flex size-12 items-center justify-center rounded-2xl bg-muted text-muted-foreground">
                      <Play className="size-5" />
                    </span>
                    <p className="text-sm text-muted-foreground">
                      Pick an endpoint, paste a {key === "q" ? "query" : "URL"}, and hit{" "}
                      <span className="font-medium text-foreground">Send request</span>.
                    </p>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="curl" className="mt-3">
              <p className="mb-3 text-xs text-muted-foreground">
                For use outside the dashboard, create an API key in{" "}
                <a href="/dashboard/api-keys" className="font-medium text-primary underline underline-offset-2">
                  API Keys
                </a>{" "}
                and replace <code className="rounded bg-muted px-1 py-0.5">capt_live_...</code>.
              </p>
              <div className="relative rounded-xl border bg-muted/30">
                <button
                  onClick={() => copy(curl, "curl")}
                  className="absolute right-3 top-3 inline-flex items-center gap-1 rounded-md border bg-background/80 px-2 py-1 text-xs text-muted-foreground backdrop-blur transition-colors hover:text-foreground"
                >
                  {copied === "curl" ? <Check className="size-3" /> : <Copy className="size-3" />}
                  {copied === "curl" ? "Copied" : "Copy"}
                </button>
                <pre className="overflow-auto p-4 text-xs leading-relaxed font-mono">{curl}</pre>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
