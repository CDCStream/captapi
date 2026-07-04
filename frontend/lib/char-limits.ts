// Character limits + video/story durations per platform, current as of 2026.

export interface CharLimit {
  field: string;
  limit: number;
  note?: string;
}

export interface PlatformLimits {
  id: string;
  label: string;
  limits: CharLimit[];
}

export const CHAR_LIMITS: PlatformLimits[] = [
  {
    id: "instagram",
    label: "Instagram",
    limits: [
      { field: "Caption", limit: 2200, note: "Feed shows ~125 chars before \u201cmore\u201d" },
      { field: "Bio", limit: 150 },
      { field: "Username", limit: 30 },
      { field: "Comment", limit: 2200 },
      { field: "Hashtags per post", limit: 30, note: "count, not characters" },
    ],
  },
  {
    id: "tiktok",
    label: "TikTok",
    limits: [
      { field: "Caption", limit: 4000 },
      { field: "Bio", limit: 80 },
      { field: "Username", limit: 24 },
      { field: "Comment", limit: 150 },
    ],
  },
  {
    id: "x",
    label: "X (Twitter)",
    limits: [
      { field: "Post", limit: 280, note: "Premium: up to 25,000" },
      { field: "Bio", limit: 160 },
      { field: "Display name", limit: 50 },
      { field: "DM", limit: 10000 },
    ],
  },
  {
    id: "youtube",
    label: "YouTube",
    limits: [
      { field: "Title", limit: 100, note: "~70 chars visible in search" },
      { field: "Description", limit: 5000 },
      { field: "Tags (total)", limit: 500 },
      { field: "Comment", limit: 10000 },
    ],
  },
  {
    id: "facebook",
    label: "Facebook",
    limits: [
      { field: "Post", limit: 63206, note: "~477 chars shown before \u201cSee more\u201d" },
      { field: "Bio / Intro", limit: 101 },
      { field: "Page description", limit: 255 },
      { field: "Ad primary text", limit: 125, note: "recommended before truncation" },
    ],
  },
  {
    id: "linkedin",
    label: "LinkedIn",
    limits: [
      { field: "Post", limit: 3000, note: "~210 chars shown before \u201csee more\u201d" },
      { field: "Headline", limit: 220 },
      { field: "About section", limit: 2600 },
      { field: "Connection note", limit: 300, note: "200 for free accounts" },
    ],
  },
  {
    id: "discord",
    label: "Discord",
    limits: [
      { field: "Message", limit: 2000, note: "Nitro: 4,000" },
      { field: "About Me bio", limit: 190 },
      { field: "Username", limit: 32 },
      { field: "Custom status", limit: 128 },
    ],
  },
  {
    id: "threads",
    label: "Threads",
    limits: [
      { field: "Post", limit: 500 },
      { field: "Bio", limit: 150 },
    ],
  },
  {
    id: "pinterest",
    label: "Pinterest",
    limits: [
      { field: "Pin title", limit: 100 },
      { field: "Pin description", limit: 500 },
      { field: "Bio", limit: 160 },
      { field: "Board name", limit: 50 },
    ],
  },
];

export interface DurationSpec {
  platform: string;
  format: string;
  duration: string;
  note?: string;
}

export const VIDEO_DURATIONS: DurationSpec[] = [
  { platform: "Instagram", format: "Story", duration: "Up to 60 seconds per card", note: "Longer videos split into 60s segments automatically" },
  { platform: "Instagram", format: "Reel", duration: "Up to 3 minutes" },
  { platform: "Instagram", format: "Feed video", duration: "Up to 60 minutes", note: "Shared as a reel for most accounts" },
  { platform: "TikTok", format: "Video (in-app record)", duration: "Up to 10 minutes" },
  { platform: "TikTok", format: "Video (upload)", duration: "Up to 60 minutes for eligible accounts" },
  { platform: "TikTok", format: "Story", duration: "Up to 15 seconds" },
  { platform: "YouTube", format: "Short", duration: "Up to 3 minutes" },
  { platform: "YouTube", format: "Video", duration: "Up to 12 hours / 256 GB", note: "Verified accounts; unverified capped at 15 minutes" },
  { platform: "Snapchat", format: "Story snap", duration: "Up to 60 seconds" },
  { platform: "Facebook", format: "Story", duration: "Up to 20 seconds per card" },
  { platform: "Facebook", format: "Reel", duration: "Up to 90 seconds" },
  { platform: "X", format: "Video", duration: "Up to 2:20", note: "Premium: up to ~4 hours" },
];
