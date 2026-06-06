import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Copy, Upload } from "lucide-react";

const PATH = "/tools/tiktok-hashtag-generator";
const TITLE = "Free TikTok Hashtag Generator — Viral & FYP Tags";
const DESC =
  "Generate 30 relevant TikTok hashtags from any topic, grouped into viral, niche, and FYP boosters. AI-powered, free, with a live character counter against TikTok's 2,200-character caption limit.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "tiktok hashtag generator",
    "viral tiktok hashtags",
    "best tiktok hashtags for views",
    "tiktok hashtags",
    "fyp hashtags",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "tiktok-hashtag-generator",
  submitLabel: "Generate hashtags",
  fields: [
    {
      name: "topic",
      label: "Video topic or niche",
      type: "text",
      required: true,
      placeholder: "e.g. easy 5-minute recipes",
      help: "Be specific for sharper hashtags.",
    },
  ],
};

const FAQS = [
  { q: "How many hashtags should I use on TikTok?", a: "TikTok works best with a focused set of 3–5 highly relevant hashtags rather than a long list. A tight mix of niche and broad tags helps the algorithm categorize your video without diluting the signal, so this tool gives you a copy-ready set you can trim to your favourites." },
  { q: "What is the TikTok caption character limit?", a: "TikTok captions can be up to 2,200 characters, and that count includes your hashtags, spaces, and emojis. Since most viewers only see the first line, keep your hook up front and place hashtags after it — this tool helps you build a caption that fits the budget." },
  { q: "Do #fyp and #foryou hashtags actually work?", a: "There is no evidence that #fyp, #foryou, or #foryoupage push a video onto the For You Page on their own. TikTok's recommendation system relies far more on watch time, rewatches, and engagement. They do no harm, but relevant topic hashtags do more to tell TikTok who should see your video." },
  { q: "Should I mix niche and broad hashtags?", a: "Yes. Broad hashtags add reach but face huge competition, while niche hashtags are less crowded and attract a more relevant, higher-converting audience. The winning approach is a balanced mix, which is why this tool groups suggestions into viral, niche, and FYP boosters." },
  { q: "Where do TikTok hashtags go?", a: "Hashtags go in your video caption, not in comments or a separate field. Add them after your hook so the caption still reads naturally. The full caption — text plus hashtags — must stay within the 2,200-character limit." },
  { q: "Can hashtags get my TikTok shadowbanned?", a: "Using banned, spammy, or misleading hashtags can suppress a video's reach or trigger moderation. Avoid hashtags unrelated to your content, anything tied to prohibited topics, and copy-pasting the same giant block on every post. Keep tags relevant and rotate them per video to stay safe." },
  { q: "Should I use hashtags for views or for niche targeting?", a: "It depends on your goal. High-volume viral hashtags chase reach but rarely convert, while specific niche hashtags reach fewer people who are far more likely to follow and engage. Most creators do best blending a few of each — broad for discovery, niche for retention." },
  { q: "Do hashtags affect the For You Page?", a: "Hashtags are one of several signals TikTok uses to understand and categorize your content, which can influence who sees it on the For You Page. They are a supporting factor, not the main driver — watch time, completion rate, shares, and comments carry far more weight." },
  { q: "Are trending sounds more important than hashtags?", a: "Often, yes. Using a trending sound that fits your video tends to boost reach more than hashtags alone because TikTok actively surfaces content built around rising audio. Pair a relevant trending sound with a tight set of hashtags for the strongest combination." },
  { q: "Do TikTok hashtags differ by region?", a: "Yes. Core topic hashtags translate everywhere, but trending tags vary by country and language. Creators in the US, UK, India, Brazil, Indonesia, and beyond should treat the suggestions as a starting point and swap in local trends their audience actually follows." },
];

export default function Page() {
  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "Free Tools", path: "/tools" },
      { name: "TikTok Hashtag Generator", path: PATH },
    ]),
    webApplicationLd({ name: "TikTok Hashtag Generator", description: DESC, path: PATH, category: "UtilitiesApplication" }),
    faqLd(FAQS),
  ];

  return (
    <div>
      <JsonLd data={jsonLd} />
      <ToolHero
        platform="TikTok"
        title="TikTok Hashtag Generator"
        subtitle="Turn any topic into 30 relevant TikTok hashtags — grouped into viral, niche, and FYP boosters, with a live character counter against TikTok's 2,200-character caption limit."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse
        steps={[
          { title: "Enter your topic", text: "Describe your video or niche in a few words.", icon: <PenLine className="size-4" /> },
          { title: "Generate", text: "Our AI returns 30 hashtags grouped into viral, niche, and FYP boosters.", icon: <Sparkles className="size-4" /> },
          { title: "Copy what fits", text: "Copy a single group or a tight set of 3–5 tags within the caption limit.", icon: <Copy className="size-4" /> },
          { title: "Add to your video", text: "Paste them into your caption after your hook and post.", icon: <Upload className="size-4" /> },
        ]}
      />

      <FAQSection faqs={FAQS} />

      <LongContent>
        <div>
          <h2>The free AI TikTok hashtag generator</h2>
          <p>
            Hashtags are one of the simplest ways to tell TikTok what your video is about and help it reach the right
            viewers on the For You Page. But stuffing in random tags wastes characters and can even hurt your reach. This
            free TikTok hashtag generator uses AI to turn any topic into 30 relevant, ready-to-use hashtags, grouped into
            viral, niche, and FYP boosters so you can build a sharp caption in seconds — with a live character counter
            keeping you inside TikTok&apos;s caption budget.
          </p>
        </div>

        <div>
          <h3>How TikTok&apos;s algorithm uses hashtags</h3>
          <p>
            TikTok&apos;s recommendation system decides who lands on the For You Page by weighing signals like watch time,
            rewatches, completion rate, shares, and comments. Hashtags are a supporting signal: they help TikTok
            understand and categorize your content so it can match your video to interested viewers. They are not a magic
            switch — a great hook, a trending sound, and content that holds attention matter far more — but relevant
            hashtags reinforce the topic and make your video easier to surface.
          </p>
        </div>

        <div>
          <h3>The right number of hashtags</h3>
          <p>
            More is not better on TikTok. A focused set of <strong>3–5 highly relevant hashtags</strong> usually
            outperforms a wall of tags, because a tight set sends a clear topic signal instead of diluting it. Cramming in
            twenty generic hashtags eats into your caption, looks spammy, and rarely improves reach. Pick the few tags that
            genuinely describe your video and skip the rest.
          </p>
        </div>

        <div>
          <h3>Viral vs niche vs FYP boosters</h3>
          <ul>
            <li><strong>Viral</strong> hashtags ride current momentum and add reach, but competition is enormous and your video can disappear fast.</li>
            <li><strong>Niche</strong> hashtags are less crowded and attract a highly relevant audience that is more likely to follow, comment, and rewatch.</li>
            <li><strong>FYP boosters</strong> like #fyp or #foryou are popular by habit; they do no harm but rarely move the needle on their own.</li>
          </ul>
          <p>
            The winning strategy is a balanced mix: a couple of niche tags for relevance, one or two broad tags for
            discovery, and an FYP tag only if it fits. This tool separates them clearly so you can choose deliberately
            instead of dumping a random list.
          </p>
        </div>

        <div>
          <h3>Your 2,200-character caption budget</h3>
          <p>
            TikTok captions allow up to <strong>2,200 characters</strong>, and that count includes your text, hashtags,
            spaces, and emojis. Most viewers only ever read the first line before it truncates, so lead with your hook and
            place hashtags afterwards. A live character counter — built into this tool — helps you stay within the limit
            while keeping the caption readable rather than buried under tags.
          </p>
        </div>

        <div>
          <h3>Common hashtag mistakes to avoid</h3>
          <p>
            The two biggest mistakes are using <strong>too many hashtags</strong> and using <strong>irrelevant ones</strong>.
            A long block of unrelated tags confuses the algorithm and can look like spam. Worse, leaning on banned or
            misleading hashtags risks a shadowban that quietly suppresses your reach. Avoid copy-pasting the same giant set
            onto every post — rotate tags to match each video, and keep every hashtag genuinely related to what viewers
            will watch.
          </p>
        </div>

        <div>
          <h3>Pair hashtags with trending sounds</h3>
          <p>
            On TikTok, audio is often a bigger lever than hashtags. Using a rising or trending sound that fits your video
            can boost reach because TikTok actively surfaces content built around popular audio. Treat hashtags and sounds
            as a team: a relevant trending sound to ride momentum, plus a tight set of hashtags to label the topic. Together
            they give the algorithm a clear, confident picture of your video.
          </p>
        </div>

        <div>
          <h3>Built for creators everywhere</h3>
          <p>
            Whether you post in the United States, the United Kingdom, India, Brazil, Indonesia, Nigeria, the Philippines,
            or anywhere else, the core topic hashtags this tool produces are globally relevant. Trends shift by region and
            language, so treat the suggestions as a strong starting point and swap in the local tags your audience actually
            follows. Because it is free and needs no account, you can regenerate fresh hashtags for every upload.
          </p>
        </div>

        <div>
          <h3>Part of a complete TikTok toolkit</h3>
          <p>
            Hashtags work best alongside scroll-stopping hooks, captions, and ideas — all of which you can create with our
            other free tools. And when you are ready to research what is working at scale, Captapi&apos;s API gives you
            transcripts, comments, and engagement metrics from TikTok and other platforms in clean JSON, so your content
            decisions are driven by real data instead of guesswork.
          </p>
        </div>
      </LongContent>

      <ToolCTA />
    </div>
  );
}
