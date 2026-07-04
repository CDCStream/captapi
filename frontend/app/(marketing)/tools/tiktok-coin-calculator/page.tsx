import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Coins, ArrowDownUp, Gift, Calculator } from "lucide-react";
import TikTokCoinCalculatorClient from "./TikTokCoinCalculatorClient";

const PATH = "/tools/tiktok-coin-calculator";
const TITLE = "TikTok Coin Calculator";
const DESC =
  "Convert TikTok coins to USD and back in real time, see the price of every TikTok gift, and estimate how much money a creator earns from each gift. Free, no sign-up.";

export const metadata = buildMetadata({
  title: TITLE + " — Coins to USD, Gift Values & Creator Earnings | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "tiktok coin calculator",
    "tiktok coins to usd",
    "tiktok recharge calculator",
    "how much are tiktok coins",
    "tiktok gift value",
    "tiktok coins price",
    "monedas de tiktok calculadora",
    "tiktok coins recharge",
  ],
});

const FAQS = [
  {
    q: "How much is 1 TikTok coin worth?",
    a: "One TikTok coin costs roughly $0.0105 when you buy coins on tiktok.com, and about $0.0132 inside the iOS or Android app, where Apple and Google add their store fee. Prices vary slightly by region and by the size of the bundle you buy.",
  },
  {
    q: "How much money do creators actually make from TikTok gifts?",
    a: "When a viewer sends a gift, the coins convert into Diamonds, and TikTok gives the creator Diamonds worth about 50% of the coin value. In practice a creator nets roughly $0.005 per coin gifted, so a 100-coin gift is about $0.50 in their pocket before TikTok's payout threshold and taxes.",
  },
  {
    q: "How many coins is $100 on TikTok?",
    a: "At the tiktok.com rate of about $1.05 per 100 coins, $100 buys roughly 9,500 coins. Buying inside the app is more expensive at about $1.32 per 100 coins, so the same $100 gets you closer to 7,500 coins. Use the calculator above to check the current amount.",
  },
  {
    q: "Is it cheaper to buy TikTok coins on the website or in the app?",
    a: "It is cheaper on tiktok.com. Because Apple's App Store and Google Play take a cut of in-app purchases, TikTok charges more for coins bought inside the app. Recharging on the website through a browser avoids that surcharge and gives you more coins for the same money.",
  },
  {
    q: "What is the most expensive TikTok gift?",
    a: "The TikTok Universe gift is the most expensive at 44,999 coins, which costs the sender around $472 on the website. Other high-tier gifts include the Lion (26,999 coins) and the Rocket (20,000 coins).",
  },
  {
    q: "Are these TikTok coin prices exact?",
    a: "They are close estimates based on TikTok's published recharge bundles and the standard creator payout of about $0.005 per Diamond. TikTok occasionally adjusts regional pricing and promotions, so treat the numbers as accurate approximations rather than an exact invoice.",
  },
  {
    q: "Do TikTok coins expire?",
    a: "No. Coins you have purchased stay in your account until you spend them on gifts. They are tied to the account you bought them with and cannot be transferred to another account or refunded for cash.",
  },
];

const STEPS = [
  { title: "Enter coins or dollars", text: "Type a coin amount, or switch the direction to start from a USD budget.", icon: <Coins className="size-4" /> },
  { title: "Switch direction anytime", text: "Toggle between coins to USD and USD to coins with one click.", icon: <ArrowDownUp className="size-4" /> },
  { title: "Check any gift", text: "Search the gift table to see its coin cost and what the creator earns.", icon: <Gift className="size-4" /> },
  { title: "Compare app vs web", text: "See how much you save recharging on tiktok.com versus inside the app.", icon: <Calculator className="size-4" /> },
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
        subtitle="Convert TikTok coins to USD and back, see the price of every gift, and estimate what a creator earns from each one. Free, always-current, no sign-up."
      />

      <TikTokCoinCalculatorClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>How TikTok coins work</h2>
          <p>
            TikTok coins are the in-app currency you buy with real money to send virtual gifts during LIVE
            streams and on videos. You purchase coins in bundles, spend them on gifts, and the creator you
            gift receives Diamonds in return. The exchange is not one to one: TikTok keeps a share, so the
            money a viewer spends is always more than the money a creator ultimately withdraws.
          </p>
          <p>
            This calculator makes the whole chain transparent. It shows what a given number of coins costs you
            (on the website and in the app), and what the creator actually receives, so both sides of a gift
            can see the real value.
          </p>
        </div>

        <div>
          <h2>Why the app costs more than the website</h2>
          <p>
            When you buy coins inside the iOS or Android app, Apple and Google take roughly 30% of the
            transaction as a store fee, and TikTok passes that cost on. Recharging on tiktok.com in a browser
            skips the app-store cut, which is why the same dollar amount buys noticeably more coins there.
            If you send gifts regularly, buying on the website is the simplest way to stretch your budget.
          </p>
        </div>

        <div>
          <h2>What creators earn from gifts</h2>
          <p>
            Gifts convert into Diamonds, and TikTok awards creators Diamonds worth about half of the coin
            value. Creators can withdraw once they pass a minimum balance, and the cash-out rate works out to
            roughly $0.005 per coin gifted. So a flashy 1,000-coin Galaxy that costs a fan about $10.50 turns
            into roughly $5 for the creator before fees and taxes. Knowing this split helps creators set
            realistic goals and helps fans understand the impact of their support.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building TikTok analytics or a creator tool?"
        sub="Captapi gives you TikTok profile stats, video details, comments, and LIVE data as clean JSON — plus YouTube, Instagram, and Facebook. Start free with 100 credits, no card required."
      />
    </>
  );
}
