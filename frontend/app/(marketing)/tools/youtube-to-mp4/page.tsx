import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Clipboard, Download, Film, Gauge } from "lucide-react";
import YouTubeToMp4Client from "./YouTubeToMp4Client";

const PATH = "/tools/youtube-to-mp4";
const TITLE = "YouTube to MP4 Converter";
const DESC =
  "Free YouTube to MP4 tool. Paste a YouTube link to preview the video and pick an MP4 quality from 144p to 1080p HD. No sign-up, works in your browser.";

export const metadata = buildMetadata({
  title: TITLE + " - Free, No Sign Up | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "youtube to mp4",
    "youtube to mp4 converter",
    "youtube mp4 downloader",
    "convert youtube to mp4",
    "download youtube video mp4",
    "youtube to mp4 1080p",
    "free youtube to mp4",
    "youtube video to mp4 online",
  ],
});

const FAQS = [
  {
    q: "How do I convert a YouTube video to MP4?",
    a: "Copy the YouTube video link, paste it into the box at the top of this page, and press Start. The tool detects the video and shows a preview with MP4 quality options from 144p up to 1080p HD, plus step-by-step guidance to save the video.",
  },
  {
    q: "Is this YouTube to MP4 tool free?",
    a: "Yes. The tool is completely free, runs in your browser, and does not require an account, email, or credit card. There is no limit on how many links you can preview.",
  },
  {
    q: "What MP4 qualities are supported?",
    a: "You can choose from common YouTube resolutions: 144p, 240p, 360p, 480p, 720p HD, and 1080p HD. The available quality of any given video depends on what the original uploader published.",
  },
  {
    q: "Do I need to install software or an extension?",
    a: "No. This is an online YouTube to MP4 tool that works directly in the browser on desktop and mobile. There is nothing to install, and no browser extension is required.",
  },
  {
    q: "Can I download videos I do not own?",
    a: "You should only download videos that you own or that are explicitly licensed for download. Downloading other people's videos can violate YouTube's Terms of Service and copyright law. This tool is intended for your own content and licensed material.",
  },
  {
    q: "How can creators export their own videos as MP4?",
    a: "If you uploaded the video, open YouTube Studio, go to Content, select the video, and use the download option to export the original MP4 file. YouTube Premium members can also save eligible videos for offline viewing inside the app.",
  },
  {
    q: "Does converting to MP4 reduce the video quality?",
    a: "MP4 is a container format used by most YouTube videos already, so saving to MP4 does not re-encode or degrade the source. The final quality is limited by the highest resolution the uploader made available.",
  },
  {
    q: "Will this work for YouTube Shorts and youtu.be links?",
    a: "Yes. The tool understands standard youtube.com watch links, youtu.be short links, Shorts URLs, and embed URLs, and extracts the correct video ID automatically.",
  },
  {
    q: "Does it work on iPhone, Android, Mac, and Windows?",
    a: "Yes. Because the tool is web-based, it works on any modern browser, including Chrome, Safari, Edge, and Firefox, across iPhone, Android, Mac, and Windows.",
  },
  {
    q: "Is my data or link stored?",
    a: "The video link is processed in your browser to build the preview. The tool is not connected to a downloading backend and is designed to keep the workflow simple and private.",
  },
];

const STEPS = [
  { title: "Copy the YouTube link", text: "Open the video on YouTube and copy its URL from the address bar or the Share button.", icon: <Clipboard className="size-4" /> },
  { title: "Paste it and press Start", text: "Paste the link into the box above. The tool detects the video and loads a preview.", icon: <Film className="size-4" /> },
  { title: "Pick an MP4 quality", text: "Choose a resolution from 144p to 1080p HD based on the original upload.", icon: <Gauge className="size-4" /> },
  { title: "Save your MP4", text: "Follow the guided steps to save the video for your own or licensed content.", icon: <Download className="size-4" /> },
];

const FEATURES = [
  { title: "MP4 quality options", text: "Pick from 144p, 240p, 360p, 480p, 720p HD, and 1080p HD, matching the resolutions YouTube videos are published in." },
  { title: "Instant video preview", text: "See the thumbnail and confirm you have the right video before you save anything." },
  { title: "No sign-up, no install", text: "Everything runs in your browser. No account, no extension, no desktop software required." },
  { title: "Works everywhere", text: "Use it on iPhone, Android, Mac, and Windows in any modern browser." },
  { title: "Handles every link format", text: "Standard watch URLs, youtu.be links, Shorts, and embed URLs are all supported." },
  { title: "Creator-friendly guidance", text: "Clear steps for exporting your own uploads from YouTube Studio in your chosen quality." },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "MultimediaApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="YouTube"
        title="YouTube to MP4 Converter"
        subtitle="Paste a YouTube link to preview the video and choose an MP4 quality from 144p to 1080p HD. Free, browser-based, and no sign-up required."
      />

      <YouTubeToMp4Client />

      <HowToUse steps={STEPS} />

      <section className="mt-16">
        <h2 className="text-2xl font-semibold">Why use this YouTube to MP4 tool?</h2>
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
          <h2>Free YouTube to MP4 converter that works in your browser</h2>
          <p>
            MP4 is the most widely supported video format across phones, tablets, laptops, smart TVs, and editing software. This free YouTube to MP4 tool helps you grab the link of a YouTube video, preview it instantly, and choose the MP4 quality you need, from a lightweight 144p file to a sharp 1080p HD version. There is no sign-up, no software to install, and no browser extension to add.
          </p>
          <p>
            The workflow is intentionally simple. Paste a YouTube URL, press Start, and the tool reads the video ID and shows a thumbnail preview so you can confirm you have the right clip. From there you select a resolution and follow clear, honest guidance to save the file. It works the same way on iPhone, Android, Mac, and Windows because everything happens in the browser.
          </p>
        </div>

        <div>
          <h2>Choose the right MP4 quality</h2>
          <p>
            Different situations call for different resolutions. Lower resolutions keep file sizes small and are handy for slow connections or quick reference. Higher resolutions preserve detail for editing, presentations, and big screens. The available options depend on what the uploader originally published on YouTube.
          </p>
          <ul>
            <li>144p and 240p: smallest files, fastest to move around, good for audio-led clips.</li>
            <li>360p and 480p: balanced size and clarity for everyday viewing on phones.</li>
            <li>720p HD: crisp standard high definition for most laptops and tablets.</li>
            <li>1080p HD: full high definition for editing, large displays, and archiving your own work.</li>
          </ul>
        </div>

        <div>
          <h2>Built for creators and your own content</h2>
          <p>
            This tool is designed for people who want to save their own uploads, licensed footage, or videos that explicitly allow downloads. If you are the creator, the cleanest way to get a high quality MP4 is through YouTube Studio, where you can download the original file you uploaded. YouTube Premium also lets eligible videos be saved for offline viewing inside the official app.
          </p>
          <p>
            Always respect copyright and YouTube's Terms of Service. Downloading videos that you do not own or that are not licensed for download can break those rules. Used responsibly, a YouTube to MP4 workflow is great for backing up your own channel, repurposing your footage, and keeping offline copies of content you have the right to use.
          </p>
        </div>

        <div>
          <h2>YouTube to MP4 frequently searched questions</h2>
          <p>
            People often ask how to convert YouTube to MP4 online, whether a YouTube MP4 downloader is free, and which quality to pick. The short answer: paste the link, preview the video, choose a resolution, and save responsibly. Because this page runs in the browser and does not require an account, you can use it any time you need a quick, no-fuss YouTube to MP4 starting point.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need YouTube data, not just video files?"
        sub="Captapi gives you APIs for transcripts, summaries, comments, profiles, search, ad intelligence, commerce data, and stats across dozens of platforms. Start free and automate the data side of your content workflow."
      />
    </>
  );
}
