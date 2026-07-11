"use client";

import { useState } from "react";
import { AtSign, ExternalLink, Eye, Film, Loader2, Music2, ShieldCheck, Sparkles, User } from "lucide-react";
import { toast } from "sonner";

function parseUsername(input: string): string | null {
  let value = input.trim();
  if (!value) return null;

  value = value.replace(/^@/, "");

  try {
    if (/^https?:\/\//i.test(value) || value.includes("tiktok.com")) {
      const url = new URL(value.startsWith("http") ? value : "https://" + value);
      const host = url.hostname.replace(/^www\./, "");
      if (host.endsWith("tiktok.com")) {
        const match = url.pathname.match(/\/@([^/]+)/);
        if (match) value = match[1];
      }
    }
  } catch {
    return null;
  }

  value = value.replace(/^@/, "");
  return /^[A-Za-z0-9._]{1,24}$/.test(value) ? value : null;
}

const CONTENT_TYPES = [
  { label: "Profile & bio", icon: <User className="size-4 text-primary" /> },
  { label: "Videos", icon: <Film className="size-4 text-primary" /> },
  { label: "Stories", icon: <Sparkles className="size-4 text-primary" /> },
  { label: "Liked sounds", icon: <Music2 className="size-4 text-primary" /> },
];

export default function TikTokViewerClient() {
  const [input, setInput] = useState("");
  const [username, setUsername] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const profileUrl = username ? "https://www.tiktok.com/@" + username : "";

  function handleView() {
    const handle = parseUsername(input);
    if (!handle) {
      toast.error("Enter a valid TikTok username, e.g. @nba");
      setUsername(null);
      return;
    }
    setLoading(true);
    setUsername(null);
    window.setTimeout(() => {
      setUsername(handle);
      setLoading(false);
      toast.success("Profile ready. Open it below.");
    }, 450);
  }

  return (
    <section className="mt-8">
      <div className="rounded-2xl border border-white/10 bg-zinc-950 p-5 sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <AtSign className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-gray-500" />
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => event.key === "Enter" && handleView()}
              placeholder="Enter a TikTok username, e.g. @nba"
              className="w-full rounded-lg border border-white/15 bg-zinc-900 py-3 pl-9 pr-3 text-sm text-white placeholder:text-gray-500 outline-none focus:border-primary"
            />
          </div>
          <button
            type="button"
            onClick={handleView}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-7 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-60"
          >
            {loading ? <Loader2 className="size-4 animate-spin" /> : <Eye className="size-4" />}
            View profile
          </button>
        </div>
        <p className="mt-2 text-xs text-gray-500">
          Free, no login. Works with public accounts only. Accepts @username or a tiktok.com profile link.
        </p>

        {username ? (
          <div className="mt-6 rounded-xl border border-white/10 bg-zinc-900 p-4 sm:p-5">
            <div className="flex items-center gap-3">
              <div className="flex size-12 shrink-0 items-center justify-center rounded-full bg-gradient-to-tr from-cyan-400 via-fuchsia-500 to-rose-500 text-base font-bold text-white">
                {username.slice(0, 1).toUpperCase()}
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-white">@{username}</p>
                <p className="truncate text-xs text-gray-400">tiktok.com/@{username}</p>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
              {CONTENT_TYPES.map((item) => (
                <div key={item.label} className="flex items-center gap-2 rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-xs text-gray-200">
                  {item.icon}
                  {item.label}
                </div>
              ))}
            </div>

            <div className="mt-4">
              <p className="flex items-center gap-2 text-sm font-medium text-white">
                <Sparkles className="size-4 text-primary" /> Watch this account anonymously
              </p>
              <ol className="mt-3 space-y-2 text-sm text-gray-300">
                <li>1. Open the public profile using the button below.</li>
                <li>2. Watch videos and browse the profile at your own pace, without logging in.</li>
                <li>3. Because you are not signed in, no view is linked to you and the owner is not notified.</li>
              </ol>
              <div className="mt-4 flex flex-wrap gap-2">
                <a
                  href={profileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90"
                >
                  <ExternalLink className="size-4" /> Open @{username} on TikTok
                </a>
              </div>
              <p className="mt-3 flex items-start gap-2 text-xs text-gray-500">
                <ShieldCheck className="mt-0.5 size-3.5 shrink-0" />
                Only public accounts can be viewed. Respect TikTok&apos;s Terms of Service and other people&apos;s privacy.
              </p>
            </div>
          </div>
        ) : (
          <div className="mt-6 flex min-h-[180px] flex-col items-center justify-center rounded-xl border border-dashed border-white/15 bg-zinc-900 p-6 text-center">
            <Eye className="mb-3 size-8 text-gray-500" />
            <p className="font-medium text-white">Enter a TikTok username to get started.</p>
            <p className="mt-1 max-w-sm text-sm text-gray-400">
              We will prepare a quick, anonymous way to open a public account and watch its videos and stories without an account.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
