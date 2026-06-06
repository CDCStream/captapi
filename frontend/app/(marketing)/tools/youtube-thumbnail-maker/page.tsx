import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Palette, Type, Image as ImageIcon, Download } from "lucide-react";
import YouTubeThumbnailClient from "./YouTubeThumbnailClient";

const PATH = "/tools/youtube-thumbnail-maker";
const TITLE = "Free YouTube Thumbnail Maker — 1280×720, No Watermark";
const DESC =
  "Make click-worthy YouTube thumbnails free in your browser. Bold outlined text, gradient or photo backgrounds, ready-made templates, and instant 1280×720 PNG export — no watermark, no sign-up.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "youtube thumbnail maker",
    "free youtube thumbnail generator",
    "youtube thumbnail size",
    "thumbnail creator",
    "1280x720 thumbnail",
    "youtube thumbnail template",
  ],
});

const FAQS = [
  { q: "What is the correct YouTube thumbnail size?", a: "YouTube recommends 1280×720 pixels with a 16:9 aspect ratio, and a file under 2MB in JPG, PNG, or GIF. This tool exports at exactly 1280×720 PNG so your thumbnail is sharp on every device, from phones in India to TVs in the US." },
  { q: "Is this YouTube thumbnail maker really free?", a: "Yes — completely free with no watermark, no account, and no credit card. Everything runs in your browser, so you can make as many thumbnails as you want." },
  { q: "Do you add a watermark to my thumbnail?", a: "Never. The PNG you download is 100% yours, with no logo, badge, or watermark of any kind." },
  { q: "Does my image get uploaded to a server?", a: "No. Image editing happens entirely on your device using the HTML Canvas API. Your background photos never leave your browser, which keeps your content private." },
  { q: "Can I use my own photo as the background?", a: "Yes. Upload any JPG or PNG and it is auto-cropped to fill the 16:9 frame. You can also dim it so your text stays readable." },
  { q: "Which fonts work best for YouTube thumbnails?", a: "Bold, condensed fonts like Anton, Bebas Neue, and Impact read well at small sizes in the YouTube feed. All three are built in here." },
  { q: "Will the thumbnail look good on mobile?", a: "Most YouTube views happen on mobile, so keep text to 3–5 large words. The live preview shows roughly how it appears in the feed for viewers worldwide." },
  { q: "Can I make thumbnails for Shorts or other platforms?", a: "This tool is tuned for standard 16:9 YouTube thumbnails. For vertical Shorts (9:16) you can still export and crop, but a dedicated vertical canvas works better." },
  { q: "How do I get more clicks with my thumbnail?", a: "Use high contrast, a single clear focal point, expressive faces, and 3–5 bold words that create curiosity. Match the thumbnail promise to your title and content." },
  { q: "Do I need design skills to use it?", a: "No. Start from a template (Gaming, Vlog, Tutorial, Reaction, Before/After), change the text and colors, and download. Most creators finish in under two minutes." },
];

export default function Page() {
  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "Free Tools", path: "/tools" },
      { name: "YouTube Thumbnail Maker", path: PATH },
    ]),
    webApplicationLd({ name: "YouTube Thumbnail Maker", description: DESC, path: PATH, category: "DesignApplication" }),
    faqLd(FAQS),
  ];

  return (
    <div>
      <JsonLd data={jsonLd} />
      <ToolHero
        platform="YouTube"
        title="YouTube Thumbnail Maker"
        subtitle="Design scroll-stopping thumbnails in your browser — bold text, templates, and instant 1280×720 PNG export. Free, private, and watermark-free."
      />

      <YouTubeThumbnailClient />

      <HowToUse
        steps={[
          { title: "Pick a template", text: "Start from Gaming, Vlog, Tutorial, Reaction, or Before/After — or a blank gradient.", icon: <Palette className="size-4" /> },
          { title: "Add your background", text: "Choose a gradient, solid color, or upload your own photo. Dim it for readability.", icon: <ImageIcon className="size-4" /> },
          { title: "Write bold text", text: "Type your headline, pick a bold font, and set text and outline colors.", icon: <Type className="size-4" /> },
          { title: "Download PNG", text: "Export a crisp 1280×720 PNG with no watermark and upload it to YouTube.", icon: <Download className="size-4" /> },
        ]}
      />

      <FAQSection faqs={FAQS} />

      <LongContent>
        <div>
          <h2>The free YouTube thumbnail maker built for clicks</h2>
          <p>
            Your thumbnail is the single most important factor in whether someone clicks your video. Before anyone reads
            your title or watches a second of content, they judge your thumbnail in a crowded feed full of competing
            videos. This free YouTube thumbnail maker helps you win that split-second decision — without Photoshop, design
            skills, or a subscription. Everything runs in your browser, exports at the official 1280×720 resolution, and
            never adds a watermark.
          </p>
          <p>
            Whether you are a gaming creator in Brazil, a tutorial channel in India, a vlogger in the United Kingdom, or a
            small business in the United States, the principles of a high-CTR thumbnail are the same. This tool bakes those
            principles into ready-made templates so you can focus on your message instead of fighting with design software.
          </p>
        </div>

        <div>
          <h3>What the right YouTube thumbnail size is</h3>
          <p>
            YouTube&apos;s recommended thumbnail size is 1280×720 pixels (16:9 aspect ratio), with a minimum width of 640
            pixels and a file size under 2MB. This tool exports exactly at 1280×720 PNG, so your thumbnail stays crisp
            whether it is shown as a tiny preview on a phone or full-screen on a smart TV. Because most YouTube watch time
            now comes from mobile devices, the safest design choice is large text and one clear focal point that survives
            being shrunk down.
          </p>
        </div>

        <div>
          <h3>How to design a thumbnail that earns clicks</h3>
          <ul>
            <li><strong>Use 3–5 bold words.</strong> Short, punchy text is readable at any size. Long sentences disappear in the feed.</li>
            <li><strong>Maximize contrast.</strong> Bright text with a dark outline (or vice versa) pops against busy backgrounds. The built-in outline and shadow do this automatically.</li>
            <li><strong>Show emotion.</strong> Expressive faces and reactions consistently outperform flat product shots in viewer testing.</li>
            <li><strong>Keep one focal point.</strong> A single subject beats a cluttered collage. Let the background support — not compete with — your text.</li>
            <li><strong>Stay consistent.</strong> A recognizable color palette and font help returning viewers spot your videos instantly.</li>
          </ul>
        </div>

        <div>
          <h3>Templates for every kind of video</h3>
          <p>
            Each template is a proven starting point: <strong>Gaming</strong> uses high-energy reds and yellows; <strong>Vlog</strong>
            leans into soft, personal tones; <strong>Tutorial</strong> uses clean, trustworthy blues; <strong>Reaction</strong> pairs
            bold expressions with bright accents; and <strong>Before / After</strong> is built for transformations and results.
            Apply one with a single click, then swap the text, colors, and background to match your video.
          </p>
        </div>

        <div>
          <h3>Privacy-first and watermark-free</h3>
          <p>
            Unlike many online thumbnail generators, this tool processes everything locally with the HTML Canvas API. Your
            uploaded photos never touch a server, there is no account to create, and the exported PNG is completely clean —
            no watermark, no branding, no catch. Make one thumbnail or a hundred; it is always free.
          </p>
        </div>

        <div>
          <h3>From thumbnail to full content workflow</h3>
          <p>
            A great thumbnail is one piece of a bigger publishing workflow. Many creators pair it with a strong title,
            an SEO-friendly description, and the right hashtags — all of which you can generate with our other free tools.
            And when you are ready to scale beyond manual work, Captapi&apos;s API lets you pull transcripts, comments,
            and engagement metrics from YouTube, TikTok, Instagram, and Facebook to research what is working and double
            down on it.
          </p>
        </div>
      </LongContent>

      <ToolCTA />
    </div>
  );
}
