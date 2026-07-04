"use client";

import { useState } from "react";
import { Download, ExternalLink, ImageIcon, Search } from "lucide-react";
import { toast } from "sonner";

function extractId(input: string): string | null {
  const raw = input.trim();
  if (!raw) return null;
  if (/^[a-zA-Z0-9_-]{11}$/.test(raw)) return raw;
  try {
    const url = new URL(raw.includes("://") ? raw : `https://${raw}`);
    if (url.hostname.includes("youtu.be")) {
      const id = url.pathname.slice(1, 12);
      return /^[a-zA-Z0-9_-]{11}$/.test(id) ? id : null;
    }
    const v = url.searchParams.get("v");
    if (v && /^[a-zA-Z0-9_-]{11}$/.test(v)) return v;
    const m = url.pathname.match(/\/(shorts|embed|v)\/([a-zA-Z0-9_-]{11})/);
    if (m) return m[2];
  } catch {
    return null;
  }
  return null;
}

const SIZES = [
  { key: "maxresdefault", label: "Max HD", dim: "1280×720" },
  { key: "sddefault", label: "SD", dim: "640×480" },
  { key: "hqdefault", label: "High", dim: "480×360" },
  { key: "mqdefault", label: "Medium", dim: "320×180" },
  { key: "default", label: "Default", dim: "120×90" },
];

export default function YouTubeThumbnailDownloaderClient() {
  const [input, setInput] = useState("");
  const [id, setId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    const found = extractId(input);
    if (!found) {
      setError("Enter a valid YouTube video URL or 11-character video ID.");
      setId(null);
      return;
    }
    setError(null);
    setId(found);
  };

  const download = async (url: string, name: string) => {
    try {
      const res = await fetch(url, { mode: "cors" });
      if (!res.ok) throw new Error("not ok");
      const blob = await res.blob();
      const href = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = href;
      a.download = name;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(href);
    } catch {
      // Cross-origin download can be blocked; fall back to opening the image.
      window.open(url, "_blank", "noopener");
      toast.info("Opened the image in a new tab — long-press or right-click to save.");
    }
  };

  return (
    <div className="mt-8 space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && load()}
            className="w-full rounded-md border bg-background py-2.5 pl-9 pr-3 outline-none focus:ring-2 focus:ring-primary/40"
            placeholder="Paste a YouTube URL or video ID"
          />
        </div>
        <button
          type="button"
          onClick={load}
          className="inline-flex h-11 items-center justify-center gap-1.5 rounded-md bg-primary px-6 text-sm font-medium text-primary-foreground hover:opacity-90"
        >
          <ImageIcon className="size-4" />
          Get thumbnails
        </button>
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}

      {id && (
        <div className="space-y-6">
          <div className="overflow-hidden rounded-2xl border bg-card">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`https://img.youtube.com/vi/${id}/maxresdefault.jpg`}
              alt="YouTube video thumbnail (max resolution)"
              className="w-full"
              onError={(e) => {
                (e.currentTarget as HTMLImageElement).src = `https://img.youtube.com/vi/${id}/hqdefault.jpg`;
              }}
            />
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {SIZES.map((s) => {
              const url = `https://img.youtube.com/vi/${id}/${s.key}.jpg`;
              return (
                <div key={s.key} className="flex items-center justify-between gap-3 rounded-xl border bg-card p-4">
                  <div>
                    <p className="font-medium">{s.label}</p>
                    <p className="text-xs text-muted-foreground">{s.dim}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => download(url, `youtube-${id}-${s.key}.jpg`)}
                      className="inline-flex items-center gap-1 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:opacity-90"
                    >
                      <Download className="size-3.5" />
                      Save
                    </button>
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 rounded-md border px-3 py-1.5 text-xs hover:bg-muted"
                    >
                      <ExternalLink className="size-3.5" />
                      Open
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <p className="text-xs text-muted-foreground">
        Not every video has a 1280×720 Max HD thumbnail — older or lower-resolution uploads may only have
        smaller sizes, in which case the preview automatically falls back. This tool works with public videos
        and Shorts.
      </p>
    </div>
  );
}
