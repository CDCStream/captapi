"use client";

import { useState } from "react";
import { BLOCK_RULES } from "@/lib/block-rules";
import { CheckCircle2, MinusCircle, XCircle } from "lucide-react";

const VERDICT_UI = {
  yes: { icon: CheckCircle2, cls: "text-emerald-600 dark:text-emerald-400" },
  no: { icon: XCircle, cls: "text-rose-600 dark:text-rose-400" },
  partial: { icon: MinusCircle, cls: "text-amber-600 dark:text-amber-400" },
} as const;

export default function BlockRulesClient() {
  const [active, setActive] = useState(0);
  const p = BLOCK_RULES[active];

  return (
    <div className="mt-8">
      <div className="flex flex-wrap gap-2">
        {BLOCK_RULES.map((r, i) => (
          <button
            key={r.platform}
            onClick={() => setActive(i)}
            className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
              i === active
                ? "border-primary bg-primary text-primary-foreground"
                : "bg-card hover:border-primary/40"
            }`}
          >
            <span className="mr-1.5">{r.emoji}</span>
            {r.platform}
          </button>
        ))}
      </div>

      <div className="mt-5 rounded-2xl border bg-card p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold">Blocking on {p.platform}</h2>
          <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-600 dark:text-emerald-400">
            They are NOT notified
          </span>
        </div>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{p.summary}</p>

        <div className="mt-5 space-y-3">
          {p.rules.map((rule) => {
            const V = VERDICT_UI[rule.verdict];
            const Icon = V.icon;
            return (
              <div key={rule.question} className="flex gap-3 rounded-xl border bg-background p-4">
                <Icon className={`mt-0.5 size-5 shrink-0 ${V.cls}`} />
                <div>
                  <p className="text-sm font-semibold">{rule.question}</p>
                  <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{rule.answer}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
