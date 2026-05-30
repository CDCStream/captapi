import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Check, X, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SITE_URL } from "@/lib/api-catalog";
import {
  COMPETITOR_LIST,
  COMPETITOR_SLUGS,
  getCompetitor,
  CAPTAPI,
  COMPARE_AS_OF,
  type Cap,
  type Competitor,
} from "@/lib/competitors";

export function generateStaticParams() {
  return COMPETITOR_SLUGS.map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const c = getCompetitor(slug);
  if (!c) return {};
  const year = new Date().getFullYear();
  const title = `Best ${c.name} Alternative (${year}) — Captapi`;
  const description = `Looking for a ${c.name} alternative? Captapi is one REST API for transcripts, AI summaries, comments & engagement across YouTube, TikTok, Instagram & Facebook. 100 free credits.`;
  const url = `${SITE_URL}/alternatives/${c.slug}`;
  return {
    title,
    description,
    keywords: [
      c.targetKeyword,
      `${c.name} alternative`,
      `${c.name} vs Captapi`,
      "social media API",
      "video transcript API",
    ],
    alternates: { canonical: url },
    openGraph: { title, description, url, type: "article" },
    twitter: { card: "summary_large_image", title, description },
  };
}

function jsonLd(c: Competitor) {
  const url = `${SITE_URL}/alternatives/${c.slug}`;
  const faqPage = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: c.faqs.map((f) => ({
      "@type": "Question",
      name: f.q,
      acceptedAnswer: { "@type": "Answer", text: f.a },
    })),
  };
  const breadcrumb = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
      {
        "@type": "ListItem",
        position: 2,
        name: "Alternatives",
        item: `${SITE_URL}/alternatives`,
      },
      {
        "@type": "ListItem",
        position: 3,
        name: `${c.name} alternative`,
        item: url,
      },
    ],
  };
  return [faqPage, breadcrumb];
}

function CapCell({ value }: { value: Cap }) {
  if (value === true)
    return (
      <span className="inline-flex items-center gap-1.5 text-foreground">
        <Check className="size-4 text-primary" /> Yes
      </span>
    );
  if (value === "varies")
    return <span className="text-muted-foreground">Varies</span>;
  return (
    <span className="inline-flex items-center gap-1.5 text-muted-foreground">
      <X className="size-4" /> No
    </span>
  );
}

export default async function AlternativePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const c = getCompetitor(slug);
  if (!c) notFound();

  const year = new Date().getFullYear();
  const scripts = jsonLd(c);
  const others = COMPETITOR_LIST.filter((x) => x.slug !== c.slug);

  const rows: { label: string; captapi: React.ReactNode; them: React.ReactNode }[] = [
    {
      label: "Platforms",
      captapi: CAPTAPI.platforms,
      them: c.platforms,
    },
    { label: "Transcripts", captapi: <CapCell value={CAPTAPI.transcripts} />, them: <CapCell value={c.transcripts} /> },
    { label: "AI summaries", captapi: <CapCell value={CAPTAPI.summaries} />, them: <CapCell value={c.summaries} /> },
    { label: "Comments & engagement", captapi: <CapCell value={CAPTAPI.comments} />, them: <CapCell value={c.comments} /> },
    { label: "Free tools (no signup)", captapi: <CapCell value={CAPTAPI.freeTools} />, them: <CapCell value={c.freeTools} /> },
    { label: "Free to start", captapi: CAPTAPI.freeTier, them: c.freeTier },
    { label: "Pricing", captapi: CAPTAPI.pricing, them: c.pricing },
  ];

  return (
    <div className="py-12">
      {scripts.map((s, i) => (
        <script
          key={i}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(s) }}
        />
      ))}

      <div className="container max-w-5xl">
        {/* Breadcrumb */}
        <nav
          aria-label="Breadcrumb"
          className="mb-6 flex items-center gap-2 text-sm text-muted-foreground"
        >
          <Link href="/" className="hover:text-foreground">Home</Link>
          <span>/</span>
          <Link href="/alternatives" className="hover:text-foreground">Alternatives</Link>
          <span>/</span>
          <span className="text-foreground">{c.name}</span>
        </nav>

        {/* Hero */}
        <Badge variant="secondary">{c.name} alternative</Badge>
        <h1 className="mt-3 text-4xl font-bold tracking-tight">
          The best {c.name} alternative for video data ({year})
        </h1>
        <p className="mt-4 max-w-3xl text-lg text-muted-foreground">{c.intro}</p>
        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <Button asChild size="lg">
            <Link href="/signup">Start free — 100 credits</Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href="/apis">Explore the APIs</Link>
          </Button>
        </div>

        {/* Answer-first */}
        <section className="mt-14">
          <h2 className="text-2xl font-semibold">
            Is Captapi a good {c.name} alternative?
          </h2>
          <p className="mt-3 max-w-3xl leading-relaxed text-muted-foreground">
            Yes. Captapi is a single REST API for transcripts, AI summaries,
            comments and engagement metrics across YouTube, TikTok, Instagram
            and Facebook. Where {c.name} focuses on {c.focus.toLowerCase()},
            Captapi gives you broader video-content coverage with clean JSON,
            response caching, free public tools, and 100 free credits to start —
            no credit card required.
          </p>
        </section>

        {/* Comparison table */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold">
            Captapi vs {c.name}
          </h2>
          <div className="mt-4 overflow-hidden rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 text-left">
                <tr>
                  <th className="px-4 py-3 font-medium"> </th>
                  <th className="px-4 py-3 font-medium text-foreground">Captapi</th>
                  <th className="px-4 py-3 font-medium">{c.name}</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.label} className="border-t align-top">
                    <td className="px-4 py-3 font-medium">{r.label}</td>
                    <td className="px-4 py-3">{r.captapi}</td>
                    <td className="px-4 py-3 text-muted-foreground">{r.them}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            Comparison based on publicly available information as of{" "}
            {COMPARE_AS_OF}. Features and pricing may change — please verify on{" "}
            <span className="font-mono">{c.domain}</span>.
          </p>
        </section>

        {/* Why switch */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold">Why developers pick Captapi</h2>
          <ul className="mt-4 grid gap-3 sm:grid-cols-2">
            {c.edge.map((e) => (
              <li key={e} className="flex items-start gap-2.5 text-sm">
                <Check className="mt-0.5 size-4 shrink-0 text-primary" />
                <span>{e}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* FAQ */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold">Frequently asked questions</h2>
          <div className="mt-4 space-y-3">
            {c.faqs.map((f) => (
              <details
                key={f.q}
                className="group rounded-lg border bg-card p-5 [&_summary::-webkit-details-marker]:hidden"
              >
                <summary className="flex cursor-pointer list-none items-center justify-between font-medium">
                  <span>{f.q}</span>
                  <span className="ml-4 text-xl leading-none text-muted-foreground transition-transform group-open:rotate-45">
                    +
                  </span>
                </summary>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                  {f.a}
                </p>
              </details>
            ))}
          </div>
        </section>

        {/* Other alternatives */}
        {others.length > 0 && (
          <section className="mt-12">
            <h2 className="text-2xl font-semibold">Compare other tools</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {others.map((o) => (
                <Link
                  key={o.slug}
                  href={`/alternatives/${o.slug}`}
                  className="flex items-center justify-between rounded-lg border bg-card px-4 py-3 text-sm transition-colors hover:border-primary"
                >
                  <span>{o.name} alternative</span>
                  <ArrowRight className="size-4 text-muted-foreground" />
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* CTA */}
        <section className="mt-14 rounded-xl border bg-muted/30 p-8 text-center">
          <h2 className="text-2xl font-bold">Try Captapi free</h2>
          <p className="mt-2 text-muted-foreground">
            Get your API key and 100 free credits in 60 seconds. No credit card.
          </p>
          <div className="mt-6">
            <Button asChild size="lg">
              <Link href="/signup">Get started free</Link>
            </Button>
          </div>
        </section>
      </div>
    </div>
  );
}
