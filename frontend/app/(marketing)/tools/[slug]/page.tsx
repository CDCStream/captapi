import Link from "next/link";
import { notFound } from "next/navigation";
import { FileText, MousePointerClick, Sparkles, Copy } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { TOOL_SLUGS, getTool, toolFaqs } from "@/lib/tools";
import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import {
  ToolHero,
  HowToUse,
  FAQSection,
  ToolCTA,
  webApplicationLd,
} from "@/components/tools/tool-sections";
import { ToolRunnerClient } from "@/components/tools/tool-runner-client";
import { TranscriptToolContent } from "@/components/tools/transcript-tool-content";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const t = getTool(slug);
  if (!t) return {};
  return buildMetadata({
    title: `${t.title} | Captapi`,
    description: t.description,
    path: `/tools/${slug}`,
    keywords: t.keywords,
  });
}

export function generateStaticParams() {
  return TOOL_SLUGS.map((slug) => ({ slug }));
}

export default async function ToolPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const t = getTool(slug);
  if (!t) notFound();

  const kind = t.kind ?? "transcript";
  const faqs = toolFaqs(t);
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "https://api.captapi.com";

  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "Free Tools", path: "/tools" },
      { name: t.title, path: `/tools/${slug}` },
    ]),
    webApplicationLd({
      name: t.title,
      description: t.description,
      path: `/tools/${slug}`,
      category: "MultimediaApplication",
    }),
    faqLd(faqs),
  ];

  const verb = kind === "summary" ? "summarize" : "transcribe";

  return (
    <div>
      <JsonLd data={jsonLd} />
      <ToolHero
        platform={t.platform}
        title={t.title}
        subtitle={
          kind === "summary"
            ? `Paste a ${t.platform} video link and get an instant AI summary with key points and topics — free, no sign-up, copy or download in one click.`
            : `Paste a ${t.platform} video link and get the full transcript as clean, copyable text in seconds — free, no sign-up, download as .txt.`
        }
      />

      <ToolRunnerClient
        endpoint={t.apiEndpoint}
        platform={t.platform}
        kind={kind}
        placeholder={t.urlPlaceholder}
      />

      <HowToUse
        steps={[
          { title: `Paste the ${t.platform} URL`, text: `Copy a public ${t.platform} video link into the box above.`, icon: <MousePointerClick className="size-4" /> },
          { title: `Run the tool`, text: `Click the button — we ${verb} the video automatically.`, icon: <Sparkles className="size-4" /> },
          { title: "Read the result", text: kind === "summary" ? "Review the summary, key points, and topics." : "Read the full, clean transcript text.", icon: <FileText className="size-4" /> },
          { title: "Copy or download", text: "Copy to clipboard or save as a .txt file — use it anywhere.", icon: <Copy className="size-4" /> },
        ]}
      />

      <section className="mt-16">
        <h2 className="text-2xl font-semibold">Prefer to do it in code?</h2>
        <p className="mt-2 max-w-2xl text-muted-foreground">
          The same {kind === "summary" ? "summary" : "transcript"} is available from the Captapi API in clean JSON — one request, no scraping.
        </p>
        <pre className="mt-4 overflow-x-auto rounded-xl border bg-muted/50 p-4 text-xs"><code>{`curl "${apiBase}${t.apiEndpoint}?url=YOUR_URL" \\
  -H "Authorization: Bearer capt_live_..."`}</code></pre>
        <Link href="/signup" className="mt-3 inline-block text-sm font-medium text-primary hover:underline">
          Get a free API key →
        </Link>
      </section>

      <FAQSection faqs={faqs} />

      <TranscriptToolContent tool={t} />

      <ToolCTA
        headline={
          slug === "tiktok-transcript"
            ? "API key = ~100× cheaper automation"
            : undefined
        }
        sub={
          slug === "tiktok-transcript"
            ? "Free tries are capped on purpose. With your own key, TikTok transcripts are 5 credits each (cache hits free) — build bots, n8n flows, and pipelines without the daily wall."
            : undefined
        }
      />
    </div>
  );
}
