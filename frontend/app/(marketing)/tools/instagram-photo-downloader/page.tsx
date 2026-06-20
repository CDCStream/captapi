import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { Clipboard, Download, Image as ImageIcon, MousePointerClick } from "lucide-react";
import InstagramPhotoDownloaderClient from "./InstagramPhotoDownloaderClient";

const PATH = "/tools/instagram-photo-downloader";
const TITLE = "Instagram Photo Downloader";
const DESC =
  "Free Instagram photo downloader. Paste a public post or reel link to open the image in full size and save it in original quality. No login or app, works on any device.";

export const metadata = buildMetadata({
  title: TITLE + " - Save Instagram Photos Free | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "instagram photo downloader",
    "download instagram photo",
    "instagram image downloader",
    "save instagram photos",
    "instagram picture downloader",
    "instagram photo download",
    "download instagram pictures hd",
    "free instagram photo downloader",
    "instagram photo saver online",
  ],
});

const FAQS = [
  {
    q: "How do I download a photo from Instagram?",
    a: "Open the Instagram post you want and copy its link. Paste the link into the box at the top of this page and press Download. The tool detects the post and shows clear steps to open the image in full size and save it to your device.",
  },
  {
    q: "Do I need an Instagram account to download photos?",
    a: "No. You do not need to log in or create an account. You only need the public URL of the photo or post you want to save. The tool never asks for your Instagram password.",
  },
  {
    q: "Is this Instagram photo downloader free?",
    a: "Yes. The tool is completely free, runs in your browser, and does not require an account, email, or app install. There is no limit on how many links you can look up.",
  },
  {
    q: "Can I download photos in high resolution?",
    a: "Yes. The goal is to save the image in the highest quality Instagram serves for that post, so the downloaded photo matches the resolution shown on the platform without resizing.",
  },
  {
    q: "Does it work for carousel posts with multiple photos?",
    a: "Yes. Open the post and move through each image in the carousel, then save the ones you want one by one. Reels and single-image posts work the same way.",
  },
  {
    q: "Do I need to install software or an extension?",
    a: "No. This is an online Instagram photo downloader that works directly in the browser on desktop and mobile. There is nothing to install and no browser extension is required.",
  },
  {
    q: "Can I download photos from a private account?",
    a: "No. Only public posts can be opened and saved. Private accounts restrict their content at the platform level, so no third-party tool can access their photos. This is an Instagram privacy restriction.",
  },
  {
    q: "Is it legal to download Instagram photos?",
    a: "Saving photos for personal, offline use is generally fine, but the images still belong to their creators. Always respect copyright and Instagram's Terms of Service, and get permission before reposting or using someone else's photo.",
  },
  {
    q: "Is it safe and private to use?",
    a: "Yes. The tool does not require any login details and processes the link in your browser to build the preview. It only ever works with publicly available posts.",
  },
];

const STEPS = [
  { title: "Copy the photo link", text: "Open the Instagram post and copy its URL from the address bar or the Share menu.", icon: <Clipboard className="size-4" /> },
  { title: "Paste it and press Download", text: "Paste the link into the box above. The tool detects the post and prepares it.", icon: <MousePointerClick className="size-4" /> },
  { title: "Open the photo", text: "Use the button to open the post so the image loads in full size.", icon: <ImageIcon className="size-4" /> },
  { title: "Save the image", text: "Right-click and Save on desktop, or press and hold to save on mobile.", icon: <Download className="size-4" /> },
];

const FEATURES = [
  { title: "Original quality", text: "Aim to save the image in the highest resolution Instagram serves, with no resizing or recompression." },
  { title: "No login or app", text: "You never enter an Instagram password and there is nothing to install. Just paste a link." },
  { title: "Works on any device", text: "Use it on iPhone, Android, Mac, and Windows in any modern browser." },
  { title: "Posts, reels, and carousels", text: "Handles single photos, reel covers, and multi-image carousel posts." },
  { title: "Fast and free", text: "No sign-up, no credit card, and no limit on how many photos you look up." },
  { title: "Privacy-respecting", text: "Only public posts are accessible, and the tool asks for no personal details." },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "UtilitiesApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Instagram"
        title="Instagram Photo Downloader"
        subtitle="Paste a public post or reel link to open the image in full size and save it in original quality. Free, browser-based, and no login required."
      />

      <InstagramPhotoDownloaderClient />

      <HowToUse steps={STEPS} />

      <section className="mt-16">
        <h2 className="text-2xl font-semibold">Why use this Instagram photo downloader?</h2>
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
          <h2>Free Instagram photo downloader that works in your browser</h2>
          <p>
            Instagram is where people share life's best moments as photos, and sometimes you want to keep a copy on your own device. This free Instagram photo downloader helps you take the link of a public post, open the image in full size, and save it in its original quality. There is no sign-up, no software to install, and no browser extension to add, and it works the same on iPhone, Android, Mac, and Windows.
          </p>
          <p>
            The workflow is simple. Copy the post URL from Instagram, paste it into the box, and press Download. The tool detects whether the link is a post, reel, or photo and prepares it so you can open it and save the image with a quick right-click on desktop or a press-and-hold on mobile.
          </p>
        </div>

        <div>
          <h2>Save posts, reels, and carousels</h2>
          <p>
            Instagram photos come in a few shapes, and this downloader is built for all of them. Whether you are saving a single picture, the cover of a reel, or a multi-image carousel, the steps are the same. For carousels, move through each slide and save the images you want one at a time so you only keep what you need.
          </p>
          <ul>
            <li>Single photos: open the post and save the full-resolution image.</li>
            <li>Carousels: swipe through each slide and save the ones you like.</li>
            <li>Reels: open the reel to grab its cover image in high quality.</li>
          </ul>
        </div>

        <div>
          <h2>Public content, privacy, and copyright</h2>
          <p>
            This tool works only with public Instagram posts. Private accounts lock their content behind a follow approval at the platform level, so no third-party downloader can access their photos, and that protects everyone's privacy. Just as important, the photos you save still belong to the people who created them.
          </p>
          <p>
            Saving an image for personal, offline reference is generally fine, but reposting or commercial use is different. Always respect copyright and Instagram's Terms of Service, and ask the creator for permission before you reuse their work. Used responsibly, a photo downloader is great for backing up your own posts and keeping inspiration you have the right to use.
          </p>
        </div>

        <div>
          <h2>Instagram photo downloader frequently searched questions</h2>
          <p>
            People often ask how to download Instagram photos without an account, whether an Instagram image downloader is free, and if the saved picture keeps its quality. The short answer: paste the link, open the post, and save the image in its original resolution, all without logging in. Because this page runs in the browser and needs no account, you can use it any time you want a quick, no-fuss way to save Instagram photos.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need Instagram data, not just photos?"
        sub="Captapi gives you APIs for Instagram, YouTube, TikTok, and Facebook transcripts, summaries, comments, and stats. Start free and automate the data side of your content workflow."
      />
    </>
  );
}
