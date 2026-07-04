import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  Youtube,
  AtSign,
  Cloud,
  Music2,
  Instagram,
  Facebook,
  Github,
  Linkedin,
  Megaphone,
  MessagesSquare,
  Pin,
  ShoppingBag,
  Twitter,
  Video,
  Search,
  LinkIcon,
  Ghost,
  Check,
  Coins,
  type LucideIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  ALL_ENDPOINTS,
  PLATFORM_PAGES,
  getEndpoint,
  getGroup,
  getPlatformBySlug,
  platformSlug,
  relatedEndpoints,
  platformLabel,
  tagline,
  longDescription,
  delivers,
  params,
  faqs,
  exampleResponse,
  errorExamples,
  responseStructure,
  useCases,
  creditLabel,
  mcpToolName,
  SITE_URL,
  type ApiEndpoint,
} from "@/lib/api-catalog";
import { CodeTabs } from "@/components/docs/code-tabs";
import { ApiPlayground } from "@/components/docs/api-playground";
import { PlatformLanding } from "@/components/marketing/platform-landing";
import { Tldr } from "@/components/marketing/tldr";
import { CONTENT_UPDATED } from "@/lib/seo";

const PLATFORM_ICONS: Record<string, LucideIcon> = {
  youtube: Youtube,
  music: Music2,
  instagram: Instagram,
  facebook: Facebook,
  twitter: Twitter,
  reddit: MessagesSquare,
  threads: AtSign,
  bluesky: Cloud,
  pinterest: Pin,
  linkedin: Linkedin,
  rumble: Video,
  github: Github,
  megaphone: Megaphone,
  shoppingBag: ShoppingBag,
  video: Video,
  cloud: Cloud,
  search: Search,
  link: LinkIcon,
  ghost: Ghost,
};

export function generateStaticParams() {
  return [
    ...PLATFORM_PAGES.map((g) => ({ slug: platformSlug(g.id) })),
    ...ALL_ENDPOINTS.map((ep) => ({ slug: ep.slug })),
  ];
}

export async function generateMetadata({
  params: routeParams,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await routeParams;

  const group = getPlatformBySlug(slug);
  if (group) {
    const title = `${group.name} API — Real-time ${group.name} Data via REST`;
    const description = `${group.blurb} ${group.endpoints.length} endpoints, one Bearer key, clean JSON — no OAuth and no scrapers to maintain. Start free with 100 credits.`;
    const url = `${SITE_URL}/apis/${slug}`;
    return {
      title: `${title} | Captapi`,
      description,
      keywords: [
        `${group.name} API`,
        `${group.name} data API`,
        `${group.name} scraper API`,
        `scrape ${group.name}`,
        "social media API",
      ],
      alternates: { canonical: url },
      openGraph: { title, description, url, type: "website" },
      twitter: { card: "summary_large_image", title, description },
    };
  }

  const ep = getEndpoint(slug);
  if (!ep) return {};
  const title = `${ep.name} — ${platformLabel(ep.platform)} Data via REST`;
  const description = `${tagline(ep)} No OAuth and no scraping — send a URL and get clean, structured JSON back, with results cached for 24 hours.`;
  const url = `${SITE_URL}/apis/${ep.slug}`;
  return {
    title: `${ep.name} | Captapi`,
    description,
    keywords: [
      ep.name,
      `${platformLabel(ep.platform)} ${ep.shortName} API`,
      `${platformLabel(ep.platform)} API`,
      `${platformLabel(ep.platform)} ${ep.category} API`,
      "social media API",
    ],
    alternates: { canonical: url },
    openGraph: { title, description, url, type: "article" },
    twitter: { card: "summary_large_image", title, description },
  };
}

function jsonLd(ep: ApiEndpoint) {
  const url = `${SITE_URL}/apis/${ep.slug}`;
  const faqList = faqs(ep);

  const faqPage = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqList.map((f) => ({
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
      { "@type": "ListItem", position: 2, name: "APIs", item: `${SITE_URL}/apis` },
      { "@type": "ListItem", position: 3, name: ep.name, item: url },
    ],
  };

  const webApi = {
    "@context": "https://schema.org",
    "@type": "WebAPI",
    name: ep.name,
    description: longDescription(ep),
    url,
    documentation: `${SITE_URL}/docs`,
    provider: { "@type": "Organization", name: "Captapi", url: SITE_URL },
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
      description: "100 free credits on signup, then credit-based pricing.",
    },
  };

  const techArticle = {
    "@context": "https://schema.org",
    "@type": "TechArticle",
    headline: `${ep.name} — ${platformLabel(ep.platform)} API`,
    description: longDescription(ep),
    datePublished: CONTENT_UPDATED,
    dateModified: CONTENT_UPDATED,
    author: { "@type": "Organization", name: "Captapi", url: SITE_URL },
    publisher: {
      "@type": "Organization",
      name: "Captapi",
      logo: { "@type": "ImageObject", url: `${SITE_URL}/logo.png` },
    },
    mainEntityOfPage: { "@type": "WebPage", "@id": url },
    proficiencyLevel: "Beginner",
  };

  return [faqPage, breadcrumb, webApi, techArticle];
}

export default async function ApiDetailPage({
  params: routeParams,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await routeParams;

  const platformGroup = getPlatformBySlug(slug);
  if (platformGroup) return <PlatformLanding group={platformGroup} />;

  const ep = getEndpoint(slug);
  if (!ep) notFound();

  const group = getGroup(ep.platform);
  const Icon = PLATFORM_ICONS[group.icon];
  const epParams = params(ep);
  const epFaqs = faqs(ep);
  const epResponse = responseStructure(ep);
  const epUseCases = useCases(ep);
  const related = relatedEndpoints(ep.slug);
  const scripts = jsonLd(ep);

  return (
    <div className="py-12">
      {scripts.map((s, i) => (
        <script
          key={i}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(s) }}
        />
      ))}

      <div className="container max-w-6xl">
        {/* Breadcrumb */}
        <nav
          aria-label="Breadcrumb"
          className="mb-6 flex items-center gap-2 text-sm text-muted-foreground"
        >
          <Link href="/" className="hover:text-foreground">
            Home
          </Link>
          <span>/</span>
          <Link href="/apis" className="hover:text-foreground">
            APIs
          </Link>
          <span>/</span>
          <span className="text-foreground">{ep.name}</span>
        </nav>

        {/* Hero */}
        <div className="flex items-center gap-2 mb-3">
          <Badge variant="secondary" className="gap-1.5">
            <Icon className={`size-3.5 ${group.color}`} />
            {platformLabel(ep.platform)}
          </Badge>
          <Badge variant="outline">
            {ep.method} {ep.path}
          </Badge>
        </div>
        <h1 className="text-4xl font-bold tracking-tight">{ep.name}</h1>
        <p className="mt-4 max-w-3xl text-lg text-muted-foreground">
          {tagline(ep)}
        </p>
        <div className="mt-4 inline-flex items-center gap-1.5 rounded-full border border-amber-500/40 bg-amber-500/10 px-3.5 py-1.5 text-sm font-medium text-amber-600 dark:text-amber-400">
          <Coins className="size-4" />
          {ep.creditsPerResult
            ? `${creditLabel(ep)} per request (${ep.creditsPerResult} per result)`
            : `${creditLabel(ep)} per request`}
        </div>
        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <Button asChild size="lg">
            <Link href="/signup">Get your API key — free</Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href="/docs">Read the docs</Link>
          </Button>
        </div>

        {/* Answer-first overview (AEO) */}
        <section className="mt-14">
          <Tldr>
            The <strong>{ep.name}</strong> ({platformLabel(ep.platform)}) returns{" "}
            {tagline(ep).charAt(0).toLowerCase() + tagline(ep).slice(1)} It&apos;s a
            single authenticated <code>{ep.method ?? "GET"}</code> request to{" "}
            <code>{ep.path}</code> that responds with clean JSON, costs{" "}
            {creditLabel(ep)}, and is cached for 24 hours (repeat calls are free).
            Start with 100 free credits — no credit card.
          </Tldr>
          <h2 className="text-2xl font-semibold">
            What is the {ep.name}?
          </h2>
          <p className="mt-3 max-w-3xl leading-relaxed text-muted-foreground">
            {longDescription(ep)}
          </p>
        </section>

        {/* What you get */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold">What you get</h2>
          <ul className="mt-4 grid gap-3 sm:grid-cols-2">
            {delivers(ep).map((d) => (
              <li key={d} className="flex items-start gap-2.5 text-sm">
                <Check className="mt-0.5 size-4 shrink-0 text-primary" />
                <span>{d}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* Interactive request builder */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold">Try it</h2>
          <p className="mt-2 mb-4 max-w-3xl text-sm text-muted-foreground">
            Fill in the parameters below and copy a ready-to-run request in your
            language of choice.
          </p>
          <ApiPlayground ep={ep} />
        </section>

        {/* Response */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold mb-4">Example response</h2>
          <CodeTabs
            samples={[
              { label: "200 OK", code: exampleResponse(ep), lang: "json" },
              ...errorExamples(ep).map((e) => ({
                label: e.label,
                code: e.code,
                lang: "json",
              })),
            ]}
          />
          <p className="mt-3 text-sm text-muted-foreground">
            Failed requests (4xx/5xx) are never charged. See the full list of
            error codes in the{" "}
            <Link href="/docs#errors" className="text-primary hover:underline">
              error reference
            </Link>
            .
          </p>
        </section>

        {/* Response structure */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold">Response structure</h2>
          <p className="mt-3 max-w-3xl text-sm text-muted-foreground">
            A successful call returns{" "}
            <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
              success
            </code>
            , <code className="rounded bg-muted px-1.5 py-0.5 text-xs">cached</code>,{" "}
            <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
              creditsUsed
            </code>
            , and a{" "}
            <code className="rounded bg-muted px-1.5 py-0.5 text-xs">data</code>{" "}
            object with the following fields:
          </p>
          <div className="mt-5 grid gap-6 sm:grid-cols-2">
            {epResponse.map((group) => (
              <div key={group.title}>
                <h3 className="text-base font-semibold">{group.title}</h3>
                {group.note && (
                  <p className="mt-1 text-sm text-muted-foreground">
                    {group.note}
                  </p>
                )}
                <ul className="mt-3 space-y-2.5 text-sm">
                  {group.fields.map((f) => (
                    <li key={f.name}>
                      <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs text-foreground">
                        {f.name}
                      </code>
                      <span className="ml-2 text-muted-foreground">
                        {f.desc}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* Parameters */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold">Parameters</h2>
          <div className="mt-4 overflow-hidden rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 text-left">
                <tr>
                  <th className="px-4 py-2.5 font-medium">Name</th>
                  <th className="px-4 py-2.5 font-medium">Type</th>
                  <th className="px-4 py-2.5 font-medium">Required</th>
                  <th className="px-4 py-2.5 font-medium">Description</th>
                </tr>
              </thead>
              <tbody>
                {epParams.map((p) => (
                  <tr key={p.name} className="border-t">
                    <td className="px-4 py-2.5 font-mono text-xs">{p.name}</td>
                    <td className="px-4 py-2.5 text-muted-foreground">
                      {p.type}
                    </td>
                    <td className="px-4 py-2.5 text-muted-foreground">
                      {p.required ? "Yes" : "No"}
                    </td>
                    <td className="px-4 py-2.5 text-muted-foreground">
                      {p.description}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-sm text-muted-foreground">
            Authentication: send your key as{" "}
            <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
              Authorization: Bearer capt_live_...
            </code>
            . A typical call costs{" "}
            <strong className="text-foreground">{creditLabel(ep)}</strong>
            {ep.creditsPerResult
              ? " — billed per result, so the exact amount scales with how many items you request"
              : ""}
            .             Repeat calls for the same request are served from cache for free
            {ep.creditsPerResult ? " (metrics refresh within ~1 hour)" : ""}.
          </p>
          <div className="mt-4 rounded-lg border bg-muted/30 px-4 py-3 text-sm">
            <span className="text-muted-foreground">Using an AI agent? This endpoint is the MCP tool </span>
            <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs text-foreground">
              {mcpToolName(ep)}
            </code>
            <span className="text-muted-foreground">
              {" "}via{" "}
              <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">@captapi/mcp</code>.{" "}
            </span>
            <Link href="/docs/integrations" className="text-primary hover:underline">
              Set it up →
            </Link>
          </div>
        </section>

        {/* How it works */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold">How it works</h2>
          <ol className="mt-4 space-y-3 text-sm text-muted-foreground">
            <li>
              <strong className="text-foreground">1. Sign up</strong> — get 100
              free credits, no card required.
            </li>
            <li>
              <strong className="text-foreground">2. Create a key</strong> from
              your dashboard.
            </li>
            <li>
              <strong className="text-foreground">3. Send one request</strong>{" "}
              to <code className="rounded bg-muted px-1.5 py-0.5 text-xs">{ep.path}</code>{" "}
              and parse the JSON response.
            </li>
          </ol>
        </section>

        {/* Use cases */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold">Use cases</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {epUseCases.map((u) => (
              <div
                key={u.title}
                className="rounded-lg border bg-card p-4"
              >
                <h3 className="text-sm font-semibold">{u.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{u.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold">Frequently asked questions</h2>
          <div className="mt-4 space-y-3">
            {epFaqs.map((f) => (
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

        {/* Related */}
        {related.length > 0 && (
          <section className="mt-12">
            <h2 className="text-2xl font-semibold">
              More {platformLabel(ep.platform)} APIs
            </h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {related.map((r) => (
                <Link
                  key={r.slug}
                  href={`/apis/${r.slug}`}
                  className="rounded-lg border bg-card px-4 py-3 text-sm transition-colors hover:border-primary"
                >
                  {r.name}
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* CTA */}
        <section className="mt-14 rounded-xl border bg-muted/30 p-8 text-center">
          <h2 className="text-2xl font-bold">
            Ready to use the {ep.name}?
          </h2>
          <p className="mt-2 text-muted-foreground">
            Sign up, grab your key, and make your first call in 60 seconds.
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
