import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Copy, MessageSquare, Search, Smile } from "lucide-react";
import { TIKTOK_EMOJIS } from "@/lib/tiktok-emojis";
import TikTokEmojisClient from "./TikTokEmojisClient";

const PATH = "/tools/tiktok-emojis";
const TITLE = "TikTok Emojis";
const DESC =
  "All 46 secret TikTok emoji codes in one place. Search the hidden TikTok emojis, see what each one means, and copy codes like [smile] with one click. Free, no sign-up.";

export const metadata = buildMetadata({
  title: TITLE + " - All 46 Secret Codes, Copy & Paste | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "tiktok emojis",
    "tiktok emoji codes",
    "secret tiktok emojis",
    "hidden tiktok emojis",
    "tiktok emoji list",
    "tiktok emoji meanings",
    "tiktok emoji copy paste",
    "tiktok smile emoji code",
    "tiktok loveface emoji",
  ],
});

const FAQS = [
  {
    q: "What are secret TikTok emojis?",
    a: "Secret TikTok emojis are a set of 46 exclusive emoticons built into the TikTok app that are not on your normal phone keyboard. You insert them by typing a shortcode in square brackets, such as [smile] or [loveface], which TikTok automatically converts into the emoji.",
  },
  {
    q: "How do I use TikTok emoji codes?",
    a: "Copy a code from this page, then paste it into a TikTok comment, caption, or DM inside the app. When you post, the code in square brackets is replaced by the matching emoji. The codes work the same on both iOS and Android.",
  },
  {
    q: "Can I copy and paste TikTok emoji codes?",
    a: "Yes. Tap any emoji card on this page to copy its code (for example [cool]) to your clipboard, then paste it into TikTok. The search box lets you find an emoji by name or code in seconds.",
  },
  {
    q: "Do TikTok emojis work outside the app?",
    a: "No. The shortcodes only render as emojis inside the TikTok app. If you paste a code like [happy] on Instagram, Twitter/X, or in a normal text message, it will appear as plain text instead of the emoji.",
  },
  {
    q: "How many secret TikTok emojis are there?",
    a: "There are 46 hidden TikTok emojis. They were introduced in 2020 without an official announcement, which is why people call them secret or hidden emojis.",
  },
  {
    q: "Why do TikTok emojis look the same on every phone?",
    a: "Unlike standard emojis that use Apple, Google, or Samsung designs depending on your device, TikTok's hidden emojis use one custom art style that looks identical across all phones and operating systems.",
  },
  {
    q: "What is the most popular TikTok emoji?",
    a: "The [wronged] emoji (a shy face with two fingers pointing together) and [loveface] (heart eyes with blushing cheeks) are among the most used, along with [laughwithtears] for jokes and [smile] for friendly comments.",
  },
  {
    q: "Is this TikTok emoji tool free?",
    a: "Yes. Browsing, searching, and copying all 46 TikTok emoji codes is completely free. There is no sign-up, no account, and no limit on how many codes you can copy.",
  },
];

const STEPS = [
  { title: "Find an emoji", text: "Scroll the grid or use the search box to find an emoji by name or code.", icon: <Search className="size-4" /> },
  { title: "Tap to copy the code", text: "Click any card to copy its shortcode, such as [smile], to your clipboard.", icon: <Copy className="size-4" /> },
  { title: "Paste it in TikTok", text: "Paste the code into a TikTok comment, caption, or DM inside the app.", icon: <MessageSquare className="size-4" /> },
  { title: "Watch it transform", text: "When you post, TikTok turns the code into the matching custom emoji.", icon: <Smile className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "UtilitiesApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="TikTok"
        title="TikTok Emojis"
        subtitle="All 46 secret TikTok emoji codes in one place. Search them, learn what they mean, and copy codes like [smile] with one click. Free and no sign-up."
      />

      <TikTokEmojisClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>The complete secret TikTok emoji list</h2>
          <p>
            TikTok has 46 hidden emojis that you will not find on your phone keyboard. Instead of picking them from an emoji picker, you type a shortcode wrapped in square brackets, like [happy] or [loveface], and TikTok swaps it for a custom emoticon when you post. They first appeared in 2020 with no official announcement, which is how they earned the nickname secret emojis. This page lists every one, explains what it means, and lets you copy the code instantly.
          </p>
          <p>
            Because these emojis use a single art style designed by TikTok, they look exactly the same on every device. That consistency is part of why creators like them: a [cool] or [wronged] emoji reads the same to your whole audience, whether they are on an iPhone, an Android, or a tablet.
          </p>
        </div>

        <div>
          <h2>How to use TikTok emoji codes in comments and captions</h2>
          <p>
            Using the codes is simple. Copy the shortcode for the emoji you want from the grid above, open TikTok, and paste it into a comment, caption, or direct message. As soon as you post, the bracketed code turns into the emoji. Keep in mind the codes only work inside the TikTok app, so pasting [smile] on another platform will just show the text.
          </p>
          <ul>
            <li>Type or paste the code exactly, including the square brackets.</li>
            <li>You can combine several codes in one comment for a fun reaction.</li>
            <li>Codes are not case sensitive, but lowercase is the safest.</li>
          </ul>
        </div>

        <div>
          <h2>TikTok emoji meanings</h2>
          <p>
            Each hidden emoji carries its own vibe. Here is what all 46 TikTok emojis mean, so you can pick the perfect one for any comment or caption.
          </p>
          <ul>
            {TIKTOK_EMOJIS.map((emoji) => (
              <li key={emoji.code}>
                <strong>{emoji.name}</strong> <code>[{emoji.code}]</code> &mdash; {emoji.meaning}
              </li>
            ))}
          </ul>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building something with TikTok data?"
        sub="Captapi gives you APIs for TikTok, YouTube, Instagram, and Facebook transcripts, summaries, comments, and stats. Start free and automate the data side of your content workflow."
      />
    </>
  );
}
