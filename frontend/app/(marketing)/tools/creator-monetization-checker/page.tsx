import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Layers, Users, ListChecks, TrendingUp } from "lucide-react";
import MonetizationCheckerClient from "./MonetizationCheckerClient";

const PATH = "/tools/creator-monetization-checker";
const TITLE = "Creator Monetization Checker";
const DESC =
  "Do you qualify for TikTok Creator Rewards, the YouTube Partner Program, Instagram monetization, or Twitch Affiliate? Enter your followers and views to check every program's 2026 requirements instantly.";

export const metadata = buildMetadata({
  title: TITLE + " — TikTok, YouTube, Instagram & Twitch Requirements | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "tiktok monetization requirements",
    "tiktok monetization",
    "youtube partner program requirements",
    "how many views to get paid on youtube",
    "how many likes on tiktok to get paid",
    "instagram monetization requirements",
    "twitch affiliate requirements",
    "youtube shorts monetization",
  ],
});

const FAQS = [
  { q: "What are the TikTok monetization requirements?", a: "For the Creator Rewards Program: 18+, at least 10,000 followers, 100,000 video views in the last 30 days, and original videos longer than one minute, in an eligible country. LIVE gifts need only 1,000 followers (and 18+), which makes LIVE the fastest path to first earnings." },
  { q: "How many likes on TikTok do you need to get paid?", a: "None — likes are not a monetization requirement on TikTok. Payouts are driven by qualified views (Creator Rewards), gifts (LIVE), and sales (Shop). Likes matter indirectly because they push videos to more viewers." },
  { q: "How many views do you need to get paid on YouTube?", a: "Views alone don't trigger payment — you need to join the Partner Program: 1,000 subscribers plus either 4,000 public watch hours in 12 months or 10 million public Shorts views in 90 days. A lighter tier at 500 subscribers unlocks fan funding (memberships, Super Thanks) but not ad revenue." },
  { q: "What are the YouTube Shorts monetization rules?", a: "Shorts ad revenue requires full Partner Program membership — 1,000 subs + 10M Shorts views in 90 days (or the 4,000 watch-hour route). Shorts revenue is pooled and split by view share, so RPMs are far lower than long-form." },
  { q: "What does Instagram monetization require?", a: "Subscriptions require 10,000 followers and a professional account (18+, eligible country). Gifts on Reels open at 5,000 followers. Instagram's bonus programs are invite-only — the app notifies eligible professional accounts directly." },
  { q: "What are the Twitch Affiliate requirements?", a: "In the last 30 days: 50 followers, 500 minutes streamed, 7 unique broadcast days, and an average of 3 concurrent viewers. Partner raises the bar to 75 average concurrent viewers and 12 streaming days. Affiliate unlocks subs, Bits, and ads." },
  { q: "I meet the numbers — why am I still not approved?", a: "Thresholds are necessary but not sufficient. Platforms also check age (18+), region, content originality, and community-guideline standing, and most run a manual or automated review after you apply. Strikes, reused content, and artificial engagement are the most common rejection reasons." },
];

const STEPS = [
  { title: "Pick your platform", text: "TikTok, YouTube, Instagram, or Twitch.", icon: <Layers className="size-4" /> },
  { title: "Enter your stats", text: "Followers plus the platform's key view metric.", icon: <Users className="size-4" /> },
  { title: "See what you qualify for", text: "Every program marked qualified or missing-X.", icon: <ListChecks className="size-4" /> },
  { title: "Close the gap", text: "The checker shows exactly how far each program is.", icon: <TrendingUp className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "FinanceApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="All platforms"
        title={TITLE}
        subtitle="Enter your followers and views and instantly see which monetization programs you qualify for — TikTok Creator Rewards, YouTube Partner Program, Instagram subscriptions, Twitch Affiliate, and more."
      />

      <MonetizationCheckerClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>The fastest first dollar on each platform</h2>
          <p>
            If you're starting from zero, the thresholds rank the paths clearly: Twitch Affiliate (50
            followers, 3 average viewers) and TikTok LIVE (1,000 followers) come first, then YouTube's fan
            funding tier at 500 subscribers, then the big ad-revenue programs — TikTok Creator Rewards at
            10,000 followers and YouTube Partner at 1,000 subs plus watch-time. Brand deals have no
            threshold at all: nano creators with 1,000 engaged followers land paid posts before any platform
            program pays out (see our TikTok Money Calculator for rates).
          </p>
        </div>
        <div>
          <h2>Requirements are floors, not guarantees</h2>
          <p>
            Every program also applies checks the numbers don't capture: you must be 18+, in an eligible
            country, posting original content, and free of community-guideline strikes. Reused or
            watermarked content is the most common silent blocker — platforms detect it and quietly exclude
            those videos from monetization even after approval. Hitting the thresholds with original content
            in one niche remains the reliable route.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Tracking creator stats programmatically?"
        sub="Captapi returns follower counts, views, and engagement as clean JSON across TikTok, YouTube, Instagram, and Twitch. Start free with 100 credits."
      />
    </>
  );
}
