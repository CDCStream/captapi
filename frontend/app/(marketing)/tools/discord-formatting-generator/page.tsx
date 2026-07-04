import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { PenLine, Wand2, Copy, MessageSquare } from "lucide-react";
import DiscordFormattingClient from "./DiscordFormattingClient";

const PATH = "/tools/discord-formatting-generator";
const TITLE = "Discord Text Formatting Generator";
const DESC =
  "Type once and copy Discord markdown instantly — bold, italic, underline, strikethrough, spoilers, code blocks, headers, quotes, and colored text. Free, no sign-up.";

export const metadata = buildMetadata({
  title: TITLE + " — Bold, Spoiler, Code & Colored Text | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "discord text formatting",
    "how to hide text in discord",
    "how to add spoiler in discord",
    "discord cross out text",
    "discord spoiler image",
    "how to bold in discord",
    "discord colored text",
    "discord markdown",
    "discord symbols",
  ],
});

const FAQS = [
  { q: "How do I hide text (spoiler) in Discord?", a: "Wrap the text in double pipes: ||like this||. It shows up as a blacked-out spoiler that other users click to reveal. On mobile, long-press the selected text and choose Spoiler, or type the pipes manually. To spoiler an image, upload it and tick \u201cMark as spoiler\u201d before sending." },
  { q: "How do I cross out text in Discord?", a: "Put two tildes on each side: ~~like this~~ renders as strikethrough. It's the same syntax as bold or italic, just with tildes." },
  { q: "How do I make bold text in Discord?", a: "Wrap it in double asterisks: **bold**. Use single asterisks for *italic*, three for ***bold italic***, and double underscores for __underline__." },
  { q: "Can you use colored text in Discord?", a: "Discord has no native color picker, but you can fake it with syntax-highlighted code blocks. A triple-backtick block with the \u201cdiff\u201d language turns lines starting with + green and lines starting with - red. This tool generates both for you. Note: colors only show on desktop, not mobile." },
  { q: "How do I make headers in Discord?", a: "Start a line with #, ##, or ### followed by a space for large, medium, or small headers. Headers were added to Discord in 2023 and work in messages, not just posts." },
  { q: "Does Discord formatting work on mobile?", a: "Markdown (bold, italic, spoilers, code) works everywhere. The one exception is colored text via diff code blocks — the color highlighting only renders on the desktop and web apps, though the text still appears (just uncolored) on mobile." },
  { q: "How do I write a code block in Discord?", a: "Wrap text in triple backticks for a multi-line code block, or single backticks for inline code. Add a language name right after the opening triple backticks (like ```js) for syntax highlighting." },
];

const STEPS = [
  { title: "Type your text", text: "Enter it once at the top.", icon: <PenLine className="size-4" /> },
  { title: "See every style", text: "Bold, spoiler, strikethrough, code, colors, and more.", icon: <Wand2 className="size-4" /> },
  { title: "Copy the markdown", text: "One click copies the exact syntax.", icon: <Copy className="size-4" /> },
  { title: "Paste into Discord", text: "It renders instantly in any channel or DM.", icon: <MessageSquare className="size-4" /> },
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
        subtitle="Type your text once and copy the exact Discord markdown for every style — bold, italic, spoilers, strikethrough, code blocks, headers, and even colored text."
      />

      <DiscordFormattingClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>How Discord formatting works</h2>
          <p>
            Discord uses Markdown, a lightweight syntax where symbols around your text change how it renders.
            Asterisks control bold and italic, tildes strike text through, double pipes hide spoilers, and
            backticks create code. Because it&apos;s all plain characters, you can type it directly — this
            tool just saves you remembering which symbol does what and lets you copy clean output every time.
          </p>
        </div>
        <div>
          <h2>The colored text trick</h2>
          <p>
            Discord deliberately has no color picker, but syntax highlighting inside code blocks lets you
            cheat. A code block marked with the <code>diff</code> language colors any line starting with
            <code>+</code> green and any line starting with <code>-</code> red. Other languages give other
            palettes — <code>fix</code> yields yellow, <code>css</code> can produce orange in brackets. It
            only renders in color on desktop and web, so use it for emphasis, not critical information your
            mobile users must see.
          </p>
        </div>
        <div>
          <h2>Combining styles</h2>
          <p>
            You can nest most formats: <code>**__bold underline__**</code>, or a spoiler inside a quote.
            The order of the symbols doesn&apos;t matter as long as each pair closes. The two things that
            don&apos;t combine are code (backticks disable all other markdown inside them, on purpose) and
            colored diff blocks, which are themselves code.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building Discord bots or tools?"
        sub="Captapi returns social profiles, posts, and stats as clean JSON across TikTok, Instagram, YouTube, Twitch, and more. Start free with 100 credits."
      />
    </>
  );
}
