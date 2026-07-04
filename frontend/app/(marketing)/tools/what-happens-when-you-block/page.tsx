import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Ban, Eye, MessageSquareOff, ShieldQuestion } from "lucide-react";
import BlockRulesClient from "./BlockRulesClient";

const PATH = "/tools/what-happens-when-you-block";
const TITLE = "What Happens When You Block Someone?";
const DESC =
  "Will they know? What can they still see? Every blocking rule for Instagram, Facebook, Snapchat, WhatsApp, and TikTok — notifications, DMs, old comments, and how to block without being obvious.";

export const metadata = buildMetadata({
  title: TITLE + " — Instagram, Facebook, Snapchat & More | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "what happens when you block someone on instagram",
    "if you block someone on instagram will they know",
    "if you block someone on facebook will they know",
    "if you block someone on snapchat will they know",
    "what happens when you block someone on whatsapp",
    "does blocking someone notify them",
  ],
});

const FAQS = [
  { q: "Will someone know if I block them?", a: "No platform sends a notification. But people can infer it: on Instagram your profile shows as empty or unfindable; on WhatsApp their messages stay on one grey check mark and your photo disappears; on Snapchat your username vanishes from search. WhatsApp leaks the most clues, Facebook and TikTok the fewest." },
  { q: "What happens when you block someone on Instagram?", a: "They aren't notified. Your profile becomes unfindable (or shows 'No posts yet'), your likes and comments disappear from their view, the DM thread stays but new messages never deliver, and you're removed from each other's follower lists. Instagram also offers to block new accounts they create." },
  { q: "If you block someone on Facebook, will they know?", a: "Not directly. You disappear from their search results, friends list, and Messenger. Old comments remain but your name becomes unclickable. Note: blocking automatically unfriends both sides, and unblocking does not restore the friendship." },
  { q: "If you block someone on Snapchat, will they know?", a: "No notification is sent. You disappear from their friends list and search. The tell: a mutual friend can still find your username in search while they can't — that difference reveals a block rather than a deleted account." },
  { q: "What happens when you block someone on WhatsApp?", a: "Their messages show a single grey check mark forever (sent, never delivered), your profile photo, about, and last-seen disappear for them, calls never connect, and they can't add you to groups. You still see each other's messages inside existing shared groups." },
  { q: "Is blocking different from restricting or muting?", a: "Yes. Muting hides their content from you only — they notice nothing and can still interact. Restricting (Instagram) hides their comments from others and moves DMs to requests without cutting access. Blocking severs the connection in both directions. If you want zero drama, restrict or mute first." },
  { q: "Can a blocked person still see my public profile?", a: "From a logged-out browser or a second account — usually yes, if your account is public. Blocks apply to the account, not the person. Going private is the only way to fully close that door." },
];

const STEPS = [
  { title: "Pick the platform", text: "Rules differ meaningfully between apps.", icon: <ShieldQuestion className="size-4" /> },
  { title: "Check the notification rule", text: "None of them notify \u2014 but clues differ.", icon: <Ban className="size-4" /> },
  { title: "See what they can still see", text: "Old comments, group chats, public pages.", icon: <Eye className="size-4" /> },
  { title: "Know the DM behavior", text: "Threads usually stay; delivery silently stops.", icon: <MessageSquareOff className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "ReferenceApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="General"
        title={TITLE}
        subtitle="Pick a platform to see exactly what blocking does — whether they're notified, what happens to your DMs and old comments, and what they can still see."
      />

      <BlockRulesClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>The universal rules of blocking</h2>
          <p>
            Across every major platform, three things are always true: no notification is ever sent, the
            block works in both directions (you also stop seeing them), and unblocking never restores what
            was severed — lost followers, friendships, and streaks stay lost. What differs is how much
            evidence leaks: WhatsApp&apos;s check marks make blocks easy to guess, while a Facebook or TikTok
            block can pass as a deleted account indefinitely.
          </p>
        </div>
        <div>
          <h2>Blocking vs. softer options</h2>
          <ul>
            <li><strong>Mute</strong> — you stop seeing them; they notice nothing at all. Zero risk.</li>
            <li><strong>Restrict (Instagram)</strong> — their comments need your approval and DMs go to requests. They keep full access and rarely notice.</li>
            <li><strong>Remove follower</strong> — quietly kicks them off a private account without blocking.</li>
            <li><strong>Block</strong> — full severance. Choose it for harassment, not just annoyance, because determined people can verify it.</li>
          </ul>
        </div>
        <div>
          <h2>Wondering if YOU were blocked?</h2>
          <p>
            The signs run in reverse: profiles that show &quot;No posts yet&quot;, messages stuck on one
            check mark, usernames that vanished from search. We built a separate step-by-step checker for
            that — see our <a href="/tools/am-i-blocked">Am I Blocked?</a> tool.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building on social data?"
        sub="Captapi returns public profiles, posts, and engagement stats as clean JSON across major platforms. Start free with 100 credits."
      />
    </>
  );
}
