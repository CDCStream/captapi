// Who-can-see-viewers rules per platform, current as of 2026.

export type Visibility = "yes" | "no" | "partial";

export interface ViewRule {
  action: string;
  visible: Visibility;
  detail: string;
}

export interface PlatformViewRules {
  id: string;
  label: string;
  summary: string;
  rules: ViewRule[];
}

export const WHO_VIEWED_RULES: PlatformViewRules[] = [
  {
    id: "instagram",
    label: "Instagram",
    summary:
      "Instagram never shows who viewed your profile. You CAN see who viewed your stories while they're up (and for 48 hours after posting) — but posts and reels only show counts, not names.",
    rules: [
      { action: "Profile visits", visible: "no", detail: "No name list exists. Professional accounts see an aggregate profile-visits number in insights, but never who. Any app claiming to show profile stalkers is a scam." },
      { action: "Story viewers", visible: "yes", detail: "Open your story and swipe up to see the full viewer list. The list is available while the story is live and for 48 hours after posting (also in your archive)." },
      { action: "Post / reel views", visible: "no", detail: "You see view and like counts; likers are listed by name, but viewers are not." },
      { action: "Highlights", visible: "partial", detail: "Viewer lists only cover the first 48 hours after the original story was posted — older highlight views are counted but anonymous." },
    ],
  },
  {
    id: "tiktok",
    label: "TikTok",
    summary:
      "TikTok shows profile viewers only if BOTH people have Profile View History turned on — and only for the last 30 days. Video views are anonymous.",
    rules: [
      { action: "Profile visits", visible: "partial", detail: "Turn on Profile View History (Profile \u2192 menu \u2192 Settings \u2192 Privacy \u2192 Profile views). You'll see who visited in the last 30 days — but only visitors who also have the feature enabled. It's off by default and only available to accounts under 5,000 followers." },
      { action: "Video views", visible: "no", detail: "View counts are public but TikTok never lists who watched a video." },
      { action: "Story viewers", visible: "yes", detail: "Tap your story and the eye icon to see who viewed it while it's live (24 hours)." },
      { action: "Post likes", visible: "yes", detail: "Likers are always listed by name on your own videos." },
    ],
  },
  {
    id: "snapchat",
    label: "Snapchat",
    summary:
      "Snapchat shows exactly who viewed your story, and rewatch indicators with Snapchat+. Profile visits are not tracked.",
    rules: [
      { action: "Story viewers", visible: "yes", detail: "Open your story and swipe up — every viewer is listed, and screenshots are flagged with an icon." },
      { action: "Story rewatches", visible: "partial", detail: "Snapchat+ subscribers see a rewatch indicator (an emoji next to viewers who watched more than once) — but not how many times." },
      { action: "Profile visits", visible: "no", detail: "Snapchat does not track or show who viewed your profile." },
      { action: "Snap opens", visible: "yes", detail: "Direct snaps show 'Opened' status per recipient — you always know when someone opened your snap." },
    ],
  },
  {
    id: "facebook",
    label: "Facebook",
    summary:
      "Facebook never shows who viewed your profile — despite decades of scam apps claiming otherwise. Story viewers are visible.",
    rules: [
      { action: "Profile visits", visible: "no", detail: "Facebook has repeatedly confirmed no such feature exists, and third-party \u201cprofile viewer\u201d apps violate their terms — most are phishing." },
      { action: "Story viewers", visible: "yes", detail: "Open your story to see the full viewer list while it's live (24 hours)." },
      { action: "Post views", visible: "no", detail: "You see reactions and comments by name, but not silent viewers. Pages/reels show counts only." },
      { action: "Video / reel views", visible: "no", detail: "Counts only, no names." },
    ],
  },
  {
    id: "linkedin",
    label: "LinkedIn",
    summary:
      "LinkedIn is the exception: it has an official \u201cWho viewed your profile\u201d feature. Free accounts see a few recent viewers; Premium unlocks the full 365-day list.",
    rules: [
      { action: "Profile visits", visible: "yes", detail: "Me \u2192 View profile \u2192 Analytics shows viewers. Free accounts see up to 5 recent viewers; Premium shows everyone from the last 365 days — unless the viewer browsed in private mode." },
      { action: "Private-mode viewers", visible: "no", detail: "Viewers using private mode appear as \u201cLinkedIn Member\u201d with no details, regardless of your subscription." },
      { action: "Post views", visible: "partial", detail: "You see impression counts and the companies/roles of viewers in analytics, but not a full name list." },
      { action: "Your own anonymity", visible: "partial", detail: "If you browse in private mode, you also lose the ability to see who viewed you (on free accounts)." },
    ],
  },
];

export const VISIBILITY_LABELS: Record<Visibility, string> = {
  yes: "Visible",
  no: "Not visible",
  partial: "Partial / conditional",
};
