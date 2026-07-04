import { buildMetadata } from "@/lib/seo";
import { BestTimePage } from "@/components/tools/best-time-page";
import { BEST_TIME } from "@/lib/best-time-data";

const PATH = "/tools/best-time-to-post-on-tiktok";
const TITLE = "Best Time to Post on TikTok";
const DESC =
  "The best times to post on TikTok every day of the week, shown in your local time zone. See today's top slots and a full weekly schedule. Free, no sign-up.";
const KEYWORDS = [
  "best time to post on tiktok",
  "best time to post on tiktok today",
  "best time to post tiktok",
  "when to post on tiktok",
  "best time to post on tiktok saturday",
  "best time to post on tiktok sunday",
];

const FAQS = [
  { q: "What is the overall best time to post on TikTok?", a: "Across the week, Tuesday around 9 AM, Thursday around noon, and Friday in the early morning tend to see the strongest engagement. This tool converts those windows into your local time zone so the advice matches when your own audience is awake and scrolling." },
  { q: "What is the best time to post on TikTok today?", a: "Scroll to the highlighted \u201ctoday\u201d card at the top of this page. It shows the best posting slots for the current day, already adjusted to your local time zone based on TikTok engagement patterns." },
  { q: "How many times a day should I post on TikTok?", a: "TikTok's own guidance suggests posting 1\u20134 times per day for growth. If you post multiple times, spread uploads across the day's best windows rather than clustering them, and prioritize consistency over hitting an exact minute." },
  { q: "Does posting time really matter on TikTok?", a: "Yes, but less than on some platforms because TikTok's For You Page keeps surfacing content over days. Still, posting when your followers are active gives a video the early watch time and engagement that help it get picked up, so a good time gives you a better starting push." },
  { q: "What are the worst times to post on TikTok?", a: "Sunday mornings and weekday late nights after 11 PM are typically the quietest windows. If that is the only time you can post, staying consistent still beats skipping days to wait for a perfect slot." },
  { q: "Should I use my TikTok analytics instead?", a: "Once you have a Pro or Business account with enough activity, yes \u2014 your Follower Activity chart shows exactly when your audience is online. Use these general windows to start, then fine-tune with your own data." },
];

export const metadata = buildMetadata({ title: TITLE + " — Daily Schedule in Your Time Zone | Captapi", description: DESC, path: PATH, keywords: KEYWORDS });

export default function Page() {
  return <BestTimePage config={BEST_TIME.tiktok} path={PATH} title={TITLE} description={DESC} keywords={KEYWORDS} faqs={FAQS} />;
}
