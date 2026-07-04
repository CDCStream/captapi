import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Layers, ListChecks, Gauge, CheckCircle2 } from "lucide-react";
import AmIBlockedClient from "./AmIBlockedClient";

const PATH = "/tools/am-i-blocked";
const TITLE = "Am I Blocked? Checker";
const DESC =
  "Find out if someone blocked you on Instagram, Snapchat, or WhatsApp. Check the signs you're seeing and get an instant verdict plus the definitive test for each platform.";

export const metadata = buildMetadata({
  title: TITLE + " — Instagram, Snapchat & WhatsApp | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "how to know if someone blocked you on instagram",
    "how to tell if someone blocked you on instagram",
    "how to see who blocked you on instagram",
    "how to know if someone blocked you on snapchat",
    "how to know if someone blocked you on whatsapp",
    "am i blocked on instagram",
    "blocked on instagram checker",
  ],
});

const FAQS = [
  { q: "How do I know if someone blocked me on Instagram?", a: "The clearest combination: their profile doesn't appear when you search their exact username, or it opens showing \u201cNo posts yet\u201d despite them being active, and your old DM thread shows their name as unavailable. Confirm by opening instagram.com/their-username in a logged-out or incognito browser — if the profile loads there but not in your account, you are blocked." },
  { q: "What's the difference between being blocked and them deactivating their Instagram?", a: "If the account is deactivated, it is invisible to everyone — including logged-out browsers and your friends' accounts. If you are blocked, the profile still exists for everyone else. That is why the incognito test and checking from a friend's account settle it." },
  { q: "How do I know if someone blocked me on Snapchat?", a: "Blocked: they disappear from your friends list AND username search finds nothing, while a friend's account can still find them. If you were only removed as a friend (not blocked), their username still shows up in your search results." },
  { q: "How do I know if someone blocked me on WhatsApp?", a: "Look for the combination: your messages permanently show one check mark, their profile photo and last seen disappear, calls never connect, and you get an error adding them to a group. Any single sign can be a privacy setting; all of them together strongly indicates a block. The group-add test is the most reliable single check." },
  { q: "Can I see a list of who blocked me?", a: "No platform provides a list of accounts that blocked you, and any app claiming to show one is a scam — often harvesting your login. The only way to know is checking the signs for a specific account, like this tool walks you through." },
  { q: "Will the person know I checked?", a: "No. Everything this checker asks you to verify — searching a username, viewing a profile from a logged-out browser, checking message ticks — is invisible to the other person." },
  { q: "Does restricting on Instagram look like blocking?", a: "No. If someone restricts you, you can still see their profile and posts normally — your comments just become invisible to others and your DMs land in their requests. Restriction is designed to be undetectable, while blocking hides their whole profile from you." },
];

const STEPS = [
  { title: "Pick the platform", text: "Instagram, Snapchat, or WhatsApp — each has different block behavior.", icon: <Layers className="size-4" /> },
  { title: "Verify each sign", text: "Open the app and check the signals one by one.", icon: <ListChecks className="size-4" /> },
  { title: "Read your verdict", text: "The checker weighs the evidence and estimates how likely a block is.", icon: <Gauge className="size-4" /> },
  { title: "Run the definitive test", text: "One conclusive check per platform confirms it.", icon: <CheckCircle2 className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "UtilitiesApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="All platforms"
        title={TITLE}
        subtitle="Suspect someone blocked you? Tick the signs you're seeing on Instagram, Snapchat, or WhatsApp and get an evidence-weighted verdict — plus the one test that settles it for sure."
      />

      <AmIBlockedClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>Why there's no official &quot;blocked&quot; notification</h2>
          <p>
            No platform tells you when you have been blocked — by design. Blocking is meant to be a quiet
            safety feature, so apps deliberately make a block look similar to an account being deleted,
            deactivated, or set to private. That ambiguity is why the reliable approach is combining several
            signals rather than trusting any single one, which is exactly what this checker does.
          </p>
        </div>
        <div>
          <h2>Blocked vs deactivated vs restricted</h2>
          <p>
            The three states get confused constantly. Blocked: their account exists for everyone except you.
            Deactivated or deleted: the account is gone for everyone — check from a logged-out browser or a
            friend&apos;s account to tell these apart. Restricted (Instagram) or muted: you can see everything
            normally and will probably never notice — these are designed to be invisible to you. If a profile
            loads fine in incognito but not from your account, that is the blocked signature.
          </p>
        </div>
        <div>
          <h2>Avoid &quot;who blocked me&quot; apps</h2>
          <p>
            Third-party apps promising a list of people who blocked you do not work — platforms expose no
            such data — and many exist to steal credentials or push subscriptions. Every check on this page
            uses only what you can see yourself in the official apps, and none of it notifies the other
            person.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need profile data programmatically?"
        sub="Captapi returns public profile info, posts, and stats as clean JSON across Instagram, TikTok, YouTube, and more — no OAuth, no scrapers. Start free with 100 credits."
      />
    </>
  );
}
