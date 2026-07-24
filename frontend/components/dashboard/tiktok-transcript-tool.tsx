"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { Loader2, Copy, Download, Search, RefreshCw, ExternalLink } from "lucide-react";
import { toast } from "sonner";
import { createClient } from "@/lib/supabase/client";
import { ALL_ENDPOINTS, requestUrl } from "@/lib/api-catalog";

const ENDPOINT = ALL_ENDPOINTS.find((e) => e.slug === "tiktok-transcript")!;

type TranscriptData = {
  title?: string | null;
  transcript?: string;
  wordCount?: number;
  segments?: number;
  language?: string | null;
};

export function DashboardTikTokTranscriptTool() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<TranscriptData | null>(null);
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
        setBalance(
          (row.subscription_credits ?? 0) + (row.topup_credits ?? 0),
        );
      }
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    void refreshBalance();
  }, [refreshBalance]);

  const run = useCallback(async () => {
    if (inFlight.current) return;
    if (!url.trim()) {
      toast.error("Please paste a TikTok video URL.");
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
        requestUrl(ENDPOINT, { url: url.trim(), cache: "true" }),
        { headers: { Authorization: `Bearer ${session.access_token}` } },
      );
      const json = await res.json().catch(() => null);
      if (!res.ok) {
        const detail = json?.detail;
        const msg =
          typeof detail === "string"
            ? detail
            : detail?.error === "free_transcript_daily_quota"
              ? "Free plan daily transcript limit reached (5/day). Upgrade or wait until tomorrow."
              : detail?.error === "insufficient_credits"
                ? "Not enough credits. Top up or upgrade your plan."
                : detail?.error || json?.error || `Request failed (HTTP ${res.status})`;
        setError(String(msg));
        return;
      }
      const payload = (json?.data ?? json) as TranscriptData;
      setData(payload);
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
  }, [url, refreshBalance]);

  const fullText = data?.transcript || "";

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
    a.download = `tiktok-transcript-${Date.now()}.txt`;
    a.click();
    toast.success("Downloaded .txt");
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-muted-foreground">
        <p>
          Uses your account credits · <span className="font-medium text-foreground">5 credits</span>{" "}
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
            placeholder="https://www.tiktok.com/@user/video/…"
            aria-label="TikTok video URL"
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
          {loading ? "Working…" : "Get transcript"}
        </button>
      </div>

      <p className="text-xs text-muted-foreground">
        Free plan: max 5 billable transcripts / day.{" "}
        <Link href="/apis/tiktok-transcript" className="underline underline-offset-2">
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
                {data.wordCount?.toLocaleString() ?? "—"} words · {data.segments ?? "—"} segments
                {data.language ? ` · ${data.language}` : ""}
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
          <textarea
            readOnly
            value={fullText}
            className="h-72 w-full resize-y rounded-lg border bg-muted/40 p-3 text-sm leading-relaxed outline-none"
          />
        </div>
      )}
    </div>
  );
}
