import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Gift, Layers, Calculator, DollarSign } from "lucide-react";
import GiftedSubCalculatorClient from "./GiftedSubCalculatorClient";

const PATH = "/tools/twitch-gifted-sub-calculator";
const TITLE = "Twitch Gifted Sub Calculator";
const DESC =
  "How much is 5, 50, or 100 gifted subs on Twitch? Calculate the exact cost by tier — and what the streamer actually earns after Twitch's revenue split.";

export const metadata = buildMetadata({
  title: TITLE + " — Cost of 50 & 100 Gifted Subs | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "how much is 100 gifted subs on twitch",
    "how much is 50 gifted subs on twitch",
    "twitch gifted sub calculator",
    "how much is a twitch sub",
    "gifted subs price",
    "twitch sub cost",
    "how much do streamers make from subs",
  ],
});

const FAQS = [
  { q: "How much is 100 gifted subs on Twitch?", a: "100 Tier 1 gifted subs cost $599 at the US web price of $5.99 each. At Tier 2 it's $999, and at Tier 3 $2,499. The streamer typically receives about half — roughly $300 from 100 Tier 1 gifts." },
  { q: "How much is 50 gifted subs on Twitch?", a: "50 Tier 1 gifted subs cost $299.50 in the US ($5.99 each). Tier 2 runs $499.50 and Tier 3 $1,249.50. There is no bulk discount — gifting 50 subs costs exactly 50 times the single-sub price." },
  { q: "How much is a single Twitch sub?", a: "In the US, Tier 1 is $5.99/month, Tier 2 $9.99, and Tier 3 $24.99 on the web. Twitch uses local pricing, so costs differ by country, and buying through the iOS/Android app costs more because of app-store fees." },
  { q: "How much does the streamer get from a gifted sub?", a: "The standard split gives streamers 50% of net sub revenue — about $3 from a $5.99 Tier 1 sub. Streamers in the Partner Plus program keep 60-70% on qualifying subs. Gifts are pooled into the same payout as regular subs." },
  { q: "Do gifted subs renew?", a: "No. A gifted sub lasts exactly one month (or the gifted duration) and never charges the recipient afterward. If the recipient wants to stay subscribed, they must subscribe themselves when the gift expires." },
  { q: "Is Prime Gaming a gifted sub?", a: "No — Prime Gaming gives Amazon Prime members one free Tier 1 sub each month to use themselves. It must be manually re-applied every month, can't be gifted, and pays the streamer at the standard rate." },
  { q: "Can I choose who receives my gifted subs?", a: "Both options exist: gift directly to a specific user from their name in chat, or gift a quantity to the community and Twitch distributes them randomly among eligible non-subscribed viewers in the channel." },
];

const STEPS = [
  { title: "Enter the gift count", text: "Or tap a quick preset — 1 to 100.", icon: <Gift className="size-4" /> },
  { title: "Pick the tier", text: "Tier 1, 2, or 3 — prices differ 4x.", icon: <Layers className="size-4" /> },
  { title: "See the total cost", text: "Exact US web price, no bulk discounts exist.", icon: <Calculator className="size-4" /> },
  { title: "See the streamer's cut", text: "Typical 50% split, up to 70% for Partner Plus.", icon: <DollarSign className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "FinanceApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Twitch"
        title={TITLE}
        subtitle="The real price of gifted subs — pick a quantity and tier to see what the gifter pays and what actually lands in the streamer's pocket."
      />

      <GiftedSubCalculatorClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>Quick reference: common gift amounts (Tier 1, US)</h2>
          <ul>
            <li>1 gifted sub — $5.99 (streamer ~$3.00)</li>
            <li>5 gifted subs — $29.95 (streamer ~$14.98)</li>
            <li>10 gifted subs — $59.90 (streamer ~$29.95)</li>
            <li>20 gifted subs — $119.80 (streamer ~$59.90)</li>
            <li>50 gifted subs — $299.50 (streamer ~$149.75)</li>
            <li>100 gifted subs — $599.00 (streamer ~$299.50)</li>
          </ul>
        </div>
        <div>
          <h2>Why prices vary</h2>
          <p>
            Twitch switched to country-specific pricing, so a Tier 1 sub costs less in most markets than the
            US $5.99 — the calculator uses US web prices as the reference. Purchases made inside the mobile
            apps add roughly 30% to cover app-store commissions, which is why chat regulars always tell you
            to sub from the browser. The streamer's share is calculated on net revenue after these fees,
            which is how two identical gift bombs can pay a streamer slightly different amounts.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building streamer analytics?"
        sub="Captapi returns Twitch channel data, streams, and VODs plus TikTok, YouTube, and Instagram stats as clean JSON. Start free with 100 credits."
      />
    </>
  );
}
