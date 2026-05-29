import Link from "next/link";
import { notFound } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Tool {
  slug: string;
  title: string;
  description: string;
  platform: string;
  apiEndpoint: string;
  faq: { q: string; a: string }[];
}

const TOOLS: Record<string, Tool> = {
  "youtube-transcript": {
    slug: "youtube-transcript",
    title: "Free YouTube Transcript Extractor",
    description: "Get the full transcript of any YouTube video in seconds. Powered by Captapi.",
    platform: "YouTube",
    apiEndpoint: "/v1/youtube/transcript",
    faq: [
      { q: "Is this really free?", a: "Yes — you get 100 free credits when you sign up. Transcripts cost 1 credit each." },
      { q: "Does it work for any language?", a: "We support all languages auto-detected by YouTube captions." },
      { q: "Can I use it programmatically?", a: "Yes — just call our API directly. See docs." },
    ],
  },
  "youtube-summarizer": {
    slug: "youtube-summarizer",
    title: "Free YouTube Video Summarizer",
    description: "AI-powered summary, key points, and topics from any YouTube video.",
    platform: "YouTube",
    apiEndpoint: "/v1/youtube/summarize",
    faq: [
      { q: "What AI model do you use?", a: "GPT-4o-mini for the right balance of quality and cost." },
      { q: "How long are the summaries?", a: "2-3 paragraphs + 4-8 key bullet points." },
    ],
  },
  "tiktok-transcript": {
    slug: "tiktok-transcript",
    title: "Free TikTok Transcript Extractor",
    description: "Extract speech and captions from any TikTok video.",
    platform: "TikTok",
    apiEndpoint: "/v1/tiktok/transcript",
    faq: [
      { q: "What if the TikTok has no captions?", a: "We use AI to transcribe the audio." },
    ],
  },
  "tiktok-summarizer": {
    slug: "tiktok-summarizer",
    title: "Free TikTok Video Summarizer",
    description: "Get the gist of any TikTok in seconds.",
    platform: "TikTok",
    apiEndpoint: "/v1/tiktok/summarize",
    faq: [
      { q: "Does it work for private accounts?", a: "No — public TikToks only." },
    ],
  },
  "instagram-transcript": {
    slug: "instagram-transcript",
    title: "Free Instagram Reel Transcript",
    description: "Extract transcripts from public Instagram Reels.",
    platform: "Instagram",
    apiEndpoint: "/v1/instagram/transcript",
    faq: [{ q: "Stories?", a: "No, Reels and Posts only." }],
  },
  "instagram-summarizer": {
    slug: "instagram-summarizer",
    title: "Free Instagram Reel Summarizer",
    description: "AI summaries for Instagram Reels.",
    platform: "Instagram",
    apiEndpoint: "/v1/instagram/summarize",
    faq: [],
  },
  "facebook-transcript": {
    slug: "facebook-transcript",
    title: "Free Facebook Video Transcript",
    description: "Transcripts from public Facebook videos.",
    platform: "Facebook",
    apiEndpoint: "/v1/facebook/transcript",
    faq: [],
  },
};

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const t = TOOLS[slug];
  if (!t) return {};
  return {
    title: `${t.title} | Captapi`,
    description: t.description,
  };
}

export function generateStaticParams() {
  return Object.keys(TOOLS).map((slug) => ({ slug }));
}

export default async function ToolPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const t = TOOLS[slug];
  if (!t) notFound();

  return (
    <div>
      <Badge variant="secondary" className="mb-3">{t.platform}</Badge>
      <h1 className="text-4xl font-bold mb-3">{t.title}</h1>
      <p className="text-muted-foreground text-lg max-w-2xl">{t.description}</p>

      <div className="grid md:grid-cols-2 gap-6 mt-10">
        <Card>
          <CardHeader>
            <CardTitle>Try it via API</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-muted/50 p-3 rounded text-xs overflow-x-auto"><code>{`curl "${(process.env.NEXT_PUBLIC_API_URL || "https://api.captapi.com")}${t.apiEndpoint}?url=YOUR_URL" \\
  -H "Authorization: Bearer sk_live_..."`}</code></pre>
            <Button asChild className="mt-4 w-full"><Link href="/signup">Get API key (free)</Link></Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>How it works</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground space-y-2">
            <p>1. Sign up — 100 credits free, no card required.</p>
            <p>2. Create an API key from the dashboard.</p>
            <p>3. Make a single GET request — done.</p>
            <p>The response is cached for 24 hours and shared by all requests for the same URL.</p>
          </CardContent>
        </Card>
      </div>

      {t.faq.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-semibold mb-4">FAQ</h2>
          <div className="space-y-3">
            {t.faq.map((f, i) => (
              <Card key={i}>
                <CardHeader>
                  <CardTitle className="text-base">{f.q}</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">{f.a}</CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
