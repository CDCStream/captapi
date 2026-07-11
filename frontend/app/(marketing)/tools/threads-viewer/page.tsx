import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AtSign, Eye, MousePointerClick, Sparkles } from "lucide-react";
import ThreadsViewerClient from "./ThreadsViewerClient";

const PATH = "/tools/threads-viewer";
const TITLE = "Threads Viewer";
const DESC =
  "Free anonymous Threads viewer. Enter any public username to browse Threads posts, replies, reposts, and profiles without an Instagram account or login.";

export const metadata = buildMetadata({
  title: TITLE + " - Browse Threads Anonymously Without an Account, Free | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "threads viewer",
    "threads profile viewer",
    "view threads without account",
    "threads anonymous viewer",
    "browse threads without login",
    "threads viewer online",
    "free threads viewer",
  ],
});

const FAQS = [
  {
    q: "What is a Threads viewer?",
    a: "A Threads viewer is an online tool that lets you browse public profiles on Threads, Meta's text-based social network, without logging in. You enter a username, open the profile, and read the person's threads, replies, and reposts anonymously.",
  },
  {
    q: "Do I need an Instagram or Threads account to view profiles?",
    a: "No. Public Threads profiles and posts are viewable on the web without any account. This tool works with just the public @username or a threads.com profile link, and you never enter a password.",
  },
  {
    q: "Will the profile owner know I viewed their Threads?",
    a: "No. Threads does not have a profile-view tracker and does not notify users when someone reads their posts. Browsing while logged out adds an extra layer: there is no account attached to your visit at all.",
  },
  {
    q: "Can I view a private Threads profile?",
    a: "No. Private profiles lock their posts behind a follow approval at the platform level, and no legitimate third-party tool can bypass that. Only public profiles can be viewed.",
  },
  {
    q: "Is this Threads viewer free?",
    a: "Yes. Looking up and opening public profiles is completely free, with no sign-up, no credit card, and no limit on how many usernames you check.",
  },
  {
    q: "Threads usernames are the same as Instagram - which one do I enter?",
    a: "Threads handles come from Instagram, so the @username is identical on both platforms. Enter the Instagram handle and the tool opens the matching Threads profile.",
  },
  {
    q: "Does it work on iPhone, Android, and desktop?",
    a: "Yes. Because the tool is web-based, it works in any modern browser - Chrome, Safari, Edge, or Firefox - on iPhone, Android, Mac, and Windows, with nothing to install.",
  },
  {
    q: "Is it safe and legal to use?",
    a: "The tool asks for no login details and only works with content accounts have made public. Viewing public content is generally fine; the posts still belong to their authors, so respect copyright and Meta's Terms of Service.",
  },
];

const STEPS = [
  { title: "Enter a username", text: "Type the public @username - the same handle as on Instagram - or paste a threads.com link.", icon: <AtSign className="size-4" /> },
  { title: "Press View profile", text: "The tool validates the handle and prepares an anonymous profile link.", icon: <MousePointerClick className="size-4" /> },
  { title: "Open the profile", text: "Use the button to open the public profile in your browser - no login asked.", icon: <Eye className="size-4" /> },
  { title: "Browse anonymously", text: "Read threads, replies, and reposts without any account attached to your visit.", icon: <Sparkles className="size-4" /> },
];

const FEATURES = [
  { title: "No account needed", text: "Browse Threads without an Instagram account, a Threads account, or the app." },
  { title: "Full public timeline", text: "Read a profile's threads, replies, reposts, and bio - everything shared publicly." },
  { title: "Anonymous by design", text: "Threads has no view tracker, and logged-out visits carry no identity at all." },
  { title: "No notifications", text: "The profile owner is never told that you read their posts or visited their page." },
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
        platform="Threads"
        title="Threads Viewer"
        subtitle="Enter any public username to browse Threads posts, replies, and profiles anonymously - no Instagram account, no login, no app. Free and browser-based."
      />

      <ThreadsViewerClient />

      <HowToUse steps={STEPS} />

      <section className="mt-16">
        <h2 className="text-2xl font-semibold">Why use this Threads viewer?</h2>
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
          <h2>Browse Threads without an account</h2>
          <p>
            Threads is Meta&apos;s text-first social network, and every account is tied to an Instagram handle. What many people do not realize is that public Threads profiles are fully readable on the web without logging in. A Threads viewer makes that easy: enter a username, open the profile, and read the person&apos;s threads, replies, and reposts - no Instagram account, no Threads app, no browser extension. It works the same on iPhone, Android, Mac, and Windows.
          </p>
          <p>
            The workflow is simple: type the @username (the same handle as on Instagram) or paste a threads.com profile link, press View profile, and open the page anonymously. Because you are not signed in, there is no account attached to your visit.
          </p>
        </div>

        <div>
          <h2>Does Threads show who viewed your profile?</h2>
          <p>
            No. Unlike LinkedIn, Threads has no &quot;profile views&quot; feature and no viewer list on posts. Authors can see aggregate view counts on their own posts, but never who viewed them. Combined with logged-out browsing, that makes reading Threads through this viewer completely anonymous - there is simply no mechanism that could reveal your visit.
          </p>
        </div>

        <div>
          <h2>Who uses a Threads viewer?</h2>
          <p>Common reasons people browse Threads without an account include:</p>
          <ul>
            <li>Marketers and researchers following conversations and competitor accounts without engaging.</li>
            <li>People who never created a Threads profile but want to follow a specific creator.</li>
            <li>Journalists verifying public statements without leaving a footprint.</li>
            <li>Anyone checking what a person posts before deciding to follow them.</li>
            <li>Users who deleted the app but still want to read a few favorite accounts.</li>
          </ul>
        </div>

        <div>
          <h2>Public profiles, privacy, and copyright</h2>
          <p>
            This tool works only with public Threads profiles. Private profiles keep their posts behind a follow approval at the platform level, so no third-party viewer can access them - which protects everyone&apos;s privacy. The posts you read still belong to their authors, so respect copyright and Meta&apos;s Terms of Service when quoting or sharing.
          </p>
        </div>

        <div>
          <h2>Threads viewer frequently searched questions</h2>
          <p>
            People often ask how to view Threads without an account, whether Threads shows profile views, and if you can read posts without the app. The short answer: enter a public username, open the profile on the web while logged out, and read everything the account shares publicly - threads, replies, and reposts - with no notification and no viewer list. Because this page runs in the browser and needs no account, you can use it whenever you want a quick, private way to read Threads.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need social data, not just a profile view?"
        sub="Captapi gives you APIs for Threads, Instagram, TikTok, YouTube, and Facebook profiles, posts, comments, and stats. Start free and automate the data side of your content workflow."
      />
    </>
  );
}
