// Live end-to-end test of the published CLI surface against the production API.
// Iterates every tool in dist/catalog.js; endpoints listed in INPUTS/CHAINS are
// called, the rest are reported as NO_INPUT. Uses the rebuilt dist catalog.
//
//   node scripts/live-test.mjs            # all catalog tools
//   node scripts/live-test.mjs youtube    # one platform
//
// Reads the API key from ~/.captapi/config.json (run `captapi login` first).
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { ENDPOINTS } from "../dist/catalog.js";

const HERE = dirname(fileURLToPath(import.meta.url));
const CLI = join(HERE, "..", "dist", "index.js");

const YT_VIDEO = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
const YT_CHANNEL = "https://www.youtube.com/@MrBeast";
const YT_SHORT = "https://www.youtube.com/watch?v=DXVHmGoCTco";
const TT_VIDEO = "https://www.tiktok.com/@khaby.lame/video/7646812028874673439";
const TT_PROFILE = "https://www.tiktok.com/@khaby.lame";
const TT_MUSIC = "https://www.tiktok.com/music/original-sound-6742811896934845190";
const IG_POST = "https://www.instagram.com/p/DZFqdAxlkUG/";
const IG_REEL = "https://www.instagram.com/p/DZFsjH9E3gK/";
const IG_PROFILE = "https://www.instagram.com/natgeo/";
const IG_AUDIO = "https://www.instagram.com/reels/audio/1186127252493819/";
const FB_POST =
  "https://www.facebook.com/NASA/posts/pfbid02skzNsrLf5atYZfzvzHAK9gHwDnZC5u4pDZMLQ1u3iJmfoA8tNsGpT7Uj6WPs6K3Rl";
const FB_PAGE = "https://www.facebook.com/NASA";
const FB_GROUP = "https://www.facebook.com/groups/444075055796968";
const KWAI_PROFILE = "https://www.kwai.com/@easycashindonesia";
const L = "2"; // small limit to keep credit cost down

// Static args per command (chained ones resolved at runtime; see CHAINS).
const INPUTS = {
  "youtube-transcript": ["--url", YT_VIDEO],
  "youtube-summarize": ["--url", YT_VIDEO],
  "youtube-video-details": ["--url", YT_VIDEO],
  "youtube-comments": ["--url", YT_VIDEO, "--limit", L],
  "youtube-channel-details": ["--url", YT_CHANNEL],
  "youtube-search": ["--q", "mrbeast", "--limit", L],
  "youtube-channel-videos": ["--url", YT_CHANNEL, "--limit", L],
  "youtube-playlist-videos": null, // chained
  "youtube-shorts-transcript": ["--url", YT_SHORT],
  "youtube-shorts-summarize": ["--url", YT_SHORT],
  "youtube-shorts-details": ["--url", YT_SHORT],
  "youtube-shorts-comments": ["--url", YT_SHORT, "--limit", L],
  "youtube-channel-shorts": ["--url", YT_CHANNEL, "--limit", L],
  "youtube-channel-streams": ["--url", YT_CHANNEL, "--limit", L],
  "youtube-hashtag-search": ["--q", "shorts", "--limit", L],
  "youtube-comment-replies": null, // chained
  "youtube-channel-playlists": ["--url", YT_CHANNEL, "--limit", L],
  "youtube-community-posts": ["--url", YT_CHANNEL, "--limit", L],

  "tiktok-transcript": ["--url", TT_VIDEO],
  "tiktok-summarize": ["--url", TT_VIDEO],
  "tiktok-video-details": ["--url", TT_VIDEO],
  "tiktok-comments": ["--url", TT_VIDEO, "--limit", L],
  "tiktok-channel-details": ["--url", TT_PROFILE],
  "tiktok-channel-posts": ["--url", TT_PROFILE, "--limit", L],
  "tiktok-comment-replies": null, // chained
  "tiktok-user-followers": ["--url", TT_PROFILE, "--limit", L],
  "tiktok-user-followings": ["--url", TT_PROFILE, "--limit", L],
  "tiktok-music-posts": ["--url", TT_MUSIC, "--limit", L],
  "tiktok-top-search": ["--q", "funny", "--limit", L],
  "tiktok-search-by-hashtag": ["--q", "funny", "--limit", L],
  "tiktok-search-users": ["--q", "khaby", "--limit", L],
  "tiktok-song-details": ["--url", TT_MUSIC],
  "tiktok-trending-feed": ["--country", "US", "--limit", L],
  "tiktok-popular-hashtags": ["--query", "funny", "--limit", L],

  "instagram-transcript": ["--url", IG_REEL],
  "instagram-summarize": ["--url", IG_REEL],
  "instagram-details": ["--url", IG_POST],
  "instagram-comments": ["--url", IG_POST, "--limit", L],
  "instagram-channel-details": ["--url", IG_PROFILE],
  "instagram-channel-posts": ["--url", IG_PROFILE, "--limit", L],
  "instagram-channel-reels": ["--url", IG_PROFILE, "--limit", L],
  "instagram-reels-search": ["--q", "travel", "--limit", L],
  "instagram-tagged-posts": ["--url", IG_PROFILE, "--limit", L],
  "instagram-hashtag-search": ["--q", "travel", "--limit", L],
  "instagram-profile-search": ["--q", "nasa", "--limit", L],
  "instagram-embed": ["--url", IG_POST],
  "instagram-basic-profile": ["--userId", "314216"],
  "instagram-reels-by-audio-id": ["--audio_id", IG_AUDIO, "--limit", L],

  "kwai-profile": ["--url", KWAI_PROFILE],
  "kwai-user-posts": ["--url", KWAI_PROFILE, "--limit", L],

  "facebook-details": ["--url", FB_POST],
  "facebook-transcript": ["--url", FB_POST],
  "facebook-summarize": ["--url", FB_POST],
  "facebook-comments": ["--url", FB_POST, "--limit", L],
  "facebook-page-details": ["--url", FB_PAGE],
  "facebook-profile-posts": ["--url", FB_PAGE, "--limit", L],
  "facebook-profile-reels": ["--url", FB_PAGE, "--limit", L],
  "facebook-group-posts": ["--url", FB_GROUP, "--limit", L],
  "facebook-comment-replies": null, // chained
};

function run(args) {
  return new Promise((resolve) => {
    const p = spawn(process.execPath, [CLI, ...args], {
      env: process.env,
    });
    let out = "";
    let err = "";
    p.stdout.on("data", (d) => (out += d));
    p.stderr.on("data", (d) => (err += d));
    p.on("close", (code) => {
      let json;
      try {
        json = JSON.parse(out);
      } catch {
        json = undefined;
      }
      resolve({ code, out, err, json });
    });
  });
}

/** Walk a response object to find the first plausible comment id. */
function findCommentId(json) {
  const data = json?.data ?? json;
  const arr =
    data?.comments || data?.items || data?.results || data?.data || [];
  for (const it of Array.isArray(arr) ? arr : []) {
    const id = it?.commentId || it?.id || it?.cid;
    if (id) return String(id);
  }
  return null;
}

const CHAINS = {
  "youtube-comment-replies": async () => {
    const r = await run(["youtube-comments", "--url", YT_VIDEO, "--limit", "5"]);
    const id = findCommentId(r.json);
    return id ? ["--url", YT_VIDEO, "--comment_id", id, "--limit", L] : null;
  },
  "tiktok-comment-replies": async () => {
    const r = await run(["tiktok-comments", "--url", TT_VIDEO, "--limit", "5"]);
    const id = findCommentId(r.json);
    return id ? ["--url", TT_VIDEO, "--comment_id", id, "--limit", L] : null;
  },
  "facebook-comment-replies": async () => {
    const r = await run(["facebook-comments", "--url", FB_POST, "--limit", "5"]);
    const id = findCommentId(r.json);
    return id ? ["--url", FB_POST, "--comment_id", id, "--limit", L] : null;
  },
  "youtube-playlist-videos": async () => {
    const r = await run(["youtube-channel-playlists", "--url", YT_CHANNEL, "--limit", "3"]);
    const data = r.json?.data ?? {};
    const list = data.playlists || data.items || [];
    const purl = (Array.isArray(list) ? list : [])
      .map((x) => x?.url)
      .find((u) => typeof u === "string" && u.includes("list="));
    return purl ? ["--url", purl, "--limit", L] : null;
  },
};

async function balance() {
  const r = await run(["balance", "--json"]);
  return r.json?.data?.balance?.total_credits ?? null;
}

function classify(res) {
  if (res.code !== 0) return res.json ? "API_ERR" : "CLI_ERR";
  if (res.json?.success === true) {
    const d = res.json.data ?? {};
    const empty = Object.values(d).some(
      (v) => Array.isArray(v) && v.length === 0,
    );
    return empty ? "OK_EMPTY" : "OK";
  }
  return "FAIL";
}

async function main() {
  const only = process.argv[2];
  const eps = ENDPOINTS.filter((e) => !only || e.platform === only);
  console.log(`Live testing ${eps.length} commands against production…\n`);

  const startCredits = await balance();
  const rows = [];

  for (const e of eps) {
    const cmd = e.tool.replace(/_/g, "-");
    let args = INPUTS[cmd];
    if (args === null && CHAINS[cmd]) args = await CHAINS[cmd]();
    if (!args) {
      rows.push({ cmd, status: "NO_INPUT", note: "" });
      console.log(`  -  ${cmd.padEnd(30)} NO_INPUT`);
      continue;
    }
    const t0 = Date.now();
    const res = await run([cmd, ...args]);
    const ms = Date.now() - t0;
    const status = classify(res);
    let note = "";
    if (status === "FAIL" || status.endsWith("ERR")) {
      note = (res.json ? JSON.stringify(res.json.detail ?? res.json) : res.err)
        .slice(0, 120)
        .replace(/\s+/g, " ");
    }
    const mark =
      status === "OK" ? "✓" : status === "OK_EMPTY" ? "≈" : "✗";
    rows.push({ cmd, status, ms, note });
    console.log(
      `  ${mark}  ${cmd.padEnd(30)} ${status.padEnd(9)} ${String(ms).padStart(6)}ms ${note}`,
    );
  }

  const endCredits = await balance();

  const tally = rows.reduce((m, r) => ((m[r.status] = (m[r.status] || 0) + 1), m), {});
  console.log("\n── Summary ──");
  for (const [k, v] of Object.entries(tally)) console.log(`  ${k}: ${v}`);
  console.log(`  TOTAL: ${rows.length}`);
  if (startCredits != null && endCredits != null)
    console.log(`  Credits: ${startCredits} → ${endCredits} (spent ${startCredits - endCredits})`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
