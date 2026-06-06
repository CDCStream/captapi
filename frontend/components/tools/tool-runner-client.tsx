"use client";

import { useCallback, useState } from "react";
import { Loader2, Copy, Download, Search, RefreshCw } from "lucide-react";
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
  const [data, setData] = useState<ResultData | null>(null);

  const run = useCallback(async () => {
    if (!url.trim()) {
      toast.error("Please paste a video URL.");
      return;
    }
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch("/api/tool-run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ endpoint, url: url.trim() }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json?.error || "Request failed. Please try again.");
      setData(json.data as ResultData);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }, [endpoint, url]);

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
            onKeyDown={(e) => e.key === "Enter" && run()}
            placeholder={placeholder || `Paste a ${platform} video URL`}
            aria-label={`${platform} video URL`}
            className="w-full rounded-lg border border-white/15 bg-zinc-900 py-2.5 pl-9 pr-3 text-sm text-white placeholder:text-gray-500 outline-none focus:border-primary"
          />
        </div>
        <button
          type="button"
          onClick={run}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-60"
        >
          {loading ? <Loader2 className="size-4 animate-spin" /> : null}
          {loading ? "Working…" : kind === "transcript" ? "Get transcript" : "Summarize"}
        </button>
      </div>
      <p className="mt-2 text-center text-xs text-gray-500 sm:text-left">
        Free · no sign-up required · public videos only
      </p>

      {error && (
        <div className="mt-4 flex flex-col items-center justify-center rounded-2xl border border-white/10 bg-zinc-950 p-6 text-center">
          <p className="text-sm text-rose-400">{error}</p>
          <button
            type="button"
            onClick={run}
            className="mt-3 inline-flex items-center gap-1.5 rounded-md border border-white/15 px-3 py-1.5 text-sm text-gray-200 hover:bg-white/10"
          >
            <RefreshCw className="size-3.5" /> Try again
          </button>
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
        </div>
      )}
    </div>
  );
}
