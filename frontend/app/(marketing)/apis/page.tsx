import type { Metadata } from "next";
import Link from "next/link";
import { ApiCatalog } from "@/components/marketing/api-catalog";
import { Button } from "@/components/ui/button";
import { ALL_ENDPOINTS, SITE_URL } from "@/lib/api-catalog";

const TITLE = "Social Media APIs — YouTube, TikTok, Instagram & Facebook";
const DESCRIPTION = `One REST API for ${ALL_ENDPOINTS.length} endpoints across YouTube, TikTok, Instagram, and Facebook. Transcripts, AI summaries, video details, comments, search, and downloads — structured JSON, no OAuth.`;

export const metadata: Metadata = {
  title: `${TITLE} | Captapi`,
  description: DESCRIPTION,
  keywords: [
    "social media API",
    "YouTube API",
    "TikTok API",
    "Instagram API",
    "Facebook API",
    "transcript API",
    "video summarizer API",
    "comments API",
  ],
  alternates: { canonical: `${SITE_URL}/apis` },
  openGraph: {
    title: TITLE,
    description: DESCRIPTION,
    url: `${SITE_URL}/apis`,
    type: "website",
  },
  twitter: { card: "summary_large_image", title: TITLE, description: DESCRIPTION },
};

export default function ApisIndexPage() {
  const itemList = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: "Captapi Social Media APIs",
    description: DESCRIPTION,
    numberOfItems: ALL_ENDPOINTS.length,
    itemListElement: ALL_ENDPOINTS.map((ep, i) => ({
      "@type": "ListItem",
      position: i + 1,
      url: `${SITE_URL}/apis/${ep.slug}`,
      name: ep.name,
    })),
  };

  const breadcrumb = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
      { "@type": "ListItem", position: 2, name: "APIs", item: `${SITE_URL}/apis` },
    ],
  };

  return (
    <div className="py-16">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(itemList) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }}
      />
      <div className="container max-w-6xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold tracking-tight">
            Our Social Media APIs
          </h1>
          <p className="mt-3 text-muted-foreground max-w-2xl mx-auto">
            Comprehensive social media analysis APIs for YouTube, TikTok,
            Instagram, and Facebook content — {ALL_ENDPOINTS.length} endpoints,
            one consistent REST interface.
          </p>
        </div>

        <ApiCatalog />

        <div className="mt-12 rounded-xl border bg-card p-8 text-center">
          <h2 className="text-2xl font-bold">Start with 100 free credits</h2>
          <p className="mt-2 text-muted-foreground">
            One key for every endpoint. No credit card required.
          </p>
          <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
            <Button asChild size="lg">
              <Link href="/signup">Get your API key</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/docs">Read the docs</Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
