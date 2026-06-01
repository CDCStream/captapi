import type { Metadata } from "next";
import Link from "next/link";
import { CodeTabs } from "@/components/docs/code-tabs";
import {
  PLATFORM_GROUPS,
  API_URL,
  SITE_URL,
  type ApiEndpoint,
} from "@/lib/api-catalog";

export const metadata: Metadata = {
  title: "Documentation — Captapi API Reference",
  description:
    "Captapi documentation: authentication, requests, response format, credits, errors, and the full REST API reference for YouTube, TikTok, Instagram, and Facebook.",
  alternates: { canonical: `${SITE_URL}/docs` },
};

const firstRequest = [
  {
    label: "cURL",
    code: `curl "${API_URL}/v1/youtube/transcript?url=https%3A%2F%2Fyoutube.com%2Fwatch%3Fv%3DdQw4w9WgXcQ" \\
  -H "Authorization: Bearer capt_live_..."`,
  },
  {
    label: "Python",
    code: `import requests

res = requests.get(
    "${API_URL}/v1/youtube/transcript",
    params={"url": "https://youtube.com/watch?v=dQw4w9WgXcQ"},
    headers={"Authorization": "Bearer capt_live_..."},
)
print(res.json())`,
  },
  {
    label: "Node",
    code: `const url =
  "${API_URL}/v1/youtube/transcript?url=" +
  encodeURIComponent("https://youtube.com/watch?v=dQw4w9WgXcQ");

const res = await fetch(url, {
  headers: { Authorization: "Bearer capt_live_..." },
});
const data = await res.json();
console.log(data);`,
  },
  {
    label: "PHP",
    code: `<?php
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "${API_URL}/v1/youtube/transcript?" . http_build_query([
    "url" => "https://youtube.com/watch?v=dQw4w9WgXcQ",
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ["Authorization: Bearer capt_live_..."]);
echo curl_exec($ch);
curl_close($ch);`,
  },
  {
    label: "Go",
    code: `package main

import (
	"fmt"
	"io"
	"net/http"
)

func main() {
	req, _ := http.NewRequest("GET",
		"${API_URL}/v1/youtube/transcript?url=https://youtube.com/watch?v=dQw4w9WgXcQ", nil)
	req.Header.Set("Authorization", "Bearer capt_live_...")
	res, _ := http.DefaultClient.Do(req)
	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)
	fmt.Println(string(body))
}`,
  },
];

const encodeSamples = [
  { label: "cURL", code: `# URL-encode the target URL before passing it
urlencode "https://youtube.com/watch?v=dQw4w9WgXcQ"`,
  },
  { label: "Python", code: `import urllib.parse
encoded = urllib.parse.quote("https://youtube.com/watch?v=dQw4w9WgXcQ")` },
  { label: "Node", code: `const encoded = encodeURIComponent("https://youtube.com/watch?v=dQw4w9WgXcQ");` },
  { label: "PHP", code: `<?php
$encoded = urlencode("https://youtube.com/watch?v=dQw4w9WgXcQ");` },
  { label: "Go", code: `import "net/url"
encoded := url.QueryEscape("https://youtube.com/watch?v=dQw4w9WgXcQ")` },
];

const successResponse = `{
  "success": true,
  "cached": false,
  "creditsUsed": 2,
  "data": {
    "language": "en",
    "segments": [
      { "start": 0.0, "end": 4.12, "text": "Hey everyone, welcome back." }
    ],
    "text": "Hey everyone, welcome back."
  }
}`;

const errorResponse = `{
  "success": false,
  "error": {
    "code": "no_captions",
    "message": "This video has no captions and audio transcription failed."
  }
}`;

const ERRORS: { code: string; status: string; meaning: string }[] = [
  { code: "invalid_api_key", status: "401", meaning: "Missing or malformed Authorization header." },
  { code: "insufficient_credits", status: "402", meaning: "Your balance is too low for this request." },
  { code: "not_found", status: "404", meaning: "The target URL or resource could not be found." },
  { code: "no_captions", status: "422", meaning: "No captions and audio transcription failed (not charged)." },
  { code: "rate_limited", status: "429", meaning: "Too many requests — slow down or upgrade your plan." },
  { code: "upstream_error", status: "502", meaning: "Temporary scraping failure. Safe to retry (not charged)." },
];

function H2({ id, children }: { id: string; children: React.ReactNode }) {
  return (
    <h2
      id={id}
      className="scroll-mt-24 text-2xl font-bold tracking-tight mt-14 mb-4 first:mt-0"
    >
      {children}
    </h2>
  );
}
function H3({ id, children }: { id: string; children: React.ReactNode }) {
  return (
    <h3 id={id} className="scroll-mt-24 text-lg font-semibold mt-8 mb-3">
      {children}
    </h3>
  );
}

function ReferenceTable({
  id,
  endpoints,
  title,
}: {
  id: string;
  endpoints: { method: string; path: string; credits: number | string; desc: string; slug?: string }[];
  title: string;
}) {
  return (
    <div className="mb-2">
      <H3 id={id}>{title}</H3>
      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/50 text-left">
            <tr>
              <th className="px-4 py-2.5 font-medium w-16">Method</th>
              <th className="px-4 py-2.5 font-medium">Endpoint</th>
              <th className="px-4 py-2.5 font-medium w-20">Credits</th>
              <th className="px-4 py-2.5 font-medium">Description</th>
            </tr>
          </thead>
          <tbody>
            {endpoints.map((e) => (
              <tr key={e.path} className="border-t align-top">
                <td className="px-4 py-2.5">
                  <span className="rounded bg-emerald-500/10 px-1.5 py-0.5 font-mono text-[11px] font-semibold text-emerald-600">
                    {e.method}
                  </span>
                </td>
                <td className="px-4 py-2.5 font-mono text-xs">
                  {e.slug ? (
                    <Link href={`/apis/${e.slug}`} className="hover:text-primary hover:underline">
                      {e.path}
                    </Link>
                  ) : (
                    e.path
                  )}
                </td>
                <td className="px-4 py-2.5 text-muted-foreground">{e.credits}</td>
                <td className="px-4 py-2.5 text-muted-foreground">{e.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function refRows(eps: ApiEndpoint[]) {
  return eps.map((e) => ({
    method: e.method,
    path: e.path,
    credits: e.creditsPerResult
      ? `~${e.credits}`
      : e.credits,
    desc: e.shortName,
    slug: e.slug,
  }));
}

const platformAnchor: Record<string, string> = {
  youtube: "api-youtube",
  tiktok: "api-tiktok",
  instagram: "api-instagram",
  facebook: "api-facebook",
};

export default function DocsPage() {
  return (
    <div className="prose-docs">
      {/* Intro */}
      <p className="text-sm font-medium text-primary mb-2">Getting Started</p>
      <H2 id="introduction">Introduction</H2>
      <p className="text-muted-foreground leading-relaxed max-w-3xl">
        Captapi gives you <strong className="text-foreground">structured data
        from social media video</strong> through one consistent REST API. Send a
        public URL from YouTube, TikTok, Instagram, or Facebook and get back
        clean JSON — transcripts, AI summaries, video details, comments, search
        results, and downloads. No OAuth, no per-platform SDKs, no scraping
        infrastructure to maintain.
      </p>
      <ul className="mt-4 space-y-2 text-sm text-muted-foreground max-w-3xl">
        <li>• One API key works across all four platforms.</li>
        <li>• Repeat calls are served from a shared cache for free (up to 24h; time-sensitive metrics refresh within ~1h).</li>
        <li>• You are only charged for successful requests.</li>
      </ul>

      {/* Quickstart */}
      <H2 id="quickstart">Quickstart</H2>
      <p className="text-muted-foreground mb-4 max-w-3xl">
        After{" "}
        <Link href="/signup" className="text-primary hover:underline">
          signing up
        </Link>{" "}
        and copying your API key from the dashboard, make your first request:
      </p>
      <CodeTabs samples={firstRequest} />

      {/* Authentication */}
      <H2 id="authentication">Authentication</H2>
      <p className="text-muted-foreground max-w-3xl">
        All requests are authenticated with a Bearer token. Generate keys in{" "}
        <Link href="/dashboard/api-keys" className="text-primary hover:underline">
          your dashboard
        </Link>{" "}
        and send them in the <code className="rounded bg-muted px-1.5 py-0.5 text-xs">Authorization</code>{" "}
        header. Keep keys secret — never expose <code className="rounded bg-muted px-1.5 py-0.5 text-xs">capt_live_</code>{" "}
        keys in client-side code.
      </p>
      <div className="mt-4">
        <CodeTabs
          samples={[
            { label: "Header", code: `Authorization: Bearer capt_live_xxxxxxxxxxxxxxxxxxxx` },
          ]}
        />
      </div>

      {/* Making Requests */}
      <H2 id="making-requests">Making Requests</H2>
      <p className="text-muted-foreground max-w-3xl">
        Most endpoints take a single <code className="rounded bg-muted px-1.5 py-0.5 text-xs">url</code>{" "}
        query parameter (search endpoints use <code className="rounded bg-muted px-1.5 py-0.5 text-xs">q</code>).
        When building the request as a query string, you must{" "}
        <strong className="text-foreground">URL-encode</strong> the target URL so
        it isn&apos;t misinterpreted as multiple parameters.
      </p>
      <div className="mt-4">
        <CodeTabs samples={encodeSamples} />
      </div>

      {/* Response Format */}
      <H2 id="response-format">Response Format</H2>
      <p className="text-muted-foreground max-w-3xl">
        Every response is JSON with a top-level <code className="rounded bg-muted px-1.5 py-0.5 text-xs">success</code>{" "}
        boolean. Successful responses include <code className="rounded bg-muted px-1.5 py-0.5 text-xs">cached</code>,{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">creditsUsed</code>, and a{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">data</code> object.
      </p>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div>
          <p className="mb-2 text-sm font-medium">Success</p>
          <CodeTabs samples={[{ label: "200 OK", code: successResponse }]} />
        </div>
        <div>
          <p className="mb-2 text-sm font-medium">Error</p>
          <CodeTabs samples={[{ label: "4xx / 5xx", code: errorResponse }]} />
        </div>
      </div>

      {/* Credits & Caching */}
      <H2 id="credits-caching">Credits &amp; Caching</H2>
      <p className="text-muted-foreground max-w-3xl">
        Credits are the unit of billing. Each endpoint costs 1–4 credits per
        successful call (video details: 1, transcript/comments: 2, summarize: 4,
        downloads: 3). <strong className="text-foreground">Failed and empty
        results are never charged.</strong>
      </p>
      <p className="mt-3 text-muted-foreground max-w-3xl">
        Responses are cached and shared across all accounts for{" "}
        <strong className="text-foreground">up to 24 hours</strong> — time-sensitive
        data (engagement metrics, follower lists) refreshes within ~1 hour so it
        stays current. If a result is served from cache,{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">cached</code> is{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">true</code> and{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">creditsUsed</code>{" "}
        is <code className="rounded bg-muted px-1.5 py-0.5 text-xs">0</code>.
      </p>

      {/* Errors */}
      <H2 id="errors">Errors</H2>
      <p className="text-muted-foreground max-w-3xl mb-4">
        Errors return a non-2xx status and an{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">error</code> object
        with a stable <code className="rounded bg-muted px-1.5 py-0.5 text-xs">code</code>{" "}
        and a human-readable <code className="rounded bg-muted px-1.5 py-0.5 text-xs">message</code>.
      </p>
      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/50 text-left">
            <tr>
              <th className="px-4 py-2.5 font-medium w-20">Status</th>
              <th className="px-4 py-2.5 font-medium">Code</th>
              <th className="px-4 py-2.5 font-medium">Meaning</th>
            </tr>
          </thead>
          <tbody>
            {ERRORS.map((e) => (
              <tr key={e.code} className="border-t">
                <td className="px-4 py-2.5 font-mono text-xs">{e.status}</td>
                <td className="px-4 py-2.5 font-mono text-xs">{e.code}</td>
                <td className="px-4 py-2.5 text-muted-foreground">{e.meaning}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Rate Limits */}
      <H2 id="rate-limits">Rate Limits</H2>
      <p className="text-muted-foreground max-w-3xl">
        Rate limits scale with your plan and are returned on every response via{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">X-RateLimit-Limit</code>,{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">X-RateLimit-Remaining</code>, and{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">X-RateLimit-Reset</code>{" "}
        headers. When you exceed the limit you&apos;ll get a{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">429</code> — back off
        and retry after the reset window.
      </p>

      {/* API Reference */}
      <H2 id="api-reference">API Reference</H2>
      <p className="text-muted-foreground max-w-3xl mb-2">
        {PLATFORM_GROUPS.reduce((n, g) => n + g.endpoints.length, 0) + 2} endpoints
        across five groups. Click any endpoint for full parameters, examples, and
        FAQs.
      </p>

      {PLATFORM_GROUPS.map((g) => (
        <ReferenceTable
          key={g.id}
          id={platformAnchor[g.id]}
          title={g.name}
          endpoints={refRows(g.endpoints)}
        />
      ))}

      <ReferenceTable
        id="api-video-files"
        title="Video Files (direct upload)"
        endpoints={[
          { method: "POST", path: "/v1/video/transcript", credits: "1/min", desc: "Whisper transcription of an uploaded file" },
          { method: "POST", path: "/v1/video/summarize", credits: "1/min +1", desc: "Transcribe an uploaded file + AI summary" },
        ]}
      />

      <div className="mt-12 rounded-xl border bg-muted/30 p-6 text-center">
        <p className="font-semibold">Ready to build?</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Grab your free API key and make your first call in 60 seconds.
        </p>
        <Link
          href="/signup"
          className="mt-4 inline-flex h-10 items-center rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground hover:opacity-90"
        >
          Get your API key
        </Link>
      </div>
    </div>
  );
}
