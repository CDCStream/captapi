"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { Loader2, Copy, Download, Search, RefreshCw, ExternalLink } from "lucide-react";
import { toast } from "sonner";
import { createClient } from "@/lib/supabase/client";
import { ALL_ENDPOINTS, requestUrl, type ApiEndpoint } from "@/lib/api-catalog";
import type { Tool } from "@/lib/tools";

type TranscriptData = {
  title?: string | null;
  transcript?: string;
  wordCount?: number;
  segments?: number;
  language?: string | null;
};
type SummaryData = {
  title?: string | null;
  summary?: string;
  keyPoints?: string[];
  topics?: string[];
  sentiment?: string;
};
type ResultData = TranscriptData & SummaryData;

export function DashboardToolRunner({ tool }: { tool: Tool }) {
  const endpoint: ApiEndpoint | undefined = ALL_ENDPOINTS.find((e) => e.slug === tool.slug);
  const kind = tool.kind ?? "transcript";
  const credits = endpoint?.credits ?? 0;

  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ResultData | null>(null);
  const [creditsUsed, setCreditsUsed] = useState<number | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  const [balance, setBalance] = useState<number | null>(null);
  const inFlight = useRef(false);

  const refreshBalance = useCallback(async () => {
    try {
      const sb = createClient();
      const {
        data: { user },
      } = await sb.auth.getUser();
      if (!user) return;
      const { data: row } = await sb
        .from("credit_balances")
        .select("subscription_credits, topup_credits")
        .eq("user_id", user.id)
        .maybeSingle();
      if (row) {
        setBalance((row.subscription_credits ?? 0) + (row.topup_credits ?? 0));
      }
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    void refreshBalance();
  }, [refreshBalance]);

  const run = useCallback(async () => {
    if (inFlight.current || !endpoint) return;
    if (!url.trim()) {
      toast.error(`Please paste a ${tool.platform} video URL.`);
      return;
    }
    inFlight.current = true;
    setLoading(true);
    setError(null);
    setData(null);
    setCreditsUsed(null);
    setCacheHit(false);
    try {
      const sb = createClient();
      const {
        data: { session },
      } = await sb.auth.getSession();
      if (!session) {
        toast.error("Session expired. Please sign in again.");
        setError("Please sign in again.");
        return;
      }
      const res = await fetch(
        requestUrl(endpoint, { url: url.trim(), cache: "true" }),
        { headers: { Authorization: `Bearer ${session.access_token}` } },
      );
      const json = await res.json().catch(() => null);
      if (!res.ok) {
        const detail = json?.detail;
        const msg =
          typeof detail === "string"
            ? detail
            : detail?.error === "free_transcript_daily_quota"
              ? "Free plan daily limit reached. Upgrade or wait until tomorrow."
              : detail?.error === "insufficient_credits"
                ? "Not enough credits. Top up or upgrade your plan."
                : detail?.error || json?.error || `Request failed (HTTP ${res.status})`;
        setError(String(msg));
        return;
      }
      setData((json?.data ?? json) as ResultData);
      const usedHeader = res.headers.get("x-captapi-credits");
      const hitHeader = res.headers.get("x-captapi-cache");
      if (usedHeader != null) setCreditsUsed(parseInt(usedHeader, 10) || 0);
      setCacheHit(hitHeader === "1" || hitHeader === "true");
      void refreshBalance();
    } catch {
      setError("Couldn't reach the API. Please try again.");
    } finally {
      setLoading(false);
      inFlight.current = false;
    }
  }, [endpoint, url, tool.platform, refreshBalance]);

  const fullText =
    kind === "transcript"
      ? data?.transcript || ""
      : [
          data?.summary,
          data?.keyPoints?.length ? "\nKey points:\n" + data.keyPoints.map((k) => `• ${k}`).join("\n") : "",
          data?.topics?.length ? "\nTopics: " + data.topics.join(", ") : "",
        ]
          .filter(Boolean)
          .join("\n");

  const copyText = async () => {
    if (!fullText) return;
    try {
      await navigator.clipboard.writeText(fullText);
      toast.success("Copied to clipboard");
    } catch {
      toast.error("Couldn't copy — please select and copy manually.");
    }
  };

  const downloadText = () => {
    if (!fullText) return;
    const blob = new Blob([fullText], { type: "text/plain;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${tool.slug}-${Date.now()}.txt`;
    a.click();
    toast.success("Downloaded .txt");
  };

  if (!endpoint) {
    return (
      <p className="text-sm text-destructive">
        This tool is not linked to an API endpoint yet. Use the{" "}
        <Link href="/dashboard/playground" className="underline">
          Playground
        </Link>{" "}
        instead.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-muted-foreground">
        <p>
          Uses your account credits ·{" "}
          <span className="font-medium text-foreground">{credits} credit{credits === 1 ? "" : "s"}</span>{" "}
          per call · cache hits are free
        </p>
        {balance != null && (
          <p>
            Balance: <span className="font-medium text-foreground">{balance.toLocaleString()}</span>
            {" · "}
            <Link href="/dashboard/billing" className="underline underline-offset-2 hover:text-foreground">
              Top up
            </Link>
          </p>
        )}
      </div>

      <div className="flex flex-col gap-3 rounded-xl border bg-card p-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="url"
            inputMode="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !loading) void run();
            }}
            disabled={loading}
            placeholder={tool.urlPlaceholder || `Paste a ${tool.platform} video URL`}
            aria-label={`${tool.platform} video URL`}
            className="w-full rounded-lg border bg-background py-2.5 pl-9 pr-3 text-sm outline-none focus:border-primary disabled:opacity-60"
          />
        </div>
        <button
          type="button"
          onClick={() => void run()}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-60"
        >
          {loading ? <Loader2 className="size-4 animate-spin" /> : null}
          {loading ? "Working…" : kind === "transcript" ? "Get transcript" : "Summarize"}
        </button>
      </div>

      <p className="text-xs text-muted-foreground">
        {tool.slug === "tiktok-transcript" ? "Free plan: max 5 billable TikTok transcripts / day. " : null}
        <Link href={`/apis/${tool.slug}`} className="underline underline-offset-2">
          API docs
        </Link>
        {" · "}
        <Link href="/dashboard/playground" className="underline underline-offset-2">
          Playground
        </Link>
      </p>

      {error && (
        <div className="flex flex-col items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/5 p-4">
          <p className="text-sm text-destructive">{error}</p>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => void run()}
              className="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm hover:bg-muted"
            >
              <RefreshCw className="size-3.5" /> Try again
            </button>
            <Link
              href="/dashboard/billing"
              className="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm hover:bg-muted"
            >
              Billing <ExternalLink className="size-3.5" />
            </Link>
          </div>
        </div>
      )}

      {data && !loading && (
        <div className="rounded-xl border bg-card p-5">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
            <div className="min-w-0">
              {data.title && <p className="truncate font-medium">{data.title}</p>}
              <p className="text-xs text-muted-foreground">
                {kind === "transcript"
                  ? `${data.wordCount?.toLocaleString() ?? "—"} words · ${data.segments ?? "—"} segments${
                      data.language ? ` · ${data.language}` : ""
                    }`
                  : "AI summary"}
                {creditsUsed != null
                  ? ` · ${cacheHit || creditsUsed === 0 ? "0 credits (cache)" : `${creditsUsed} credits`}`
                  : null}
              </p>
            </div>
            <div className="flex shrink-0 gap-2">
              <button
                type="button"
                onClick={() => void copyText()}
                className="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs hover:bg-muted"
              >
                <Copy className="size-3.5" /> Copy
              </button>
              <button
                type="button"
                onClick={downloadText}
                className="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs hover:bg-muted"
              >
                <Download className="size-3.5" /> .txt
              </button>
            </div>
          </div>

          {kind === "transcript" ? (
            <textarea
              readOnly
              value={fullText}
              className="h-72 w-full resize-y rounded-lg border bg-muted/40 p-3 text-sm leading-relaxed outline-none"
            />
          ) : (
            <div className="space-y-4 text-sm">
              {data.summary && <p className="leading-relaxed">{data.summary}</p>}
              {data.keyPoints && data.keyPoints.length > 0 && (
                <div>
                  <p className="mb-1 font-medium">Key points</p>
                  <ul className="list-disc space-y-1 pl-5 text-muted-foreground">
                    {data.keyPoints.map((k, i) => (
                      <li key={i}>{k}</li>
                    ))}
                  </ul>
                </div>
              )}
              {data.topics && data.topics.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {data.topics.map((t, i) => (
                    <span key={i} className="rounded-full border bg-muted/40 px-3 py-1 text-xs">
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
