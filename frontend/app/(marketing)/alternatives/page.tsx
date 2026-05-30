import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SITE_URL } from "@/lib/api-catalog";
import { COMPETITOR_LIST } from "@/lib/competitors";

export const metadata: Metadata = {
  title: "Captapi Alternatives & Comparisons | Social Media Data API",
  description:
    "See how Captapi compares to other social media and video data APIs. One REST API for transcripts, AI summaries, comments & engagement across YouTube, TikTok, Instagram & Facebook.",
  alternates: { canonical: `${SITE_URL}/alternatives` },
};

export default function AlternativesHub() {
  return (
    <div className="py-12">
      <div className="container max-w-5xl">
        <nav
          aria-label="Breadcrumb"
          className="mb-6 flex items-center gap-2 text-sm text-muted-foreground"
        >
          <Link href="/" className="hover:text-foreground">Home</Link>
          <span>/</span>
          <span className="text-foreground">Alternatives</span>
        </nav>

        <h1 className="text-4xl font-bold tracking-tight">
          Captapi alternatives & comparisons
        </h1>
        <p className="mt-4 max-w-3xl text-lg text-muted-foreground">
          Evaluating social media and video data APIs? See how Captapi compares.
          One REST API for transcripts, AI summaries, comments and engagement
          metrics across YouTube, TikTok, Instagram and Facebook — with 100 free
          credits and free public tools.
        </p>

        <div className="mt-10 grid gap-4 sm:grid-cols-2">
          {COMPETITOR_LIST.map((c) => (
            <Link
              key={c.slug}
              href={`/alternatives/${c.slug}`}
              className="group rounded-xl border bg-card p-6 transition-colors hover:border-primary"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">
                  Captapi vs {c.name}
                </h2>
                <ArrowRight className="size-4 text-muted-foreground transition-transform group-hover:translate-x-1" />
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{c.focus}</p>
              <p className="mt-3 text-xs text-muted-foreground">
                The best {c.name} alternative for video data →
              </p>
            </Link>
          ))}
        </div>

        <section className="mt-14 rounded-xl border bg-muted/30 p-8 text-center">
          <h2 className="text-2xl font-bold">Start building with Captapi</h2>
          <p className="mt-2 text-muted-foreground">
            One API, four platforms, 100 free credits. No credit card required.
          </p>
          <div className="mt-6">
            <Button asChild size="lg">
              <Link href="/signup">Get your free API key</Link>
            </Button>
          </div>
        </section>
      </div>
    </div>
  );
}
