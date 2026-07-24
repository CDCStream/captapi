"use client";

import Link from "next/link";
import { useCallback, useRef, useState } from "react";
import { Loader2, Copy, Download, Search, RefreshCw, KeyRound, ArrowRight } from "lucide-react";
import { toast } from "sonner";

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

export function ToolRunnerClient({
  endpoint,
  platform,
  kind,
  placeholder,
}: {
  endpoint: string;
  platform: string;
  kind: "transcript" | "summary";
  placeholder?: string;
}) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [paywalled, setPaywalled] = useState(false);
  const [data, setData] = useState<ResultData | null>(null);
  const [showApiCta, setShowApiCta] = useState(false);
  // Ref guard blocks a second submit (e.g. rapid Enter) before React flushes
  // the loading state — more reliable than reading `loading` alone.
  const inFlight = useRef(false);

  const isTikTokTranscript = endpoint === "/v1/tiktok/transcript";

  const run = useCallback(async () => {
    if (inFlight.current) return;
    if (!url.trim()) {
      toast.error("Please paste a video URL.");
      return;
    }
    inFlight.current = true;
    setLoading(true);
    setError(null);
    setPaywalled(false);
    setData(null);
    setShowApiCta(false);
    try {
      const res = await fetch("/api/tool-run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ endpoint, url: url.trim() }),
      });
      const json = await res.json();
      if (!res.ok) {
        const code = json?.code as string | undefined;
        if (res.status === 429 || code === "soft_paywall" || code === "anon_daily_limit") {
          setPaywalled(true);
          setError(json?.error || "Daily free limit reached. Sign up to continue.");
          return;
        }
        throw new Error(json?.error || "Request failed. Please try again.");
      }
      setData(json.data as ResultData);
      if (isTikTokTranscript) setShowApiCta(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
      inFlight.current = false;
    }
  }, [endpoint, url, isTikTokTranscript]);

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
    a.download = `${platform.toLowerCase()}-${kind}-${Date.now()}.txt`;
    a.click();
    toast.success("Downloaded .txt");
  };

  return (
    <div className="mt-8">
      <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-zinc-950 p-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-gray-500" />
          <input
            type="url"
            inputMode="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !loading) run();
            }}
            disabled={loading || paywalled}
            placeholder={placeholder || `Paste a ${platform} video URL`}
            aria-label={`${platform} video URL`}
            className="w-full rounded-lg border border-white/15 bg-zinc-900 py-2.5 pl-9 pr-3 text-sm text-white placeholder:text-gray-500 outline-none focus:border-primary disabled:opacity-60"
          />
        </div>
        <button
          type="button"
          onClick={run}
          disabled={loading || paywalled}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-60"
        >
          {loading ? <Loader2 className="size-4 animate-spin" /> : null}
          {loading ? "Working…" : kind === "transcript" ? "Get transcript" : "Summarize"}
        </button>
      </div>
      <p className="mt-2 text-center text-xs text-gray-500 sm:text-left">
        {isTikTokTranscript
          ? "3 free tries / day · then sign up for API credits"
          : "Free · no sign-up required · public videos only"}
      </p>

      {(error || paywalled) && (
        <div className="mt-4 flex flex-col items-center justify-center rounded-2xl border border-white/10 bg-zinc-950 p-6 text-center">
          <p className="text-sm text-rose-400">{error}</p>
          {paywalled ? (
            <div className="mt-4 flex flex-col items-center gap-3 sm:flex-row">
              <Link
                href="/signup"
                className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground hover:opacity-90"
              >
                <KeyRound className="size-4" />
                Get free API credits
              </Link>
              <Link
                href="/apis/tiktok-transcript"
                className="inline-flex items-center gap-1.5 text-sm text-gray-300 hover:text-white"
              >
                API docs <ArrowRight className="size-3.5" />
              </Link>
            </div>
          ) : (
            <button
              type="button"
              onClick={run}
              className="mt-3 inline-flex items-center gap-1.5 rounded-md border border-white/15 px-3 py-1.5 text-sm text-gray-200 hover:bg-white/10"
            >
              <RefreshCw className="size-3.5" /> Try again
            </button>
          )}
        </div>
      )}

      {data && !loading && (
        <div className="mt-4 rounded-2xl border border-white/10 bg-zinc-950 p-5">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
            <div className="min-w-0">
              {data.title && <p className="truncate font-medium text-white">{data.title}</p>}
              <p className="text-xs text-gray-400">
                {kind === "transcript"
                  ? `${data.wordCount?.toLocaleString() ?? "—"} words · ${data.segments ?? "—"} segments${
                      data.language ? ` · ${data.language}` : ""
                    }`
                  : "AI summary"}
              </p>
            </div>
            <div className="flex shrink-0 gap-2">
              <button
                type="button"
                onClick={copyText}
                className="inline-flex items-center gap-1.5 rounded-md border border-white/15 px-3 py-1.5 text-xs text-gray-200 hover:bg-white/10"
              >
                <Copy className="size-3.5" /> Copy
              </button>
              <button
                type="button"
                onClick={downloadText}
                className="inline-flex items-center gap-1.5 rounded-md border border-white/15 px-3 py-1.5 text-xs text-gray-200 hover:bg-white/10"
              >
                <Download className="size-3.5" /> .txt
              </button>
            </div>
          </div>

          {kind === "transcript" ? (
            <textarea
              readOnly
              value={data.transcript || ""}
              className="h-72 w-full resize-y rounded-lg border border-white/10 bg-zinc-900 p-3 text-sm leading-relaxed text-gray-200 outline-none"
            />
          ) : (
            <div className="space-y-4 text-sm text-gray-200">
              {data.summary && <p className="leading-relaxed">{data.summary}</p>}
              {data.keyPoints && data.keyPoints.length > 0 && (
                <div>
                  <p className="mb-1 font-medium text-white">Key points</p>
                  <ul className="list-disc space-y-1 pl-5 text-gray-300">
                    {data.keyPoints.map((k, i) => (
                      <li key={i}>{k}</li>
                    ))}
                  </ul>
                </div>
              )}
              {data.topics && data.topics.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {data.topics.map((t, i) => (
                    <span key={i} className="rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs text-gray-300">
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {showApiCta && (
            <div className="mt-5 rounded-xl border border-primary/30 bg-primary/5 p-4 text-center sm:text-left">
              <p className="text-sm font-medium text-white">
                With an API key, the same transcript is ~100× cheaper to automate
              </p>
              <p className="mt-1 text-xs text-gray-400">
                5 credits per call · cache hits are free · build bots, n8n, and pipelines without the free-tool limit.
              </p>
              <div className="mt-3 flex flex-col items-stretch gap-2 sm:flex-row sm:items-center">
                <Link
                  href="/signup"
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90"
                >
                  <KeyRound className="size-4" />
                  Get free API credits
                </Link>
                <Link
                  href="/dashboard/tools/tiktok-transcript"
                  className="inline-flex items-center justify-center gap-1.5 text-sm text-gray-300 hover:text-white"
                >
                  Open in dashboard <ArrowRight className="size-3.5" />
                </Link>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
