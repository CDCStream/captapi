import { JsonLd } from "@/components/seo/json-ld";
import { breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { BestTimeClient } from "@/components/tools/best-time-client";
import { CalendarClock, Clock, MapPin, LineChart } from "lucide-react";
import type { BestTimeConfig } from "@/lib/best-time-data";

const STEPS = [
  { title: "We detect your time zone", text: "Every slot is converted from the study's reference zone into your local time automatically.", icon: <MapPin className="size-4" /> },
  { title: "Check today's best slots", text: "The highlighted card shows the strongest posting times for the current day.", icon: <Clock className="size-4" /> },
  { title: "Plan the week", text: "Use the full table to schedule content on the best day-and-hour combinations.", icon: <CalendarClock className="size-4" /> },
  { title: "Verify with your analytics", text: "Post consistently, then confirm against your own audience insights.", icon: <LineChart className="size-4" /> },
];

export function BestTimePage({
  config,
  path,
  title,
  description,
  keywords,
  faqs,
}: {
  config: BestTimeConfig;
  path: string;
  title: string;
  description: string;
  keywords: string[];
  faqs: { q: string; a: string }[];
}) {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: title, description, path, category: "BusinessApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: title, path }])} />
      <JsonLd data={faqLd(faqs)} />

      <ToolHero platform={config.label} title={title} subtitle={config.intro} />

      <BestTimeClient config={config} />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>When is the best time to post on {config.label}?</h2>
          <p>{config.bestOverall}</p>
          <p>
            The single most important thing to know is that &quot;best time&quot; is relative to your
            audience&apos;s time zone, not the studies that report it. That is why this tool converts every
            recommended slot into <strong>your</strong> local time — so a &quot;9 AM&quot; tip actually lines
            up with when you should hit publish.
          </p>
        </div>
        <div>
          <h2>Times to avoid</h2>
          <p>{config.worst}</p>
          <p>
            Low-traffic windows are not forbidden — they just start with a smaller initial audience, which
            matters most on platforms where early engagement influences distribution. If a quiet slot is the
            only time you can post consistently, consistency still wins over a &quot;perfect&quot; time you
            can never hit.
          </p>
        </div>
        <div>
          <h2>Why posting time matters on {config.label}</h2>
          <p>
            Most social platforms weigh the engagement a post earns in its first minutes and hours. Publishing
            when your followers are already active gives a post the early likes, comments, and watch time that
            signal the algorithm to show it to more people. Posting into a dead window means competing later
            from a colder start. Use these windows as a schedule, keep your cadence steady, and let your own
            analytics fine-tune the details over time.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={faqs} />
      <ToolCTA
        headline={`Tracking ${config.label} performance at scale?`}
        sub="Captapi returns profile stats, post/video details, and engagement metrics as clean JSON across YouTube, TikTok, Instagram, and Facebook. Start free with 100 credits — no card required."
      />
    </>
  );
}
