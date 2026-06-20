"use client";

import { useMemo, useState } from "react";
import { Check, Copy, Search } from "lucide-react";
import { toast } from "sonner";
import { TIKTOK_EMOJIS, tiktokEmojiImage } from "@/lib/tiktok-emojis";

export default function TikTokEmojisClient() {
  const [query, setQuery] = useState("");
  const [copied, setCopied] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return TIKTOK_EMOJIS;
    return TIKTOK_EMOJIS.filter(
      (e) => e.name.toLowerCase().includes(q) || e.code.toLowerCase().includes(q),
    );
  }, [query]);

  async function copyCode(code: string) {
    const text = "[" + code + "]";
    try {
      await navigator.clipboard.writeText(text);
      setCopied(code);
      toast.success("Copied " + text + " to clipboard");
      window.setTimeout(() => setCopied((c) => (c === code ? null : c)), 1500);
    } catch {
      toast.error("Could not copy. Long-press to copy manually.");
    }
  }

  return (
    <section className="mt-8">
      <div className="rounded-2xl border border-white/10 bg-zinc-950 p-5 sm:p-6">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-gray-500" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search emojis by name or code, e.g. smile, laugh, cool"
            className="w-full rounded-lg border border-white/15 bg-zinc-900 py-3 pl-9 pr-3 text-sm text-white placeholder:text-gray-500 outline-none focus:border-primary"
          />
        </div>
        <p className="mt-2 text-xs text-gray-500">
          {filtered.length} of {TIKTOK_EMOJIS.length} emojis. Tap any card to copy its code.
        </p>

        {filtered.length ? (
          <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {filtered.map((emoji) => (
              <button
                key={emoji.code}
                type="button"
                onClick={() => copyCode(emoji.code)}
                title={"Copy [" + emoji.code + "]"}
                className="group flex items-center gap-3 rounded-xl border border-white/10 bg-zinc-900 p-3 text-left transition-colors hover:border-primary/60 hover:bg-white/5"
              >
                <img
                  src={tiktokEmojiImage(emoji.code)}
                  alt={emoji.name + " TikTok emoji"}
                  loading="lazy"
                  width={44}
                  height={44}
                  className="size-11 shrink-0 rounded-md bg-black/20 object-contain"
                  onError={(event) => {
                    event.currentTarget.style.visibility = "hidden";
                  }}
                />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-white">{emoji.name}</p>
                  <p className="truncate font-mono text-xs text-gray-400">[{emoji.code}]</p>
                </div>
                <span className="shrink-0 text-gray-500 group-hover:text-primary">
                  {copied === emoji.code ? <Check className="size-4 text-primary" /> : <Copy className="size-4" />}
                </span>
              </button>
            ))}
          </div>
        ) : (
          <div className="mt-6 flex min-h-[140px] flex-col items-center justify-center rounded-xl border border-dashed border-white/15 bg-zinc-900 p-6 text-center">
            <p className="font-medium text-white">No emojis match &ldquo;{query}&rdquo;.</p>
            <p className="mt-1 text-sm text-gray-400">Try a different name or code.</p>
          </div>
        )}
      </div>
    </section>
  );
}
