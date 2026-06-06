import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Copy, Clapperboard } from "lucide-react";

const PATH = "/tools/youtube-shorts-idea-generator";
const TITLE = "Free YouTube Shorts Idea Generator";
const DESC =
  "Get 8 scroll-stopping YouTube Shorts ideas tailored to your niche — each with a 2-second hook, a 60-second script outline, and retention tips. AI-powered, free, no sign-up.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "youtube shorts ideas",
    "short video ideas",
    "youtube shorts topics",
    "shorts content ideas",
    "what to post on youtube shorts",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "youtube-shorts-idea-generator",
  submitLabel: "Generate Shorts ideas",
  fields: [
    {
      name: "niche",
      label: "Channel niche",
      type: "text",
      required: true,
      placeholder: "e.g. personal finance",
      help: "Be specific for sharper ideas — e.g. \u201cbudgeting tips for students\u201d.",
    },
    {
      name: "subs",
      label: "Subscriber count",
      type: "select",
      options: [
        { value: "0-1K", label: "0 – 1K" },
        { value: "1K-10K", label: "1K – 10K" },
        { value: "10K-100K", label: "10K – 100K" },
        { value: "100K+", label: "100K+" },
      ],
    },
    {
      name: "format",
      label: "Format",
      type: "select",
      options: [
        { value: "tutorial", label: "Tutorial" },
        { value: "reaction", label: "Reaction" },
        { value: "facts", label: "Facts" },
        { value: "storytelling", label: "Storytelling" },
        { value: "challenge", label: "Challenge" },
      ],
    },
  ],
};

const FAQS = [
  { q: "What is the best length for a YouTube Short?", a: "Shorts can now be up to 3 minutes long, but the sweet spot for most viral Shorts is still 15–60 seconds. Shorter clips are easier to watch fully, and high completion rates are one of the strongest signals the Shorts feed rewards." },
  { q: "How important is the first 2 seconds of a Short?", a: "It is everything. Viewers decide to keep watching or swipe within the first 2 seconds, so open with a bold visual, a surprising claim, or a clear promise of what they will get. A weak hook means low retention, and low retention means limited reach." },
  { q: "How often should I post YouTube Shorts?", a: "Consistency beats volume, but Shorts reward frequency more than long-form. Aim for at least 3–5 Shorts per week if you can sustain the quality. Daily posting can accelerate growth early on, as long as each Short still has a strong hook and a reason to watch." },
  { q: "Do YouTube Shorts actually grow a channel?", a: "Yes — Shorts are currently the fastest way to put your content in front of new viewers because the feed pushes videos to people who do not subscribe yet. The key is converting those views into subscribers with a clear niche, a channel that delivers on its promise, and pinned or linked long-form content." },
  { q: "Should I make Shorts or long-form videos?", a: "Do both if you can. Shorts are unmatched for reach and discovery, while long-form builds deeper loyalty, watch time, and ad revenue. A strong strategy is to use Shorts as the top of the funnel to attract viewers, then guide them to long-form videos that turn them into fans." },
  { q: "How does the YouTube Shorts algorithm pick what to show?", a: "The Shorts feed tests each video with a small audience and watches how people respond. Strong watch-through, rewatches, likes, comments, and shares tell YouTube to show it to more people. Unlike long-form, subscriber count matters less, so a brand-new channel can still go viral on a single great Short." },
  { q: "Does the music or sound I use matter?", a: "Yes. Trending sounds can give a Short an early discovery boost, and clear, well-mixed audio improves retention. Pick sounds that fit your niche rather than chasing every trend, and make sure any voiceover is easy to hear on a phone speaker." },
  { q: "When is the best time to post Shorts for a global audience?", a: "Post when your specific audience is most active, which you can find in YouTube Analytics. If your viewers span multiple time zones — for example the US, UK, and India — schedule around the overlap of their peak hours, or simply post consistently and let the feed distribute the video over the following days." },
  { q: "Do hashtags like #shorts still help?", a: "Adding #shorts and a couple of relevant niche hashtags helps YouTube categorize your video, but it will not save weak content. Treat hashtags as a small bonus and put your energy into the hook, retention, and a satisfying loop or payoff." },
  { q: "Can I repurpose my Shorts for TikTok and Reels?", a: "Absolutely — vertical short-form content travels well across platforms. Export without the watermark, adjust the caption and hashtags for each app, and re-upload. Repurposing multiplies your reach for almost no extra effort, which is why most successful creators publish the same clip everywhere." },
];

export default function Page() {
  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "Free Tools", path: "/tools" },
      { name: "YouTube Shorts Idea Generator", path: PATH },
    ]),
    webApplicationLd({ name: "YouTube Shorts Idea Generator", description: DESC, path: PATH, category: "UtilitiesApplication" }),
    faqLd(FAQS),
  ];

  return (
    <div>
      <JsonLd data={jsonLd} />
      <ToolHero
        platform="YouTube"
        title="YouTube Shorts Idea Generator"
        subtitle="Turn your niche into 8 ready-to-film YouTube Shorts ideas — each with a scroll-stopping hook, a 60-second script outline, and retention tips built in."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse
        steps={[
          { title: "Describe your channel", text: "Enter your niche, subscriber range, and the format you want to make.", icon: <PenLine className="size-4" /> },
          { title: "Generate ideas", text: "Our AI returns 8 Shorts ideas with hooks and 60-second outlines.", icon: <Sparkles className="size-4" /> },
          { title: "Pick and film", text: "Choose the ideas that fit your style and shoot them on your phone.", icon: <Clapperboard className="size-4" /> },
          { title: "Copy and publish", text: "Copy any idea or outline, add #shorts, and post to your channel.", icon: <Copy className="size-4" /> },
        ]}
      />

      <FAQSection faqs={FAQS} />

      <LongContent>
        <div>
          <h2>The free AI YouTube Shorts idea generator</h2>
          <p>
            The hardest part of posting Shorts consistently is not filming — it is deciding what to film. Staring at a
            blank screen kills momentum, and momentum is exactly what the Shorts feed rewards. This free YouTube Shorts
            idea generator turns your niche, audience size, and preferred format into 8 ready-to-film ideas, each with a
            scroll-stopping hook and a 60-second script outline, so you can go from idea to upload in minutes instead of
            hours.
          </p>
        </div>

        <div>
          <h3>Why Shorts are the fastest growth lever on YouTube</h3>
          <p>
            Long-form video rewards channels that already have an audience, but the Shorts feed is built to surface
            content from creators viewers have never heard of. That makes Shorts the single fastest way to reach new
            people right now. A first-time uploader can land on millions of For You feeds with one great clip, because
            the algorithm cares far more about how people respond to the video than about how many subscribers you have.
            Used well, Shorts become the top of your funnel — pulling in strangers and converting the best of them into
            subscribers and long-form viewers.
          </p>
        </div>

        <div>
          <h3>Anatomy of a viral Short</h3>
          <p>
            Almost every breakout Short shares the same three ingredients. Nail these and the rest is refinement:
          </p>
          <ul>
            <li><strong>The hook</strong> — the first 2 seconds. A bold claim, a striking visual, or a clear promise that stops the swipe and tells viewers exactly why they should stay.</li>
            <li><strong>Retention</strong> — the middle. Keep every second earning its place with quick cuts, on-screen text, and no filler. If a moment does not add value, cut it.</li>
            <li><strong>The loop or payoff</strong> — the end. Either deliver a satisfying conclusion or loop seamlessly back to the opening so the video replays, which quietly doubles your watch time.</li>
          </ul>
        </div>

        <div>
          <h3>How the Shorts algorithm works</h3>
          <p>
            The Shorts feed is a testing machine. Every upload gets shown to a small sample, and YouTube measures
            watch-through rate, rewatches, likes, comments, and shares. Strong signals earn a bigger audience; weak
            signals quietly cap the reach. Because the system optimizes for engagement rather than subscriber count,
            quality and retention matter more than your channel size. The practical takeaway: obsess over your hook and
            your completion rate, and let the feed do the distribution.
          </p>
        </div>

        <div>
          <h3>Idea frameworks for every format</h3>
          <p>
            Different formats demand different structures, which is why this tool tailors ideas to the format you choose:
          </p>
          <ul>
            <li><strong>Tutorials</strong> — promise a specific result in the hook, then deliver the steps fast with text overlays.</li>
            <li><strong>Reactions</strong> — lead with the most surprising moment, then react with genuine, high-energy commentary.</li>
            <li><strong>Facts</strong> — open with the most counterintuitive fact first, then stack the rest to keep viewers watching.</li>
            <li><strong>Storytelling</strong> — start in the middle of the action, build tension, and resolve it before the swipe.</li>
            <li><strong>Challenges</strong> — state the stakes immediately so viewers stay to see whether you succeed or fail.</li>
          </ul>
        </div>

        <div>
          <h3>Posting cadence and retention tips</h3>
          <p>
            Consistency compounds. Posting 3–5 strong Shorts a week trains both the algorithm and your audience to expect
            you, and gives you more shots at a breakout. To protect retention, keep most Shorts in the 15–60 second range,
            front-load the value, add captions for sound-off viewing, and end on a clean loop. Resist the urge to pad a
            video to hit a length — a tight 20-second Short with 90% completion will almost always outperform a loose
            60-second one that people abandon halfway through.
          </p>
        </div>

        <div>
          <h3>Built for creators everywhere</h3>
          <p>
            Whether you publish from the United States, the United Kingdom, India, Brazil, Nigeria, the Philippines, or
            anywhere else, short vertical video travels across cultures and languages better than almost any other format.
            Post when your own audience is most active — you can find this in YouTube Analytics — and if your viewers span
            several time zones, aim for the overlap of their peak hours or simply post consistently and let the feed
            spread the video over the following days. Because this tool is free and needs no account, you can generate a
            fresh batch of ideas for every upload.
          </p>
        </div>

        <div>
          <h3>Part of a complete YouTube toolkit</h3>
          <p>
            Great ideas go further when they are paired with strong titles, descriptions, hashtags, and thumbnails — all
            of which you can create with our other free tools. And once you are ready to study what is actually working at
            scale, Captapi&apos;s API gives you transcripts, comments, and engagement metrics from YouTube and other
            platforms in clean JSON, so your next Short is informed by real data instead of guesswork.
          </p>
        </div>
      </LongContent>

      <ToolCTA />
    </div>
  );
}
