import { spawn } from "node:child_process";
import { appendFileSync, existsSync, unlinkSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { ALL_ENDPOINTS, params as frontendParams } from "../frontend/lib/api-catalog";
import { ENDPOINTS as MCP_ENDPOINTS } from "../packages/captapi-mcp/src/catalog";

const API_KEY = process.env.CAPTAPI_API_KEY?.trim();
const BASE_URL = (process.env.CAPTAPI_BASE_URL || "https://api.captapi.com").replace(/\/$/, "");
const WEB_URL = (process.env.CAPTAPI_WEB_URL || "https://captapi.com").replace(/\/$/, "");
const LIVE = process.argv.includes("--live");
const MCP = process.argv.includes("--mcp");
const SKIP_PAGES = process.argv.includes("--skip-pages");
const LIMIT = "1";
const LIVE_REQUEST_TIMEOUT_MS = Number(process.env.CAPTAPI_AUDIT_TIMEOUT_MS || 45_000);
const LIVE_SLOW_THRESHOLD_MS = Number(process.env.CAPTAPI_AUDIT_SLOW_MS || 8_000);
const LIVE_CONCURRENCY = Number(process.env.CAPTAPI_AUDIT_CONCURRENCY || 8);
const LIVE_RPM = Number(process.env.CAPTAPI_AUDIT_RPM || 30);
const LIVE_429_RETRIES = Number(process.env.CAPTAPI_AUDIT_429_RETRIES || 1);
const LIVE_PROGRESS_FILE = join(process.cwd(), "comprehensive-live-audit-live.jsonl");
const ONLY_SLUGS = new Set(
  (process.env.CAPTAPI_AUDIT_ONLY || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean),
);

type Row = {
  slug: string;
  tool?: string;
  platform: string;
  path: string;
  status: string;
  http?: number;
  ms?: number;
  note?: string;
};

const YT_VIDEO = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
const YT_SHORT = "https://www.youtube.com/shorts/DXVHmGoCTco";
const YT_CHANNEL = "https://www.youtube.com/@MrBeast";
const YT_PLAYLIST = "https://www.youtube.com/playlist?list=PLM4u6gbmK0Y6BVTwsCwWqz2yh4HpRG6c2";
const TT_VIDEO = "https://www.tiktok.com/@khaby.lame/video/7646812028874673439";
const TT_PROFILE = "https://www.tiktok.com/@khaby.lame";
const TT_MUSIC = "https://www.tiktok.com/music/original-sound-6742811896934845190";
const IG_POST = "https://www.instagram.com/p/DZFqdAxlkUG/";
const IG_REEL = "https://www.instagram.com/reel/DZFsjH9E3gK/";
const IG_PROFILE = "https://www.instagram.com/natgeo/";
const IG_AUDIO_ID = "1186127252493819";
const FB_POST =
  "https://www.facebook.com/NASA/posts/pfbid02skzNsrLf5atYZfzvzHAK9gHwDnZC5u4pDZMLQ1u3iJmfoA8tNsGpT7Uj6WPs6K3Rl";
const FB_PAGE = "https://www.facebook.com/NASA";
const FB_GROUP = "https://www.facebook.com/groups/444075055796968";
const X_PROFILE = "https://x.com/NASA";
const X_POST = "https://x.com/NASA/status/1938958756698054876";
const REDDIT_POST = "https://www.reddit.com/r/programming/comments/1l3zv7o/";
const THREADS_PROFILE = "https://www.threads.net/@zuck";
const THREADS_POST = "https://www.threads.net/@zuck/post/CuVFQ9ovJ9D";
const BLUESKY_PROFILE = "https://bsky.app/profile/bsky.app";
const BLUESKY_POST = "https://bsky.app/profile/bsky.app/post/3kqfrsowfns2j";
const PINTEREST_PROFILE = "https://www.pinterest.com/nasa/";
const PINTEREST_PIN = "https://www.pinterest.com/pin/211174977333739/";
const LINKEDIN_PROFILE = "https://www.linkedin.com/in/williamhgates/";
const LINKEDIN_COMPANY = "https://www.linkedin.com/company/microsoft/";
const LINKEDIN_POST = "https://www.linkedin.com/posts/microsoft_activity-7338945708093050880-wwLq";
const RUMBLE_VIDEO = "https://rumble.com/v4w0mri-test.html";
const RUMBLE_CHANNEL = "https://rumble.com/c/Rumble";
const TWITCH_PROFILE = "https://www.twitch.tv/ninja";
const TWITCH_CLIP = "https://www.twitch.tv/ninja/clip/BlatantSoftBunnyBCouch";
const SPOTIFY_ARTIST = "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02";
const SPOTIFY_TRACK = "https://open.spotify.com/track/1dGr1c8CrMLDpV6mPbImSI";
const SPOTIFY_ALBUM = "https://open.spotify.com/album/151w1FgRZfnKZA9FEcg9Z3";
const SPOTIFY_PODCAST = "https://open.spotify.com/show/6ZcvVBPQ2ToLXEWVbaw59P";
const SOUNDCLOUD_ARTIST = "https://soundcloud.com/octobersveryown";
const SOUNDCLOUD_TRACK = "https://soundcloud.com/octobersveryown/drake-family-matters";
const LINKTREE_PROFILE = "https://linktr.ee/taylorswift";
const SNAPCHAT_PROFILE = "https://www.snapchat.com/add/teamsnapchat";
const TRUTH_PROFILE = "https://truthsocial.com/@realDonaldTrump";
const KICK_CLIP = "https://kick.com/xqc";
const AMAZON_SHOP = "https://www.amazon.com/stores/page/70B8C232-4C8C-49A0-9F6D-DFB7C8EA52BF";
const KWAI_PROFILE = "https://www.kwai.com/profile/524195695";
const KWAI_POST = "https://www.kwai.com/photo/524195695/5220781517837508406";
const KOMI_PAGE = "https://komi.io/charlidamelio";
const PILLAR_PAGE = "https://pillar.io/cacao";
const LINKBIO_PAGE = "https://lnk.bio/nasa";
const LINKME_PROFILE = "https://link.me/nasa";

const requestStarts: number[] = [];

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function acquireAuditSlot() {
  if (!Number.isFinite(LIVE_RPM) || LIVE_RPM <= 0) return;
  while (true) {
    const now = Date.now();
    while (requestStarts.length && now - requestStarts[0] >= 60_000) {
      requestStarts.shift();
    }
    if (requestStarts.length < LIVE_RPM) {
      requestStarts.push(now);
      return;
    }
    const waitMs = Math.max(250, 60_000 - (now - requestStarts[0]) + 250);
    await sleep(waitMs);
  }
}

function normalizePath(path: string) {
  return path.replace(/\/$/, "");
}

function statusOf(res: Response, bodyText: string) {
  if (res.ok) return "OK";
  if (res.status === 401 || res.status === 402) return "AUTH_OR_CREDITS";
  if (res.status === 404 || res.status === 422) return "INPUT_OR_EMPTY_TARGET";
  if (res.status === 429) return "RATE_LIMIT";
  if (res.status >= 500) return "SERVER_OR_UPSTREAM_FAIL";
  if (bodyText.includes("invalid") || bodyText.includes("missing")) return "PARAM_FAIL";
  return "HTTP_FAIL";
}

function findFirstId(value: unknown): string | null {
  if (!value || typeof value !== "object") return null;
  if (Array.isArray(value)) {
    for (const item of value) {
      const found = findFirstId(item);
      if (found) return found;
    }
    return null;
  }
  const record = value as Record<string, unknown>;
  for (const key of ["commentId", "comment_id", "id", "cid", "aweme_id", "post_id"]) {
    const found = record[key];
    if (typeof found === "string" || typeof found === "number") return String(found);
  }
  for (const child of Object.values(record)) {
    const found = findFirstId(child);
    if (found) return found;
  }
  return null;
}

function sampleUrl(path: string) {
  if (path.includes("/youtube/playlist")) return YT_PLAYLIST;
  if (path.includes("/youtube/shorts")) return YT_SHORT;
  if (path.includes("/youtube/channel") || path.includes("/youtube/community")) return YT_CHANNEL;
  if (path.includes("/youtube/")) return YT_VIDEO;
  if (path.includes("/tiktok/music") || path.includes("/tiktok/song")) return TT_MUSIC;
  if (path.includes("/tiktok/channel") || path.includes("/tiktok/user") || path.includes("/tiktok/live") || path.includes("/tiktok/profile") || path.includes("/tiktok/audience")) return TT_PROFILE;
  if (path.includes("/tiktok/")) return TT_VIDEO;
  if (path.includes("/instagram/music")) return `https://www.instagram.com/reels/audio/${IG_AUDIO_ID}/`;
  if (path.includes("/instagram/channel") || path.includes("/instagram/tagged") || path.includes("/instagram/story") || path.includes("/instagram/highlights") || path.includes("/instagram/basic-profile")) return IG_PROFILE;
  if (path.includes("/instagram/transcript") || path.includes("/instagram/summarize")) return IG_REEL;
  if (path.includes("/instagram/")) return IG_POST;
  if (path.includes("/facebook/page") || path.includes("/facebook/profile")) return FB_PAGE;
  if (path.includes("/facebook/group")) return FB_GROUP;
  if (path.includes("/facebook/marketplace-item")) return "https://www.facebook.com/marketplace/item/1262139982358466";
  if (path.includes("/facebook/event-details")) return "https://www.facebook.com/events/1017939276305684";
  if (path.includes("/facebook/")) return FB_POST;
  if (path.includes("/twitter/profile") || path.includes("/twitter/user")) return X_PROFILE;
  if (path.includes("/twitter/")) return X_POST;
  if (path.includes("/reddit/subreddit")) return "https://www.reddit.com/r/programming/";
  if (path.includes("/reddit/post")) return REDDIT_POST;
  if (path.includes("/threads/user") || path.includes("/threads/profile")) return THREADS_PROFILE;
  if (path.includes("/threads/post")) return THREADS_POST;
  if (path.includes("/bluesky/post")) return BLUESKY_POST;
  if (path.includes("/bluesky/")) return BLUESKY_PROFILE;
  if (path.includes("/pinterest/pin")) return PINTEREST_PIN;
  if (path.includes("/pinterest/board")) return "https://www.pinterest.com/nasa/nasa/";
  if (path.includes("/pinterest/")) return PINTEREST_PROFILE;
  if (path.includes("/linkedin/company")) return LINKEDIN_COMPANY;
  if (path.includes("/linkedin/post")) return LINKEDIN_POST;
  if (path.includes("/linkedin/")) return LINKEDIN_PROFILE;
  if (path.includes("/rumble/channel")) return RUMBLE_CHANNEL;
  if (path.includes("/rumble/")) return RUMBLE_VIDEO;
  if (path.includes("/twitch/clip")) return TWITCH_CLIP;
  if (path.includes("/twitch/")) return TWITCH_PROFILE;
  if (path.includes("/spotify/artist")) return SPOTIFY_ARTIST;
  if (path.includes("/spotify/track")) return SPOTIFY_TRACK;
  if (path.includes("/spotify/album")) return SPOTIFY_ALBUM;
  if (path.includes("/spotify/podcast")) return SPOTIFY_PODCAST;
  if (path.includes("/soundcloud/track")) return SOUNDCLOUD_TRACK;
  if (path.includes("/soundcloud/")) return SOUNDCLOUD_ARTIST;
  if (path.includes("/linktree/")) return LINKTREE_PROFILE;
  if (path.includes("/snapchat/")) return SNAPCHAT_PROFILE;
  if (path.includes("/truth-social/post")) return "https://truthsocial.com/@realDonaldTrump/posts/114743513808881146";
  if (path.includes("/truth-social/")) return TRUTH_PROFILE;
  if (path.includes("/kick/")) return KICK_CLIP;
  if (path.includes("/amazon-shop/")) return AMAZON_SHOP;
  if (path.includes("/kwai/post")) return KWAI_POST;
  if (path.includes("/kwai/")) return KWAI_PROFILE;
  if (path.includes("/komi/")) return KOMI_PAGE;
  if (path.includes("/pillar/")) return PILLAR_PAGE;
  if (path.includes("/linkbio/")) return LINKBIO_PAGE;
  if (path.includes("/linkme/")) return LINKME_PROFILE;
  if (path.includes("/ad-library/facebook/ad-transcript") || path.includes("/ad-library/facebook/ad-details")) return "1525108188069665";
  if (path.includes("/ad-library/tiktok/ad-details")) return "1839430445786152";
  if (path.includes("/ad-library/linkedin/ad-details")) return "urn:li:sponsoredCreative:123456789";
  return YT_VIDEO;
}

async function buildParams(endpoint: { path: string; params: { name: string; required: boolean; type?: string }[] }) {
  const params: Record<string, string> = {};
  for (const p of endpoint.params) {
    if (p.name === "limit") params[p.name] = LIMIT;
    else if (p.name === "language") params[p.name] = "en";
    else if (p.name === "country") params[p.name] = "US";
    else if (p.name === "region") params[p.name] = "US";
    else if (p.name === "state") params[p.name] = "CA";
    else if (p.name === "sort") params[p.name] = "follower";
    else if (p.name === "follower_count") params[p.name] = "100k-1m";
    else if (p.name === "type") params[p.name] = "recent";
    else if (p.name === "marketplace") params[p.name] = "US";
    else if (p.name === "details") params[p.name] = "false";
    else if (p.name === "days") params[p.name] = "7";
    else if (p.name === "q") params[p.name] = endpoint.path.includes("marketplace-location") ? "Austin" : "coffee";
    else if (p.name === "query") params[p.name] = "coffee";
    else if (p.name === "name") params[p.name] = "Michael";
    else if (p.name === "names") params[p.name] = "Michael,Sarah";
    else if (p.name === "username") params[p.name] = endpoint.path.includes("github") ? "torvalds" : "khaby.lame";
    else if (p.name === "repo") params[p.name] = "vercel/next.js";
    else if (p.name === "audio_id") params[p.name] = IG_AUDIO_ID;
    else if (p.name === "location") params[p.name] = "Austin";
    else if (p.name === "advertiser") params[p.name] = "nike";
    else if (p.name === "creative_id") params[p.name] = endpoint.path.includes("/google/") ? "CR10435207215413411841" : "1525108188069665";
    else if (p.name === "comment_id") params[p.name] = "seed-comment-id";
    else if (p.name === "url") params[p.name] = sampleUrl(endpoint.path);
  }
  return params;
}

async function buildMcpArgs(endpoint: { path: string; params: { name: string; required: boolean; type?: string }[] }) {
  const params = await buildParams(endpoint);
  return Object.fromEntries(
    Object.entries(params).map(([key, value]) => {
      const param = endpoint.params.find((item) => item.name === key);
      if (param?.type === "number" || param?.type === "integer") return [key, Number(value)];
      if (param?.type === "boolean") return [key, value === "true"];
      return [key, value];
    }),
  );
}

function endpointParams(endpoint: (typeof ALL_ENDPOINTS)[number]) {
  return frontendParams(endpoint).map((param) => ({
    name: param.name,
    required: param.required,
    type: param.type,
  }));
}

async function getJson(url: string) {
  const res = await fetch(url);
  const text = await res.text();
  try {
    return { res, text, json: JSON.parse(text) };
  } catch {
    return { res, text, json: null };
  }
}

async function docsAudit() {
  const catalogPaths = new Set(ALL_ENDPOINTS.map((e) => normalizePath(e.path)));
  const frontendByPath = new Map(ALL_ENDPOINTS.map((e) => [normalizePath(e.path), e]));
  const mcpByPath = new Map(MCP_ENDPOINTS.map((e) => [normalizePath(e.path), e]));
  const liveOpenApi = await getJson(`${BASE_URL}/v1/openapi.json`);
  const livePaths = liveOpenApi.json?.paths ? Object.keys(liveOpenApi.json.paths).map(normalizePath) : [];
  const livePathSet = new Set(livePaths);

  const docs = await getJson(`${WEB_URL}/docs`);
  const apis = await getJson(`${WEB_URL}/apis`);
  const mcpManifest = await getJson(`${WEB_URL}/mcp.json`);

  const docsPaths = new Set((docs.text.match(/\/v1\/[a-z0-9/_-]+/g) || []).map(normalizePath));
  const apisPaths = new Set((apis.text.match(/\/v1\/[a-z0-9/_-]+/g) || []).map(normalizePath));
  const docsMissing = [...catalogPaths].filter((p) => !docsPaths.has(p));
  const apisMissing = [...catalogPaths].filter((p) => !apisPaths.has(p));
  const notInOpenApi = [...catalogPaths].filter((p) => !livePathSet.has(p));
  const inOpenApiNotCatalog = [...livePathSet].filter((p) => p.startsWith("/v1/") && !catalogPaths.has(p));

  const perPageRows: Row[] = [];
  if (!SKIP_PAGES) {
    const queue = [...ALL_ENDPOINTS];
    const workers = Array.from({ length: 8 }, async () => {
      while (queue.length) {
        const e = queue.shift()!;
        const t0 = Date.now();
        try {
          const page = await fetch(`${WEB_URL}/apis/${e.slug}`);
          const text = await page.text();
          const missingRequired = endpointParams(e)
            .filter((p) => p.required)
            .map((p) => p.name)
            .filter((p) => !text.includes(p));
          const status =
            page.ok && text.includes(e.path) && missingRequired.length === 0
              ? "OK"
              : page.ok
                ? "CONTENT_MISMATCH"
                : "PAGE_FAIL";
          perPageRows.push({
            slug: e.slug,
            platform: e.platform,
            path: e.path,
            status,
            http: page.status,
            ms: Date.now() - t0,
            note: missingRequired.length ? `missing required params: ${missingRequired.join(",")}` : undefined,
          });
        } catch (err) {
          perPageRows.push({
            slug: e.slug,
            platform: e.platform,
            path: e.path,
            status: "FETCH_ERROR",
            ms: Date.now() - t0,
            note: String(err).slice(0, 140),
          });
        }
      }
    });
    await Promise.all(workers);
  }

  const paramDiffs = [...catalogPaths]
    .map((path) => {
      const frontend = frontendByPath.get(path);
      const mcp = mcpByPath.get(path);
      const liveGet = liveOpenApi.json?.paths?.[path]?.get;
      const liveRequired = new Set(
        (liveGet?.parameters || [])
          .filter((p: { in?: string; required?: boolean }) => p.in === "query" && p.required)
          .map((p: { name: string }) => p.name),
      );
      const frontendRequired = new Set(frontend ? endpointParams(frontend).filter((p) => p.required).map((p) => p.name) : []);
      const mcpRequired = new Set((mcp?.params || []).filter((p) => p.required).map((p) => p.name));
      const missFrontend = [...liveRequired].filter((p) => !frontendRequired.has(p));
      const missMcp = [...liveRequired].filter((p) => !mcpRequired.has(p));
      if (!missFrontend.length && !missMcp.length) return null;
      return { path, missFrontend, missMcp };
    })
    .filter(Boolean);

  return {
    counts: {
      frontend: ALL_ENDPOINTS.length,
      mcp: MCP_ENDPOINTS.length,
      liveOpenApiPaths: livePaths.length,
      docsPathRefs: docsPaths.size,
      apisPathRefs: apisPaths.size,
      mcpManifestToolCount: mcpManifest.json?.tools?.count,
      mcpManifestPlatformCount: mcpManifest.json?.tools?.platform_count,
    },
    docsMissing,
    apisMissing,
    notInOpenApi,
    inOpenApiNotCatalog,
    paramDiffs,
    perPageRows,
  };
}

async function callApi(
  endpoint: (typeof ALL_ENDPOINTS)[number],
  params: Record<string, string>,
  attempt = 0,
): Promise<{ res: Response; text: string; ms: number }> {
  const url = new URL(`${BASE_URL}${endpoint.path}`);
  for (const [key, value] of Object.entries(params)) url.searchParams.set(key, value);
  await acquireAuditSlot();
  const t0 = Date.now();
  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      Accept: "application/json",
      "User-Agent": "captapi-live-audit/1.0",
    },
    signal: AbortSignal.timeout(LIVE_REQUEST_TIMEOUT_MS),
  });
  const text = await res.text();
  const ms = Date.now() - t0;
  if (res.status === 429 && attempt < LIVE_429_RETRIES) {
    const retryAfter = Number(res.headers.get("retry-after") || 60);
    await sleep(Math.max(1, retryAfter) * 1000);
    const retry = await callApi(endpoint, params, attempt + 1);
    return { ...retry, ms: retry.ms };
  }
  return { res, text, ms };
}

async function liveAudit() {
  if (!API_KEY) throw new Error("CAPTAPI_API_KEY is required for --live");
  const rows: Row[] = [];
  const byPath = new Map(ALL_ENDPOINTS.map((e) => [e.path, e]));
  const comments: Record<string, string> = {};
  if (existsSync(LIVE_PROGRESS_FILE)) unlinkSync(LIVE_PROGRESS_FILE);

  function record(row: Row) {
    rows.push(row);
    appendFileSync(LIVE_PROGRESS_FILE, `${JSON.stringify(row)}\n`);
    const marker =
      row.status === "OK" ? "ok" : row.status === "OK_SLOW" ? "slow" : "warn";
    console.log(
      `[${marker}] ${row.slug} ${row.status} ${row.http ?? "-"} ${row.ms ?? "-"}ms`,
    );
  }

  for (const seedPath of ["/v1/youtube/comments", "/v1/tiktok/comments", "/v1/facebook/comments"]) {
    const endpoint = byPath.get(seedPath);
    if (!endpoint) continue;
    try {
      const seedParams = await buildParams({ path: endpoint.path, params: endpointParams(endpoint) });
      seedParams.limit = "5";
      const seed = await callApi(endpoint, seedParams);
      const parsed = JSON.parse(seed.text);
      const id = findFirstId(parsed);
      if (id) comments[seedPath.split("/")[2]] = id;
    } catch {
      // The reply endpoints will be classified with the fallback comment id.
    }
  }

  const queue = ALL_ENDPOINTS.filter((endpoint) => !ONLY_SLUGS.size || ONLY_SLUGS.has(endpoint.slug));
  const workers = Array.from({ length: LIVE_CONCURRENCY }, async () => {
    while (queue.length) {
      const endpoint = queue.shift()!;
      const params = await buildParams({ path: endpoint.path, params: endpointParams(endpoint) });
      if (endpoint.path.includes("comment-replies")) {
        const platform = endpoint.path.split("/")[2];
        if (comments[platform]) params.comment_id = comments[platform];
      }
      const t0 = Date.now();
      try {
        const { res, text, ms } = await callApi(endpoint, params);
        let note = ms > LIVE_SLOW_THRESHOLD_MS ? `slow>${LIVE_SLOW_THRESHOLD_MS}ms` : "";
        if (!res.ok) {
          try {
            const parsed = JSON.parse(text);
            note = JSON.stringify(parsed.detail ?? parsed.error ?? parsed).slice(0, 220);
          } catch {
            note = text.slice(0, 220);
          }
        }
        const baseStatus = statusOf(res, text);
        record({
          slug: endpoint.slug,
          platform: endpoint.platform,
          path: endpoint.path,
          status: res.ok && ms > LIVE_SLOW_THRESHOLD_MS ? "OK_SLOW" : baseStatus,
          http: res.status,
          ms,
          note,
        });
      } catch (err) {
        const isTimeout =
          err instanceof Error &&
          (err.name === "TimeoutError" || err.name === "AbortError");
        record({
          slug: endpoint.slug,
          platform: endpoint.platform,
          path: endpoint.path,
          status: isTimeout ? "TIMEOUT" : "FETCH_ERROR",
          ms: Date.now() - t0,
          note: String(err).slice(0, 220),
        });
      }
    }
  });
  await Promise.all(workers);

  return rows;
}

async function mcpAudit() {
  const packageDir = join(process.cwd(), "packages", "captapi-mcp");
  const [{ Client }, { StdioClientTransport }] = await Promise.all([
    import("../packages/captapi-mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js"),
    import("../packages/captapi-mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js"),
  ]);

  await new Promise<void>((resolve, reject) => {
    const child = spawn(/^win/.test(process.platform) ? "npm.cmd" : "npm", ["run", "build"], {
      cwd: packageDir,
      stdio: "pipe",
      shell: /^win/.test(process.platform),
    });
    let stderr = "";
    child.stderr.on("data", (chunk) => (stderr += String(chunk)));
    child.on("close", (code) => (code === 0 ? resolve() : reject(new Error(stderr || `build exited ${code}`))));
  });

  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [join(packageDir, "dist", "index.js")],
    env: Object.fromEntries(
      Object.entries({
        ...process.env,
        CAPTAPI_API_KEY: API_KEY || "",
        CAPTAPI_BASE_URL: BASE_URL,
      }).filter(([key, value]) => key && !key.startsWith("=") && typeof value === "string"),
    ) as Record<string, string>,
  });
  const client = new Client({ name: "captapi-live-audit", version: "1.0.0" });
  await client.connect(transport);
  const listed = await client.listTools();
  const toolNames = new Set(listed.tools.map((tool) => tool.name));
  const missingTools = MCP_ENDPOINTS.map((e) => e.tool).filter((tool) => !toolNames.has(tool));
  const extraTools = listed.tools.map((tool) => tool.name).filter((tool) => !MCP_ENDPOINTS.some((e) => e.tool === tool));
  const schemaMismatches = MCP_ENDPOINTS.flatMap((endpoint) => {
    const tool = listed.tools.find((item) => item.name === endpoint.tool);
    const props = tool?.inputSchema?.properties || {};
    return endpoint.params
      .filter((param) => !(param.name in props))
      .map((param) => ({ tool: endpoint.tool, missingParam: param.name }));
  });

  const callTools = [
    "github_user",
    "github_repository",
    "tiktok_shop_shop_search",
    "google_ad_library_company_ads",
    "facebook_marketplace_location_search",
    "age_gender_get",
    "linktree_page",
    "kwai_profile",
    "youtube_video_details",
    "instagram_basic_profile",
  ];
  const calls = [];
  for (const toolName of callTools) {
    const endpoint = MCP_ENDPOINTS.find((item) => item.tool === toolName);
    if (!endpoint) continue;
    const t0 = Date.now();
    try {
      const result = await client.callTool({
        name: toolName,
        arguments: await buildMcpArgs(endpoint),
      });
      const text = result.content?.[0]?.type === "text" ? result.content[0].text : JSON.stringify(result);
      calls.push({
        tool: toolName,
        path: endpoint.path,
        status: result.isError ? "MCP_CALL_ERROR" : "OK",
        ms: Date.now() - t0,
        note: result.isError ? text.slice(0, 220) : undefined,
      });
    } catch (err) {
      calls.push({
        tool: toolName,
        path: endpoint.path,
        status: "MCP_EXCEPTION",
        ms: Date.now() - t0,
        note: String(err).slice(0, 220),
      });
    }
  }
  await client.close();
  return {
    listedTools: listed.tools.length,
    catalogTools: MCP_ENDPOINTS.length,
    missingTools,
    extraTools,
    schemaMismatches,
    calls,
  };
}

function tally(rows: Row[]) {
  return rows.reduce<Record<string, number>>((acc, row) => {
    acc[row.status] = (acc[row.status] || 0) + 1;
    return acc;
  }, {});
}

async function main() {
  const docs = await docsAudit();
  const liveRows = LIVE ? await liveAudit() : [];
  const mcp = MCP ? await mcpAudit() : null;
  const report = {
    generatedAt: new Date().toISOString(),
    baseUrl: BASE_URL,
    webUrl: WEB_URL,
    docs,
    live: {
      enabled: LIVE,
      tally: tally(liveRows),
      rows: liveRows,
    },
    mcp,
  };
  const out = join(process.cwd(), "comprehensive-live-audit-report.json");
  writeFileSync(out, JSON.stringify(report, null, 2));
  console.log(JSON.stringify({
    report: out,
    docsCounts: docs.counts,
    docsMissing: docs.docsMissing.length,
    apisMissing: docs.apisMissing.length,
    perPage: tally(docs.perPageRows),
    live: tally(liveRows),
    mcp: mcp
      ? {
          listedTools: mcp.listedTools,
          catalogTools: mcp.catalogTools,
          missingTools: mcp.missingTools.length,
          schemaMismatches: mcp.schemaMismatches.length,
          calls: tally(mcp.calls as Row[]),
        }
      : null,
  }, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
