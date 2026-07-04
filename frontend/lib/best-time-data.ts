// Best-time-to-post data. Hours are in ET (America/New_York), the reference
// zone most published social-media engagement studies use. The client shifts
// every slot into the visitor's local zone so the advice is personalized.
// Each hour is 0-23 ET. "top" = strongest slots, "good" = solid alternatives.

export type BestTimePlatform = "tiktok" | "instagram" | "facebook" | "youtube";

export interface DaySlots {
  day: string; // Monday .. Sunday
  top: number[]; // best hours (ET)
  good: number[]; // secondary hours (ET)
}

export interface BestTimeConfig {
  platform: BestTimePlatform;
  label: string; // "TikTok"
  accent: string; // tailwind text color for highlights
  intro: string;
  bestOverall: string;
  worst: string;
  schedule: DaySlots[];
}

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

function build(rows: Record<string, [number[], number[]]>): DaySlots[] {
  return DAYS.map((day) => ({ day, top: rows[day][0], good: rows[day][1] }));
}

export const BEST_TIME: Record<BestTimePlatform, BestTimeConfig> = {
  tiktok: {
    platform: "tiktok",
    label: "TikTok",
    accent: "text-rose-500",
    intro:
      "TikTok engagement peaks in the early morning, mid-afternoon, and late evening when users scroll before work, on breaks, and in bed. Tuesday through Thursday are the strongest days.",
    bestOverall: "Tuesday 9 AM, Thursday 12 PM, and Friday 5 AM tend to see the highest engagement.",
    worst: "Sunday mornings and weekday late nights after 11 PM are the quietest windows.",
    schedule: build({
      Monday: [[6, 10, 22], [16, 19]],
      Tuesday: [[9, 14], [4, 19]],
      Wednesday: [[7, 11, 23], [15]],
      Thursday: [[9, 12, 19], [5, 17]],
      Friday: [[5, 13, 15], [10, 20]],
      Saturday: [[11, 19], [9, 16]],
      Sunday: [[7, 16], [13, 20]],
    }),
  },
  instagram: {
    platform: "instagram",
    label: "Instagram",
    accent: "text-fuchsia-500",
    intro:
      "Instagram Reels and feed posts do best late morning to early afternoon on weekdays, when people check the app on lunch breaks. Midweek consistently outperforms weekends.",
    bestOverall: "Wednesday 11 AM and Monday–Friday around noon are the most reliable high-engagement slots.",
    worst: "Late Sunday evenings and very early weekend mornings see the lowest reach.",
    schedule: build({
      Monday: [[11, 12], [7, 14]],
      Tuesday: [[10, 13], [8, 16]],
      Wednesday: [[11], [9, 12, 15]],
      Thursday: [[11, 14], [9, 17]],
      Friday: [[10, 13], [8, 15]],
      Saturday: [[10, 11], [13, 19]],
      Sunday: [[10, 16], [12, 18]],
    }),
  },
  facebook: {
    platform: "facebook",
    label: "Facebook",
    accent: "text-blue-500",
    intro:
      "Facebook Pages and Reels get the most engagement mid-morning to early afternoon on weekdays, with a secondary bump in the early evening when people wind down.",
    bestOverall: "Weekdays between 9 AM and 1 PM — Tuesday through Friday — perform best.",
    worst: "Weekend mornings and late nights after 10 PM are the weakest slots.",
    schedule: build({
      Monday: [[9, 12], [15, 19]],
      Tuesday: [[10, 13], [8, 16]],
      Wednesday: [[9, 11], [13, 18]],
      Thursday: [[10, 12], [9, 17]],
      Friday: [[9, 13], [11, 15]],
      Saturday: [[10, 12], [14, 19]],
      Sunday: [[12, 17], [10, 19]],
    }),
  },
  youtube: {
    platform: "youtube",
    label: "YouTube",
    accent: "text-red-500",
    intro:
      "Upload videos a few hours before your audience is most active — typically late afternoon and evening on weekdays, and mid-to-late morning on weekends when viewers have more free time.",
    bestOverall: "Thursday and Friday between 2 PM and 4 PM, plus weekends from 9 AM to 11 AM, are prime upload windows.",
    worst: "Early weekday mornings before 7 AM tend to get the least early traction.",
    schedule: build({
      Monday: [[14, 16], [18, 20]],
      Tuesday: [[14, 15], [16, 19]],
      Wednesday: [[14, 17], [12, 19]],
      Thursday: [[14, 16], [15, 20]],
      Friday: [[15, 16], [12, 18]],
      Saturday: [[9, 11], [10, 15]],
      Sunday: [[9, 10], [11, 16]],
    }),
  },
};

export const BEST_TIME_SLUGS = Object.values(BEST_TIME).map(
  (c) => `best-time-to-post-on-${c.platform}`,
);
