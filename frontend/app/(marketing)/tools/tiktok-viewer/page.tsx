import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AtSign, Eye, MousePointerClick, Sparkles } from "lucide-react";
import TikTokViewerClient from "./TikTokViewerClient";

const PATH = "/tools/tiktok-viewer";
const TITLE = "TikTok Viewer";
const DESC =
  "Free anonymous TikTok viewer. Enter any public username to watch TikTok videos, stories, and profiles without an account, login, or app. Works on any device.";

export const metadata = buildMetadata({
  title: TITLE + " - Watch TikTok Anonymously Without an Account, Free | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "tiktok viewer",
    "tiktok story viewer",
    "anonymous tiktok story viewer",
    "tiktok story viewer anonymous",
    "tiktok profile viewer",
    "tiktok viewer without account",
    "watch tiktok without account",
    "tiktok anonymous viewer",
    "free tiktok viewer",
  ],
});

const FAQS = [
  {
    q: "What is a TikTok viewer?",
    a: "A TikTok viewer is an online tool that lets you watch public TikTok profiles and videos without logging in or creating an account. You enter a username, open the profile, and browse videos, stories, and the bio anonymously - the account owner is never told you visited.",
  },
  {
    q: "Do I need a TikTok account to watch videos?",
    a: "No. Public TikTok profiles and videos can be watched without any account. This tool works with just the public @username or profile link, and you never enter a TikTok password.",
  },
  {
    q: "Can I watch TikTok stories anonymously?",
    a: "Yes, as long as you are not logged in. TikTok only records story viewers who watch while signed into an account. Because this tool opens the profile without any login, your view cannot be attached to a profile and you will not appear in the story's viewer list.",
  },
  {
    q: "Will the account owner know I viewed their profile?",
    a: "No. Browsing a public profile and watching its videos while logged out sends no notification and adds you to no viewer list. TikTok's Profile Views feature only tracks logged-in users who have the feature turned on.",
  },
  {
    q: "Is this TikTok viewer free?",
    a: "Yes. Looking up and opening public profiles is completely free, with no sign-up, no credit card, and no limit on how many usernames you check.",
  },
  {
    q: "Can I view a private TikTok account?",
    a: "No. Private accounts lock their videos behind a follow approval at the platform level, and no legitimate third-party tool can bypass that. Only public accounts can be viewed.",
  },
  {
    q: "Does it work on iPhone, Android, and desktop?",
    a: "Yes. The tool is web-based, so it works in any modern browser - Chrome, Safari, Edge, or Firefox - on iPhone, Android, Mac, and Windows, with nothing to install.",
  },
  {
    q: "Is it safe and legal to use?",
    a: "The tool asks for no login details and only works with content that accounts have made public. Viewing public content is generally fine, but the videos still belong to their creators, so respect copyright and TikTok's Terms of Service.",
  },
];

const STEPS = [
  { title: "Enter a username", text: "Type the public TikTok @username, or paste a tiktok.com profile link.", icon: <AtSign className="size-4" /> },
  { title: "Press View profile", text: "The tool validates the handle and prepares an anonymous profile link.", icon: <MousePointerClick className="size-4" /> },
  { title: "Open the profile", text: "Use the button to open the public profile in your browser - no login asked.", icon: <Eye className="size-4" /> },
  { title: "Watch anonymously", text: "Browse videos, stories, and the bio without being recorded in any viewer list.", icon: <Sparkles className="size-4" /> },
];

const FEATURES = [
  { title: "Watch without an account", text: "No TikTok account, no login, no app install - just a username and your browser." },
  { title: "Anonymous story viewing", text: "Logged-out views are never attached to a profile, so you stay off the story viewer list." },
  { title: "Full profile access", text: "Browse the bio, follower counts, posted videos, and pinned clips of any public account." },
  { title: "No notifications", text: "The account owner is never notified that you looked at their profile or videos." },
  { title: "Works on any device", text: "iPhone, Android, Mac, and Windows - anything with a modern browser." },
  { title: "Free and unlimited", text: "No sign-up, no credit card, and no limit on how many profiles you can look up." },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "SocialNetworkingApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="TikTok"
        title="TikTok Viewer"
        subtitle="Enter any public username to watch TikTok videos, stories, and profiles anonymously - no account, no login, no app. Free and browser-based."
      />

      <TikTokViewerClient />

      <HowToUse steps={STEPS} />

      <section className="mt-16">
        <h2 className="text-2xl font-semibold">Why use this TikTok viewer?</h2>
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
          <h2>Watch TikTok anonymously, right in your browser</h2>
          <p>
            A TikTok viewer lets you browse any public account without logging in or revealing who you are. This free tool opens a profile by username so you can watch posted videos, check the bio and follower counts, and view public stories - all without a TikTok account, an app install, or a browser extension. It behaves the same on iPhone, Android, Mac, and Windows.
          </p>
          <p>
            The workflow is simple: type a username or paste a tiktok.com profile link, press View profile, and open the account anonymously. Because you are not signed in, TikTok has no profile to attach your visit to, which is what keeps your viewing private.
          </p>
        </div>

        <div>
          <h2>Anonymous TikTok story viewer</h2>
          <p>
            Stories are the one place on TikTok where viewers are normally recorded: the poster can see a list of logged-in accounts that watched their story while it is live. The key word is logged-in. When you watch a public story through this tool, you are browsing without any account, so there is no identity to record and you never show up in the viewer list. That makes this the most reliable way to watch TikTok stories anonymously - no shady third-party mirror sites required.
          </p>
        </div>

        <div>
          <h2>Who uses a TikTok viewer?</h2>
          <p>Common reasons people watch TikTok without an account include:</p>
          <ul>
            <li>Marketers and social teams studying competitor accounts and trends without alerting them.</li>
            <li>People who deleted the app or never had an account but still want to check a profile.</li>
            <li>Parents keeping an eye on what their children post publicly.</li>
            <li>Journalists and researchers reviewing public accounts without leaving a footprint.</li>
            <li>Anyone checking out a creator before deciding to follow them.</li>
          </ul>
        </div>

        <div>
          <h2>Public accounts, privacy, and copyright</h2>
          <p>
            This tool works only with public TikTok accounts. Private accounts keep their videos behind a follow approval at the platform level, so no legitimate viewer can access them - which protects everyone&apos;s privacy. The videos you watch still belong to the people who made them, so respect copyright and TikTok&apos;s Terms of Service, and keep anything you save for personal use unless you have permission to do more.
          </p>
        </div>

        <div>
          <h2>TikTok viewer frequently searched questions</h2>
          <p>
            People often ask how to watch TikTok without an account, whether an anonymous story viewer really works, and if the owner can tell. The short answer: enter a public username, open the profile logged out, and watch videos and stories without appearing in any viewer list. Because this page runs in the browser and needs no account, you can use it whenever you want a quick, private way to view a TikTok profile.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need TikTok data, not just a profile view?"
        sub="Captapi gives you APIs for TikTok, Instagram, YouTube, and Facebook transcripts, summaries, comments, and stats. Start free and automate the data side of your content workflow."
      />
    </>
  );
}
