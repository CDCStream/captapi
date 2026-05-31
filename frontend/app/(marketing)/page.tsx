import type { Metadata } from "next";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Zap,
  Code2,
  ShieldCheck,
  Sparkles,
  Database,
  BrainCircuit,
  Users,
  TrendingUp,
} from "lucide-react";
import { CaptapiHero } from "@/components/marketing/captapi-hero";
import { ApiCatalog } from "@/components/marketing/api-catalog";
import { PricingPlans } from "@/components/marketing/pricing-plans";
import { ALL_ENDPOINTS } from "@/lib/api-catalog";

export const metadata: Metadata = {
  alternates: { canonical: "/" },
};

const features = [
  {
    icon: Sparkles,
    title: "AI Summaries",
    body: "GPT-4o-mini powered video summaries with key points, topics, and sentiment.",
  },
  {
    icon: Zap,
    title: "Sub-second Cache",
    body: "24h shared cache. Repeat requests are instant and free.",
  },
  {
    icon: Code2,
    title: "Developer-First",
    body: "Plain REST. No OAuth. SDKs for Python, Node, and PHP coming soon.",
  },
  {
    icon: ShieldCheck,
    title: "Reliable Scraping",
    body: "Apify-backed actors with automatic retries and fallback.",
  },
];

const useCases = [
  {
    icon: BrainCircuit,
    title: "AI startups",
    body: "Feed transcripts straight into your RAG pipeline, fine-tuning dataset, or video Q&A agent.",
  },
  {
    icon: TrendingUp,
    title: "Marketing & agencies",
    body: "Track competitor content, monitor brand mentions, analyze sentiment across platforms.",
  },
  {
    icon: Users,
    title: "Content creators",
    body: "Auto-generate timestamps, blog posts, and social captions from your own videos.",
  },
  {
    icon: Database,
    title: "Researchers & journalists",
    body: "Bulk-export comments and metadata for trend analysis, OSINT, or academic studies.",
  },
];

const faqs = [
  {
    q: "Do I need OAuth or each platform's API key?",
    a: "No. One Captapi key gives you access to all four platforms. We handle authentication, proxies, rate limits, and retries for you.",
  },
  {
    q: "How is this different from the official YouTube/Instagram APIs?",
    a: "Official APIs are restrictive (rate limits, OAuth flows, deprecated endpoints, no transcript support for Reels/TikToks). Captapi works on public data with one consistent REST interface — no app review process, no quotas to negotiate.",
  },
  {
    q: "What counts as a credit?",
    a: "Each request consumes 1-6 credits depending on the endpoint (transcript: 2, summarize: 4, video details: 1). Cached results (within 24h) cost 0 credits.",
  },
  {
    q: "What happens if a video has no captions?",
    a: "You'll get a 422 with a clear error message. We don't charge credits for empty results — only for successful data extraction.",
  },
  {
    q: "Can I cancel anytime?",
    a: "Yes. All paid plans are monthly and cancellable with one click in the dashboard. No long-term contracts.",
  },
  {
    q: "Is this GDPR / TOS compliant?",
    a: "Captapi only extracts publicly accessible data and is intended for compliant business use. You are responsible for how you process and store the data within your jurisdiction.",
  },
];

const faqJsonLd = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: faqs.map((f) => ({
    "@type": "Question",
    name: f.q,
    acceptedAnswer: { "@type": "Answer", text: f.a },
  })),
};

export default function LandingPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />
      {/* HERO */}
      <CaptapiHero />

      {/* APIs — One API. Every platform. */}
      <section className="pt-6 pb-16 border-t bg-muted/30" id="apis">
        <div className="container max-w-6xl">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold">One API. Every platform.</h2>
            <p className="mt-3 text-muted-foreground max-w-2xl mx-auto">
              {ALL_ENDPOINTS.length} REST endpoints across YouTube, TikTok,
              Instagram, and Facebook. No more juggling 4 different scrapers or
              platform SDKs.
            </p>
          </div>
          <ApiCatalog />
          <div className="mt-8 text-center">
            <Link
              href="/apis"
              className="text-sm text-primary hover:underline"
            >
              Browse all APIs →
            </Link>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="py-16 border-t" id="features">
        <div className="container">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold">
              Everything you need, nothing you don&apos;t
            </h2>
            <p className="mt-3 text-muted-foreground">
              A focused toolkit for builders.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((f) => (
              <Card key={f.title}>
                <CardHeader>
                  <f.icon className="size-6 text-primary mb-2" />
                  <CardTitle className="text-lg">{f.title}</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">
                  {f.body}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* USE CASES */}
      <section className="py-16 border-t bg-muted/30">
        <div className="container">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold">Built for serious workloads</h2>
            <p className="mt-3 text-muted-foreground">
              From scrappy MVPs to enterprise data pipelines.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {useCases.map((u) => (
              <Card key={u.title}>
                <CardHeader>
                  <u.icon className="size-6 text-primary mb-2" />
                  <CardTitle className="text-lg">{u.title}</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">
                  {u.body}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* PRICING PREVIEW */}
      <section className="py-16 border-t" id="pricing-preview">
        <PricingPlans />
        <div className="mt-10 text-center">
          <Link
            href="/pricing"
            className="text-sm text-primary hover:underline"
          >
            See full pricing comparison →
          </Link>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-16 border-t" id="faq">
        <div className="container max-w-3xl">
          <h2 className="text-3xl font-bold text-center mb-12">
            Frequently asked questions
          </h2>
          <div className="space-y-3">
            {faqs.map((f) => (
              <details
                key={f.q}
                className="group rounded-lg border bg-card p-5 [&_summary::-webkit-details-marker]:hidden"
              >
                <summary className="flex items-center justify-between cursor-pointer font-medium list-none">
                  <span>{f.q}</span>
                  <span className="ml-4 text-muted-foreground transition-transform group-open:rotate-45 text-xl leading-none">
                    +
                  </span>
                </summary>
                <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
                  {f.a}
                </p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="py-20 border-t bg-muted/30">
        <div className="container max-w-3xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ship your first integration in 60 seconds
          </h2>
          <p className="text-muted-foreground mb-8">
            Sign up, copy your API key, make your first call — no credit card,
            no demos.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button asChild size="lg">
              <Link href="/signup">Get Your API Key</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/tools">Try Free Tools</Link>
            </Button>
          </div>
        </div>
      </section>
    </>
  );
}
