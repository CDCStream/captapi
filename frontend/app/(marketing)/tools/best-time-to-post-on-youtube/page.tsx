import { buildMetadata } from "@/lib/seo";
import { BestTimePage } from "@/components/tools/best-time-page";
import { BEST_TIME } from "@/lib/best-time-data";

const PATH = "/tools/best-time-to-post-on-youtube";
const TITLE = "Best Time to Post on YouTube";
const DESC =
  "The best days and times to upload YouTube videos and Shorts, shown in your local time zone. See today's top slots and a full weekly schedule. Free, no sign-up.";
const KEYWORDS = [
  "best time to post on youtube",
  "best time to upload youtube videos",
  "when to post on youtube",
  "best time to post youtube shorts",
  "best time to upload on youtube",
];

const FAQS = [
  { q: "What is the overall best time to upload on YouTube?", a: "Thursday and Friday between 2 PM and 4 PM, plus weekend late mornings from 9 AM to 11 AM, are prime upload windows. The idea is to publish a few hours before your audience's peak viewing so the video is indexed and ready. This tool converts those windows into your local time zone." },
  { q: "What is the best time to post on YouTube today?", a: "Check the highlighted \u201ctoday\u201d card at the top of the page for the strongest upload slots for the current day, already adjusted to your local time zone." },
  { q: "Should I upload before my audience is active?", a: "Yes. Unlike short-form feeds, YouTube needs time to process and index a video. Publishing 2\u20134 hours before your typical peak viewing time gives the upload a head start so it is ready when viewers arrive." },
  { q: "Is the best time to post Shorts different from long videos?", a: "Shorts behave more like other short-form feeds and get evening engagement, while long videos benefit from the pre-peak upload strategy. The weekday afternoon and weekend morning slots in the table work for both." },
  { q: "How often should I upload to YouTube?", a: "Consistency matters more than frequency. A reliable weekly (or twice-weekly) schedule that your audience can anticipate outperforms sporadic bursts. Pick a day and time from the table and stick to it." },
  { q: "Should I use YouTube Analytics instead?", a: "Yes, once you have enough watch history. The \u201cWhen your viewers are on YouTube\u201d report in Analytics shows your audience's actual active hours. Use these general windows to start and refine with your own data." },
];

export const metadata = buildMetadata({ title: TITLE + " — Daily Upload Schedule in Your Time Zone | Captapi", description: DESC, path: PATH, keywords: KEYWORDS });

export default function Page() {
  return <BestTimePage config={BEST_TIME.youtube} path={PATH} title={TITLE} description={DESC} keywords={KEYWORDS} faqs={FAQS} />;
}
