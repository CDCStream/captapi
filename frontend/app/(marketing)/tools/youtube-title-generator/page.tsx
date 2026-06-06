import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Gauge, Copy } from "lucide-react";

const PATH = "/tools/youtube-title-generator";
const TITLE = "Free YouTube Title Generator — 10 Catchy Titles";
const DESC =
  "Generate 10 catchy, CTR-scored YouTube titles from any topic in seconds. Pick a style — clickbait, how-to, or listicle — stay within the 100-character limit, and copy the best. Free, no sign-up.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "youtube title generator",
    "catchy youtube titles",
    "youtube video title ideas",
    "youtube title ideas",
    "best youtube titles",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "youtube-title-generator",
  submitLabel: "Generate titles",
  fields: [
    {
      name: "topic",
      label: "Video topic",
      type: "text",
      required: true,
      placeholder: "e.g. how to save money on groceries",
      help: "Describe what your video is about — the more specific, the sharper the titles.",
    },
    {
      name: "audience",
      label: "Target audience",
      type: "text",
      placeholder: "e.g. college students",
    },
    {
      name: "style",
      label: "Title style",
      type: "select",
      options: [
        { value: "Clickbait", label: "Clickbait" },
        { value: "Educational", label: "Educational" },
        { value: "Story-telling", label: "Story-telling" },
        { value: "How-to", label: "How-to" },
        { value: "Listicle", label: "Listicle" },
        { value: "Mixed", label: "Mixed" },
      ],
    },
  ],
};

const FAQS = [
  { q: "How long should a YouTube title be?", a: "Aim for around 60 characters so the title is not cut off in search and suggested feeds, even though YouTube allows up to 100 characters. The first 60 or so characters are what most viewers actually see, so front-load the words that matter most." },
  { q: "How do I write a YouTube title that boosts CTR?", a: "Lead with a clear benefit or curiosity gap, use specific numbers or outcomes, and match the promise to your thumbnail. This generator scores each title for click-through potential so you can pick the strongest option instead of guessing." },
  { q: "Why should I front-load keywords in my title?", a: "YouTube and Google read the start of your title most heavily, and viewers scan left to right. Putting your main keyword near the front helps search ranking and makes the topic obvious before the title gets truncated on small screens." },
  { q: "Is clickbait or an honest title better?", a: "Curiosity works, but the title must deliver what it promises or viewers bounce and watch time drops. The best approach is an honest, irresistible title — strong hook, real payoff. Try the Clickbait and Educational styles and compare which fits your content." },
  { q: "Should I use emojis, numbers, and power words in titles?", a: "Numbers (\u201c7 ways\u201d, \u201cin 5 minutes\u201d) and power words (proven, easy, ultimate) reliably lift clicks. Emojis can help a title stand out but use one at most and avoid them if they look spammy for your niche. The generator weaves these in naturally." },
  { q: "Can I A/B test my YouTube titles?", a: "Yes. YouTube Studio offers Test & Compare for thumbnails and titles, and you can also manually swap a title after 48–72 hours if CTR is low. Generate several variations here, launch with the highest-scoring one, then test alternatives." },
  { q: "Do YouTube titles affect search rankings?", a: "Absolutely. Your title is one of the strongest relevance signals YouTube uses to match videos to searches, alongside the description, tags, and watch time. A keyword-rich, accurate title helps you rank for the terms people actually type." },
  { q: "How do titles get truncated on mobile?", a: "On phones — where most YouTube watching happens in the US, India, Brazil, and Southeast Asia — titles often cut off after roughly 40–60 characters. Keep the hook and keyword early so the message survives truncation on smaller screens." },
  { q: "Will these titles work for a global audience?", a: "Yes. The core formulas — curiosity, clarity, numbers, and benefit — translate across markets like the US, UK, India, Brazil, Nigeria, and the Philippines. Edit wording to match local language and slang, but the title structure stays effective worldwide." },
  { q: "Is this YouTube title generator free?", a: "Yes — it is completely free with no sign-up required. Enter your topic, optionally add an audience and style, and get 10 catchy, CTR-scored titles within YouTube's 100-character limit instantly." },
];

export default function Page() {
  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "Free Tools", path: "/tools" },
      { name: "YouTube Title Generator", path: PATH },
    ]),
    webApplicationLd({ name: "YouTube Title Generator", description: DESC, path: PATH, category: "UtilitiesApplication" }),
    faqLd(FAQS),
  ];

  return (
    <div>
      <JsonLd data={jsonLd} />
      <ToolHero
        platform="YouTube"
        title="YouTube Title Generator"
        subtitle="Turn any topic into 10 catchy, CTR-scored YouTube titles — choose a style, stay within the 100-character limit, and copy the one most likely to win the click."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse
        steps={[
          { title: "Describe your video", text: "Enter your video topic and, optionally, who it is for.", icon: <PenLine className="size-4" /> },
          { title: "Pick a style", text: "Choose clickbait, how-to, listicle, story-telling, or mixed.", icon: <Sparkles className="size-4" /> },
          { title: "Compare CTR scores", text: "Our AI returns 10 titles scored for click-through potential.", icon: <Gauge className="size-4" /> },
          { title: "Copy the winner", text: "One-click copy your favorite and paste it onto your video.", icon: <Copy className="size-4" /> },
        ]}
      />

      <FAQSection faqs={FAQS} />

      <LongContent>
        <div>
          <h2>The free AI YouTube title generator</h2>
          <p>
            Your title is the single most important piece of text on your video. Before anyone watches a second, they read
            your title and glance at your thumbnail and decide — in a fraction of a second — whether to click. A weak title
            buries great content; a sharp one can double your views. This free YouTube title generator uses AI to turn any
            topic into 10 catchy, CTR-scored titles, so you can stop staring at a blinking cursor and start publishing
            videos people actually click.
          </p>
        </div>

        <div>
          <h3>Why titles drive your click-through rate</h3>
          <p>
            Click-through rate (CTR) is the percentage of people who click your video after seeing it in search,
            suggested, or the home feed. YouTube watches CTR closely: a video that earns clicks gets shown to more people,
            which compounds into more views, subscribers, and watch time. Your title and thumbnail are the two levers that
            control CTR, and the title is the one you can rewrite in seconds. That is why testing several title variations
            is one of the highest-leverage things any creator can do.
          </p>
        </div>

        <div>
          <h3>Anatomy of a high-CTR title</h3>
          <ul>
            <li><strong>A hook</strong> — curiosity, a bold claim, or a clear promise in the first few words.</li>
            <li><strong>A keyword</strong> — the phrase your audience actually searches for, placed near the front.</li>
            <li><strong>Specificity</strong> — numbers, timeframes, and concrete outcomes (&ldquo;in 7 days&rdquo;, &ldquo;$0 budget&rdquo;).</li>
            <li><strong>A power word</strong> — proven, easy, ultimate, secret, or fast to add emotional pull.</li>
            <li><strong>A payoff</strong> — a promise your video and thumbnail genuinely deliver.</li>
          </ul>
          <p>
            The best titles combine these without feeling stuffed. The generator scores each option so you can see which
            blend of curiosity and clarity is likely to perform best for your topic.
          </p>
        </div>

        <div>
          <h3>Title length and truncation</h3>
          <p>
            YouTube allows up to <strong>100 characters</strong>, but only about the first <strong>60</strong> reliably
            show in search and suggested videos — and on mobile, titles can cut off even earlier, around 40–60 characters.
            Since most viewing happens on phones, front-load your hook and keyword so the message survives truncation.
            Treat the extra characters as a bonus for keyword coverage, not as room for your main promise.
          </p>
        </div>

        <div>
          <h3>Title styles explained</h3>
          <ul>
            <li><strong>Clickbait</strong> — maximum curiosity and bold claims; powerful, but only if your video delivers.</li>
            <li><strong>Educational</strong> — clear, keyword-rich titles ideal for search and how-to content.</li>
            <li><strong>Story-telling</strong> — personal, narrative hooks (&ldquo;I tried X for 30 days&rdquo;) that build connection.</li>
            <li><strong>How-to</strong> — direct, instructional titles that promise a specific result or skill.</li>
            <li><strong>Listicle</strong> — numbered formats (&ldquo;10 tips for…&rdquo;) that set clear expectations.</li>
            <li><strong>Mixed</strong> — a spread of styles so you can compare angles in one batch.</li>
          </ul>
        </div>

        <div>
          <h3>Common title mistakes to avoid</h3>
          <ul>
            <li>Writing for yourself instead of your viewer — keep it about their benefit or curiosity.</li>
            <li>Burying the keyword at the end where search and viewers never see it.</li>
            <li>Over-promising with clickbait the video cannot back up, which kills retention.</li>
            <li>Going ALL CAPS or stacking emojis until the title reads as spam.</li>
            <li>Making it too long, vague, or generic to stand out in a crowded feed.</li>
          </ul>
        </div>

        <div>
          <h3>Pair your title with the right thumbnail</h3>
          <p>
            A title and thumbnail are a team — they should never repeat the same words but should reinforce the same
            promise. If your thumbnail shows the result, your title can add the curiosity, and vice versa. Test them
            together: YouTube Studio&apos;s Test &amp; Compare lets you trial thumbnails, and you can swap titles manually
            if CTR lags after a couple of days. Generate several variations here and launch with the highest-scoring
            combination.
          </p>
        </div>

        <div>
          <h3>Built for creators everywhere</h3>
          <p>
            Whether you publish in the United States, the United Kingdom, India, Brazil, Nigeria, the Philippines, or
            anywhere across Southeast Asia, the formulas that drive clicks — curiosity, clarity, numbers, and benefit —
            work across languages and markets. Use the generated titles as a strong starting point, then tune the wording
            and slang for your local audience. Because the tool is free and needs no account, you can generate fresh
            titles for every upload.
          </p>
        </div>

        <div>
          <h3>Part of a complete YouTube toolkit</h3>
          <p>
            Great titles work best alongside relevant hashtags, keyword-rich descriptions, and click-worthy thumbnails —
            all of which you can create with our other free tools. And when you are ready to research what is working at
            scale, Captapi&apos;s API gives you transcripts, comments, and engagement metrics from YouTube and other
            platforms in clean JSON, so your titles and content decisions are driven by real data rather than guesswork.
          </p>
        </div>
      </LongContent>

      <ToolCTA />
    </div>
  );
}
