import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { DollarSign, Eye, ListChecks, PlaySquare } from "lucide-react";
import YouTubeMoneyCalculatorClient from "./YouTubeMoneyCalculatorClient";

const PATH = "/tools/youtube-money-calculator";
const TITLE = "YouTube Money Calculator";
const DESC =
  "Estimate how much YouTube pays for your views. Real RPM ranges by niche for long-form videos and Shorts, monthly and yearly projections — free, no sign-up.";

export const metadata = buildMetadata({
  title: TITLE + " — How Much Does YouTube Pay per 1,000 Views? | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "youtube money calculator",
    "how much does youtube pay per 1000 views",
    "youtube cpm",
    "youtube rpm by niche",
    "youtube shorts pay",
    "how much do youtubers make",
    "youtube earnings calculator",
  ],
});

const FAQS = [
  { q: "How much does YouTube pay per 1,000 views?", a: "For long-form videos, creators typically earn $1-$8 per 1,000 monetized views depending on niche — finance and tech channels can hit $8-$22 RPM, while entertainment and music sit under $3. Shorts pay far less: about $0.05-$0.10 per 1,000 views from the pooled Shorts fund." },
  { q: "What's the difference between CPM and RPM?", a: "CPM is what advertisers pay per 1,000 ad impressions. RPM is what YOU earn per 1,000 video views after YouTube takes its 45% cut and accounts for views without ads. RPM is the number that matters for your income, and it's usually 40-60% lower than CPM." },
  { q: "Why do finance channels earn so much more?", a: "Ad rates follow advertiser competition. Banks, brokers, and SaaS companies pay premium CPMs ($30-$60+) to reach buyers with high lifetime value. Entertainment viewers are cheap to reach, so those CPMs stay low. Same views, 10x revenue difference." },
  { q: "What are the YouTube monetization requirements?", a: "The YouTube Partner Program requires 1,000 subscribers plus either 4,000 public watch hours in the last 12 months or 10 million Shorts views in the last 90 days. A lighter fan-funding tier (memberships, Supers) opens at 500 subscribers. Check your progress with our Creator Monetization Checker." },
  { q: "How much do YouTube Shorts pay?", a: "Shorts revenue comes from a shared pool split by view share, working out to roughly $0.05-$0.10 per 1,000 views — 10 million Shorts views might pay $500-$1,000. That's why most Shorts creators treat them as a funnel to long-form content and brand deals rather than a direct income source." },
  { q: "Does this calculator use my real channel data?", a: "No — it's an estimate from the view count and niche you enter, using publicly reported RPM ranges. Your actual RPM depends on audience geography (US/UK/AU views pay most), seasonality (Q4 is highest), ad formats enabled, and average watch time." },
];

const STEPS = [
  { title: "Pick your format", text: "Long-form ads and Shorts pay from completely different systems.", icon: <PlaySquare className="size-4" /> },
  { title: "Enter monthly views", text: "Use your typical monetized views per month.", icon: <Eye className="size-4" /> },
  { title: "Choose your niche", text: "RPM varies 10\u00d7 between finance and entertainment.", icon: <ListChecks className="size-4" /> },
  { title: "Read the range", text: "Monthly and yearly ad revenue estimates, instantly.", icon: <DollarSign className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "FinanceApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="YouTube"
        title={TITLE}
        subtitle="How much do your views actually pay? Pick your niche and format to see realistic RPM-based earnings — not inflated averages."
      />

      <YouTubeMoneyCalculatorClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>How YouTube ad revenue actually works</h2>
          <p>
            Advertisers bid for space on your videos (CPM). YouTube keeps 45% of long-form ad revenue and
            passes the rest to you — and since not every view shows an ad, your effective earnings per 1,000
            views (RPM) land well below the headline CPM. The single biggest lever is niche: an audience of
            investors is worth 10{"\u00d7"} an audience of meme viewers to advertisers, and rates follow.
            Geography matters almost as much — US, UK, Canadian, and Australian views pay several times more
            than views from most other countries.
          </p>
        </div>
        <div>
          <h2>Beyond AdSense</h2>
          <p>
            For most creators, ads are the floor, not the ceiling. Channel memberships, Super Thanks,
            affiliate links, sponsorships, and digital products routinely out-earn AdSense — sponsors alone
            often pay $20{"\u2013"}$50 per 1,000 expected views, an order of magnitude above ad RPM. Use the
            ad estimate here as your baseline, then layer brand deals on top (our TikTok Money Calculator
            shows comparable sponsorship benchmarks by follower tier).
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Tracking creator stats programmatically?"
        sub="Captapi returns YouTube channel stats, video data, and transcripts as clean JSON. Start free with 100 credits."
      />
    </>
  );
}
