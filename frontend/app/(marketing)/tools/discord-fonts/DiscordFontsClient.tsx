"use client";

import { useState } from "react";
import { Copy } from "lucide-react";
import { toast } from "sonner";
import { DISCORD_FONT_STYLES, DISCORD_MARKDOWN, styleText } from "@/lib/discord-fonts";

async function copy(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  } catch {
    toast.error("Couldn't copy — please copy manually.");
  }
}

export default function DiscordFontsClient() {
  const [text, setText] = useState("Hello");
  const sample = text.trim() ? text : "Hello";

  return (
    <div className="mt-8 space-y-10">
      <div>
        <label htmlFor="df-input" className="mb-1.5 block text-sm font-medium">
          Your text
        </label>
        <input
          id="df-input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          maxLength={100}
          className="w-full rounded-md border bg-background px-3 py-2.5 text-lg outline-none focus:ring-2 focus:ring-primary/40"
          placeholder="Type something…"
        />
        <p className="mt-1 text-xs text-muted-foreground">
          Tap any style to copy it. These use Unicode letters, so they paste into Discord names, statuses,
          and messages — no bots or Nitro required.
        </p>
      </div>

      <div className="grid gap-2.5 sm:grid-cols-2">
        {DISCORD_FONT_STYLES.map((style) => {
          const out = styleText(sample, style.map);
          return (
            <button
              key={style.name}
              type="button"
              onClick={() => copy(out)}
              className="group flex items-center justify-between gap-3 rounded-xl border bg-card px-4 py-3 text-left transition-colors hover:border-primary/50"
            >
              <div className="min-w-0">
                <p className="text-[11px] uppercase tracking-wide text-muted-foreground">{style.name}</p>
                <p className="truncate text-lg">{out}</p>
              </div>
              <span className="inline-flex shrink-0 items-center gap-1 rounded-md border px-2 py-1 text-xs text-muted-foreground group-hover:bg-muted">
                <Copy className="size-3.5" />
                Copy
              </span>
            </button>
          );
        })}
      </div>

      <div>
        <h2 className="text-2xl font-semibold">Discord markdown formatting</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Discord&apos;s built-in text formatting uses markdown. Copy a syntax pattern and replace the sample
          text.
        </p>
        <div className="mt-4 overflow-x-auto rounded-2xl border">
          <table className="w-full text-sm">
            <thead className="bg-muted/60 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Style</th>
                <th className="px-4 py-3 font-medium">Type this</th>
                <th className="px-4 py-3 font-medium">How it works</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y">
              {DISCORD_MARKDOWN.map((r) => {
                const syntax = r.syntax.replace(/\\n/g, "\n");
                return (
                  <tr key={r.label}>
                    <td className="whitespace-nowrap px-4 py-3 font-medium">{r.label}</td>
                    <td className="px-4 py-3">
                      <code className="rounded bg-muted px-1.5 py-0.5 text-xs">{r.syntax.replace(/\\n/g, "\u21B5")}</code>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{r.note}</td>
                    <td className="px-4 py-3 text-right">
                      <button
                        type="button"
                        onClick={() => copy(syntax)}
                        className="inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs text-muted-foreground hover:bg-muted"
                      >
                        <Copy className="size-3.5" />
                        Copy
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
