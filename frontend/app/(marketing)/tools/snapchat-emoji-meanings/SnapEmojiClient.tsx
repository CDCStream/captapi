"use client";

import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { SNAP_EMOJIS, SNAP_CATEGORIES } from "@/lib/snapchat-emojis";

export default function SnapEmojiClient() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string>("All");

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    return SNAP_EMOJIS.filter((e) => {
      if (category !== "All" && e.category !== category) return false;
      if (!q) return true;
      return e.name.toLowerCase().includes(q) || e.meaning.toLowerCase().includes(q) || e.emoji.includes(q);
    });
  }, [query, category]);

  return (
    <div className="mt-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full rounded-md border bg-background py-2.5 pl-9 pr-3 outline-none focus:ring-2 focus:ring-primary/40"
            placeholder="Search an emoji or meaning, e.g. yellow heart, hourglass…"
          />
        </div>
        <div className="flex flex-wrap gap-1.5">
          {SNAP_CATEGORIES.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setCategory(c)}
              className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
                category === c ? "border-primary bg-primary/10 text-primary" : "hover:bg-muted"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <p className="mt-3 text-xs text-muted-foreground">
        {results.length} of {SNAP_EMOJIS.length} entries
      </p>

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        {results.map((e) => (
          <div key={`${e.emoji}-${e.name}`} className="flex items-start gap-3 rounded-xl border bg-card p-4">
            <span className="text-3xl leading-none">{e.emoji}</span>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold">{e.name}</h3>
                <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                  {e.category}
                </span>
              </div>
              <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{e.meaning}</p>
            </div>
          </div>
        ))}
        {results.length === 0 && (
          <p className="col-span-full rounded-xl border border-dashed p-8 text-center text-sm text-muted-foreground">
            No matches — try a shorter search or set the category to All.
          </p>
        )}
      </div>
    </div>
  );
}
