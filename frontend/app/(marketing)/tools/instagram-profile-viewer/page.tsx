import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AtSign, Eye, MousePointerClick, Sparkles } from "lucide-react";
import InstagramProfileViewerClient from "./InstagramProfileViewerClient";

const PATH = "/tools/instagram-profile-viewer";
const TITLE = "Instagram Profile Viewer";
const DESC =
  "Free Instagram profile viewer. Enter any public username to browse the profile photo, posts, reels, stories, and highlights anonymously, with no login or app. Any device.";

export const metadata = buildMetadata({
  title: TITLE + " - View Insta Profiles Anonymously, Free | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "instagram profile viewer",
    "insta profile viewer",
    "anonymous instagram profile viewer",
    "instagram profile viewer online",
    "view instagram profile without account",
    "insta dp viewer",
    "instagram profile picture viewer",
    "free instagram profile viewer",
    "instagram account viewer",
  ],
});

const FAQS = [
  {
    q: "What is an Instagram profile viewer?",
    a: "An Instagram profile viewer is an online tool that lets you browse a public Instagram profile without logging in or creating an account. You can look at the profile picture, posts, reels, stories, and highlights, and the account owner is never told that you visited.",
  },
  {
    q: "Do I need an Instagram account to view a profile?",
    a: "No. The tool works without any login or registration. You only need the public username or profile link of the account you want to view, and you never enter an Instagram password.",
  },
  {
    q: "Will the profile owner know I viewed their page?",
    a: "No. Browsing a public profile, its posts, reels, and permanent highlights does not notify the owner or add your name to any list. Instagram only keeps a viewer list for active 24-hour stories, which requires being logged in to appear in.",
  },
  {
    q: "Is this Instagram profile viewer free?",
    a: "Yes. Looking up and opening public profiles is completely free. There is no sign-up, no account, and no limit on how many usernames you can check.",
  },
  {
    q: "Can I view a private Instagram profile?",
    a: "No. Only public accounts can be viewed. Private profiles lock all of their content, including posts, stories, and highlights, behind a follow approval at the platform level, and no legitimate third-party tool can bypass that.",
  },
  {
    q: "What is an Insta DP viewer?",
    a: "An Insta DP viewer shows an Instagram profile picture (display picture) in full size. Instagram displays profile photos as small thumbnails, so a DP viewer helps you open the profile to see the picture clearly in its original quality.",
  },
  {
    q: "Does it work on iPhone, Android, and desktop?",
    a: "Yes. Because the tool is web-based, it works in any modern browser, including Chrome, Safari, Edge, and Firefox, across iPhone, Android, Mac, and Windows, with nothing to install.",
  },
  {
    q: "Is it safe and private to use?",
    a: "Yes. The tool asks for no login details, installs nothing, and processes the username in your browser. It only ever works with publicly available profiles, so private accounts stay protected.",
  },
  {
    q: "Is it legal to use an Instagram profile viewer?",
    a: "Viewing content that an account has made public is generally fine. The content still belongs to its creators, so respect copyright and Instagram's Terms of Service, and only use what you view for personal purposes unless you have permission.",
  },
];

const STEPS = [
  { title: "Enter a username", text: "Type the public Instagram @username, or paste an instagram.com profile link.", icon: <AtSign className="size-4" /> },
  { title: "Press View profile", text: "The tool validates the handle and prepares an anonymous profile link.", icon: <MousePointerClick className="size-4" /> },
  { title: "Open the profile", text: "Use the button to open the public profile in your browser.", icon: <Eye className="size-4" /> },
  { title: "Browse anonymously", text: "Explore the profile photo, posts, reels, and highlights without being recorded.", icon: <Sparkles className="size-4" /> },
];

const FEATURES = [
  { title: "Full-size profile photo", text: "Open the profile to see the display picture clearly instead of a tiny thumbnail." },
  { title: "Posts, reels, and highlights", text: "Browse everything a public account shares, from the grid to permanent highlights." },
  { title: "Anonymous by design", text: "Viewing a public profile and its permanent content sends no notification to the owner." },
  { title: "No login or app", text: "You never enter an Instagram password and there is nothing to install. Just type a username." },
  { title: "Works on any device", text: "Use it on iPhone, Android, Mac, and Windows in any modern browser." },
  { title: "Free and unlimited", text: "No sign-up, no credit card, and no limit on how many profiles you can look up." },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "SocialNetworkingApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Instagram"
        title="Instagram Profile Viewer"
        subtitle="Enter any public username to browse the profile photo, posts, reels, and highlights anonymously. Free, browser-based, and no login required."
      />

      <InstagramProfileViewerClient />

      <HowToUse steps={STEPS} />

      <section className="mt-16">
        <h2 className="text-2xl font-semibold">Why use this Instagram profile viewer?</h2>
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
          <h2>Free Instagram profile viewer that works in your browser</h2>
          <p>
            An Instagram profile viewer lets you browse any public account without logging in or revealing who you are. This free tool helps you open a profile by username and look through everything it shares publicly: the full-size profile photo, the posts grid, reels, stories, and pinned highlights. There is no sign-up, no app to install, and no browser extension, so it works the same on iPhone, Android, Mac, and Windows.
          </p>
          <p>
            The workflow is simple. Type a username or paste an instagram.com profile link, press View profile, and the tool prepares a clean, anonymous way to open the public account. From there you browse at your own pace. Because you are not logged into any account, your visit is private and the owner is not notified.
          </p>
        </div>

        <div>
          <h2>See the profile picture in full size</h2>
          <p>
            One of the most requested features is an Insta DP viewer, short for display picture viewer. Instagram shows profile photos as small circular thumbnails, which makes it hard to see the detail, especially on a phone. Opening the profile through this tool lets you view the picture clearly in its original quality so you can verify an identity, check a brand logo, or simply get a better look.
          </p>
        </div>

        <div>
          <h2>Who uses an Instagram profile viewer?</h2>
          <p>
            A profile viewer is useful any time you want to look without interacting. Common reasons include:
          </p>
          <ul>
            <li>Marketers and brand researchers studying competitor content without alerting them.</li>
            <li>People without an Instagram account who still need to check a public profile.</li>
            <li>Parents keeping an eye on what their children post publicly.</li>
            <li>Journalists and researchers reviewing public profiles without leaving a footprint.</li>
            <li>Anyone previewing a profile before accepting a follow request.</li>
          </ul>
        </div>

        <div>
          <h2>Public profiles, privacy, and copyright</h2>
          <p>
            This tool works only with public Instagram accounts. Private profiles keep their content behind a follow approval at the platform level, so no third-party viewer can access them, which protects everyone's privacy. The content you view still belongs to the people who created it, so respect copyright and Instagram's Terms of Service, and keep anything you save for personal use unless you have permission to do more.
          </p>
        </div>

        <div>
          <h2>Instagram profile viewer frequently searched questions</h2>
          <p>
            People often ask how to view an Instagram profile without an account, whether an anonymous profile viewer is free, and if the owner can tell. The short answer: enter a public username, open the profile, and browse the photo, posts, reels, and highlights, all without logging in and without appearing in any viewer list. Because this page runs in the browser and needs no account, you can use it any time you want a quick, private way to view an Instagram profile.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need Instagram data, not just a profile view?"
        sub="Captapi gives you APIs for Instagram, YouTube, TikTok, and Facebook transcripts, summaries, comments, and stats. Start free and automate the data side of your content workflow."
      />
    </>
  );
}
