import { buildMetadata } from "@/lib/seo";
import { BestTimePage } from "@/components/tools/best-time-page";
import { BEST_TIME } from "@/lib/best-time-data";

const PATH = "/tools/best-time-to-post-on-facebook";
const TITLE = "Best Time to Post on Facebook";
const DESC =
  "The best times to post on Facebook Pages and Reels every day of the week, shown in your local time zone. See today's top slots and a weekly schedule. Free, no sign-up.";
const KEYWORDS = [
  "best time to post on facebook",
  "best time to post on facebook today",
  "when to post on facebook",
  "best time to post facebook reels",
  "best time to post on facebook page",
];

const FAQS = [
  { q: "What is the overall best time to post on Facebook?", a: "Weekday mid-mornings to early afternoons \u2014 roughly 9 AM to 1 PM, Tuesday through Friday \u2014 tend to perform best. This tool converts those windows into your local time zone so they match when your Page audience is online." },
  { q: "What is the best time to post on Facebook today?", a: "See the highlighted \u201ctoday\u201d card near the top of the page. It shows the strongest posting slots for the current day, already adjusted to your local time zone." },
  { q: "Is the best time to post Facebook Reels different from regular posts?", a: "They overlap heavily. Regular Page posts do best in the mid-morning-to-lunch window, while Reels pick up an additional bump in the early evening. The weekday slots in the table cover both well." },
  { q: "How often should I post on a Facebook Page?", a: "For most Pages, 3\u20137 posts per week is a healthy range. Posting in the best windows and keeping a steady cadence matters more than sheer volume, which can suppress reach if quality drops." },
  { q: "What are the worst times to post on Facebook?", a: "Weekend mornings and late nights after 10 PM are usually the weakest slots. If those are your only options, consistency still beats skipping days." },
  { q: "Should I use Facebook Page Insights instead?", a: "Yes, when you have enough activity. The \u201cWhen Your Fans Are Online\u201d report shows exactly when your audience is active. Start with these general windows and refine with your own Insights." },
];

export const metadata = buildMetadata({ title: TITLE + " — Daily Schedule in Your Time Zone | Captapi", description: DESC, path: PATH, keywords: KEYWORDS });

export default function Page() {
  return <BestTimePage config={BEST_TIME.facebook} path={PATH} title={TITLE} description={DESC} keywords={KEYWORDS} faqs={FAQS} />;
}
