import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, BookOpen, Braces, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  McpIcon,
  CliIcon,
  N8nIcon,
  MakeIcon,
  ApifyIcon,
  TypeScriptIcon,
  PythonIcon,
} from "@/components/docs/integration-icons";
import { ENDPOINT_COUNT, PLATFORM_COUNT, SITE_URL, API_URL } from "@/lib/api-catalog";

const TITLE = "Integrations — MCP, SDKs, CLI, n8n, Make.com & Apify";
const DESCRIPTION = `Official Captapi integrations: hosted + local MCP server for Claude, Cursor, and VS Code, typed TypeScript & Python SDKs, a CLI, an n8n community node, a Make.com app, and an Apify Actor — all ${ENDPOINT_COUNT} endpoints across ${PLATFORM_COUNT} platforms, everywhere you build.`;

export const metadata: Metadata = {
  title: `${TITLE} | Captapi`,
  description: DESCRIPTION,
  keywords: [
    "social media API integrations",
    "MCP server",
    "Model Context Protocol",
    "TypeScript SDK",
    "Python SDK",
    "n8n social media node",
    "Make.com social media app",
    "Apify Actor",
    "social media CLI",
  ],
  alternates: { canonical: `${SITE_URL}/integrations` },
  openGraph: {
    title: TITLE,
    description: DESCRIPTION,
    url: `${SITE_URL}/integrations`,
    type: "website",
  },
  twitter: { card: "summary_large_image", title: TITLE, description: DESCRIPTION },
};

type Integration = {
  id: string;
  name: string;
  tagline: string;
  description: string;
  icon: React.ReactNode;
  docsHref: string;
  install?: string;
  external?: { label: string; href: string };
};

const INTEGRATIONS: Integration[] = [
  {
    id: "mcp",
    name: "MCP Server",
    tagline: "For Claude, Cursor, VS Code & any MCP agent",
    description: `Every endpoint as a typed tool over the Model Context Protocol. Connect hosted (just a URL, nothing to install) or run @captapi/mcp locally via npx.`,
    icon: <McpIcon className="size-6" />,
    docsHref: "/docs/integrations#mcp",
    install: `"url": "${API_URL}/mcp"`,
    external: { label: "npm: @captapi/mcp", href: "https://www.npmjs.com/package/@captapi/mcp" },
  },
  {
    id: "sdk-ts",
    name: "TypeScript SDK",
    tagline: "Typed client for Node, Deno, Bun & edge",
    description:
      "Zero-dependency client with a typed, namespaced method for every endpoint. Great autocomplete for humans and AI coding agents; errors always throw.",
    icon: <TypeScriptIcon className="size-6 rounded" />,
    docsHref: "/docs/integrations#sdk",
    install: "npm install @captapi/sdk",
    external: { label: "npm: @captapi/sdk", href: "https://www.npmjs.com/package/@captapi/sdk" },
  },
  {
    id: "sdk-py",
    name: "Python SDK",
    tagline: "Sync + async clients on httpx",
    description:
      "The same typed, namespaced methods in Python — use Captapi for scripts and AsyncCaptapi for high-concurrency pipelines. Python 3.9+.",
    icon: <PythonIcon className="size-6" />,
    docsHref: "/docs/integrations#sdk",
    install: "pip install captapi",
    external: { label: "PyPI: captapi", href: "https://pypi.org/project/captapi/" },
  },
  {
    id: "cli",
    name: "CLI",
    tagline: "Terminal, scripts, cron & CI",
    description:
      "Every endpoint as a subcommand with flags, printing clean JSON to stdout — pipe straight into jq. Can also wire the MCP server into your agent for you.",
    icon: <CliIcon className="size-6" />,
    docsHref: "/docs/integrations#cli",
    install: "npm install -g @captapi/cli",
    external: { label: "npm: @captapi/cli", href: "https://www.npmjs.com/package/@captapi/cli" },
  },
  {
    id: "n8n",
    name: "n8n",
    tagline: "Community node for n8n workflows",
    description:
      "Drop the Captapi node into any workflow, pick a platform and operation, and map the structured JSON into your downstream nodes. Installs from Community Nodes.",
    icon: <N8nIcon className="size-6" />,
    docsHref: "/docs/integrations#n8n",
    install: "n8n-nodes-captapi",
    external: {
      label: "npm: n8n-nodes-captapi",
      href: "https://www.npmjs.com/package/n8n-nodes-captapi",
    },
  },
  {
    id: "make",
    name: "Make.com",
    tagline: "No-code scenarios (Integromat)",
    description:
      "A custom app with an action module for every endpoint, grouped by platform. Add your key once as a connection and build scenarios without writing code.",
    icon: <MakeIcon className="size-6" />,
    docsHref: "/docs/integrations#make",
  },
  {
    id: "apify",
    name: "Apify Actor",
    tagline: "Bring your own key on Apify",
    description:
      "A thin wrapper around the REST API (no scraping) that returns the same structured JSON as a dataset item. Discoverable by AI agents on Apify's MCP server.",
    icon: <ApifyIcon className="size-6" />,
    docsHref: "/docs/integrations#apify",
  },
  {
    id: "rest",
    name: "REST API",
    tagline: "Plain HTTPS — works from anything",
    description: `No SDK required: one Bearer key, ${ENDPOINT_COUNT} GET endpoints, consistent JSON envelopes. OpenAPI 3 spec, llms.txt, and mcp.json manifests keep agents in sync.`,
    icon: <Braces className="size-6" />,
    docsHref: "/docs",
    install: `curl ${API_URL}/v1/...`,
  },
];

export default function IntegrationsIndexPage() {
  const itemList = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: "Captapi Integrations",
    description: DESCRIPTION,
    numberOfItems: INTEGRATIONS.length,
    itemListElement: INTEGRATIONS.map((it, i) => ({
      "@type": "ListItem",
      position: i + 1,
      url: `${SITE_URL}${it.docsHref}`,
      name: `Captapi ${it.name}`,
    })),
  };

  const breadcrumb = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
      { "@type": "ListItem", position: 2, name: "Integrations", item: `${SITE_URL}/integrations` },
    ],
  };

  return (
    <div className="py-16">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(itemList) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }}
      />
      <div className="container max-w-6xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold tracking-tight">Integrations</h1>
          <p className="mt-3 text-muted-foreground max-w-2xl mx-auto">
            All {ENDPOINT_COUNT} endpoints across {PLATFORM_COUNT} platforms,
            available wherever you build — AI agents over MCP, typed SDKs, the
            terminal, and no-code automation platforms.
          </p>
          <p className="mt-3 text-sm text-muted-foreground max-w-2xl mx-auto">
            Every integration is <strong>official and maintained</strong> — the
            same key works in all of them, and cached results stay free.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {INTEGRATIONS.map((it) => (
            <div
              key={it.id}
              className="group relative flex flex-col rounded-xl border bg-card p-5 transition-colors hover:border-primary/50"
            >
              <div className="flex items-center gap-3">
                <span className="flex size-11 shrink-0 items-center justify-center rounded-lg border bg-background">
                  {it.icon}
                </span>
                <div>
                  <h2 className="font-semibold leading-tight">
                    <Link href={it.docsHref} className="after:absolute after:inset-0">
                      {it.name}
                    </Link>
                  </h2>
                  <p className="text-xs text-muted-foreground">{it.tagline}</p>
                </div>
              </div>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                {it.description}
              </p>
              {it.install && (
                <code className="mt-3 block overflow-x-auto whitespace-nowrap rounded-md border bg-muted/40 px-3 py-2 font-mono text-xs text-muted-foreground">
                  {it.install}
                </code>
              )}
              <div className="mt-auto flex items-center justify-between pt-4 text-sm">
                <span className="inline-flex items-center gap-1.5 font-medium text-primary">
                  <BookOpen className="size-3.5" />
                  Setup guide
                  <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
                </span>
                {it.external && (
                  <a
                    href={it.external.href}
                    target="_blank"
                    rel="noreferrer"
                    className="relative z-10 inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                  >
                    {it.external.label}
                    <ExternalLink className="size-3" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-10 rounded-xl border bg-muted/30 p-5 text-sm text-muted-foreground">
          <p>
            <strong className="text-foreground">Building with AI?</strong>{" "}
            Point your agent at the machine-readable manifests:{" "}
            <Link href="/mcp.json" className="text-primary hover:underline">
              /mcp.json
            </Link>
            ,{" "}
            <Link href="/llms.txt" className="text-primary hover:underline">
              /llms.txt
            </Link>
            , and the{" "}
            <a href={`${API_URL}/v1/openapi.json`} className="text-primary hover:underline">
              OpenAPI 3 spec
            </a>{" "}
            — they stay in sync with the docs automatically.
          </p>
        </div>

        <div className="mt-12 rounded-xl border bg-card p-8 text-center">
          <h2 className="text-2xl font-bold">One key. Every integration.</h2>
          <p className="mt-2 text-muted-foreground">
            Start with 100 free credits — no credit card required.
          </p>
          <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
            <Button asChild size="lg">
              <Link href="/signup">Get your API key</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/docs/integrations">Read the setup guides</Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
