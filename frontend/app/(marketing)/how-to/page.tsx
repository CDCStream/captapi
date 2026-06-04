import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { PLATFORM_GROUPS, howToTitle } from "@/lib/api-catalog";
import { buildMetadata } from "@/lib/seo";

export const metadata = buildMetadata({
  title: "How-to Guides — Social Media Data APIs | Captapi",
  description:
    "Step-by-step guides to extract transcripts, AI summaries, comments, downloads and engagement data from YouTube, TikTok, Instagram and Facebook with a single REST API call.",
  path: "/how-to",
});

export default function HowToHub() {
  return (
    <div className="container max-w-5xl py-16">
      <h1 className="text-4xl font-bold tracking-tight">How-to guides</h1>
      <p className="mt-3 max-w-2xl text-lg text-muted-foreground">
        Short, copy-paste guides for getting social media data with one REST API
        call — no OAuth, scraping infrastructure or platform SDKs.
      </p>

      <div className="mt-12 space-y-12">
        {PLATFORM_GROUPS.map((group) => (
          <section key={group.id}>
            <h2 className="text-2xl font-semibold">{group.name}</h2>
            <ul className="mt-4 grid gap-3 sm:grid-cols-2">
              {group.endpoints.map((ep) => (
                <li key={ep.slug}>
                  <Link
                    href={`/how-to/${ep.slug}`}
                    className="group flex items-center justify-between rounded-lg border p-4 transition-colors hover:border-primary/40 hover:bg-muted/40"
                  >
                    <span className="text-sm font-medium">{howToTitle(ep)}</span>
                    <ArrowRight className="size-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-foreground" />
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
