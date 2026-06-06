import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { MAKER_TOOLS } from "@/lib/maker-tools";

const tools = [
  { slug: "youtube-transcript",  name: "YouTube Transcript Extractor" },
  { slug: "youtube-summarizer",  name: "YouTube Video Summarizer" },
  { slug: "tiktok-transcript",   name: "TikTok Transcript Extractor" },
  { slug: "tiktok-summarizer",   name: "TikTok Video Summarizer" },
  { slug: "instagram-transcript",name: "Instagram Reel Transcript" },
  { slug: "instagram-summarizer",name: "Instagram Reel Summarizer" },
  { slug: "facebook-transcript", name: "Facebook Video Transcript" },
  ...MAKER_TOOLS.map((t) => ({ slug: t.slug, name: t.name })),
];

export default function ToolsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="py-12">
      <div className="container max-w-6xl">
        {children}
        <div className="mt-16 border-t pt-12">
          <h2 className="text-2xl font-semibold mb-6">All free tools</h2>
          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
            {tools.map((t) => (
              <Link key={t.slug} href={`/tools/${t.slug}`}>
                <Card className="hover:border-primary transition cursor-pointer">
                  <CardContent className="py-4">{t.name}</CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
