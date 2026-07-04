import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { BadgeCheck, Eye, Palette, Search } from "lucide-react";

const PATH = "/tools/snapchat-plus-checker";
const TITLE = "Snapchat+ Checker";
const DESC =
  "How to tell if someone has Snapchat+ — the badge, custom app icons, story rewatch indicators, and every other visible sign of a Snapchat Plus subscription, explained.";

export const metadata = buildMetadata({
  title: TITLE + " — How to Tell if Someone Has Snapchat Plus | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "how to tell if someone has snapchat plus",
    "how to see if someone has snapchat plus",
    "how do you know if someone has snapchat premium",
    "can you tell if someone has snapchat premium",
    "what does snapchat premium do",
    "snapchat plus features",
    "snapchat plus badge",
  ],
});

const SIGNS = [
  {
    title: "The Snapchat+ badge on their profile",
    detail:
      "The clearest sign: a black Snapchat+ ghost badge next to their name on their profile. But it's optional — subscribers can hide it in settings, so no badge doesn't mean no subscription.",
    strength: "Definitive (when shown)",
  },
  {
    title: "A custom app icon or theme",
    detail:
      "If you ever see their phone and the Snapchat icon isn't the default yellow ghost, that's a Snapchat+ exclusive customization.",
    strength: "Strong",
  },
  {
    title: "They know you rewatched their story",
    detail:
      "Snapchat+ subscribers see a rewatch indicator showing how many friends rewatched their story. If someone mentions your rewatch, they almost certainly subscribe.",
    strength: "Strong",
  },
  {
    title: "A \u2764\ufe0f\u200d\ud83d\udd25 or custom Best Friends emoji",
    detail:
      "Snapchat+ lets users customize friend emojis and set a BFF background. Unusual, non-default friendship emojis on your chat with them hint at Plus.",
    strength: "Moderate",
  },
  {
    title: "Their story replies get pinned or they use exclusive chat colors",
    detail:
      "Chat wallpapers, message colors, and camera color borders are Plus perks — anything visually non-default in your chat with them points to a subscription.",
    strength: "Moderate",
  },
  {
    title: "Priority story replies",
    detail:
      "Replies from Snapchat+ users are pushed higher in celebrities' and creators' reply lists — hard to observe directly, but part of the package.",
    strength: "Weak",
  },
];

const FAQS = [
  { q: "How can you tell if someone has Snapchat+?", a: "The most reliable sign is the black Snapchat+ ghost badge on their profile page — though subscribers can hide it. Indirect signs: they know you rewatched their story (rewatch indicators are a Plus perk), custom friend emojis or chat colors in your conversation, and a non-default app icon on their phone." },
  { q: "Can someone hide that they have Snapchat+?", a: "Yes. The profile badge is opt-in, and most Plus features (pinned #1 BFF, ghost trails, priority replies) are invisible to other people. If someone hides the badge and doesn't mention rewatches, there is no certain way to know." },
  { q: "What does Snapchat+ (Premium) actually do?", a: "Highlights include: story rewatch indicators, seeing who rewatched, pinning a #1 BFF, custom app icons and chat colors, ghost trails on the Snap Map, Solar System (friend planets), longer video uploads, and priority story replies. It does NOT let anyone see who viewed their profile or bypass privacy settings." },
  { q: "Does Snapchat+ show who viewed your profile?", a: "No. Snapchat does not track profile views for anyone, Plus or not. Snapchat+ adds rewatch indicators for stories — a count of friends who rewatched — but never a list of profile visitors." },
  { q: "What is the Snapchat+ Solar System?", a: "A Plus feature showing your position in a friend's orbit: tapping their Best Friends or Friends badge reveals a planet — Mercury means you're their #1 closest friend, Venus #2, and so on. See our Snapchat Planets guide for the full order." },
  { q: "Can Snapchat+ users see rewatches from everyone?", a: "They see a rewatch count (and with settings, which friends rewatched) for their own stories only, and only when the viewer rewatches after the first view. It doesn't apply to public profiles they don't own." },
];

const STEPS = [
  { title: "Check their profile", text: "Look for the black Snapchat+ ghost badge next to their name.", icon: <BadgeCheck className="size-4" /> },
  { title: "Watch for rewatch mentions", text: "Knowing you rewatched a story is a Plus-only ability.", icon: <Eye className="size-4" /> },
  { title: "Spot customizations", text: "Custom emojis, chat colors, and app icons are Plus perks.", icon: <Palette className="size-4" /> },
  { title: "Accept the limits", text: "With the badge hidden, there's no guaranteed way to know.", icon: <Search className="size-4" /> },
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
        subtitle="Every visible sign that someone subscribes to Snapchat+ — ranked by how reliable each one actually is."
      />

      <div className="mt-8 space-y-3">
        {SIGNS.map((s, i) => (
          <div key={s.title} className="rounded-2xl border bg-card p-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="font-semibold">
                {i + 1}. {s.title}
              </h2>
              <span className="rounded-full border border-primary/30 bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary">
                {s.strength}
              </span>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{s.detail}</p>
          </div>
        ))}
      </div>

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>Why there&apos;s no foolproof check</h2>
          <p>
            Snapchat treats the subscription as a private perk: the badge is optional, and nearly every
            feature — pinned BFFs, ghost trails, priority replies — changes only what the subscriber sees.
            The signs above are the complete list of what leaks to the outside. The rewatch indicator is the
            most commonly noticed one, because Plus users tend to mention it.
          </p>
        </div>
        <div>
          <h2>Signs that do NOT mean Snapchat+</h2>
          <ul>
            <li>The green activity dot — everyone has it (it&apos;s an ordinary online indicator).</li>
            <li>Story viewer lists — all users see who viewed their story; only rewatch counts are Plus.</li>
            <li>Streak restores — everyone gets one free restore per month.</li>
            <li>The verified star on public figures — that&apos;s a creator badge, not a subscription.</li>
          </ul>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building on social data?"
        sub="Captapi returns public profiles, stories metadata, and stats as clean JSON across major platforms. Start free with 100 credits."
      />
    </>
  );
}
