import { buildMetadata } from "@/lib/seo";
import { BestTimePage } from "@/components/tools/best-time-page";
import { BEST_TIME } from "@/lib/best-time-data";

const PATH = "/tools/best-time-to-post-on-instagram";
const TITLE = "Best Time to Post on Instagram";
const DESC =
  "The best times to post on Instagram — Reels, feed posts, and Stories — every day of the week, shown in your local time zone. See today's top slots. Free, no sign-up.";
const KEYWORDS = [
  "best time to post on instagram",
  "best time to post on instagram today",
  "when to post on instagram",
  "best time to post reels",
  "best time to post on instagram reels",
];

const FAQS = [
  { q: "What is the overall best time to post on Instagram?", a: "Midweek late mornings win most often \u2014 Wednesday around 11 AM and weekday slots around noon consistently perform well. This tool shifts those windows into your local time zone so they match when your followers actually open the app." },
  { q: "What is the best time to post on Instagram today?", a: "Check the highlighted \u201ctoday\u201d card at the top of the page. It lists the strongest posting slots for the current day, already converted to your local time zone." },
  { q: "Is the best time to post Reels different from feed posts?", a: "The windows are broadly similar, but Reels get an extra lift in the evenings when people watch video to unwind. The late-morning-to-noon slots in the table work well for both; add an early-evening Reel when you can." },
  { q: "How often should I post on Instagram?", a: "A common rhythm is 3\u20135 feed posts or Reels per week plus daily Stories. Quality and consistency matter more than volume \u2014 pick a sustainable cadence and post in the best windows rather than flooding a single day." },
  { q: "What are the worst times to post on Instagram?", a: "Late Sunday evenings and very early weekend mornings tend to see the lowest reach. If those are your only options, consistency still beats waiting for a perfect slot." },
  { q: "Should I rely on Instagram Insights instead?", a: "Yes, once you have a professional account with enough followers. Insights shows the exact hours your audience is most active. Use these general windows to begin and then tune to your own data." },
];

export const metadata = buildMetadata({ title: TITLE + " — Daily Schedule in Your Time Zone | Captapi", description: DESC, path: PATH, keywords: KEYWORDS });

export default function Page() {
  return <BestTimePage config={BEST_TIME.instagram} path={PATH} title={TITLE} description={DESC} keywords={KEYWORDS} faqs={FAQS} />;
}
