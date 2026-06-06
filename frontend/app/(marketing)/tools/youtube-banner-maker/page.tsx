import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { LayoutTemplate, Type, Image as ImageIcon, Download } from "lucide-react";
import YouTubeBannerClient from "./YouTubeBannerClient";

const PATH = "/tools/youtube-banner-maker";
const TITLE = "Free YouTube Banner Maker — 2560×1440 Channel Art";
const DESC =
  "Create a YouTube banner (channel art) free in your browser. Correct 2560×1440 size with a safe-zone guide, gradient or photo backgrounds, text, and social handles — instant PNG export, no watermark.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "youtube banner maker",
    "youtube channel art maker",
    "youtube banner size 2024",
    "youtube banner size",
    "channel art template",
    "2560x1440 banner",
  ],
});

const FAQS = [
  { q: "What is the correct YouTube banner size?", a: "YouTube channel art should be 2560×1440 pixels. The most important content must sit inside the centered safe zone of 1546×423 pixels, which is the only area guaranteed to show on every device. This tool exports at 2560×1440 with a built-in safe-zone guide." },
  { q: "What is the YouTube banner safe zone?", a: "The safe zone is a 1546×423 pixel area in the center of the banner. TVs show the full image, desktops show a wide strip, and phones show only the safe zone — so keep your channel name and logo inside it." },
  { q: "Is this banner maker free?", a: "Yes. It is 100% free with no watermark, no sign-up, and no credit card. You can design and download unlimited banners." },
  { q: "Do you add a watermark?", a: "No. The exported PNG is clean — no logos, badges, or watermarks. The safe-zone guide is only shown in the editor and is never included in the download." },
  { q: "Are my uploaded images private?", a: "Yes. All rendering happens locally in your browser with the Canvas API, so your background photos are never uploaded to any server." },
  { q: "What file format does YouTube accept for banners?", a: "YouTube accepts JPG, PNG, GIF, and BMP up to 6MB. This tool exports a high-quality PNG that stays well within the limit." },
  { q: "Will my banner look right on mobile and TV?", a: "Yes, if you keep text inside the safe-zone guide. The full 2560×1440 background fills TV displays, while phones crop to the center strip — so the guide ensures your branding is always visible." },
  { q: "Can I add my social media handles?", a: "Yes. Add a handles line and it renders below your slogan inside the safe zone, so viewers around the world can find you on other platforms." },
  { q: "Do I need design software like Photoshop?", a: "No. Pick a template (Gaming, Music, Tech, Lifestyle), edit the text and colors, and download — no installs or design experience required." },
  { q: "How often should I update my banner?", a: "Refresh it when your branding, upload schedule, or focus changes. A clear, current banner builds trust with new visitors from any country." },
];

export default function Page() {
  const jsonLd = [
    breadcrumbLd([
      { name: "Home", path: "/" },
      { name: "Free Tools", path: "/tools" },
      { name: "YouTube Banner Maker", path: PATH },
    ]),
    webApplicationLd({ name: "YouTube Banner Maker", description: DESC, path: PATH, category: "DesignApplication" }),
    faqLd(FAQS),
  ];

  return (
    <div>
      <JsonLd data={jsonLd} />
      <ToolHero
        platform="YouTube"
        title="YouTube Banner Maker"
        subtitle="Design channel art at the exact 2560×1440 size with a live safe-zone guide so your branding looks perfect on phones, desktops, and TVs. Free and watermark-free."
      />

      <YouTubeBannerClient />

      <HowToUse
        steps={[
          { title: "Pick a template", text: "Start from Gaming, Music, Tech, or Lifestyle — or a custom gradient.", icon: <LayoutTemplate className="size-4" /> },
          { title: "Set the background", text: "Use a gradient, solid color, or upload your own image (auto-darkened for contrast).", icon: <ImageIcon className="size-4" /> },
          { title: "Add your text", text: "Enter your channel name, slogan, and handles — all kept inside the safe zone.", icon: <Type className="size-4" /> },
          { title: "Download PNG", text: "Export a 2560×1440 PNG (no guide, no watermark) and upload it to YouTube.", icon: <Download className="size-4" /> },
        ]}
      />

      <FAQSection faqs={FAQS} />

      <LongContent>
        <div>
          <h2>The free YouTube banner maker with a built-in safe zone</h2>
          <p>
            Your YouTube banner — also called channel art — is the first thing visitors see when they land on your channel
            page. It sets the tone, communicates what your channel is about, and either earns a subscribe or gets ignored.
            The tricky part is that YouTube displays your banner at different crops on different devices, which is why so
            many banners end up with cut-off logos and unreadable text. This free banner maker solves that with a live
            safe-zone guide and exact 2560×1440 export — no design software, no subscription, and no watermark.
          </p>
        </div>

        <div>
          <h3>YouTube banner size and the safe zone explained</h3>
          <p>
            The full banner canvas is <strong>2560×1440 pixels</strong>, but only the centered <strong>1546×423 pixel</strong>
            safe zone is guaranteed to appear on every device. Smart TVs show the entire 2560×1440 image, desktop browsers
            display a wide horizontal strip, and mobile phones crop down to the safe zone. The practical rule: put your
            channel name, logo, and key message inside the safe zone, and treat the rest of the canvas as decorative
            background. The dashed guide in this editor shows exactly where that boundary is.
          </p>
        </div>

        <div>
          <h3>What makes a great channel banner</h3>
          <ul>
            <li><strong>Lead with your channel name.</strong> Make it the largest, most legible element inside the safe zone.</li>
            <li><strong>Add a one-line value proposition.</strong> Tell visitors what they get and how often (&quot;Reviews · Tips · News&quot;).</li>
            <li><strong>Keep it on-brand.</strong> Reuse the colors and fonts from your thumbnails and logo for instant recognition.</li>
            <li><strong>Avoid clutter.</strong> Negative space reads as professional; a busy collage reads as amateur.</li>
            <li><strong>Test the crop.</strong> Toggle the safe zone on and off to preview the mobile versus TV experience.</li>
          </ul>
        </div>

        <div>
          <h3>Templates for every niche</h3>
          <p>
            The built-in templates give you a polished starting point for the most common channel types: high-contrast
            <strong> Gaming</strong>, atmospheric <strong>Music</strong>, clean and modern <strong>Tech</strong>, and warm,
            personal <strong>Lifestyle</strong>. Apply one, then customize the channel name, slogan, colors, and background
            to make it yours. Because every creator&apos;s brand is different, nothing is locked — swap any element freely.
          </p>
        </div>

        <div>
          <h3>Private, free, and watermark-free</h3>
          <p>
            Everything in this banner maker runs in your browser using the HTML Canvas API. Uploaded images never leave
            your device, there is no account to create, and your exported PNG is completely clean. Whether you are
            launching a channel in the United States, India, Nigeria, the Philippines, or anywhere else, you get a
            professional banner at zero cost.
          </p>
        </div>

        <div>
          <h3>Build your whole channel brand</h3>
          <p>
            A consistent banner pairs naturally with matching thumbnails, strong titles, and SEO-friendly descriptions —
            all available in our free tools collection. And when you want to study what is working across YouTube and other
            platforms, Captapi&apos;s API delivers transcripts, comments, follower counts, and engagement metrics in clean
            JSON so you can grow faster with data instead of guesswork.
          </p>
        </div>
      </LongContent>

      <ToolCTA />
    </div>
  );
}
