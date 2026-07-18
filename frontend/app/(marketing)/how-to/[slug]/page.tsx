import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowRight, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CodeTabs } from "@/components/docs/code-tabs";
import { Tldr } from "@/components/marketing/tldr";
import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd, CONTENT_UPDATED, absoluteUrl } from "@/lib/seo";
import {
  ALL_ENDPOINTS,
  getEndpoint,
  howToTitle,
  howToAction,
  tagline,
  longDescription,
  platformLabel,
  params,
  faqs,
  codeSamples,
  exampleResponse,
  creditLabel,
  type ApiEndpoint,
} from "@/lib/api-catalog";

export function generateStaticParams() {
  return ALL_ENDPOINTS.map((ep) => ({ slug: ep.slug }));
}

export async function generateMetadata({
  params: routeParams,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await routeParams;
  const ep = getEndpoint(slug);
  if (!ep) return {};
  const title = howToTitle(ep);
  return buildMetadata({
    title: `${title} (${new Date(CONTENT_UPDATED).getFullYear()}) | Captapi`,
    description: `Step-by-step guide to ${howToAction(ep)} with a single REST API call. ${tagline(ep)}`,
    path: `/how-to/${ep.slug}`,
    ogType: "article",
    keywords: [
      howToTitle(ep),
      `${platformLabel(ep.platform)} API`,
      `${platformLabel(ep.platform)} ${ep.shortName} API`,
    ],
  });
}

function steps(ep: ApiEndpoint) {
  return [
    {
      name: "Get a free API key",
      text: "Create a free Captapi account (100 credits, no card) and generate an API key from the dashboard.",
    },
    {
      name: `Call the ${ep.name}`,
      text: `Send an authenticated ${ep.method} request to ${ep.path} with your input. No OAuth, no scraping setup.`,
    },
    {
      name: "Read the JSON response",
      text: "Parse the clean JSON response. Pass cache=true for a free 24h cache hit; default is always fresh.",
    },
  ];
}

export default async function HowToPage({
  params: routeParams,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await routeParams;
  const ep = getEndpoint(slug);
  if (!ep) notFound();

  const title = howToTitle(ep);
  const epSteps = steps(ep);
  const epFaqs = faqs(ep);
  const epParams = params(ep);

  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "How-to guides", path: "/how-to" },
      { name: title, path: `/how-to/${ep.slug}` },
    ]),
    {
      "@context": "https://schema.org",
      "@type": "HowTo",
      name: title,
      description: `${tagline(ep)}`,
      datePublished: CONTENT_UPDATED,
      dateModified: CONTENT_UPDATED,
      totalTime: "PT2M",
      estimatedCost: { "@type": "MonetaryAmount", currency: "USD", value: "0" },
      step: epSteps.map((s, i) => ({
        "@type": "HowToStep",
        position: i + 1,
        name: s.name,
        text: s.text,
        url: `${absoluteUrl(`/how-to/${ep.slug}`)}#step-${i + 1}`,
      })),
    },
    ...(epFaqs.length > 0 ? [faqLd(epFaqs)] : []),
  ];

  return (
    <div className="py-12">
      <JsonLd data={jsonLd} />

      <div className="container max-w-4xl">
        {/* Breadcrumb */}
        <nav
          aria-label="Breadcrumb"
          className="mb-6 flex items-center gap-2 text-sm text-muted-foreground"
        >
          <Link href="/" className="hover:text-foreground">Home</Link>
          <span>/</span>
          <Link href="/how-to" className="hover:text-foreground">How-to</Link>
          <span>/</span>
          <span className="text-foreground">{ep.name}</span>
        </nav>

        <Badge variant="secondary">{platformLabel(ep.platform)} · Guide</Badge>
        <h1 className="mt-3 text-4xl font-bold tracking-tight">{title}</h1>

        <Tldr>
          To {howToAction(ep)}, sign up for a free Captapi key, then send one{" "}
          <code>{ep.method}</code> request to <code>{ep.path}</code> with your
          input. You get clean JSON back in seconds for {creditLabel(ep)} per
          call — no OAuth, scraping or platform SDKs. {tagline(ep)}
        </Tldr>

        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <Button asChild size="lg">
            <Link href="/signup">Get your free API key</Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href={`/apis/${ep.slug}`}>
              API reference <ArrowRight className="ml-1 size-4" />
            </Link>
          </Button>
        </div>

        {/* Steps */}
        <section className="mt-14">
          <h2 className="text-2xl font-semibold">
            How to {howToAction(ep)} (step by step)
          </h2>
          <ol className="mt-5 space-y-4">
            {epSteps.map((s, i) => (
              <li key={s.name} id={`step-${i + 1}`} className="flex gap-4">
                <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                  {i + 1}
                </span>
                <div>
                  <h3 className="font-semibold">{s.name}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{s.text}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        {/* Code */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold mb-4">Code example</h2>
          <CodeTabs samples={codeSamples(ep)} />
        </section>

        {/* Response */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold mb-4">What the response looks like</h2>
          <CodeTabs samples={[{ label: "200 OK", code: exampleResponse(ep) }]} />
          <p className="mt-3 text-sm text-muted-foreground">
            Billing metadata (credits charged, cache hit/miss) is returned in
            the <code className="text-xs">X-Captapi-Credits</code> and{" "}
            <code className="text-xs">X-Captapi-Cache</code> response headers.
          </p>
        </section>

        {/* Parameters */}
        {epParams.length > 0 && (
          <section className="mt-12">
            <h2 className="text-2xl font-semibold">Request parameters</h2>
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
                      <td className="px-4 py-2.5 text-muted-foreground">{p.type}</td>
                      <td className="px-4 py-2.5">
                        {p.required ? (
                          <span className="inline-flex items-center gap-1 text-foreground">
                            <Check className="size-3.5 text-primary" /> Yes
                          </span>
                        ) : (
                          <span className="text-muted-foreground">No</span>
                        )}
                      </td>
                      <td className="px-4 py-2.5 text-muted-foreground">{p.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* FAQ */}
        {epFaqs.length > 0 && (
          <section className="mt-12">
            <h2 className="text-2xl font-semibold">Frequently asked questions</h2>
            <div className="mt-4 space-y-3">
              {epFaqs.map((f) => (
                <details key={f.q} className="rounded-lg border p-4">
                  <summary className="cursor-pointer font-medium">{f.q}</summary>
                  <p className="mt-2 text-sm text-muted-foreground">{f.a}</p>
                </details>
              ))}
            </div>
          </section>
        )}

        {/* CTA */}
        <section className="mt-14 rounded-xl border bg-muted/30 p-6 text-center">
          <h2 className="text-xl font-semibold">Ready to {howToAction(ep)}?</h2>
          <p className="mx-auto mt-2 max-w-xl text-sm text-muted-foreground">
            Start free with 100 credits — no credit card required.
          </p>
          <Button asChild size="lg" className="mt-4">
            <Link href="/signup">Get your free API key</Link>
          </Button>
        </section>
      </div>
    </div>
  );
}
