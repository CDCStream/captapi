import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Copy, Check } from "lucide-react";

const PATH = "/tools/youtube-name-generator";
const TITLE = "Free YouTube Name Generator - 15 Channel Name Ideas";
const DESC =
  "Generate 15 catchy YouTube channel name ideas from your niche with AI. Pick personal or business, choose a style, and copy a brandable name in seconds. Free, no sign-up.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "youtube name generator",
    "youtube channel name generator",
    "youtube channel name ideas",
    "channel name generator",
    "youtube username generator",
    "youtube name ideas",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "youtube-name-generator",
  submitLabel: "Generate channel names",
  fields: [
    {
      name: "niche",
      label: "Your channel topic or niche",
      type: "text",
      required: true,
      placeholder: "e.g. budget travel and van life",
      help: "Be specific for sharper ideas, e.g. beginner home cooking on a budget.",
    },
    {
      name: "accountType",
      label: "Account type",
      type: "select",
      options: [
        { value: "personal", label: "Personal / Creator" },
        { value: "business", label: "Business / Brand" },
      ],
    },
    {
      name: "style",
      label: "Style",
      type: "select",
      options: [
        { value: "brandable", label: "Brandable" },
        { value: "descriptive", label: "Descriptive" },
        { value: "catchy", label: "Catchy / Fun" },
        { value: "professional", label: "Professional" },
      ],
    },
    {
      name: "keywords",
      label: "Words to include (optional)",
      type: "text",
      placeholder: "e.g. your name, a keyword",
      help: "Leave blank to let the AI choose freely.",
    },
  ],
};

const FAQS = [
  { q: "How long can a YouTube channel name be?", a: "A YouTube channel name can be up to 50 characters long. Your handle (the @username under your name) can be 3 to 30 characters and may contain letters, numbers, underscores, periods, and hyphens. This tool keeps every channel name suggestion within the 50-character limit." },
  { q: "Can I change my YouTube channel name later?", a: "Yes. You can change your channel name in YouTube Studio settings, and changing the channel name no longer changes your Google account name. You can update it a couple of times within a short window, so it is still worth picking a name you will be happy with." },
  { q: "Is the YouTube name generator free?", a: "Yes. Generating channel name ideas here is completely free, with no account, email, or credit card required, and no limit on how many times you can regenerate fresh ideas." },
  { q: "What makes a good YouTube channel name?", a: "A good YouTube channel name is short, easy to say and spell, memorable, and hints at your niche or personality. Names that are searchable and brandable get typed into search and shared by word of mouth far more than random or hard-to-spell ones." },
  { q: "Should I use my real name or a brand name?", a: "Use your real name if you are building a personal creator brand, and a brand name if you are growing a business or themed channel. Many creators blend both, such as a first name plus their niche, so the name is personal but still descriptive." },
  { q: "How do I check if a channel name or handle is available?", a: "The display name does not have to be unique, but your @handle does. In YouTube Studio, open Customization then Basic info to set your handle; YouTube shows whether it is available. You can also visit youtube.com/@yourhandle to see if it is already taken." },
  { q: "Should my YouTube name match my other social platforms?", a: "Where possible, yes. Matching your name and handle across YouTube, Instagram, TikTok, and X makes you easier to find and tag and protects your brand. Check availability on every platform before you commit so you can stay consistent." },
  { q: "Will these names rank in YouTube search?", a: "A descriptive, keyword-aware name can help people who search your topic discover you, but content quality and consistency matter most. Choose a name that is brandable first and naturally hints at your niche, rather than stuffing it with keywords." },
];

export default function Page() {
  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "Free Tools", path: "/tools" },
      { name: "YouTube Name Generator", path: PATH },
    ]),
    webApplicationLd({ name: "YouTube Name Generator", description: DESC, path: PATH, category: "UtilitiesApplication" }),
    faqLd(FAQS),
  ];

  return (
    <div>
      <JsonLd data={jsonLd} />
      <ToolHero
        platform="YouTube"
        title="YouTube Name Generator"
        subtitle="Turn your niche into 15 catchy, brandable YouTube channel name ideas, tuned to personal or business and your chosen style, with one-click copy and no sign-up."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse
        steps={[
          { title: "Describe your channel", text: "Enter your niche, topic, or the kind of videos you make.", icon: <PenLine className="size-4" /> },
          { title: "Pick type and style", text: "Choose personal or business and the naming style, then generate.", icon: <Sparkles className="size-4" /> },
          { title: "Copy your favorite", text: "Copy any of the 15 ideas with a single click.", icon: <Copy className="size-4" /> },
          { title: "Check and claim", text: "Confirm the handle is available on YouTube and set your name.", icon: <Check className="size-4" /> },
        ]}
      />

      <FAQSection faqs={FAQS} />

      <LongContent>
        <div>
          <h2>The free AI YouTube name generator</h2>
          <p>
            Your channel name is the first thing viewers see in search, on your videos, and in every recommendation. A great
            one is short, memorable, and instantly hints at what you make, but coming up with it from a blank page is hard,
            and every good idea can feel taken. This free YouTube name generator uses AI to turn your niche into 15 catchy,
            brandable channel name ideas, tuned to whether you are a creator or a business and to the style you choose, all
            within YouTube&apos;s 50-character limit.
          </p>
        </div>

        <div>
          <h3>Why your YouTube channel name matters</h3>
          <p>
            On YouTube, your name is part branding and part discovery. Viewers type names into search, so a clear,
            niche-aware name helps the right audience find you, while a memorable one gets shared by word of mouth and
            recommended alongside similar channels. Your name also follows you across collaborations, shoutouts, and other
            platforms, so it quietly shapes how professional and trustworthy your channel looks. Choosing well early saves
            you from rebranding later and from confusing the audience that already knows you.
          </p>
        </div>

        <div>
          <h3>YouTube name and handle rules</h3>
          <ul>
            <li>Channel names can be up to <strong>50 characters</strong> and may include spaces.</li>
            <li>Your <strong>@handle</strong> is 3 to 30 characters and uses letters, numbers, underscores, periods, or hyphens.</li>
            <li>The display name does not need to be unique, but the <strong>handle does</strong>.</li>
            <li>You can update your name in YouTube Studio, so you are not locked in forever.</li>
          </ul>
          <p>
            Every name this tool produces stays within the 50-character channel-name limit, so you can focus on choosing a
            favorite instead of trimming names that are too long.
          </p>
        </div>

        <div>
          <h3>Naming strategies by style</h3>
          <ul>
            <li><strong>Brandable</strong>: short, coined, or evocative words that are easy to trademark and own, like a real brand name.</li>
            <li><strong>Descriptive</strong>: names that say exactly what the channel is about, great for search and clarity.</li>
            <li><strong>Catchy / Fun</strong>: playful, punny, or rhythmic names that are easy to remember and fun to say.</li>
            <li><strong>Professional</strong>: clean, credible names that suit a business, expert, or educational channel.</li>
          </ul>
          <p>
            Pick the style that matches your content and audience, and the generator leans the whole set in that direction
            so your name feels intentional rather than random.
          </p>
        </div>

        <div>
          <h3>Personal channel vs business channel</h3>
          <p>
            If you are building a personal brand, names that include or play on your own name help viewers connect with you
            as a creator. If you are growing a business or a themed content brand, a clean brand-style name keeps you
            consistent across your website and social platforms and is easier to scale beyond a single person. The tool
            adjusts its suggestions based on whether you choose personal or business, so the ideas fit your goal.
          </p>
        </div>

        <div>
          <h3>Stay consistent across platforms</h3>
          <p>
            The strongest creator brands use the same name everywhere. Matching your YouTube name and handle with Instagram,
            TikTok, and X makes you easy to find, tag, and remember, and protects your name from being claimed by someone
            else. Before you commit, check availability on every platform you plan to use. If your exact name is taken on
            one, a small consistent tweak is better than a totally different name on each app.
          </p>
        </div>

        <div>
          <h3>Mistakes to avoid</h3>
          <p>
            Skip names that are hard to spell, full of random numbers, or so long they get cut off in search results. Avoid
            inside jokes that mean nothing to new viewers, and be careful not to box yourself into one narrow trend you may
            outgrow. Steer clear of names that are too close to existing brands or other channels, which can cause confusion
            and trademark problems down the line.
          </p>
        </div>

        <div>
          <h3>Built for creators everywhere</h3>
          <p>
            Whether you create from the United States, the United Kingdom, India, Brazil, Indonesia, or the Philippines, the
            ideas this tool generates are built to travel. Short, easy-to-say names cross language barriers and get shared
            globally. Because it is free and needs no account, you can regenerate fresh ideas as many times as you like
            until a name clicks.
          </p>
        </div>

        <div>
          <h3>Part of a complete creator toolkit</h3>
          <p>
            A great channel name works best alongside great titles, descriptions, and thumbnails you can craft with our
            other free tools. And when you are ready to research what is working at scale, Captapi&apos;s API gives you
            transcripts, comments, and engagement metrics from YouTube and other platforms in clean JSON, so your content
            and growth decisions are driven by real data instead of guesswork.
          </p>
        </div>
      </LongContent>

      <ToolCTA />
    </div>
  );
}
