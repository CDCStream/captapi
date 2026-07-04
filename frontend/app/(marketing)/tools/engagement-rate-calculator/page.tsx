import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { MousePointerClick, Calculator, BarChart3, Users } from "lucide-react";
import EngagementRateCalculatorClient from "./EngagementRateCalculatorClient";

const PATH = "/tools/engagement-rate-calculator";
const TITLE = "Engagement Rate Calculator";
const DESC =
  "Calculate your Instagram, TikTok, or YouTube engagement rate from likes, comments, shares, and followers or views — with benchmarks for what counts as good. Free, no sign-up.";

export const metadata = buildMetadata({
  title: TITLE + " — Instagram, TikTok & YouTube | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "engagement rate calculator",
    "instagram engagement rate calculator",
    "tiktok engagement rate calculator",
    "youtube engagement rate",
    "how to calculate engagement rate",
    "good engagement rate",
  ],
});

const FAQS = [
  { q: "How do you calculate engagement rate?", a: "The most common formula is total engagement divided by audience size, times 100. On Instagram that is (likes + comments) ÷ followers × 100. On TikTok and YouTube it is usually measured against views: (likes + comments + shares) ÷ views × 100. This calculator applies the right formula for the platform you pick." },
  { q: "What is a good engagement rate?", a: "It depends on the platform and your size. On Instagram, 1–3% is solid and above 3% is excellent. On TikTok, 3–6% by views is solid and 6%+ is excellent. On YouTube, 2–4% by views is solid and above 4% is excellent. Smaller accounts typically post higher rates than large ones." },
  { q: "Should I use followers or views for engagement rate?", a: "For feed platforms like Instagram, followers is the standard denominator. For video-first platforms like TikTok and YouTube, views is more meaningful because reach often far exceeds follower count. This tool switches automatically based on the platform." },
  { q: "Why do smaller accounts have higher engagement rates?", a: "Smaller creators tend to have tighter, more active communities, and their content is shown to a higher share of genuinely interested followers. As an account grows, its audience becomes broader and more passive, which usually lowers the percentage even as total engagement rises." },
  { q: "Does engagement rate include saves and shares?", a: "It can. Definitions vary — some marketers include saves and shares, others only likes and comments. Saves and shares are strong signals of value, so if you have those numbers it is worth calculating a version that includes them. This tool includes shares for TikTok, where they are a core metric." },
  { q: "How often should I check my engagement rate?", a: "Track it per post and as a rolling average over your last 10–20 posts. A single post can spike or dip, so trends matter more than one number. Comparing your average over time tells you whether your content and audience fit are improving." },
  { q: "Is a higher engagement rate always better?", a: "Generally yes, because it signals an active, interested audience that algorithms reward. But context matters: a huge account with a 1% rate can still drive more total actions than a tiny one at 10%. Use engagement rate alongside reach and conversions, not on its own." },
];

const STEPS = [
  { title: "Pick a platform", text: "Choose Instagram, TikTok, or YouTube to use the right formula.", icon: <BarChart3 className="size-4" /> },
  { title: "Enter your numbers", text: "Add likes, comments, and shares, plus followers or views.", icon: <MousePointerClick className="size-4" /> },
  { title: "See your rate", text: "Your engagement rate is calculated instantly as a percentage.", icon: <Calculator className="size-4" /> },
  { title: "Compare to benchmarks", text: "Check whether your rate is good for your platform and size.", icon: <Users className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "BusinessApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Creators"
        title={TITLE}
        subtitle="Work out your Instagram, TikTok, or YouTube engagement rate in seconds — then see how it stacks up against benchmarks for your platform and audience size. Free, no sign-up."
      />

      <EngagementRateCalculatorClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>What is engagement rate?</h2>
          <p>
            Engagement rate measures how actively your audience interacts with your content, expressed as a
            percentage. Instead of looking at raw likes, it weighs interactions against how many people could
            have engaged — your followers or your views. That makes it a fairer way to compare posts and
            creators of very different sizes, and it is the metric brands look at first when evaluating a
            creator for a partnership.
          </p>
        </div>
        <div>
          <h2>Which formula should you use?</h2>
          <p>
            On follower-based platforms like Instagram, the standard is (likes + comments) ÷ followers × 100.
            On video-first platforms like TikTok and YouTube, engagement is usually measured against views,
            because a video often reaches far more people than the creator has followers. TikTok also treats
            shares as a first-class signal, so its formula adds them in. This calculator picks the appropriate
            formula automatically when you choose a platform.
          </p>
        </div>
        <div>
          <h2>How to improve your engagement rate</h2>
          <ul>
            <li>Post when your audience is active — try our best-time-to-post tools.</li>
            <li>Ask a question or add a clear call to action to invite comments.</li>
            <li>Reply to comments quickly to keep conversations alive.</li>
            <li>Lean into the formats (Reels, Shorts, series) your audience engages with most.</li>
            <li>Prioritize saves and shares — they signal high value and boost reach.</li>
          </ul>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Measuring engagement across many accounts?"
        sub="Captapi returns likes, comments, views, and follower counts as clean JSON across TikTok, Instagram, YouTube, and more — perfect for automated engagement tracking. Start free with 100 credits."
      />
    </>
  );
}
