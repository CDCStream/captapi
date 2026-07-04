import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Upload, Scaling, Eye, Download } from "lucide-react";
import TwitchEmoteResizerClient from "./TwitchEmoteResizerClient";

const PATH = "/tools/twitch-emote-resizer";
const TITLE = "Twitch Emote Resizer";
const DESC =
  "Resize any image to Twitch's required emote sizes — 112 × 112, 56 × 56, and 28 × 28 px — plus Discord's 128 × 128 emoji size. Free, in your browser, transparency preserved.";

export const metadata = buildMetadata({
  title: TITLE + " — 112, 56 & 28 px + Discord 128 px | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "twitch emote resizer",
    "twitch emote size",
    "twitch emotes",
    "resize twitch emote",
    "discord emote size",
    "discord emoji size",
    "emote maker twitch",
    "112x112 emote",
  ],
});

const FAQS = [
  { q: "What sizes do Twitch emotes need to be?", a: "Twitch requires three versions of every emote: 112 × 112, 56 × 56, and 28 × 28 pixels, all as PNG files under 1 MB with a transparent background. This tool generates all three from one upload." },
  { q: "What size are Discord emojis?", a: "Discord custom emojis are 128 × 128 pixels, up to 256 KB (PNG, JPG, or GIF for animated). We include a 128 px export precisely for this — one upload covers both platforms." },
  { q: "Does the emote stay transparent?", a: "Yes. If your source image has a transparent background (PNG or WebP with alpha), the resized PNGs keep it — the checkerboard behind each preview shows exactly what is transparent." },
  { q: "What happens if my image isn't square?", a: "The tool center-crops to a square before scaling, keeping the middle of the image. For best results, crop your emote to a square in your editor first so nothing important gets trimmed." },
  { q: "Why does my emote look blurry at 28 px?", a: "At 28 × 28 there are simply very few pixels. Emotes that survive small sizes use bold outlines, a single readable subject (usually a face), and high contrast. If details vanish, simplify the design rather than sharpening the export." },
  { q: "Is my image uploaded to a server?", a: "No. Resizing happens entirely in your browser using the canvas API — the image never leaves your device, which also makes the tool instant." },
  { q: "How many emote slots do Twitch channels get?", a: "Affiliates start with 1 emote slot and gain more through sub points (up to 5 for tier 1). Partners start at 6 and can unlock dozens. Follower emotes and Bits-tier emotes add extra slots on top." },
];

const STEPS = [
  { title: "Upload your art", text: "PNG with transparency works best — drag and drop or browse.", icon: <Upload className="size-4" /> },
  { title: "Auto-resize", text: "All four sizes are generated instantly in your browser.", icon: <Scaling className="size-4" /> },
  { title: "Check the 28 px preview", text: "If it reads at 28 px, it reads everywhere.", icon: <Eye className="size-4" /> },
  { title: "Download PNGs", text: "Grab each size and upload straight to Twitch or Discord.", icon: <Download className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "DesignApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Twitch"
        title={TITLE}
        subtitle="One upload, every required size: Twitch's 112, 56, and 28 px emote set plus Discord's 128 px emoji — with transparency preserved and nothing sent to any server."
      />

      <TwitchEmoteResizerClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>Why Twitch wants three sizes</h2>
          <p>
            Twitch renders emotes at different scales depending on context: 28 px in chat at normal density,
            56 px on high-DPI displays, and 112 px in the emote picker and cheer cards. Uploading all three
            (rather than letting one get scaled by the browser) keeps edges crisp everywhere. This tool uses
            high-quality downscaling so each size is generated from your full-resolution art, not from a
            smaller intermediate.
          </p>
        </div>
        <div>
          <h2>Design tips for emotes that read small</h2>
          <ul>
            <li>Design at 500 × 500 or larger, then let the resizer do the rest.</li>
            <li>One subject, big in the frame — faces and simple objects beat full scenes.</li>
            <li>Thick outlines (3–5 px at design size) survive downscaling; thin lines vanish.</li>
            <li>High contrast against both dark and light chat themes — test on both.</li>
            <li>Avoid text unless it is 2–4 huge letters; anything longer is unreadable at 28 px.</li>
          </ul>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building for streamers?"
        sub="Captapi returns Twitch channel info, streams, and VODs plus TikTok, YouTube, and Instagram data as clean JSON. Start free with 100 credits."
      />
    </>
  );
}
