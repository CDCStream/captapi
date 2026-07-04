"use client";

import { useMemo, useState } from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { CHAR_LIMITS } from "@/lib/char-limits";

export default function CharCounterClient() {
  const [text, setText] = useState("");
  const count = text.length;
  const words = useMemo(() => (text.trim() ? text.trim().split(/\s+/).length : 0), [text]);

  return (
    <div className="mt-8 grid gap-6 lg:grid-cols-2">
      <div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={10}
          className="w-full rounded-2xl border bg-background p-4 text-base outline-none focus:ring-2 focus:ring-primary/40"
          placeholder="Paste or type your caption, bio, post, or title here…"
        />
        <div className="mt-2 flex gap-4 text-sm text-muted-foreground">
          <span>
            <strong className="text-foreground tabular-nums">{count.toLocaleString()}</strong> characters
          </span>
          <span>
            <strong className="text-foreground tabular-nums">{words.toLocaleString()}</strong> words
          </span>
        </div>
      </div>

      <div className="max-h-[480px] space-y-4 overflow-y-auto pr-1">
        {CHAR_LIMITS.map((p) => (
          <div key={p.id} className="rounded-2xl border bg-card p-4">
            <h3 className="font-semibold">{p.label}</h3>
            <div className="mt-2 space-y-1.5">
              {p.limits.map((l) => {
                const isCountField = l.note === "count, not characters";
                const fits = isCountField || count <= l.limit;
                const active = count > 0 && !isCountField;
                return (
                  <div key={l.field} className="flex items-center justify-between gap-2 text-sm">
                    <span className="text-muted-foreground">
                      {l.field}
                      {l.note && <span className="ml-1 text-xs text-muted-foreground/70">({l.note})</span>}
                    </span>
                    <span className={`flex items-center gap-1.5 whitespace-nowrap tabular-nums font-medium ${
                      !active ? "" : fits ? "text-emerald-600 dark:text-emerald-400" : "text-red-500"
                    }`}>
                      {active && (fits ? <CheckCircle2 className="size-3.5" /> : <XCircle className="size-3.5" />)}
                      {isCountField ? l.limit : `${active ? `${count.toLocaleString()} / ` : ""}${l.limit.toLocaleString()}`}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
