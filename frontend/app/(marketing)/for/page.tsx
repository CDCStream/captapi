import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { USE_CASE_LIST } from "@/lib/use-cases";
import { buildMetadata } from "@/lib/seo";

export const metadata = buildMetadata({
  title: "Captapi Use Cases | Social Media Data API for Every Team",
  description:
    "See how teams use Captapi — AI startups, agencies, content creators, researchers and developers — to extract transcripts, summaries, comments and engagement from social video.",
  path: "/for",
});

export default function UseCasesHub() {
  return (
    <div className="py-12">
      <div className="container max-w-5xl">
        <nav
          aria-label="Breadcrumb"
          className="mb-6 flex items-center gap-2 text-sm text-muted-foreground"
        >
          <Link href="/" className="hover:text-foreground">Home</Link>
          <span>/</span>
          <span className="text-foreground">Use Cases</span>
        </nav>

        <h1 className="text-4xl font-bold tracking-tight">
          One API, built for your use case
        </h1>
        <p className="mt-4 max-w-3xl text-lg text-muted-foreground">
          Captapi turns social video into structured data — transcripts, AI
          summaries, comments and engagement metrics across YouTube, TikTok,
          Instagram and Facebook. See how different teams put it to work.
        </p>

        <div className="mt-10 grid gap-4 sm:grid-cols-2">
          {USE_CASE_LIST.map((uc) => (
            <Link
              key={uc.slug}
              href={`/for/${uc.slug}`}
              className="group rounded-xl border bg-card p-6 transition-colors hover:border-primary"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">For {uc.audience}</h2>
                <ArrowRight className="size-4 text-muted-foreground transition-transform group-hover:translate-x-1" />
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{uc.h1}</p>
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
