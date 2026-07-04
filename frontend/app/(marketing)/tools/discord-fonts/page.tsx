import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Type, Copy, MessageSquare, Sparkles } from "lucide-react";
import DiscordFontsClient from "./DiscordFontsClient";

const PATH = "/tools/discord-fonts";
const TITLE = "Discord Fonts & Text Generator";
const DESC =
  "Turn any text into bold, italic, cursive, gothic, and 15+ other Unicode styles you can paste into Discord — plus a complete Discord markdown formatting cheat sheet. Free, no sign-up.";

export const metadata = buildMetadata({
  title: TITLE + " — Copy & Paste Fonts + Markdown Guide | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "discord fonts",
    "discord font generator",
    "discord text formatting",
    "discord text generator",
    "discord formatting",
    "discord bold text",
    "discord italics",
    "discord spoiler",
    "discord markdown",
  ],
});

const FAQS = [
  { q: "How do I change fonts in Discord?", a: "Discord does not have a built-in font picker, so you use Unicode look-alike characters. Type your text in the generator above, tap a style like Bold or Script to copy it, then paste it into a Discord message, display name, or status. The styled characters render everywhere Unicode is supported." },
  { q: "Are Discord fonts actually different fonts?", a: "No \u2014 they are Unicode characters that look like styled letters, such as mathematical bold or script symbols. That is why they work without Nitro or bots: you are pasting special characters, not changing Discord's actual typeface." },
  { q: "Do these fonts work in Discord usernames and display names?", a: "Yes. Because they are standard Unicode characters, you can paste them into your display name, server nickname, and custom status. Some servers or screen readers may render them plainly, so keep important names readable." },
  { q: "What is the difference between the fonts and markdown formatting?", a: "The font styles use special Unicode characters and work anywhere text goes, including names. Discord markdown (like **bold** or *italic*) is Discord's own formatting that only works inside messages and is more accessible. The cheat sheet on this page covers markdown." },
  { q: "How do I make bold text in Discord messages?", a: "Wrap the text in two asterisks: **like this**. Discord converts it to bold when you send the message. For italics use single asterisks, and for bold italics use three. See the markdown table on this page for every option." },
  { q: "Will Unicode fonts get me banned or flagged?", a: "No. Using Unicode characters is allowed and extremely common. Just avoid overusing hard-to-read styles in places where clarity matters, since some styles can be difficult for screen readers and search." },
  { q: "Are these Discord fonts free?", a: "Yes, completely free. There is no sign-up, no Nitro requirement, and no limit on how many styles you can generate and copy." },
];

const STEPS = [
  { title: "Type your text", text: "Enter the word or phrase you want to style in the input box.", icon: <Type className="size-4" /> },
  { title: "Pick a style", text: "Browse bold, cursive, gothic, monospace, bubble, and more.", icon: <Sparkles className="size-4" /> },
  { title: "Tap to copy", text: "Click any style card to copy the styled text to your clipboard.", icon: <Copy className="size-4" /> },
  { title: "Paste into Discord", text: "Drop it into a message, display name, nickname, or status.", icon: <MessageSquare className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "UtilitiesApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Discord"
        title={TITLE}
        subtitle="Turn plain text into bold, cursive, gothic, monospace and more — copy-paste ready for Discord names, statuses, and messages. Plus a full markdown formatting cheat sheet."
      />

      <DiscordFontsClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>How Discord fonts work</h2>
          <p>
            Discord ships with one interface font and no way to change it, so &quot;Discord fonts&quot; are
            really Unicode characters that mimic styled letters. When you copy a Bold or Script result above,
            you are copying special characters that look like styled type. Because they are ordinary Unicode,
            they display in messages, usernames, server nicknames, and your custom status without Nitro, bots,
            or any extra setup.
          </p>
          <p>
            Keep readability in mind: fancy styles are great for a display name or a one-line status, but a
            whole paragraph in gothic script is hard to read and unfriendly to screen readers. Use them for
            accent, not for everything.
          </p>
        </div>
        <div>
          <h2>Discord markdown vs Unicode fonts</h2>
          <p>
            For formatting inside messages, Discord has its own markdown system, which is the more accessible
            choice. Two asterisks make text <strong>bold</strong>, single asterisks make it italic, two
            tildes add a strikethrough, and two pipes create a hidden spoiler. The cheat sheet above lists
            every pattern, including code blocks with syntax highlighting and block quotes. Markdown only
            works inside messages, while the Unicode styles work in names and statuses too — use whichever
            fits the spot.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building a Discord bot or community tool?"
        sub="Captapi gives you social data — profiles, posts, comments, transcripts, and stats — as clean JSON across YouTube, TikTok, Instagram, and more. Start free with 100 credits, no card required."
      />
    </>
  );
}
