import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Check, Copy } from "lucide-react";

const PATH = "/tools/instagram-caption-generator";
const TITLE = "Free Instagram Caption Generator";
const DESC =
  "Generate 10 scroll-stopping Instagram captions in your vibe — funny, aesthetic, short, or hard — complete with emoji and hashtags. AI-powered, free, no sign-up.";

export const metadata = buildMetadata({
  title: TITLE + " — Funny, Aesthetic & Short Captions | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "instagram caption generator",
    "captions for instagram post",
    "good instagram captions",
    "funny instagram captions",
    "instagram captions for girls",
    "hard instagram captions",
    "aesthetic captions for instagram",
    "short instagram captions",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "instagram-caption-generator",
  submitLabel: "Generate captions",
  fields: [
    {
      name: "topic",
      label: "What's the post about?",
      type: "text",
      required: true,
      placeholder: "e.g. beach sunset with friends",
      help: "Describe the photo or moment \u2014 more detail gets sharper captions.",
    },
    {
      name: "style",
      label: "Vibe",
      type: "select",
      options: [
        { value: "aesthetic", label: "Aesthetic" },
        { value: "funny", label: "Funny" },
        { value: "short and clean", label: "Short & clean" },
        { value: "hard / confident", label: "Hard / confident" },
        { value: "cute", label: "Cute" },
        { value: "motivational", label: "Motivational" },
      ],
    },
  ],
};

const FAQS = [
  { q: "How long can an Instagram caption be?", a: "Up to 2,200 characters, but only the first ~125 characters show in the feed before the \u201cmore\u201d cutoff. Put the hook or punchline first, and treat everything after the fold as bonus context and hashtags." },
  { q: "What makes a good Instagram caption?", a: "A strong first line (it's what shows before the fold), a voice that matches your photo's mood, and a reason to engage — a question, a joke, or a call to action. This generator writes captions with a hook up front and hashtags at the end for exactly that reason." },
  { q: "Do captions affect reach?", a: "Yes. Instagram's ranking weighs engagement — comments, saves, shares, and time spent. Captions that spark replies or make people pause measurably lift a post's distribution. Keyword-rich captions also help your post surface in Instagram's search results." },
  { q: "How many hashtags should I use?", a: "Instagram officially suggests 3 to 5 relevant hashtags rather than the maximum 30. Each generated caption ends with 3\u20135 fitting tags — swap any of them for niche tags your audience actually follows." },
  { q: "Can I edit a caption after posting?", a: "Yes — tap the three dots on your post and choose Edit. Note that edited posts may see a brief dip in distribution right after editing, so it's better to get the caption right before publishing." },
  { q: "Is this caption generator free?", a: "Yes. Generating, regenerating, and copying captions is completely free with no sign-up and no watermarks." },
];

const STEPS = [
  { title: "Describe the post", text: "A few words about the photo or moment is enough.", icon: <PenLine className="size-4" /> },
  { title: "Pick your vibe", text: "Funny, aesthetic, short, hard, cute, or motivational.", icon: <Sparkles className="size-4" /> },
  { title: "Generate 10 captions", text: "Each with a hook, fitting emoji, and 3\u20135 hashtags.", icon: <Check className="size-4" /> },
  { title: "Copy and post", text: "One click copies your favorite straight to the clipboard.", icon: <Copy className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "UtilitiesApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: "Instagram Caption Generator", path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Instagram"
        title="Instagram Caption Generator"
        subtitle="Describe your post, pick a vibe, and get 10 ready-to-paste captions with emoji and hashtags — aesthetic, funny, short, or hard. Free and unlimited."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>Why the first line decides everything</h2>
          <p>
            Instagram truncates captions after roughly 125 characters in the feed — everything else hides
            behind &quot;more&quot;. That means your caption is really a headline plus optional body. The
            generator front-loads the hook in every suggestion: the joke, the bold statement, or the
            question comes first, and context plus hashtags follow. When you edit a generated caption, keep
            that structure.
          </p>
        </div>
        <div>
          <h2>Matching caption to content</h2>
          <p>
            The same photo lands differently depending on the words under it. A sunset shot with an
            aesthetic one-liner reads as a mood; the same shot with a punchline reads as personality. Pick
            the vibe that matches what you want your grid to say about you — and stay consistent, because
            accounts with a recognizable voice earn more repeat engagement than accounts that change tone
            every post.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Working with Instagram data?"
        sub="Captapi returns Instagram profiles, posts, reels, and comments as clean JSON — plus TikTok, YouTube, and Facebook. Start free with 100 credits."
      />
    </>
  );
}
