import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Clipboard, Download, Music, Gauge } from "lucide-react";
import YouTubeToMp3Client from "./YouTubeToMp3Client";

const PATH = "/tools/youtube-to-mp3";
const TITLE = "YouTube to MP3 Converter";
const DESC =
  "Free YouTube to MP3 converter. Paste a YouTube link to preview the video and pick an MP3 audio quality from 64 to 320 kbps. No sign-up, works in your browser.";

export const metadata = buildMetadata({
  title: TITLE + " - Free, No Sign Up | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "mp3 youtube converter",
    "youtube to mp3",
    "youtube to mp3 converter",
    "youtube mp3 converter",
    "convert youtube to mp3",
    "youtube to mp3 320kbps",
    "free youtube to mp3",
    "youtube mp3 downloader",
    "youtube audio to mp3",
    "youtube to mp3 online",
  ],
});

const FAQS = [
  {
    q: "How do I convert a YouTube video to MP3?",
    a: "Copy the YouTube video link, paste it into the box at the top of this page, and press Start. The tool detects the video and shows a preview with MP3 audio quality options from 64 kbps up to 320 kbps, plus step-by-step guidance to save the audio.",
  },
  {
    q: "Is this YouTube to MP3 converter free?",
    a: "Yes. The tool is completely free, runs in your browser, and does not require an account, email, or credit card. There is no limit on how many links you can preview.",
  },
  {
    q: "What MP3 audio qualities are supported?",
    a: "You can choose from common MP3 bitrates: 64 kbps, 128 kbps, 192 kbps, 256 kbps, and 320 kbps. Higher bitrates sound better and produce larger files; 320 kbps is the highest standard MP3 quality.",
  },
  {
    q: "What is the best MP3 bitrate for music?",
    a: "For music, 256 kbps or 320 kbps gives near-CD audio quality and is the best choice when you want the clearest sound. For podcasts, audiobooks, or spoken-word content, 128 kbps is usually enough and keeps the file small.",
  },
  {
    q: "Do I need to install software or an extension?",
    a: "No. This is an online YouTube to MP3 tool that works directly in the browser on desktop and mobile. There is nothing to install, and no browser extension is required.",
  },
  {
    q: "Can I convert audio from videos I do not own?",
    a: "You should only download audio that you own or that is explicitly licensed for download. Converting other people's videos can violate YouTube's Terms of Service and copyright law. This tool is intended for your own content and licensed material.",
  },
  {
    q: "How can creators export their own audio as MP3?",
    a: "If you uploaded the video, open YouTube Studio, select the video, and download the original file, then convert the audio track to MP3 at your chosen bitrate. YouTube Music Premium members can also save eligible tracks for offline listening inside the app.",
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
  { title: "Paste it and press Start", text: "Paste the link into the box above. The tool detects the video and loads a preview.", icon: <Music className="size-4" /> },
  { title: "Pick an MP3 bitrate", text: "Choose an audio quality from 64 kbps to 320 kbps depending on how clear you need the sound.", icon: <Gauge className="size-4" /> },
  { title: "Save your MP3", text: "Follow the guided steps to save the audio for your own or licensed content.", icon: <Download className="size-4" /> },
];

const FEATURES = [
  { title: "MP3 quality options", text: "Pick from 64, 128, 192, 256, and 320 kbps so you can balance audio clarity against file size." },
  { title: "Instant video preview", text: "See the thumbnail and confirm you have the right video before you save anything." },
  { title: "No sign-up, no install", text: "Everything runs in your browser. No account, no extension, no desktop software required." },
  { title: "Works everywhere", text: "Use it on iPhone, Android, Mac, and Windows in any modern browser." },
  { title: "Handles every link format", text: "Standard watch URLs, youtu.be links, Shorts, and embed URLs are all supported." },
  { title: "Creator-friendly guidance", text: "Clear steps for exporting your own audio from YouTube Studio at the bitrate you choose." },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "MultimediaApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="YouTube"
        title="YouTube to MP3 Converter"
        subtitle="Paste a YouTube link to preview the video and choose an MP3 audio quality from 64 to 320 kbps. Free, browser-based, and no sign-up required."
      />

      <YouTubeToMp3Client />

      <HowToUse steps={STEPS} />

      <section className="mt-16">
        <h2 className="text-2xl font-semibold">Why use this YouTube to MP3 converter?</h2>
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
          <h2>Free YouTube to MP3 converter that works in your browser</h2>
          <p>
            MP3 is the most widely supported audio format across phones, tablets, laptops, car stereos, and music players. This free YouTube to MP3 converter helps you grab the link of a YouTube video, preview it instantly, and choose the audio quality you need, from a lightweight 64 kbps file to a rich 320 kbps track. There is no sign-up, no software to install, and no browser extension to add.
          </p>
          <p>
            The workflow is intentionally simple. Paste a YouTube URL, press Start, and the tool reads the video ID and shows a thumbnail preview so you can confirm you have the right clip. From there you select a bitrate and follow clear, honest guidance to save the file. It works the same way on iPhone, Android, Mac, and Windows because everything happens in the browser.
          </p>
        </div>

        <div>
          <h2>Choose the right MP3 bitrate</h2>
          <p>
            The bitrate controls how much audio detail is kept and how large the final MP3 is. Lower bitrates keep files small and are perfect for speech, while higher bitrates preserve the richness of music. Pick the option that matches what you are listening to.
          </p>
          <ul>
            <li>64 kbps: smallest files, fine for spoken word, voice notes, and audiobooks.</li>
            <li>128 kbps: balanced quality and size, a common choice for podcasts.</li>
            <li>192 kbps: clear, full sound that works well for most music.</li>
            <li>256 kbps: high quality that is hard to distinguish from the source for most listeners.</li>
            <li>320 kbps: the highest standard MP3 quality, best for music you want to keep.</li>
          </ul>
        </div>

        <div>
          <h2>Built for creators and your own content</h2>
          <p>
            This converter is designed for people who want to save their own uploads, licensed tracks, or audio that explicitly allows downloads. If you are the creator, the cleanest way to get a high quality MP3 is through YouTube Studio, where you can download the original file and convert its audio. YouTube Music Premium also lets eligible tracks be saved for offline listening inside the official app.
          </p>
          <p>
            Always respect copyright and YouTube's Terms of Service. Converting videos that you do not own or that are not licensed for download can break those rules. Used responsibly, a YouTube to MP3 workflow is great for backing up your own channel audio, repurposing your podcast clips, and keeping offline copies of content you have the right to use.
          </p>
        </div>

        <div>
          <h2>YouTube to MP3 frequently searched questions</h2>
          <p>
            People often ask how to convert YouTube to MP3 online, whether a YouTube MP3 converter is free, and which bitrate to pick. The short answer: paste the link, preview the video, choose an audio quality, and save responsibly. Because this page runs in the browser and does not require an account, you can use it any time you need a quick, no-fuss YouTube to MP3 starting point.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need YouTube data, not just audio files?"
        sub="Captapi gives you APIs for YouTube, TikTok, Instagram, and Facebook transcripts, summaries, comments, and stats. Start free and automate the data side of your content workflow."
      />
    </>
  );
}
