import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { AtSign, Sparkles, Copy, Check } from "lucide-react";

const PATH = "/tools/social-media-bio-generator";
const TITLE = "Free Social Media Bio Generator — YouTube, TikTok, IG, X";
const DESC =
  "Generate 6 on-brand social media bios for Instagram, TikTok, Twitter/X, or YouTube — each within the platform's character limit. AI-powered, free, with one-click copy and no sign-up.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "social media bio generator",
    "youtube bio generator",
    "tiktok bio ideas",
    "instagram bio generator",
    "bio generator",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "social-media-bio-generator",
  submitLabel: "Generate bios",
  fields: [
    {
      name: "platform",
      label: "Platform",
      type: "select",
      options: [
        { value: "instagram", label: "Instagram (150 chars)" },
        { value: "tiktok", label: "TikTok (80 chars)" },
        { value: "twitter", label: "Twitter / X (160 chars)" },
        { value: "youtube", label: "YouTube (1000 chars)" },
      ],
    },
    {
      name: "niche",
      label: "Your niche or profession",
      type: "text",
      required: true,
      placeholder: "e.g. travel photographer",
    },
    {
      name: "tone",
      label: "Personality tone",
      type: "select",
      options: [
        { value: "professional", label: "Professional" },
        { value: "funny", label: "Funny" },
        { value: "minimal", label: "Minimal" },
        { value: "aesthetic", label: "Aesthetic" },
      ],
    },
  ],
};

const FAQS = [
  { q: "What is the character limit for a social media bio on each platform?", a: "Limits differ by platform: Instagram allows 150 characters, TikTok 80, Twitter/X 160, and YouTube channel descriptions stretch to roughly 1,000 characters. This generator tailors every bio to the limit of the platform you choose so nothing gets cut off." },
  { q: "What should I include in a social media bio?", a: "A strong bio answers three questions fast: who you are, what you offer, and what to do next. Combine your niche or profession, a value or personality hook, and a clear call to action or link. On short platforms like TikTok, lead with the single most important detail." },
  { q: "Should I use emojis in my bio?", a: "Yes, when they fit your brand. Emojis act as visual bullet points, save characters, and add personality — especially useful on tight limits like TikTok's 80 characters. Keep them relevant and don't overdo it; one or two per line usually reads best for audiences in the US, UK, India, and beyond." },
  { q: "How do I add a call to action or link to my bio?", a: "End your bio with a short, action-led line such as \u201cShop new drops below\u201d or \u201cFree guide \u2193\u201d and pair it with your link. Instagram and TikTok give you one clickable link field, while Twitter/X and YouTube let you add links directly in the description." },
  { q: "Do keywords in my bio help people find me?", a: "They can. Searchable keywords — your niche, location, or service — help platforms and users surface your profile in search and suggestions. Naturally working terms like \u201cBangalore food blogger\u201d or \u201cLondon fitness coach\u201d into your bio improves discoverability without looking spammy." },
  { q: "How do I add line breaks to my Instagram bio?", a: "Instagram bios support line breaks, which make them far easier to scan. Type your bio with line breaks in your phone's notes app or directly in the edit screen, then save. Each line can hold a different idea — identity, offer, and CTA — within the 150-character total." },
  { q: "Should my bio be the same across every platform?", a: "Keep your core identity and voice consistent so people recognise you everywhere, but adapt the length and detail to each platform. A 160-character Twitter/X bio can be punchy, while your YouTube description can expand with full context, links, and upload schedule." },
  { q: "How often should I update my bio?", a: "Refresh it whenever your focus, offer, or campaign changes — a new product, a launch, a season, or a milestone. Many creators in Brazil, Southeast Asia, and globally rotate their CTA or pinned link regularly to match what they're currently promoting." },
  { q: "Do bios affect discoverability and the algorithm?", a: "Bios don't directly rank your posts, but they influence whether a visitor follows and how platforms categorise your profile in search and recommendations. A clear, keyword-aware bio raises your follow-through rate, which indirectly supports growth." },
  { q: "Can you give bio examples by profession?", a: "Absolutely — that's what this tool does. Enter a profession like \u201ctravel photographer,\u201d \u201cSaaS founder,\u201d \u201cfitness coach,\u201d or \u201cfood blogger,\u201d pick a tone, and you'll get six ready-to-use bios tailored to your chosen platform's limit." },
];

export default function Page() {
  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "Free Tools", path: "/tools" },
      { name: "Social Media Bio Generator", path: PATH },
    ]),
    webApplicationLd({ name: "Social Media Bio Generator", description: DESC, path: PATH, category: "UtilitiesApplication" }),
    faqLd(FAQS),
  ];

  return (
    <div>
      <JsonLd data={jsonLd} />
      <ToolHero
        platform="All platforms"
        title="Social Media Bio Generator"
        subtitle="Turn your niche and tone into 6 on-brand bios for Instagram, TikTok, Twitter/X, or YouTube — each crafted to fit the platform's exact character limit, with one-click copy."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse
        steps={[
          { title: "Pick your platform", text: "Choose Instagram, TikTok, Twitter/X, or YouTube so bios fit the right limit.", icon: <AtSign className="size-4" /> },
          { title: "Add your niche & tone", text: "Enter your profession and pick a personality tone.", icon: <Sparkles className="size-4" /> },
          { title: "Copy your favourite", text: "Get six bios within the character limit and copy the one you love.", icon: <Copy className="size-4" /> },
          { title: "Paste & save", text: "Drop it into your profile, add your link, and save.", icon: <Check className="size-4" /> },
        ]}
      />

      <FAQSection faqs={FAQS} />

      <LongContent>
        <div>
          <h2>The free AI social media bio generator</h2>
          <p>
            Your bio is the most valuable real estate on any profile. It is the first thing a visitor reads after your
            name and photo, and in a few short seconds it decides whether they tap follow, click your link, or scroll
            away. Yet most people leave it half-finished, stuffed with clich&eacute;s, or copy-pasted across platforms
            that each work differently. This free social media bio generator uses AI to turn your niche and tone into six
            polished bios — each written to fit the exact character limit of the platform you choose, whether that is
            Instagram, TikTok, Twitter/X, or YouTube.
          </p>
        </div>

        <div>
          <h3>Character limits by platform</h3>
          <p>
            Every platform plays by different rules, and a bio that overflows simply gets truncated. Knowing the limits
            up front is the difference between a bio that lands and one that gets cut off mid-sentence:
          </p>
          <ul>
            <li><strong>Instagram &mdash; 150 characters.</strong> Tight but expressive. Line breaks and emojis help you pack identity, offer, and a CTA into a scannable block.</li>
            <li><strong>TikTok &mdash; 80 characters.</strong> The strictest limit. Lead with the single most important thing about you and let emojis do the heavy lifting.</li>
            <li><strong>Twitter/X &mdash; 160 characters.</strong> Room for a punchy one-liner plus a hook. Wit and clarity travel well here.</li>
            <li><strong>YouTube &mdash; ~1,000 characters.</strong> A full channel description where you can add context, links, upload schedule, and searchable keywords.</li>
          </ul>
        </div>

        <div>
          <h3>The bio formula that works</h3>
          <p>
            The strongest bios follow a simple structure: <strong>who you are + what you offer + a call to action</strong>.
            Start with your identity or niche so visitors instantly know they are in the right place. Follow with the
            value you deliver — the reason to stick around. Then close with a clear next step: a link, an offer, or an
            invitation. On longer platforms you can expand each part; on TikTok you might compress all three into a single
            sharp line. The formula keeps your bio focused instead of a random list of facts.
          </p>
        </div>

        <div>
          <h3>Using emojis and keywords</h3>
          <p>
            Emojis are more than decoration. They act as visual bullet points, break up text, save precious characters,
            and signal personality at a glance — invaluable when you only have 80 characters to work with. Use them with
            intent rather than scattering them everywhere. Keywords matter too: weaving your niche, location, or service
            into the bio — think &ldquo;Lagos wedding photographer&rdquo; or &ldquo;remote-work productivity coach&rdquo; —
            helps platforms and people surface your profile in search and suggested results without sounding forced.
          </p>
        </div>

        <div>
          <h3>Consistency across platforms</h3>
          <p>
            Audiences often find the same creator on several apps, so a consistent core identity and voice make you
            instantly recognisable. Keep your name, tagline, and personality aligned everywhere, then adapt the length and
            detail to each platform&apos;s limit. Your Twitter/X bio can be a punchy one-liner, your Instagram bio a
            scannable three-line block, and your YouTube description a fuller story with links and a schedule. Same you,
            tailored fit.
          </p>
        </div>

        <div>
          <h3>Mistakes to avoid</h3>
          <ul>
            <li><strong>Overflowing the limit</strong> so your most important words get cut off.</li>
            <li><strong>No call to action</strong> — leaving visitors unsure what to do next.</li>
            <li><strong>Vague clich&eacute;s</strong> like &ldquo;living my best life&rdquo; that say nothing about what you offer.</li>
            <li><strong>Copy-pasting</strong> an identical bio onto a platform with a very different limit and audience.</li>
            <li><strong>Letting it go stale</strong> after a launch, season, or rebrand has moved on.</li>
          </ul>
        </div>

        <div>
          <h3>Built for creators everywhere</h3>
          <p>
            Whether you build your audience in the United States, the United Kingdom, India, Brazil, the Philippines, or
            anywhere across Southeast Asia, a clear bio is universal currency. The tone and keyword options let you match
            local language and culture, while the platform limits stay accurate worldwide. Because it is free and needs no
            account, you can regenerate fresh bios whenever your focus shifts or a new campaign goes live.
          </p>
        </div>

        <div>
          <h3>Part of a complete creator toolkit</h3>
          <p>
            A great bio works hand in hand with strong captions, hashtags, titles, and thumbnails — all of which you can
            create with our other free tools. And when you are ready to understand what is working at scale,
            Captapi&apos;s API delivers transcripts, comments, and engagement metrics from YouTube, TikTok, Instagram, and
            Facebook in clean JSON, so your profile and content decisions are driven by real data rather than guesswork.
          </p>
        </div>
      </LongContent>

      <ToolCTA />
    </div>
  );
}
