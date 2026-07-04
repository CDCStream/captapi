import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { MousePointerClick, Layers, Bell, CheckCircle2 } from "lucide-react";
import ScreenshotCheckerClient from "./ScreenshotCheckerClient";

const PATH = "/tools/screenshot-notification-checker";
const TITLE = "Screenshot Notification Checker";
const DESC =
  "Does Instagram notify when you screenshot a story or post? What about Snapchat, TikTok, Facebook, or WhatsApp? Pick a platform and action for an instant, up-to-date answer.";

export const metadata = buildMetadata({
  title: TITLE + " — Instagram, Snapchat, TikTok, Facebook & WhatsApp | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "does instagram notify when you screenshot a story",
    "does instagram notify when you screenshot a post",
    "does instagram show screenshots",
    "does tiktok notify screenshots",
    "does facebook notify screenshots",
    "does snapchat notify screenshots",
    "screenshot instagram story",
    "can people see if you screenshot their instagram story",
  ],
});

const FAQS = [
  { q: "Does Instagram notify when you screenshot a story?", a: "No. Instagram does not notify anyone when you screenshot their story, including close-friends stories. The poster can see that you viewed the story in their viewers list, but nothing marks you as having taken a screenshot." },
  { q: "Does Instagram notify when you screenshot a post or reel?", a: "No. Screenshotting a feed post, carousel, or reel never sends a notification to the creator. The same goes for screenshotting someone's profile page." },
  { q: "When DOES Instagram notify a screenshot?", a: "Only in one case: disappearing photos or videos sent in DMs with 'view once' or 'allow replay' mode. If you screenshot one of those, a shutter icon appears next to the message and the sender is notified." },
  { q: "Does Snapchat notify screenshots?", a: "Yes, almost everywhere. Screenshotting a snap, a story, or a chat conversation all trigger notifications — the other person sees a screenshot icon or an explicit '… took a screenshot!' message. Snapchat is the strictest major platform about this." },
  { q: "Does TikTok notify screenshots?", a: "No. TikTok does not notify creators when you screenshot or screen-record videos, stories, profiles, or direct messages as of 2026." },
  { q: "Does Facebook notify screenshots?", a: "No for posts, stories, profiles, and regular Messenger chats. The one exception is Messenger's vanish mode and end-to-end encrypted disappearing messages, where a notice appears in the chat when someone takes a screenshot." },
  { q: "Does WhatsApp notify screenshots?", a: "No — WhatsApp never notifies screenshots of chats, statuses, or profile photos. For view-once photos and videos, WhatsApp takes a different approach: it blocks the screenshot entirely, so you get a black image instead." },
  { q: "Can an app really detect screenshots?", a: "Yes. Both iOS and Android give apps a signal when a screenshot is taken inside the app, which is how Snapchat and Instagram's DM detection work. Detection only applies inside that app — the platform cannot see screenshots you take of other apps." },
];

const STEPS = [
  { title: "Pick a platform", text: "Instagram, Snapchat, TikTok, Facebook, or WhatsApp.", icon: <Layers className="size-4" /> },
  { title: "Find the action", text: "Story, post, DM, profile — each behaves differently.", icon: <MousePointerClick className="size-4" /> },
  { title: "Read the verdict", text: "Green means no notification, red means the other person is alerted.", icon: <Bell className="size-4" /> },
  { title: "Screenshot with confidence", text: "Know the rules before you capture anything sensitive.", icon: <CheckCircle2 className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "ReferenceApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="All platforms"
        title={TITLE}
        subtitle="Find out instantly whether Instagram, Snapchat, TikTok, Facebook, or WhatsApp notifies the other person when you take a screenshot — for stories, posts, DMs, and more."
      />

      <ScreenshotCheckerClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>The short version</h2>
          <p>
            Only Snapchat notifies screenshots broadly. Instagram, TikTok, Facebook, and WhatsApp do not
            notify screenshots of normal content — stories, posts, profiles, and regular chats are all safe
            to capture without an alert. The exceptions are disappearing content: Instagram&apos;s view-once
            DMs and Messenger&apos;s vanish mode notify the sender, and WhatsApp blocks view-once screenshots
            outright.
          </p>
        </div>
        <div>
          <h2>Why disappearing content is the exception</h2>
          <p>
            Platforms treat ephemeral messages as a privacy promise: the sender chose content that should
            vanish after viewing. Both iOS and Android expose an in-app screenshot signal, and platforms use
            it exactly where that promise applies. That is why the same app can ignore a story screenshot but
            flag a view-once photo seconds later. If a chat is in a disappearing mode, assume screenshots are
            either reported or blocked.
          </p>
        </div>
        <div>
          <h2>Rules change — check before you rely on them</h2>
          <p>
            These behaviors are current as of 2026, but platforms adjust privacy features regularly.
            Instagram briefly tested story screenshot alerts back in 2018 before dropping the idea, and
            WhatsApp added view-once screenshot blocking years after launch. We keep this page updated as
            platforms change their rules, so bookmark it if screenshots are part of your workflow.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building tools on social data?"
        sub="Captapi returns profiles, posts, stories metadata, comments, and stats as clean JSON across TikTok, Instagram, YouTube, Facebook, and more. Start free with 100 credits."
      />
    </>
  );
}
