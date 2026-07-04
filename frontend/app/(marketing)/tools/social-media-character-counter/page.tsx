import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { PenLine, Gauge, CheckCircle2, Send } from "lucide-react";
import { CHAR_LIMITS, VIDEO_DURATIONS } from "@/lib/char-limits";
import CharCounterClient from "./CharCounterClient";

const PATH = "/tools/social-media-character-counter";
const TITLE = "Social Media Character Counter";
const DESC =
  "Type once, check every limit live — Instagram captions and bios, X posts, TikTok captions, YouTube titles, Discord messages, and more. Plus every video and story length limit for 2026.";

export const metadata = buildMetadata({
  title: TITLE + " — Check Every Platform Limit Live | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "social media character counter",
    "instagram caption character limit",
    "instagram bio character limit",
    "twitter character limit",
    "tiktok caption limit",
    "youtube title character limit",
    "discord character limit",
    "how long can an instagram story be",
    "how long can a tiktok be",
  ],
});

const FAQS = [
  { q: "What is the Instagram caption character limit?", a: "2,200 characters — but only about the first 125 show in the feed before the \u201cmore\u201d cutoff, so front-load your hook. Bios are capped at 150 characters and usernames at 30." },
  { q: "What is the character limit on X (Twitter)?", a: "280 characters for standard accounts. X Premium subscribers can post up to 25,000 characters, though only the first 280 show in the timeline before expansion." },
  { q: "How long can a TikTok caption be?", a: "4,000 characters — TikTok expanded it from 2,200 to make room for keyword-rich descriptions, which now matter for TikTok search ranking. Bios remain short at 80 characters." },
  { q: "How long can an Instagram story be?", a: "Up to 60 seconds per story card. If you upload a longer video, Instagram automatically splits it into consecutive 60-second segments. Stories disappear after 24 hours as usual." },
  { q: "How long can a TikTok video be?", a: "Up to 10 minutes when recording in-app, and eligible accounts can upload videos up to 60 minutes. TikTok Stories are capped at 15 seconds. For monetization, remember only videos over 1 minute earn Creator Rewards." },
  { q: "What is the YouTube title character limit?", a: "100 characters, but search results typically truncate around 70 — keep the essential keywords in the first 60-70 characters. Descriptions allow 5,000 characters and total tags 500." },
  { q: "Does this counter count emoji correctly?", a: "The counter uses the same character counting as most platforms (UTF-16 code units), so standard emoji count as 2 characters — matching what Instagram and X actually enforce. When in doubt near a limit, leave a few characters of buffer." },
];

const STEPS = [
  { title: "Paste your text", text: "Caption, bio, post, title — anything you're about to publish.", icon: <PenLine className="size-4" /> },
  { title: "Watch the live counts", text: "Every platform limit updates as you type.", icon: <Gauge className="size-4" /> },
  { title: "Check green vs red", text: "Instantly see which fields your text fits.", icon: <CheckCircle2 className="size-4" /> },
  { title: "Publish with confidence", text: "No more mid-upload truncation surprises.", icon: <Send className="size-4" /> },
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
        subtitle="One text box, every limit — see live whether your text fits Instagram captions, X posts, TikTok bios, YouTube titles, Discord messages, and 30+ other fields."
      />

      <CharCounterClient />

      <HowToUse steps={STEPS} />

      <section className="mt-14">
        <h2 className="text-2xl font-semibold">Video &amp; story length limits (2026)</h2>
        <div className="mt-4 overflow-x-auto rounded-2xl border">
          <table className="w-full text-sm">
            <thead className="bg-muted/60 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Platform</th>
                <th className="px-4 py-3 font-medium">Format</th>
                <th className="px-4 py-3 font-medium">Max length</th>
                <th className="px-4 py-3 font-medium">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {VIDEO_DURATIONS.map((d) => (
                <tr key={`${d.platform}-${d.format}`}>
                  <td className="px-4 py-3 font-medium">{d.platform}</td>
                  <td className="px-4 py-3">{d.format}</td>
                  <td className="whitespace-nowrap px-4 py-3">{d.duration}</td>
                  <td className="px-4 py-3 text-muted-foreground">{d.note ?? ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <LongContent>
        <div>
          <h2>All character limits at a glance</h2>
          <ul>
            {CHAR_LIMITS.map((p) => (
              <li key={p.id}>
                <strong>{p.label}:</strong>{" "}
                {p.limits.map((l) => `${l.field} ${l.limit.toLocaleString()}`).join(" \u00b7 ")}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h2>The limit that matters is the visible one</h2>
          <p>
            Most platforms cut text visually long before the hard limit: Instagram shows ~125 caption
            characters before &quot;more&quot;, LinkedIn ~210, Facebook ~477, and YouTube search truncates
            titles near 70. Write to the visible limit — hook first, context after the fold — and treat the
            hard cap as space for hashtags, credits, and keywords rather than the message itself.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Publishing at scale?"
        sub="Captapi returns posts, captions, and metadata as clean JSON across TikTok, Instagram, YouTube, and Facebook — ideal for content pipelines. Start free with 100 credits."
      />
    </>
  );
}
