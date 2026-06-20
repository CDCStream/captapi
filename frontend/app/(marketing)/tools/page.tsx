import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { TOOL_LIST } from "@/lib/tools";
import { MAKER_TOOLS, type MakerToolType } from "@/lib/maker-tools";
import { buildMetadata } from "@/lib/seo";

const MAKER_BADGES: Record<MakerToolType, string> = {
  ai: "AI generator",
  converter: "Converter",
  viewer: "Viewer",
  downloader: "Downloader",
  reference: "Reference",
  canvas: "Maker",
};

type HubTool = {
  slug: string;
  title: string;
  description: string;
  platform: string;
  badge: string;
};

const PLATFORM_ORDER = ["YouTube", "TikTok", "Instagram", "Facebook", "General"];

const PLATFORM_DESCRIPTIONS: Record<string, string> = {
  YouTube: "Transcript, summary, thumbnail, banner, title, description, hashtag, and Shorts idea tools for YouTube creators.",
  TikTok: "Transcript, summary, username, hashtag, video idea, and secret emoji tools for TikTok content workflows.",
  Instagram: "Free transcript, summarizer, highlights viewer, and photo downloader tools for Instagram.",
  Facebook: "Free transcript tools for public Facebook videos.",
  General: "Cross-platform creator utilities for bios and reusable social media assets.",
};

const tools: HubTool[] = [
  ...TOOL_LIST.map((tool) => ({
    slug: tool.slug,
    title: tool.title,
    description: tool.description,
    platform: tool.platform,
    badge: tool.kind === "summary" ? "AI summary" : "Transcript",
  })),
  ...MAKER_TOOLS.map((tool) => ({
    slug: tool.slug,
    title: tool.name,
    description: tool.blurb,
    platform: tool.platform,
    badge: MAKER_BADGES[tool.type] ?? "Maker",
  })),
];

const groupedTools = PLATFORM_ORDER.map((platform) => ({
  platform,
  description: PLATFORM_DESCRIPTIONS[platform],
  tools: tools.filter((tool) => tool.platform === platform),
})).filter((group) => group.tools.length > 0);

export const metadata = buildMetadata({
  title: "Free Tools — social video transcripts, summaries & AI generators",
  description:
    "Free YouTube, TikTok, Instagram, Facebook, and general creator tools grouped by platform. Transcripts, summaries, makers, and AI generators powered by Captapi.",
  path: "/tools",
});

export default function ToolsHub() {
  return (
    <div>
      <h1 className="text-4xl font-bold mb-2">Free Tools</h1>
      <p className="text-muted-foreground max-w-2xl">
        Try Captapi right in your browser. Free transcript, summary, maker, and AI
        generator tools grouped by platform — start free, no card required.
      </p>

      <div className="mt-10 space-y-14">
        {groupedTools.map((group) => (
          <section key={group.platform}>
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div>
                <h2 className="text-2xl font-semibold">{group.platform} tools</h2>
                <p className="mt-1 max-w-2xl text-muted-foreground">{group.description}</p>
              </div>
              <Badge variant="secondary">{group.tools.length} tools</Badge>
            </div>

            <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {group.tools.map((tool) => (
                <Link
                  key={tool.slug}
                  href={`/tools/${tool.slug}`}
                  className="group flex flex-col rounded-xl border bg-card p-5 transition-all hover:shadow-lg hover:-translate-y-0.5"
                >
                  <Badge variant="secondary" className="mb-3 w-fit">
                    {tool.badge}
                  </Badge>
                  <h3 className="text-lg font-semibold leading-snug group-hover:text-primary transition-colors">
                    {tool.title}
                  </h3>
                  <p className="mt-2 flex-1 text-sm text-muted-foreground">{tool.description}</p>
                  <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary">
                    Open tool
                    <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
                  </span>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
