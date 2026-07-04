import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Search, Filter, BookOpen, MessageSquare } from "lucide-react";
import { SLANG_TERMS } from "@/lib/slang-terms";
import SlangClient from "./SlangClient";

const PATH = "/tools/social-media-slang";
const TITLE = "Social Media Slang Dictionary";
const DESC =
  "What does PMO, NFS, GTS, or the green dot mean? Search " + SLANG_TERMS.length + "+ TikTok, Snapchat, Instagram, Discord, and Twitch slang terms with clear meanings and examples. Free.";

export const metadata = buildMetadata({
  title: TITLE + " — PMO, NFS, GTS & 60+ Terms Explained | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "pmo meaning tiktok",
    "nfs meaning snapchat",
    "what does nfs mean snapchat",
    "gts meaning",
    "what does the green dot on snapchat mean",
    "social media slang",
    "tiktok slang",
    "snapchat slang meanings",
    "what does idle mean on discord",
  ],
});

const FAQS = [
  { q: "What does PMO mean on TikTok?", a: "PMO most commonly means \u201cpiss me off\u201d — used when something annoys you, like \u201cslow walkers pmo\u201d. In some contexts it means \u201cput me on\u201d, i.e. recommend me something. Read the sentence: annoyance = piss me off, requests = put me on." },
  { q: "What does NFS mean on Snapchat?", a: "On Snapchat, NFS usually means \u201cno funny stuff\u201d (being serious) or \u201cnew friends\u201d when someone is looking to meet people. On Instagram posts, especially of items, it means \u201cnot for sale\u201d." },
  { q: "What does the green dot on Snapchat mean?", a: "The green dot next to someone's name or Bitmoji means they are currently online and active in the app. It is part of Snapchat's activity indicators; users can turn it off in settings, so no dot doesn't necessarily mean offline." },
  { q: "What does GTS mean?", a: "GTS usually means \u201cgo to sleep\u201d — a late-night way to end a conversation. Occasionally it stands for \u201cgood times\u201d when reminiscing." },
  { q: "What does idle mean on Discord?", a: "Idle (the yellow crescent moon) means the person is signed in but hasn't interacted with Discord for several minutes — the app sets it automatically, or users can set it manually. It's the in-between state between Online and Do Not Disturb." },
  { q: "What does restrict mean on Instagram?", a: "Restricting someone is a quiet alternative to blocking: their comments on your posts become visible only to them until you approve, their DMs move to your message requests, and they can't see when you've read messages or when you're online. They are not notified." },
  { q: "How fast does social media slang change?", a: "Very fast — most viral terms peak within months. We keep this dictionary updated with the terms people actually search for, so bookmark it and check back when a comment section stops making sense." },
];

const STEPS = [
  { title: "Search any term", text: "Type the slang word or even part of its meaning.", icon: <Search className="size-4" /> },
  { title: "Filter by platform", text: "TikTok, Snapchat, Instagram, Discord, Twitch, or X.", icon: <Filter className="size-4" /> },
  { title: "Read the meaning", text: "Plain-English definitions with usage context.", icon: <BookOpen className="size-4" /> },
  { title: "Reply with confidence", text: "Never get caught off guard in a comment section again.", icon: <MessageSquare className="size-4" /> },
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
        subtitle={`Search ${SLANG_TERMS.length}+ current slang terms from TikTok, Snapchat, Instagram, Discord, Twitch, and X — from PMO and NFS to aura, rizz, and vanish mode. Free, always updated.`}
      />

      <SlangClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>Every term in this dictionary</h2>
          <p>
            Here is the full list, so you can skim it end to end. Each entry above is searchable and filterable
            by platform.
          </p>
          <ul>
            {SLANG_TERMS.map((t) => (
              <li key={t.term}>
                <strong>{t.term}</strong> ({t.platforms.join(", ")}) — {t.meaning}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h2>Why slang differs by platform</h2>
          <p>
            Each platform's culture produces its own vocabulary. Snapchat slang leans toward messaging
            shorthand (GTS, WTW, DWU) because the app is chat-first. TikTok slang comes from trends and
            audio memes (rizz, gyat, canon event), so it changes fastest. Discord and Twitch share gamer
            vocabulary (AFK, poggers, copium) shaped by live chat speed. Knowing where a term comes from is
            half of understanding what it means — which is why every entry here is tagged by platform.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Analyzing comments at scale?"
        sub="Captapi returns TikTok, YouTube, Instagram, and Reddit comments as clean JSON — perfect for sentiment and trend analysis pipelines. Start free with 100 credits."
      />
    </>
  );
}
