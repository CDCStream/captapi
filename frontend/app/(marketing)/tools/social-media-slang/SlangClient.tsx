"use client";

import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { SLANG_TERMS } from "@/lib/slang-terms";

const ALL_PLATFORMS = ["All", "TikTok", "Snapchat", "Instagram", "Discord", "Twitch", "X"];

export default function SlangClient() {
  const [query, setQuery] = useState("");
  const [platform, setPlatform] = useState("All");

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    return SLANG_TERMS.filter((t) => {
      if (platform !== "All" && !t.platforms.includes(platform)) return false;
      if (!q) return true;
      return t.term.toLowerCase().includes(q) || t.meaning.toLowerCase().includes(q);
    });
  }, [query, platform]);

  return (
    <div className="mt-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full rounded-md border bg-background py-2.5 pl-9 pr-3 outline-none focus:ring-2 focus:ring-primary/40"
            placeholder="Search a term, e.g. pmo, nfs, rizz…"
          />
        </div>
        <div className="flex flex-wrap gap-1.5">
          {ALL_PLATFORMS.map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => setPlatform(p)}
              className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
                platform === p ? "border-primary bg-primary/10 text-primary" : "hover:bg-muted"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      <p className="mt-3 text-xs text-muted-foreground">
        {results.length} of {SLANG_TERMS.length} terms
      </p>

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        {results.map((t) => (
          <div key={t.term} className="rounded-xl border bg-card p-4">
            <div className="flex items-start justify-between gap-2">
              <h3 className="text-lg font-bold">{t.term}</h3>
              <div className="flex flex-wrap justify-end gap-1">
                {t.platforms.map((p) => (
                  <span key={p} className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                    {p}
                  </span>
                ))}
              </div>
            </div>
            <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{t.meaning}</p>
            {t.example && (
              <p className="mt-2 text-xs italic text-muted-foreground/80">&ldquo;{t.example}&rdquo;</p>
            )}
          </div>
        ))}
        {results.length === 0 && (
          <p className="col-span-full rounded-xl border border-dashed p-8 text-center text-sm text-muted-foreground">
            No matches — try a shorter search or switch the platform filter to All.
          </p>
        )}
      </div>
    </div>
  );
}
