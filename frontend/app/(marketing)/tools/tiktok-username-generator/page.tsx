import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Copy, Check } from "lucide-react";

const PATH = "/tools/tiktok-username-generator";
const TITLE = "Free TikTok Username Generator — 15 Name Ideas";
const DESC =
  "Generate 15 catchy TikTok username ideas by vibe — aesthetic, funny, edgy, or cute — all within TikTok's 24-character limit. AI-powered, free, with one-click copy and no sign-up.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "tiktok username generator",
    "tiktok name ideas",
    "aesthetic tiktok usernames",
    "tiktok username ideas",
    "cute tiktok usernames",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "tiktok-username-generator",
  submitLabel: "Generate usernames",
  fields: [
    {
      name: "interest",
      label: "Your interest or niche",
      type: "text",
      required: true,
      placeholder: "e.g. skincare and beauty",
      help: "Be specific for sharper ideas — e.g. \u201cclean girl skincare routines\u201d.",
    },
    {
      name: "style",
      label: "Vibe",
      type: "select",
      options: [
        { value: "aesthetic", label: "Aesthetic" },
        { value: "funny", label: "Funny" },
        { value: "edgy", label: "Edgy" },
        { value: "cute", label: "Cute" },
      ],
    },
  ],
};

const FAQS = [
  { q: "How long can a TikTok username be?", a: "A TikTok username can be up to 24 characters long. Your display name — the bolder name shown above your handle — can be up to 30 characters. This tool keeps every suggestion within the 24-character handle limit so you can register it directly." },
  { q: "What characters are allowed in a TikTok username?", a: "TikTok usernames can only contain letters, numbers, underscores, and periods. Spaces and most special symbols are not allowed, and a username cannot start or end with a period or contain consecutive periods. Display names are more flexible and can include spaces and emoji." },
  { q: "How often can I change my TikTok username?", a: "TikTok lets you change your username once every 30 days. Because of this cooldown, it is worth picking a name you will be happy with for a while — check availability and say it out loud before you commit." },
  { q: "How do I check if a TikTok username is available?", a: "Open TikTok, go to Edit profile, and type the username — TikTok shows a green check if it is free and a warning if it is taken. You can also visit tiktok.com/@username in a browser; a 'couldn't find this account' page usually means it is available." },
  { q: "What makes a good TikTok username?", a: "A good TikTok username is short, easy to say, easy to spell, and hints at your niche or personality. Avoid hard-to-remember number strings and random symbols. Memorable, brandable handles get typed into search and shared by word of mouth far more often." },
  { q: "Should I use my real name or a brand name?", a: "Use your real name if you are building a personal brand or creator identity, and a brand name if you are growing a business, product, or themed page. Many creators blend both — like a first name plus their niche — so the handle is personal but still searchable." },
  { q: "Should I use periods or underscores in my username?", a: "Both are allowed and purely stylistic. Periods (jane.skincare) tend to look cleaner and more aesthetic, while underscores (jane_skincare) are a classic separator. Pick one style and keep it consistent so people can find and tag you easily." },
  { q: "Should my TikTok username match my other platforms?", a: "Yes, where possible. Matching handles across TikTok, Instagram, YouTube, and X makes you easier to find and tag, and protects your brand. Before locking in a name, check availability on every platform you plan to use so you can stay consistent." },
  { q: "What are popular aesthetic TikTok username trends?", a: "Aesthetic handles often pair soft, dreamy words — like luxe, angel, soft, dusk, or bloom — with a name or niche, separated by a period. Lowercase styling and short, airy words feel current. This tool leans into those trends when you pick the Aesthetic vibe." },
  { q: "Why should I avoid numbers that look spammy?", a: "Long or random number strings (like user284910) look auto-generated, are hard to remember, and can read as spam or a bot account. If you need numbers, keep them meaningful and minimal — a birth year or lucky number — rather than filler digits added just to claim a taken name." },
];

export default function Page() {
  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "Free Tools", path: "/tools" },
      { name: "TikTok Username Generator", path: PATH },
    ]),
    webApplicationLd({ name: "TikTok Username Generator", description: DESC, path: PATH, category: "UtilitiesApplication" }),
    faqLd(FAQS),
  ];

  return (
    <div>
      <JsonLd data={jsonLd} />
      <ToolHero
        platform="TikTok"
        title="TikTok Username Generator"
        subtitle="Turn your interest into 15 catchy TikTok username ideas — tuned to your vibe, kept within TikTok's 24-character limit, with one-click copy and no sign-up."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse
        steps={[
          { title: "Enter your niche", text: "Describe your interest, content, or personality in a few words.", icon: <PenLine className="size-4" /> },
          { title: "Pick a vibe", text: "Choose aesthetic, funny, edgy, or cute, then generate.", icon: <Sparkles className="size-4" /> },
          { title: "Copy your favorite", text: "Copy any of the 15 ideas with a single click.", icon: <Copy className="size-4" /> },
          { title: "Check and claim", text: "Confirm it is available in TikTok and set it as your handle.", icon: <Check className="size-4" /> },
        ]}
      />

      <FAQSection faqs={FAQS} />

      <LongContent>
        <div>
          <h2>The free AI TikTok username generator</h2>
          <p>
            Your TikTok username is the first thing people see, the link they share, and the handle they tag in duets and
            comments. A great one is short, memorable, and instantly says what your page is about — but staring at a blank
            field while every good name feels taken is frustrating. This free TikTok username generator uses AI to turn any
            interest into 15 catchy, on-brand handle ideas, tuned to the vibe you choose and kept within TikTok&apos;s
            24-character limit so you can register them straight away.
          </p>
        </div>

        <div>
          <h3>Why your TikTok username matters</h3>
          <p>
            On TikTok, your username is part branding and part search. People type names into the search bar, and a clear,
            keyword-friendly handle helps the right viewers find you, while a memorable one gets shared by word of mouth.
            Your handle also follows you across collabs, shoutouts, and other platforms, so it quietly shapes how
            professional and trustworthy your account looks. Choosing well early saves you from rebranding later — and from
            losing the audience that already knows you by name.
          </p>
        </div>

        <div>
          <h3>TikTok username rules and limits</h3>
          <ul>
            <li>Usernames can be up to <strong>24 characters</strong>; display names up to <strong>30</strong>.</li>
            <li>Only <strong>letters, numbers, underscores, and periods</strong> are allowed — no spaces or special symbols.</li>
            <li>A username can&apos;t start or end with a period, and can&apos;t use two periods in a row.</li>
            <li>You can change your username <strong>once every 30 days</strong>, so choose deliberately.</li>
          </ul>
          <p>
            Every suggestion this tool produces respects these rules, so you spend your time choosing a favorite instead of
            fixing invalid characters or trimming names that are too long.
          </p>
        </div>

        <div>
          <h3>Naming strategies by vibe</h3>
          <ul>
            <li><strong>Aesthetic</strong> — soft, dreamy words like luxe, soft, bloom, or dusk paired with your name or niche, often with a period for a clean look.</li>
            <li><strong>Funny</strong> — playful puns, unexpected combos, and self-aware handles that make people smile and screenshot.</li>
            <li><strong>Edgy</strong> — bold, punchy, slightly mysterious names with strong consonants that feel confident and distinctive.</li>
            <li><strong>Cute</strong> — warm, friendly words and gentle diminutives that feel approachable and easy to root for.</li>
          </ul>
          <p>
            Pick the vibe that matches your content and audience, and the generator leans the whole set in that direction so
            your handle feels intentional rather than random.
          </p>
        </div>

        <div>
          <h3>Stay consistent across platforms</h3>
          <p>
            The strongest creator brands use the same handle everywhere. Matching your TikTok username with Instagram,
            YouTube, and X makes you easy to find, tag, and remember, and it protects your name from being claimed by
            someone else. Before you commit, check availability on every platform you plan to use. If your exact name is
            taken on one, a small consistent tweak — like adding your niche or swapping an underscore for a period — is
            better than a totally different handle on each app.
          </p>
        </div>

        <div>
          <h3>Mistakes to avoid</h3>
          <p>
            Skip long random number strings like <em>user284910</em> — they look auto-generated, read as spam, and are
            impossible to remember. Avoid hard-to-spell words, doubled letters that get mistyped, and inside jokes that mean
            nothing to new viewers. Don&apos;t pack in so many periods and underscores that nobody can type your name
            correctly. And resist a handle that boxes you into one narrow trend you may outgrow in a few months.
          </p>
        </div>

        <div>
          <h3>How to check availability</h3>
          <p>
            Once you have a favorite, confirming it is free takes seconds. In the TikTok app, go to <strong>Edit
            profile</strong> and type the username — a green check means it is available, and a warning means it is taken.
            You can also open <em>tiktok.com/@yourname</em> in a browser; if the profile doesn&apos;t exist, the handle is
            likely free. Because TikTok only lets you change usernames every 30 days, double-check the spelling before you
            confirm.
          </p>
        </div>

        <div>
          <h3>Built for creators everywhere</h3>
          <p>
            Whether you post from the United States, the United Kingdom, India, Brazil, Indonesia, or the Philippines, the
            ideas this tool generates are built to travel. Short, easy-to-say handles cross language barriers and get
            shared globally. Trends and slang vary by region, so treat the suggestions as a strong starting point and tweak
            them to fit your local audience and language. Because it is free and needs no account, you can regenerate fresh
            ideas as many times as you like.
          </p>
        </div>

        <div>
          <h3>Part of a complete creator toolkit</h3>
          <p>
            A great username works best alongside great content — captions, hashtags, and hooks you can craft with our other
            free tools. And when you are ready to research what is working at scale, Captapi&apos;s API gives you
            transcripts, comments, and engagement metrics from TikTok and other platforms in clean JSON, so your content
            and growth decisions are driven by real data instead of guesswork.
          </p>
        </div>
      </LongContent>

      <ToolCTA />
    </div>
  );
}
