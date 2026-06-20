"use client";

import { useState } from "react";
import { Download, ExternalLink, Image as ImageIcon, Link2, Loader2, ShieldCheck } from "lucide-react";
import { toast } from "sonner";

type ParsedPost = { shortcode: string; kind: string; url: string };

function parsePost(input: string): ParsedPost | null {
  const value = input.trim();
  if (!value) return null;

  try {
    const url = new URL(value.startsWith("http") ? value : "https://" + value);
    const host = url.hostname.replace(/^www\./, "");
    if (!host.endsWith("instagram.com")) return null;

    const parts = url.pathname.split("/").filter(Boolean);
    const marker = parts.findIndex((p) => ["p", "reel", "reels", "tv"].includes(p));
    if (marker === -1) return null;

    const shortcode = parts[marker + 1];
    if (!shortcode || !/^[A-Za-z0-9_-]{5,20}$/.test(shortcode)) return null;

    const kindMap: Record<string, string> = { p: "Post", reel: "Reel", reels: "Reel", tv: "IGTV" };
    return {
      shortcode,
      kind: kindMap[parts[marker]] || "Post",
      url: "https://www.instagram.com/" + parts[marker] + "/" + shortcode + "/",
    };
  } catch {
    return null;
  }
}

export default function InstagramPhotoDownloaderClient() {
  const [input, setInput] = useState("");
  const [post, setPost] = useState<ParsedPost | null>(null);
  const [loading, setLoading] = useState(false);

  function handleStart() {
    const parsed = parsePost(input);
    if (!parsed) {
      toast.error("Paste a valid Instagram post, reel, or photo link.");
      setPost(null);
      return;
    }
    setLoading(true);
    setPost(null);
    window.setTimeout(() => {
      setPost(parsed);
      setLoading(false);
      toast.success(parsed.kind + " found. Follow the steps to save it.");
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
              placeholder="Paste an Instagram photo link, e.g. https://www.instagram.com/p/..."
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
          Free, no login. Works with public posts, reels, and photo links from instagram.com.
        </p>

        {post ? (
          <div className="mt-6 rounded-xl border border-white/10 bg-zinc-900 p-4 sm:p-5">
            <div className="flex items-center gap-3">
              <div className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-amber-400 via-pink-500 to-purple-600 text-white">
                <ImageIcon className="size-5" />
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-white">Instagram {post.kind} detected</p>
                <p className="truncate text-xs text-gray-400">/{post.shortcode}</p>
              </div>
            </div>

            <div className="mt-4">
              <p className="text-sm font-medium text-white">Save this photo to your device</p>
              <ol className="mt-3 space-y-2 text-sm text-gray-300">
                <li>1. Open the post in full size using the button below.</li>
                <li>2. On desktop, right-click the image and choose &ldquo;Save image as&rdquo;.</li>
                <li>3. On mobile, press and hold the image, then tap &ldquo;Save&rdquo; or &ldquo;Download image&rdquo;.</li>
              </ol>
              <div className="mt-4 flex flex-wrap gap-2">
                <a
                  href={post.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90"
                >
                  <ExternalLink className="size-4" /> Open photo on Instagram
                </a>
              </div>
              <p className="mt-3 flex items-start gap-2 text-xs text-gray-500">
                <ShieldCheck className="mt-0.5 size-3.5 shrink-0" />
                Only download photos you own or that are licensed for download. Respect Instagram&apos;s Terms of Service and copyright.
              </p>
            </div>
          </div>
        ) : (
          <div className="mt-6 flex min-h-[180px] flex-col items-center justify-center rounded-xl border border-dashed border-white/15 bg-zinc-900 p-6 text-center">
            <ImageIcon className="mb-3 size-8 text-gray-500" />
            <p className="font-medium text-white">Paste an Instagram photo link to get started.</p>
            <p className="mt-1 max-w-sm text-sm text-gray-400">
              We will detect the post and show clear steps to save the image in its original quality.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
