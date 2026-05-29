"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";

export interface CodeSample {
  label: string;
  code: string;
}

export function CodeTabs({ samples }: { samples: CodeSample[] }) {
  const [active, setActive] = useState(0);
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(samples[active].code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <div className="overflow-hidden rounded-xl border border-white/10 bg-[#0d1117] text-sm">
      <div className="flex items-center justify-between border-b border-white/10 bg-white/[0.03] pl-1 pr-2">
        <div className="flex items-center overflow-x-auto">
          {samples.map((s, i) => (
            <button
              key={s.label}
              onClick={() => setActive(i)}
              className={`whitespace-nowrap px-3 py-2.5 text-xs font-medium transition-colors ${
                i === active
                  ? "text-white border-b-2 border-primary"
                  : "text-slate-400 hover:text-slate-200 border-b-2 border-transparent"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
        <button
          onClick={copy}
          className="flex shrink-0 items-center gap-1.5 rounded-md px-2 py-1 text-xs text-slate-400 transition-colors hover:bg-white/10 hover:text-white"
          aria-label="Copy code"
        >
          {copied ? (
            <>
              <Check className="size-3.5" /> Copied
            </>
          ) : (
            <>
              <Copy className="size-3.5" /> Copy
            </>
          )}
        </button>
      </div>
      <pre className="overflow-x-auto p-4 leading-relaxed">
        <code className="text-slate-200">{samples[active].code}</code>
      </pre>
    </div>
  );
}
