import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Download, Layers, Sparkles, Upload, Wand2 } from "lucide-react";
import YouTubeThumbnailClient from "./YouTubeThumbnailClient";

const PATH = "/tools/youtube-thumbnail-maker";
const TITLE = "Free AI YouTube Thumbnail Maker";
const DESC =
  "Generate AI YouTube thumbnails from a title, style, optional portrait, and optional reference image. Create 16:9 click-ready thumbnail variations free, no sign-up required.";

export const metadata = buildMetadata({
  title: TITLE + " | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "free ai youtube thumbnail maker",
    "ai youtube thumbnail generator",
    "youtube thumbnail maker no sign up",
    "youtube thumbnail generator",
    "video thumbnail maker",
    "youtube thumbnail size 1280x720",
    "ai thumbnail maker",
  ],
});

const FAQS = [
  {
    q: "What does the Free AI YouTube Thumbnail Maker do?",
    a: "It turns your video title or topic into high-contrast 16:9 YouTube thumbnail concepts. You can choose a style, add a target audience, upload a portrait, and upload a reference thumbnail so the AI can generate multiple click-ready variations.",
  },
  {
    q: "Is this really an AI thumbnail generator, not just a template editor?",
    a: "Yes. The page now uses an image generation model to create original thumbnail images. It is not limited to preset canvas templates, although the prompt still follows YouTube thumbnail best practices such as strong contrast, simple composition, and readable text.",
  },
  {
    q: "Can I upload my face or portrait?",
    a: "Yes. Upload a selfie or creator portrait and the AI will use it as the main subject of the thumbnail, removing the need for manual cutouts in Photoshop or Canva. For best results, use a clear front-facing image with good lighting.",
  },
  {
    q: "Can I clone the style of another thumbnail?",
    a: "You can upload a reference thumbnail so the AI can learn the layout, contrast, framing, and visual mood. The tool asks the model to create an original result rather than copying logos, exact text, or protected artwork.",
  },
  {
    q: "What size are the generated thumbnails?",
    a: "The model is instructed to generate a 16:9 YouTube thumbnail suitable for 1280x720 usage. Downloaded files can be uploaded to YouTube as custom thumbnails and should remain readable on mobile previews.",
  },
  {
    q: "How many thumbnail variations can I generate?",
    a: "You can generate one, two, or three variations at a time. Multiple outputs are useful for A/B testing different hooks, emotions, compositions, and visual styles before you publish.",
  },
  {
    q: "Do I need design skills?",
    a: "No. You only need a video topic or title. The AI handles composition, color, focal point, text hierarchy, and overall thumbnail style. Optional reference images help when you want a specific look.",
  },
  {
    q: "Can I use the thumbnails for monetized YouTube videos?",
    a: "The tool is designed for original, commercially usable outputs based on your prompt and uploaded assets. You should only upload portraits, brand assets, or references that you have the right to use.",
  },
  {
    q: "Why does a good YouTube thumbnail matter?",
    a: "Thumbnails affect click-through rate. A clearer hook, stronger emotion, and more readable design can help a video earn more clicks from impressions, which can support more views and better distribution.",
  },
  {
    q: "Do I need to sign up?",
    a: "No sign-up is required for the free tool. Captapi also offers APIs for creators and teams who want to automate transcripts, summaries, comments, stats, and other social data workflows.",
  },
];

const STEPS = [
  { title: "Enter your video idea", text: "Paste the title, topic, or hook you want the thumbnail to sell.", icon: <Wand2 className="size-4" /> },
  { title: "Pick a CTR style", text: "Choose a visual direction such as challenge, tutorial, gaming, tech, or premium brand.", icon: <Sparkles className="size-4" /> },
  { title: "Add optional images", text: "Upload a portrait for creator branding or a reference thumbnail for layout inspiration.", icon: <Upload className="size-4" /> },
  { title: "Download variations", text: "Generate multiple 16:9 thumbnails and save the strongest option for YouTube.", icon: <Download className="size-4" /> },
];

const FEATURES = [
  { title: "AI video hook composition", text: "The prompt focuses the model on one clear emotional hook so the thumbnail communicates instantly at small preview size." },
  { title: "Smart portrait integration", text: "Creator faces help channels become recognizable. Upload a portrait and the model will build the thumbnail around it." },
  { title: "Reference style matching", text: "Use a thumbnail you admire as visual guidance for contrast, framing, mood, and layout without directly copying it." },
  { title: "A/B test ready", text: "Generate multiple distinct outputs so you can test curiosity, urgency, transformation, or authority angles." },
  { title: "YouTube-first sizing", text: "Outputs are composed as 16:9 thumbnails suitable for the standard 1280x720 YouTube workflow." },
  { title: "No manual editing workflow", text: "Skip timeline scrubbing, face cutouts, font pairing, and layer-by-layer thumbnail design." },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="YouTube"
        title={TITLE}
        subtitle="Generate click-ready AI thumbnails from your title, style, portrait, and reference image. Create multiple 16:9 variations for YouTube without Photoshop, Canva, or sign-up."
      />

      <YouTubeThumbnailClient />

      <HowToUse steps={STEPS} />

      <section className="mt-16">
        <h2 className="text-2xl font-semibold">Why choose this AI YouTube thumbnail maker?</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => (
            <div key={feature.title} className="rounded-xl border bg-card p-5">
              <div className="mb-3 flex size-10 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Layers className="size-5" />
              </div>
              <h3 className="font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{feature.text}</p>
            </div>
          ))}
        </div>
      </section>

      <LongContent>
        <div>
          <h2>AI thumbnails that help viewers understand the hook fast</h2>
          <p>
            A YouTube thumbnail has one job: make the right viewer stop scrolling and understand why the video is worth clicking. This free AI YouTube Thumbnail Maker is built around that job. Instead of starting from a blank canvas, you give the tool your video title, audience, and desired emotion. The AI then composes a 16:9 thumbnail around a clear focal point, strong contrast, and short readable text.
          </p>
          <p>
            The workflow is designed for creators who want the speed of an AI thumbnail generator without writing complex prompts. Choose a style such as gaming reaction, clean tech tutorial, business authority, or premium brand. Add a portrait if your channel uses creator-led thumbnails. Upload a reference if you want the model to understand a layout or visual mood you already like.
          </p>
        </div>

        <div>
          <h2>From portrait and reference image to custom YouTube thumbnail</h2>
          <p>
            Many high-performing thumbnails use a recognizable face, exaggerated emotion, and a simple visual story. Manually cutting out a face, matching lighting, and balancing text can take longer than editing the video itself. With the portrait upload, the tool can use your image as the primary subject and blend it into a fresh thumbnail composition.
          </p>
          <p>
            Reference images are useful when you want to follow a proven trend without copying it. The AI looks at composition signals such as subject placement, contrast, spacing, and mood, then creates an original thumbnail for your own topic. That makes it easier to test styles from your niche while keeping the output unique.
          </p>
        </div>

        <div>
          <h2>Generate multiple options for thumbnail A/B testing</h2>
          <p>
            Thumbnail testing works best when each option has a different angle. One version might focus on surprise, another on a before-and-after transformation, and another on expert authority. This tool can create up to three variations in one run, giving you more than one creative direction to compare before publishing.
          </p>
          <ul>
            <li>Use curiosity for videos with a surprising result or reveal.</li>
            <li>Use transformation for tutorials, fitness, finance, and case studies.</li>
            <li>Use authority for reviews, explainers, SaaS, education, and B2B videos.</li>
            <li>Use reaction for entertainment, gaming, commentary, and challenge formats.</li>
          </ul>
        </div>

        <div>
          <h2>Built for YouTube thumbnail best practices</h2>
          <p>
            The generator is instructed to avoid clutter, tiny text, weak contrast, misleading badges, and watermark-style elements. It favors a single clear focal point, readable text, and bold visual hierarchy. The output is composed in 16:9 format for the standard YouTube thumbnail workflow, so it works for long-form videos and many YouTube surfaces where a horizontal preview is shown.
          </p>
          <p>
            A strong thumbnail cannot rescue a weak video, but it can stop a strong video from being ignored. Use the generated options as a fast creative starting point, then publish the version that best matches your title, promise, and audience intent.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need more than thumbnails?"
        sub="Captapi gives you APIs for YouTube, TikTok, Instagram, and Facebook transcripts, summaries, comments, stats, and creator workflows. Start with free credits and automate the parts that come after the thumbnail."
      />
    </>
  );
}
