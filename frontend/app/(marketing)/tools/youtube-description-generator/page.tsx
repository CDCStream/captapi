import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Copy, Upload } from "lucide-react";

const PATH = "/tools/youtube-description-generator";
const TITLE = "Free YouTube Description Generator — SEO-Optimized";
const DESC =
  "Generate an SEO-optimized YouTube description in seconds — with a keyword-rich hook, timestamps, a clear CTA, and hashtags. Free, no sign-up, one-click copy.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "youtube description generator",
    "youtube seo description",
    "video description template",
    "youtube description ideas",
    "how to write youtube description",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "youtube-description-generator",
  submitLabel: "Generate description",
  fields: [
    {
      name: "title",
      label: "Video title",
      type: "text",
      required: true,
      placeholder: "e.g. 10 Easy Meal Prep Ideas",
    },
    {
      name: "topic",
      label: "What the video is about",
      type: "textarea",
      required: true,
      placeholder: "Briefly describe the content and main keywords",
    },
    {
      name: "timestamps",
      label: "Timestamps (optional)",
      type: "textarea",
      placeholder: "0:00 Intro\n1:20 Tip 1\n...",
    },
  ],
};

const FAQS = [
  { q: "How long should a YouTube description be?", a: "YouTube allows up to 5,000 characters, but you don't need to fill it. A strong description is usually 150–300 words: a punchy 1–2 line hook, a short keyword-rich paragraph, timestamps, links, a CTA, and 2–3 hashtags. Front-load the most important information." },
  { q: "What part of the description shows in search and on the watch page?", a: "Only the first 2–3 lines — roughly the first 157 characters — appear before the 'Show more' fold and in Google and YouTube search snippets. Put your main keyword and a compelling hook there so viewers and search engines see it immediately." },
  { q: "Where should I place keywords in my description?", a: "Use your primary keyword naturally in the first sentence, then sprinkle related terms through the body. Avoid keyword stuffing — write for humans first. One or two natural mentions of your target phrase is enough to signal relevance without spamming." },
  { q: "Do I need timestamps, and how do chapters work?", a: "Timestamps create clickable chapters that improve watch experience and can surface in search. To enable chapters, your list must start at 0:00 and include at least three timestamps, each on its own line in ascending order, with each chapter at least 10 seconds long." },
  { q: "What call to action should I include?", a: "Pick one or two clear CTAs — subscribe, watch a related video, download a resource, or visit a link. A focused CTA placed after the hook or near your links converts better than a long list of requests buried at the bottom." },
  { q: "Should I put hashtags in the description?", a: "Yes — add 2–3 relevant hashtags. The first three appear as clickable links above your title. Stay under 15 total hashtags, because going over that limit makes YouTube ignore all of them." },
  { q: "Can I add links to my description?", a: "Absolutely. Add links to your website, social profiles, products, or related videos. Place the most important link high up, label each link clearly, and use full https URLs so they become clickable." },
  { q: "Do descriptions actually affect YouTube ranking?", a: "Descriptions help YouTube understand your video's topic and context, which supports discovery in search and suggested videos. They are one ranking signal among many — pair a strong description with a click-worthy title, thumbnail, and high watch time for the best results." },
  { q: "Do I need affiliate or copyright disclosures?", a: "If you use affiliate links, sponsorships, or paid promotions, disclose them clearly — the US FTC, the UK ASA, India's ASCI, and similar bodies worldwide require it. Also credit any music or footage you license, and add the required attribution in your description." },
  { q: "Can I reuse a description template across videos?", a: "Yes for the static parts — your channel boilerplate, social links, and standard CTA can stay consistent. But always rewrite the hook, keywords, and timestamps for each video so every description is unique and relevant to that specific content." },
];

export default function Page() {
  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "Free Tools", path: "/tools" },
      { name: "YouTube Description Generator", path: PATH },
    ]),
    webApplicationLd({ name: "YouTube Description Generator", description: DESC, path: PATH, category: "UtilitiesApplication" }),
    faqLd(FAQS),
  ];

  return (
    <div>
      <JsonLd data={jsonLd} />
      <ToolHero
        platform="YouTube"
        title="YouTube Description Generator"
        subtitle="Turn your video title and topic into an SEO-optimized YouTube description — with a keyword-rich hook, timestamps, a clear CTA, and hashtags, ready to copy in one click."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse
        steps={[
          { title: "Add your details", text: "Enter your video title, what it's about, and any timestamps you have.", icon: <PenLine className="size-4" /> },
          { title: "Generate", text: "Our AI writes an SEO-optimized description with a hook, body, CTA, and hashtags.", icon: <Sparkles className="size-4" /> },
          { title: "Copy it", text: "Copy the full description with one click and tweak any details you like.", icon: <Copy className="size-4" /> },
          { title: "Paste and publish", text: "Drop it into your YouTube description box and hit publish.", icon: <Upload className="size-4" /> },
        ]}
      />

      <FAQSection faqs={FAQS} />

      <LongContent>
        <div>
          <h2>The free AI YouTube description generator</h2>
          <p>
            Your description is one of the most underused growth levers on YouTube. It tells both viewers and the
            algorithm what your video is about, drives clicks to your links, and can even surface in Google search. Yet
            most creators leave it blank or paste the same boilerplate every time. This free YouTube description
            generator uses AI to turn your title and topic into a complete, SEO-optimized description — hook, body,
            timestamps, CTA, links, and hashtags — in seconds, with one-click copy and no sign-up required.
          </p>
        </div>

        <div>
          <h3>Why descriptions matter for YouTube SEO</h3>
          <p>
            YouTube can&apos;t watch your video the way a person does, so it leans on your title, description, and
            metadata to understand context and decide where to surface your content. A clear, keyword-rich description
            helps your video rank in YouTube search, appear in suggested videos, and get indexed by Google. It also
            improves the viewer experience with chapters, links, and a strong call to action — and a better experience
            means longer watch time, which is one of the strongest ranking signals of all.
          </p>
        </div>

        <div>
          <h3>The structure of a perfect description</h3>
          <p>A high-performing YouTube description follows a simple, repeatable structure:</p>
          <ul>
            <li><strong>Hook (lines 1–2):</strong> A compelling sentence with your primary keyword that makes people want to keep watching.</li>
            <li><strong>Body (2–4 sentences):</strong> A short summary of what the video covers, using related keywords naturally.</li>
            <li><strong>Timestamps:</strong> Clickable chapters starting at 0:00 so viewers can jump to what they need.</li>
            <li><strong>Call to action:</strong> One or two clear asks — subscribe, watch next, or grab a resource.</li>
            <li><strong>Links:</strong> Your website, products, or related videos, each clearly labeled.</li>
            <li><strong>Hashtags:</strong> 2–3 relevant tags; the first three appear above your title.</li>
          </ul>
        </div>

        <div>
          <h3>The search-snippet preview</h3>
          <p>
            Only the first 2–3 lines of your description — about the first 157 characters — show before the
            &apos;Show more&apos; fold, and that same snippet is what Google and YouTube display in search results. This
            is prime real estate. Lead with your main keyword and a benefit-driven hook, and never waste those lines on
            &quot;Don&apos;t forget to like and subscribe.&quot; Treat the opening like a meta description: it has to
            earn the click.
          </p>
        </div>

        <div>
          <h3>Keyword research basics</h3>
          <p>
            Good keywords start with how your audience actually searches. Use YouTube&apos;s search autocomplete, scan
            the titles of top-ranking videos in your niche, and check the &quot;people also search for&quot; suggestions.
            Pick one primary phrase and a handful of supporting terms, then weave them into your hook and body. Write
            naturally — if it reads like a robot wrote it, you&apos;ve overdone it. The goal is relevance, not density.
          </p>
        </div>

        <div>
          <h3>Chapters explained</h3>
          <p>
            Chapters turn your timestamps into a clickable navigation bar on the progress scrubber. To unlock them,
            your description needs a timestamp list that starts at <strong>0:00</strong>, contains at least
            <strong> three timestamps</strong> in ascending order, and gives each chapter a minimum length of 10
            seconds. Put each timestamp on its own line with a short label. Chapters boost watch experience, increase
            session time, and occasionally appear directly in search results as key moments.
          </p>
        </div>

        <div>
          <h3>Mistakes to avoid</h3>
          <ul>
            <li>Leaving the description blank or pasting identical boilerplate on every video.</li>
            <li>Keyword stuffing — repeating the same phrase until it reads as spam.</li>
            <li>Burying your most important info below the fold.</li>
            <li>Using more than 15 hashtags, which makes YouTube ignore all of them.</li>
            <li>Forgetting affiliate or sponsorship disclosures required by law.</li>
            <li>Broken or unlabeled links that viewers won&apos;t trust or click.</li>
          </ul>
        </div>

        <div>
          <h3>Built for creators everywhere</h3>
          <p>
            Whether you publish in the United States, the United Kingdom, India, Brazil, the Philippines, Indonesia, or
            anywhere else, a clear keyword-rich description travels well. Search behavior and disclosure rules differ by
            region — the FTC, the ASA, ASCI, and similar bodies each have their own guidance — so adapt language and
            compliance notes to your audience. Because this tool is free and needs no account, you can generate a fresh,
            localized description for every upload.
          </p>
        </div>

        <div>
          <h3>Part of a complete YouTube toolkit</h3>
          <p>
            A great description works best next to a strong title, hashtags, and thumbnail — all of which you can build
            with our other free tools. And when you&apos;re ready to research what&apos;s working at scale,
            Captapi&apos;s API gives you transcripts, comments, and engagement metrics from YouTube and other platforms
            in clean JSON, so your content decisions are driven by real data instead of guesswork.
          </p>
        </div>
      </LongContent>

      <ToolCTA />
    </div>
  );
}
