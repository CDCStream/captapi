import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Copy, Check } from "lucide-react";

const PATH = "/tools/instagram-username-generator";
const TITLE = "Free Instagram Username Generator — 15 Name Ideas";
const DESC =
  "Generate 15 catchy Instagram username ideas by vibe — aesthetic, minimal, funny, or edgy — all within Instagram's 30-character limit. AI-powered, free, one-click copy, no sign-up.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "instagram username generator",
    "instagram name ideas",
    "aesthetic instagram usernames",
    "instagram username ideas",
    "cute instagram usernames",
    "ig username generator",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "instagram-username-generator",
  submitLabel: "Generate usernames",
  fields: [
    {
      name: "interest",
      label: "Your interest or niche",
      type: "text",
      required: true,
      placeholder: "e.g. travel photography",
      help: "Be specific for sharper ideas — e.g. \u201cbudget backpacking in Asia\u201d.",
    },
    {
      name: "style",
      label: "Vibe",
      type: "select",
      options: [
        { value: "aesthetic", label: "Aesthetic" },
        { value: "minimal", label: "Minimal" },
        { value: "funny", label: "Funny" },
        { value: "edgy", label: "Edgy" },
      ],
    },
  ],
};

const FAQS = [
  { q: "How long can an Instagram username be?", a: "An Instagram username (your @handle) can be up to 30 characters. Your display name — shown in bold on your profile — can be up to 64 characters. This tool keeps every suggestion within the 30-character handle limit." },
  { q: "What characters are allowed in an Instagram username?", a: "Instagram usernames can contain letters, numbers, underscores, and periods. Spaces and other symbols are not allowed, and a username cannot start or end with a period or contain consecutive periods." },
  { q: "How do I check if an Instagram username is available?", a: "Go to Edit profile in the Instagram app and type the name — Instagram tells you instantly if it is taken. You can also visit instagram.com/username in a browser; a \u201cpage not found\u201d usually means it is free." },
  { q: "How often can I change my Instagram username?", a: "You can change it at any time, but Instagram may hold your old username for 14 days so you can revert. Frequent changes confuse followers and break existing tags and links, so pick something you can keep." },
  { q: "What makes a good Instagram username?", a: "Short, easy to spell, easy to say out loud, and hinting at your niche or personality. Avoid long number strings and heavy symbol use — memorable, brandable handles get searched and shared far more often." },
  { q: "Should my Instagram username match my other platforms?", a: "Yes, where possible. Matching handles across Instagram, TikTok, YouTube, and X makes you easier to find and tag, and protects your brand. Check availability everywhere before you commit." },
  { q: "Periods or underscores in an Instagram handle?", a: "Both are fine and purely stylistic. Periods (jane.travels) read cleaner and more aesthetic; underscores (jane_travels) are the classic separator. Pick one and stay consistent." },
  { q: "Is this Instagram username generator free?", a: "Yes. Generating, browsing, and copying username ideas is completely free with no sign-up and no limit." },
];

const STEPS = [
  { title: "Describe your niche", text: "Tell us what your account is about — the more specific, the better.", icon: <PenLine className="size-4" /> },
  { title: "Pick a vibe", text: "Aesthetic, minimal, funny, or edgy — the style shapes every suggestion.", icon: <Sparkles className="size-4" /> },
  { title: "Generate 15 ideas", text: "AI produces 15 handles that fit Instagram's 30-character rules.", icon: <Check className="size-4" /> },
  { title: "Copy your favorite", text: "One-click copy, then check availability in the Instagram app.", icon: <Copy className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "UtilitiesApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: "Instagram Username Generator", path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Instagram"
        title="Instagram Username Generator"
        subtitle="Get 15 catchy, available-style Instagram username ideas in your niche and vibe — all within the 30-character limit. AI-powered, free, no sign-up."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>How to pick the perfect Instagram username</h2>
          <p>
            Your username is your address on Instagram — it appears in your profile URL, in every tag and
            mention, and in search. The best handles are short, easy to spell after hearing them once, and
            give a hint of what the account is about. Skip long number strings and complicated symbol
            patterns: if a friend cannot type it from memory, neither can a potential follower.
          </p>
          <p>
            This generator combines your niche with a vibe you choose and produces 15 ideas that already meet
            Instagram&apos;s rules: 30 characters max, only letters, numbers, underscores, and periods. Copy
            the ones you like and test availability right inside the app.
          </p>
        </div>
        <div>
          <h2>Username rules and limits on Instagram</h2>
          <ul>
            <li>Maximum 30 characters; letters, numbers, underscores, and periods only.</li>
            <li>No spaces, and no periods at the start or end of the handle.</li>
            <li>Usernames must be unique across all of Instagram.</li>
            <li>You can change your handle anytime, but old links and tags will break.</li>
            <li>Your display name is separate and more flexible — up to 64 characters with spaces and emoji.</li>
          </ul>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building with Instagram data?"
        sub="Captapi returns Instagram profiles, posts, reels, comments, and stats as clean JSON — plus TikTok, YouTube, and Facebook. Start free with 100 credits, no card required."
      />
    </>
  );
}
