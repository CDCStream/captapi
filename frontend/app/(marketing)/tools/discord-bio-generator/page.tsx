import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Check, Copy } from "lucide-react";

const PATH = "/tools/discord-bio-generator";
const TITLE = "Free Discord Bio Generator";
const DESC =
  "Generate 6 Discord About Me bios that fit the 190-character limit — aesthetic, funny, edgy, or minimal, with emoji and kaomoji. Free, no sign-up.";

export const metadata = buildMetadata({
  title: TITLE + " — Aesthetic Bio Ideas & Templates | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "discord bio generator",
    "discord bio template",
    "discord bio ideas",
    "discord bios",
    "aesthetic discord bio",
    "funny discord bio",
    "discord about me ideas",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "discord-bio-generator",
  submitLabel: "Generate bios",
  fields: [
    {
      name: "interest",
      label: "What are you into?",
      type: "text",
      required: true,
      placeholder: "e.g. valorant, anime, lofi music",
      help: "Games, music, hobbies \u2014 whatever should show up in your bio.",
    },
    {
      name: "style",
      label: "Style",
      type: "select",
      options: [
        { value: "aesthetic", label: "Aesthetic" },
        { value: "funny", label: "Funny" },
        { value: "edgy", label: "Edgy" },
        { value: "minimal", label: "Minimal" },
        { value: "cute / kaomoji", label: "Cute / kaomoji" },
      ],
    },
  ],
};

const FAQS = [
  { q: "How long can a Discord bio be?", a: "The About Me section allows up to 190 characters. Every bio this generator produces is counted against that limit, with the character count shown under each suggestion." },
  { q: "Where do I edit my Discord bio?", a: "User Settings \u2192 Profiles \u2192 About Me on desktop, or Settings \u2192 Account \u2192 Profile on mobile. Paste your bio, and it appears when anyone clicks your name or avatar." },
  { q: "Can I use custom fonts in a Discord bio?", a: "The About Me field supports basic markdown (bold, italic, links) plus emoji and Unicode. For fancy Unicode fonts, generate styled text with our Discord Fonts tool and paste it into your bio — it works because the characters are Unicode, not formatting." },
  { q: "Can I put links in my Discord bio?", a: "Yes — plain URLs in the About Me become clickable links. Markdown-style named links only render in some contexts, so plain URLs are the safe choice." },
  { q: "What makes a good Discord bio?", a: "Short beats long even within 190 characters: a line about what you're into, a touch of personality (emoji, kaomoji, or a joke), and optionally your pronouns, timezone, or a link. Servers see thousands of profiles — a distinctive one line is more memorable than a packed paragraph." },
  { q: "Is this generator free?", a: "Yes — unlimited generations, no account, no watermark." },
];

const STEPS = [
  { title: "List your interests", text: "Games, music, fandoms \u2014 a few words is plenty.", icon: <PenLine className="size-4" /> },
  { title: "Choose a style", text: "Aesthetic, funny, edgy, minimal, or cute kaomoji.", icon: <Sparkles className="size-4" /> },
  { title: "Generate 6 bios", text: "Every suggestion fits Discord's 190-character limit.", icon: <Check className="size-4" /> },
  { title: "Copy and paste", text: "Settings \u2192 Profiles \u2192 About Me. Done.", icon: <Copy className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "UtilitiesApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: "Discord Bio Generator", path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Discord"
        title="Discord Bio Generator"
        subtitle="Tell us what you're into and get 6 About Me bios that fit Discord's 190-character limit — aesthetic, funny, edgy, minimal, or kaomoji-cute."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>Bio templates to riff on</h2>
          <p>Prefer to write your own? These skeletons work for almost any profile — fill in the brackets:</p>
          <ul>
            <li><strong>Minimal:</strong> [name] \u30fb [age/pronouns] \u30fb [main game/hobby]</li>
            <li><strong>Aesthetic:</strong> \u2727 [one-word mood] \u2727 \u2014 [interest] enjoyer \u2014 [timezone]</li>
            <li><strong>Funny:</strong> professional [game] loser \u2022 powered by [drink/snack]</li>
            <li><strong>Gamer:</strong> [rank] in [game] \u2022 [platform] \u2022 dm for customs</li>
            <li><strong>Creator:</strong> i make [thing] \u2022 [link] \u2022 slow replies, fast edits</li>
          </ul>
        </div>
        <div>
          <h2>Make it match the rest of your profile</h2>
          <p>
            Your bio lands alongside your avatar, banner, and status — the strongest profiles treat all four
            as one look. If your bio is soft-aesthetic, an aggressive gamer banner fights it. Nitro users can
            add an animated banner and profile theme colors; free profiles still look sharp when the bio's
            tone matches the avatar. For styled Unicode text inside the bio, pair this with our Discord Fonts
            generator.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building social tools?"
        sub="Captapi returns profiles, posts, comments, and stats as clean JSON across TikTok, Instagram, YouTube, Twitch, and more. Start free with 100 credits."
      />
    </>
  );
}
