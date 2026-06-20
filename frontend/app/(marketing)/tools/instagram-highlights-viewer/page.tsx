import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AtSign, Eye, MousePointerClick, Sparkles } from "lucide-react";
import InstagramHighlightsViewerClient from "./InstagramHighlightsViewerClient";

const PATH = "/tools/instagram-highlights-viewer";
const TITLE = "Instagram Highlights Viewer";
const DESC =
  "Free Instagram highlights viewer. Enter any public username to open and browse their story highlights anonymously, with no login or app. Works on any device.";

export const metadata = buildMetadata({
  title: TITLE + " - View Highlights Anonymously, Free | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "instagram highlights viewer",
    "instagram highlight viewer",
    "view instagram highlights",
    "anonymous instagram highlights viewer",
    "instagram story highlights viewer",
    "view instagram highlights without account",
    "instagram highlights viewer online",
    "free instagram highlights viewer",
  ],
});

const FAQS = [
  {
    q: "How do I view someone's Instagram highlights?",
    a: "Enter the public Instagram username in the box at the top of this page and press View highlights. The tool prepares an anonymous way to open the profile so you can browse the highlight covers under their bio and tap any one to play it.",
  },
  {
    q: "Can someone see if I viewed their Instagram highlights?",
    a: "Instagram does not show a viewer list for permanent highlights the way it does for active 24-hour stories. Browsing a profile's highlight covers does not put your name in any viewer list, so the owner is not notified.",
  },
  {
    q: "Is this Instagram highlights viewer free?",
    a: "Yes. The tool is completely free, runs in your browser, and does not require an account, email, or app install. There is no limit on how many usernames you can look up.",
  },
  {
    q: "Do I need an Instagram account to view highlights?",
    a: "No account or login is required to open a public profile and view its highlights. You only need the username. The tool never asks for your Instagram password.",
  },
  {
    q: "What are Instagram highlights and how long do they last?",
    a: "Highlights are curated collections of past stories that a user pins permanently to their profile. Unlike regular stories that disappear after 24 hours, highlights stay visible indefinitely until the owner removes them.",
  },
  {
    q: "Can I view highlights from a private Instagram account?",
    a: "No. Only public profiles can be viewed. Private accounts restrict all content at the platform level, so no third-party tool can retrieve their highlights, stories, or posts. This is an Instagram privacy restriction, not a tool limitation.",
  },
  {
    q: "Does it work on iPhone, Android, and desktop?",
    a: "Yes. Because the tool is web-based, it works in any modern browser, including Chrome, Safari, Edge, and Firefox, across iPhone, Android, Mac, and Windows.",
  },
  {
    q: "Does the airplane mode trick work for viewing highlights?",
    a: "The airplane mode trick was designed for 24-hour stories and is unreliable. For permanent highlights it is unnecessary, because Instagram does not record a viewer list for them in the first place.",
  },
  {
    q: "Is my search or the username stored?",
    a: "The username is processed in your browser to build the link. The tool is designed to keep the workflow simple and private, and it only ever works with publicly available profiles.",
  },
];

const STEPS = [
  { title: "Enter a username", text: "Type the public Instagram @username, or paste an instagram.com profile link.", icon: <AtSign className="size-4" /> },
  { title: "Press View highlights", text: "The tool validates the handle and prepares an anonymous profile link.", icon: <MousePointerClick className="size-4" /> },
  { title: "Open the profile", text: "Use the button to open the public profile where the highlight covers are listed.", icon: <Eye className="size-4" /> },
  { title: "Tap a highlight", text: "Select any highlight cover under the bio to watch it. No viewer list is recorded.", icon: <Sparkles className="size-4" /> },
];

const FEATURES = [
  { title: "Anonymous by design", text: "Highlights have no viewer list, so browsing a public profile's highlights leaves no trace and sends no notification." },
  { title: "No login or app", text: "You never enter an Instagram password and there is nothing to install. Just type a username." },
  { title: "Works on any device", text: "Use it on iPhone, Android, Mac, and Windows in any modern browser." },
  { title: "Public profiles", text: "Look up any public account by username or by pasting its instagram.com profile link." },
  { title: "Fast and free", text: "No sign-up, no credit card, and no usage limits on how many profiles you can check." },
  { title: "Privacy-respecting", text: "Only publicly available highlights are accessible, and private accounts stay protected." },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "SocialNetworkingApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Instagram"
        title="Instagram Highlights Viewer"
        subtitle="Enter any public username to open and browse their story highlights anonymously. Free, browser-based, and no login required."
      />

      <InstagramHighlightsViewerClient />

      <HowToUse steps={STEPS} />

      <section className="mt-16">
        <h2 className="text-2xl font-semibold">Why use this Instagram highlights viewer?</h2>
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
          <h2>Free Instagram highlights viewer that works in your browser</h2>
          <p>
            Instagram highlights are the curated story collections people pin under their bio, and they often hold the best moments from a profile. This free Instagram highlights viewer lets you enter any public username and open their highlights anonymously, with no login, no app, and no sign-up. Everything runs in your browser, so it works the same on iPhone, Android, Mac, and Windows.
          </p>
          <p>
            The workflow is simple. Type a username or paste an instagram.com profile link, press View highlights, and the tool prepares a clean, anonymous way to open the public profile. From there you can browse the highlight covers and tap any one to watch it. Because highlights are permanent rather than 24-hour stories, you can revisit them any time.
          </p>
        </div>

        <div>
          <h2>Can people tell if you view their highlights?</h2>
          <p>
            This is the most common question, and the answer is reassuring. Instagram keeps a viewer list only for active stories that expire after 24 hours. Permanent highlights do not have a viewer list, so opening and browsing a public profile's highlights does not reveal your identity or send the owner a notification. There is nothing for them to see.
          </p>
          <p>
            That makes a highlights viewer ideal for catching up on content quietly, whether you are a casual browser, a marketer checking competitor highlights, or someone who simply does not want to interact with a post or follow an account just to see its pinned stories.
          </p>
        </div>

        <div>
          <h2>Public profiles only, and why that matters</h2>
          <p>
            This tool works exclusively with public Instagram accounts. Private profiles lock all of their content, including highlights, stories, and posts, behind a follow approval at the platform level. No third-party viewer can bypass that restriction, and that is a good thing for everyone's privacy. If an account is private, the only way to see its highlights is to follow it and be approved by the owner.
          </p>
          <ul>
            <li>Enter the username exactly as it appears on the profile.</li>
            <li>Make sure the account is public before looking it up.</li>
            <li>Use it for content you are allowed to view, and respect people's privacy.</li>
          </ul>
        </div>

        <div>
          <h2>Instagram highlights viewer frequently searched questions</h2>
          <p>
            People often ask how to view Instagram highlights without an account, whether an anonymous highlights viewer is free, and if the owner can tell. The short answer: enter a public username, open the profile, and browse the highlights, all without logging in and without appearing in any viewer list. Because this page runs in the browser and needs no account, you can use it any time you want a quick, private way to view Instagram highlights.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need Instagram data, not just highlights?"
        sub="Captapi gives you APIs for Instagram, YouTube, TikTok, and Facebook transcripts, summaries, comments, and stats. Start free and automate the data side of your content workflow."
      />
    </>
  );
}
