import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Clapperboard, Clipboard, Download, Gauge } from "lucide-react";
import YouTubeShortsDownloaderClient from "./YouTubeShortsDownloaderClient";

const PATH = "/tools/youtube-shorts-downloader";
const TITLE = "YouTube Shorts Downloader";
const DESC =
  "Free YouTube Shorts downloader. Paste a Shorts link to preview the video and pick an MP4 quality from 360p to 1080p HD. No watermarks, no sign-up, works in your browser.";

export const metadata = buildMetadata({
  title: TITLE + " - Free MP4, No Watermark | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "youtube shorts downloader",
    "download youtube shorts",
    "youtube shorts to mp4",
    "youtube shorts download",
    "shorts downloader mp4",
    "download youtube shorts hd",
    "free youtube shorts downloader",
    "youtube shorts saver online",
    "youtube shorts downloader no watermark",
  ],
});

const FAQS = [
  {
    q: "How do I download a YouTube Short?",
    a: "Copy the YouTube Shorts link, paste it into the box at the top of this page, and press Download. The tool detects the Short and shows a preview with MP4 quality options from 360p up to 1080p HD, plus step-by-step guidance to save the video.",
  },
  {
    q: "Is this YouTube Shorts downloader free?",
    a: "Yes. The tool is completely free, runs in your browser, and does not require an account, email, or credit card. There is no limit on how many Shorts links you can preview.",
  },
  {
    q: "What quality can I download YouTube Shorts in?",
    a: "You can choose from common resolutions: 360p, 480p, 720p HD, and 1080p HD. The maximum quality available for any Short depends on the resolution the original creator uploaded.",
  },
  {
    q: "Does it add a watermark to the video?",
    a: "No. The goal is a clean copy of the original Short with no added watermark or overlay. If the creator burned text or branding into the video itself, that stays because it is part of the original upload, not added by this tool.",
  },
  {
    q: "Do I need to install software or an extension?",
    a: "No. This is an online YouTube Shorts downloader that works directly in the browser on desktop and mobile. There is nothing to install and no browser extension is required.",
  },
  {
    q: "Can I download Shorts I do not own?",
    a: "You should only download Shorts that you own or that are explicitly licensed for download. Saving other people's videos can violate YouTube's Terms of Service and copyright law. This tool is intended for your own content and licensed material.",
  },
  {
    q: "How can creators export their own Shorts?",
    a: "If you uploaded the Short, open YouTube Studio, go to Content, select the video, and use the download option to export the original MP4. YouTube Premium members can also save eligible videos for offline viewing inside the app.",
  },
  {
    q: "Does it work with youtu.be and standard watch links?",
    a: "Yes. The tool understands youtube.com/shorts links, standard youtube.com watch links, youtu.be short links, and embed URLs, and extracts the correct video ID automatically.",
  },
  {
    q: "Does it work on iPhone, Android, Mac, and Windows?",
    a: "Yes. Because the tool is web-based, it works on any modern browser, including Chrome, Safari, Edge, and Firefox, across iPhone, Android, Mac, and Windows.",
  },
];

const STEPS = [
  { title: "Copy the Shorts link", text: "Open the Short on YouTube and copy its URL from the address bar or the Share button.", icon: <Clipboard className="size-4" /> },
  { title: "Paste it and press Download", text: "Paste the link into the box above. The tool detects the Short and loads a preview.", icon: <Clapperboard className="size-4" /> },
  { title: "Pick an MP4 quality", text: "Choose a resolution from 360p to 1080p HD based on the original upload.", icon: <Gauge className="size-4" /> },
  { title: "Save your MP4", text: "Follow the guided steps to save the Short for your own or licensed content.", icon: <Download className="size-4" /> },
];

const FEATURES = [
  { title: "HD MP4 quality", text: "Pick from 360p, 480p, 720p HD, and 1080p HD, matching the resolutions Shorts are published in." },
  { title: "No watermarks", text: "Aim for a clean copy of the original Short with no added watermark or overlay." },
  { title: "Instant preview", text: "See the thumbnail and confirm you have the right Short before you save anything." },
  { title: "No sign-up, no install", text: "Everything runs in your browser. No account, no extension, no desktop software required." },
  { title: "Works everywhere", text: "Use it on iPhone, Android, Mac, and Windows in any modern browser." },
  { title: "Every link format", text: "Shorts URLs, standard watch links, youtu.be links, and embed URLs are all supported." },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "MultimediaApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="YouTube"
        title="YouTube Shorts Downloader"
        subtitle="Paste a YouTube Shorts link to preview the video and choose an MP4 quality from 360p to 1080p HD. Free, browser-based, no watermarks, and no sign-up required."
      />

      <YouTubeShortsDownloaderClient />

      <HowToUse steps={STEPS} />

      <section className="mt-16">
        <h2 className="text-2xl font-semibold">Why use this YouTube Shorts downloader?</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => (
            <div key={feature.title} className="rounded-xl border bg-card p-5">
              <h3 className="font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{feature.text}</p>
            </div>
          ))}
        </div>
      </section>

      <LongContent>
        <div>
          <h2>Free YouTube Shorts downloader that works in your browser</h2>
          <p>
            YouTube Shorts are vertical, short-form videos up to 60 seconds long, and YouTube does not offer a built-in way to save them. This free YouTube Shorts downloader bridges that gap. Paste any Shorts link, preview the video instantly, and choose the MP4 quality you need, from a lightweight 360p file to a sharp 1080p HD version. There is no sign-up, no software to install, and no browser extension to add.
          </p>
          <p>
            The workflow is intentionally simple. Paste a Shorts URL, press Download, and the tool reads the video ID and shows a thumbnail preview so you can confirm you have the right clip. From there you select a resolution and follow clear, honest guidance to save the file. It works the same way on iPhone, Android, Mac, and Windows because everything happens in the browser.
          </p>
        </div>

        <div>
          <h2>Choose the right quality for your Short</h2>
          <p>
            Different uses call for different resolutions. Lower resolutions keep files small for quick sharing or slow connections, while higher resolutions preserve detail for editing and re-posting on other platforms. The options available depend on what the creator originally uploaded.
          </p>
          <ul>
            <li>360p and 480p: smallest files, fastest to share, good for quick reference.</li>
            <li>720p HD: crisp standard high definition for phones and tablets.</li>
            <li>1080p Full HD: full high definition for editing and re-sharing your own work.</li>
          </ul>
        </div>

        <div>
          <h2>Built for creators repurposing their own Shorts</h2>
          <p>
            Many creators want to repurpose their Shorts across Instagram Reels, TikTok, and other platforms. The cleanest way to get a high quality MP4 of your own Short is through YouTube Studio, where you can download the original file you uploaded. YouTube Premium also lets eligible videos be saved for offline viewing inside the official app.
          </p>
          <p>
            Always respect copyright and YouTube's Terms of Service. Downloading Shorts that you do not own or that are not licensed for download can break those rules. Used responsibly, a Shorts download workflow is great for backing up your own channel, repurposing your vertical clips, and keeping offline copies of content you have the right to use.
          </p>
        </div>

        <div>
          <h2>YouTube Shorts downloader frequently searched questions</h2>
          <p>
            People often ask how to download YouTube Shorts to MP4, whether a Shorts downloader is free, and how to avoid watermarks. The short answer: paste the link, preview the Short, choose a resolution, and save responsibly. Because this page runs in the browser and does not require an account, you can use it any time you need a quick, no-fuss YouTube Shorts download starting point.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need YouTube data, not just Shorts files?"
        sub="Captapi gives you APIs for YouTube, TikTok, Instagram, and Facebook transcripts, summaries, comments, and stats. Start free and automate the data side of your content workflow."
      />
    </>
  );
}
