import { Sparkles } from "lucide-react";

// Answer-first "TL;DR" callout. Surfaces a concise, direct answer at the top
// of a page so both readers and AI answer engines get the gist immediately.
export function Tldr({ children }: { children: React.ReactNode }) {
  return (
    <div className="not-prose my-6 rounded-xl border border-primary/20 bg-primary/5 p-4 md:p-5">
      <div className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-primary">
        <Sparkles className="size-3.5" />
        TL;DR
      </div>
      <div className="text-sm leading-relaxed text-foreground/90">{children}</div>
    </div>
  );
}
