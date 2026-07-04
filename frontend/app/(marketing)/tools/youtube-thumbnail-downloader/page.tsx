import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Link2, ImageIcon, Download, Ruler } from "lucide-react";
import YouTubeThumbnailDownloaderClient from "./YouTubeThumbnailDownloaderClient";

const PATH = "/tools/youtube-thumbnail-downloader";
const TITLE = "YouTube Thumbnail Downloader";
const DESC =
  "Download any YouTube video or Shorts thumbnail in full HD (1280×720) and every other size. Paste a URL, preview, and save instantly. Free, no sign-up.";

export const metadata = buildMetadata({
  title: TITLE + " — Grab HD Thumbnails (1280×720) | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "youtube thumbnail downloader",
    "youtube thumbnail grabber",
    "download youtube thumbnail",
    "youtube thumbnail size",
    "youtube thumbnail dimensions",
    "youtube thumbnail hd",
    "get youtube thumbnail",
  ],
});

const FAQS = [
  { q: "What size is a YouTube thumbnail?", a: "The full-resolution YouTube thumbnail is 1280×720 pixels (16:9), which is the size YouTube recommends creators upload. This tool also gives you the smaller stored versions: 640×480, 480×360, 320×180, and 120×90." },
  { q: "How do I download a YouTube thumbnail?", a: "Paste the video's URL or its 11-character video ID into the box above and press Get thumbnails. You will see a preview plus every available size with a Save button. Click Save to download the image, or Open to view it in a new tab." },
  { q: "Can I download thumbnails from YouTube Shorts?", a: "Yes. Paste a Shorts URL (youtube.com/shorts/…) and the tool extracts the video ID and pulls the thumbnails exactly like a regular video." },
  { q: "Why is the Max HD thumbnail not available for some videos?", a: "The 1280×720 maxresdefault image only exists if the uploader had a high-resolution thumbnail. Older or lower-quality uploads may only have the smaller sizes, so the preview automatically falls back to the next best size." },
  { q: "Is it legal to download YouTube thumbnails?", a: "Downloading a thumbnail for personal reference, research, or fair-use commentary is generally fine. Thumbnails are copyrighted by their creators, so do not republish someone else's thumbnail as your own or use it commercially without permission." },
  { q: "Do I need an account or extension?", a: "No. This is a free browser tool with no sign-up, no software, and no extension. It reads the public thumbnail image that YouTube serves for every video." },
  { q: "What are the correct thumbnail dimensions for uploading?", a: "Upload custom thumbnails at 1280×720 pixels, 16:9 aspect ratio, under 2 MB, in JPG, PNG, or GIF. That resolution looks crisp everywhere YouTube displays it, from search to the watch page." },
];

const STEPS = [
  { title: "Paste a video link", text: "Drop in any YouTube video or Shorts URL, or just the video ID.", icon: <Link2 className="size-4" /> },
  { title: "Preview the thumbnail", text: "We show the highest-resolution thumbnail available for that video.", icon: <ImageIcon className="size-4" /> },
  { title: "Pick a size", text: "Choose from Max HD down to the smallest stored version.", icon: <Ruler className="size-4" /> },
  { title: "Save it", text: "Click Save to download, or Open to view the raw image.", icon: <Download className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "MultimediaApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="YouTube"
        title={TITLE}
        subtitle="Grab any YouTube video or Shorts thumbnail in full HD and every other size. Paste a link, preview, and download in one click. Free, no sign-up."
      />

      <YouTubeThumbnailDownloaderClient />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>Download YouTube thumbnails in every size</h2>
          <p>
            Every YouTube video stores its thumbnail in several fixed sizes, from the full 1280×720 HD image
            down to a tiny 120×90 preview. This tool reads the public thumbnail that YouTube already serves
            for a video, so you can preview it and save the exact size you need — no software, extension, or
            account required. Paste a normal watch URL, a youtu.be short link, or a Shorts URL and it pulls
            the right image automatically.
          </p>
        </div>
        <div>
          <h2>YouTube thumbnail size and dimensions</h2>
          <p>
            If you are creating a thumbnail rather than downloading one, YouTube recommends 1280×720 pixels at
            a 16:9 aspect ratio, saved as a JPG, PNG, or GIF under 2 MB. That is the same resolution as the
            Max HD option here. Designing at 1280×720 keeps your thumbnail sharp everywhere it appears, and
            because the smaller sizes are scaled down from it, a clean high-resolution original always looks
            best across search results, suggested videos, and the watch page.
          </p>
        </div>
        <div>
          <h2>A note on copyright</h2>
          <p>
            Thumbnails belong to the creators who made them. Downloading one for personal use, research, or
            fair-use commentary is generally acceptable, but do not pass someone else&apos;s thumbnail off as
            your own or use it commercially without permission. When in doubt, use thumbnails only as
            reference and design your own.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need YouTube data in your app?"
        sub="Captapi returns video details, channel stats, comments, transcripts, and thumbnails as clean JSON — plus TikTok, Instagram, and Facebook. Start free with 100 credits, no card required."
      />
    </>
  );
}
