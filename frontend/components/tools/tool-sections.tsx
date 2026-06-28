import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { absoluteUrl } from "@/lib/seo";
import { ENDPOINT_COUNT, PLATFORM_COUNT } from "@/lib/api-catalog";

/** WebApplication JSON-LD for a free tool. */
export function webApplicationLd(input: {
  name: string;
  description: string;
  path: string;
  category?: string;
}) {
  return {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    name: input.name,
    description: input.description,
    url: absoluteUrl(input.path),
    applicationCategory: input.category ?? "MultimediaApplication",
    operatingSystem: "Any (web-based)",
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
    provider: { "@type": "Organization", name: "Captapi", url: absoluteUrl("/") },
  };
}

export function ToolHero({
  platform,
  title,
  subtitle,
}: {
  platform: string;
  title: string;
  subtitle: string;
}) {
  return (
    <header className="max-w-3xl">
      <Badge variant="secondary" className="mb-3">
        {platform} · Free tool
      </Badge>
      <h1 className="text-4xl font-bold tracking-tight">{title}</h1>
      <p className="mt-3 text-lg text-muted-foreground">{subtitle}</p>
    </header>
  );
}

export type HowToStep = { title: string; text: string; icon?: React.ReactNode };

export function HowToUse({ steps }: { steps: HowToStep[] }) {
  return (
    <section className="mt-16">
      <h2 className="text-2xl font-semibold">How to use it</h2>
      <ol className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {steps.map((s, i) => (
          <li key={i} className="rounded-xl border bg-card p-5">
            <div className="mb-3 flex items-center gap-2">
              <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                {i + 1}
              </span>
              {s.icon && <span className="text-muted-foreground">{s.icon}</span>}
            </div>
            <p className="font-medium">{s.title}</p>
            <p className="mt-1 text-sm text-muted-foreground">{s.text}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}

export function FAQSection({ faqs }: { faqs: { q: string; a: string }[] }) {
  if (!faqs.length) return null;
  return (
    <section className="mt-16">
      <h2 className="text-2xl font-semibold">Frequently asked questions</h2>
      <div className="mt-6 divide-y rounded-xl border">
        {faqs.map((f, i) => (
          <details key={i} className="group px-5 py-4">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-medium">
              {f.q}
              <span className="text-muted-foreground transition-transform group-open:rotate-45">+</span>
            </summary>
            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{f.a}</p>
          </details>
        ))}
      </div>
    </section>
  );
}

/** Keyword-rich long-form content wrapper. Pass section JSX as children. */
export function LongContent({ children }: { children: React.ReactNode }) {
  return (
    <section className="mt-16 max-w-3xl space-y-10 text-[15px] leading-relaxed text-muted-foreground [&_h2]:text-2xl [&_h2]:font-semibold [&_h2]:text-foreground [&_h3]:mt-6 [&_h3]:text-lg [&_h3]:font-semibold [&_h3]:text-foreground [&_p]:mt-3 [&_ul]:mt-3 [&_ul]:list-disc [&_ul]:space-y-1 [&_ul]:pl-5">
      {children}
    </section>
  );
}

/** Bottom CTA — "more than a tool" → drive to signup. */
export function ToolCTA({
  headline = "Need this at scale?",
  sub = `These free tools run on Captapi — the social data API with ${ENDPOINT_COUNT} endpoints across ${PLATFORM_COUNT} platforms. Sign up for 100 free credits and automate transcripts, comments, stats, and more.`,
}: {
  headline?: string;
  sub?: string;
}) {
  const points = [
    "100 free credits, no card required",
    `${ENDPOINT_COUNT} endpoints across ${PLATFORM_COUNT} platforms`,
    "Clean JSON — MCP, CLI, n8n, Make & Apify ready",
  ];
  return (
    <section className="mt-20 overflow-hidden rounded-2xl border bg-muted/30 p-8 text-center">
      <h2 className="text-2xl font-bold tracking-tight">{headline}</h2>
      <p className="mx-auto mt-2 max-w-2xl text-muted-foreground">{sub}</p>
      <ul className="mx-auto mt-5 flex max-w-2xl flex-col flex-wrap justify-center gap-2 sm:flex-row sm:gap-5">
        {points.map((p) => (
          <li key={p} className="flex items-center justify-center gap-1.5 text-sm text-muted-foreground">
            <Check className="size-4 text-primary" />
            {p}
          </li>
        ))}
      </ul>
      <div className="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
        <Link
          href="/signup"
          className="inline-flex h-11 items-center rounded-md bg-primary px-6 text-sm font-medium text-primary-foreground hover:opacity-90"
        >
          Get your free API key
        </Link>
        <Link
          href="/tools"
          className="inline-flex h-11 items-center gap-1.5 rounded-md border px-6 text-sm font-medium hover:bg-muted"
        >
          Explore all free tools
          <ArrowRight className="size-4" />
        </Link>
      </div>
    </section>
  );
}
