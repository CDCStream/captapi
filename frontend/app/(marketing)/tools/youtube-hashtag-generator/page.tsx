import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Copy, Upload } from "lucide-react";

const PATH = "/tools/youtube-hashtag-generator";
const TITLE = "Free YouTube Hashtag Generator — 30 Tags in Seconds";
const DESC =
  "Generate 30 relevant YouTube hashtags from any topic, grouped into trending, niche, and broad-reach. AI-powered, free, with one-click copy and YouTube's 15-tag / 60-character limits built in.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "youtube hashtag generator",
    "best youtube hashtags",
    "youtube tags generator",
    "youtube hashtags",
    "hashtags for youtube",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "youtube-hashtag-generator",
  submitLabel: "Generate hashtags",
  fields: [
    {
      name: "topic",
      label: "Video topic or niche",
      type: "text",
      required: true,
      placeholder: "e.g. beginner home workouts",
      help: "Be specific for sharper hashtags — e.g. \u201ckitchen knife skills for beginners\u201d.",
    },
  ],
};

const FAQS = [
  { q: "How many hashtags should I use on YouTube?", a: "YouTube allows up to 15 hashtags per video, but only the first 3 appear above your title. Going over 15 causes YouTube to ignore all of them, so this tool highlights a copy-ready set within that limit." },
  { q: "Where do I put hashtags on YouTube?", a: "Add them in your video description or directly in the title. The first three hashtags in your description show as clickable links above the video title." },
  { q: "Is this YouTube hashtag generator free?", a: "Yes — it is free to use with no sign-up required. Enter a topic and get 30 grouped hashtags instantly." },
  { q: "What is the YouTube hashtag character limit?", a: "Each hashtag can be up to 60 characters, and hashtags cannot contain spaces. Keep them short and relevant for the best results." },
  { q: "Do YouTube hashtags actually help with views?", a: "Hashtags help YouTube understand and categorize your content and make it discoverable through hashtag pages and search. They work best combined with a strong title, description, and thumbnail." },
  { q: "Should I use trending or niche hashtags?", a: "Use a mix. Broad trending hashtags add reach but high competition; niche hashtags are less competitive and attract a more relevant audience. This tool gives you both, grouped clearly." },
  { q: "Will the same hashtags work in every country?", a: "Core topic hashtags work globally, but trends vary by region. Creators in the US, UK, India, Brazil, and Southeast Asia can edit the suggestions to match local trends and languages." },
  { q: "Can I use these hashtags for YouTube Shorts?", a: "Yes. Hashtags like #shorts plus 2–3 niche tags help Shorts get categorized. Add #shorts manually and pick relevant tags from the results." },
  { q: "Are hashtags the same as tags on YouTube?", a: "No. Hashtags (#example) appear publicly in the title or description. Tags are hidden keywords added in the upload settings. Both help discovery in different ways." },
  { q: "How often should I change my hashtags?", a: "Tailor hashtags to each video's topic rather than reusing the same set everywhere. Regenerate for every upload to stay relevant and avoid spam signals." },
];

export default function Page() {
  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "Free Tools", path: "/tools" },
      { name: "YouTube Hashtag Generator", path: PATH },
    ]),
    webApplicationLd({ name: "YouTube Hashtag Generator", description: DESC, path: PATH, category: "UtilitiesApplication" }),
    faqLd(FAQS),
  ];

  return (
    <div>
      <JsonLd data={jsonLd} />
      <ToolHero
        platform="YouTube"
        title="YouTube Hashtag Generator"
        subtitle="Turn any topic into 30 relevant YouTube hashtags — grouped into trending, niche, and broad reach, with one-click copy and YouTube's limits built in."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse
        steps={[
          { title: "Enter your topic", text: "Describe your video or channel niche in a few words.", icon: <PenLine className="size-4" /> },
          { title: "Generate", text: "Our AI returns 30 hashtags grouped by trending, niche, and broad reach.", icon: <Sparkles className="size-4" /> },
          { title: "Copy what fits", text: "Copy a single group or the copy-ready set within YouTube's 15-tag limit.", icon: <Copy className="size-4" /> },
          { title: "Add to your video", text: "Paste them into your description or title and publish.", icon: <Upload className="size-4" /> },
        ]}
      />

      <FAQSection faqs={FAQS} />

      <LongContent>
        <div>
          <h2>The free AI YouTube hashtag generator</h2>
          <p>
            Hashtags are one of the simplest ways to help YouTube understand what your video is about and surface it to the
            right viewers. But guessing which hashtags to use — and how many — wastes time and can even hurt you if you
            break YouTube&apos;s rules. This free YouTube hashtag generator uses AI to turn any topic into 30 relevant,
            ready-to-use hashtags, neatly grouped so you can build the perfect mix in seconds.
          </p>
        </div>

        <div>
          <h3>How many YouTube hashtags should you use?</h3>
          <p>
            YouTube lets you add up to <strong>15 hashtags</strong> per video. Add more than that and YouTube ignores
            every hashtag on the video, which is why staying under the limit matters. Only the <strong>first three</strong>
            hashtags appear as clickable links above your title, so put your most important, most specific tags first.
            Each hashtag can be up to 60 characters and cannot contain spaces.
          </p>
        </div>

        <div>
          <h3>Trending vs niche vs broad-reach hashtags</h3>
          <ul>
            <li><strong>Trending</strong> hashtags ride current momentum and add reach, but competition is high.</li>
            <li><strong>Niche-specific</strong> hashtags are less competitive and bring in a highly relevant audience that is more likely to subscribe.</li>
            <li><strong>Broad reach</strong> hashtags categorize your content within larger topics and connect it to related videos.</li>
          </ul>
          <p>
            The winning strategy is a balanced mix: a couple of broad tags for context, a few niche tags for relevance, and
            one or two trending tags when they genuinely fit your content. This tool separates them so you can pick
            deliberately instead of dumping a random list.
          </p>
        </div>

        <div>
          <h3>Do hashtags really help YouTube growth?</h3>
          <p>
            Hashtags are a discovery signal, not a magic switch. They help YouTube categorize your video, make it
            appear on hashtag landing pages, and reinforce the keywords in your title and description. Channels that pair
            relevant hashtags with a compelling thumbnail, a click-worthy title, and a keyword-rich description consistently
            outperform those that rely on any single tactic. Think of hashtags as one reinforcing layer in a complete SEO
            strategy.
          </p>
        </div>

        <div>
          <h3>Built for creators everywhere</h3>
          <p>
            Whether you publish in the United States, the United Kingdom, India, Brazil, Nigeria, the Philippines, or
            anywhere else, the core topic hashtags this tool produces are globally relevant. Trends differ by region and
            language, so treat the suggestions as a strong starting point and adjust for the local trends your audience
            follows. Because it is free and requires no account, you can regenerate fresh hashtags for every upload.
          </p>
        </div>

        <div>
          <h3>Part of a complete YouTube toolkit</h3>
          <p>
            Hashtags work best alongside great titles, descriptions, and thumbnails — all of which you can create with our
            other free tools. And when you are ready to research what is working at scale, Captapi&apos;s API gives you
            transcripts, comments, and engagement metrics from YouTube and other platforms in clean JSON, so your content
            decisions are driven by real data.
          </p>
        </div>
      </LongContent>

      <ToolCTA />
    </div>
  );
}
