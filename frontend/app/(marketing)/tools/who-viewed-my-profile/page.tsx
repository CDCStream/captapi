import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Layers, MousePointerClick, Eye, ShieldCheck } from "lucide-react";
import WhoViewedClient from "./WhoViewedClient";

const PATH = "/tools/who-viewed-my-profile";
const TITLE = "Who Viewed My Profile?";
const DESC =
  "Can you see who viewed your Instagram, TikTok, Snapchat, Facebook, or LinkedIn profile? Pick a platform and content type for an instant, accurate answer — and learn which viewer lists actually exist.";

export const metadata = buildMetadata({
  title: TITLE + " — Instagram, TikTok, Facebook & LinkedIn | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "can you see who viewed your profile on instagram",
    "does instagram show profile views",
    "does tiktok show who viewed your profile",
    "tiktok profile views",
    "can you see who views your instagram story",
    "how to see who viewed your facebook profile",
    "who viewed my profile",
    "instagram profile views",
  ],
});

const FAQS = [
  { q: "Can you see who viewed your Instagram profile?", a: "No. Instagram does not show who visited your profile — not to anyone, on any plan. Professional accounts see an aggregate profile-visit count in insights, but never names. Story viewers are the exception: you can see exactly who watched your story for up to 48 hours after posting." },
  { q: "Does TikTok show who viewed your profile?", a: "Yes, conditionally. If you enable Profile View History (Settings \u2192 Privacy \u2192 Profile views), you can see who visited your profile in the last 30 days — but only visitors who also have the feature turned on. It's off by default and unavailable to accounts over 5,000 followers. Video views remain anonymous for everyone." },
  { q: "Can you see who viewed your Facebook profile?", a: "No. Facebook has confirmed for years that no such feature exists, and every app or link claiming to reveal profile viewers is against their terms — most are phishing scams. Story viewers are visible while the story is live." },
  { q: "Can you see who views your Instagram story?", a: "Yes. Open your story and swipe up to see every viewer by name. The list stays available for 48 hours after posting; after that, only the view count remains." },
  { q: "Who can see profile viewers on LinkedIn?", a: "LinkedIn is the one major platform with an official viewer list. Free accounts see a handful of recent viewers; Premium unlocks the full list from the last 365 days. Viewers browsing in private mode always appear as anonymous \u201cLinkedIn Member\u201d." },
  { q: "Do \u201cprofile stalker\u201d apps work?", a: "No. Instagram, TikTok, Facebook, and Snapchat expose no profile-visitor data to third parties, so no app can show it — regardless of what it promises. These apps typically harvest your login credentials or push paid subscriptions for fabricated results." },
  { q: "Can someone tell if I viewed THEIR profile?", a: "Follow the same rules in reverse: on Instagram, Facebook, and Snapchat they cannot tell. On TikTok they can only if you both have Profile View History on. On LinkedIn they can, unless you browse in private mode. And watching anyone's story always puts your name in their viewer list." },
];

const STEPS = [
  { title: "Pick a platform", text: "Instagram, TikTok, Snapchat, Facebook, or LinkedIn.", icon: <Layers className="size-4" /> },
  { title: "Find the content type", text: "Profile visits, stories, posts — each has different rules.", icon: <MousePointerClick className="size-4" /> },
  { title: "Read the verdict", text: "Green = viewer list exists, red = nobody can see it.", icon: <Eye className="size-4" /> },
  { title: "Browse accordingly", text: "Know when your views are visible before you look.", icon: <ShieldCheck className="size-4" /> },
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
        subtitle="The accurate answer for every platform — which viewer lists actually exist on Instagram, TikTok, Snapchat, Facebook, and LinkedIn, and which \u201cprofile stalker\u201d claims are scams."
      />

      <WhoViewedClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>The one-line answer per platform</h2>
          <p>
            Profile visits: invisible on Instagram, Facebook, and Snapchat; conditionally visible on TikTok
            (both sides opted in, under 5,000 followers); officially visible on LinkedIn. Stories: viewer
            lists exist everywhere they are offered — Instagram, TikTok, Snapchat, and Facebook all show
            story viewers by name while the story is live. Regular posts and videos: counts only, names
            never.
          </p>
        </div>
        <div>
          <h2>Why platforms hide profile viewers</h2>
          <p>
            Anonymous browsing drives engagement — people check profiles far more when nobody can tell.
            LinkedIn flips the logic on purpose: knowing recruiters viewed you is the product, and the full
            list is a Premium upsell. Stories sit in the middle: viewer lists reward posting without exposing
            casual profile browsing, which is exactly why every platform ships them.
          </p>
        </div>
        <div>
          <h2>Protecting your own browsing</h2>
          <ul>
            <li>Stories always record your view the moment the story loads — there is no safe preview in the official apps.</li>
            <li>On TikTok, turning Profile View History off hides your visits — and hides your visitors from you, symmetrically.</li>
            <li>On LinkedIn, private mode makes you anonymous but (on free accounts) blinds your own viewer list.</li>
            <li>Logged-out viewing works for public Instagram and TikTok profiles — see our profile viewer tools.</li>
          </ul>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need public profile data via API?"
        sub="Captapi returns public profiles, posts, stories metadata, and stats as clean JSON across Instagram, TikTok, YouTube, and more. Start free with 100 credits."
      />
    </>
  );
}
