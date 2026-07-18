import Link from "next/link";
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
  type LucideIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CodeTabs } from "@/components/docs/code-tabs";
import {
  API_URL,
  SITE_URL,
  PLATFORM_PAGES,
  platformSlug,
  platformFaqs,
  tagline,
  params,
  creditLabel,
  type PlatformGroup,
  type ApiEndpoint,
} from "@/lib/api-catalog";
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

/** Pick a representative endpoint (prefer a URL-input one) for hero examples. */
function heroEndpoint(group: PlatformGroup): ApiEndpoint {
  return (
    group.endpoints.find((ep) =>
      params(ep).some((p) => p.name === "url" && p.required),
    ) ?? group.endpoints[0]
  );
}

function exampleValue(group: PlatformGroup, name: string): string {
  switch (name) {
    case "url":
      return group.exampleUrl;
    case "q":
    case "query":
      return "nasa";
    case "username":
    case "handle":
      return "nasa";
    case "limit":
      return "20";
    default:
      return "...";
  }
}

function heroSamples(group: PlatformGroup) {
  const ep = heroEndpoint(group);
  const required = params(ep).filter((p) => p.required);
  const qs = required
    .map((p) => `${p.name}=${encodeURIComponent(exampleValue(group, p.name))}`)
    .join("&");
  const url = `${API_URL}${ep.path}${qs ? `?${qs}` : ""}`;

  return [
    {
      label: "cURL",
      code: `curl "${url}" \\\n  -H "Authorization: Bearer capt_live_..."`,
    },
    {
      label: "JavaScript",
      code: `const response = await fetch(\n  "${url}",\n  { headers: { Authorization: "Bearer capt_live_..." } },\n);\n\nconst data = await response.json();\nconsole.log(data);`,
    },
    {
      label: "Python",
      code: `import requests\n\nresponse = requests.get(\n    "${url}",\n    headers={"Authorization": "Bearer capt_live_..."},\n)\n\nprint(response.json())`,
    },
  ];
}

function jsonLd(group: PlatformGroup) {
  const url = `${SITE_URL}/apis/${platformSlug(group.id)}`;

  const breadcrumb = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
      { "@type": "ListItem", position: 2, name: "APIs", item: `${SITE_URL}/apis` },
      { "@type": "ListItem", position: 3, name: `${group.name} API`, item: url },
    ],
  };

  const itemList = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: `${group.name} API endpoints`,
    description: group.blurb,
    numberOfItems: group.endpoints.length,
    itemListElement: group.endpoints.map((ep, i) => ({
      "@type": "ListItem",
      position: i + 1,
      url: `${SITE_URL}/apis/${ep.slug}`,
      name: ep.name,
    })),
  };

  const webApi = {
    "@context": "https://schema.org",
    "@type": "WebAPI",
    name: `${group.name} API`,
    description: group.blurb,
    url,
    documentation: `${SITE_URL}/docs`,
    dateModified: CONTENT_UPDATED,
    provider: { "@type": "Organization", name: "Captapi", url: SITE_URL },
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
      description: "100 free credits on signup, then credit-based pricing.",
    },
  };

  const faqPage = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: platformFaqs(group).map((f) => ({
      "@type": "Question",
      name: f.q,
      acceptedAnswer: { "@type": "Answer", text: f.a },
    })),
  };

  const techArticle = {
    "@context": "https://schema.org",
    "@type": "TechArticle",
    headline: `${group.name} API — real-time ${group.name} data via REST`,
    description: group.blurb,
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

  return [breadcrumb, itemList, webApi, faqPage, techArticle];
}

export function PlatformLanding({ group }: { group: PlatformGroup }) {
  const Icon = PLATFORM_ICONS[group.icon] ?? Search;
  const scripts = jsonLd(group);
  const others = PLATFORM_PAGES.filter((g) => g.id !== group.id);

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
          <Link href="/" className="hover:text-foreground">Home</Link>
          <span>/</span>
          <Link href="/apis" className="hover:text-foreground">APIs</Link>
          <span>/</span>
          <span className="text-foreground">{group.name} API</span>
        </nav>

        {/* Hero */}
        <div className="grid items-start gap-10 lg:grid-cols-2">
          <div>
            <Badge variant="secondary" className="gap-1.5">
              <Icon className={`size-3.5 ${group.color}`} />
              {group.name} API
            </Badge>
            <h1 className="mt-4 text-4xl font-bold tracking-tight md:text-5xl">
              Real-time {group.name}{" "}
              <span className="text-muted-foreground">data, one API call.</span>
            </h1>
            <p className="mt-4 max-w-xl text-lg text-muted-foreground">
              {group.blurb}
            </p>
            <p className="mt-3 max-w-xl text-sm text-muted-foreground">
              The {group.name} API from Captapi gives developers reliable access
              to public {group.name} data without building or maintaining
              scrapers — send one authenticated request and get clean,
              structured JSON back.
            </p>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg">
                <Link href="/signup">Start free — 100 credits</Link>
              </Button>
              <Button asChild size="lg" variant="outline">
                <Link href="/docs">View documentation →</Link>
              </Button>
            </div>

            {/* Stats */}
            <div className="mt-10 grid max-w-md grid-cols-3 gap-6 border-t pt-6">
              <div>
                <div className="text-2xl font-bold">{group.endpoints.length}</div>
                <div className="mt-1 text-xs uppercase tracking-wider text-muted-foreground">
                  Endpoints
                </div>
              </div>
              <div>
                <div className="text-2xl font-bold">REST</div>
                <div className="mt-1 text-xs uppercase tracking-wider text-muted-foreground">
                  Protocol
                </div>
              </div>
              <div>
                <div className="text-2xl font-bold">JSON</div>
                <div className="mt-1 text-xs uppercase tracking-wider text-muted-foreground">
                  Response
                </div>
              </div>
            </div>
          </div>

          <CodeTabs samples={heroSamples(group)} />
        </div>

        {/* Answer-first overview (AEO) */}
        <section className="mt-16">
          <Tldr>
            The <strong>{group.name} API</strong> returns public {group.name}{" "}
            data as clean, structured JSON — {group.endpoints.length} REST
            endpoint{group.endpoints.length === 1 ? "" : "s"} behind one Bearer
            key. No OAuth, no scrapers to maintain. Pass cache=true for a free
            24h cache hit; by default every call is fresh. Start with 100 free
            credits — no credit card.
          </Tldr>
          <h2 className="text-2xl font-semibold">
            What is the {group.name} API?
          </h2>
          <p className="mt-3 max-w-3xl leading-relaxed text-muted-foreground">
            {group.blurb} Every endpoint is a single authenticated GET request
            that responds with predictable JSON, so the data drops straight
            into dashboards, AI pipelines, RAG systems, and no-code automations.
            AI agents can call the same endpoints as MCP tools via{" "}
            <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
              @captapi/mcp
            </code>
            .
          </p>
        </section>

        {/* Endpoint grid */}
        <section className="mt-16">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary">
            Endpoints
          </p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight">
            What you can do with the {group.name} API
          </h2>
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {group.endpoints.map((ep) => (
              <Link
                key={ep.slug}
                href={`/apis/${ep.slug}`}
                className="group rounded-xl border bg-card p-5 transition-colors hover:border-primary"
              >
                <h3 className="flex items-center gap-2 text-sm font-semibold">
                  <span className="size-1.5 rounded-full bg-primary" />
                  {ep.shortName}
                </h3>
                <p className="mt-2 font-mono text-[11px] text-muted-foreground">
                  {ep.method}{" "}
                  <span className="text-foreground/70">{ep.path}</span>
                </p>
                <p className="mt-2.5 text-sm leading-relaxed text-muted-foreground">
                  {tagline(ep)}
                </p>
                <p className="mt-3 text-xs text-muted-foreground">
                  {creditLabel(ep)}
                  {ep.creditsPerResult ? " · billed per result" : ""}
                </p>
              </Link>
            ))}
          </div>
        </section>

        {/* How it works */}
        <section className="mt-16">
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
              <strong className="text-foreground">3. Call any endpoint</strong>{" "}
              above with{" "}
              <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
                Authorization: Bearer capt_live_...
              </code>{" "}
              and parse the JSON response. Pass{" "}
              <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
                cache=true
              </code>{" "}
              to reuse a prior response from the 24h cache at no cost.
            </li>
          </ol>
        </section>

        {/* FAQ */}
        <section className="mt-16">
          <h2 className="text-2xl font-semibold">Frequently asked questions</h2>
          <div className="mt-4 space-y-3">
            {platformFaqs(group).map((f) => (
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

        {/* Other platforms */}
        <section className="mt-16">
          <h2 className="text-2xl font-semibold">Explore other platforms</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {others.map((g) => (
              <Link
                key={g.id}
                href={`/apis/${platformSlug(g.id)}`}
                className="rounded-full border bg-card px-3.5 py-1.5 text-sm text-muted-foreground transition-colors hover:border-primary hover:text-foreground"
              >
                {g.name} API
              </Link>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="mt-16 rounded-xl border bg-muted/30 p-8 text-center">
          <h2 className="text-2xl font-bold">
            Start using the {group.name} API in sixty seconds
          </h2>
          <p className="mt-2 text-muted-foreground">
            Sign up, grab your API key, and make your first request. 100
            credits on the house — no credit card.
          </p>
          <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
            <Button asChild size="lg">
              <Link href="/signup">Get your API key — free</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/docs">Read the docs</Link>
            </Button>
          </div>
        </section>
      </div>
    </div>
  );
}
