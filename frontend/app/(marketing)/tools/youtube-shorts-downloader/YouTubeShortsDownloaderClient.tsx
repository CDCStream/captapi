"use client";

import { useMemo, useState } from "react";
import { Check, Clapperboard, Download, Link2, Loader2, Play, ShieldCheck } from "lucide-react";
import { toast } from "sonner";

const QUALITIES = ["360p", "480p", "720p HD", "1080p HD"];

function parseVideoId(input: string): string | null {
  const value = input.trim();
  if (!value) return null;

  if (/^[a-zA-Z0-9_-]{11}$/.test(value)) return value;

  try {
    const url = new URL(value.startsWith("http") ? value : "https://" + value);
    const host = url.hostname.replace(/^www\./, "");

    if (host === "youtu.be") {
      const id = url.pathname.split("/").filter(Boolean)[0];
      return id && /^[a-zA-Z0-9_-]{11}$/.test(id) ? id : null;
    }

    if (host.endsWith("youtube.com") || host.endsWith("youtube-nocookie.com")) {
      const param = url.searchParams.get("v");
      if (param && /^[a-zA-Z0-9_-]{11}$/.test(param)) return param;

      const parts = url.pathname.split("/").filter(Boolean);
      const marker = parts.findIndex((p) => ["shorts", "embed", "live", "v"].includes(p));
      if (marker !== -1 && parts[marker + 1] && /^[a-zA-Z0-9_-]{11}$/.test(parts[marker + 1])) {
        return parts[marker + 1];
      }
    }
  } catch {
    return null;
  }

  return null;
}

export default function YouTubeShortsDownloaderClient() {
  const [input, setInput] = useState("");
  const [videoId, setVideoId] = useState<string | null>(null);
  const [quality, setQuality] = useState(QUALITIES[2]);
  const [loading, setLoading] = useState(false);

  const watchUrl = useMemo(() => (videoId ? "https://www.youtube.com/shorts/" + videoId : ""), [videoId]);
  const thumbnail = useMemo(
    () => (videoId ? "https://i.ytimg.com/vi/" + videoId + "/hqdefault.jpg" : ""),
    [videoId],
  );

  function handleStart() {
    const id = parseVideoId(input);
    if (!id) {
      toast.error("Paste a valid YouTube Shorts link.");
      setVideoId(null);
      return;
    }
    setLoading(true);
    setVideoId(null);
    window.setTimeout(() => {
      setVideoId(id);
      setLoading(false);
      toast.success("Short found. Choose a quality below.");
    }, 450);
  }

  return (
    <section className="mt-8">
      <div className="rounded-2xl border border-white/10 bg-zinc-950 p-5 sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Link2 className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-gray-500" />
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => event.key === "Enter" && handleStart()}
              placeholder="Paste a YouTube Shorts link, e.g. https://www.youtube.com/shorts/..."
              className="w-full rounded-lg border border-white/15 bg-zinc-900 py-3 pl-9 pr-3 text-sm text-white placeholder:text-gray-500 outline-none focus:border-primary"
            />
          </div>
          <button
            type="button"
            onClick={handleStart}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-7 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-60"
          >
            {loading ? <Loader2 className="size-4 animate-spin" /> : <Download className="size-4" />}
            Download
          </button>
        </div>
        <p className="mt-2 text-xs text-gray-500">
          Free, no sign-up. Works with youtube.com/shorts, youtu.be, and standard watch links.
        </p>

        {videoId ? (
          <div className="mt-6 grid gap-5 lg:grid-cols-[320px_1fr]">
            <div className="relative overflow-hidden rounded-xl border border-white/10 bg-black">
              <img src={thumbnail} alt="YouTube Shorts preview" className="aspect-video w-full object-cover" />
              <span className="absolute left-2 top-2 rounded-md bg-black/70 px-2 py-1 text-xs font-medium text-white">
                Shorts
              </span>
            </div>

            <div>
              <p className="text-sm font-medium text-white">Choose your MP4 quality</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {QUALITIES.map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setQuality(option)}
                    className={
                      "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm transition-colors " +
                      (quality === option
                        ? "border-primary bg-primary/15 text-white"
                        : "border-white/15 bg-zinc-900 text-gray-200 hover:bg-white/10")
                    }
                  >
                    {quality === option ? <Check className="size-3.5" /> : null}
                    {option}
                  </button>
                ))}
              </div>

              <div className="mt-5 rounded-xl border border-white/10 bg-zinc-900 p-4">
                <p className="flex items-center gap-2 text-sm font-medium text-white">
                  <Clapperboard className="size-4 text-primary" /> Save this Short as MP4 ({quality})
                </p>
                <ol className="mt-3 space-y-2 text-sm text-gray-300">
                  <li>1. Open the Short on YouTube using the button below.</li>
                  <li>2. Use YouTube Premium offline download, or your own licensed/owned content export.</li>
                  <li>3. For your own uploads, download the original MP4 from YouTube Studio in your selected quality.</li>
                </ol>
                <div className="mt-4 flex flex-wrap gap-2">
                  <a
                    href={watchUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90"
                  >
                    <Play className="size-4" /> Open Short on YouTube
                  </a>
                </div>
                <p className="mt-3 flex items-start gap-2 text-xs text-gray-500">
                  <ShieldCheck className="mt-0.5 size-3.5 shrink-0" />
                  Only download Shorts you own or that are licensed for download. Respect YouTube&apos;s Terms of Service and copyright.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-6 flex min-h-[180px] flex-col items-center justify-center rounded-xl border border-dashed border-white/15 bg-zinc-900 p-6 text-center">
            <Clapperboard className="mb-3 size-8 text-gray-500" />
            <p className="font-medium text-white">Paste a YouTube Shorts link to get started.</p>
            <p className="mt-1 max-w-sm text-sm text-gray-400">
              We will fetch the Short preview and show MP4 quality options from 360p to 1080p HD.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
