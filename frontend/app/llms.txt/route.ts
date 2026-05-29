import {
  ALL_ENDPOINTS,
  PLATFORM_GROUPS,
  SITE_URL,
  tagline,
} from "@/lib/api-catalog";

export const dynamic = "force-static";

const TOOLS: { slug: string; name: string; desc: string }[] = [
  { slug: "youtube-transcript", name: "YouTube Transcript Generator", desc: "Free tool to get a YouTube video transcript." },
  { slug: "youtube-summarizer", name: "YouTube Summarizer", desc: "Free AI summary of any YouTube video." },
  { slug: "tiktok-transcript", name: "TikTok Transcript Generator", desc: "Free TikTok video transcript." },
  { slug: "tiktok-summarizer", name: "TikTok Summarizer", desc: "Free AI summary of any TikTok video." },
  { slug: "instagram-transcript", name: "Instagram Transcript Generator", desc: "Free Instagram Reel transcript." },
  { slug: "instagram-summarizer", name: "Instagram Summarizer", desc: "Free AI summary of any Instagram Reel." },
  { slug: "facebook-transcript", name: "Facebook Transcript Generator", desc: "Free Facebook video transcript." },
];

export async function GET() {
  const base = SITE_URL;

  const apiLines = ALL_ENDPOINTS.map(
    (ep) => `- [${ep.name}](${base}/apis/${ep.slug}): ${tagline(ep)}`,
  ).join("\n");

  const toolLines = TOOLS.map(
    (t) => `- [${t.name}](${base}/tools/${t.slug}): ${t.desc}`,
  ).join("\n");

  const platformLines = PLATFORM_GROUPS.map(
    (g) => `- **${g.name}** (${g.endpoints.length} endpoints): ${g.blurb}`,
  ).join("\n");

  const body = `# Captapi

> One API for structured data from YouTube, TikTok, Instagram, and Facebook. Extract transcripts, AI summaries, comments, video details, profile/channel stats, search results, and downloadable media — with a single REST request that returns clean JSON.

Captapi is a developer API (Merchant of Record billing via Dodo Payments) that unifies access to public social-media video data across four platforms. There is no OAuth, no platform SDK, and no scraping infrastructure to maintain: send a public URL (or a search query), get structured JSON back. A single API key works across every platform. Responses are cached for 24 hours, so repeat lookups are instant and cost 0 credits. New accounts start with 100 free credits.

Base API URL: https://api.captapi.com
Authentication: \`Authorization: Bearer sk_live_...\` (create a key in the dashboard).
Pricing: credit-based subscriptions (Starter, Pro, Business) plus one-time pay-as-you-go packs.

## Platforms
${platformLines}

## Documentation
- [Documentation](${base}/docs): Getting started, authentication, request/response formats, and the full endpoint reference.
- [All APIs](${base}/apis): Browse every available endpoint with examples.
- [Pricing](${base}/pricing): Plans, credit costs, and pay-as-you-go packs.

## APIs
${apiLines}

## Free Tools
${toolLines}

## Optional
- [Terms of Service](${base}/legal/terms)
- [Privacy Policy](${base}/legal/privacy)
`;

  return new Response(body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=3600, s-maxage=86400",
    },
  });
}
