"use client";

import { useState } from "react";
import { AtSign, ExternalLink, Eye, Loader2, MessageSquare, Repeat2, ShieldCheck, Sparkles, User } from "lucide-react";
import { toast } from "sonner";

function parseUsername(input: string): string | null {
  let value = input.trim();
  if (!value) return null;

  value = value.replace(/^@/, "");

  try {
    if (/^https?:\/\//i.test(value) || value.includes("threads.")) {
      const url = new URL(value.startsWith("http") ? value : "https://" + value);
      const host = url.hostname.replace(/^www\./, "");
      if (host === "threads.net" || host === "threads.com") {
        const match = url.pathname.match(/\/@([^/]+)/);
        if (match) value = match[1];
      }
    }
  } catch {
    return null;
  }

  value = value.replace(/^@/, "");
  return /^[A-Za-z0-9._]{1,30}$/.test(value) ? value : null;
}

const CONTENT_TYPES = [
  { label: "Profile & bio", icon: <User className="size-4 text-primary" /> },
  { label: "Threads (posts)", icon: <MessageSquare className="size-4 text-primary" /> },
  { label: "Replies", icon: <Sparkles className="size-4 text-primary" /> },
  { label: "Reposts", icon: <Repeat2 className="size-4 text-primary" /> },
];

export default function ThreadsViewerClient() {
  const [input, setInput] = useState("");
  const [username, setUsername] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const profileUrl = username ? "https://www.threads.com/@" + username : "";

  function handleView() {
    const handle = parseUsername(input);
    if (!handle) {
      toast.error("Enter a valid Threads username, e.g. @zuck");
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
              placeholder="Enter a Threads username, e.g. @zuck"
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
          Free, no login. Works with public profiles only. Accepts @username or a threads.com profile link.
        </p>

        {username ? (
          <div className="mt-6 rounded-xl border border-white/10 bg-zinc-900 p-4 sm:p-5">
            <div className="flex items-center gap-3">
              <div className="flex size-12 shrink-0 items-center justify-center rounded-full bg-gradient-to-tr from-zinc-200 to-zinc-500 text-base font-bold text-black">
                {username.slice(0, 1).toUpperCase()}
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-white">@{username}</p>
                <p className="truncate text-xs text-gray-400">threads.com/@{username}</p>
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
                <Sparkles className="size-4 text-primary" /> Browse this profile anonymously
              </p>
              <ol className="mt-3 space-y-2 text-sm text-gray-300">
                <li>1. Open the public profile using the button below.</li>
                <li>2. Read threads, replies, and reposts at your own pace, without logging in.</li>
                <li>3. Threads does not notify anyone when you view their profile or posts.</li>
              </ol>
              <div className="mt-4 flex flex-wrap gap-2">
                <a
                  href={profileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90"
                >
                  <ExternalLink className="size-4" /> Open @{username} on Threads
                </a>
              </div>
              <p className="mt-3 flex items-start gap-2 text-xs text-gray-500">
                <ShieldCheck className="mt-0.5 size-3.5 shrink-0" />
                Only public profiles can be viewed. Respect Threads&apos; Terms of Service and other people&apos;s privacy.
              </p>
            </div>
          </div>
        ) : (
          <div className="mt-6 flex min-h-[180px] flex-col items-center justify-center rounded-xl border border-dashed border-white/15 bg-zinc-900 p-6 text-center">
            <Eye className="mb-3 size-8 text-gray-500" />
            <p className="font-medium text-white">Enter a Threads username to get started.</p>
            <p className="mt-1 max-w-sm text-sm text-gray-400">
              We will prepare a quick, anonymous way to open a public profile and read its threads, replies, and reposts without an account.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
