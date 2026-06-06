import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { TOOL_LIST } from "@/lib/tools";
import { MAKER_TOOLS } from "@/lib/maker-tools";
import { buildMetadata } from "@/lib/seo";

export const metadata = buildMetadata({
  title: "Free Tools — transcripts & summaries for social video",
  description:
    "Free YouTube, TikTok, Instagram, and Facebook transcript & summarizer tools. Powered by the Captapi.",
  path: "/tools",
});

export default function ToolsHub() {
  return (
    <div>
      <h1 className="text-4xl font-bold mb-2">Free Tools</h1>
      <p className="text-muted-foreground max-w-2xl">
        Try Captapi right in your browser. Transcripts and AI summaries for
        YouTube, TikTok, Instagram, and Facebook — start free, no card required.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-10">
        {TOOL_LIST.map((tool) => (
          <Link
            key={tool.slug}
            href={`/tools/${tool.slug}`}
            className="group flex flex-col rounded-xl border bg-card p-5 transition-all hover:shadow-lg hover:-translate-y-0.5"
          >
            <Badge variant="secondary" className="mb-3 w-fit">
              {tool.platform}
            </Badge>
            <h2 className="text-lg font-semibold leading-snug group-hover:text-primary transition-colors">
              {tool.title}
            </h2>
            <p className="mt-2 flex-1 text-sm text-muted-foreground">
              {tool.description}
            </p>
            <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary">
              Open tool
              <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
            </span>
          </Link>
        ))}
      </div>

      <div className="mt-16">
        <h2 className="text-2xl font-semibold">Generators & makers</h2>
        <p className="mt-1 max-w-2xl text-muted-foreground">
          Free, no-login creator tools for YouTube and TikTok — design thumbnails and banners, and
          generate titles, hashtags, descriptions, video ideas, usernames, and bios in seconds.
        </p>
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {MAKER_TOOLS.map((tool) => (
            <Link
              key={tool.slug}
              href={`/tools/${tool.slug}`}
              className="group flex flex-col rounded-xl border bg-card p-5 transition-all hover:shadow-lg hover:-translate-y-0.5"
            >
              <Badge variant="secondary" className="mb-3 w-fit">
                {tool.platform}
              </Badge>
              <h3 className="text-lg font-semibold leading-snug group-hover:text-primary transition-colors">
                {tool.name}
              </h3>
              <p className="mt-2 flex-1 text-sm text-muted-foreground">{tool.blurb}</p>
              <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary">
                Open tool
                <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
