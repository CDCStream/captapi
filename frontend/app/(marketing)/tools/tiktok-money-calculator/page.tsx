import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Eye, Users, Calculator, DollarSign } from "lucide-react";
import TikTokMoneyCalculatorClient from "./TikTokMoneyCalculatorClient";

const PATH = "/tools/tiktok-money-calculator";
const TITLE = "TikTok Money Calculator";
const DESC =
  "How much does TikTok pay? Estimate Creator Rewards earnings per view and per video, plus brand deal rates by follower tier. Free calculator, no sign-up.";

export const metadata = buildMetadata({
  title: TITLE + " — How Much Does TikTok Pay Per View? | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "tiktok money calculator",
    "how much does tiktok pay",
    "how much does tiktok pay per view",
    "tiktok creator rewards calculator",
    "tiktok earnings calculator",
    "how much money do you make on tiktok",
    "tiktok pay per 1000 views",
  ],
});

const FAQS = [
  { q: "How much does TikTok pay per view?", a: "Through the Creator Rewards Program, TikTok pays roughly $0.40 to $1.00 per 1,000 qualified views for US creators — about $0.0004 to $0.001 per view. Only views on videos longer than one minute count as qualified, and rates vary with niche, region, and engagement." },
  { q: "How much does TikTok pay for 1 million views?", a: "At Creator Rewards rates of $0.40–$1.00 per 1,000 qualified views, one million qualified views earns roughly $400 to $1,000. High-engagement niches with strong watch time land near the top of that range; low-RPM niches near the bottom." },
  { q: "What are the requirements for the TikTok Creator Rewards Program?", a: "You need to be 18+, have at least 10,000 followers, at least 100,000 video views in the last 30 days, live in an eligible country, and post original videos longer than one minute. Views on shorter videos do not earn rewards." },
  { q: "How much do brand deals pay on TikTok?", a: "Sponsored post rates scale with audience size: nano creators (1K–10K followers) typically charge $20–$150 per video, micro creators (10K–50K) $150–$500, mid-tier (50K–500K) $500–$3,000, macro (500K–1M) $3,000–$10,000, and mega creators (1M+) $10,000–$50,000+. Engagement rate moves these numbers significantly." },
  { q: "What replaced the TikTok Creator Fund?", a: "TikTok retired the original Creator Fund in late 2023 and replaced it with the Creator Rewards Program, which pays significantly better but only counts videos over one minute. That is why RPMs jumped from roughly $0.02–$0.04 to $0.40–$1.00 per 1,000 views." },
  { q: "What other ways can you earn on TikTok?", a: "Beyond Creator Rewards and brand deals: LIVE gifts (viewers send coins that convert to Diamonds — see our TikTok Coin Calculator), TikTok Shop commissions, affiliate links, and selling your own products or services. Most full-time creators stack several of these." },
  { q: "Is this calculator's estimate exact?", a: "No — it is a realistic range based on published Creator Rewards RPMs and industry brand-rate surveys. Actual earnings depend on qualified-view share, audience region, niche RPM, and your engagement rate. Use it for planning, then compare against your Creator Center analytics." },
];

const STEPS = [
  { title: "Enter your views", text: "Per video or per month — qualified views drive Creator Rewards.", icon: <Eye className="size-4" /> },
  { title: "Add your followers", text: "Follower count sets your brand deal tier.", icon: <Users className="size-4" /> },
  { title: "See both estimates", text: "Creator Rewards range plus sponsored post benchmarks.", icon: <Calculator className="size-4" /> },
  { title: "Plan your income mix", text: "Stack rewards, deals, LIVE gifts, and TikTok Shop.", icon: <DollarSign className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "FinanceApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="TikTok"
        title={TITLE}
        subtitle="Estimate what TikTok actually pays — Creator Rewards earnings from your views, and what brands typically pay creators your size for a sponsored video."
      />

      <TikTokMoneyCalculatorClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>How TikTok creators actually get paid</h2>
          <p>
            TikTok income comes from four main streams. The Creator Rewards Program pays for qualified views
            on videos over one minute — roughly $0.40 to $1.00 per 1,000 views in the US. Brand deals pay per
            sponsored video and scale with your follower count and engagement. LIVE gifts convert viewer
            coins into Diamonds you can cash out. And TikTok Shop pays commissions for products you feature.
            The calculator above covers the first two, which are the most predictable.
          </p>
        </div>
        <div>
          <h2>Why the &quot;per view&quot; number varies so much</h2>
          <p>
            Two creators with identical view counts can earn very different amounts. Only qualified views
            count — the viewer must watch a 60-second-plus original video for enough time, in an eligible
            region. Niche matters too: finance and business content commands higher RPMs than entertainment,
            because advertisers pay more to reach those audiences. Finally, watch time and engagement shift
            your effective rate within TikTok&apos;s range. Treat the estimate as a band, then track your real
            RPM in Creator Center after a few weeks in the program.
          </p>
        </div>
        <div>
          <h2>Growing your earnings</h2>
          <ul>
            <li>Make videos longer than one minute so views actually qualify for rewards.</li>
            <li>Post in the best time windows — see our Best Time to Post on TikTok tool.</li>
            <li>Track your engagement rate (our free calculator) — brands check it before quoting.</li>
            <li>Convert LIVE viewers: gifts are pure margin once you can go live.</li>
            <li>Pitch brands directly with a simple media kit once you pass 10K followers.</li>
          </ul>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Tracking creator earnings at scale?"
        sub="Captapi returns TikTok profile stats, video views, engagement, and LIVE data as clean JSON — plus YouTube, Instagram, and Facebook. Start free with 100 credits."
      />
    </>
  );
}
