import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Flame, Hourglass, RotateCcw, Trophy } from "lucide-react";

const PATH = "/tools/snapchat-streaks";
const TITLE = "Snapchat Streaks Guide";
const DESC =
  "How Snapchat streaks work, what the hourglass emoji means, how to restore a lost streak for free, and the longest streaks ever recorded — the complete 2026 guide.";

export const metadata = buildMetadata({
  title: TITLE + " — Restore a Lost Streak, Hourglass & Records | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "snapchat restore streak",
    "snapchat streaks",
    "how to restore a snapchat streak",
    "snapchat hourglass",
    "longest snapchat streak",
    "how do snapchat streaks work",
    "snapchat streak lost",
  ],
});

const FAQS = [
  { q: "How do Snapchat streaks work?", a: "A streak (the fire emoji plus a number) starts after you and a friend snap each other on 3 consecutive days. To keep it alive, BOTH of you must send at least one photo or video snap every 24 hours. Chat messages, group snaps, Stories, and Memories do not count — only direct photo/video snaps between the two of you." },
  { q: "How do I restore a lost Snapchat streak?", a: "Open the chat with that friend — Snapchat shows a Restore option next to the expired streak. Every user gets one free restore per month (per streak, within a limited window after losing it); additional restores cost a small in-app fee or come with Snapchat+. You can also submit a support request at help.snapchat.com if the streak was lost due to an app issue." },
  { q: "What does the hourglass emoji on Snapchat mean?", a: "The hourglass appears when a streak is about to expire — roughly the last 4 hours of the 24-hour window. If either of you sends a snap before time runs out, the hourglass disappears and the streak continues." },
  { q: "Why did my streak disappear when we both snapped?", a: "Common causes: one snap was sent to a group (doesn't count), it was a chat message instead of a photo/video snap, a snap failed to send on poor connection, or one side sent it just after the 24-hour mark. If you believe it's an app error, use the free restore or Snapchat support." },
  { q: "What is the longest Snapchat streak?", a: "Community-tracked record streaks run over 4,000 days — dating back to shortly after streaks launched in April 2015. Snapchat doesn't publish an official leaderboard, so records are self-reported screenshots." },
  { q: "Do streaks give you anything?", a: "Nothing tangible — no rewards, features, or Snap Score multipliers. The number next to the fire emoji counts consecutive days, and Snapchat designed it purely as an engagement habit. That said, losing a long one still hurts, which is why restores exist." },
  { q: "Does Snapchat+ help with streaks?", a: "Snapchat+ includes streak restores as a perk, plus indicators like rewatch counts on stories. It doesn't change how streaks work — the 24-hour rule still applies to both sides." },
];

const STEPS = [
  { title: "Start the streak", text: "Snap each other 3 days in a row \u2014 the fire emoji appears.", icon: <Flame className="size-4" /> },
  { title: "Keep it alive", text: "Both sides send a photo/video snap every 24 hours.", icon: <Hourglass className="size-4" /> },
  { title: "Watch the hourglass", text: "It warns you ~4 hours before the streak expires.", icon: <RotateCcw className="size-4" /> },
  { title: "Restore if lost", text: "One free restore per month, right in the chat.", icon: <Trophy className="size-4" /> },
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
        subtitle="Everything about the fire emoji — the exact rules that keep a streak alive, what the hourglass means, how to restore a lost streak for free, and the records people have hit."
      />

      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border bg-card p-5">
          <p className="text-3xl">🔥</p>
          <h2 className="mt-2 font-semibold">Fire + number</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Your active streak: the number of consecutive days you and this friend have snapped each other.
            Appears after 3 straight days.
          </p>
        </div>
        <div className="rounded-2xl border bg-card p-5">
          <p className="text-3xl">⌛</p>
          <h2 className="mt-2 font-semibold">Hourglass</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Warning: the 24-hour window is almost up (last ~4 hours). Either of you snapping resets the
            clock and clears it.
          </p>
        </div>
        <div className="rounded-2xl border bg-card p-5">
          <p className="text-3xl">💯</p>
          <h2 className="mt-2 font-semibold">100 emoji</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Shown next to the fire on day 100 as a milestone. After day 100 the regular number returns and
            keeps counting.
          </p>
        </div>
      </div>

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>What counts (and what doesn&apos;t)</h2>
          <ul>
            <li><strong>Counts:</strong> a photo or video snap sent directly to the friend, from the camera.</li>
            <li><strong>Doesn&apos;t count:</strong> chat messages, snaps sent to groups, Stories (even if they watch), Memories or camera-roll content sent as chats, and audio/video calls.</li>
            <li>Both people must snap within each rolling 24-hour window — one side snapping daily is not enough.</li>
          </ul>
        </div>
        <div>
          <h2>Restoring a lost streak, step by step</h2>
          <p>
            When a streak expires, Snapchat now shows a restore prompt directly in the chat: tap the expired
            streak (or the bar above the send field) and choose Restore. Everyone gets one free restore per
            month; after that, restores are a paid in-app purchase or a Snapchat+ perk. The restore option
            only appears for a limited time after the loss, so act within a day or two. If the streak
            vanished because of a Snapchat outage or failed delivery, submit a request at
            help.snapchat.com under &quot;My Snapstreaks disappeared&quot; — support restores legitimate
            cases for free regardless of the monthly limit.
          </p>
        </div>
        <div>
          <h2>Keeping long streaks safe</h2>
          <ul>
            <li>Snap right after waking up — it removes the deadline from the rest of the day.</li>
            <li>Agree on a &quot;streak snap&quot; convention with the friend (even a black screen counts).</li>
            <li>Watch for the hourglass on your friends list before bed.</li>
            <li>Traveling across time zones? The window is 24 real hours, not calendar days — snap early.</li>
          </ul>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building on social engagement data?"
        sub="Captapi returns profiles, posts, and engagement stats as clean JSON across TikTok, Instagram, YouTube, and more. Start free with 100 credits."
      />
    </>
  );
}
