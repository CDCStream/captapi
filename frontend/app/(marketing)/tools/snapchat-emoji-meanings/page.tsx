import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Search, Filter, BookOpen, Smile } from "lucide-react";
import { SNAP_EMOJIS } from "@/lib/snapchat-emojis";
import SnapEmojiClient from "./SnapEmojiClient";

const PATH = "/tools/snapchat-emoji-meanings";
const TITLE = "Snapchat Emoji Meanings";
const DESC =
  "What does the yellow heart, smirking face, hourglass, or green dot mean on Snapchat? Search every friend emoji, symbol, charm, and icon with clear explanations.";

export const metadata = buildMetadata({
  title: TITLE + " — Every Friend Emoji & Symbol Explained | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "snapchat emoji meanings",
    "snapchat symbols meaning",
    "what does the yellow heart mean on snapchat",
    "what does the green circle mean on snapchat",
    "smiling face meaning in snapchat",
    "snapchat friend emojis",
    "snapchat hourglass",
    "smirking face snapchat",
  ],
});

const FAQS = [
  { q: "What does the yellow heart mean on Snapchat?", a: "You and this friend are each other's #1 Best Friends — you send the most snaps to each other. Keep it up for two weeks and it turns into a red heart; two months earns the pink hearts." },
  { q: "What does the smirking face 😏 mean on Snapchat?", a: "You are one of their Best Friends, but they are not one of yours — they snap you a lot more than you snap them back. It's one-directional, which is why the smirk has a reputation." },
  { q: "What does the green dot mean on Snapchat?", a: "The green dot (or green circle) next to a name or Bitmoji means the person is online and active in the app right now. Users can disable their activity indicator in settings, so no dot doesn't guarantee they're offline." },
  { q: "What does the hourglass mean on Snapchat?", a: "Your Snapstreak with this friend is about to expire — you're in roughly the last 4 hours of the 24-hour window. Either of you sending a photo or video snap clears it and keeps the streak alive." },
  { q: "What does the grimacing face 😬 mean on Snapchat?", a: "Your #1 Best Friend is also their #1 Best Friend — you both snap the same person the most. It's Snapchat quietly telling you that you share a top friend." },
  { q: "What does the baby emoji mean on Snapchat?", a: "You just became friends with this person — it marks brand-new friendships and disappears after a while as your snap history develops." },
  { q: "Can I change Snapchat's friend emojis?", a: "Yes — Settings \u2192 Manage \u2192 Friend Emojis lets you customize which emoji represents each friendship status. That means a friend's emojis may differ from the defaults listed here if they've customized them." },
  { q: "How do Best Friends work on Snapchat?", a: "Snapchat privately ranks up to 8 Best Friends based on who you snap and chat with most. The list is only visible to you, but the friend emojis (yellow heart, smiley, etc.) reveal where people stand — which is exactly what this page decodes." },
];

const STEPS = [
  { title: "Search the emoji", text: "Type the emoji itself or its name — e.g. hourglass.", icon: <Search className="size-4" /> },
  { title: "Filter by category", text: "Friend emojis, symbols, charms, or trophies.", icon: <Filter className="size-4" /> },
  { title: "Read the meaning", text: "What it says about your friendship, precisely.", icon: <BookOpen className="size-4" /> },
  { title: "Decode your list", text: "Know exactly where you stand with every friend.", icon: <Smile className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "ReferenceApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Snapchat"
        title={TITLE}
        subtitle="Every Snapchat emoji decoded — friend hearts, the smirk, the hourglass, dots, arrows, and charms — searchable and always up to date."
      />

      <SnapEmojiClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>Every emoji at a glance</h2>
          <ul>
            {SNAP_EMOJIS.map((e) => (
              <li key={`${e.emoji}-${e.name}`}>
                <strong>{e.emoji} {e.name}</strong> — {e.meaning}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h2>How Snapchat decides your friend emojis</h2>
          <p>
            Friend emojis update automatically based on your private Best Friends ranking — the people you
            exchange the most snaps and chats with. The hierarchy of hearts (yellow at #1, red after two
            weeks, pink after two months) rewards consistency on both sides, while the smirk exposes
            one-sided friendships. Because the ranking recalculates constantly, emojis can appear or vanish
            overnight when your snapping habits change — losing a heart just means the balance shifted, not
            that anyone did anything.
          </p>
        </div>
        <div>
          <h2>Related Snapchat guides</h2>
          <p>
            Decoding the fire emoji and keeping streaks alive is covered in our Snapchat Streaks Guide, the
            Snapchat+ solar system is explained in Snapchat Planets, and whether screenshots notify is in
            our Screenshot Notification Checker — all free.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building on social data?"
        sub="Captapi returns profiles, posts, comments, and stats as clean JSON across TikTok, Instagram, YouTube, and more. Start free with 100 credits."
      />
    </>
  );
}
