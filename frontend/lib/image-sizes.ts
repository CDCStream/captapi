// Social media image & video dimensions, current as of 2026.

export interface SizeSpec {
  name: string;
  size: string; // "1080 × 1350 px"
  ratio: string; // "4:5"
  note?: string;
}

export interface PlatformSizes {
  id: string;
  label: string;
  specs: SizeSpec[];
}

export const IMAGE_SIZES: PlatformSizes[] = [
  {
    id: "instagram",
    label: "Instagram",
    specs: [
      { name: "Feed post (portrait, recommended)", size: "1080 × 1350 px", ratio: "4:5", note: "Takes the most screen space in feed — the default choice." },
      { name: "Feed post (square)", size: "1080 × 1080 px", ratio: "1:1" },
      { name: "Feed post (landscape)", size: "1080 × 566 px", ratio: "1.91:1" },
      { name: "Story / Reel", size: "1080 × 1920 px", ratio: "9:16", note: "Keep text inside the middle ~1080 × 1420 safe zone — UI covers top and bottom." },
      { name: "Profile picture", size: "320 × 320 px", ratio: "1:1", note: "Displayed as a circle — keep the subject centered." },
      { name: "Reel cover", size: "1080 × 1920 px", ratio: "9:16", note: "Also shown cropped 1:1 in the grid." },
    ],
  },
  {
    id: "tiktok",
    label: "TikTok",
    specs: [
      { name: "Video", size: "1080 × 1920 px", ratio: "9:16", note: "Full-screen vertical. TikTok compresses hard — export at high bitrate." },
      { name: "Profile photo", size: "200 × 200 px (min 20 × 20)", ratio: "1:1" },
      { name: "Photo mode / carousel", size: "1080 × 1920 px", ratio: "9:16", note: "1:1 also works but letterboxes." },
      { name: "Video cover", size: "1080 × 1920 px", ratio: "9:16", note: "Grid shows a 3:4 center crop — keep the title centered." },
    ],
  },
  {
    id: "youtube",
    label: "YouTube",
    specs: [
      { name: "Video", size: "1920 × 1080 px (up to 3840 × 2160)", ratio: "16:9" },
      { name: "Thumbnail", size: "1280 × 720 px", ratio: "16:9", note: "Under 2 MB, JPG/PNG/GIF. Text readable at 10% size wins clicks." },
      { name: "Shorts", size: "1080 × 1920 px", ratio: "9:16" },
      { name: "Channel banner", size: "2560 × 1440 px", ratio: "16:9", note: "Safe area (visible on all devices): the central 1546 × 423 px." },
      { name: "Profile picture", size: "800 × 800 px", ratio: "1:1", note: "Displayed as a circle." },
    ],
  },
  {
    id: "facebook",
    label: "Facebook",
    specs: [
      { name: "Feed post (landscape)", size: "1200 × 630 px", ratio: "1.91:1" },
      { name: "Feed post (portrait)", size: "1080 × 1350 px", ratio: "4:5" },
      { name: "Story / Reel", size: "1080 × 1920 px", ratio: "9:16" },
      { name: "Cover photo (Page)", size: "820 × 312 px desktop", ratio: "~2.6:1", note: "Mobile crops to 640 × 360 — keep content centered." },
      { name: "Profile picture", size: "170 × 170 px (desktop display)", ratio: "1:1", note: "Upload at least 320 × 320." },
      { name: "Event cover", size: "1200 × 628 px", ratio: "1.91:1" },
    ],
  },
  {
    id: "x",
    label: "X (Twitter)",
    specs: [
      { name: "In-feed image (single)", size: "1200 × 675 px", ratio: "16:9" },
      { name: "Header (banner)", size: "1500 × 500 px", ratio: "3:1" },
      { name: "Profile picture", size: "400 × 400 px", ratio: "1:1" },
      { name: "Card / link preview", size: "1200 × 628 px", ratio: "1.91:1" },
    ],
  },
  {
    id: "linkedin",
    label: "LinkedIn",
    specs: [
      { name: "Feed post image", size: "1200 × 627 px", ratio: "1.91:1" },
      { name: "Profile photo", size: "400 × 400 px", ratio: "1:1" },
      { name: "Personal banner", size: "1584 × 396 px", ratio: "4:1" },
      { name: "Company page banner", size: "1128 × 191 px", ratio: "~5.9:1" },
    ],
  },
  {
    id: "pinterest",
    label: "Pinterest",
    specs: [
      { name: "Standard pin", size: "1000 × 1500 px", ratio: "2:3", note: "Taller than 2100 px gets cut off in feed." },
      { name: "Square pin", size: "1000 × 1000 px", ratio: "1:1" },
      { name: "Idea pin / video", size: "1080 × 1920 px", ratio: "9:16" },
      { name: "Profile picture", size: "165 × 165 px", ratio: "1:1" },
    ],
  },
];
