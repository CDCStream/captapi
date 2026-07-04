// Screenshot notification rules per platform/action, current as of 2026.
// "notifies" is a tri-state: yes / no / partial (depends on context).

export type Notifies = "yes" | "no" | "partial";

export interface ScreenshotRule {
  action: string;
  notifies: Notifies;
  detail: string;
}

export interface PlatformRules {
  id: string;
  label: string;
  summary: string;
  rules: ScreenshotRule[];
}

export const SCREENSHOT_RULES: PlatformRules[] = [
  {
    id: "instagram",
    label: "Instagram",
    summary:
      "Instagram does NOT notify screenshots of stories, posts, reels, or profiles. The only exception is disappearing (view-once) photos and videos in DMs.",
    rules: [
      { action: "Story", notifies: "no", detail: "No notification is sent when you screenshot someone's story — even close-friends stories. The poster can see who viewed the story, but not who screenshotted it." },
      { action: "Post or Reel", notifies: "no", detail: "Screenshotting a feed post or reel never notifies the creator." },
      { action: "Profile", notifies: "no", detail: "Screenshotting someone's profile page sends no notification." },
      { action: "Regular DM chat", notifies: "no", detail: "Screenshots of normal text conversations in DMs are not reported." },
      { action: "Disappearing (view-once) photo or video in DMs", notifies: "yes", detail: "If someone sends a photo or video in 'view once' or 'allow replay' mode and you screenshot it, Instagram shows a shutter icon next to the message — the sender is notified." },
    ],
  },
  {
    id: "snapchat",
    label: "Snapchat",
    summary:
      "Snapchat notifies screenshots almost everywhere — snaps, stories, and chats all alert the other person.",
    rules: [
      { action: "Snap (photo or video)", notifies: "yes", detail: "The sender instantly gets a 'screenshot' notification with a double-arrow icon in the chat." },
      { action: "Story", notifies: "yes", detail: "The poster sees a screenshot icon next to your name in their story views list." },
      { action: "Chat messages", notifies: "yes", detail: "Screenshotting a conversation triggers a '… took a screenshot of Chat!' message visible to both of you." },
      { action: "Profile", notifies: "no", detail: "Screenshotting a profile page itself does not notify, but screenshotting a Snap or story from it does." },
      { action: "Memories", notifies: "no", detail: "Your own saved Memories are yours — no notifications involved." },
    ],
  },
  {
    id: "tiktok",
    label: "TikTok",
    summary:
      "TikTok does not notify screenshots or screen recordings of videos, profiles, or stories.",
    rules: [
      { action: "Video", notifies: "no", detail: "Screenshotting or screen-recording any TikTok video sends no notification to the creator." },
      { action: "Story", notifies: "no", detail: "TikTok stories do not report screenshots — viewers stay anonymous beyond the view list." },
      { action: "Profile", notifies: "no", detail: "No notification for screenshotting a profile." },
      { action: "Direct messages", notifies: "no", detail: "TikTok DMs do not report screenshots as of 2026 — but treat private chats with care anyway." },
    ],
  },
  {
    id: "facebook",
    label: "Facebook",
    summary:
      "Facebook and Messenger do not notify screenshots, with one exception: secret/vanish-mode conversations in Messenger.",
    rules: [
      { action: "Post or photo", notifies: "no", detail: "No notification for screenshotting posts, photos, or albums." },
      { action: "Story", notifies: "no", detail: "Facebook stories do not report screenshots." },
      { action: "Profile", notifies: "no", detail: "Screenshotting profiles sends no alert." },
      { action: "Regular Messenger chat", notifies: "no", detail: "Standard Messenger conversations do not report screenshots." },
      { action: "Vanish mode / disappearing messages", notifies: "yes", detail: "In vanish mode (and end-to-end encrypted disappearing messages), Messenger shows a notice in the chat when someone takes a screenshot." },
    ],
  },
  {
    id: "whatsapp",
    label: "WhatsApp",
    summary:
      "WhatsApp does not notify screenshots of chats or statuses, but it blocks screenshots of view-once media entirely.",
    rules: [
      { action: "Chat conversation", notifies: "no", detail: "No screenshot notifications for regular or group chats." },
      { action: "Status", notifies: "no", detail: "Screenshotting someone's status sends no alert — they only see that you viewed it." },
      { action: "Profile photo", notifies: "no", detail: "No notification for screenshotting profile photos." },
      { action: "View-once photo or video", notifies: "partial", detail: "WhatsApp blocks the screenshot instead of notifying — you get a black screen. The sender is not alerted, but you cannot capture the media." },
    ],
  },
];

export const NOTIFY_LABELS: Record<Notifies, string> = {
  yes: "Notifies",
  no: "No notification",
  partial: "Blocked / depends",
};
