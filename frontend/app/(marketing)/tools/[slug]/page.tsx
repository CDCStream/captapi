import Link from "next/link";
import { notFound } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TOOL_SLUGS, getTool } from "@/lib/tools";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const t = getTool(slug);
  if (!t) return {};
  return {
    title: `${t.title} | Captapi`,
    description: t.description,
    alternates: { canonical: `/tools/${slug}` },
  };
}

export function generateStaticParams() {
  return TOOL_SLUGS.map((slug) => ({ slug }));
}

export default async function ToolPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const t = getTool(slug);
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
  -H "Authorization: Bearer capt_live_..."`}</code></pre>
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
