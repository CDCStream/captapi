import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Copy, Film } from "lucide-react";

const PATH = "/tools/tiktok-video-idea-generator";
const TITLE = "Free TikTok Video Idea Generator";
const DESC =
  "Generate 8 fresh TikTok video ideas for your niche — each with a scroll-stopping hook, a clear concept, a suggested sound, and a virality score. AI-powered, free, and no sign-up required.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "tiktok video ideas",
    "what to post on tiktok",
    "tiktok content ideas",
    "tiktok ideas",
    "content ideas for tiktok",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "tiktok-video-idea-generator",
  submitLabel: "Generate ideas",
  fields: [
    {
      name: "niche",
      label: "Your niche",
      type: "select",
      required: true,
      options: [
        { value: "dance", label: "Dance" },
        { value: "comedy", label: "Comedy" },
        { value: "food", label: "Food" },
        { value: "fitness", label: "Fitness" },
        { value: "beauty", label: "Beauty" },
        { value: "education", label: "Education" },
        { value: "gaming", label: "Gaming" },
      ],
    },
    {
      name: "trendType",
      label: "Format / trend type",
      type: "select",
      options: [
        { value: "original", label: "Original" },
        { value: "duet", label: "Duet" },
        { value: "stitch", label: "Stitch" },
        { value: "transition", label: "Transition" },
        { value: "storytime", label: "Storytime" },
      ],
    },
  ],
};

const FAQS = [
  { q: "How often should I post on TikTok?", a: "TikTok itself has suggested posting 1–4 times per day, and many growing creators land somewhere between 1 and 3 posts daily. The honest answer is that consistency beats raw volume: a sustainable rhythm you can keep — even once a day — outperforms a burst of ten videos followed by a week of silence. Start with one quality post per day and scale up only if you can hold the quality." },
  { q: "Why does the first 3 seconds matter so much?", a: "The opening 3 seconds is your hook — it decides whether someone keeps watching or swipes away. Because TikTok measures watch time and completion rate, a weak intro tanks your video before the algorithm ever gives it a chance. Open with motion, a bold claim, a question, or a visual payoff teaser so viewers feel they have to stay to see what happens." },
  { q: "What do duet, stitch, transition, and storytime mean?", a: "A duet plays your video side-by-side with someone else's clip, great for reactions and collaborations. A stitch clips a few seconds of another video and lets you continue or respond to it. A transition uses a cut or effect on a beat to jump between scenes, outfits, or locations. A storytime is a first-person narrated story, usually with a hook promising a twist or payoff at the end." },
  { q: "How do I find trending sounds on TikTok?", a: "Open the TikTok Creative Center or the in-app sound library and sort by what's rising, watch your own For You feed for songs you hear repeatedly, and look for the small upward-arrow 'trending' label when adding audio. Saving sounds the moment you spot them gives you a ready-to-use bank, so you can publish while the trend is still climbing rather than after it peaks." },
  { q: "How does the For You Page decide what to show?", a: "The FYP is a recommendation engine that weighs signals like watch time, completion rate, rewatches, likes, comments, shares, and saves, alongside content signals such as captions, sounds, and hashtags. It tests your video on a small audience first; strong early signals earn wider distribution. Followers matter less than how compelling each individual video is, which is why small accounts can still go viral." },
  { q: "Should I stay in one niche or post about everything?", a: "Niche consistency helps TikTok learn who to show your videos to and helps viewers know why to follow you, which usually drives faster, stickier growth. That said, you can vary formats and angles within a niche to stay fresh. If you want to branch out widely, many creators run separate accounts so each one keeps a clear, trainable focus for the algorithm." },
  { q: "Is batch filming worth it?", a: "Yes — batching is one of the biggest time-savers for consistent posting. Setting up your lighting and outfit once and filming several videos in a single session removes the daily friction that causes creators to fall off. You can batch-film a week of ideas, then edit and schedule them, so a busy day never breaks your streak." },
  { q: "What is the ideal TikTok video length?", a: "There's no single perfect length — what matters is that the video stays engaging for its full duration. Short 7–15 second clips can rack up high completion rates and rewatches, while longer 30–60 second (or multi-minute) videos can earn more total watch time if the story holds. Match the length to the idea and cut anything that doesn't keep attention." },
  { q: "Can I repost TikToks to Reels and Shorts?", a: "Absolutely — repurposing the same idea to Instagram Reels and YouTube Shorts multiplies your reach with little extra work. For the best results, remove the visible TikTok watermark and re-export a clean version, since platforms can suppress competitor-watermarked uploads. Tweak the caption and hashtags for each platform to feel native rather than copy-pasted." },
  { q: "When are the best times to post across regions?", a: "Good general windows are weekday mornings, lunchtime, and evenings in your audience's local time zone — but your own analytics beat any generic chart. If your viewers span the US, Europe, India, and Southeast Asia, identify where most of your audience lives and post toward their peak hours. Test a few slots, check your follower-activity data, and double down on what performs." },
];

export default function Page() {
  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "Free Tools", path: "/tools" },
      { name: "TikTok Video Idea Generator", path: PATH },
    ]),
    webApplicationLd({ name: "TikTok Video Idea Generator", description: DESC, path: PATH, category: "MultimediaApplication" }),
    faqLd(FAQS),
  ];

  return (
    <div>
      <JsonLd data={jsonLd} />
      <ToolHero
        platform="TikTok"
        title="TikTok Video Idea Generator"
        subtitle="Beat creative block in seconds — get 8 tailored TikTok video ideas for your niche, each with a scroll-stopping hook, a clear concept, a suggested sound, and a virality score."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse
        steps={[
          { title: "Pick your niche", text: "Choose your content category and the format or trend type you want to make.", icon: <PenLine className="size-4" /> },
          { title: "Generate", text: "Our AI returns 8 video ideas, each with a hook, concept, sound, and virality score.", icon: <Sparkles className="size-4" /> },
          { title: "Copy your favorites", text: "Grab the hooks and concepts you love with one click and drop them into your plan.", icon: <Copy className="size-4" /> },
          { title: "Film and post", text: "Shoot, add the suggested sound, and publish while the trend is still climbing.", icon: <Film className="size-4" /> },
        ]}
      />

      <FAQSection faqs={FAQS} />

      <LongContent>
        <div>
          <h2>The free AI TikTok video idea generator</h2>
          <p>
            The hardest part of growing on TikTok is rarely the filming — it&apos;s staring at a blank screen wondering what
            to post next. Creative block is real, and it hits hardest right when you need to stay consistent. This free TikTok
            video idea generator turns that blank screen into 8 ready-to-shoot ideas for your niche, each one packaged with a
            scroll-stopping hook, a clear concept, a suggested sound, and a virality score so you know where to point your
            energy first. No sign-up, no cost — just refresh whenever inspiration runs dry.
          </p>
        </div>

        <div>
          <h3>The anatomy of a viral TikTok</h3>
          <p>
            Almost every video that takes off shares the same skeleton: a <strong>hook</strong>, a <strong>payoff</strong>,
            and a <strong>loop</strong>. The hook is the first 3 seconds — a bold claim, a question, motion, or a teaser of
            the result — and it exists to stop the swipe. The payoff is the promise you made in the hook actually delivered,
            which is what earns the watch time TikTok rewards. The loop is an ending that flows back into the beginning so
            viewers rewatch without realizing it, quietly stacking completion rate and replays. Every idea this tool produces
            is built around landing that hook fast and paying it off cleanly.
          </p>
        </div>

        <div>
          <h3>Formats explained: original, duet, stitch, transition, storytime</h3>
          <ul>
            <li><strong>Original</strong> — your own concept from scratch, the most flexible way to show personality.</li>
            <li><strong>Duet</strong> — your clip plays beside someone else&apos;s, ideal for reactions and collabs.</li>
            <li><strong>Stitch</strong> — you clip a few seconds of another video and continue or respond to it.</li>
            <li><strong>Transition</strong> — a beat-synced cut or effect that jumps between scenes, outfits, or locations.</li>
            <li><strong>Storytime</strong> — a narrated first-person story with a hook that promises a twist or payoff.</li>
          </ul>
          <p>
            Picking the right format for an idea is half the battle. A surprising opinion lands well as a storytime, a strong
            visual change shines as a transition, and a hot take begs for a stitch. Choose the format that frames your idea
            in its best light.
          </p>
        </div>

        <div>
          <h3>Using trends and sounds without being late</h3>
          <p>
            Trending sounds are rocket fuel — TikTok surfaces videos that ride momentum — but the window closes fast. The
            trick is to catch sounds on the way up, not after they&apos;ve peaked. Watch your For You feed for audio you keep
            hearing, browse the Creative Center for rising tracks, and save sounds the instant you spot them so you have a
            ready bank to pull from. Pair a climbing sound with one of your generated ideas and you get the best of both:
            original substance carried by a trend&apos;s reach.
          </p>
        </div>

        <div>
          <h3>Consistency and batching</h3>
          <p>
            Growth on TikTok is a compounding game, and consistency is the multiplier. TikTok has suggested posting 1–4 times
            a day, but the sustainable rhythm you can actually keep matters more than any number. This is where batching wins:
            set up your space once, film several ideas in a single session, then edit and schedule them across the week. A bank
            of pre-made videos means a hectic day never breaks your streak — and it frees your creative energy for the ideas
            themselves rather than the daily scramble.
          </p>
        </div>

        <div>
          <h3>Idea frameworks for every niche</h3>
          <p>
            Different niches reward different angles. <strong>Dance</strong> and <strong>comedy</strong> thrive on trends,
            transitions, and relatable timing. <strong>Food</strong> wins with satisfying close-ups, fast recipes, and
            curiosity-gap hooks. <strong>Fitness</strong> and <strong>beauty</strong> lean on before-and-after payoffs,
            quick tips, and myth-busting. <strong>Education</strong> performs with surprising facts and clear step-by-step
            value, while <strong>gaming</strong> lives on clutch moments, reactions, and behind-the-scenes commentary. The
            generator tailors its hooks and concepts to the niche you pick, so the ideas already speak your audience&apos;s
            language.
          </p>
        </div>

        <div>
          <h3>Built for creators everywhere</h3>
          <p>
            Whether you post from the United States, the United Kingdom, India, Brazil, Nigeria, Indonesia, or the
            Philippines, the idea frameworks here are globally relevant — strong hooks and clear payoffs work in every
            language. Trends and peak posting times shift by region, so treat the suggested sounds and concepts as a launchpad
            and adapt them to what&apos;s climbing for your local audience. Because the tool is free and needs no account,
            you can generate fresh ideas as often as you publish.
          </p>
        </div>

        <div>
          <h3>Part of a complete creator toolkit</h3>
          <p>
            Great ideas are step one — captions, hashtags, and cross-posting do the rest, and you can build those with our
            other free tools, then repurpose every winner to Instagram Reels and YouTube Shorts. And when you&apos;re ready to
            study what&apos;s actually working at scale, Captapi&apos;s API delivers transcripts, comments, and engagement
            metrics from TikTok and other platforms in clean JSON — so your next round of ideas is driven by real data, not
            guesswork.
          </p>
        </div>
      </LongContent>

      <ToolCTA />
    </div>
  );
}
