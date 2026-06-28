import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Check, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  SITE_URL,
  ENDPOINT_COUNT,
  PLATFORM_COUNT,
  getEndpoint,
} from "@/lib/api-catalog";
import {
  USE_CASE_LIST,
  USE_CASE_SLUGS,
  getUseCase,
  type UseCase,
} from "@/lib/use-cases";

export function generateStaticParams() {
  return USE_CASE_SLUGS.map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const uc = getUseCase(slug);
  if (!uc) return {};
  const url = `${SITE_URL}/for/${uc.slug}`;
  return {
    title: uc.metaTitle,
    description: uc.metaDescription,
    keywords: [uc.keyword, `${uc.audience} API`, "social media API", "video transcript API"],
    alternates: { canonical: url },
    openGraph: { title: uc.metaTitle, description: uc.metaDescription, url, type: "article" },
    twitter: { card: "summary_large_image", title: uc.metaTitle, description: uc.metaDescription },
  };
}

function jsonLd(uc: UseCase) {
  const url = `${SITE_URL}/for/${uc.slug}`;
  const faqPage = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: uc.faqs.map((f) => ({
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
      { "@type": "ListItem", position: 2, name: "Use Cases", item: `${SITE_URL}/for` },
      { "@type": "ListItem", position: 3, name: uc.audience, item: url },
    ],
  };
  return [faqPage, breadcrumb];
}

export default async function UseCasePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const uc = getUseCase(slug);
  if (!uc) notFound();

  const scripts = jsonLd(uc);
  const related = uc.apiSlugs.map((s) => getEndpoint(s)).filter(Boolean);
  const others = USE_CASE_LIST.filter((x) => x.slug !== uc.slug);

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
        <nav
          aria-label="Breadcrumb"
          className="mb-6 flex items-center gap-2 text-sm text-muted-foreground"
        >
          <Link href="/" className="hover:text-foreground">Home</Link>
          <span>/</span>
          <Link href="/for" className="hover:text-foreground">Use Cases</Link>
          <span>/</span>
          <span className="text-foreground">{uc.audience}</span>
        </nav>

        <Badge variant="secondary">For {uc.audience}</Badge>
        <h1 className="mt-3 text-4xl font-bold tracking-tight">{uc.h1}</h1>
        <p className="mt-4 max-w-3xl text-lg text-muted-foreground">{uc.intro}</p>
        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <Button asChild size="lg">
            <Link href="/signup">Start free — 100 credits</Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href="/apis">Explore the APIs</Link>
          </Button>
        </div>

        {/* What you can build */}
        <section className="mt-14">
          <h2 className="text-2xl font-semibold">What you can build</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {uc.builds.map((b) => (
              <div key={b.title} className="rounded-lg border bg-card p-5">
                <h3 className="text-base font-semibold">{b.title}</h3>
                <p className="mt-1.5 text-sm text-muted-foreground">{b.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Related APIs */}
        {related.length > 0 && (
          <section className="mt-12">
            <h2 className="text-2xl font-semibold">APIs you&apos;ll use</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {related.map((ep) => (
                <Link
                  key={ep!.slug}
                  href={`/apis/${ep!.slug}`}
                  className="flex items-center justify-between rounded-lg border bg-card px-4 py-3 text-sm transition-colors hover:border-primary"
                >
                  <span>{ep!.name}</span>
                  <ArrowRight className="size-4 text-muted-foreground" />
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Why Captapi */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold">Why {uc.audience} choose Captapi</h2>
          <ul className="mt-4 grid gap-3 sm:grid-cols-2">
            {[
              `One REST API for ${PLATFORM_COUNT} platforms and ${ENDPOINT_COUNT} endpoints`,
              "Clean JSON — no scraping, no OAuth, no quotas",
              "Transcripts, AI summaries, comments, search, ads, commerce & engagement",
              "100 free credits to start, no credit card",
            ].map((e) => (
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
            {uc.faqs.map((f) => (
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

        {/* Other use cases */}
        {others.length > 0 && (
          <section className="mt-12">
            <h2 className="text-2xl font-semibold">Other use cases</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {others.map((o) => (
                <Link
                  key={o.slug}
                  href={`/for/${o.slug}`}
                  className="flex items-center justify-between rounded-lg border bg-card px-4 py-3 text-sm transition-colors hover:border-primary"
                >
                  <span>For {o.audience}</span>
                  <ArrowRight className="size-4 text-muted-foreground" />
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* CTA */}
        <section className="mt-14 rounded-xl border bg-muted/30 p-8 text-center">
          <h2 className="text-2xl font-bold">Build it with Captapi</h2>
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
