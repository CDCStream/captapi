// Generates catalog.json for the Captapi Zapier app from the shared endpoint
// catalog. Single source of truth: ../captapi-n8n/src/catalog.ts
//
// Run with Node >= 22.6 (TypeScript type-stripping enabled):
//   node generate.mjs

import { writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const { ENDPOINTS } = await import("../captapi-n8n/src/catalog.ts");

const HERE = dirname(fileURLToPath(import.meta.url));

const PLATFORM_LABELS = {
  youtube: "YouTube",
  tiktok: "TikTok",
  instagram: "Instagram",
  facebook: "Facebook",
  twitter: "Twitter / X",
  reddit: "Reddit",
  threads: "Threads",
  bluesky: "Bluesky",
  pinterest: "Pinterest",
  linkedin: "LinkedIn",
  rumble: "Rumble",
  google: "Google",
  twitch: "Twitch",
  spotify: "Spotify",
  soundcloud: "SoundCloud",
  linktree: "Linktree",
  snapchat: "Snapchat",
  truth_social: "Truth Social",
  kick: "Kick",
  amazon_shop: "Amazon Shop",
  age_gender: "Age and Gender",
  account: "Account",
  kwai: "Kwai",
  komi: "Komi",
  pillar: "Pillar",
  linkbio: "Linkbio",
  linkme: "Linkme",
  tiktok_shop: "TikTok Shop",
  github: "GitHub",
  ad_library: "Ad Library",
};

const catalog = ENDPOINTS.map((e) => ({
  tool: e.tool,
  platform: PLATFORM_LABELS[e.platform] ?? e.platform,
  name: e.name,
  path: e.path,
  credits: e.credits,
  summary: e.summary,
  params: e.params,
}));

writeFileSync(
  `${HERE}/catalog.json`,
  JSON.stringify(catalog, null, 2) + "\n",
  "utf8",
);
console.log(`Wrote catalog.json with ${catalog.length} endpoints`);
