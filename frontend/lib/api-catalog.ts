// Central catalog of every Captapi endpoint.
// Drives the landing "One API. Every platform." section, the /apis index,
// and the programmatic SEO (pSEO) detail pages at /apis/[slug].
//
// Content (taglines, descriptions, params, FAQs, example responses) is generated
// from a small declarative spec so every endpoint gets a unique, answer-first
// page that is SEO / GEO / AEO friendly without hand-writing 34 pages.
//
// Example responses prefer real snapshots captured live from the production API
// (see api-examples.generated.ts); a generic per-category shape is used as a
// fallback for any endpoint without a snapshot.

import { API_EXAMPLES } from "./api-examples.generated";
import { API_EXAMPLE_VARIANTS } from "./api-example-variants";

export type PlatformId =
  | "youtube"
  | "tiktok"
  | "instagram"
  | "facebook"
  | "twitter"
  | "reddit"
  | "threads"
  | "bluesky"
  | "pinterest"
  | "linkedin"
  | "rumble"
  | "tiktok_shop"
  | "facebook_marketplace"
  | "facebook_events"
  | "facebook_ad_library"
  | "tiktok_ad_library"
  | "google_ad_library"
  | "linkedin_ad_library"
  | "github"
  | "twitch"
  | "spotify"
  | "soundcloud"
  | "linktree"
  | "snapchat"
  | "truth_social"
  | "kick"
  | "amazon_shop"
  | "account"
  | "utilities"
  | "kwai"
  | "komi"
  | "pillar"
  | "linkbio"
  | "linkme";

export type Category =
  | "transcript"
  | "summarize"
  | "details"
  | "comments"
  | "channel"
  | "search"
  | "list";

export interface ApiParam {
  name: string;
  type: string;
  required: boolean;
  description: string;
}

export interface FaqItem {
  q: string;
  a: string;
}

export interface ResponseField {
  name: string;
  desc: string;
}

export interface ResponseGroup {
  title: string;
  note?: string;
  fields: ResponseField[];
}

export interface UseCase {
  title: string;
  desc: string;
}

export interface ApiEndpoint {
  slug: string;
  platform: PlatformId;
  /** Full marketing name, e.g. "YouTube Transcript API" */
  name: string;
  /** Short label used inside grouped cards, e.g. "Transcript" */
  shortName: string;
  category: Category;
  method: "GET" | "POST";
  path: string;
  /**
   * Typical credit cost of a standard request. For list/search/comments
   * endpoints this is the cost at the default result count (a fixed average so
   * users know roughly what a call consumes); actual billing scales with the
   * number of results returned at `creditsPerResult`.
   */
  credits: number;
  /** Credits billed per result for list/search/comments endpoints. */
  creditsPerResult?: number;
  /** Optional override for the "what you get" bullet list. */
  delivers?: string[];
  /** Optional override for the generated category tagline. */
  tagline?: string;
  /** Optional override for the generated "What is the X?" paragraph. */
  longDescription?: string;
  /**
   * Honest platform-surface ceilings (not Captapi bugs). Shown as a dedicated
   * "Platform limits" block when set — omit when there is nothing worth warning.
   */
  platformLimits?: string[];
}

export interface PlatformGroup {
  id: PlatformId;
  name: string;
  blurb: string;
  /** lucide-react icon name (resolved in components) */
  icon:
    | "youtube"
    | "music"
    | "tiktok"
    | "instagram"
    | "facebook"
    | "twitter"
    | "reddit"
    | "threads"
    | "bluesky"
    | "pinterest"
    | "linkedin"
    | "rumble"
    | "shoppingBag"
    | "github"
    | "megaphone"
    | "calendar"
    | "google"
    | "amazon"
    | "video"
    | "cloud"
    | "search"
    | "link"
    | "ghost"
    | "captapi";
  /** brand color class for the icon */
  color: string;
  exampleUrl: string;
  endpoints: ApiEndpoint[];
}

export const SITE_URL =
  process.env.NEXT_PUBLIC_APP_URL?.replace(/\/$/, "") || "https://captapi.com";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
  "https://api.captapi.com";

/**
 * Human-friendly credit cost label for an endpoint. `credits` already holds the
 * typical cost of a standard request (for list endpoints, the cost at the
 * default result count), so we display a single fixed number everywhere.
 */
export function creditLabel(
  e: Pick<ApiEndpoint, "credits" | "creditsPerResult" | "slug">,
): string {
  if (e.slug === "analytics-compare") return "1 credit/url";
  if (e.slug === "video-transcript") return "1 credit/min";
  if (e.slug === "video-summarize") return "1 credit/min +1";
  if (e.slug === "youtube-audio-transcript") return "2 credits/min of audio";
  // Published-flat endpoints (measurement window): one number, always.
  // Dual native/extended labels are retired — meter matches the badge.
  if (
    e.slug === "tiktok-shop-product-details" ||
    e.slug === "tiktok-shop-search" ||
    e.slug === "twitter-community-tweets" ||
    e.slug === "threads-user-posts" ||
    e.slug === "threads-search" ||
    e.slug === "threads-search-users" ||
    e.slug === "truth-social-user-posts" ||
    e.slug === "facebook-event-search" ||
    e.slug === "facebook-profile-events"
  ) {
    return `${e.credits} credit${e.credits === 1 ? "" : "s"}`;
  }
  if (e.creditsPerResult) {
    return `~${e.credits} credits (${e.creditsPerResult}/result)`;
  }
  return `${e.credits} credit${e.credits === 1 ? "" : "s"}`;
}

const PLATFORM_LABEL: Record<PlatformId, string> = {
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
  tiktok_shop: "TikTok Shop",
  facebook_marketplace: "Facebook Marketplace",
  facebook_events: "Facebook Events",
  facebook_ad_library: "Facebook Ad Library",
  tiktok_ad_library: "TikTok Ad Library",
  google_ad_library: "Google Ad Library",
  linkedin_ad_library: "LinkedIn Ad Library",
  github: "GitHub",
  twitch: "Twitch",
  spotify: "Spotify",
  soundcloud: "SoundCloud",
  linktree: "Linktree",
  snapchat: "Snapchat",
  truth_social: "Truth Social",
  kick: "Kick",
  amazon_shop: "Amazon Shop",
  account: "CaptAPI Account",
  utilities: "Utilities",
  kwai: "Kwai",
  komi: "Komi",
  pillar: "Pillar",
  linkbio: "Linkbio",
  linkme: "Linkme",
};

// ---------------------------------------------------------------------------
// Raw spec — kept terse; everything else is derived.
// ---------------------------------------------------------------------------

type Spec = Omit<ApiEndpoint, "platform">;

const YOUTUBE: Spec[] = [
  {
    slug: "youtube-transcript",
    name: "YouTube Transcript API",
    shortName: "Transcript",
    category: "transcript",
    method: "GET",
    path: "/v1/youtube/transcript",
    credits: 1,
    tagline:
      "YouTube's published captions with timestamps — not speech-to-text. Flat 1 credit; 404 is free.",
    longDescription:
      "Returns the captions YouTube publishes for a video — manual or auto-generated. It does not perform speech-to-text. Long live streams and VODs frequently have no auto-captions at all. When there is no caption track this endpoint returns 404 and costs 0 credits (strictly better than charging for a null body); use /v1/youtube/audio-transcript to transcribe the audio directly (priced per minute). The 404 body includes code (no_captions / language_not_available), reason, availableLanguages[], hasAutoCaptions, and — when the video is reachable with audio — a suggestion block with estimatedCredits for audio-transcript. Success responses use the same transcript vocabulary as audio-transcript / Rumble: text + segments[{text,startMs,endMs}], plus source: \"captions\", requestedLanguage, and returnedLanguage (no redundant language twin). Pass language to require that track; there is no silent fallback. Flat 1 credit on success.",
  },
  {
    slug: "youtube-audio-transcript",
    name: "YouTube Audio Transcript API",
    shortName: "Audio Transcript",
    category: "transcript",
    method: "GET",
    path: "/v1/youtube/audio-transcript",
    credits: 2,
    tagline:
      "Speech-to-text for YouTube audio. Use it when a video has no captions — or when you want a transcript of what was actually spoken rather than YouTube's published captions. Priced per started minute of audio.",
    longDescription:
      "Transcribes YouTube audio with Whisper-class ASR when the video has no published captions (or when you want speech-to-text regardless). Separate from /transcript — that endpoint only returns YouTube's caption tracks. Pricing is duration-based and honest: creditsUsed = ceil(durationSeconds / 60) × 2 (badge: 2 credits/min of audio). Pass maxCredits to refuse expensive jobs before any STT runs (400 cost_exceeds_max, 0 credits). Prefers Groq whisper-large-v3-turbo when GROQ_API_KEY is set (measured: ~20 min ≈ 12s e2e, ~82 min ≈ 49s); otherwise OpenAI whisper-1. Audio is re-encoded to 16 kHz mono 32 kbps before upload so podcast-length jobs stay under the ~25 MB ceiling. Sync path is capped at 90 minutes under Cloudflare's 110s hard deadline; longer videos return 400 duration_too_long with estimatedCredits before any STT spend. Response always includes source: \"asr\", asrProvider, languageIsDetected, numeric segments[{text,startMs,endMs}], text, durationSeconds, creditsUsed. Cache hits still bill — the cache is our margin.",
    delivers: [
      "source:asr discriminator (pair with /transcript source:captions)",
      "Per-minute pricing + maxCredits preflight",
      "Uniform segments[] with numeric startMs/endMs (verbose_json)",
      "Groq-first path; 90-minute sync cap from measured e2e",
    ],
    platformLimits: [
      "Sync transcription is capped at 90 minutes (Cloudflare ~110s hard deadline + ~25 MB upload). Longer videos — including multi-hour livestreams — return 400 duration_too_long with estimatedCredits (0 credits, no STT).",
      "Audio is speech-reencoded (16 kHz mono 32 kbps) before ASR; rare extract failures may still hit audio_too_large.",
      "Requires GROQ_API_KEY in production for the 90-minute band; without it the OpenAI fallback is far slower and should stay on a tighter operational cap.",
    ],
  },
  {
    slug: "youtube-summarizer",
    name: "YouTube Summarizer API",
    shortName: "Summarizer",
    category: "summarize",
    method: "GET",
    path: "/v1/youtube/summarize",
    credits: 3,
    tagline:
      "GPT summary from YouTube's published captions — same source as /transcript. Flat 3 credits; caption-miss 404 is free.",
    longDescription:
      "Fetches YouTube's published captions (same engine as /transcript — not speech-to-text) and returns a GPT summary, key points, topics, and sentiment. When the video has no caption tracks, you get the same diagnostic 404 as /transcript (code, reason, availableLanguages, hasAutoCaptions) and are charged 0 credits — never 3. Long live streams often lack auto-captions. Flat 3 credits only when a summary is returned.",
  },
  {
    slug: "youtube-video-details",
    name: "YouTube Video Details API",
    shortName: "Video Details",
    category: "details",
    method: "GET",
    path: "/v1/youtube/video-details",
    credits: 1,
    tagline:
      "YouTube video metadata + stats. Always includes degraded / degradedReason — retry when degraded is true.",
    longDescription:
      "Returns title, channel, duration, view/like/comment counts, publishedAt, genre/categoryId, captions list, and live flags. ANDROID InnerTube supplies engagement; publishDate / genre / @handle / isFamilySafe come from the watch-page microformat (retried once when missing). Responses always include degraded (boolean) and degradedReason (null or \"partial-extraction\") — same envelope as Instagram channel-posts — plus timings.path (android | watch | android+watch). Flat 1 credit.",
    delivers: [
      "degraded / degradedReason always present (retry on partial-extraction)",
      "publishedAt + likeCount from watch microformat / label when ANDROID omits them",
      "timings.path shows which fetch path filled the row",
    ],
  },
  {
    slug: "youtube-comments",
    name: "YouTube Comments API",
    shortName: "Comments",
    category: "comments",
    method: "GET",
    path: "/v1/youtube/comments",
    credits: 2,
    tagline:
      "Get comments on any YouTube video — text, author, likes, and truncated publishedTimeApprox from the relative label, with cursor pagination (nextCursor + hasMore). Flat 2 credits per call.",
    platformLimits: [
      "YouTube's public comment surface is soft-capped (~1,500 top / ~7,000 newest depending on sort). Cursor ends when YouTube stops — not a Captapi truncation.",
      "YouTube only exposes relative labels (e.g. \"7 days ago\"). publishedTimeApprox is derived and truncated to that label's precision; publishedTimeIsApproximate is always true for those rows.",
    ],
  },
  {
    slug: "youtube-channel-details",
    name: "YouTube Channel Details API",
    shortName: "Channel Details",
    category: "channel",
    method: "GET",
    path: "/v1/youtube/channel-details",
    credits: 1,
    tagline:
      "YouTube channel stats — ISO country/joinedAt, real banner, quote-aware SEO tags, absolute links. Flat 1 credit.",
    longDescription:
      "Pass a channel URL, @handle, or UC… id and get clean JSON. Canonical profile core (same keys on every Captapi profile endpoint): platform, id, username, url, displayName, bio, avatar, banner, followers, following, postCount, verified, createdAt. Identical-value aliases (handle/name/description/thumbnailUrl/bannerUrl/subscriberCount/videoCount/joinedAt/joinedDate) are not emitted. Also: canonicalUrl (@handle when known), subscriberCountIsApproximate, viewCount (exact when About exposes it), country (ISO-3166 alpha-2) + countryName, links[{text,url}] with absolute https URLs, email when published in About/description (not the CAPTCHA reveal), and tags[] from channel SEO keywords (quote-aware — multi-word tags stay one entry). banner is null when the channel has no banner — we never substitute the avatar. Flat 1 credit.",
    platformLimits: [
      "followers is YouTube's rounded shelf value; subscriberCountIsApproximate is true when the source used K/M/B compact form. viewCount is exact when the About panel exposes it. createdAt is ISO-8601 (YYYY-MM-DD) — no parallel display-formatted date.",
      "banner is null when the channel has no banner — we never substitute the avatar.",
      "email is only returned when the creator published it in description/About text or a mailto link — not from YouTube's CAPTCHA email reveal.",
    ],
  },
  {
    slug: "youtube-search",
    name: "YouTube Search API",
    shortName: "Search",
    category: "search",
    method: "GET",
    path: "/v1/youtube/search",
    credits: 2,
    tagline:
      "YouTube search with cursor pagination — typed hits, ids, canonical URLs, filters (2 credits/page).",
    longDescription:
      "Search YouTube by keyword and get a cursor-paginated page of clean JSON: results[] with type (video|short|channel|playlist|live), id, canonical url, title, publishedTimeApprox + publishedTimeIsApproximate + publishedTimeText, viewCount + viewCountText + viewCountIsApproximate, durationSeconds, thumbnailUrl, channel{id,title,handle,url,thumbnail}, badges[], and subscriberCount on channel hits. Typed arrays videos[] / shorts[] / channels[] / playlists[] / lives[] / shelves[] are disjoint partitions of results (a live is only in lives[], never also in videos[]) — Σ typed === results.length. Filter with type, sortBy, uploadDate, duration, region. Pass nextCursor as cursor for the next page. Flat 2 credits per page.",
    delivers: [
      "Disjoint typed arrays: videos / shorts / channels / playlists / lives",
      "cursor ↔ nextCursor round-trip (hasMore)",
      "subscriberCount on channel hits; publishedTimeIsApproximate null when no time",
      "viewCountIsApproximate false on exact rows; channel{} only",
    ],
  },
  {
    slug: "youtube-channel-videos",
    name: "YouTube Channel Videos API",
    shortName: "Channel Videos",
    category: "list",
    method: "GET",
    path: "/v1/youtube/channel-videos",
    credits: 2,
    tagline:
      "Channel uploads with cursor pagination — exact publishedAt from reel_item_watch (same as channel-shorts).",
    longDescription:
      "Send a channel URL, @handle, or UC… id and get uploads as clean JSON with nextCursor + hasMore. Pass nextCursor as cursor for page 2+. Each row shares the channel-shorts / playlist-videos shape: exact publishedAt from reel/reel_item_watch microformat (not publishedTimeApprox), publishedTimeText from the shelf label, viewCount + viewCountIsApproximate, durationSeconds + durationFormatted, genre, badges, thumbnailUrl, and nested channel{}. commentCount* appears only on Shorts rows (channel-shorts). Optional fast=true uses YouTube RSS (exact publishedAt, thinner metadata, no cursor). Flat 2 credits on the native path.",
    delivers: [
      "cursor ↔ nextCursor + hasMore (zero id overlap across pages)",
      "exact publishedAt via reel_item_watch (same source as channel-shorts)",
      "Shared row shape with channel-shorts / playlist-videos (genre, badges, durationFormatted)",
      "channel{} only — drop flat channel* twins",
    ],
  },
  {
    slug: "youtube-playlist-videos",
    name: "YouTube Playlist Videos API",
    shortName: "Playlist Videos",
    category: "list",
    method: "GET",
    path: "/v1/youtube/playlist-videos",
    credits: 2,
    tagline:
      "Paginated playlist contents — cursor/nextCursor/hasMore, same row shape as channel-videos. Flat 2 credits/page.",
    longDescription:
      "Paste a YouTube playlist URL and get one page of videos as clean JSON (same enriched row shape as channel-videos / channel-shorts): id, url, title, publishedAt (ISO from reel_item_watch), publishedTimeText, viewCount, durationSeconds/durationFormatted, genre, badges, thumbnailUrl, channel{}. Envelope: id, totalVideos, totalReturned, nextCursor, hasMore, timings. Pass nextCursor for the next page until hasMore is false. Optional fast=true uses YouTube RSS (no cursor). Flat 2 credits per page on the native path. For title/channel/thumbnail without videos, use Playlist (1 credit).",
    highlights: [
      "cursor ↔ nextCursor / hasMore (pages to totalVideos)",
      "Shared row shape with channel-videos",
      "timings{path,fetchMs,browseMs,enrichMs,totalMs}",
    ],
  },
  {
    slug: "youtube-playlist",
    name: "YouTube Playlist API",
    shortName: "Playlist",
    category: "list",
    method: "GET",
    path: "/v1/youtube/playlist",
    credits: 1,
    tagline:
      "Playlist metadata only — title, channel{}, totalVideos, thumbnailUrl. No videos[]. Flat 1 credit.",
    longDescription:
      "Paste a YouTube playlist URL and get identity JSON: platform, url, id, title, channel{id,title,handle,url}, totalVideos, thumbnailUrl, timings. No videos array — use Playlist Videos for paginated contents. Flat 1 credit (single HTML fetch, no player enrich).",
    highlights: [
      "Metadata only (no videos[]) — 1 credit",
      "channel{} (not owner / channelName twins)",
      "Pair with /playlist-videos for contents",
    ],
  },

  {
    slug: "youtube-shorts-transcript",
    name: "YouTube Shorts Transcript API",
    shortName: "Shorts Transcript",
    category: "transcript",
    method: "GET",
    path: "/v1/youtube/shorts/transcript",
    credits: 1,
    tagline: "Transcript for a YouTube Short — rejects long-form videos (≤3 min only).",
    longDescription:
      "Same caption engine as YouTube Transcript (published captions only — not speech-to-text), scoped to Shorts. Pass a youtube.com/shorts/… URL (or a watch URL that is actually a Short). Videos longer than 3 minutes return HTTP 422 — use /v1/youtube/transcript for those. Caption-miss 404 uses the same diagnostic body and charges 0. Flat 1 credit on success.",
  },
  {
    slug: "youtube-shorts-summarizer",
    name: "YouTube Shorts Summarizer API",
    shortName: "Shorts Summarizer",
    category: "summarize",
    method: "GET",
    path: "/v1/youtube/shorts/summarize",
    credits: 3,
    tagline: "AI summary of a YouTube Short — rejects long-form videos (≤3 min only).",
    longDescription:
      "Same summarizer as YouTube Summarizer (captions → GPT), scoped to Shorts (≤3 minutes). Longer videos return HTTP 422. Caption-miss 404 matches /transcript diagnostics and charges 0 — never 3. Flat 3 credits only when a summary is returned.",
  },
  {
    slug: "youtube-shorts-stats",
    name: "YouTube Shorts Stats API",
    shortName: "Shorts Stats",
    category: "details",
    method: "GET",
    path: "/v1/youtube/shorts/video-details",
    credits: 1,
    tagline: "YouTube Short metadata — same schema as Video Details, with isShort:true; long-form videos get HTTP 422.",
    longDescription:
      "Same field schema as YouTube Video Details (title, channel, duration, view/like/comment counts, tags, timings.path, …) but scoped to Shorts: response always includes platform, isShort:true, durationSeconds + durationFormatted, and a youtube.com/shorts/{id} URL. Uses reel_item_watch for publishDate / description / @handle (ANDROID player often omits Shorts microformat). Thumbnails prefer vertical / channel covers over landscape frame-2 stills. commentCountIsApproximate is true when YouTube only exposes a compact total (e.g. 11K→11000). defaultLanguage / defaultAudioLanguage are present (null when YouTube omits them). genre / categoryId / isFamilySafe are omitted when unavailable. Videos longer than 3 minutes — even if pasted as /shorts/{id} — return HTTP 422; use Video Details for those. Flat 1 credit.",
    delivers: [
      "Same schema as Video Details + isShort: true + platform",
      "publishedAt / description / channelHandle from reel_item_watch",
      "durationSeconds + durationFormatted; commentCountIsApproximate",
      "Canonical shorts URL; HTTP 422 for long-form (>3 min)",
      "Flat 1 credit",
    ],
    platformLimits: [
      "commentCount is usually YouTube's rounded header value (11K) — see commentCountIsApproximate.",
      "genre / categoryId / isFamilySafe / defaultLanguage / defaultAudioLanguage are omitted when Shorts microformat lacks them.",
      "When the player only ships landscape frame-2 stills, thumbnailUrl falls back to oardefault / maxresdefault.",
    ],
  },
  {
    slug: "youtube-shorts-comments",
    name: "YouTube Shorts Comments API",
    shortName: "Shorts Comments",
    category: "comments",
    method: "GET",
    path: "/v1/youtube/shorts/comments",
    credits: 2,
    tagline: "Comments on a YouTube Short — rejects long-form videos (≤3 min only).",
    longDescription: "Same comments engine as YouTube Comments, scoped to Shorts. Long-form videos return HTTP 422. Flat 2 credits with cursor pagination.",
  },
  {
    slug: "youtube-channel-shorts",
    name: "YouTube Channel Shorts API",
    shortName: "Channel Shorts",
    category: "list",
    method: "GET",
    path: "/v1/youtube/channel-shorts",
    credits: 2,
    tagline:
      "Channel Shorts with cursor pagination — same row shape as channel-videos (exact publishedAt).",
    longDescription:
      "Lists a channel's Shorts tab with nextCursor + hasMore (same cursor as channel-videos). Each row is player-enriched via reel_item_watch + ANDROID: exact publishedAt, publishedTimeText when the shelf exposes a relative label, viewCount + viewCountIsApproximate, durationSeconds/durationFormatted, genre, badges, commentCount trio, thumbnailUrl (prefers cover over frame-2 stills), and nested channel{}. Flat 2 credits on the native path. Not an alias of Video Details.",
    delivers: [
      "cursor ↔ nextCursor + hasMore (zero id overlap across pages)",
      "exact publishedAt from reel_item_watch microformat",
      "Shared row shape with channel-videos",
    ],
  },
  {
    slug: "youtube-trending-shorts",
    name: "YouTube Trending Shorts API",
    shortName: "Trending Shorts",
    category: "list",
    method: "GET",
    path: "/v1/youtube/trending-shorts",
    credits: 2,
    tagline: "YouTube Shorts recommendation sequence — not a global trending chart or keyword search.",
    longDescription:
      "Served from YouTube's reel_watch_sequence (Shorts recommendation feed — same surface ScrapeCreators uses for /v1/youtube/shorts/trending). This is not a global trending ranking: results are session-dependent, may include older or re-uploaded Shorts, and can vary between calls. Response source is always reel_watch_sequence on the native path. Each row is player-enriched with nested channel{id,url,title,handle} (https + percent-decoded @handle), exact viewCount + viewCountText + viewCountIsApproximate, durationSeconds + durationFormatted, publishedAt/genre when microformat exposes them, and commentCount with commentCountIsApproximate. Flat aliases (channelId/channelUrl/viewCountInt/…) and empty badges/channel.thumbnail are omitted. Optional q seeds the sequence from a topic Short only — values like trending/shorts are ignored (not echoed as query). Flat 2 credits.",
    delivers: [
      "reel_watch_sequence feed — not a keyword search for \"trending\"",
      "Nested channel{} with https + decoded @handle",
      "Exact views + commentCountIsApproximate; no dead empty fields",
      "Flat 2 credits",
    ],
    platformLimits: [
      "Not a global trending chart — recommendation sequence varies between calls.",
      "Older Shorts and re-uploads can appear; filter by publishedAt client-side if you need freshness.",
      "No cursor — each call returns a fresh batch up to limit.",
    ],
  },
  {
    slug: "youtube-channel-streams",
    name: "YouTube Channel Streams API",
    shortName: "Channel Streams",
    category: "list",
    method: "GET",
    path: "/v1/youtube/channel-streams",
    credits: 2,
    tagline: "Channel Live tab only — past streams + upcoming; empty when the channel has no Live tab.",
    longDescription:
      "Reads YouTube's Live tab (not Videos). Channels without a Live tab (common for non-streamers) return totalReturned:0 and hasLiveTab:false instead of silently echoing Videos. Each row is player-enriched with exact viewCount, ISO publishedAt + publishedTimeText, thumbnailUrl, and type stream|upcoming|video. Flat 2 credits on the native path (was incorrectly ~1/result at 20).",
    delivers: [
      "Live tab only — never Videos fallthrough",
      "hasLiveTab false when the channel has no Live tab",
      "Exact viewCount + ISO publishedAt via player enrich",
      "Flat 2 credits native",
    ],
  },
  {
    slug: "youtube-hashtag-search",
    name: "YouTube Hashtag Search API",
    shortName: "Hashtag Search",
    category: "search",
    method: "GET",
    path: "/v1/youtube/hashtag-search",
    credits: 20,
    creditsPerResult: 1,
    tagline:
      "Videos from youtube.com/hashtag/{name} — type (video|short|live), id, channelId. Not keyword search.",
    longDescription:
      "Pass a hashtag (with or without #) and get the videos listed on YouTube's hashtag page as clean JSON. This is the /hashtag/{name} feed — not a search?q= keyword query. Titles often omit the #tag (it may live only in the description); association is the hashtag page itself. Each result includes type (video|short|live), id, url, title, publishedAt, viewCount, durationSeconds, channelName, and channelId when YouTube exposes them. Billed per result (~1 credit each).",
    delivers: [
      "Hashtag page feed (not keyword search)",
      "type: video | short | live on every row",
      "id + channelId when available",
      "ISO publishedAt + numeric viewCount",
    ],
  },
  { slug: "youtube-comment-replies", name: "YouTube Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/youtube/comment-replies", credits: 2 },
  {
    slug: "youtube-channel-playlists",
    name: "YouTube Channel Playlists API",
    shortName: "Channel Playlists",
    category: "list",
    method: "GET",
    path: "/v1/youtube/channel-playlists",
    credits: 2,
    tagline:
      "Channel playlists with cursor pagination — id, title, totalVideos, thumbnailUrl. Flat 2 credits/page.",
    longDescription:
      "Pass a channel URL, @handle, or UC… ID and get that channel's /playlists tab as clean JSON with nextCursor + hasMore. Each row: id (playlist list= ID — chain into /v1/youtube/playlist), url, title, totalVideos (same name as /playlist), thumbnailUrl. Flat 2 credits per page.",
    delivers: [
      "cursor ↔ nextCursor / hasMore",
      "Playlist id for chaining into /youtube/playlist",
      "totalVideos (aligned with /playlist), thumbnailUrl",
    ],
  },
  {
    slug: "youtube-community-posts",
    name: "YouTube Community Posts API",
    shortName: "Community Posts",
    category: "list",
    method: "GET",
    path: "/v1/youtube/community-posts",
    credits: 1,
    tagline:
      "Community posts — channel{}, publishedTimeApprox, likeCountIsApproximate, linkedVideos[], cursor (1 credit).",
    longDescription:
      "Pass a channel URL, @handle, or UC… ID and get that channel's community /posts tab as clean JSON. Each post: id/url, channel{id,title,url,handle} (no flat author twin), text, likeCount + likeCountText + likeCountIsApproximate, publishedTimeApprox + publishedTimeIsApproximate + publishedTimeText (relative labels only — no exact instant source), postType (text|image|poll|video|playlist|quiz), pollOptions[] + totalVotes + totalVotesIsApproximate when poll, images[], hashtags[], linkedVideos[] when the post attaches a video. Cursor pagination via nextCursor + hasMore. Flat 1 credit on the native path; Apify fallback bills about 0.5 credits per returned post (min 2).",
    delivers: [
      "channel{} only — drop author string twin",
      "publishedTimeApprox + publishedTimeIsApproximate (comments vocabulary)",
      "likeCountIsApproximate / totalVotesIsApproximate naming",
      "linkedVideos[] when attached; cursor pagination; 1 credit native",
    ],
  },
  {
    slug: "youtube-community-post-details",
    name: "YouTube Community Post Details API",
    shortName: "Community Post Details",
    category: "details",
    method: "GET",
    path: "/v1/youtube/community-post-details",
    credits: 1,
    tagline:
      "One community post — same schema as the list endpoint plus comments (channel{}, publishedTimeApprox, pollOptions).",
    longDescription:
      "Paste a YouTube community post URL and get the same clean shape as Community Posts list items: text, images[], postType, pollOptions + totalVotes + totalVotesIsApproximate when poll, likeCount + likeCountText + likeCountIsApproximate, publishedTimeApprox + publishedTimeIsApproximate + publishedTimeText, channel{}, linkedVideos[] when present, and comments. Flat 1 credit.",
    delivers: [
      "Same fields as community-posts list items + comments",
      "pollOptions[] + totalVotes for polls",
      "channel{}; publishedTimeApprox vocabulary",
    ],
  },
  {
    slug: "youtube-video-sponsors",
    name: "YouTube Video Sponsors API",
    shortName: "Video Sponsors",
    category: "details",
    method: "GET",
    path: "/v1/youtube/video-sponsors",
    credits: 1,
    tagline:
      "SponsorBlock segments — sorted by time, overlapsWith flagged, minVotes filter, coverageSeconds for density.",
    longDescription:
      "Paste a YouTube video URL (response videoId/url always match the request). Returns community-sourced SponsorBlock skip segments: category (sponsor|selfpromo|interaction|intro|outro|preview|music_offtopic|poi_highlight|filler), actionType, start/end seconds + formatted times, votes, uuid. Segments are sorted by startSeconds; overlapping rows include overlapsWith:[uuid…]; coverageSeconds is the union duration (no double-count for brand-density). Default minVotes=0 drops rejected segments (votes < 0). Optional categories= comma list. Flat 1 credit. Data comes from SponsorBlock — not YouTube official.",
    delivers: [
      "Sorted segments + overlapsWith for nested skips",
      "coverageSeconds union length for density math",
      "minVotes filter (default 0 excludes votes < 0)",
      "videoId/url echo the requested video",
    ],
  },
];

const TIKTOK: Spec[] = [
  {
    slug: "tiktok-transcript",
    name: "TikTok Transcript API",
    shortName: "Transcript",
    category: "transcript",
    method: "GET",
    path: "/v1/tiktok/transcript",
    credits: 2,
    platformLimits: [
      "Some TikTok caption surfaces only expose about the first ~2 minutes of speech. Longer clips may return a partial transcript when TikTok truncates captions upstream.",
    ],
  },
  { slug: "tiktok-summarizer", name: "TikTok Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/tiktok/summarize", credits: 4 },
  { slug: "tiktok-video-details", name: "TikTok Video Details API", shortName: "Video Details", category: "details", method: "GET", path: "/v1/tiktok/video-details", credits: 1, tagline: "Get everything about one TikTok video from its URL — caption, view/like/comment/share/save counts, creator, sound, hashtags, and thumbnail.", longDescription: "Paste any public TikTok video URL and the TikTok Video Details API returns the full picture as clean JSON: the caption, when it was posted, how long it runs, and its engagement — views, likes, comments, shares, and saves. You also get the creator (username, display name, follower count, verified badge, and avatar), the sound/music name, the list of hashtags, and a thumbnail image. Use it to build analytics dashboards, track a campaign, or enrich a content database. This endpoint focuses on metadata and stats. No TikTok login and no proxies or infrastructure to maintain on your side. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Caption, publish date, and video duration", "Views, likes, comments, shares, and saves", "Creator profile — handle, name, followers, verified, avatar", "Sound name, hashtags, and thumbnail image"] },
  { slug: "tiktok-comments", name: "TikTok Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/tiktok/comments", credits: 2, tagline: "TikTok comments — clean schema plus stable authorId/authorSecUid and commentLanguage for listening loops.", longDescription: "Paste a public TikTok video URL and get comments as clean JSON (not TikTok's 40+ junk user fields). Each comment keeps username + avatar, and adds stable authorId (uid) and authorSecUid for repeat-commenter detection, plus commentLanguage for market listening without a separate language detector. replyCount when TikTok exposes it. totalComments + cursor pagination (nextCursor/hasMore). Flat 2 credits per call. Need replies? Use TikTok Comment Replies with the parent comment id.", delivers: ["Stable authorId + authorSecUid (not just username)", "commentLanguage for market listening", "replyCount when TikTok exposes it", "Like count, publish time, totalComments + cursor pagination", "limit up to 500 — flat 2 credits per call"] },
  {
    slug: "tiktok-channel-details",
    name: "TikTok Channel Details API",
    shortName: "Channel Details",
    category: "channel",
    method: "GET",
    path: "/v1/tiktok/channel-details",
    credits: 1,
    tagline:
      "Resolve a TikTok @handle to id + secUid — createTime, ttSeller, bioLink.risk, category, commerce flags.",
    longDescription:
      "Pass a profile URL or @handle and get clean JSON for CRM joins and chaining. Canonical profile core: platform, id, handle, url, displayName, bio, avatar, followers, following, postCount, verified, createdAt — plus deprecated username/profileImage aliases for one release. Also: secUid (stable identity — handles change; follower/video lists need secUid), likes, category (commerce niche when exposed), createTime / createTimeUnix, bioLink{link,risk} + bioLinkRisk, ttSeller / isSeller (TikTok Shop bridge), isCommerceUser, isOrganization, friendCount, diggCount, language/region, duet/stitch/download/comment settings, and contact{emails,links} from the bio. Pass cacheMaxAge=1d|3d|7d|14d|30d to reuse a cached copy (envelope cached + cachedAt). Flat 1 credit.",
    delivers: [
      "id + secUid for CRM joins and follower/video chaining",
      "createTime / createTimeUnix (account age)",
      "ttSeller / isSeller — bridge to TikTok Shop endpoints",
      "bioLink.risk, category, commerce + remix settings",
    ],
  },
  { slug: "tiktok-profile-region", name: "TikTok Profile Region API", shortName: "Profile Region", category: "channel", method: "GET", path: "/v1/tiktok/profile-region", credits: 2 , tagline: "Find out where a TikTok creator is likely based and what language they use — country, language, stable ids, and core profile stats.", longDescription: "Give the TikTok Profile Region API a profile URL, @handle, or username and it returns location and language as clean JSON. TikTok almost never shows an account's country publicly, so when that value is missing we estimate the country from public cues like the bio, display name, and language. The response tells you whether the country came from TikTok itself or from that estimate (regionSource), and how confident the estimate is (regionConfidence: high, medium, or low). You also get stable id + secUid, account createTime / createTimeUnix, ttSeller + isOrganization, interface language, and core profile stats — followers, following, total likes, and videos (integer count) — plus display name, verified and private flags, and the avatar. Use it for audience and geo analysis, content localization, compliance checks, or vetting creators before a partnership. Flat 2 credits per call. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Creator country — TikTok's own when available, otherwise an AI estimate", "regionSource + regionConfidence (measured vs inferred)", "id + secUid + createTime / createTimeUnix", "ttSeller + isOrganization for Shop / org vetting", "Interface language plus followers, following, likes, and video count", "Display name, verified and private flags, and avatar"] },
  {
    slug: "tiktok-audience-demographics",
    name: "TikTok Audience Demographics API",
    shortName: "Audience Demographics",
    category: "channel",
    method: "GET",
    path: "/v1/tiktok/audience-demographics",
    credits: 3,
    tagline:
      "Commenter country + language mix for a TikTok creator — engagement sample, not a follower census.",
    longDescription:
      "Give a profile URL, @handle, or username and get a ranked commenter-country breakdown as clean JSON. TikTok does not publish follower geography — we sample people commenting on recent videos (user.region) and tally country name, countryCode, count, and numeric percentage (+ percentageText). Response includes basis=\"commenters\", sampleSize, totalCountries, confidence (low/medium/high), optional other{} when countriesLimit truncates, and audienceLanguages[] from comment_language (same sample, no extra cost). Choose videos=12|30|60 (credits 3/5/8) for sample depth. Percentages across audienceLocations (+ other) sum to ~100%. This reflects who engages, not a full follower census.",
    delivers: [
      "Numeric percentage + percentageText per country",
      "totalCountries + other{} when truncated",
      "audienceLanguages[] from the same comment sample",
      "videos=12|30|60 with scaled credits (3/5/8)",
      "basis=commenters + confidence label",
    ],
  },
  { slug: "tiktok-search-suggestions", name: "TikTok Search Suggestions API", shortName: "Search Suggestions", category: "search", method: "GET", path: "/v1/tiktok/search-suggestions", credits: 2, tagline: "Get the autocomplete terms TikTok suggests in its search bar for a keyword — the real phrases people search, ranked, so you can find trending queries and long-tail keyword ideas.", delivers: ["The autocomplete terms TikTok suggests for your keyword", "Each suggestion with its rank — the order it appears in the search bar", "A ready-to-open searchUrl that runs that exact search on TikTok", "The seed keyword plus the region and language it was localized for", "Localize by country + language to see what a specific market searches", "Flat 2 credits per call"] , longDescription: "Give the TikTok Search Suggestions API a seed keyword and it returns the autocomplete phrases TikTok shows in its search bar as clean JSON — the actual phrases people search for. Each suggestion includes the search term, its rank (1 = top of the list), a ready-to-open search URL, the seed keyword it came from, and the country and language it was localized for (region/language echo the market you requested — not a creator country). Use the country and language parameters to see what a specific market is searching (for example US in English, or DE in German). Great for TikTok keyword research, trending queries, and content planning. No TikTok login required. Flat 2 credits per call, no matter how many suggestions return. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  { slug: "tiktok-channel-posts", name: "TikTok Channel Posts API", shortName: "Channel Posts", category: "list", method: "GET", path: "/v1/tiktok/channel-posts", credits: 2, tagline: "Get the latest videos from any public TikTok profile — playable videoUrl, download links, engagement, caption, sound, and hashtags, with cursor pagination to page through them all." , longDescription: "Send a profile URL, @handle, or username and the TikTok Channel Posts API returns that creator's most recent videos as clean, structured JSON. If TikTok blocks a direct fetch, the first page automatically retries through a backup path so you still get a response. Each post includes the TikTok page URL and video ID, caption, publish date, duration, thumbnail, playable videoUrl plus downloadUrl / downloadUrlNoWatermark when TikTok exposes them (CDN-signed — check mediaUrlsExpireAt before archiving), hashtags, sound/music, isAd / isPaidPartnership / shopProductUrl when present, and the author's profile (id, secUid, username, display name, followers, verified badge, avatar). Fetch up to 200 posts per call with the limit parameter, then pass the returned nextCursor value back in to page through older videos (hasMore tells you when you've reached the end) — a flat 2 credits per call, no matter how many posts you fetch. Ideal for creator monitoring, content calendars, competitor tracking, archiving, and feeding analytics or influencer tools. No TikTok login and no infrastructure to maintain on your side.", delivers: ["Latest public videos from any TikTok profile", "Playable videoUrl + download URLs (CDN-signed; mediaUrlsExpireAt)", "Caption, publish date, duration, thumbnail, hashtags, and sound name", "Views, likes, comments, shares, and saves per video", "Author profile — id, secUid, handle, name, followers, verified, avatar", "isAd / isPaidPartnership / shopProductUrl when TikTok exposes them", "Cursor pagination (nextCursor + hasMore) — flat 2 credits per call", "Automatic first-page backup if the direct fetch fails"] },
  { slug: "tiktok-comment-replies", name: "TikTok Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/tiktok/comment-replies", credits: 2, tagline: "Replies under a TikTok comment — same authorId/authorSecUid/commentLanguage shape as comments.", longDescription: "Pass a TikTok video URL and a parent comment id and get that comment's replies as clean JSON. Each reply includes text, author username, stable authorId/authorSecUid when TikTok exposes them, commentLanguage, like count, and publish time. Fetch up to 500 replies per call, then pass nextCursor to page through the rest — a flat 2 credits per call.", delivers: ["Reply text + authorId/authorSecUid", "commentLanguage when available", "Like count and publish time per reply", "Cursor pagination (nextCursor + hasMore)", "Flat 2 credits per call"] },
  {
    slug: "tiktok-user-followers",
    name: "TikTok User Followers API",
    shortName: "User Followers",
    category: "list",
    method: "GET",
    path: "/v1/tiktok/user-followers",
    credits: 1,
    creditsPerResult: 0.4,
    tagline:
      "List a TikTok user's followers — id, secUid, createTime, region, language, cursor pagination. Flat 1 credit.",
    longDescription:
      "Pass a TikTok profile URL or @handle and get followers as clean JSON: id + secUid (stable identity — same fields search-users documents), username, displayName, bio, url, followers, following, verified, profileImage, plus createTime/createTimeUnix, region, and language when TikTok exposes them (audience quality / bot signals). total is the profile's followerCount (universe size); totalReturned is this page. Cursor pagination via nextCursor + hasMore (TikTok minCursor). Flat 1 credit on the native path; Apify fallback bills about 0.4 credits per returned user (min 5).",
    delivers: [
      "id + secUid on every follower row",
      "createTime, region, language when TikTok exposes them",
      "total (profile followerCount) + nextCursor / hasMore",
      "Flat 1 credit native; Apify ~0.4/user (min 5)",
    ],
  },
  {
    slug: "tiktok-user-followings",
    name: "TikTok User Followings API",
    shortName: "User Followings",
    category: "list",
    method: "GET",
    path: "/v1/tiktok/user-followings",
    credits: 1,
    creditsPerResult: 0.4,
    tagline:
      "List who a TikTok user follows — id, secUid, createTime, region, language, cursor pagination. Flat 1 credit.",
    longDescription:
      "Pass a TikTok profile URL or @handle and get followings as clean JSON: id + secUid, username, displayName, bio, url, followers, following, verified, profileImage, plus createTime/createTimeUnix, region, and language when TikTok exposes them. total is the profile's followingCount; cursor pagination via nextCursor + hasMore. Flat 1 credit on the native path; Apify fallback bills about 0.4 credits per returned user (min 5).",
    delivers: [
      "id + secUid on every following row",
      "createTime, region, language when TikTok exposes them",
      "total (profile followingCount) + nextCursor / hasMore",
      "Flat 1 credit native; Apify ~0.4/user (min 5)",
    ],
  },

  { slug: "tiktok-music-posts", name: "TikTok Music Posts API", shortName: "Music Posts", category: "list", method: "GET", path: "/v1/tiktok/music-posts", credits: 2, tagline: "List TikTok videos that use a specific sound — caption, author, engagement, canonical hashtags, and mentions.", longDescription: "Paste a TikTok music/sound URL and get the public videos that use that sound as structured JSON. Each result includes caption, author (same shape as top-search / channel-posts: username, displayName, url, profileImage, id, secUid, followers, verified), thumbnail, engagement, canonical hashtags (from TikTok text_extra — not caption regex), and mentions[{userId,secUid,username}] when TikTok exposes them. On MUSIC_AWEME, followers and verified are often null (unknown — not zero/false); use Channel Details for definitive profile stats. Flat 2 credits per call." },
  {
    slug: "tiktok-top-search",
    name: "TikTok Top Search API",
    shortName: "Top Search",
    category: "search",
    method: "GET",
    path: "/v1/tiktok/top-search",
    credits: 2,
    tagline:
      "TikTok Top/General search — videos and photo carousels when TikTok includes them, with contentType + images[].",
    longDescription:
      "Hits TikTok's Top/General search tab (not video-only keyword search). Results can mix videos and photo carousels: each item has mediaType/contentType (video | photo | multi_photo); carousels include images[]. Hashtags come from TikTok text_extra (canonical names — no caption-regex emoji bleed) and are lowercase-deduped; mentions[{userId,secUid,username}] when present. Supports cursor pagination via nextCursor. TikTok may return duplicate ids across pages — we drop duplicates within a page. Flat 2 credits. Not yet: sort_by / publish_time / region filters (use other endpoints or ask).",
    delivers: [
      "Videos + photo carousels (contentType, images[])",
      "Canonical hashtags from text_extra (casefold-deduped)",
      "mentions[{userId,secUid,username}] when TikTok exposes them",
      "cursor / nextCursor / hasMore",
      "isAd + isPaidPartnership when TikTok exposes them",
      "Flat 2 credits",
    ],
  },
  {
    slug: "tiktok-search-by-hashtag",
    name: "TikTok Search by Hashtag API",
    shortName: "Search by Hashtag",
    category: "search",
    method: "GET",
    path: "/v1/tiktok/search/hashtag",
    credits: 14,
    creditsPerResult: 0.7,
    tagline:
      "Videos from TikTok's /tag/{name} challenge feed — not keyword or username search. Cursor + hasMore.",
    longDescription:
      "Pass a hashtag (with or without #) and get videos from TikTok's /tag/{name} challenge feed (CHALLENGE_AWEME / api/challenge/item_list) as clean JSON — the same feed as the tag page in the app. This is not keyword search: an @comedy… account with no #comedy tag is dropped. Each result must carry the hashtag in structured tags or as #tag in the caption. Fields: url, id, caption, publishedAt, durationSeconds, thumbnail, author (+ author.region when present), engagement, hashtags, musicName, plus region / shopProductUrl / isPaidPartnership / descLanguage when TikTok exposes them. Cursor pagination via nextCursor + hasMore. The optional region query param only chooses the proxy exit country — it does not filter results by country. Billed per result — about 0.7 credits each.",
    platformLimits: [
      "The optional region query param only chooses the proxy exit country — it does not filter results by creator country.",
    ],
    delivers: [
      "Real /tag/{name} challenge feed (CHALLENGE_AWEME — not keyword search)",
      "Hashtag required on every result (structured or #tag in caption)",
      "shopProductUrl + per-video region / authorRegion when present",
      "hasMore + nextCursor (null = end)",
      "Caption only — no duplicate description field",
    ],
  },
  {
    slug: "tiktok-search-users",
    name: "TikTok Search Users API",
    shortName: "Search Users",
    category: "search",
    method: "GET",
    path: "/v1/tiktok/search/users",
    credits: 1,
    tagline:
      "Search TikTok users — id, secUid, followers/following, verified, and sample videos, with cursor pagination.",
    longDescription:
      "Pass a search query and get matching creators as clean JSON: id + secUid (stable TikTok identity — secUid is what follower/video list calls need), username, displayName, bio, url, followers, following, videos, likes, verified, profileImage, and items[] sample videos when TikTok includes them. Cursor pagination via nextCursor + hasMore. Prefer id/secUid over @handle for CRM joins — handles change. Flat 1 credit on the native path; Apify fallback bills about 0.4 credits per returned user (min 5).",
    delivers: [
      "id + secUid for stable identity / chaining",
      "followers, following, videos, likes, verified",
      "Sample items[] videos when present",
      "Cursor pagination (nextCursor + hasMore)",
    ],
  },
  {
    slug: "tiktok-song-details",
    name: "TikTok Song Details API",
    shortName: "Song Details",
    category: "details",
    method: "GET",
    path: "/v1/tiktok/song-details",
    credits: 1,
    tagline:
      "TikTok sound metadata — usageCount, durationSeconds, artists[{id,secUid,handle}], commerce rights (1 credit native).",
    longDescription:
      "Paste a TikTok music/sound URL and get the sound as clean JSON: title, author, artistId/authorSecUid, artists[{id,uid,secUid,handle,displayName,verified,avatarUrl}], durationSeconds (canonical float; duration kept as alias), cover/coverUrl/playUrl, usageCount (videos using the sound — filled from music/detail or the music page when music/aweme omits it; null when TikTok still hides the total), createdAt, isExplicit/hasLyrics when present, commerce flags (isCommerceMusic / hasCommerceRight / commercialRightType), isOriginalSound / isPgc, matchedSong.chorusInfo{startMs,durationMs}, musicReleaseInfo{isNewReleaseSong}, and extra{bpm,loudnessLufs,beats} when TikTok exposes them. Pair with Music Posts to list videos on the sound. Flat 1 credit on the native path; Apify fallback bills 2.",
    delivers: [
      "usageCount when TikTok exposes video-use totals",
      "durationSeconds (float) aligned with Music Posts",
      "artists[] + artistId / authorSecUid",
      "Commerce rights + matchedSong chorus timing",
      "Audio analysis (loudness / beats) when present; 1 credit native",
    ],
  },
  {
    slug: "tiktok-trending-feed",
    name: "TikTok Trending Feed API",
    shortName: "Trending Feed",
    category: "list",
    method: "GET",
    path: "/v1/tiktok/trending-feed",
    credits: 2,
    tagline:
      "For You by default; pass orderBy/period/page for Creative Center popular videos (like/hot/comment/repost) with totalCount. Flat 2 credits.",
    longDescription:
      "Default: TikTok For You / recommend feed with rank, publishedAt, caption, mediaType, coverUrl/videoUrl, author + authorId/secUid, and views/likes/comments/shares/saves. Pass orderBy (hot|like|comment|repost), period (7|30|120), page, or countryCode to switch to the TikTok Creative Center popular-videos chart (same filters as SC videos/popular) — Captapi still hydrates engagement/author when possible and returns pagination.totalCount (typically 500). country / countryCode is the chart market in Creative Center mode; on For You it is a region-availability hint. Flat 2 credits per call.",
    delivers: [
      "For You richness: engagement + rank + author",
      "orderBy / period / countryCode / page → Creative Center chart",
      "pagination.totalCount (~500) in chart mode",
      "Flat 2 credits",
    ],
  },
  {
    slug: "tiktok-popular-hashtags",
    name: "TikTok Popular Hashtags API",
    shortName: "Popular Hashtags",
    category: "list",
    method: "GET",
    path: "/v1/tiktok/popular-hashtags",
    credits: 2,
    tagline:
      "TikTok Creative Center hashtag chart — real videoCount/totalPlays, rankDiff, trend[]. Flat 2 credits.",
    longDescription:
      "Official TikTok Creative Center popular-hashtag chart (ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag) as clean JSON. videoCount and totalPlays are Creative Center population totals — never a 20-video sample tally. Each row: rank, rankDiff, hashtagId, trend[] time series, growthRate (from trend), optional newOnBoard / industryId filters, country + period (7/30/120). Optional query=niche seed switches to legacy co-occurrence + challenge/detail enrich for related tags. Flat 2 credits on the Creative Center path.",
    delivers: [
      "Creative Center population videoCount + totalPlays",
      "rankDiff + trend[] time series + growthRate",
      "country / period / page / newOnBoard filters",
      "Flat 2 credits (not per-video sampling)",
    ],
  },
  {
    slug: "tiktok-popular-songs",
    name: "TikTok Popular Songs API",
    shortName: "Popular Songs",
    category: "list",
    method: "GET",
    path: "/v1/tiktok/popular-songs",
    credits: 2,
    tagline:
      "Creative Center popular/surging sounds — rankDiff, trend[], commercialMusic. Flat 2 credits.",
    longDescription:
      "TikTok Creative Center sound chart (inspiration/popular/music). rankType=popular|surging, newOnBoard, commercialMusic (Commercial Music Library / ifCml — brand-safe), country, period (7/30/120), page. Each song: songId, clipId, title, artist, rankDiff, trend[] time series, growthRate, promoted. Can take up to ~30 seconds. Flat 2 credits. Pair with song-details / music-posts for a single sound's metadata and videos.",
    delivers: [
      "rankType popular | surging",
      "commercialMusic / ifCml brand-safe filter",
      "rankDiff + trend[] time series",
      "Flat 2 credits",
    ],
  },
  {
    slug: "tiktok-live",
    name: "TikTok Live API",
    shortName: "Live",
    category: "details",
    method: "GET",
    path: "/v1/tiktok/live",
    credits: 1,
    tagline:
      "Is this TikTok creator live — isLive/status, creator.id/secUid, room, streamQualities with flv/hls/cmaf/dash.",
    longDescription:
      "Send a profile URL or @handle. isLive is true only when TikTok liveRoom.status === 2 (also top-level status + room.status). A non-empty room does not mean live — offline responses may still include the last broadcast (title, startedAt, totalEnterCount, pull URLs). viewerCount is only set while live (stale concurrent counts are omitted when offline). Parsed streamQualities[{quality,codec,resolution,bitrate,flv,hls,cmaf,dash,lls}] unwrap TikTok's triple-escaped stream_data (prefer hls/cmaf for browsers — FLV will not play in a web player). Also: creator.id/secUid/following, liveSubOnly, gameTagId/hashTagId, paidEvent, streams{}. Flat 1 credit. /live-info is the identical payload at 7 credits for SC path compatibility — prefer /live.",
    delivers: [
      "Authoritative isLive (status === 2 only)",
      "creator.id + secUid for chaining",
      "streamQualities with flv + hls + cmaf/dash (when TikTok exposes them)",
      "gameTagId / hashTagId / paidEvent when present",
    ],
  },
  {
    slug: "tiktok-live-info",
    name: "TikTok Live Info API",
    shortName: "Live Info",
    category: "details",
    method: "GET",
    path: "/v1/tiktok/live-info",
    credits: 7,
    tagline:
      "Identical to TikTok Live (isLive, creator.id/secUid, streamQualities hls/cmaf) — 7 credits for SC compatibility.",
    longDescription:
      "True alias of GET /v1/tiktok/live — same runner, same JSON (isLive/status, creator.id/secUid, room.streamQualities with flv/hls/cmaf/dash when TikTok exposes them). Own billing/cache key only. Prefer /live (1 credit) unless you need this path for ScrapeCreators-compatible routing. Flat 7 credits.",
  },
  {
    slug: "tiktok-popular-creators",
    name: "TikTok Popular Creators API",
    shortName: "Popular Creators",
    category: "list",
    method: "GET",
    path: "/v1/tiktok/popular-creators",
    credits: 2,
    tagline:
      "Creative Center creators + createTime / bioLinkRisk / ttSeller hydrate for partnership vetting.",
    longDescription:
      "Primary source: TikTok Creative Center creator chart with official interact rate (engagementRateBasis=creative_center) plus rankDiff. Each creator is profile-hydrated with createTime / createTimeUnix (account age — the #1 bot signal), bioLinkRisk, ttSeller, and contact{emails,links} when present — so Creator Verification and Partnership Qualification actually work. Falls back to For You feed hydrate then Apify. sort=follower|engagement|popularity. Flat 2 credits on Creative Center / FYP native. Pass cacheMaxAge=1d|3d|7d|14d|30d for freshness-tolerant caching.",
    delivers: [
      "createTime account age on every hydrated creator",
      "bioLinkRisk + ttSeller + contact{}",
      "Creative Center official ER + rankDiff",
      "Flat 2 credits native",
    ],
  },
];

const INSTAGRAM: Spec[] = [
  {
    slug: "instagram-transcript",
    name: "Instagram Transcript API",
    shortName: "Transcript",
    category: "transcript",
    method: "GET",
    path: "/v1/instagram/transcript",
    credits: 2,
    tagline:
      "Turn any Instagram Reel's speech into text — the full transcript plus timestamped segments, ready for search, subtitles, or AI pipelines.",
    longDescription:
      "Send a Reel URL and the Instagram Transcript API returns everything spoken in the video as clean text: the full transcript, timestamped segments (start time and duration for each line), and word count. Auto-detects the spoken language, or pass an optional language code (like 'tr' or 'en') to pin it — recommended for short clips. Great for making Reels searchable, generating subtitles, feeding AI tools, or turning video into text. No Instagram login or OAuth required. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.",
    platformLimits: [
      "Some Instagram caption surfaces only expose about the first ~2 minutes of speech. Longer Reels may return a partial transcript when Meta truncates captions upstream.",
    ],
  },
  { slug: "instagram-summarizer", name: "Instagram Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/instagram/summarize", credits: 4, tagline: "Get an AI summary of any Instagram Reel — a short paragraph plus key points, without watching the video.", longDescription: "Send a Reel URL and the Instagram Summarizer API transcribes the video and returns an AI-written summary as clean JSON: a concise paragraph plus a list of key points. Pass an optional language code (like 'tr') to pin the speech language and get the summary in that language — otherwise it auto-detects and summarizes in English. Perfect for content research at scale, briefing tools, and AI agents that need to understand video content without processing media. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  {
    slug: "instagram-details",
    name: "Instagram Post Details API",
    shortName: "Post Details",
    category: "details",
    method: "GET",
    path: "/v1/instagram/details",
    credits: 1,
    tagline:
      "Get an Instagram post or Reel — caption, likes, comments, media URLs, author, and split view counts on Reels.",
    longDescription:
      "Paste an Instagram post or Reel URL and get the item as clean JSON: caption, like and comment counts, media URLs, author profile, duration when it is a Reel, and publish date. On Reels, engagement.views is the canonical play count when Instagram exposes one; viewsSource is instagram|facebook whenever views is set; plays is a deprecated one-release alias of views. Flat 1 credit. Pass cache=true for the 24h shared cache.",
    delivers: [
      "Caption, media URLs, and publish date",
      "engagement.views + viewsSource on Reels when available",
      "Like and comment counts",
      "Author profile fields",
    ],
  },
  { slug: "instagram-comments", name: "Instagram Post Comments API", shortName: "Post Comments", category: "comments", method: "GET", path: "/v1/instagram/comments", credits: 45, creditsPerResult: 0.9, tagline: "Get the comments on any Instagram post or Reel — text, author, avatar, likes, and timestamp for each comment.", longDescription: "Send a post or Reel URL and the Instagram Post Comments API returns its comments as clean, structured JSON. Each comment includes the text, author username and avatar, like count, and when it was posted. Use the limit parameter (up to 500) to control how many you fetch — billing scales with results returned. Ideal for sentiment analysis, social listening, comment moderation, and finding engaged fans or customer feedback. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  {
    slug: "instagram-channel-details",
    name: "Instagram Channel Details API",
    shortName: "Channel Details",
    category: "channel",
    method: "GET",
    path: "/v1/instagram/channel-details",
    credits: 1,
    tagline:
      "Instagram profile stats — fixed key set (null fillers), fbid, bioLinks, isBusinessAccount, approx flags.",
    longDescription:
      "Send a profile URL or @handle and get clean JSON with a fixed key set on every profile (absent → null, never a missing key): platform, url, id, fbid, username, displayName, bio, bioLinks, followers, following, postCount, verified, avatar, imageExpiresAt, externalUrl, isPrivate, isBusinessAccount, followersIsApproximate, followingIsApproximate, postCountIsApproximate, fetchedAt. Twin aliases handle/name/profileImage and the duplicate profileImageHd key are not emitted — avatar is the single best profile-pic URL (CDN size token upgraded when Instagram only ships s150x150). Approx flags are derived from the source (true when a count came from a K/M/B display string such as og:description \"32K\"). Flat 1 credit. Cold path races WPI/GraphQL/HTML; hard cap 110s → 502, 0 credits. Pass cache / cacheMaxAge for the profile trust layer.",
  },
  {
    slug: "instagram-channel-posts",
    name: "Instagram Channel Posts API",
    shortName: "Channel Posts",
    category: "list",
    method: "GET",
    path: "/v1/instagram/channel-posts",
    credits: 6,
    creditsPerResult: 0.3,
    tagline:
      "Latest posts from a public Instagram profile — carousel children[], mediaCount, user{} in one call.",
    longDescription:
      "Send a profile URL or @handle and get recent posts as JSON plus a top-level user{} profile block (id, username, displayName, url, verified, followers, avatar, isPrivate) so you do not need a second channel-details call. Profile URLs are always https://www.instagram.com/{username}/ (www + trailing slash) on the envelope, user{}, and author{}. Each item includes postType / productType (Image/feed, Video/clips, Sidecar/carousel_container — the discriminator a mixed feed needs), caption (not a duplicated description), mediaCount (1 for singles; children.length when carousel expansion ran; null on Sidecar when slides were not expanded — never a fabricated 1), and children[] (per-slide id / mediaType / thumbnailUrl / videoUrl — [] on non-carousels and on unexpanded Sidecars). Cover thumbnailUrl is the first slide; Sidecar cover videoUrl stays null — video slides live in children[]. Also likes, comments, and on videos: durationSeconds, hasAudio, music{}, isAd / isAffiliate / isPaidPartnership when Instagram exposes them. accessibilityCaption when Instagram provides alt-text (backfilled from the api/v1 feed overlay — populated e.g. on @instagram/DbbY9pdm6Q2; still often null on nasa/natgeo). Envelope always includes the same keys on both paths: user / userId (null when unknown), degraded, degradedReason (null when healthy; apify-fallback, apify-timeout, or apify-timeout-served-stale when soft-fail). Apify soft-fail is hard-capped at ~105s; on timeout we serve the last cached page for that profile (degradedReason=apify-timeout-served-stale + cachedAt) when one exists, else an empty apify-timeout page — never a 524 at Cloudflare's 125s edge. Metrics: engagement.views + viewsSource on videos. Cursor pagination via nextCursor + hasMore. Billing ceil(n × 0.3); empty and labelled-stale timeout responses are 0 credits. Pass cache=true for the 24h shared cache (successful fetches always refresh it). Set client timeouts ≥130s.",
    delivers: [
      "Top-level user{} profile (null on degraded path)",
      "Sidecar children[] + honest mediaCount (null if unexpanded)",
      "Stale-serve on extended-timeout (cachedAt labelled)",
      "Uniform envelope: degraded / degradedReason / user / userId",
    ],
    platformLimits: [
      "location is not returned — logged-out feed/GraphQL samples never carry a tagged place (0/72 across nasa/natgeo/instagram); not a silent cover-only gap.",
      "description is not returned — caption is the text field (same as channel-reels).",
      "degraded: true (extended | extended-timeout | extended-timeout-served-stale) — extended-path budget ~105s; on timeout prefer a labelled day-old cache over empty. Set client timeouts ≥130s.",
      "accessibilityCaption is sparse Instagram alt-text — null on many profiles; when present it is backfilled from the feed overlay (e.g. @instagram/DbbY9pdm6Q2).",
    ],
  },
  {
    slug: "instagram-channel-reels",
    name: "Instagram Channel Reels API",
    shortName: "Channel Reels",
    category: "list",
    method: "GET",
    path: "/v1/instagram/channel-reels",
    credits: 6,
    creditsPerResult: 0.3,
    tagline:
      "Latest Reels from a public Instagram profile — pass userId to skip resolve; ceil(n×0.3) credits; nextCursor + hasMore.",
    longDescription:
      "Send a profile URL/@handle or a numeric userId and get that account's recent Reels (videos only). Prefer userId when you already have it (from basic-profile or profile-search) — it skips handle→ID resolve (the old sequential path alone could cost ~80s; url/@handle now uses the same raced resolver as profile-search). Each Reel includes videoUrl, thumbnailUrl, caption (not a duplicated description), likes, comments, duration, and publish date. Billing is ceil(n × 0.3) credits on the returned reel count (17 → 6, 5 → 2). Metrics when Instagram exposes them: engagement.views + viewsSource. Cursor pagination via nextCursor; hasMore is true until the end of the list. Pass cache=true for the 24h shared cache.",
    delivers: [
      "Reels only (photos/carousels filtered out)",
      "userId skips resolve (~80s saved vs legacy sequential WPI)",
      "engagement.views + viewsSource when available",
      "nextCursor + hasMore pagination",
      "Credits: ceil(returned × 0.3), minimum 1",
    ],
    platformLimits: [
      "Envelope url is a real profile URL when known; with userId-only input it is null (identity is userId) — never instagram_user:{id}.",
      "postType/productType/description are not on reels[] (reels-only endpoint; caption is the text field).",
    ],
  },
  {
    slug: "instagram-reels-search",
    name: "Instagram Reels Search API",
    shortName: "Reels Search",
    category: "search",
    method: "GET",
    path: "/v1/instagram/reels-search",
    credits: 2,
    tagline:
      "Native Instagram Reels hashtag search — engagement.views + viewsSource, location, commercial flags. Flat 2 credits.",
    longDescription:
      "Send a hashtag (without the #) or keyword and get matching Reels from Instagram's native hashtag grid as clean JSON — videos only. Engagement: likes, comments, views (canonical play count when Instagram exposes one), viewsSource (instagram|facebook|null — non-null whenever views is), and plays as a deprecated one-release alias of views. Author includes id / verified / profileImage / followers / postCount when available. Also music{}, location{id,name,slug,address}, isAd / isAffiliate / isPaidPartnership, previewComments with authorId, hasAudio, accessibilityCaption, durationSeconds (3 d.p.), and publish date. Optional datePosted=last_24_hours|last_week|last_month|last_year. Flat 2 credits. Pass cache=true for the 24h shared cache.",
    delivers: [
      "engagement.views + viewsSource (discriminator tracks views)",
      "location{} with address when tagged",
      "isAd / isAffiliate / isPaidPartnership",
      "durationSeconds rounded to 3 decimals",
    ],
  },
  {
    slug: "instagram-trending-reels",
    name: "Instagram Trending Reels API",
    shortName: "Trending Reels",
    category: "list",
    method: "GET",
    path: "/v1/instagram/trending-reels",
    credits: 2,
    tagline:
      "Cache-first trending Reels — flat 2 credits every call (4h TTL).",
    longDescription:
      "On-demand trending Reels for a country. Flat 2 credits on every successful call — including cache hits (the 4h per-country response cache is our margin, not a free tier). Default cache=true is cache-first for latency; cache=false forces a live native /reels scrape (typically under 20s, hard-capped at 110s under Cloudflare). Concurrent requests for the same country share one scrape (single-flight). Failures return 502 with a stage-specific code (scrape_failed / fetch_empty / hydrate_empty / filtered_empty / timeout) — never an old snapshot, never 503 warming, and no silent Apify fallback. Each reel includes engagement{likes,comments,views,viewsSource} where views is the platform play count when exposed and viewsSource is instagram|facebook whenever views is set. Instagram withholds view counts on roughly a third of reels — those rows keep views/viewsSource null. Constant postType/productType are omitted. durationSeconds is always present (null when unknown), rounded to 3 decimals when set. Photos/carousels are never returned. Content older than ~180 days is dropped as Explore resurfacing. For live keyword search use Instagram Reels Search.",
    delivers: [
      "Flat 2 credits always (cache hit or live)",
      "Cache-first hot path (<2s) with 4h TTL; single-flight; 110s hard deadline",
      "engagement.views + viewsSource (plays removed); staged 502 on scrape failure",
      "Video Reels only — never Explore photos; native path only",
    ],
    platformLimits: [
      "No warm cron / country snapshots — only the on-demand response cache.",
      "cache=false always live-scrapes. Billing stays flat 2 credits either way. Hard deadline 110s.",
      "Photos / carousels / Explore resurfaces older than ~180 days are filtered out.",
      "Instagram does not expose a view count for every reel; engagement.views stays null when withheld.",
    ],
  },
  {
    slug: "instagram-tagged-posts",
    name: "Instagram Tagged Posts API",
    shortName: "Tagged Posts",
    category: "list",
    method: "GET",
    path: "/v1/instagram/tagged-posts",
    credits: 1,
    tagline:
      "Posts that tag an Instagram account — author verified/avatar when available, staleFeed when Instagram only exposes an archive.",
    longDescription:
      "Pass a profile URL or @handle and get the profile's Tagged tab as clean JSON: id/shortcode, postType, caption, publishedAt, author{id,username,displayName,url,verified,profileImage when Instagram exposes them}, engagement{views,likes,comments}, hashtags[], mentions[]. Cursor pagination via nextCursor + hasMore. Every response includes staleFeed plus newestPublishedAt / oldestPublishedAt — when Instagram only exposes a truncated historical window (e.g. natgeo returning only 2018 tags), staleFeed is true and note explains why this is not live brand monitoring. Accounts like nasa still return recent UGC with staleFeed false. Flat 1 credit on the native path; Apify fallback is ~0.9/result only when the feed is fresh — archived windows stay flat 1 credit.",
    delivers: [
      "staleFeed + newest/oldestPublishedAt (archive window honesty)",
      "author.verified / profileImage when available",
      "engagement.views on video/Reel tags when Instagram exposes them",
      "Cursor pagination (nextCursor + hasMore)",
    ],
  },
  {
    slug: "instagram-reels-by-audio-id",
    name: "Instagram Reels By Audio ID API",
    shortName: "Reels By Audio ID",
    category: "list",
    method: "GET",
    path: "/v1/instagram/reels-by-audio-id",
    credits: 28,
    creditsPerResult: 1.4,
    tagline:
      "Is this Instagram sound trending? Reels that use it + isTrendingInClips / trendRank / rich music{}.",
    longDescription:
      "Pass an audio ID or https://www.instagram.com/reels/audio/AUDIO_ID/ URL. The response includes the trend signals this endpoint is for — isTrendingInClips, trendRank, previousTrendRank — plus music{} (clusterId, assetId, canonicalId, title, artist, durationMs, audioType, isExplicit, hasLyrics, coverUrl). Then the list of public Reels using that sound: video URL, caption, creator, views/likes/comments, durationSeconds, hasAudio, and when Instagram exposes them coauthors[] (collabs) and mashupInfo.hasBeenMashedUp. Use it to measure how far a sound has spread or whether it is trending in Reels. Pass cache=true for the 24h shared cache.",
    delivers: [
      "isTrendingInClips + trendRank + previousTrendRank",
      "music{} with clusterId / title / artist / audioType / coverUrl",
      "Reels list with hasAudio, coauthors, mashupInfo when available",
      "Video URL, caption, engagement, durationSeconds",
    ],
  },
  {
    slug: "instagram-hashtag-search",
    name: "Instagram Hashtag Search API",
    shortName: "Hashtag Search",
    category: "search",
    method: "GET",
    path: "/v1/instagram/hashtag-search",
    credits: 2,
    tagline:
      "Native Instagram hashtag Explore — Reels-heavy top surface with real likes, views, captions, and paid flags. Flat 2 credits.",
    longDescription:
      "Pass a hashtag without the # (e.g. travel or foodie) and get posts from Instagram's hashtag Explore as clean JSON — not keyword search and not a Google-indexed subset. Instagram's top/hashtag surface is Reels-heavy (productType clips); photos and Sidecars appear when the tag grid includes them, or use mediaType=reels for clips only. Each result includes url, postType, productType, caption, author (followers / postCount when available), engagement.views (video_view_count when present) plus engagement.plays (total plays incl. replays — often ~2× views), likes and comments — likes come from like_count, never from play totals — and viewsInstagram / viewsFacebook when Instagram exposes the IG vs Facebook split (viewsInstagram excludes Facebook cross-post). Also paid-partnership / ad / affiliate flags, audio (musicId), location{id,name,slug,address}, preview comments with authorId when present, thumbnail, and hashtags / @mentions. Flat 2 credits per call. Pass cache=true for the 24h shared cache (0 credits on hit); default is always fresh.",
    delivers: [
      "Hashtag Explore posts (Reels-heavy top surface; not keyword search)",
      "views + plays + likes + comments (likes ≠ plays; views ≠ plays)",
      "viewsInstagram / viewsFacebook on Reels when available",
      "isPaidPartnership / isAd / isAffiliate, musicId, location, mediaType=reels",
    ],
  },
  {
    slug: "instagram-profile-search",
    name: "Instagram Profile Search API",
    shortName: "Profile Search",
    category: "search",
    method: "GET",
    path: "/v1/instagram/profile-search",
    credits: 1,
    tagline:
      "Resolve a brand or @handle to one public Instagram profile — stable id, bio, links, and stats (not niche discovery).",
    delivers: [
      "One resolved public profile (mode=resolve only — keyword search is login-gated)",
      "Stable numeric id + canonical www.instagram.com/{user}/ url for joins",
      "username, displayName, bio, bioLinks, externalUrl, categoryName, platform",
      "followers / following / postCount + verified, isPrivate, business flags",
    ],
    platformLimits: [
      "mode is always resolve — Instagram's multi-result keyword search requires login; there is no search mode and no nextCursor/hasMore on this endpoint.",
      "Cold resolve typically finishes in a few seconds when Decodo GraphQL or logged-out WPI wins; budget ~15s client-side. Cache hits are ~2–3s and free.",
      "avatar is a signed Instagram CDN URL (oe= expiry). imageExpiresAt is ISO when oe= is present; re-host for long-term storage.",
      "0 or 1 users[] — not a paginated discovery feed. Use relatedProfiles[] for adjacent accounts.",
    ],
    longDescription:
      "Pass an account name, @handle, or profile URL (e.g. nike, @nasa, instagram.com/natgeo) and this endpoint resolves it to the matching public Instagram account — a name→username resolver, not a Google-style niche discovery search (queries like \"fitness coach\" will not return a creator list). Response: mode=resolve (the only mode; Instagram keyword search is login-gated), users[0] with platform, id (numeric), username, displayName, url (canonical https://www.instagram.com/{user}/), bio, bioLinks[], externalUrl, categoryName, fbid, relatedProfiles[], businessAddress, likeAndViewCountsDisabled, followers/following/postCount, verified, isPrivate, isBusinessAccount/isProfessionalAccount, avatar, and imageExpiresAt when the CDN oe= param is present. No nextCursor — resolve returns at most one user. Walk relatedProfiles for niche discovery without a separate creator-search endpoint. Flat 1 credit. Cache is on by default (24h shared cache, 0 credits on hit) because a resolve answer barely changes — pass cache=false to force a fresh upstream lookup. Cold path is a raced native WPI + Decodo GraphQL resolve (not Apify); set client timeouts ≥15s, not 10s.",
  },
  { slug: "instagram-embed", name: "Instagram Embed HTML API", shortName: "Embed HTML", category: "details", method: "GET", path: "/v1/instagram/embed", credits: 1, tagline: "Get Instagram's own self-contained embed HTML for any post, reel, or profile — ready to drop into an iframe on your site.", longDescription: "Pass an Instagram post, reel, or profile URL (or an @handle) and get back Instagram's own self-contained embed page as ready-to-use HTML — the full <html> document Instagram serves at /embed/, which you can drop straight into an <iframe srcdoc> or render server-side. The response also returns embedUrl, so you can point an <iframe src> at it directly instead. Posts and reels come back as a rich media card (with caption); profiles come back as a profile card that links to the account. No login or OAuth needed — it's fast, costs just 1 credit. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh. If Instagram's embed page is ever unavailable, the response falls back to the classic blockquote + embed.js snippet.", delivers: ["Instagram's full self-contained embed HTML document", "embedUrl you can load directly in an <iframe src>", "Canonical Instagram permalink for the post/reel/profile", "Type flag (post/reel/profile) plus shortcode or username"] },
  {
    slug: "instagram-highlights",
    name: "Instagram Highlights API",
    shortName: "Highlights",
    category: "list",
    method: "GET",
    path: "/v1/instagram/highlights",
    credits: 1,
    tagline:
      "Persistent Story Highlight albums for a public profile — id, title, cover, owner. Flat 1 credit.",
    longDescription:
      "Pass a profile URL/@handle or numeric userId and get that account's Story Highlight albums as clean JSON — persistent collections (GRWM, Travel, Products…), not live 24h Stories. Each item: id, title (niche signal without AI), coverUrl, itemCount when available, and owner{id,username}. Use titles for category discovery or brand product catalogs stored in highlights. Flat 1 credit. Pass cache=true for the 24h shared cache. Pair with /v1/instagram/highlights-details for album items.",
    delivers: [
      "Highlight id + title + coverUrl",
      "owner{id, username}",
      "Persistent albums (not live Stories)",
      "Flat 1 credit",
    ],
  },
  {
    slug: "instagram-highlights-details",
    name: "Instagram Highlights Details API",
    shortName: "Highlight Details",
    category: "details",
    method: "GET",
    path: "/v1/instagram/highlights-details",
    credits: 1,
    tagline:
      "Items inside one Instagram Story Highlight album — media URLs, type, takenAt. Flat 1 credit.",
    longDescription:
      "Pass a highlight id from /v1/instagram/highlights and get the album's items as clean JSON: type (Image/Video), url, thumbnailUrl, takenAt, dimensions, durationSeconds on videos, plus coverUrl and title. Flat 1 credit. Pass cache=true for the 24h shared cache.",
    delivers: [
      "Per-item media URLs + takenAt",
      "Video duration when applicable",
      "coverUrl + title + itemCount",
      "Flat 1 credit",
    ],
  },
  {
    slug: "instagram-basic-profile",
    name: "Instagram Basic Profile API",
    shortName: "Basic Profile",
    category: "channel",
    method: "GET",
    path: "/v1/instagram/basic-profile",
    credits: 1,
    tagline:
      "Instagram profile by user ID or @handle — camelCase schema aligned with Channel Details (followers, externalUrl, businessAddress).",
    longDescription:
      "Pass an Instagram numeric user ID (e.g. 13460080) or a profile URL / @handle and get that account's public profile as clean Captapi JSON — same naming as Channel Details: displayName, bio, followers / following / postCount, verified, isPrivate, profileImage / profileImageHd, externalUrl, bioLinks[], categoryName (Instagram business niche — Entrepreneur, Digital Creator, …), isBusinessAccount / isProfessionalAccount, businessAddress{cityName,latitude,longitude,…}, fbid (Instagram↔Facebook join key), relatedProfiles[] (edge_related_profiles discovery graph), likeAndViewCountsDisabled (distinguishes hidden likes from true zero), highlightReelCount, hasClips, and transparency flags when Instagram exposes them. Empty/null fields are omitted. Flat 1 credit. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.",
    delivers: [
      "categoryName + fbid + businessAddress + relatedProfiles",
      "likeAndViewCountsDisabled (0 ≠ hidden)",
      "externalUrl + bioLinks[] when present",
      "Lookup by numeric user ID or @handle (1 credit)",
    ],
  },
];

const FACEBOOK: Spec[] = [
  { slug: "facebook-details", name: "Facebook Details API", shortName: "Details", category: "details", method: "GET", path: "/v1/facebook/details", credits: 2, tagline: "Facebook post or Reel — caption, engagement, author id, SD/HD video, captions, and music when Facebook exposes them.", longDescription: "Paste a Facebook post or Reel URL and get clean JSON: caption, publishedAt, engagement, author (including stable author.id when present), videoUrl plus additive videoSdUrl/videoHdUrl, videoWidth/videoHeight, captionsUrl (.srt), feedbackId, and music when available. Note: for some Reels, the view count on the individual post page can be null or lower than the public Reels grid badge — use Facebook Profile Reels and match by post id if you need that badge count. Flat 2 credits per call." },
  { slug: "facebook-summarizer", name: "Facebook Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/facebook/summarize", credits: 4 },
  {
    slug: "facebook-comments",
    name: "Facebook Comments API",
    shortName: "Comments",
    category: "comments",
    method: "GET",
    path: "/v1/facebook/comments",
    credits: 2,
    tagline:
      "Facebook post comments with 10-type reaction breakdown, stable author.id (pfbid), gender, and replyCount.",
    longDescription:
      "Pass a post/Reel URL or feedbackId (from /v1/facebook/details) and get top-level comments as clean JSON. Each comment includes reactionCount plus reactions{like,love,care,haha,wow,sad,anger,thankful,pride,confused} — Facebook's ground-truth sentiment mix, not an AI guess. author is an object with stable id (pfbid or numeric), name, shortName, gender when exposed, plus authorUrl/authorAvatarUrl. replyCount and hasMore are included for threading/loops. Flat 2 credits. Prefer feedbackId when you already fetched details.",
    delivers: [
      "10-type reactions{} + reactionCount (not just likeCount)",
      "Stable author.id (pfbid) for repeat-commenter detection",
      "author.gender + shortName when Facebook exposes them",
      "replyCount + hasMore; optional feedbackId input",
    ],
  },
  {
    slug: "facebook-page-details",
    name: "Facebook Page Details API",
    shortName: "Page Details",
    category: "channel",
    method: "GET",
    path: "/v1/facebook/page-details",
    credits: 2,
    tagline:
      "Facebook page profile — likes vs followers (distinct), talkingAbout, category, website, and public email.",
    longDescription:
      "Pass a Facebook page URL, @handle, or page name and get clean JSON: username, displayName (short brand) + fullName (page title), bio, verified, profileImage/coverImage, category, website, and public email when the page exposes one (CRM/outreach-ready). Metrics are distinct: likes (exact page likes from Facebook), followers (often a compact chrome label like 28M — flagged with followersIsApproximate=true), following, and talkingAbout. Likes are never copied into followers. Flat 2 credits. Pass cache=true for the 24h shared cache.",
  },
  {
    slug: "facebook-profile-posts",
    name: "Facebook Profile Posts API",
    shortName: "Profile Posts",
    category: "list",
    method: "GET",
    path: "/v1/facebook/profile-posts",
    credits: 2,
    tagline: "Latest posts and Reels from a Facebook page — one author casing, stable engagement shape, scrapedAt.",
    longDescription: "Pass a Facebook page URL or @handle and get that page's recent posts as clean JSON (text posts and Reels mixed). author.username uses one consistent vanity casing across the page (no nasa vs NASA split). engagement always includes views and shares (null when unknown / not a video) — never invents shares:0 from listing noise. Top-level scrapedAt tells you when the page was fetched so you can compare with Profile Reels. Flat 2 credits on the native path.",
    delivers: [
      "Mixed posts + Reels with one author.username casing per page",
      "engagement.views / shares always present (null when unknown)",
      "scrapedAt on the response for freshness vs profile-reels",
      "Flat 2 credits native",
    ],
    platformLimits: [
      "Facebook's public page feed typically returns about 3 posts per page/cursor hop. Use nextCursor/hasMore to walk further — not a full dump in one call.",
    ],
  },
  { slug: "facebook-profile-reels", name: "Facebook Profile Reels API", shortName: "Profile Reels", category: "list", method: "GET", path: "/v1/facebook/profile-reels", credits: 2, tagline: "Latest Facebook page Reels — views, likes, comments, shares; newest-first without archive padding.", longDescription: "Pass a Facebook page or profile URL and get that account's recent Reels as clean JSON: caption, publishedAt, duration, thumbnail / video URL, author, and full engagement (views, likes, comments, shares). Results are newest-first. Listing uses the Reels tab when available (else Videos), with a shallow scroll so years-old archive videos from deep /videos history are not mixed in; a >1 year gap between consecutive items stops the page (recency cliff). Includes scrapedAt so you can compare counts with Profile Posts from the same moment. Flat 2 credits per call. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  { slug: "facebook-group-posts", name: "Facebook Group Posts API", shortName: "Group Posts", category: "list", method: "GET", path: "/v1/facebook/group-posts", credits: 2 },
  { slug: "facebook-comment-replies", name: "Facebook Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/facebook/comment-replies", credits: 2 },
  {
    slug: "facebook-profile-photos",
    name: "Facebook Profile Photos API",
    shortName: "Profile Photos",
    category: "list",
    method: "GET",
    path: "/v1/facebook/profile-photos",
    credits: 2,
    tagline:
      "Photo grid from a Facebook Page — full image URL plus accessibilityCaption (alt-text, not a post caption).",
    longDescription:
      "Pass a Facebook Page URL or @handle and get photos from the public /photos grid as clean JSON: id, url, image (full-size CDN), optional thumbnailUrl, width/height when Facebook exposes them, and accessibilityCaption — Facebook's image alt-text / accessibility description, not a user-written post caption. Publish time and likes/comments are usually absent on this surface (platform limit, not a Captapi gap). Flat 2 credits. Pass cache=true for the 24h shared cache.",
    delivers: [
      "accessibilityCaption = alt-text (never mislabeled as caption)",
      "Full-size image URL (+ thumbnailUrl when present)",
      "Honest: date/engagement usually unavailable on /photos",
    ],
  },
];

const FACEBOOK_MARKETPLACE: Spec[] = [
  {
    slug: "facebook-marketplace-search",
    name: "Facebook Marketplace Search API",
    shortName: "Marketplace Search",
    category: "search",
    method: "GET",
    path: "/v1/facebook/marketplace-search",
    credits: 2,
    tagline:
      "Search Marketplace by keyword + city — filters, isLocal/shipsOutsideRadius, opaque cursor (2 credits).",
    longDescription:
      "Search Facebook Marketplace with a product keyword and a city/place name (no lat/lng required — resolved to a hub slug, not a Decodo location-search). Each result: title, price + priceAmount (minor units), categoryId, location{name,city,state,countryCode,latitude,longitude} (same object shape as Event endpoints; flat city/state kept one release), deliveryTypes, status (available|pending|sold) with isSold/isPending/isHidden, cover image, createdAt, plus isLocal and shipsOutsideRadius so nationwide shipped listings (SHIPPING / SHIPPING_ONSITE) are not mistaken for nearby pickups. Facebook can surface shipped inventory outside radiusMiles — use deliveryMethod=local_pickup for local-only, or filter on isLocal. Optional filters: minPrice, maxPrice, sortBy, daysSinceListed, condition, deliveryMethod, availability, radiusMiles, category. Opaque nextCursor within the fetched SSR page. Default list path is flat 2 credits (cover photo in image — photos[] only when the card has more than one). Pass details=true for description, condition, coordinates, full photo gallery, seller{} when Facebook exposes it, and distanceMiles — billed as 2 + 2 credits per listing. Decodo search typically ~25–60s; budgets 80s (90s with scroll). Timeouts return HTTP 504 UPSTREAM_TIMEOUT with timings{resolveMs,fetchMs,parseMs,totalMs,path} on the error envelope. Client timeout ≥100s.",
    delivers: [
      "12 filters + city-name location (no lat/lng required)",
      "isLocal / shipsOutsideRadius on every row",
      "status enum (available|pending|sold)",
      "details=true = 2 + 2 credits per listing (stated upfront)",
    ],
    platformLimits: [
      "Shipped listings can appear outside radiusMiles — prefer deliveryMethod=local_pickup or isLocal.",
      "Deep feed pagination beyond one SSR/scroll page is not replayable across Decodo calls.",
      "Client timeout ≥100s recommended — Decodo search often lands near 25–60s, occasionally longer.",
    ],
  },
  {
    slug: "facebook-marketplace-location-search",
    name: "Facebook Marketplace Location Search API",
    shortName: "Location Resolve",
    category: "search",
    method: "GET",
    path: "/v1/facebook/marketplace-location-search",
    credits: 2,
    tagline:
      "Disambiguate city names into Marketplace hubs — id + lat/lng. Flat 2 credits.",
    longDescription:
      "Resolve a city/place query into Facebook Marketplace location hubs with id (Facebook city_page.id — same value marketplace-search listings expose as cityPageId), slug, city/state, and coordinates when available. marketplace-search already accepts a city string with no lat/lng required — use this endpoint when the name is ambiguous (Austin TX vs Austin MN vs Austin IN) or you need id/coordinates before searching. Bare ambiguous cities (Austin, Portland, Springfield) resolve from a local table in typically under 1s; single-hub Decodo fetches budget ~35s. Envelope timings{path,hubMs,hubCount,totalMs}. Client timeout ≥60s. Flat 2 credits.",
    delivers: [
      "id = Facebook city_page.id (join to search cityPageId)",
      "Multi-candidate disambiguation for bare city names",
      "lat/lng + Marketplace hub slug when available",
    ],
    platformLimits: [
      "Optional geocode — skip when marketplace-search's city string is enough.",
      "id may be omitted when Facebook's hub HTML does not expose city_page.id.",
      "Client timeout ≥60s recommended (ambiguous table path is usually <1s).",
    ],
  },
  {
    slug: "facebook-marketplace-item",
    name: "Facebook Marketplace Item API",
    shortName: "Marketplace Item",
    category: "details",
    method: "GET",
    path: "/v1/facebook/marketplace-item",
    credits: 2,
    tagline:
      "Marketplace listing — title, priceAmount, status, seller{}, condition, coords (2 credits).",
    longDescription:
      "Paste a Facebook Marketplace item URL and get the listing as clean JSON aligned with search rows: title, price + priceAmount (minor units), currency, categoryId, location{name,city,state,countryCode,latitude,longitude} (same object shape as Event endpoints), cityPageId, status (available|pending|sold) with isSold/isPending/isHidden, deliveryTypes, image + photos[], createdAt, plus detail-only description, condition, and seller{id,name,url,joinedAt,rating} when Facebook's public page exposes marketplace_listing_seller. Flat city/state/latitude/longitude kept one release. Decodo fetch budgets ~50s — timeouts return HTTP 504 UPSTREAM_TIMEOUT with timings (not a mislabelled 404). Flat 2 credits. Session-only isViewerSeller is never returned.",
    delivers: [
      "Same core fields as search rows (incl. priceAmount, city/state)",
      "status enum — not livestream isLive",
      "seller{} when Facebook exposes it",
      "description, condition, lat/lng, full photos[]",
    ],
  },
];

const FACEBOOK_EVENTS: Spec[] = [
  {
    slug: "facebook-event-search",
    name: "Facebook Event Search API",
    shortName: "Event Search",
    category: "search",
    method: "GET",
    path: "/v1/facebook/event-search",
    credits: 2,
    tagline:
      "Search Facebook events by topic and city — local startDate/timezone, venue. 2 credits.",
    longDescription:
      "Search public Facebook events with a topic query (e.g. comedy) and optional location / from / to / upcoming filters. Each result uses the same Event shape as Event Details and Profile Events — every field present, null when Facebook omits it: startDate/endDate as ISO with the host timezone offset (calendar day matches startTime — evening CDT events do not roll to the next UTC day), IANA timezone (from venue lat/lng when present — never Etc/*), startTime (always includes the year), isPast, eventType (discovery category, e.g. Comedy), visibility (public|private|friends|… from Facebook's *_TYPE), location{name,city,latitude,longitude,countryCode} (all five keys always — null when unknown), description, image, organizers, ticketsUrl, categories, and usersGoing/usersInterested when exposed. Relative labels like \"Happening now\" are never returned as startTime. Billing: flat 2 credits on every successful call — check source / x-captapi-source (native|extended). Envelope timings{serpMs,hydrateMs,hydrateAttempts,discoveryMs,totalMs,path} exposes per-stage latency. Set client timeouts ≥130s until typical searches stay under 60s.",
    platformLimits: [
      "Facebook/SERP discovery can return past events. Use upcoming=true (sets from=today UTC) or from=YYYY-MM-DD for a forward window, or filter client-side on isPast — same pattern as playCount absence on Spotify search.",
      "timezone is a real IANA zone or null — never Etc/GMT. Prefer location.latitude/longitude → IANA when coords exist.",
      "location is a geo filter (timezone / city / coords near the place) — not a required substring of the event title. Most London venues do not contain \"London\" in their name.",
      "Client timeouts ≥130s recommended — native path hydrates event pages (timings.hydrateMs is usually the dominant stage).",
    ],
  },
  {
    slug: "facebook-event-details",
    name: "Facebook Event Details API",
    shortName: "Event Details",
    category: "details",
    method: "GET",
    path: "/v1/facebook/event-details",
    credits: 2,
    tagline:
      "Get a Facebook event — title, local start/end, timezone, place, host id, and attendance when exposed.",
    longDescription:
      "Paste a Facebook event URL and get clean JSON using the shared Event shape: title, description, startDate/endDate as ISO with the host timezone offset (calendar day matches startTime), IANA timezone resolved from venue coordinates when present (else the display-sentence abbreviation — GMT→Europe/London; never Etc/*; null when unknown), duration, eventType (discovery category) + visibility (public|private|…), location{name,city,latitude,longitude,countryCode} (fixed key set — null when unknown), organizers[{id,name,url,verified}], categories, ticketsUrl, and going/interested counts when Facebook exposes them on the logged-out hydrate. Flat 2 credits per call.",
    platformLimits: [
      "timezone is never an Etc/* fixed-offset stand-in. lat/lng → IANA when coords exist; otherwise null.",
      "location always has name, city, latitude, longitude, countryCode — null when Facebook omits them.",
    ],
  },
  {
    slug: "facebook-profile-events",
    name: "Facebook Profile Events API",
    shortName: "Profile Events",
    category: "list",
    method: "GET",
    path: "/v1/facebook/profile-events",
    credits: 2,
    tagline:
      "List a Facebook Page's events — local startDate, timezone, venue. 2 credits.",
    longDescription:
      "Pass a Facebook Page URL and get that page's /events list as clean JSON using the same Event shape as Event Search / Event Details — every field present, null when the profile card omits it (description, endDate, duration, image, organizers, ticketsUrl, categories, …). startDate is ISO with host offset (year resolved from yearless cards like \"Tue, Aug 4 at 8:00 PM EDT\"); startTime always includes the year; eventType is the discovery category when known; visibility is public|private|… (not PUBLIC_TYPE). Envelope includes source (native|extended) for the fetch path. Billing: flat 2 credits on every successful call.",
  },
];

const TWITTER: Spec[] = [
  {
    slug: "twitter-tweet-details",
    name: "Twitter/X Tweet Details API",
    shortName: "Tweet Details",
    category: "details",
    method: "GET",
    path: "/v1/twitter/tweet-details",
    credits: 1,
    tagline:
      "One tweet as JSON — text, author (followers), likes/replies/retweets/quotes, media, ISO publishedAt.",
    longDescription:
      "Paste a tweet URL and get clean JSON using the same tweet contract as Search and User Tweets: text, language, ISO-8601 publishedAt, author (username, displayName, verified, profileImage, followers when exposed), engagement always shaped as {views,likes,replies,retweets,quotes,bookmarks} (null when Twitter omits a metric), isReply / isRetweet, hashtags[], and media[]. Guest GraphQL TweetResultByRestId fills views/bookmarks when available; otherwise we hydrate retweets/quotes/followers from the popular timeline / profile. Flat 1 credit per call.",
    delivers: [
      "Same engagement{} shape as search (6 keys; null when omitted)",
      "ISO-8601 publishedAt",
      "author.followers + isRetweet / hashtags[] / media[]",
      "Flat 1 credit per call",
    ],
  },
  {
    slug: "twitter-transcript",
    name: "Twitter/X Transcript API",
    shortName: "Transcript",
    category: "transcript",
    method: "GET",
    path: "/v1/twitter/transcript",
    credits: 1,
    tagline:
      "Tweet text as a transcript — timingSource none (not Whisper). Flat 1 credit.",
    longDescription:
      "Paste a public tweet URL and get the tweet body as structured text. timingSource is always \"none\" today — syndication text only, not Whisper/captions. When timingSource is \"none\", segment start/duration/timestamp are omitted (returned only when timingSource is \"captions\"). Paragraph-split transcriptSegments include index, wordCount, charStart/charEnd; estimatedReadSeconds is a top-level 200 wpm estimate — never inside duration. Flat 1 credit.",
  },
  {
    slug: "twitter-profile",
    name: "Twitter/X Profile API",
    shortName: "Profile",
    category: "channel",
    method: "GET",
    path: "/v1/twitter/profile",
    credits: 1,
    tagline:
      "X profile: verified + blue/legacy/identity, displayName, tipjar→contact{}, expanded website, createdAt.",
    longDescription:
      "Paste a profile URL or @handle and get clean JSON. Canonical profile core: platform, id, handle, url, displayName, bio, avatar, banner, followers, following, postCount, verified, createdAt — plus deprecated aliases username/name/profileImage/bannerImage/tweetCount for one release. Verification is three independent bits — isBlueVerified (paid blue), isLegacyVerified (old celebrity check), isIdentityVerified — plus aggregate verified (always present), verification{reason,verifiedSince,verifiedType}, and affiliate{description,url,badgeUrl}. Trust signals: fastFollowers / normalFollowers (X's own suspicious-follower split), possiblySensitive, withheldInCountries. Outreach: tipjarSettings + contact{emails,paymentHandles,links}, website as expanded URL (not raw t.co), and bioUrls[] with expandedUrl. Also listedCount, mediaCount, likesCount, pinnedTweetIds, highlightedTweets. Flat 1 credit. Pass cacheMaxAge=1d|3d|7d|14d|30d (envelope cached + cachedAt).",
    delivers: [
      "verified + isBlueVerified ≠ isLegacyVerified ≠ isIdentityVerified",
      "displayName (+ name for compatibility)",
      "contact{emails,paymentHandles,links} from tipjar + bio",
      "website / bioUrls expanded (not t.co) + ISO createdAt",
    ],
  },
  {
    slug: "twitter-user-tweets",
    name: "Twitter/X User Tweets API",
    shortName: "User Tweets",
    category: "list",
    method: "GET",
    path: "/v1/twitter/user-tweets",
    credits: 2,
    tagline:
      "Most popular public tweets from a Twitter/X profile (~100 cap) — not chronological. Text, author, engagement, hashtags, media. Flat 2 credits.",
    longDescription:
      "Pass a profile URL or @handle and get the tweets Twitter's public timeline embed exposes as clean JSON. Important: this is not a chronological or latest feed — Twitter publicly returns on the order of ~100 of the account's most popular posts (same limit ScrapeCreators documents). Do not use this endpoint to detect new tweets. Each result uses the same tweet contract as Search / Tweet Details: ISO-8601 publishedAt, author (id when exposed, username, displayName, followers, verified, avatar), engagement always shaped as {views,likes,replies,retweets,quotes,bookmarks} (the timeline embed usually leaves views and bookmarks null), isReply / isRetweet / isQuote, conversationId, source when present, hashtags[] (always present, may be empty), and media[]. Flat 2 credits per call. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.",
    platformLimits: [
      "Twitter's public timeline embed returns on the order of ~100 of the account's most popular tweets — not a chronological or latest feed. Do not use this endpoint to detect new tweets.",
    ],
    delivers: [
      "Most popular public tweets (~100 Twitter cap) — not latest/chronological",
      "ISO-8601 publishedAt (same parser as tweet-details)",
      "engagement{} with 6 keys (views/bookmarks often null on this surface)",
      "hashtags[] + media[] (empty arrays when none)",
      "conversationId / source / isQuote when Twitter exposes them",
      "Flat 2 credits per call",
    ],
  },
  {
    slug: "twitter-search",
    name: "Twitter/X Search API",
    shortName: "Search",
    category: "search",
    method: "GET",
    path: "/v1/twitter/search",
    credits: 2,
    tagline:
      "Search public tweets on X — SC has no search endpoint. Six engagement metrics + ISO dates. Flat 2 credits.",
    longDescription:
      "Pass a keyword or phrase and get matching public tweets as clean JSON. Captapi advantage: ScrapeCreators does not ship a Twitter search endpoint. Each result uses the shared tweet contract: ISO-8601 publishedAt, author (username, displayName, followers, verified, avatar), engagement{views,likes,replies,retweets,quotes,bookmarks}, isReply / isRetweet, hashtags[] (always present), and media[]. Ideal for topic monitoring and brand listening on the first page of Top results (limit up to 200; cursor / since-until filters are on the backlog). Flat 2 credits per call. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.",
    delivers: [
      "No SC equivalent — Captapi-only Twitter search",
      "ISO-8601 publishedAt + engagement 6-key shape",
      "hashtags[] always present (empty when none)",
      "Flat 2 credits per call",
    ],
  },
  {
    slug: "twitter-community",
    name: "Twitter/X Community API",
    shortName: "Community",
    category: "details",
    method: "GET",
    path: "/v1/twitter/community",
    credits: 1,
    tagline:
      "X Community metadata — ISO createdAt, flat creator handle, isNsfw + bannerImage (SC gaps), rules[].",
    longDescription:
      "Paste an X community URL (x.com/i/communities/ID) or community ID — not a tweet URL — and get clean JSON: name, description, memberCount, ISO-8601 createdAt (.000Z), creator as a flat handle (not nested creator_results), joinPolicy, isNsfw, bannerImage, and rules[{name,description}]. isNsfw and bannerImage are Captapi extras vs ScrapeCreators. Pair with Community Tweets to list posts. Flat 1 credit.",
    delivers: [
      "ISO createdAt + flat creator handle",
      "isNsfw + bannerImage (not in SC)",
      "rules[{name, description}] without GraphQL noise",
      "Flat 1 credit per call",
    ],
  },
  {
    slug: "twitter-community-tweets",
    name: "Twitter/X Community Tweets API",
    shortName: "Community Tweets",
    category: "list",
    method: "GET",
    path: "/v1/twitter/community-tweets",
    credits: 2,
    tagline:
      "Posts in an X Community — same 6-metric tweet shape as search. Flat 2 credits.",
    longDescription:
      "Pass an X community URL (x.com/i/communities/ID) or community ID — not a tweet/status URL — and get recent posts as clean JSON. Response includes url + communityId + communityName + memberCount (so you often skip a second Community call) plus tweets[] using the shared contract: ISO-8601 publishedAt, engagement{views,likes,replies,retweets,quotes,bookmarks}, hashtags[], media[]. Flat 2 credits (same guest surface as Search). Pass cache=true for the 24h shared cache.",
    delivers: [
      "communityName + memberCount + community url/id",
      "Same engagement 6-key shape + ISO publishedAt as search",
      "Flat 2 credits",
      "hashtags[] + media[] always present on each tweet",
    ],
  },
];

const REDDIT: Spec[] = [
  { slug: "reddit-subreddit-posts", name: "Reddit Subreddit Posts API", shortName: "Subreddit Posts", category: "list", method: "GET", path: "/v1/reddit/subreddit-posts", credits: 2, tagline: "List posts from a subreddit with sort, timeframe, and cursor pagination — title, score, upvote ratio, flair, and more.", longDescription: "Pass a subreddit URL or r/name and get its posts as clean JSON. Choose sort (best/hot/new/top/rising) and, for top, a timeframe (hour/day/week/month/year/all). Each post includes title, selftext, author + authorFullname, upvotes/score/downs/upvoteRatio, comment count, subscriberCount, isVideo, flair, nsfw, thumbnail, and ISO publishedAt. Cursor pagination via nextCursor + hasMore. Flat 2 credits." },
  { slug: "reddit-post-details", name: "Reddit Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/reddit/post-details", credits: 1 , tagline: "Get a Reddit post — title, body, score, comments count, subreddit, and author as structured JSON.", longDescription: "Paste a Reddit post URL and get the post as clean JSON: title, body text, score, comment count, subreddit, author, and flair when available. Flat 1 credit per call." },
  {
    slug: "reddit-post-comments",
    name: "Reddit Post Comments API",
    shortName: "Post Comments",
    category: "comments",
    method: "GET",
    path: "/v1/reddit/post-comments",
    credits: 2,
    tagline:
      "Flat Reddit comment threads with depth/parentId, ISO timestamps, score, and the parent post in one call.",
    longDescription:
      "Fetch comments on a Reddit post as a flat list with depth and parentId (easy to store, rebuild the tree when you need it). publishedAt is ISO 8601 UTC. Each comment includes score/downs and authorFullname (t2_…) when Reddit exposes them. The response also includes the parent post (title, score, upvoteRatio, subscriberCount) plus hasMore when more comments exist beyond the limit. Flat 2 credits per call. Max 500 comments per request.",
  },
  {
    slug: "reddit-post-transcript",
    name: "Reddit Post Transcript API",
    shortName: "Post Transcript",
    category: "transcript",
    method: "GET",
    path: "/v1/reddit/post-transcript",
    credits: 2,
    tagline:
      "Reddit discussion as text — title/body/comments segments, timingSource none. Flat 2 credits.",
    longDescription:
      "Paste a Reddit post URL and get the discussion as structured text: title, body, and comments as transcriptSegments (speaker labeled). timingSource is always \"none\" today — discussion text has no caption track. When timingSource is \"none\", segment start/duration/timestamp are omitted (returned only when timingSource is \"captions\"). Each segment has index, wordCount, charStart/charEnd into transcript. estimatedReadSeconds is a top-level 200 wpm estimate only — never inside duration. Flat 2 credits.",
  },
  {
    slug: "reddit-search",
    name: "Reddit Search API",
    shortName: "Search",
    category: "search",
    method: "GET",
    path: "/v1/reddit/search",
    credits: 2,
    tagline:
      "Reddit site-wide post search — sort + timeframe + cursor, score/upvoteRatio, authorFullname. Flat 2 credits.",
    longDescription:
      "Pass a keyword and get matching public posts across Reddit as clean JSON. Sort with sort=relevance|new|top|hot|comments (alias comment_count); for top/comments use timeframe=hour|day|week|month|year|all (default all). The response echoes sort and timeframe. Each result includes id/name (t3_…), title, text, subreddit, author + authorFullname (t2_…), Reddit's authoritative score (not ups−downs), upvotes/downs/upvoteRatio, scoreHidden when Reddit hides the score, comments, subscriberCount, totalAwardsReceived, isVideo, ISO publishedAt, flair, nsfw, and thumbnail. Cursor pagination via nextCursor/hasMore. This endpoint returns posts only — not a comments[] or media[] search surface. Flat 2 credits. Pass cache=true for the 24h shared cache.",
    delivers: [
      "sort + timeframe echo (relevance/new/top/hot/comments × hour…all)",
      "authorFullname (t2_…) + authoritative score + upvoteRatio + scoreHidden",
      "isVideo + totalAwardsReceived; flair/nsfw/thumbnail; subscriberCount",
      "Cursor pagination (nextCursor + hasMore); ISO publishedAt",
    ],
    platformLimits: [
      "Posts only (kind=t3). ScrapeCreators returns posts + comments[] + media[] from a richer search surface — comment brand listening needs a separate comments path (not this endpoint).",
      "Public JSON almost always zeros downs. New posts with hide_score can show score/upvotes 0 while upvoteRatio is still set — use scoreHidden and do not treat score 0 as worthless until the hide window ends.",
    ],
  },
  {
    slug: "reddit-subreddit-details",
    name: "Reddit Subreddit Details API",
    shortName: "Subreddit Details",
    category: "details",
    method: "GET",
    path: "/v1/reddit/subreddit-details",
    credits: 1,
    tagline:
      "Subreddit card — id (t5_…), members, activeUsers, rules[], ISO createdAt, nsfw/type. Flat 1 credit.",
    longDescription:
      "Pass a subreddit URL, r/name, or bare name (case-insensitive — AskReddit and askreddit both resolve; response name is Reddit's canonical casing) and get clean JSON: stable id (t5_…), name, title, public description, members, activeUsers (accounts currently online — Reddit active_user_count, not weekly uniques), category (advertiser niche), language, type (public/restricted/private), ISO-8601 createdAt, nsfw, submitText, rules[{name,description,kind,violationReason,priority}] from about/rules, icon, and banner. Flat 1 credit. Use it to map communities before sampling posts or comments.",
    delivers: [
      "Stable id (t5_…) + canonical name/url",
      "members + activeUsers (currently online)",
      "rules[] from Reddit about/rules + submitText",
      "ISO createdAt, nsfw, type, language, category, icon/banner",
    ],
    platformLimits: [
      "activeUsers is Reddit's live online count, not weekly active users. Treat ScrapeCreators weekly_active_users with the same caution when the ratio looks unrealistic vs members.",
      "rules[] is empty when the subreddit has no configured rules endpoint payload (rare on large communities).",
    ],
  },
  { slug: "reddit-subreddit-search", name: "Reddit Subreddit Search API", shortName: "Subreddit Search", category: "search", method: "GET", path: "/v1/reddit/subreddit-search", credits: 2, tagline: "Search inside one subreddit — same sort/timeframe and post fields as site-wide Search. Flat 2 credits.", longDescription: "Pass a subreddit (r/name) and a query to search posts inside that community only. Same sort (relevance/new/top/hot/comments), timeframe, cursor pagination, and result fields as Reddit Search (authorFullname, score/upvoteRatio, subscriberCount, isVideo, flair, …). Flat 2 credits." },
];

const THREADS: Spec[] = [
  {
    slug: "threads-profile",
    name: "Threads Profile API",
    shortName: "Profile",
    category: "channel",
    method: "GET",
    path: "/v1/threads/profile",
    credits: 1,
    tagline:
      "Threads profile — displayName, private/isPrivate, bioLinks (Meta verified), isThreadsOnlyUser, transparencyLabel, bioFragments, HD avatars (1 credit).",
    longDescription:
      "Pass a Threads profile URL or @handle and get the public profile as clean JSON. Canonical core: platform, id, handle, url, displayName, bio, avatar, followers, verified — plus deprecated username/name/profileImage aliases for one release. Also: isThreadsOnlyUser (Threads-only vs Instagram-linked — pair with Instagram fbid for an IG↔FB↔Threads identity chain when Meta exposes it), private/isPrivate, bioLinks[] ({url, verified, linkId} — verified means Meta confirmed the bio link), bioFragments[] (parsed plaintext/link/mention/tag pieces from text_app_biography), transparencyLabel (state-affiliated media etc.), profileImageVersions[] ({url,width,height}), and hasOnboarded. Flat 1 credit. following and post counts are not publicly exposed on this surface (same gap as ScrapeCreators).",
    delivers: [
      "Canonical displayName/avatar (+ name/profileImage aliases), bio, followers, verified",
      "private / isPrivate always present when Meta exposes privacy",
      "bioLinks[] with Meta verified + linkId; bioFragments[] when hydrated",
      "isThreadsOnlyUser + transparencyLabel for cross-platform / brand-safety signals",
    ],
    platformLimits: [
      "following and postCount are not publicly exposed on Threads profile hydrate (same gap ScrapeCreators documents).",
      "isThreadsOnlyUser and transparencyLabel are often null on logged-out web hydrate even when the account has a value in Meta's app GraphQL.",
    ],
  },
  {
    slug: "threads-user-posts",
    name: "Threads User Posts API",
    shortName: "User Posts",
    category: "list",
    method: "GET",
    path: "/v1/threads/user-posts",
    credits: 2,
    tagline:
      "Recent Threads posts — engagement{views,likes,replies,reposts,quotes}, threadId/isReply. Flat 2 credits.",
    longDescription:
      "Pass a Threads profile URL or @handle and get recent public posts as clean JSON: id, code, url, text, ISO publishedAt, threadId / replyToId / isReply / isQuote (rebuild multi-part Threads), top-level author{} (full card once — per-post rows keep slim author without repeating profileImage), engagement{views,likes,replies,reposts,quotes} (views null when Meta omits them on hydrate), and media[] (carousel-aware). Flat 2 credits (same soft-cap surface ScrapeCreators uses). Pass cache=true for the 24h shared cache.",
    delivers: [
      "engagement with views + likes/replies/reposts/quotes",
      "threadId / replyToId / isReply / isQuote for multi-part Threads",
      "Top-level author{} once (no repeated CDN avatar on every row)",
      "Flat 2 credits",
    ],
    platformLimits: [
      "Only the last ~20–30 posts are publicly visible on this surface (Meta soft-cap on profile hydrate / logged-out feeds). limit=100 will not return 100 — asking above ~30 just returns what Meta exposes.",
    ],
  },
  {
    slug: "threads-post-details",
    name: "Threads Post Details API",
    shortName: "Post Details",
    category: "details",
    method: "GET",
    path: "/v1/threads/post-details",
    credits: 1,
    tagline:
      "Threads post — engagement (views when exposed), comments[], relatedPosts[], threadId/isReply. Flat 1 credit.",
    longDescription:
      "Pass a Threads post URL and get one enriched post as clean JSON: id, code, url, text, ISO publishedAt, author{}, engagement{views,likes,replies,reposts,quotes}, threadId/replyToId/isReply/isQuote, media[], plus comments[] (inline replies when Meta embeds them on the permalink) and relatedPosts[] (BarcelonaLoggedOutRelatedPosts — algorithmic related threads, no extra call). Flat 1 credit. This is not an alias of user-posts: relatedPosts and comments are only on this endpoint.",
    delivers: [
      "Same post card as user-posts + engagement.views when Meta exposes it",
      "comments[] inline (empty array when logged-out hydrate omits the reply tree)",
      "relatedPosts[] from Meta's logged-out related module — no second request",
      "threadId / replyToId / isReply / isQuote",
    ],
    platformLimits: [
      "Logged-out Threads permalink HTML usually embeds relatedPosts but not the public reply tree. comments[] is then [] with a stable key — not a missing field. ScrapeCreators often fills comments via a deeper GraphQL path we do not use on this surface.",
      "engagement.views is often null on web hydrate even when the Threads app shows a view count (Meta's enable_view_counts flag is off for many logged-out renders).",
    ],
  },
  {
    slug: "threads-search",
    name: "Threads Post Search API",
    shortName: "Post Search",
    category: "search",
    method: "GET",
    path: "/v1/threads/search",
    credits: 2,
    tagline:
      "Threads keyword search — posts with engagement + media. Flat 2 credits.",
    longDescription:
      "Pass a keyword and get public Threads posts from Meta's Top SERP hydrate as clean JSON: id, code, url, text, ISO publishedAt, author{username,displayName,verified}, engagement{views,likes,replies,reposts,quotes}, threadId/isReply/isQuote, and media[]. Flat 2 credits (parity with twitter/search). There is no sort or date filter — Meta ranks the page, and older or engagement-farm posts can appear near the top. Pass cache=true for the 24h shared cache (0 credits on hit).",
    delivers: [
      "Posts from Meta Top SERP for your keyword",
      "id/code/url, text, ISO publishedAt",
      "engagement{views,likes,replies,reposts,quotes} + media[]",
      "Flat 2 credits",
    ],
    platformLimits: [
      "No sort or since/until — Meta's default Top ranking only. Results often mix recent and months-old posts.",
      "Engagement-farm / giveaway spam can rank first (high replies vs likes). Captapi does not filter spam.",
      "Native hydrate soft-caps around ~20–25 posts per page.",
    ],
  },
  {
    slug: "threads-search-users",
    name: "Threads Search Users API",
    shortName: "Search Users",
    category: "search",
    method: "GET",
    path: "/v1/threads/search-users",
    credits: 1,
    tagline:
      "Threads user discovery from keyword search — id, handle, avatar, verified. Flat 1 credit.",
    longDescription:
      "Pass a keyword and get distinct Threads authors who appear in Meta's keyword post search as clean JSON: id (pk when embedded), username, displayName, url, verified, profileImage, and followers (usually null on this surface — call Threads Profile for counts). Flat 1 credit (parity with TikTok search-users and ScrapeCreators). This is not a semantic people-search: users are unique authors of posts that matched the keyword on Top SERP, so handles may not contain the query. Pass cache=true for the 24h shared cache (0 credits on hit).",
    delivers: [
      "Distinct authors from keyword post search",
      "id + username + displayName + url + verified",
      "profileImage when Meta embeds it; followers keyed (often null)",
      "Flat 1 credit",
    ],
    platformLimits: [
      "Not a Users-tab GraphQL people search — authors are derived from post SERP hits. Handle/bio may not mention your query.",
      "followers is usually null here; use /threads/profile for follower counts and bioLinks.",
    ],
  },
];

const BLUESKY: Spec[] = [
  {
    slug: "bluesky-profile",
    name: "Bluesky Profile API",
    shortName: "Profile",
    category: "channel",
    method: "GET",
    path: "/v1/bluesky/profile",
    credits: 1,
    tagline:
      "Bluesky profile — handle, did, bio, counts, banner, verification{}, labels[], and associated{} (1 credit).",
    longDescription:
      "Give a Bluesky profile URL, @handle, or handle and get the public AT Protocol profile as clean JSON. Canonical profile core (same keys on every Captapi profile endpoint): platform, id, handle, url, displayName, bio, avatar, banner, followers, following, postCount, verified, createdAt. Bluesky also returns did (same as id), deprecated aliases name/posts for one release, indexedAt (AppView last indexed the profile record — not last activity), pinnedPost{uri,cid,rkey} when the account featured a post, joinedViaStarterPack when present, verified + verification{verifications[{issuer, issuerHandle, issuerDisplayName, uri, isValid, createdAt}], verifiedStatus, trustedVerifierStatus} (issuer DIDs resolved to handle/display name), moderation labels[{src, uri, cid, val, neg, createdAt, expiresAt}], and associated{lists, feedgens, starterPacks, labeler, chat, activitySubscription} so you can tell feed/labeler service accounts from people. Accepts cache / cacheMaxAge like other profile trust-layer endpoints. Flat 1 credit per call.",
    delivers: [
      "Canonical core: displayName, avatar, banner, postCount (+ name/posts aliases)",
      "DID + verification{} with issuerHandle / issuerDisplayName resolved",
      "pinnedPost + joinedViaStarterPack when AppView exposes them",
      "Moderation labels[] (full shape) and associated{lists, feedgens, starterPacks, labeler}",
    ],
  },
  {
    slug: "bluesky-user-posts",
    name: "Bluesky User Posts API",
    shortName: "User Posts",
    category: "list",
    method: "GET",
    path: "/v1/bluesky/user-posts",
    credits: 3,
    creditsPerResult: 0.1,
    tagline:
      "Author feed — posts and reposts (isRepost marked), quote/external/images embeds, opaque cursor.",
    longDescription:
      "Send a Bluesky profile URL, @handle, or handle and get that account's public author feed (app.bsky.feed.getAuthorFeed) as clean JSON — original posts and reposts. Reposts keep the original author{} and engagement; they are marked isRepost=true with repostedBy{handle,displayName,did,avatar} and repostedAt so analytics do not credit someone else's likes to the profile you queried. Pass includeReposts=false to drop reposts. Optional filter maps to Bluesky's feed filter (posts_with_replies | posts_no_replies | posts_with_media | posts_and_author_threads | posts_with_video) — that controls replies/media/threads, not reposts. Each row: uri/url/cid, text, publishedAt, indexedAt, author{}, engagement{likes,reposts,replies,quotes}, and embed as one of type external | images | video | quote (quotes include uri/url/text/author — never a raw lexicon NSID). Rows are ordered by effective timestamp — repostedAt for reposts, publishedAt otherwise — matching Bluesky's author-feed order; re-sorting by publishedAt alone yields a different feed. nextCursor is Bluesky's opaque cursor (do not derive it from publishedAt). Billed ~0.1 credits per returned row (limit max 100). Pass cache=true for the 24h shared cache.",
    delivers: [
      "Author feed: originals + reposts with isRepost / repostedBy / repostedAt",
      "includeReposts=false and Bluesky filter= for replies/media/threads",
      "Normalized embeds: external | images | video | quote (with text/author/url)",
      "Opaque nextCursor from AppView (not publishedAt)",
      "~0.1 credits/row; limit up to 100",
    ],
    platformLimits: [
      "getAuthorFeed includes reposts by default — check isRepost before averaging engagement on author.handle.",
      "filter does not exclude reposts; use includeReposts=false for that.",
      "Ordered by effective timestamp (repostedAt for reposts, else publishedAt) — Bluesky author-feed order; re-sorting by publishedAt alone changes the feed.",
      "Always pass nextCursor through — do not invent a cursor from publishedAt.",
    ],
  },
  {
    slug: "bluesky-post-details",
    name: "Bluesky Post Details API",
    shortName: "Post Details",
    category: "details",
    method: "GET",
    path: "/v1/bluesky/post-details",
    credits: 1,
    tagline:
      "Post thread via getPostThread — nested replies[], facet links/mentions/hashtags, rich author (1 credit).",
    longDescription:
      "Pass a Bluesky post URL and get the public thread (app.bsky.feed.getPostThread) — not a duplicate of a user-posts row. Beyond the list card you get: nested replies[] with per-reply author/text/engagement (depth, default 1, max 6), parentUri/rootUri/isReply so a reply is never mistaken for a root post, facet-derived links[] (full URIs — Bluesky truncates long URLs inside text), mentions[] with did, and hashtags[], post-level labels[] + langs[], and a rich author{handle,displayName,did,avatar,createdAt,labels[],verification{},verified} matching bluesky/profile (including !no-unauthenticated compliance labels). Embeds use the same normalized type namespace as user-posts (external | images | video | quote). Flat 1 credit. This is the only Captapi surface that returns Bluesky reply content.",
    delivers: [
      "Nested replies[] from getPostThread (depth 0–6)",
      "Facet links[] / mentions[{did}] / hashtags[] — not regex over truncated text",
      "Rich author: verification{}, labels[], createdAt",
      "parentUri / rootUri / isReply + post labels[] + langs[]",
    ],
    platformLimits: [
      "depth defaults to 1; large threads can return many reply rows in one credit.",
      "Bluesky has no view/play metric — engagement is likes/reposts/replies/quotes only.",
    ],
  },
];

const PINTEREST: Spec[] = [
  { slug: "pinterest-pin-details", name: "Pinterest Pin Details API", shortName: "Pin Details", category: "details", method: "GET", path: "/v1/pinterest/pin-details", credits: 1, tagline: "Get a Pinterest pin — title, description, link, board, origin creator, and engagement as structured JSON.", longDescription: "Pass a Pinterest pin URL and get clean JSON: title, description, seoAltText, link/destinationUrl, createdAt (ISO-8601), board{name,url,pinCount,followers}, author (board pinner), originAuthor (native creator / original uploader), saves plus repinCount/shareCount/reactionCount, image plus images{236x,564x,originals}. Flat 1 credit. Fields Pinterest does not expose on a given pin stay omitted/null." },
  { slug: "pinterest-user-pins", name: "Pinterest User Pins API", shortName: "User Pins", category: "list", method: "GET", path: "/v1/pinterest/user-pins", credits: 13, creditsPerResult: 0.5 },
  { slug: "pinterest-search", name: "Pinterest Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/pinterest/search", credits: 13, creditsPerResult: 0.5 },
  {
    slug: "pinterest-board",
    name: "Pinterest Board API",
    shortName: "Board",
    category: "list",
    method: "GET",
    path: "/v1/pinterest/board",
    credits: 13,
    creditsPerResult: 0.5,
    tagline:
      "Pins on a Pinterest board — saves, imageOriginal, destinationUrl, top-level author. ~0.5 credits/pin.",
    longDescription:
      "Pass a Pinterest board URL (.../username/board-name/ — not a /pin/ URL) and get that board's public pins as clean JSON. Response includes board + boardName, a top-level author{} (pinner card with followers, once), and pins[] with id/url, title when Pinterest exposes it, description, destinationUrl (outbound link), domain, saves (the primary Pinterest engagement metric from aggregated_pin_data), image (display CDN size) + imageOriginal (/originals/) + images{236x,564x,originals,…}, and a slim per-pin author{username,displayName}. Billed about 0.5 credits per returned pin (min 2). Native pidgets soft-caps around 50–100 pins with no cursor yet — larger boards need a follow-up surface.",
    delivers: [
      "saves (repin metric) + destinationUrl + domain",
      "image + imageOriginal + images{} size map",
      "Top-level author{} (followers); slim per-pin author",
      "title when exposed; board + boardName",
    ],
    platformLimits: [
      "Pass a board URL (.../user/board-slug/), not a pin URL. Pin URLs belong on /pinterest/pin-details.",
      "Native board hydrate soft-caps ~50–100 pins. No cursor/hasMore yet — limit alone cannot page a 500+ pin board.",
      "title / richPinType are often null on the board pidgets list; pin-details hydrates richer pin metadata.",
    ],
  },
  {
    slug: "pinterest-user-boards",
    name: "Pinterest User Boards API",
    shortName: "User Boards",
    category: "list",
    method: "GET",
    path: "/v1/pinterest/user-boards",
    credits: 13,
    creditsPerResult: 0.5,
    tagline:
      "Boards on a Pinterest profile — pinCount, coverImage (474x), privacy, sections. Board followers when scoped.",
    longDescription:
      "Pass a Pinterest profile URL or username and get that profile's public boards as clean JSON. Every board row uses the same shape: id, name, url, description, privacy, pinCount, followers, sectionCount, coverImage (prefers Pinterest's 474x HD cover), createdAt (ISO-8601 UTC), and owner{username,displayName}. followers is the board-scoped follower count when available — Pinterest's logged-out board.follower_count is account-scale (identical on every board) and is never echoed here (null until a board-scoped source is wired). Billed about 0.5 credits per returned board (min 2). No cursor yet.",
    delivers: [
      "Stable board row shape (same keys on every item)",
      "pinCount + sectionCount + privacy + description",
      "coverImage (474x HD when Redux exposes it)",
      "createdAt ISO-8601 + owner{username,displayName}",
      "followers only when board-scoped (else null — never account count)",
    ],
    platformLimits: [
      "Board-scoped followers are not on the logged-out /_boards/ hydrate — followers is null rather than a misleading account twin. ScrapeCreators exposes follower_count per board from a different path.",
      "No cursor/hasMore yet — limit alone cannot page a profile with hundreds of boards.",
      "Catalog list price is ~0.5 credits/board (min 2); ScrapeCreators bills 1 credit flat for this surface.",
    ],
  },
];

const LINKEDIN: Spec[] = [
  {
    slug: "linkedin-profile",
    name: "LinkedIn Profile API",
    shortName: "Profile",
    category: "channel",
    method: "GET",
    path: "/v1/linkedin/profile",
    credits: 2,
    tagline:
      "LinkedIn person profile with experience[], education[], similarProfiles[] — masked guest text becomes restricted:true.",
    longDescription:
      "Public LinkedIn person profile as clean JSON for B2B sales intel. Core identity: name, headline, about, followers, currentCompany — about from the real bio (JSON-LD), never LinkedIn's og:description SEO blurb. connections only when LinkedIn exposes a trustworthy count (logged-out LinkedIn often omits it — a platform limit, not a Captapi gap). B2B sections when upstream exposes them: experience[], education[], similarProfiles[] (people-also-viewed discovery graph), plus projects / publications / articles / activity / recommendations / certifications / languages. Guest-masked asterisk descriptions (******* …) are returned as description:null with restricted:true — not as fake star text. Native HTML bills 1 credit; Apify section enrich is 2.",
    delivers: [
      "experience[] + education[] for B2B qualification",
      "similarProfiles[] discovery graph",
      "restricted:true instead of ******* masking",
      "SEO-clean about + honest connections nullability",
    ],
  },
  {
    slug: "linkedin-company",
    name: "LinkedIn Company API",
    shortName: "Company",
    category: "channel",
    method: "GET",
    path: "/v1/linkedin/company",
    credits: 2,
    tagline:
      "Company page for B2B intel — specialties, similarPages, size/founded, slogan, cover. Native 1 / enrich 2.",
    longDescription:
      "Pass a LinkedIn company URL and get B2B-ready JSON: name, industry, description, website, followers, employeeCount, size (e.g. 10,001+ employees), founded, organizationType (Public Company / …), specialties[], headquarters + location{city,state,country}, slogan, coverImage, logo, similarPages[{name,link,image}] (discovery graph — same pattern as profile similarProfiles), funding when upstream exposes rounds/investors, and employees[] for featured people when LinkedIn exposes them (guest pages usually return []). type stays the entity discriminator \"company\" — organizationType is the About \"Type\" field. Native guest HTML bills 1 credit; Apify enrich for slogan/cover (and rare funding) bills 2. Recent posts live on /linkedin/company-posts, not inlined here.",
    delivers: [
      "specialties[] + organizationType + founded + size",
      "similarPages[] discovery graph (name/link)",
      "location{city,state,country} + headquarters string",
      "slogan + coverImage when enrich fills them",
      "employeeCount (headcount); employees[] featured people when exposed",
      "funding object when LinkedIn/Apify expose rounds — else null",
    ],
    platformLimits: [
      "Guest /company/{slug}/ does not expose funding rounds or featured employee cards — funding and employees[] stay null/[] unless an enrich path fills them. ScrapeCreators often ships both.",
      "similarPages images are often omitted on guest HTML (name + link still return).",
      "Inline posts[] are not on this endpoint — use /v1/linkedin/company-posts.",
      "Apify input must be identifier:[slug]. Legacy company/url shapes could scrape the wrong company.",
    ],
  },
  { slug: "linkedin-post-details", name: "LinkedIn Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/linkedin/post-details", credits: 1 , tagline: "Get a LinkedIn post — text, author, reactions, and comments count as structured JSON." },
  {
    slug: "linkedin-post-transcript",
    name: "LinkedIn Post Transcript API",
    shortName: "Post Transcript",
    category: "transcript",
    method: "GET",
    path: "/v1/linkedin/post-transcript",
    credits: 1,
    tagline:
      "LinkedIn post text as a transcript — paragraph segments, timingSource none. Flat 1 credit.",
    longDescription:
      "Paste a LinkedIn post/activity URL and get the public post body as structured text: transcript, wordCount, author, publishedAt, and transcriptSegments split on blank-line paragraphs (including NBSP gaps). timingSource is always \"none\" today (native and Apify) — no caption track or Whisper. When timingSource is \"none\", segment start/duration/timestamp are omitted (returned only when timingSource is \"captions\"). Each segment has index, wordCount, charStart/charEnd into transcript. estimatedReadSeconds is a single top-level 200 wpm estimate — never inside duration. Flat 1 credit.",
  },
  {
    slug: "linkedin-company-posts",
    name: "LinkedIn Company Posts API",
    shortName: "Company Posts",
    category: "list",
    method: "GET",
    path: "/v1/linkedin/company-posts",
    credits: 16,
    creditsPerResult: 0.8,
    tagline:
      "Company posts with engagement{likes,comments,reposts} — cursor pages up to 100.",
    longDescription:
      "Pass a LinkedIn company URL and get recent public posts as clean JSON. Each row always includes id, url, text, publishedAt, author{name,url}, and engagement{likes,comments,reposts} (null only when LinkedIn omits that metric — never invented zeros). Homepage JSON-LD often ships text without counts; we hydrate each permalink for reaction/comment totals so analytics and competitor content scoring work. Cursor pagination via nextCursor + hasMore (numeric offset); a null nextCursor means the end of the list (max 100 posts). Native path bills 1 credit; Apify deepen stays ~0.8/result. Pass cache=true for the 24h shared cache.",
    delivers: [
      "engagement{likes,comments,reposts} always keyed",
      "Permalink hydrate when homepage LD omits counts",
      "author{name,url} + activity id",
      "nextCursor + hasMore (hard max 100, documented)",
    ],
    platformLimits: [
      "Reaction breakdown (like/celebrate/love/…) and postType/media carousels are not on this surface yet.",
      "reposts is often null on guest hydrates even when likes/comments fill.",
      "A null nextCursor means the end of the list (max 100 posts).",
    ],
  },
  { slug: "linkedin-search-posts", name: "LinkedIn Search Posts API", shortName: "Search Posts", category: "search", method: "GET", path: "/v1/linkedin/search-posts", credits: 16, creditsPerResult: 0.8 },
];

const RUMBLE: Spec[] = [
  {
    slug: "rumble-video-details",
    name: "Rumble Video Details API",
    shortName: "Video Details",
    category: "details",
    method: "GET",
    path: "/v1/rumble/video-details",
    credits: 1,
    tagline:
      "Rumble video metadata — uniform streams[] with rendition meta, captions[], audioStreams.",
    longDescription:
      "Paste a Rumble video URL and get clean JSON: title, description, views, likes/dislikes/comments (null when Rumble does not expose them — never fake zeros), durationSeconds + durationText, publishedAt, thumbnail, width/height, channel name/url/handle plus channelFollowers and channelVerified, numericId/embedId/shareUrl/embedUrl (real embed id, not the page permalink), captions[{code,language,url,expiresAt}], streams[{url,type,quality,width,height,bitrateKbps,sizeBytes,expiresAt}] built from embed metadata height/bitrate (two 1080p bitrates stay two rows — no fabricated 1081 keys; metadata-less and timeline strips are dropped), audioStreams[] (width/height/quality null — bitrateKbps carries the rate), and thumbnailTrack when Rumble ships a timeline sprite. type is video/mp4 (MIME-style). expiresAt is null when the URL is unsigned and does not expire (typical for video-details progressive files); when a signed CDN query is present it is parsed. The raw quality-keyed media dump is not returned. Flat 1 credit. Pass cache=true for the 24h shared cache.",
    delivers: [
      "Engagement counts stay null when unknown (no fake zeros)",
      "Uniform streams[] keys with real height/bitrate (no junk rows)",
      "Real embedId/embedUrl (page id ≠ embed id on Rumble)",
      "expiresAt null on unsigned progressive URLs (documented)",
    ],
  },
  {
    slug: "rumble-video-transcript",
    name: "Rumble Video Transcript API",
    shortName: "Video Transcript",
    category: "transcript",
    method: "GET",
    path: "/v1/rumble/video/transcript",
    credits: 1,
    tagline:
      "Rumble published captions as timed segments — parses the .vtt from video-details (not speech-to-text).",
    longDescription:
      "Fetches the caption track Rumble already exposes on /video-details (unsigned .vtt URLs), parses cues into segments[{text,startMs,endMs}], and returns the full text. source is always \"captions\". Pass language to require that track (en matches en-auto); mismatch → 404 language_not_available with availableLanguages (never a silent fallback). No tracks → 404 no_captions. 404 costs 0 credits. No STT fallback on this endpoint. Flat 1 credit on success. Segment shape is shared with /v1/youtube/audio-transcript.",
    delivers: [
      "source always \"captions\" on success",
      "Uniform segments[{text,startMs,endMs}] (shared shape)",
      "Rolling auto-caption duplicates collapsed",
      "404 language_not_available / no_captions cost 0",
    ],
  },
  {
    slug: "rumble-channel-videos",
    name: "Rumble Channel Videos API",
    shortName: "Channel Videos",
    category: "list",
    method: "GET",
    path: "/v1/rumble/channel-videos",
    credits: 12,
    creditsPerResult: 0.6,
    tagline:
      "Rumble channel uploads — lean streams[{url,type,expiresAt}]; call video-details for rendition meta.",
    longDescription:
      "List a channel's uploads as clean JSON. Each row: id, url, type (video|short|live), title, channel/channelUrl/channelHandle, views/likes/dislikes/comments, durationSeconds + durationText (same pair as video-details), publishedAt, thumbnail, streams[{url,type,expiresAt}] from signed playback URLs (expiresAt from the JWT exp claim). Per-rendition quality/height/bitrate/sizeBytes require /v1/rumble/video-details — the channel scrape does not ship that metadata. shareUrl. embedUrl/embedId are present only when Rumble exposes a distinct embed id — page permalink ids are never used to invent /embed/{id}/ URLs (those 404). Flat ~0.6 credits per returned video (min 2).",
  },
  {
    slug: "rumble-search",
    name: "Rumble Search API",
    shortName: "Search",
    category: "search",
    method: "GET",
    path: "/v1/rumble/search",
    credits: 12,
    creditsPerResult: 0.6,
    tagline:
      "Rumble keyword search — same video card shape as channel-videos (type, durationSeconds + durationText, UTC publishedAt).",
    longDescription:
      "Search Rumble videos by keyword. Every result has the same key set (null when scrape miss): id, url, type, title, channel/channelUrl/channelHandle/channelVerified, views/likes/dislikes/comments, durationSeconds + durationText, publishedAt UTC (+00:00), thumbnail, isLive, shareUrl. views is null when unknown or impossible (e.g. 0 with likes/comments). Flat ~0.6 credits per returned video (min 2).",
  },
  {
    slug: "rumble-comments",
    name: "Rumble Comments API",
    shortName: "Comments",
    category: "comments",
    method: "GET",
    path: "/v1/rumble/comments",
    credits: 2,
    tagline: "Rumble top-level comments — publishedAt ISO-8601 UTC from title= on the comment time link.",
    longDescription:
      "Paste a Rumble video URL and get top-level comments as clean JSON: id, text, author{name,url,verified}, likes, replyCount, publishedAt (ISO-8601 UTC parsed from a.comments-meta-post-time title=, e.g. Friday, July 17, 2026 08:33 AM -04 — minute precision; relative textContent like 2 weeks ago is never returned). createdAt is not emitted. Flat 2 credits.",
  },
];

const TIKTOK_SHOP: Spec[] = [
  {
    slug: "tiktok-shop-search",
    name: "TikTok Shop Search API",
    shortName: "Shop Search",
    category: "search",
    method: "GET",
    path: "/v1/tiktok-shop/shop-search",
    credits: 2,
    tagline:
      "TikTok Shop keyword search — priced products with sold, rating/reviews, originalPrice/discount, seller id.",
    longDescription:
      "Search TikTok Shop by keyword and get products as clean JSON: id, url, title, price + originalPrice/discount/savings, currency, sold, rating + reviews (always keyed; null when the PDP has no score yet), image, and seller{id,name,url}. top-level region is an echo of the region query param you sent (default US) — market selection, not a creator country and not AI-inferred. price uses the same canonical rule as Product Details: TikTok's promotion minimum sale price across SKUs at fetch time (promos can move between calls). Flat 2 credits per call. Pass cache=true for the 24h shared cache.",
    delivers: [
      "rating + reviews always keyed on every hit",
      "originalPrice + discount + savings (same price rule as Product Details)",
      "seller{id,name,url}",
      "region = request param echo (not AI / no regionSource)",
      "Flat 2 credits",
    ],
    platformLimits: [
      "Native path hydrates each hit via PDP SSR (Shop search HTML is WAF-gated). rating/reviews come from the PDP review_model — new products often have null until TikTok publishes a score.",
      "No page/cursor yet — soft-cap is whatever the SERP+hydrate window returns (limit max 200; you usually get fewer).",
      "TikTok promotion prices are point-in-time; the same product_id can show a different sale price minutes later on Search vs Product Details.",
    ],
  },
  {
    slug: "tiktok-shop-products",
    name: "TikTok Shop Products API",
    shortName: "Shop Products",
    category: "list",
    method: "GET",
    path: "/v1/tiktok-shop/shop-products",
    credits: 2,
    tagline:
      "Store catalog with shopInfo (sold/followers/rating) + products priced with sold, rating, savings.",
    longDescription:
      "Pass a TikTok Shop store URL and get that shop's public catalog as clean JSON — products and the store card from the same SSR call. Top-level shopInfo: sold + formatSold (e.g. 5.6M), reviews, followers, rating, productCount, videoCount, isOfficial + identityLabel (OFFICIAL SHOP), region, logo, storeScores[]. Each products[] row: id/url/slug, title, numeric price + originalPrice + discount + savings (unmasked — not TikTok's $3? strings), currency, sold, rating, reviews, image, seller{id,name,url}. Optional region (default US). Billing: flat 2 credits per call on native SSR (limit does not multiply credits — a 200-cap request that returns ~30 SSR rows still costs 2). Apify fallback (rare) scales ~2.8/result. No cursor/sort_by yet. Non-US coverage depends on TikTok exposing that shop in the selected region — empty results outside the US are often a platform limit, not a Captapi bug.",
    delivers: [
      "shopInfo{sold,formatSold,followers,rating,productCount,isOfficial,…}",
      "Unmasked numeric price / originalPrice / discount / savings",
      "products with sold + rating + reviews always keyed",
      "SEO slug per product",
      "Flat 2 credits on native SSR",
    ],
    platformLimits: [
      "Native soft-caps around ~30 products per store page. No cursor / sort_by (top|new_releases) yet — productCount on shopInfo shows how much of the catalog you are missing.",
      "shop_slogan is often omitted on US store SSR even when ScrapeCreators fills it.",
      "Non-US shop catalog coverage depends on TikTok exposing that shop in the selected region — some shops return empty outside the US even when they appear in shop search. Sorry: this is a TikTok exposure limit we document rather than hide.",
    ],
  },
  {
    slug: "tiktok-shop-product-details",
    name: "TikTok Shop Product Details API",
    shortName: "Product Details",
    category: "details",
    method: "GET",
    path: "/v1/tiktok-shop/product-details",
    credits: 2,
    tagline:
      "PDP — price/originalPrice/discount, images[], skus[] with per-variant stock + saleProps, seller id/url, categories (2 credits).",
    longDescription:
      "Pass a TikTok Shop product URL and get the PDP as clean JSON from the same SSR product_info blob TikTok ships: title, rich description, numeric price + originalPrice + discount + savings (when a seller deduction exists), currency, sold, stock (sum of SKUs), rating/reviews, images[] gallery, categories[{id,name}], saleProperties[] (Color/Size axes), and skus[{id,stock,price,warehouseId,saleProps[]}]. seller includes id, name, url, rating, productCount, and logo when present. Flat 2 credits — same as Shop Products. region (default US) selects the market when the primary path misses. relatedVideos[] (affiliate creator bridge) and seller.tiktokUrl are not in US PDP SSR today — returned when an upstream path provides them; use Product Reviews for sample review text.",
    delivers: [
      "Flat 2 credits",
      "originalPrice / discount / savings always keyed (null when no promo)",
      "skus[] with per-variant stock + saleProps (e.g. Phone Models)",
      "images[] gallery + categories[{id,name}]",
      "seller{id,name,url,rating,productCount,logo}",
    ],
    platformLimits: [
      "relatedVideos[] (creator↔product affiliate bridge) is not embedded in US PDP SSR — Captapi returns it only when an upstream path provides it. ScrapeCreators documents US-only coverage for that block.",
      "seller.tiktokUrl / tiktokId are often absent from PDP SSR (shop catalog shopInfo is richer for store-level signals).",
      "Sample review text lives on Product Reviews — not duplicated here.",
    ],
  },
  {
    slug: "tiktok-shop-product-reviews",
    name: "TikTok Shop Product Reviews API",
    shortName: "Product Reviews",
    category: "comments",
    method: "GET",
    path: "/v1/tiktok-shop/product-reviews",
    credits: 45,
    creditsPerResult: 2.25,
    tagline:
      "TikTok Shop product reviews — star rating, text, SKU variant, verified purchase, country, and review photos.",
    longDescription:
      "Pass a TikTok Shop product URL and get customer reviews as clean JSON — not a video comment thread. Each review includes the per-review star rating (1–5), review text, createdAt (UTC ISO with Z), verifiedPurchase, the SKU / variant label the buyer selected (e.g. \"Thicc 16oz | Ice Cream\"), review country, masked author name when TikTok exposes one, and images[] of photos the reviewer attached. Native PDP SSR returns a short preview (~3) for 2 credits; deeper pages use Apify and bill about 2.25 credits per review returned (e.g. ~45 for limit=20). There is no Comment Replies endpoint for Shop reviews — these are product reviews, not nested social comments, and like counts are not exposed. For sample reviews inside a single PDP call, competitors often stop at 2–3 embedded quotes; this endpoint can page up to 200.",
    delivers: [
      "Per-review star rating + text + createdAt (UTC Z)",
      "verifiedPurchase + review country + SKU variant label",
      "images[] — photos shoppers attached to the review",
      "Up to 200 reviews (SSR preview ~3 for 2 credits native)",
      "Not video comments — no likes / no Comment Replies hop",
    ],
    platformLimits: [
      "Reviewer identity is usually TikTok-masked (e.g. \"C**e\") — full handle/avatar/profile URL are often omitted on public Shop surfaces.",
      "Shop reviews are not a threaded comment system — there is no TikTok Shop Comment Replies endpoint and no like count on review rows.",
      "Native SSR typically embeds ~3 reviews; higher limits use Apify and scale per returned review.",
    ],
  },
  {
    slug: "tiktok-shop-user-showcase",
    name: "TikTok Shop User Showcase API",
    shortName: "User Showcase",
    category: "list",
    method: "GET",
    path: "/v1/tiktok-shop/user-showcase",
    credits: 45,
    creditsPerResult: 2.25,
    tagline:
      "Creator Shop showcase — affiliate shelf products with sold, rating, originalPrice/discount, and seller name/url.",
    longDescription:
      "Pass a TikTok username (with or without @, or a profile URL) and the TikTok Shop User Showcase API returns the products that creator is featuring in their TikTok Shop showcase as clean JSON. This is the affiliate / creator storefront shelf — not the full inventory of a brand store. Each product includes id/url/slug, title, price + originalPrice/discount/savings (same canonical promo-min rule as Shop Search / Product Details), currency, sold, rating/reviews, image, and seller{id,name,url}. For a brand's full catalog, use TikTok Shop Products with a store URL instead. For stock / skus[] / categories, call Product Details with a product URL. Billed per result — about 2.25 credits each. Pass cache=true for the 24h shared cache.",
    delivers: [
      "Affiliate / creator storefront shelf (not a brand catalog)",
      "sold + rating/reviews always keyed (PDP-hydrated)",
      "originalPrice / discount / savings + seller{id,name,url}",
      "SEO slug when the PDP URL includes one",
      "Cross-links: Shop Products for full store · Product Details for SKUs",
    ],
    platformLimits: [
      "Affiliate commission rate is not in the public Apify showcase payload today — commissionRate is returned only when upstream exposes it.",
      "Showcase shelf rows are hydrated via PDP SSR for commerce fields; empty sold/rating means the PDP omitted them, not that Captapi dropped the keys.",
      "ScrapeCreators has no showcase endpoint — this surface is Captapi-only.",
    ],
  },
];

const GITHUB: Spec[] = [
  {
    slug: "github-user",
    name: "GitHub User API",
    shortName: "User",
    category: "channel",
    method: "GET",
    path: "/v1/github/user",
    credits: 1,
    tagline:
      "GitHub public profile — login, type User|Organization, email when public, followers (1 credit).",
    longDescription:
      "Pass a GitHub username or profile URL and get the public /users/{username} profile as camelCase JSON: login, name, company, blog, location, email (only when the account made it public — omitted when null), bio, avatar, publicRepos/publicGists, followers/following, twitterUsername, hireable, nodeId, siteAdmin, and createdAt/updatedAt. type is User or Organization (GitHub's casing) so orgs are distinguishable from people. Flat 1 credit. Honesty note: this is a thin wrap of GitHub's free public REST API (60 req/hour unauthenticated; 5,000/hour with a personal access token). Captapi's value here is one key across ~32 platforms, no per-platform rate-limit handling, and the same response envelope/field names as other profile endpoints — not removing a GitHub OAuth barrier (there isn't one for public profiles). Call api.github.com directly for GitHub-only jobs.",
  },
  {
    slug: "github-repositories",
    name: "GitHub Repositories API",
    shortName: "Repositories",
    category: "list",
    method: "GET",
    path: "/v1/github/repositories",
    credits: 12,
    creditsPerResult: 0.4,
    tagline:
      "List a user's repos with sort/direction/type — opaque Link cursor (~0.4/repo).",
    longDescription:
      "List repositories from GitHub REST /users/{login}/repos. Pass sort=created|updated|pushed|full_name (default updated), direction=asc|desc, and type=owner|member|all — all echoed at the top level. Each row is the same camelCase repo card as github/repository minus watchers and parent (list payloads omit subscribers_count and parent — call github/repository for those). Opaque nextCursor from GitHub's Link header. ~0.4 credits/repo (default limit 30 → ~12). Pricing vs detail: single-repo lookup is flat 1 credit; this list is per-result for bulk. Trending is a separate HTML scrape at flat 2.",
  },
  {
    slug: "github-pull-requests",
    name: "GitHub Pull Requests API",
    shortName: "Pull Requests",
    category: "list",
    method: "GET",
    path: "/v1/github/pull-requests",
    credits: 12,
    creditsPerResult: 0.4,
    tagline:
      "List repo PRs — draft, labels, author{}, head/base, opaque Link cursor (state echoed).",
    longDescription:
      "List pull requests for a repository via GitHub REST /pulls. Default state=open (pass closed|all — the applied filter is echoed as data.state). Each row: number, title, state, draft, labels[], author{id,login,avatar,url}, head/base refs, assignees, requestedReviewers, closedAt/mergedAt. Opaque nextCursor from GitHub's Link header (not a bare page number). Billing scales with results (~0.4/PR, min ~12 at default limit).",
  },
  {
    slug: "github-activity",
    name: "GitHub Activity API",
    shortName: "Activity",
    category: "list",
    method: "GET",
    path: "/v1/github/activity",
    credits: 12,
    creditsPerResult: 0.4,
    tagline:
      "Public events with typed payload (Push commits/ref, PR/issue action) — 90-event ceiling.",
    longDescription:
      "Recent public events from /users/{login}/events/public with a normalized payload per type: PushEvent → ref, size, commits[{sha,message}]; PullRequestEvent → action + PR fields; IssuesEvent → action + issue fields. actor is omitted (same as username). GitHub caps this feed at 90 events (~90 days) — eventCeiling is echoed and pagination stops there (limit max 90). Opaque nextCursor from the Link header. Not a contribution graph — use github/contributions for the heatmap.",
  },
  {
    slug: "github-followers",
    name: "GitHub Followers API",
    shortName: "Followers",
    category: "list",
    method: "GET",
    path: "/v1/github/followers",
    credits: 3,
    creditsPerResult: 0.1,
    tagline:
      "Follower cards {id, login, type, url, avatar} — ~0.1/row; large accounts are expensive to page fully.",
    longDescription:
      "List followers from /users/{login}/followers as {id, login, type (User|Organization), url, avatar}. Opaque nextCursor from GitHub's Link header. Billed ~0.1 credits/row (min 3; default limit 30 → ~3). There is no sampling/since parameter — paging a mega-account (~250k followers) costs ~25k credits at this rate; for full archives prefer api.github.com. Structurally identical to github/following.",
  },
  {
    slug: "github-following",
    name: "GitHub Following API",
    shortName: "Following",
    category: "list",
    method: "GET",
    path: "/v1/github/following",
    credits: 3,
    creditsPerResult: 0.1,
    tagline:
      "Accounts a user follows — same card and ~0.1/row pricing as followers.",
    longDescription:
      "List accounts from /users/{login}/following as {id, login, type, url, avatar}. Same shape, opaque Link cursor, and ~0.1 credits/row (min 3) as github/followers. No sampling parameter — large following lists are expensive to exhaust via Captapi.",
  },
  {
    slug: "github-contributions",
    name: "GitHub Contributions API",
    shortName: "Contributions",
    category: "details",
    method: "GET",
    path: "/v1/github/contributions",
    credits: 2,
    tagline:
      "GitHub contribution graph — sorted days[], currentStreak (today grace), longestStreak (2 credits).",
    longDescription:
      "Pass a GitHub username or profile URL and get the real last-year contribution calendar from github.com/users/{login}/contributions: totalContributions, from/to (min/max date), currentStreak, longestStreak, and days[{date, count, level}] sorted ascending by date (not GitHub's weekday-major DOM order). currentStreak uses GitHub's today-grace rule: a zero on today does not break the streak; a zero on any earlier day does. source discloses that HTML calendar. This is not /users/{u}/events/public (max 90 events / 90 days) and not a sampled stars sum. Flat 2 credits.",
  },
  {
    slug: "github-repository",
    name: "GitHub Repository API",
    shortName: "Repository",
    category: "details",
    method: "GET",
    path: "/v1/github/repository",
    credits: 1,
    tagline:
      "GitHub repo — stars, real watchers (subscribers), openIssuesAndPrs, license, parent when fork (1 credit).",
    longDescription:
      "Pass a repository URL or owner/name and get GitHub REST /repos/{owner}/{repo} as camelCase JSON: description, stars, forks, watchers (subscribers_count — people notified of activity; not the legacy watchers_count star alias), openIssuesAndPrs (GitHub's open_issues_count = open issues + open PRs), primary programming language, license (SPDX; NOASSERTION → null with licenseName kept), topics, parent when isFork, size, visibility, hasIssues/hasDiscussions, ownerType (User|Organization), and timestamps. Flat 1 credit. For the curated trending page (stars gained today/this week/month), use github/trending-repositories.",
  },
  {
    slug: "github-trending-repositories",
    name: "GitHub Trending Repositories API",
    shortName: "Trending",
    category: "search",
    method: "GET",
    path: "/v1/github/trending-repositories",
    credits: 2,
    tagline:
      "github.com/trending — repos ranked by starsGained (daily|weekly|monthly), not all-time stars (2 credits).",
    longDescription:
      "Scrapes the public github.com/trending page (source: \"github.com/trending\") — repositories ranked by stars gained in a window, not REST /search/repositories sorted by all-time stars. Pass since=daily|weekly|monthly (default daily) and optional language slug (e.g. python → /trending/python). Each row: rank, fullName, url, description, language (programming language), stars, forks, starsGained, since. Flat 2 credits. The HTML page usually lists ~25 repos; there is no cursor (unlike Search API's 1000-result cap). This is not a substitute for github/repository detail fields (license, watchers/subscribers, parent, …).",
    delivers: [
      "Real github.com/trending (not all-time star search)",
      "since=daily|weekly|monthly + starsGained",
      "source field discloses the HTML page",
    ],
    platformLimits: [
      "Page usually has ≤25 rows — no cursor / no Search API 1000 cap.",
      "Not the same 23-field detail object as github/repository.",
    ],
  },
  {
    slug: "github-trending-developers",
    name: "GitHub Trending Developers API",
    shortName: "Trending Devs",
    category: "search",
    method: "GET",
    path: "/v1/github/trending-developers",
    credits: 2,
    tagline:
      "github.com/trending/developers — windowed ranks with popularRepo + followers (2 credits).",
    longDescription:
      "Scrapes github.com/trending/developers (source: \"github.com/trending/developers\") for developers ranked in a since=daily|weekly|monthly window — not REST /search/users with followers:>1000 (all-time most-followed). Each row: rank, login, name, url, avatar, popularRepo/popularRepoUrl/popularRepoDescription, plus followers, following, bio, company, location, publicRepos, ownerType hydrated from GET /users/{login}. No Search relevance score field. Flat 2 credits. Page usually ≤25 rows (no cursor).",
    delivers: [
      "Real github.com/trending/developers (not followers:>1000 search)",
      "since window + popularRepo from the page",
      "followers/bio/company/location for ranking and vetting",
    ],
    platformLimits: [
      "Hydration uses GitHub REST /users/{login} per row — profile fields may be omitted if GitHub rate-limits.",
      "Page usually has ≤25 rows — no cursor.",
    ],
  },
];


const TWITCH: Spec[] = [
  {
    slug: "twitch-profile",
    name: "Twitch Profile API",
    shortName: "Profile",
    category: "channel",
    method: "GET",
    path: "/v1/twitch/profile",
    credits: 1,
    tagline:
      "Twitch channel — socials[], topClips, schedule preview, live stream block (null when offline), clean VODs (1 credit).",
    longDescription:
      "Pass a Twitch channel URL or username and get a clean profile (no GraphQL junk). Canonical core: platform, id, handle, url, displayName, bio, avatar, banner, followers, createdAt — plus deprecated aliases login/username/description/profileImage/bannerImage for one release. Also: isPartner/isAffiliate, isLive, stream{title, game, gameBoxArtUrl, viewers, startedAt, thumbnail} when live (null when offline — not six null fields), lastBroadcast{}, socials[{platform,url,title}] from channel panels / socialMedias, recentVideos[] (embedUrl from real video id, thumbnail with {width}x{height} substituted to 320x180, thumbnailTemplate kept for custom sizes, language, animatedPreviewUrl, gameBoxArtUrl), topClips[], and schedule[] (lean preview, max 10). Canonical full schedule with id/isRecurring/canceledUntil: GET /v1/twitch/user-schedule. game stays the category name string; gameBoxArtUrl and animatedPreviewUrl are additive media fields. Accepts cache / cacheMaxAge=1d|3d|7d|14d|30d. Flat 1 credit.",
    delivers: [
      "socials[] from DefaultPanel linkURLs + socialMedias",
      "topClips[] + schedule[] preview (user-schedule is the dedicated schedule endpoint)",
      "stream null when offline; VOD thumbs substituted to 320x180",
      "Canonical avatar/banner/displayName (+ deprecated aliases)",
    ],
    platformLimits: [
      "schedule[] on profile is a short upcoming preview — use /twitch/user-schedule for the full schedule surface.",
      "embedUrl is only emitted when a real embed id is known (Twitch video/clip id) — never invented from an unrelated page id.",
    ],
  },
  {
    slug: "twitch-user-videos",
    name: "Twitch User Videos API",
    shortName: "User Videos",
    category: "list",
    method: "GET",
    path: "/v1/twitch/user-videos",
    credits: 2,
    tagline:
      "Twitch channel VODs — lean rows, video-id cursor, filter/sort, top-level broadcaster{} (flat 2).",
    longDescription:
      "Pass a Twitch channel URL or username and get a clean videos[] list (not a profile dump). Each row: id, url, embedUrl, title, createdAt, durationSeconds, views, thumbnail (320x180 — {width}x{height} substituted; thumbnailTemplate kept), animatedPreviewUrl, broadcastType, game (+ gameId/gameSlug/box art), lowercase language. Channel identity is once at the top as broadcaster{} — videos[] do not repeat channel{}/broadcaster/broadcasterProfileImage. filterBy=ARCHIVE|HIGHLIGHT|UPLOAD (omit for all types — no default filter; filterBy echoes null when omitted). sortBy=TIME|VIEWS. nextCursor is the last video id on the page (stable within the window — not a raw offset). Hard ceiling: first 100 matching videos (windowMax=100); Twitch anonymous GQL rejects after-cursors with IntegrityCheckFailed, so deeper history is not available. Flat 2 credits per call.",
    platformLimits: [
      "At most the first 100 matching videos (windowMax). Deeper VOD history is not available on this surface.",
      "nextCursor is a video id within that 100-video window — not Twitch's GQL after-cursor (anonymous integrity check blocks it).",
    ],
  },
  {
    slug: "twitch-user-schedule",
    name: "Twitch User Schedule API",
    shortName: "User Schedule",
    category: "list",
    method: "GET",
    path: "/v1/twitch/user-schedule",
    credits: 1,
    tagline:
      "Twitch channel schedule — segment id, isRecurring, canceledUntil, startedAt/endedAt (1 credit).",
    longDescription:
      "Pass a Twitch channel URL or username and get upcoming schedule segments as clean JSON. Each segment: id (stable segment key for dedup), title, startedAt/endedAt (canonical — same tense as stream.startedAt; startAt/endAt kept as deprecated aliases), game/gameId, isRecurring, isCancelled, canceledUntil (skip segments where this is set — a canceled broadcast still appears in Twitch's list), firstOccurrenceAt. This is the canonical full schedule; twitch/profile.schedule[] is only a short preview (up to 10). Anonymous GQL does not expose timezone or vacation mode. Flat 1 credit. Pass limit (default 50, max 100).",
    delivers: [
      "Segment id + isRecurring + canceledUntil / isCancelled",
      "startedAt/endedAt (startAt/endAt deprecated aliases)",
      "game + gameId when the segment has a category",
      "Canonical full schedule — profile.schedule[] is a lean preview only",
    ],
    platformLimits: [
      "timezone and vacation mode are not on Twitch's anonymous Schedule type — not inventable here.",
      "Canceled segments still appear; filter client-side on canceledUntil / isCancelled.",
    ],
  },
  {
    slug: "twitch-clip",
    name: "Twitch Clip API",
    shortName: "Clip",
    category: "details",
    method: "GET",
    path: "/v1/twitch/clip",
    credits: 1,
    tagline:
      "Twitch clip — curator vs channel, signedVideoUrl, unwrapped token, relatedClips (1 credit).",
    longDescription:
      "Pass a Twitch clip URL (or channel URL/username for a recent clip) and get a clean structured object — not Twitch's raw GraphQL envelope. Includes curator (who cut the clip) separate from channel (id, followers, isPartner, lastBroadcast), BCP-47 lowercase language (same as twitch/profile recentVideos), isFeatured/isPublished, videoOffsetSeconds, gameId/gameSlug/gameBoxArtUrl, videoQualities[{quality,frameRate,url,signedUrl}] with frameRate rounded to 2dp, videoUrl (unsigned source) plus signedVideoUrl (?sig=&token= — required for /nauth/ MP4s; unsigned returns 401), playbackAccessToken as parsed fields (signature, expires, expiresAt, clipUri, clipSlug, deviceId, version, authorization — no escaped JSON value string), and relatedClips[] from the same broadcaster. Flat broadcaster / broadcasterProfileImage kept as deprecated aliases of channel{}. Accepts cache / cacheMaxAge=1d|3d|7d|14d|30d. Flat 1 credit.",
    delivers: [],
  },
];

const SPOTIFY: Spec[] = [
  {
    slug: "spotify-artist",
    name: "Spotify Artist API",
    shortName: "Artist",
    category: "channel",
    method: "GET",
    path: "/v1/spotify/artist",
    credits: 1,
    tagline:
      "Spotify artist — followers, monthlyListeners, worldRank, topCities, topTracks with playCount, concerts, and related artists (1 credit).",
    longDescription:
      "Pass a Spotify artist URL, URI, or ID and get a clean profile: name (track/artist title — not a profile displayName alias), description, image, followers, monthlyListeners, worldRank, topCities[{city,country,region,listeners}], externalLinks[], verified, topTracks[] (with playCount), concerts[], relatedArtists[], and albums[]/singles[] samples plus albumsCount/singlesCount and albumsHasMore/singlesHasMore. Flat 1 credit. monthlyListeners, topCities, and worldRank are not on Spotify's public Web API. The overview GraphQL only embeds a short discography sample — when HasMore is true, chain release URIs into /spotify/album. Pass raw=true only if you need the full upstream GraphQL payload (omitted by default — it is ~80% of the old response).",
  },
  {
    slug: "spotify-track",
    name: "Spotify Track API",
    shortName: "Track",
    category: "details",
    method: "GET",
    path: "/v1/spotify/track",
    credits: 1,
    tagline:
      "Spotify track — playCount, joinable artists[]/album{}, explicit, releaseDate (1 credit).",
    longDescription:
      "Pass a Spotify track URL, URI, or ID and get clean JSON: id, name (song title), playCount (stream count from Spotify's web GraphQL — same metric as artist topTracks[].playCount), trackNumber, contentRating + explicit, durationMs, artists[{id,uri,name,url}] (chain into /spotify/artist), album{id,uri,name,url,releaseDate} (chain into /spotify/album), releaseDate, and previewUrl / isrc / popularity when this Pathfinder surface exposes them. Flat 1 credit (same as artist — not 2). Pass raw=true only for the full GraphQL payload (omitted by default). Note: Spotify's official 0–100 popularity and ISRC are often absent on getTrack; playCount is the listen metric here.",
    platformLimits: [
      "contentRating is Spotify's Pathfinder label enum (tracks: NONE | EXPLICIT | NINETEEN_PLUS | UNKNOWN) — not a 2-valued alias of explicit. explicit is true only when the label is EXPLICIT.",
    ],
  },
  {
    slug: "spotify-album",
    name: "Spotify Album API",
    shortName: "Album",
    category: "details",
    method: "GET",
    path: "/v1/spotify/album",
    credits: 1,
    tagline:
      "Spotify album — tracks[] with playCount, joinable artists[], releaseDate, explicit (1 credit).",
    longDescription:
      "Pass a Spotify album URL, URI, or ID and get clean JSON: name, artists[{id,uri,name,url}] (chain into /spotify/artist), tracks[{id,trackNumber,discNumber,name,uri,url,durationMs,playCount,explicit,artists}] from tracksV2 (per-track stream counts; id matches the uri suffix for joins into /spotify/track), totalTracks, releaseDate (full ISO — not year-only), releaseYear, album-level explicit (true if any track label is EXPLICIT), and cover image. Flat 1 credit (same as artist/track — not 2). Pass raw=true only if you need the full GraphQL payload (omitted by default).",
  },
  {
    slug: "spotify-search",
    name: "Spotify Search API",
    shortName: "Search",
    category: "search",
    method: "GET",
    path: "/v1/spotify/search",
    credits: 2,
    tagline:
      "Search Spotify — canonical spotify: URIs, explicit, fetchedAt (flat 2 credits).",
    longDescription:
      "Pass q plus optional type=tracks|albums|artists|podcasts|episodes (default tracks) and limit (max 50, no cursor). Primary path is web-player Pathfinder GraphQL (same family as /spotify/artist|track|album); Apify scraper is fallthrough only — do not assume one raw schema across both (GraphQL __typename vs flat albumName/isExplicit). Envelope: query, type, fetchedAt, source (pathfinder|apify), results[]. Each result ships a canonical Spotify URI (spotify:track:… not a bare id), url, name, artists (structured on Pathfinder track/album hits), durationMs/durationFormatted, explicit, contentRating, and image. Request freshness is envelope fetchedAt only — not copied onto every row. Pathfinder search (decorateContextTracks) does not expose playCount or playable (absence ≠ false/zero); chain uri into /spotify/track for those. Flat 2 credits on native Pathfinder; Apify fallthrough scales per result. Pass raw=true for per-result upstream payloads (omitted by default; searchTerm is not repeated inside raw).",
    platformLimits: [
      "playCount is not on search.results[] — Pathfinder search hydrate omits stream counts; use /spotify/track or /spotify/album tracks[].",
      "playable is not on search.results[] — decorateContextTracks omits playability; use /spotify/track.",
      "fetchedAt is envelope-only — results[] do not carry scrapedAt.",
    ],
  },
  {
    slug: "spotify-podcast",
    name: "Spotify Podcast API",
    shortName: "Podcast",
    category: "details",
    method: "GET",
    path: "/v1/spotify/podcast",
    credits: 1,
    tagline:
      "Spotify podcast show — publisher, rating, topics, explicit flag, and totalEpisodes as clean JSON.",
    longDescription:
      "Pass a Spotify show/podcast URL, URI, or ID (not an artist URL) and get clean JSON: id, name, description, publisher{name}, rating{average, totalRatings}, topics[{title, uri}], contentRating / contentRatingLabels / explicit, mediaType, showTypes, totalEpisodes, and cover image. Publisher is the show's publisher (not host names stuffed into artists[]). Flat 1 credit per call. Does not ship Spotify's UI color palette (visualIdentity) or a bulky raw dump. For the episode archive, use /spotify/podcast-episodes (cursor pagination).",
    platformLimits: [
      "contentRatingLabels can include EXPLICIT | NINETEEN_PLUS | NOT_FOR_CHILDREN | SPOTIFY_EIGHTEEN_PLUS | UNKNOWN (and NONE on some surfaces). explicit is true only when EXPLICIT is among the labels — keep contentRating for age-gate values.",
    ],
  },
  {
    slug: "spotify-podcast-episodes",
    name: "Spotify Podcast Episodes API",
    shortName: "Podcast Episodes",
    category: "list",
    method: "GET",
    path: "/v1/spotify/podcast-episodes",
    credits: 2,
    tagline:
      "Podcast episode archive — previewUrl, releaseDate, explicit, cursor pagination (flat 2 credits).",
    longDescription:
      "Pass a Spotify show/podcast URL, URI, or ID (not an artist URL). Returns the show card plus episodes[{id, name, description, releaseDate, durationMs, previewUrl, audioUrls[], mediaTypes, hasVideo, contentRating/explicit, hasTranscripts, paywallContent, showTypes}]. totalEpisodes comes from the same episodes query as the page (no drift vs a separate show fetch). Cursor pagination via nextCursor/hasMore (offset into the archive; limit max 50). Flat 2 credits per call on native Pathfinder. Same anti-bloat rule as /spotify/podcast: no visualIdentity color dumps, no playedState, no per-episode podcastV2 show copies — raw is opt-in (?raw=true) and still slimmed.",
  },
];

const SOUNDCLOUD: Spec[] = [
  {
    slug: "soundcloud-artist",
    name: "SoundCloud Artist API",
    shortName: "Artist",
    category: "channel",
    method: "GET",
    path: "/v1/soundcloud/artist",
    credits: 1,
    tagline:
      "SoundCloud artist — handle, subscriptionTier, externalLinks, verified (1 credit).",
    longDescription:
      "Pass a SoundCloud artist URL or username and get clean JSON: id, handle (permalink slug — the join key; username is the display name and may differ in casing), username, name, description, avatar, city/countryCode, verified, subscriptionTier (pro-unlimited|pro|mid-tier|free — one field, not badges + creatorSubscription duplicates), followers/followings/trackCount/playlistCount/likesCount, externalLinks[{url,network,title,username}] from SoundCloud web-profiles when published, createdAt when SoundCloud exposes it (often redacted on the public api-v2), and lastModified. Flat 1 credit. Accepts cache / cacheMaxAge.",
  },
  {
    slug: "soundcloud-artist-tracks",
    name: "SoundCloud Artist Tracks API",
    shortName: "Artist Tracks",
    category: "list",
    method: "GET",
    path: "/v1/soundcloud/artist-tracks",
    credits: 2,
    tagline:
      "Artist track list — same track shape as /soundcloud/track, artist{} once at top, opaque cursor (2 credits).",
    longDescription:
      "Pass a SoundCloud artist URL or username and get that artist's tracks as clean JSON. Each track row matches /soundcloud/track (title, plays/likes/reposts/comments/downloads, license, genre/tags, artwork, streamable/downloadable) — without repeating artist{} on every row. Top-level artistId + artist{id,handle,name,url,avatar,followers,verified} join to /soundcloud/artist; artistUrl is the profile URL. nextCursor is an opaque token (not a SoundCloud api-v2 URL). Flat 2 credits per call (limit up to 100).",
  },
  {
    slug: "soundcloud-track",
    name: "SoundCloud Track API",
    shortName: "Track",
    category: "details",
    method: "GET",
    path: "/v1/soundcloud/track",
    credits: 1,
    tagline:
      "SoundCloud track — plays/likes/license, nested artist{}, streamUrl when streamable (1 credit).",
    longDescription:
      "Pass a SoundCloud track URL and get clean JSON: title, artist{id,handle,name,url,avatar,followers,verified} (chain id/handle into /soundcloud/artist), plays/likes/reposts/comments/downloads, license, genre/tags, publishedAt, streamable/downloadable (SoundCloud permission flags), and when the public api-v2 allows it — streamUrl (progressive MP3), hlsUrl, downloadUrl, plus mediaUrlsExpireAt for signed CDN links. waveformUrl is the waveform JSON endpoint, not audio. Flat 1 credit. Accepts cache / cacheMaxAge.",
  },
];

const LINKTREE: Spec[] = [
  {
    slug: "linktree-page",
    name: "Linktree Page API",
    shortName: "Page",
    category: "details",
    method: "GET",
    path: "/v1/linktree/page",
    credits: 1,
    delivers: [],
    tagline:
      "Link-in-bio → creator graph: typed links, socialAccounts{} that feed TikTok/Instagram/Spotify/SoundCloud, email, verticals. Flat 1 credit.",
    longDescription:
      "Paste a Linktree URL or username and get the public page as clean JSON. Canonical profile fields: platform, id (string), handle/username, url, displayName (name is a deprecated alias), description, avatar, verified. Also verticals[] (Linktree niche labels, e.g. music_artist), linkPlatforms[] (platforms Linktree detected on the page), timezone, and email when the creator publishes a mailto social. links[] are typed (CLASSIC, PRODUCT, SPOTIFY_*, YOUTUBE_VIDEO, GROUP, …) with id/url/thumbnail; PRODUCT rows resolve shopUrl when Linktree leaves url empty (url is always present — null only when no destination exists); GROUP children nest under links with parentId. socials[] is the icon list (incl. EMAIL_ADDRESS). socialAccounts{} is the camelCase HTTP map for catalog joins (instagram/tiktok/spotify/soundcloud/appleMusic/youtube/…) — email is not duplicated there (use top-level email). YouTube watch URLs in socialAccounts are resolved to the channel via oEmbed so they pipe into youtube/channel-details. Accepts cache / cacheMaxAge. Flat 1 credit. This is the fan-out point for a creator graph: one Linktree call feeds the rest of the catalog.",
  },
];

const SNAPCHAT: Spec[] = [
  {
    slug: "snapchat-user-profile",
    name: "Snapchat User Profile API",
    shortName: "User Profile",
    category: "channel",
    method: "GET",
    path: "/v1/snapchat/user-profile",
    credits: 1,
    tagline:
      "Snapchat profile — unwrapped highlight ids, mediaType image/video, category labels, Spotlight boosts (1 credit).",
    longDescription:
      "Pass a Snapchat username or profile URL and get the public profile as clean JSON — not Snapchat's protobuf wrappers. Canonical card: username, displayName, bio, avatar, banner (square hero), url, followers, verified (from badge), human-readable category (public-profile-category-v3-business-group → Business Group), absolute website URL, snapcode, createdAt (+ creationTimestampMs for the same instant). Identical-value aliases (handle/subscriberCount/profilePictureUrl/squareHeroImageUrl) are not emitted. highlights[] are curated Story albums; spotlightHighlights[] are Spotlight posts — different collections. Highlight ids/titles unwrap to plain strings (never Python dict repr). Each snap has mediaType image|video from snapMediaType 0|1, plus embeddedTextCaption / contextCards / hashtags / lensMetadata when Snapchat exposes them. story.snapCount always equals story.snapList length. Spotlight rows add engagement{views,shares,comments,boosts,recommends}. relatedAccounts[] use the same avatar/url keys as the top-level card. Flat 1 credit.",
    delivers: [
      "Unwrapped highlightId / storyTitle (no protobuf {value} leaks)",
      "mediaType image|video on every snap (snapMediaType 0 and 1)",
      "Canonical username/followers/avatar/banner (no alias twins)",
      "Spotlight boosts/recommends + relatedAccounts with avatar/url",
    ],
  },
];

const TRUTH_AUTH_LIMIT =
  "As of late 2025, Truth Social only lets you view public profiles/posts of prominent users (e.g. Trump, Vance) without authentication; most other accounts require auth and will 404 here.";

const TRUTH_SOCIAL: Spec[] = [
  {
    slug: "truth-social-profile",
    name: "Truth Social Profile API",
    shortName: "Profile",
    category: "channel",
    method: "GET",
    path: "/v1/truth-social/profile",
    credits: 1,
    tagline:
      "Prominent public Truth Social profiles — isPrivate/bot/group, fields[], avatar/banner. Flat 1 credit.",
    longDescription:
      `Pass a Truth Social @username or profile URL and get the public account as clean JSON. Canonical profile core: platform, id, username, url, displayName, bio, avatar, banner, followers, following, postCount, verified, createdAt. Also: bot/isPrivate/group, discoverable, location/website, ISO lastStatusAt, emojis[], and profile fields[] with verifiedAt for confirmed links. Mastodon twin keys (handle/acct/name/avatarStatic/headerStatic/locked) are omitted — acct never differs from username on reachable public accounts. ${TRUTH_AUTH_LIMIT} Flat 1 credit.`,
    delivers: [
      "isPrivate / bot / group classification flags",
      "fields[] with verifiedAt for confirmed profile links",
      "HTML-stripped bio + avatar/banner URLs",
      "Honest prominent-only access limit (most accounts 404)",
    ],
  },
  {
    slug: "truth-social-user-posts",
    name: "Truth Social User Posts API",
    shortName: "User Posts",
    category: "list",
    method: "GET",
    path: "/v1/truth-social/user-posts",
    credits: 2,
    tagline:
      "Recent Truths — same post mapper as /post (links, card, reblog/quote, mentions). 2 credits.",
    longDescription:
      `Pass a Truth Social @username or profile URL and get recent public posts as clean JSON — same status mapper as /post (not a slim sibling). Full author{} once at the top (same shape as /profile); each post keeps a slim author {id,username,displayName,avatar,verified}. text + links[] (unbroken URLs), card, media.meta, externalVideoId→Rumble, engagement {replies,reblogs,likes,downvotes} (likes is favourites/upvotes — identical upstream; downvotes keeps real zeros). Chain fields when present: reblog{}, quote{}/quoteId, inReplyToId/inReplyToAccountId/inReplyTo{} — so a boost is not mistaken for an original. Also mentions[]/tags[] (platform lists), poll{}, visibility, spoilerText, sponsored, pinned, group. Session-only flags (favourited/reblogged/muted/bookmarked) are omitted. Native timeline excludes replies (Truth Social exclude_replies); reblogs and quotes still appear. nextCursor/hasMore; max limit 80. ${TRUTH_AUTH_LIMIT} Flat 2 credits.`,
    delivers: [
      "Same _normalize_post mapper as /post (links/card/media.meta/externalVideoId)",
      "reblog / quote / inReplyTo chain fields for monitoring accuracy",
      "Platform mentions[] + tags[] (not regex-from-text)",
      "Cursor pagination; honest prominent-only access limit",
    ],
    platformLimits: [
      "Native timeline uses exclude_replies — reply posts are not listed (use /post for a specific reply URL).",
      "Most non-prominent accounts require auth and 404.",
    ],
  },
  {
    slug: "truth-social-post",
    name: "Truth Social Post API",
    shortName: "Post",
    category: "details",
    method: "GET",
    path: "/v1/truth-social/post",
    credits: 1,
    tagline:
      "One Truth — text, links[], card, reblog/quote chain, media.meta, externalVideoId. Flat 1 credit.",
    longDescription:
      `Pass a Truth Social post URL or numeric ID and get the public status as clean JSON (same mapper as user-posts rows): text with unbroken URLs, links[], full author{} (same _normalize_account as /profile), engagement {replies,reblogs,likes,downvotes}, card, media[] with meta/durationSeconds, externalVideoId when the clip is on Rumble, plus reblog/quote/inReplyTo chain fields, mentions[]/tags[], poll, visibility, spoilerText, sponsored, pinned when present. Session-only favourited/reblogged/muted/bookmarked are omitted. ${TRUTH_AUTH_LIMIT} Flat 1 credit.`,
  },
];

const KICK: Spec[] = [
  {
    slug: "kick-clip",
    name: "Kick Clip API",
    shortName: "Clip",
    category: "details",
    method: "GET",
    path: "/v1/kick/clip",
    credits: 1,
    delivers: [],
    tagline:
      "Get a Kick clip — creator vs channel, HLS playback, VOD deep-link, views, and duration as structured JSON.",
    longDescription:
      "Two modes. Clip URL → {channelUrl, clip} with creator (who cut the clip) separate from channel (broadcaster), privacy, isMature, startedAt, livestreamId, vod{id,url,urlWithOffset}, vodStartsAt, and categorySlug/parentCategory. Playback is HLS: videoType is \"hls\", videoUrl/hlsUrl are the .m3u8 playlist (not a progressive MP4 — download that URL and you get a text manifest). Channel URL/@username → {channelUrl, totalReturned, clips[]} only — no top-level clip and no cursor (Kick's channel clips list is a single page; use limit, default 30, max 100). Session-only liked is omitted. Accepts cache / cacheMaxAge. Flat 1 credit on the native path.",
  },
];

const AMAZON_SHOP: Spec[] = [
  {
    slug: "amazon-shop-page",
    name: "Amazon Seller Storefront API",
    shortName: "Seller Storefront",
    category: "list",
    method: "GET",
    path: "/v1/amazon-shop/page",
    credits: 1,
    tagline:
      "Third-party seller storefronts (/sp?seller= / /s?me=) — ASIN + canonical /dp URLs, price, badges. Not influencer /shop/{handle}.",
    longDescription:
      "Pass an Amazon seller storefront URL (/sp?seller=… or /s?me=…) or raw seller ID (e.g. A294P4X9EWVXLJ) and get that merchant's product listings as clean JSON. Each product includes an extracted ASIN and a canonical https://www.amazon.com/dp/{ASIN} URL (joinable to Amazon's catalog — not shop/{handle}/getProductDetails/… affiliate paths), plus title, image, price/currency/priceFormatted, rating/reviews, and isPrime/isBestSeller/isSponsored. Also seller{id,name,url}, scrapedAt, and cursor pagination (nextCursor/hasMore). Billing is 1 credit per ~16-product storefront page. This is not the influencer Amazon Shop surface (amazon.com/shop/{handle}) that returns avatar/socials/lists/curations — those creator vitrines are a different product and return HTTP 400 here.",
    platformLimits: [
      "Influencer Amazon Shops (amazon.com/shop/{handle}) are out of scope — HTTP 400. That surface has socials[], lists[], curations[], trendingPicks[] and is not a seller storefront.",
      "Not an SC amazon/shop equivalent: SC targets creator affiliate vitrines; this endpoint targets third-party seller storefronts with ASIN-first product identity.",
    ],
  },
];

const ACCOUNT: Spec[] = [
  {
    slug: "account-balance",
    name: "Credit Balance API",
    shortName: "Credit Balance",
    category: "details",
    method: "GET",
    path: "/v1/account/balance",
    credits: 0,
    tagline: "Plan, subscription vs top-up credits, monthly quota, and renewsAt — 0 credits.",
    longDescription:
      "Live (never cached) credit balance for the calling Captapi key as camelCase JSON: plan, monthlyQuota, subscriptionCredits, topupCredits, totalCredits, subscriptionRenewsAt / quotaResetsAt, usedThisMonth, keyName, and rateLimitPerMinute. snake_case aliases (monthly_quota, …) are emitted for one release — prefer camelCase. Free — does not consume credits. Use for low-balance alerts and dashboards.",
  },
  {
    slug: "account-request-history",
    name: "Request History API",
    shortName: "Request History",
    category: "list",
    method: "GET",
    path: "/v1/account/request-history",
    credits: 0,
    tagline: "Recent API requests for your key — requestId, status, credits, cacheHit (0 credits).",
    longDescription:
      "Live (never cached) request log for your Captapi key — free. Each row includes requestId (same UUID as the response envelope / x-captapi-request-id for support matching), endpoint, platform, resource (public URL or internal cache key such as instagram_user:handle — resourceUrl is a deprecated alias), creditsUsed, cacheHit, statusCode, responseTimeMs, errorMessage, createdAt. Filter with endpoint, statusCode, since, and until. limit only caps rows returned — it does not bill.",
    delivers: [
      "requestId per row for support / envelope matching",
      "creditsUsed + cacheHit + responseTimeMs (see cache savings in one sample)",
      "Filters: endpoint, statusCode, since, until",
      "Free — never cached, never billed",
    ],
  },
  {
    slug: "account-daily-usage",
    name: "Daily Usage API",
    shortName: "Daily Usage",
    category: "list",
    method: "GET",
    path: "/v1/account/daily-usage",
    credits: 0,
    tagline: "Day-by-day credit usage for spend monitoring (0 credits).",
    longDescription:
      "Daily credit usage buckets for your Captapi key — date, requests, creditsUsed, success/fail counts. Live account data — not cached. Free.",
  },
  {
    slug: "account-most-used-routes",
    name: "Most Used Routes API",
    shortName: "Most Used Routes",
    category: "list",
    method: "GET",
    path: "/v1/account/most-used-routes",
    credits: 0,
    tagline: "Ranked list of which Captapi routes your key calls most (0 credits).",
    longDescription:
      "Ranked routes for your Captapi key over a chosen window — endpoint, request counts, creditsUsed. Live account data — not cached. Free.",
  },
];

/** Cross-platform analytics + direct video-file upload helpers (not social platforms). */
const UTILITIES: Spec[] = [
  {
    slug: "analytics-post",
    name: "Post Analytics API",
    shortName: "Post Analytics",
    category: "details",
    method: "GET",
    path: "/v1/analytics/post",
    credits: 1,
    tagline: "Unified metrics for one post, video, or reel — platform auto-detected (1 credit).",
    longDescription:
      "Pass a public post/video/reel URL from one of 11 platforms (YouTube, TikTok, Instagram, Facebook, X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble) — not the full Captapi catalog (Kwai, Twitch, Spotify, Snapchat, and others are out of scope). Platform is auto-detected; cross-platform URLs are the point of this endpoint. Returns one normalized metrics object: views, likes, comments, shares, saves, interactions, engagementRate with engagementRateBasis=interactions/views (ratio), plus commentsIsApproximate / interactionsIsApproximate when a compact UI count (e.g. YouTube \"2.4M\") contributed. Schema is stable across networks; unavailable values are null (YouTube has no public share/save counts; author.username is the @handle when known, never the display name). Do not compare this engagementRate to TikTok popular-creators — that field uses a different engagementRateBasis (percent). Flat 1 credit. Pass cache=true for the 24h shared cache (0 credits on hit).",
  },
  {
    slug: "analytics-compare",
    name: "Compare Analytics API",
    shortName: "Compare Analytics",
    category: "details",
    method: "GET",
    path: "/v1/analytics/compare",
    credits: 1,
    tagline: "Compare unified metrics across up to 10 URLs — each row is the analytics/post object (1 credit/resolved URL).",
    longDescription:
      "Pass up to 10 comma-separated post/video/reel URLs (any mix of the same 11 platforms as Post Analytics) and get count/resolved/failedCount plus results[] and failed[]. Each ok row is exactly the /v1/analytics/post object plus status — platform, id, title, url, publishedAt (full ISO), durationSeconds, thumbnailUrl, author{}, metrics{views, likes, comments, shares, saves, interactions, engagementRate, engagementRateBasis, approximate flags}. Failed URLs appear in failed[] with a reason. Bills 1 credit per successfully resolved URL that is not served from the 24h cache shared with post analytics; no bulk discount vs N separate /post calls — the win is one HTTP round-trip. Pass cache=true for free cache hits.",
  },
  {
    slug: "video-transcript",
    name: "Video File Transcript API",
    shortName: "File Transcript",
    category: "transcript",
    method: "POST",
    path: "/v1/video/transcript",
    credits: 1,
    tagline: "Whisper transcription of an uploaded file — 1 credit/min; durationSeconds + creditsCharged in the response.",
    longDescription:
      "POST multipart form field `file` (not a query string). Returns transcript, transcriptSegments[{text,start,duration,timestamp}], wordCount, segments, language, durationSeconds (alias duration), creditsCharged, and noSpeech. Optional form fields: language (ISO-639-1 hint), translate=true (English), timestampGranularity=segment|word. Limits: 200MB / 60 minutes. No speech → empty transcript + noSpeech=true (still billed for duration). Billed 1 credit per minute of audio (rounded up, min 1) — verify with creditsCharged.",
  },
  {
    slug: "video-summarize",
    name: "Video File Summarizer API",
    shortName: "File Summarizer",
    category: "summarize",
    method: "POST",
    path: "/v1/video/summarize",
    credits: 2,
    tagline: "Whisper + AI summary of an uploaded file — transcript included; 1 credit/min + 1.",
    longDescription:
      "POST multipart form field `file` (use curl -F file=@path — not a query string). Whisper-transcribes the upload, then GPT-4o-mini returns summary, keyPoints, topics, and sentiment in the same JSON as the full transcript (transcript, transcriptSegments, wordCount, language, durationSeconds / duration, creditsCharged). Summary length scales with the audio — short clips may be one paragraph with fewer bullets; longer recordings aim for 2–3 paragraphs and 4–8 key points. Same Whisper controls (language, translate, timestampGranularity) and 200MB / 60 min limits as File Transcript. Empty/no-speech → HTTP 422. Billing: ceil(durationSeconds/60) + 1.",
    delivers: [
      "AI summary + keyPoints + topics + sentiment (GPT-4o-mini)",
      "Full Whisper transcript + timed segments in the same response",
      "language, durationSeconds, and creditsCharged for bill verification",
      "POST multipart file upload — same Whisper controls as File Transcript",
    ],
  },
];

const KWAI: Spec[] = [
  {
    slug: "kwai-profile",
    name: "Kwai Profile API",
    shortName: "Profile",
    category: "channel",
    method: "GET",
    path: "/v1/kwai/profile",
    credits: 1,
    tagline:
      "Fetch Kwai profile — display name, bio, counts, and verification as structured JSON.",
    longDescription:
      "Pass a Kwai profile URL or @handle and get the public account as clean JSON — one fixed key set on every profile: id (Kwai's opaque eid string — no twin eid key), username, displayName, bio, avatar, verified, verifiedDescription, gender, followers, following, likedCount, publicPostCount, privatePostCount, postCount (= public + private when both known), isPrivate. Sparse fields are null, never omitted (verifiedDescription / gender / privatePostCount included). No videoCount (Kwai posts are videos — structurally equal to postCount). No verifiedNumber (Kwai's verified_num is an undocumented enum; use verified + verifiedDescription). No redundant raw{}. Parsed from Kwai's public web page (JSON-LD + Nuxt SSR state). Note: Kwai's web surface sometimes stubs follower/following to 1; when that happens we prefer schema.org counts for followers and set following to null rather than ship a fake 1. Flat 1 credit.",
    delivers: [
      "verifiedDescription / gender / privatePostCount always present",
      "postCount = public + private when both known",
      "No eid twin, no videoCount, no verifiedNumber",
    ],
    platformLimits: [
      "publicPostCount can diverge from postCount when privatePostCount > 0; videoCount is never emitted (posts ≡ videos).",
      "verifiedNumber is not exposed — Kwai's verified_num values beyond 0 (none) and 3 (Conta Oficial) are not documented upstream.",
    ],
  },
  {
    slug: "kwai-user-posts",
    name: "Kwai User Posts API",
    shortName: "User Posts",
    category: "list",
    method: "GET",
    path: "/v1/kwai/user-posts",
    credits: 20,
    creditsPerResult: 1,
    tagline:
      "Kwai profile posts — caption (\"\" when none), engagement, mp4 + transcript (~1 credit/post).",
    longDescription:
      "Pass a Kwai profile URL or @handle and get that creator's public posts as clean JSON. Each post: id/url, text (the post caption only — empty string when none; never Kwai's SEO title / \"Áudio original criado por …\" boilerplate), hashtags[] (always present — [] when the caption has no tags), publishedAt, durationSeconds, thumbnailUrl, videoUrl with videoType (\"mp4\" or \"hls\"), mediaUrlsExpireAt parsed from the signed CDN tag=, engagement{views,likes,comments,shares}, and transcript when Kwai's JSON-LD auto-captions are present (duplicate merged tracks are deduped). Author{id,username,displayName,avatar,url} is returned once at the top — not repeated on every row. Envelope uses url (the requested profile) — same key as /kwai/post and /kwai/profile. HARD PAGE LIMIT: Kwai's public web only SSR-embeds a first-page window of posts (typically a handful — observed ~6 on large accounts), not the full postCount from /kwai/profile. hasMore/nextCursor page within that window; hasMore=false means the window is exhausted, not that the account has no more posts upstream. ~1 credit per post returned (min 2; default limit 20 → ~20 credits). Transcript is included when Kwai publishes it — not a separate Whisper bill. Shares _normalize_post with /kwai/post.",
    delivers: [
      "Posts with engagement + signed mp4 videoUrl",
      "hashtags[] always present ([] when none)",
      "hasMore/nextCursor within SSR first-page window",
      "Author{} once; envelope url",
    ],
    platformLimits: [
      "hasMore=false is end of Kwai's SSR first-page window, not the account archive. Use /kwai/profile postCount for universe size — there is no public deep-archive pagination API.",
    ],
  },
  {
    slug: "kwai-post",
    name: "Kwai Post API",
    shortName: "Post",
    category: "details",
    method: "GET",
    path: "/v1/kwai/post",
    credits: 2,
    tagline:
      "Single Kwai video — caption (\"\" when none), hashtags[], author, mp4 (2 credits).",
    longDescription:
      "Pass a Kwai video URL and get one post as clean JSON: same core card as a user-posts row (text = caption only, empty string when the post has none — never SEO title boilerplate; hashtags[] always present — [] when none; author{}, engagement, videoUrl/videoType, mediaUrlsExpireAt, transcript when Kwai exposes auto-captions). Flat 2 credits — priced in line with one list item, not the old 17-credit Apify-era rate. Shares _normalize_post with /kwai/user-posts.",
    delivers: [
      "text = caption only (\"\" when none)",
      "hashtags[] always present ([] when none)",
      "author{} + engagement{}",
      "videoUrl / videoType / mediaUrlsExpireAt",
    ],
    platformLimits: [
      "text is never synthesised from meta description, og:description, author name, or audio title — empty caption → \"\".",
      "hashtags is never omitted — empty caption / no tags → [].",
    ],
  },
];

const KOMI: Spec[] = [
  {
    slug: "komi-page",
    name: "Komi Page API",
    shortName: "Page",
    category: "channel",
    method: "GET",
    path: "/v1/komi/page",
    credits: 1,
    tagline:
      "Komi link-in-bio → identity, socials{} (incl. website), content LINK/PRODUCT rows with price/currency. Flat 1 credit.",
    longDescription:
      "Paste a Komi URL (komi.io/user or user.komi.io) and get the public page as clean JSON. Identity: id (string UUID), username, url, displayName, firstName/lastName, bio (may be an empty string), avatar. socials{} maps typed Komi social icons (instagram/tiktok/youtube/twitter/facebook/snapchat/spotify/appleMusic/…) and includes website when the creator publishes a WEBSITE row. links[] are content modules only — every row shares the same keys (id, moduleId, versionId, order, type, title, url, visible, thumbnail, price, currency); absent values are null, never missing keys. type distinguishes PRODUCT (price/currency filled) from LINK/YOUTUBE_VIDEO. YouTube embed rows read title/thumbnail from item.metadata when the module label is empty. Social icon rows are not duplicated into links[]. Komi does not expose follower counts or a verified badge. Flat 1 credit via Komi's public JSON APIs (not HTML scrape). Pass cache=true or cacheMaxAge (1d/3d/7d/14d/30d) for the shared response cache.",
    delivers: [
      "Page id + displayName + bio (empty string when unset)",
      "socials{} incl. website when published",
      "Content links[] with id/thumbnail/order/visible",
      "PRODUCT price + currency for commerce rows",
    ],
  },
];

const PILLAR: Spec[] = [
  {
    slug: "pillar-page",
    name: "Pillar Page API",
    shortName: "Page",
    category: "channel",
    method: "GET",
    path: "/v1/pillar/page",
    credits: 1,
    tagline:
      "Pillar link-in-bio → identity, socials{}, links[] with per-link clicks, products[]. Flat 1 credit.",
    longDescription:
      "Paste a Pillar URL (pillar.io/user) and get the public page as clean JSON. Identity: id (string UUID), handle/username, url, displayName (name is a deprecated alias), firstName/lastName, bio (description is a deprecated alias — may be an empty string), avatar, location, email. socials{} maps Pillar banner + connected channels (instagram/tiktok/youtube/twitter/facebook/spotify/soundcloud/linkedin/snapchat/patreon/discord/twitch/medium/amazon/appleAppStore/googleAppStore/…). links[] are custom link rows with id, type, title, url, clicks (public per-link click counts — Pillar's unique performance signal), and order. products[] carries featured commerce rows (id, title/name, price, url, description, image). Pillar does not expose follower counts or a verified badge on this endpoint. Flat 1 credit via Pillar's public GraphQL API (not HTML scrape). Pass cache=true or cacheMaxAge (1d/3d/7d/14d/30d) for the shared response cache.",
    delivers: [
      "Page id + displayName + bio + location + email",
      "socials{} incl. patreon/discord/twitch/amazon/app stores when published",
      "links[] with clicks / id / type / order",
      "products[] with title, price, url, description, image",
    ],
  },
];

const LINKBIO: Spec[] = [
  {
    slug: "linkbio-page",
    name: "Linkbio Page API",
    shortName: "Page",
    category: "channel",
    method: "GET",
    path: "/v1/linkbio/page",
    credits: 1,
    tagline:
      "lnk.bio → id, socials{} (SC often null), titled links[], website/email/whatsapp, other[]. Flat 1 credit.",
    longDescription:
      "Paste an lnk.bio URL and get the public page as clean JSON. Identity: id (lnk.bio numeric string, e.g. \"-1344625\"), handle/username, url, avatar. displayName/name are emitted only when lnk.bio publishes a real display name — @handle OG titles are not synthesised (null/omitted). socials{} is derived from data-network icon rows and username CTAs (facebook/twitter/instagram/tiktok/youtube/snapchat/triller/website/whatsapp/…) — ScrapeCreators often leaves these null even when the matching URL sits in links[]. other[] holds typed social networks we could not map to a known key so nothing disappears. Top-level website / email / whatsapp when published. links[] includes content buttons (pb-linkbox) plus primary social icons with titles from icon labels (Facebook, Instagram, Triller, …) — not null. lnk.bio does not expose follower counts or a verified badge. Flat 1 credit. Pass cache=true or cacheMaxAge (1d/3d/7d/14d/30d).",
    delivers: [
      "lnk.bio id + avatar + handle (no fabricated displayName)",
      "socials{} filled from icon rows — beats SC's null social fields",
      "links[] with titles on social rows + content buttons",
      "website / email / whatsapp + other[] for unmapped networks",
    ],
  },
];

const LINKME: Spec[] = [
  {
    slug: "linkme-profile",
    name: "Linkme Profile API",
    shortName: "Profile",
    category: "channel",
    method: "GET",
    path: "/v1/linkme/profile",
    credits: 1,
    tagline:
      "Linkme profile → bio, profileVisitCount, featured links, webLinks, email/infoLinks, stripeStatus. Flat 1 credit.",
    longDescription:
      "Paste a Linkme URL (link.me/danucd) and get the public profile from Linkme's dehydrated SSR payload (TanStack $tsr) — not HTML meta tags or the site footer. Identity: id, username, displayName, firstName/lastName when distinct, bio, avatar + isDefaultProfilePicture. Audience: profileVisitCount (e.g. 15.9k) and totalLinks (Linkme's SSR counter — not links[].length). Flags: verifiedAccount, isAmbassador, isPrivate. Timestamps: createdAt/updatedAt. links[] are featured CTA rows; webLinks[] are social icon groups; infoLinks[] carry email/contact — three separate buckets, not a union. stripeStatus{tipsEnabled,stripeEnabled} signals monetization; socials{} + other[] cover mapped/unmapped networks. Flat 1 credit. Pass cache=true or cacheMaxAge (1d/3d/7d/14d/30d) for the shared response cache.",
  },
];

const FACEBOOK_AD_LIBRARY: Spec[] = [
  {
    slug: "facebook-ad-library-search",
    name: "Facebook Ad Library Search API",
    shortName: "Search",
    category: "search",
    method: "GET",
    path: "/v1/ad-library/facebook/search",
    credits: 2,
    tagline:
      "Search Meta Ad Library by keyword — active/inactive, media type, date range, platforms, cursor, and spend/impressions when Meta publishes them.",
    longDescription:
      "Search Meta's Ad Library and get competitor creatives as clean JSON — SC filter set: status (default ACTIVE), media_type, platforms, ad_type, search_type (exact phrase), sort_by (total_impressions|relevancy_monthly_grouped), start_date/end_date, cursor, trim. Cursor pages the current HTML result batch via nextCursor (not Meta's multi-thousand POST cursor). Same advertiser id collapses to one name within a response. Each ad: text/headline/cta/ctaType/landingUrl, media[] plus typed images/videos + cards[], isActive, publisherPlatforms, pageLikeCount/pageCategories/pageEntityType, politicalCountries, reachEstimate, spend/impressions when Meta publishes them (political/issue ads — commercial usually null). searchResultsCount is best-effort. Flat 2 credits on the native path.",
    platformLimits: [
      "Meta's Ad Library GET/HTML search surface soft-caps around ~1,500 results. Cursor ends when Meta stops — deeper archives need Meta's authenticated POST library tools, not this endpoint.",
    ],
  },
  { slug: "facebook-ad-library-company-ads", name: "Facebook Company Ads API", shortName: "Company Ads", category: "list", method: "GET", path: "/v1/ad-library/facebook/company-ads", credits: 2 },
  {
    slug: "facebook-ad-library-search-companies",
    name: "Facebook Ad Library Search Companies API",
    shortName: "Search Companies",
    category: "search",
    method: "GET",
    path: "/v1/ad-library/facebook/search-companies",
    credits: 2,
    tagline:
      "Find Meta Ad Library pages by brand — name-matched, pageId for company-ads (not profileId).",
    longDescription:
      "Search Meta Ad Library advertisers/pages by brand name. Results are relevance-filtered so query tokens must appear in the page name — off-brand pages that merely appeared near the keyword (e.g. Sukeban for q=nike) are dropped; empty beats spam. Each company returns id = pageId = advertiserId (pass to /facebook/company-ads), profileId when the facebook.com/{digits}/ URL uses a different numeric identity, vanity or numeric url, logo, and libraryUrl (ready view_all_page_id link). Chain: search-companies → companies[0].pageId → company-ads?url=. Flat 2 credits.",
    delivers: [
      "Name-matched ranking (exact brand first)",
      "pageId / advertiserId for company-ads (view_all_page_id)",
      "profileId when facebook.com/{digits}/ ≠ pageId",
      "libraryUrl ready for Ad Library page view",
      "Empty beats off-brand spam",
    ],
  },
  {
    slug: "facebook-ad-library-ad-details",
    name: "Facebook Ad Details API",
    shortName: "Ad Details",
    category: "details",
    method: "GET",
    path: "/v1/ad-library/facebook/ad-details",
    credits: 2,
    tagline:
      "One Meta ad by ID — same creative as search, plus delivery breakdowns when Meta publishes them.",
    longDescription:
      "Paste a Meta Ad Library ad URL or archive ID and get that creative as clean JSON. Creative fields (text, headline, cta, landingUrl, media, advertiser) match a search hit for the same id — use this for ID lookup without paging search. Delivery extras when Meta publishes them (mostly political/issue and EU AAA ads): platforms / publisherPlatforms, demographicDistribution[], regionDistribution[], ageCountryGenderReachBreakdown / euTransparency, variantCount (collation), isAaaEligible. On commercial ads Meta often withholds those breakdowns — keys stay present as null so the schema is stable. Flat 2 credits on the native path.",
    delivers: [
      "ID lookup without paging Ad Library search",
      "platforms / publisherPlatforms when Meta lists them",
      "demographicDistribution[] + regionDistribution[] when published",
      "EU AAA: euTransparency + ageCountryGenderReachBreakdown",
      "variantCount (collation) + isAaaEligible",
      "Stable null keys when Meta withholds delivery extras",
    ],
  },
  { slug: "facebook-ad-library-ad-transcript", name: "Facebook Ad Transcript API", shortName: "Ad Transcript", category: "transcript", method: "GET", path: "/v1/ad-library/facebook/ad-transcript", credits: 2 , tagline: "Get a Meta Ad Library ad's creative text — headline, body, CTA, and landing URL as a transcript-style payload.", longDescription: "Paste a Meta Ad Library ad URL or ad ID and get the creative copy as structured transcript text (headline, body, CTA, landing URL). Flat 2 credits per call." },
];

const TIKTOK_AD_LIBRARY: Spec[] = [
  {
    slug: "tiktok-ad-library-search",
    name: "TikTok Ad Library Search API",
    shortName: "Search",
    category: "search",
    method: "GET",
    path: "/v1/ad-library/tiktok/search",
    credits: 2,
    tagline:
      "Search TikTok Commercial Content Library — relevance-filtered, uniform null schema (2 credits).",
    longDescription:
      "Search TikTok's Commercial Content Library (library.tiktok.com / EU DSA) by keyword. Local keyword matching is case-insensitive whole-word match=any|all (hair ≠ wheelchair). Envelope uses candidatesScanned / truncated (true when literalMatches > totalReturned); each hit has matchedFrom as a string array of matched fields. platform is tiktok (library=dsa). media[] are objects with url/type/expiresAt when signed. Ads share a uniform key set — withheld fields are null, not missing. firstShown/lastShown are omitted (DSA list XHR stamps scrape/serve times, not run dates) — use /tiktok/ad-details for calendar-day ISO dates. advertiser is always {id,name,url,logo,location}. Flat 2 credits when results are returned (empty is free); Apify fallback capped at 5. Hard-capped at 110s. country default GB (US often empty). For brand performance use /v1/ad-library/tiktok/top-ads.",
  },
  {
    slug: "tiktok-ad-library-top-ads",
    name: "TikTok Creative Center Top Ads API",
    shortName: "Top Ads",
    category: "search",
    method: "GET",
    path: "/v1/ad-library/tiktok/top-ads",
    credits: 20,
    creditsPerResult: 1,
    tagline:
      "TikTok Creative Center Top Ads — browser-intercepted list XHR, CTR/likes, video (flat 2 / ~1 Apify).",
    longDescription:
      "Pull high-performing auction ads from TikTok Creative Center Top Ads as clean JSON: id, url (per-ad detail page), title, brandName (= advertiser.name), advertiser{id,name}, likes + likesIsApproximate, ctr, costTier when present, resolved industry/industryKey, objective, and video{} (urlHd only when a distinct HD rendition exists). Creative Center does not expose ad run dates on the list surface — use /tiktok/ad-details (DSA) for firstShown/lastShown (search omits them). Optional ctrTier/isSparkAd appear only when upstream ships them (never null-padded). Keyword q is case-insensitive whole-word match=any|all on title/brand/tags/industry (hair ≠ wheelchair); each hit includes matchedFrom (field names that matched) and the envelope reports candidatesScanned/filteredOut/literalMatches/matchBasis — zero literal hits return empty ads[], never the unfiltered leaderboard. Empty results and upstream timeouts are never charged. A real browser is required — Creative Center HTML is an empty shell and the list API needs page-signed requests. We intercept the signed top_ads/v2/list XHR and exit when that JSON arrives (typically 30-60 seconds; not networkidle). Flat 2 credits on the browser path; Apify fallback ~1 credit per returned ad (min 2; ~20 at default limit). truncated:true only when a non-empty page is shorter than limit while Creative Center still has pages (empty after filter → truncated:false). Pass cache=true for a 24h hit (0 credits).",
    delivers: [
      "advertiser{id,name} for grouping + Spark author fallback",
      "Honest keyword filter — per-ad matchedFrom + candidatesScanned envelope",
      "No always-null date/flag fields (CC list has no run dates)",
      "Signed list XHR early-exit (30–60s typical); empty/timeout free",
    ],
    platformLimits: [
      "This endpoint queries TikTok Creative Center live in a browser and typically takes 30-60 seconds. Set your HTTP client timeout to at least 120 seconds. Note that nginx and AWS ALB default to 60s and Heroku caps at 30s.",
      "Creative Center HTML has no ad data — unsigned list API calls return no permission. Anonymous access may be capped; truncated:true means we exited before filling limit while more pages existed.",
    ],
  },
  {
    slug: "tiktok-ad-library-ad-details",
    name: "TikTok Ad Details API",
    shortName: "Ad Details",
    category: "details",
    method: "GET",
    path: "/v1/ad-library/tiktok/ad-details",
    credits: 2,
    tagline:
      "One TikTok Commercial Content Library ad by ID — calendar-day dates, always 2 credits.",
    longDescription:
      "Paste a TikTok Ad Library URL or ad ID and get that creative as clean JSON with the same uniform key set as /tiktok/search (null when withheld) plus calendar-day ISO firstShown/lastShown (search omits those). platform=tiktok, library=dsa, media[] objects, impressions from Unique users seen when disclosed, spend only when shipped. advertiser is always {id,name,url,logo,location} — name is a human label, never a bare numeric id. Always 2 credits on success — native and Apify fallback share one price (no 2-vs-5 surprise). Response includes fetchPath: \"native\" | \"fallback\" so you can see which path ran. Default country GB (EU-led library).",
    delivers: [
      "ID lookup with search-parity fields (including impressions)",
      "Uniform null keys + advertiser{id,name,url,logo,location}",
      "Calendar-day ISO firstShown / lastShown",
      "Always 2 credits; fetchPath native|fallback",
    ],
  },
];

const GOOGLE_AD_LIBRARY: Spec[] = [
  {
    slug: "google-ad-library-company-ads",
    name: "Google Company Ads API",
    shortName: "Company Ads",
    category: "list",
    method: "GET",
    path: "/v1/ad-library/google/company-ads",
    credits: 2,
    tagline:
      "List an advertiser's Google Ads Transparency creatives — AR chain, cursor, dates, sort (2 credits).",
    longDescription:
      "Pass an advertiser name, domain (nike.com), or AR… id from advertiser-search and get public commercial creatives as clean JSON. Response includes resolvedAdvertiser{id,name,url} (the entity actually queried), stable nulls for text/headline/cta/landingUrl/spend/impressions when ATC withholds them, firstShown/lastShown, adFormat, and media[]. Supports country/region, start_date/end_date, sort=last_shown|first_shown, cursor pagination (nextCursor + hasMore), and adsCountEstimate. Prefer advertiser=AR… from /google/advertiser-search for a deterministic chain. Spend/impressions are usually null for commercial ads (Google only publishes them for political). Flat 2 credits on the native path (max 200 per page).",
  },
  {
    slug: "google-ad-library-ad-details",
    name: "Google Ad Details API",
    shortName: "Ad Details",
    category: "details",
    method: "GET",
    path: "/v1/ad-library/google/ad-details",
    credits: 2,
    tagline:
      "One Google ATC creative by AR…+CR… — text/headline/impressions + countries[] ISO (not an alias of company-ads).",
    longDescription:
      "Paste a Google Ads Transparency URL with both AR… advertiser and CR… creative IDs. Unlike company-ads list rows, ad-details adds text, headline, landingUrl, and impressions when ATC publishes them. Response id and advertiser.id always match the request — Nike, Inc. / Nike Retail BV / NIKE SRL are different legal entities and are never swapped. countries[] is ISO-3166 alpha-2 (country is a single ISO only when unambiguous). textIsTemplate is true when Dynamic Keyword Insertion macros like {KeyWord:Nike Shoes} appear. Chain: advertiser-search → company-ads?advertiser=AR… → ad-details with that AR + a CR from ads[]. Flat 2 credits native; Apify fallback capped at 5.",
    delivers: [
      "text / headline / landingUrl / impressions beyond company-ads rows",
      "Strict AR+CR identity (no cross-entity Nike swaps)",
      "countries[] ISO codes (not a comma-name string)",
      "textIsTemplate for Google Ads DKI macros",
      "Flat 2 credits native; Apify cap 5",
    ],
  },
  {
    slug: "google-ad-library-advertiser-search",
    name: "Google Advertiser Search API",
    shortName: "Advertiser Search",
    category: "search",
    method: "GET",
    path: "/v1/ad-library/google/advertiser-search",
    credits: 1,
    tagline: "Find Google Ads Transparency AR… entities — ranked multi-result (1 credit).",
    longDescription:
      "Search advertisers on Google Ads Transparency and get ranked AR… entities with name, url, optional country/adsCount. Brand queries are expanded (nike → Nike, Inc. + regional entities) so country=US prefers the parent company over NIKE SRL. Pass advertisers[0].id into /google/company-ads?advertiser=AR… to complete the chain. Flat 1 credit.",
  },
];

const LINKEDIN_AD_LIBRARY: Spec[] = [
  {
    slug: "linkedin-ad-library-search-ads",
    name: "LinkedIn Ad Library Search API",
    shortName: "Search Ads",
    category: "search",
    method: "GET",
    path: "/v1/ad-library/linkedin/search-ads",
    credits: 2,
    tagline:
      "LinkedIn Ad Library search — targeting{}, ISO dates, impressions, CTA/destination, cursor pagination (2 credits).",
    longDescription:
      "Search LinkedIn's Ad Library and get transparency fields as clean JSON: headline + description, targeting{language, location, company, …}, ISO startDate/endDate + adDuration, totalImpressions + impressionsByCountry[], cta + destinationUrl, advertiser{id, name, url, logo}, media[] / carouselImages[]. Filter with q (advertiser), keyword, companyId, country or countries (US,CA,MX), and startDate/endDate. Page with cursor / paginationToken (nextCursor + hasMore + totalAds). Flat 2 credits on the native path.",
    delivers: [
      "targeting{} — language, location, company, and other LinkedIn targeting segments",
      "ISO startDate/endDate, adDuration, totalImpressions, impressionsByCountry[]",
      "cta, destinationUrl, headline/description split, advertiser id + LinkedIn page URL",
      "Cursor pagination via paginationToken / nextCursor + totalAds",
    ],
  },
  {
    slug: "linkedin-ad-library-ad-details",
    name: "LinkedIn Ad Details API",
    shortName: "Ad Details",
    category: "details",
    method: "GET",
    path: "/v1/ad-library/linkedin/ad-details",
    credits: 2,
    tagline:
      "One LinkedIn Ad Library ad by ID — headline, targeting, advertiser.id from /company/{id} (2 credits).",
    longDescription:
      "Paste a LinkedIn Ad Library URL or ad ID. Detail pages add headline, destination/landingUrl, targeting{}, impressionsByCountry[], and advertiser.url when LinkedIn publishes them. advertiser.id is extracted from linkedin.com/company/{id} so you can join to LinkedIn Company endpoints. Schema keeps null keys for country/logo so details is never thinner by omission vs search. Flat 2 credits native; Apify fallback capped at 5.",
    delivers: [
      "headline + landingUrl/destination when published",
      "advertiser.id from /company/{id} (joinable)",
      "targeting{} + impressionsByCountry[]",
      "Stable null keys (country, logo) — no silent field loss",
      "Flat 2 credits native; Apify cap 5",
    ],
  },
];

export const PLATFORM_GROUPS: PlatformGroup[] = [
  {
    id: "youtube",
    name: "YouTube & Shorts",
    blurb: "Extract transcripts, summaries, stats, comments, and more from YouTube videos and Shorts.",
    icon: "youtube",
    color: "text-red-500",
    exampleUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    endpoints: YOUTUBE.map((s) => ({ ...s, platform: "youtube" as const })),
  },
  {
    id: "tiktok",
    name: "TikTok",
    blurb: "Analyze TikTok videos with transcripts, summaries, engagement metrics, and comments.",
    icon: "tiktok",
    color: "text-foreground",
    exampleUrl: "https://www.tiktok.com/@username/video/7311234567890123456",
    endpoints: TIKTOK.map((s) => ({ ...s, platform: "tiktok" as const })),
  },
  {
    id: "instagram",
    name: "Instagram Reels",
    blurb: "Extract data from Instagram Reels and posts including transcripts and profile analytics.",
    icon: "instagram",
    color: "text-fuchsia-500",
    exampleUrl: "https://www.instagram.com/reel/CzKZqfdN5j8/",
    endpoints: INSTAGRAM.map((s) => ({ ...s, platform: "instagram" as const })),
  },
  {
    id: "facebook",
    name: "Facebook",
    blurb: "Pull details, summaries, and comments from public Facebook videos and pages.",
    icon: "facebook",
    color: "text-blue-600",
    exampleUrl: "https://www.facebook.com/watch/?v=1234567890123456",
    endpoints: FACEBOOK.map((s) => ({ ...s, platform: "facebook" as const })),
  },
  {
    id: "twitter",
    name: "Twitter / X",
    blurb: "Pull tweet metadata and engagement, profiles, timelines, and keyword search from Twitter / X.",
    icon: "twitter",
    color: "text-sky-500",
    exampleUrl: "https://x.com/NASA/status/1816004914774937656",
    endpoints: TWITTER.map((s) => ({ ...s, platform: "twitter" as const })),
  },
  {
    id: "reddit",
    name: "Reddit",
    blurb: "Fetch subreddit posts, post details and stats, comment threads, and keyword search from Reddit.",
    icon: "reddit",
    color: "text-orange-500",
    exampleUrl: "https://www.reddit.com/r/technology/comments/1a2b3c4/example_discussion_thread/",
    endpoints: REDDIT.map((s) => ({ ...s, platform: "reddit" as const })),
  },
  {
    id: "threads",
    name: "Threads",
    blurb: "Extract Threads profiles, post timelines, and individual post metadata and engagement.",
    icon: "threads",
    color: "text-foreground",
    exampleUrl: "https://www.threads.net/@zuck/post/C8H1abcdEFG",
    endpoints: THREADS.map((s) => ({ ...s, platform: "threads" as const })),
  },
  {
    id: "bluesky",
    name: "Bluesky",
    blurb: "Pull Bluesky profiles, post timelines, and post details via the public AT-Protocol API.",
    icon: "bluesky",
    color: "text-sky-400",
    exampleUrl: "https://bsky.app/profile/bsky.app/post/3kabcd2efg2h",
    endpoints: BLUESKY.map((s) => ({ ...s, platform: "bluesky" as const })),
  },
  {
    id: "pinterest",
    name: "Pinterest",
    blurb: "Extract Pinterest pin details and saves, user pins, and keyword search results.",
    icon: "pinterest",
    color: "text-red-600",
    exampleUrl: "https://www.pinterest.com/pin/99360735500167749/",
    endpoints: PINTEREST.map((s) => ({ ...s, platform: "pinterest" as const })),
  },
  {
    id: "linkedin",
    name: "LinkedIn",
    blurb: "Pull public LinkedIn person profiles, company pages, and post engagement metrics.",
    icon: "linkedin",
    color: "text-blue-700",
    exampleUrl: "https://www.linkedin.com/posts/williamhgates_example-activity-7180000000000000000-abcd",
    endpoints: LINKEDIN.map((s) => ({ ...s, platform: "linkedin" as const })),
  },
  {
    id: "rumble",
    name: "Rumble",
    blurb: "Extract Rumble video details and stats, channel video lists, and keyword search.",
    icon: "rumble",
    color: "text-green-600",
    exampleUrl: "https://rumble.com/v4abcd-example-video.html",
    endpoints: RUMBLE.map((s) => ({ ...s, platform: "rumble" as const })),
  },
  {
    id: "tiktok_shop",
    name: "TikTok Shop",
    blurb: "Research TikTok Shop products, reviews, stores, and creator showcases for ecommerce intelligence.",
    icon: "tiktok",
    color: "text-foreground",
    exampleUrl: "https://shop.tiktok.com/us/pdp/example-product/1234567890",
    endpoints: TIKTOK_SHOP.map((s) => ({ ...s, platform: "tiktok_shop" as const })),
  },
  {
    id: "facebook_marketplace",
    name: "Facebook Marketplace",
    blurb: "Search Facebook Marketplace listings by keyword and location, resolve places, and fetch item details.",
    icon: "facebook",
    color: "text-blue-600",
    exampleUrl: "https://www.facebook.com/marketplace/",
    endpoints: FACEBOOK_MARKETPLACE.map((s) => ({ ...s, platform: "facebook_marketplace" as const })),
  },
  {
    id: "facebook_events",
    name: "Facebook Events",
    blurb: "Search Facebook events, pull event details, and list events from a public profile or page.",
    icon: "facebook",
    color: "text-blue-600",
    exampleUrl: "https://www.facebook.com/events/",
    endpoints: FACEBOOK_EVENTS.map((s) => ({ ...s, platform: "facebook_events" as const })),
  },
  {
    id: "facebook_ad_library",
    name: "Facebook Ad Library",
    blurb: "Search Meta Ad Library creatives, advertisers, and company ads for competitor research.",
    icon: "facebook",
    color: "text-blue-600",
    exampleUrl: "https://www.facebook.com/ads/library/",
    endpoints: FACEBOOK_AD_LIBRARY.map((s) => ({ ...s, platform: "facebook_ad_library" as const })),
  },
  {
    id: "tiktok_ad_library",
    name: "TikTok Ad Library",
    blurb:
      "Search TikTok's Commercial Content Library (EU DSA), pull Creative Center Top Ads with performance metrics, and fetch ad details.",
    icon: "tiktok",
    color: "text-foreground",
    exampleUrl: "https://library.tiktok.com/",
    endpoints: TIKTOK_AD_LIBRARY.map((s) => ({ ...s, platform: "tiktok_ad_library" as const })),
  },
  {
    id: "google_ad_library",
    name: "Google Ad Library",
    blurb: "Search Google Ads Transparency Center advertisers and pull company ads or creative details.",
    icon: "google",
    color: "text-foreground",
    exampleUrl: "https://adstransparency.google.com/",
    endpoints: GOOGLE_AD_LIBRARY.map((s) => ({ ...s, platform: "google_ad_library" as const })),
  },
  {
    id: "linkedin_ad_library",
    name: "LinkedIn Ad Library",
    blurb: "Search LinkedIn Ad Library ads and fetch creative details for B2B competitor intelligence.",
    icon: "linkedin",
    color: "text-blue-700",
    exampleUrl: "https://www.linkedin.com/ad-library/",
    endpoints: LINKEDIN_AD_LIBRARY.map((s) => ({ ...s, platform: "linkedin_ad_library" as const })),
  },
  {
    id: "amazon_shop",
    name: "Amazon Seller Storefront",
    blurb:
      "Third-party seller storefronts (/sp?seller=) with ASIN + canonical /dp URLs — not influencer amazon.com/shop/{handle} vitrines.",
    icon: "amazon",
    color: "text-amber-500",
    exampleUrl: "https://www.amazon.com/s?me=ATVPDKIKX0DER",
    endpoints: AMAZON_SHOP.map((s) => ({ ...s, platform: "amazon_shop" as const })),
  },
  {
    id: "github",
    name: "GitHub",
    blurb: "Pull public GitHub users, repositories, pull requests, activity, followers, and trending repos.",
    icon: "github",
    color: "text-foreground",
    exampleUrl: "https://github.com/vercel/next.js",
    endpoints: GITHUB.map((s) => ({ ...s, platform: "github" as const })),
  },
  {
    id: "twitch",
    name: "Twitch",
    blurb: "Pull Twitch channel profiles, VOD lists, public schedules, and clip metadata.",
    icon: "video",
    color: "text-purple-500",
    exampleUrl: "https://www.twitch.tv/shroud",
    endpoints: TWITCH.map((s) => ({ ...s, platform: "twitch" as const })),
  },
  {
    id: "spotify",
    name: "Spotify",
    blurb:
      "Extract Spotify artist intel (monthly listeners, top cities, top tracks with play counts), plus track, album, podcast, episode, and search metadata.",
    icon: "music",
    color: "text-green-500",
    exampleUrl: "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02",
    endpoints: SPOTIFY.map((s) => ({ ...s, platform: "spotify" as const })),
  },
  {
    id: "soundcloud",
    name: "SoundCloud",
    blurb: "Fetch SoundCloud artist profiles, artist tracks, and track engagement metadata.",
    icon: "cloud",
    color: "text-orange-500",
    exampleUrl: "https://soundcloud.com/nasa",
    endpoints: SOUNDCLOUD.map((s) => ({ ...s, platform: "soundcloud" as const })),
  },
  {
    id: "linktree",
    name: "Linktree",
    blurb:
      "Link-in-bio → creator graph: typed links, socialAccounts{} for TikTok/Instagram/Spotify/SoundCloud joins, email, verticals.",
    icon: "link",
    color: "text-lime-500",
    exampleUrl: "https://linktr.ee/tonyhawk",
    endpoints: LINKTREE.map((s) => ({ ...s, platform: "linktree" as const })),
  },
  {
    id: "snapchat",
    name: "Snapchat",
    blurb: "Pull public Snapchat profile cards with subscriber counts, bios, and highlights.",
    icon: "ghost",
    color: "text-yellow-500",
    exampleUrl: "https://www.snapchat.com/@nba",
    endpoints: SNAPCHAT.map((s) => ({ ...s, platform: "snapchat" as const })),
  },
  {
    id: "truth_social",
    name: "Truth Social",
    blurb:
      "Prominent public Truth Social profiles/posts only — as of late 2025 most accounts require auth and will 404. Flat 1 credit on profile/post.",
    icon: "threads",
    color: "text-red-700",
    exampleUrl: "https://truthsocial.com/@realDonaldTrump",
    endpoints: TRUTH_SOCIAL.map((s) => ({ ...s, platform: "truth_social" as const })),
  },
  {
    id: "kick",
    name: "Kick",
    blurb: "Extract Kick clip metadata from clip URLs or recent channel clips.",
    icon: "video",
    color: "text-green-500",
    exampleUrl: "https://kick.com/xqc",
    endpoints: KICK.map((s) => ({ ...s, platform: "kick" as const })),
  },
  {
    id: "account",
    name: "CaptAPI Account",
    blurb:
      "Your key-scoped credit balance, request history, daily usage, and most-used routes — free, no credits charged.",
    icon: "captapi",
    color: "text-emerald-600",
    exampleUrl: "https://captapi.com/dashboard",
    endpoints: ACCOUNT.map((s) => ({ ...s, platform: "account" as const })),
  },
  {
    id: "utilities",
    name: "Analytics & Video Files",
    blurb: "Cross-platform post analytics and Whisper transcription/summarization for uploaded video or audio files.",
    icon: "video",
    color: "text-slate-600",
    exampleUrl: "https://captapi.com/docs#api-analytics",
    endpoints: UTILITIES.map((s) => ({ ...s, platform: "utilities" as const })),
  },
  {
    id: "kwai",
    name: "Kwai",
    blurb: "Extract Kwai profile details, user posts, and post metadata.",
    icon: "video",
    color: "text-orange-500",
    exampleUrl: "https://www.kwai.com/@topfilmeseseriesnatv",
    endpoints: KWAI.map((s) => ({ ...s, platform: "kwai" as const })),
  },
  {
    id: "komi",
    name: "Komi",
    blurb: "Komi link-in-bio pages — identity, socials (incl. website), LINK/PRODUCT commerce rows.",
    icon: "link",
    color: "text-violet-500",
    exampleUrl: "https://komi.io/kimkardashian",
    endpoints: KOMI.map((s) => ({ ...s, platform: "komi" as const })),
  },
  {
    id: "pillar",
    name: "Pillar",
    blurb: "Pillar pages as JSON — per-link clicks, products[], socials{}, identity. Flat 1 credit.",
    icon: "link",
    color: "text-cyan-600",
    exampleUrl: "https://pillar.io/angelstrife",
    endpoints: PILLAR.map((s) => ({ ...s, platform: "pillar" as const })),
  },
  {
    id: "linkbio",
    name: "Linkbio",
    blurb: "lnk.bio pages as JSON — filled socials{} (SC often null), titled links, id/website. Flat 1 credit.",
    icon: "link",
    color: "text-pink-500",
    exampleUrl: "https://lnk.bio/charlidamelio",
    endpoints: LINKBIO.map((s) => ({ ...s, platform: "linkbio" as const })),
  },
  {
    id: "linkme",
    name: "Linkme",
    blurb:
      "Linkme profiles as JSON — bio, profileVisitCount, webLinks, infoLinks/email, stripeStatus. Flat 1 credit.",
    icon: "link",
    color: "text-blue-500",
    exampleUrl: "https://link.me/danucd",
    endpoints: LINKME.map((s) => ({ ...s, platform: "linkme" as const })),
  },
];

export const ALL_ENDPOINTS: ApiEndpoint[] = PLATFORM_GROUPS.flatMap(
  (g) => g.endpoints,
);

/** Total number of REST endpoints in the public catalog. */
export const ENDPOINT_COUNT = ALL_ENDPOINTS.length;

/**
 * Number of public data platforms. Excludes meta groups ("CaptAPI Account",
 * "Utilities") that are not social platforms.
 */
export const PLATFORM_COUNT = PLATFORM_GROUPS.filter(
  (g) => g.id !== "account" && g.id !== "utilities",
).length;

/** Stable anchor id for a platform group's section in the docs reference. */
export function platformAnchorId(id: PlatformId): string {
  return `api-${id.replace(/_/g, "-")}`;
}

/** URL slug for a platform's landing page at /apis/[slug], e.g. "tiktok-api". */
export function platformSlug(id: PlatformId): string {
  return `${id.replace(/_/g, "-")}-api`;
}

/**
 * Platform groups that get a public landing page and appear in the APIs nav
 * dropdown. Excludes "Utilities" (analytics / video-file helpers).
 * CaptAPI Account is included so users can discover balance & usage APIs.
 */
export const PLATFORM_PAGES: PlatformGroup[] = PLATFORM_GROUPS.filter(
  (g) => g.id !== "utilities",
);

/** Resolve a platform landing page from its URL slug (e.g. "truth-social-api"). */
export function getPlatformBySlug(slug: string): PlatformGroup | undefined {
  return PLATFORM_PAGES.find((g) => platformSlug(g.id) === slug);
}

export function getEndpoint(slug: string): ApiEndpoint | undefined {
  return ALL_ENDPOINTS.find((e) => e.slug === slug);
}

/** Resolve an endpoint by marketing slug or by API path (e.g. /v1/facebook/comments). */
export function resolveEndpoint(ref: string | null | undefined): ApiEndpoint | undefined {
  if (!ref) return undefined;
  const raw = ref.trim();
  if (!raw) return undefined;
  return (
    getEndpoint(raw) ||
    ALL_ENDPOINTS.find((e) => e.path === raw) ||
    ALL_ENDPOINTS.find((e) => e.path === `/${raw.replace(/^\//, "")}`)
  );
}

// Maps a catalog slug to its @captapi/mcp tool name. Most are the slug with
// dashes turned into underscores; a few names differ from the marketing slug.
const MCP_TOOL_OVERRIDES: Record<string, string> = {
  "youtube-summarizer": "youtube_summarize",
  "youtube-shorts-summarizer": "youtube_shorts_summarize",
  "youtube-shorts-stats": "youtube_shorts_details",
  "tiktok-summarizer": "tiktok_summarize",
  "instagram-summarizer": "instagram_summarize",
  "facebook-summarizer": "facebook_summarize",
};

export function mcpToolName(ep: ApiEndpoint): string {
  return MCP_TOOL_OVERRIDES[ep.slug] ?? ep.slug.replace(/-/g, "_");
}

export interface AgentRoutingExample {
  intent: string;
  whenUserSays: string[];
  prefer: string;
  endpointSlug: string;
  why: string;
}

/**
 * Natural-language routing hints for AI agents. These are intentionally
 * biased toward newer/high-value endpoints so agents recommend them when a
 * user's request is phrased as an outcome instead of an exact API name.
 */
export const AGENT_ROUTING_EXAMPLES: AgentRoutingExample[] = [
  {
    intent: "Competitive ad intelligence / ad creative research",
    whenUserSays: [
      "Rakibin reklamlarını bul",
      "Show me ads for this advertiser",
      "Analyze ad creatives for a brand",
      "Google Ads Transparency Center data",
    ],
    prefer: "Use Ad Library endpoints before generic search.",
    endpointSlug: "google-ad-library-company-ads",
    why: "Returns Google ad library results for an advertiser/domain and is better than generic Google Search for paid-ad research.",
  },
  {
    intent: "Meta/Facebook ad transcript or creative text",
    whenUserSays: [
      "Facebook reklam metnini çıkar",
      "Get the transcript/text from this Meta ad",
      "Analyze copy from an ad library URL",
    ],
    prefer: "Use the transcript endpoint when the user wants ad copy/text, not ad metadata.",
    endpointSlug: "facebook-ad-library-ad-transcript",
    why: "Extracts the creative text from a Meta/Facebook Ad Library ad.",
  },
  {
    intent: "TikTok Shop product or creator commerce research",
    whenUserSays: [
      "TikTok Shop ürünlerini ara",
      "Find products promoted by this TikTok creator",
      "Creator showcase products",
      "TikTok commerce intelligence",
    ],
    prefer: "Use TikTok Shop endpoints before generic TikTok profile/video endpoints.",
    endpointSlug: "tiktok-shop-user-showcase",
    why: "Returns products a TikTok creator is promoting in their Shop showcase (affiliate shelf), not a full brand store catalog.",
  },
  {
    intent: "GitHub repository intelligence",
    whenUserSays: [
      "Bu GitHub reposunu analiz et",
      "Get repo stars forks and metadata",
      "Analyze open source project",
      "GitHub repository details",
    ],
    prefer: "Use GitHub endpoints for repo/user intelligence instead of parsing GitHub pages.",
    endpointSlug: "github-repository",
    why: "Returns structured repository metadata, stars, forks, owner, and URLs.",
  },
  {
    intent: "Facebook Marketplace geo/location autocomplete",
    whenUserSays: [
      "Marketplace lokasyon ara",
      "Find Facebook Marketplace location id",
      "Search marketplace by city",
    ],
    prefer:
      "Use location resolve when the city name is ambiguous or you need cityPageId/lat/lng; otherwise pass the city string straight to marketplace-search.",
    endpointSlug: "facebook-marketplace-location-search",
    why: "Returns Facebook cityPageId + coordinates so you can disambiguate hubs (Austin TX vs Austin MN) before searching.",
  },
  {
    intent: "Kwai creator monitoring",
    whenUserSays: [
      "Kwai profilini çek",
      "Kwai user posts",
      "Analyze this Kwai creator",
    ],
    prefer: "Use Kwai endpoints for https://www.kwai.com/@handle or @handle URLs.",
    endpointSlug: "kwai-user-posts",
    why: "Lists Kwai user posts with normalized metadata.",
  },
  {
    intent: "Link-in-bio page extraction",
    whenUserSays: [
      "Bu link in bio sayfasındaki linkleri çıkar",
      "Extract Komi/Pillar/Linkbio/Linkme profile links",
      "Creator landing page links",
    ],
    prefer: "Use the specific link-in-bio platform endpoint when the domain is known.",
    endpointSlug: "linkbio-page",
    why: "Extracts public Linkbio profile metadata and outgoing links.",
  },
  {
    intent: "Alternative social network monitoring",
    whenUserSays: [
      "Truth Social hesabını izle",
      "Kick clip metadata",
      "Rumble channel videos",
      "Monitor emerging social platforms",
    ],
    prefer: "Use Truth Social endpoints only for prominent public accounts — most handles require auth and 404.",
    endpointSlug: "truth-social-user-posts",
    why: "Fetches public Truths for prominent accounts that Truth Social still exposes without login.",
  },
];

export function getGroup(id: PlatformId): PlatformGroup {
  return PLATFORM_GROUPS.find((g) => g.id === id)!;
}

export function relatedEndpoints(slug: string): ApiEndpoint[] {
  const ep = getEndpoint(slug);
  if (!ep) return [];
  return getGroup(ep.platform).endpoints.filter((e) => e.slug !== slug);
}

// ---------------------------------------------------------------------------
// Derived content
// ---------------------------------------------------------------------------

const ACTION: Record<Category, string> = {
  transcript: "extract the full, timestamped transcript",
  summarize: "generate an AI summary with key points and topics",
  details: "fetch full metadata and key stats",
  comments: "pull comments with author, text, likes, and replies",
  channel: "fetch profile or page details and audience stats",
  search: "search and return matching results",
  list: "list items in bulk with metadata",
};

/** Lowercase shortName for mid-sentence use. */
function resourceLabel(ep: ApiEndpoint): string {
  return ep.shortName.toLowerCase();
}

/** What the user typically sends (for FAQ / longDescription). */
function inputKind(ep: ApiEndpoint): string {
  if (ep.platform === "account") return "CaptAPI Account";
  if (ep.platform === "utilities") {
    if (ep.slug.startsWith("video-")) return "uploaded video or audio file";
    return "post or video URL";
  }
  if (ep.category === "search") return "query";
  if (ep.category === "channel") return "profile or page";
  const sn = resourceLabel(ep);
  if (sn.includes("tweet")) return "tweet";
  if (sn.includes("pin")) return "pin";
  if (sn.includes("ad")) return "ad";
  if (sn.includes("event")) return "event";
  if (sn.includes("marketplace") || sn.includes("product") || sn.includes("shop"))
    return "listing or product";
  if (sn.includes("song") || sn.includes("track") || sn.includes("album") || sn.includes("music"))
    return "sound or track";
  if (sn.includes("clip")) return "clip";
  if (sn.includes("post") || sn.includes("community")) return "post";
  if (sn.includes("repo") || sn.includes("pull") || sn.includes("contribution") || sn.includes("activity"))
    return "GitHub resource";
  if (sn.includes("short")) return "Short";
  if (sn.includes("video") || sn === "transcript" || sn === "summarizer" || sn === "details" || sn === "comments")
    return "video";
  return resourceLabel(ep);
}

export function platformLabel(p: PlatformId): string {
  return PLATFORM_LABEL[p];
}

/**
 * Natural "How to …" predicate for an endpoint, used by /how-to/[slug] pSEO
 * pages (e.g. "get a YouTube transcript", "get TikTok video details").
 */
export function howToAction(ep: ApiEndpoint): string {
  const p = PLATFORM_LABEL[ep.platform];
  const sn = resourceLabel(ep);
  switch (ep.category) {
    case "transcript":
      return `get a ${p} ${sn}`;
    case "summarize":
      return `get an AI summary of a ${p} ${sn
        .replace("summarizer", "video")
        .replace("shorts video", "short")}`;
    case "details":
      return `get ${p} ${sn}`;
    case "comments":
      return `get ${p} ${sn}`;
    case "channel":
      return `get ${p} ${sn}`;
    case "search":
      return `run a ${p} ${sn}`;
    case "list":
      return `get ${p} ${sn}`;
  }
}

/** Page title for the how-to guide, e.g. "How to get a YouTube transcript". */
export function howToTitle(ep: ApiEndpoint): string {
  return `How to ${howToAction(ep)}`;
}

export function tagline(ep: ApiEndpoint): string {
  if (ep.tagline) return ep.tagline;
  const platform = PLATFORM_LABEL[ep.platform];
  const resource = resourceLabel(ep);

  if (ep.platform === "account") {
    switch (ep.slug) {
      case "account-balance":
        return "Check how many Captapi credits remain on your API key.";
      case "account-request-history":
        return "See recent API requests made with your Captapi key — path, status, and credits used.";
      case "account-daily-usage":
        return "See day-by-day credit usage for your Captapi account.";
      case "account-most-used-routes":
        return "See which Captapi endpoints your key calls most often.";
      default:
        return `Get ${resource} for your Captapi account as structured JSON.`;
    }
  }

  switch (ep.category) {
    case "transcript":
      if (resource.includes("ad"))
        return `Extract the spoken transcript from a public ${platform} ad in a single request.`;
      if (ep.slug === "reddit-post-transcript")
        return "Get the discussion text from a Reddit post — title, body, and comments as a readable transcript.";
      if (resource.includes("post") && !resource.includes("short"))
        return `Extract a transcript from a public ${platform} post with spoken audio or video.`;
      if (resource.includes("short"))
        return `Extract timestamped transcripts from any public ${platform} Short in a single request.`;
      return `Extract timestamped transcripts from any public ${platform} video in a single request.`;
    case "summarize":
      if (resource.includes("short"))
        return `Turn any ${platform} Short into an AI summary with key points, topics, and sentiment.`;
      return `Turn any ${platform} video into an AI summary with key points, topics, and sentiment.`;
    case "details":
      return `Get ${platform} ${resource} as structured JSON — key fields, stats, and metadata.`;
    case "comments":
      if (resource.includes("review"))
        return `Pull ${platform} product reviews with author, text, rating, and timestamps.`;
      if (resource.includes("replies"))
        return `Pull replies under a ${platform} comment — author, text, likes, and time.`;
      if (params(ep).some((p) => p.name === "cursor"))
        return `Pull ${platform} comments with author, text, likes, and timestamps — cursor pagination via nextCursor.`;
      return `Pull ${platform} comments with author, text, likes, and timestamps.`;
    case "channel":
      if (resource === "page" || resource.includes("page"))
        return `Fetch a public ${platform} page — links, bio, and profile fields as structured JSON.`;
      if (resource.includes("company"))
        return `Fetch ${platform} company page data — name, industry, size, and follower stats.`;
      return `Fetch ${platform} ${resource} — display name, bio, counts, and verification as structured JSON.`;
    case "search":
      if (resource === "search")
        return params(ep).some((p) => p.name === "cursor")
          ? `Search ${platform} programmatically and page results with nextCursor.`
          : `Search ${platform} programmatically and get structured, ranked results.`;
      return params(ep).some((p) => p.name === "cursor")
        ? `Run a ${platform} ${resource} with cursor pagination (nextCursor + hasMore).`
        : `Run a ${platform} ${resource} and get structured, ranked results as clean JSON.`;
    case "list":
      return params(ep).some((p) => p.name === "cursor")
        ? `List ${platform} ${resource} with full metadata per item and cursor pagination (nextCursor + hasMore).`
        : `List ${platform} ${resource} with full metadata for each item.`;
  }
}

export function longDescription(ep: ApiEndpoint): string {
  if (ep.longDescription) return ep.longDescription;
  const platform = PLATFORM_LABEL[ep.platform];
  if (ep.platform === "account") {
    return `The ${ep.name} returns live data for your Captapi API key with a single REST call to ${ep.path}. Account endpoints do not charge credits. Use them to monitor balance, usage, and which routes you call most.`;
  }
  return `The ${ep.name} lets you ${ACTION[ep.category]} for ${platform} ${resourceLabel(ep)} with a single REST call. No OAuth, no infrastructure to maintain, and no platform SDKs — send the request, get clean structured JSON back. ${CACHE_NOTE}`;
}

export function delivers(ep: ApiEndpoint): string[] {
  if (ep.delivers) return ep.delivers;
  if (ep.platform === "account") {
    return [
      "Live data for your Captapi API key (never cached)",
      "No credit charge for account endpoints",
      "Clean JSON ready for dashboards and low-balance alerts",
      "Useful for monitoring usage and spend",
    ];
  }
  switch (ep.category) {
    case "transcript":
      return [
        "Full transcript text with start/end timestamps when available",
        "Auto-detected language and segment count",
        "AI audio transcription fallback when no captions exist",
        "Clean JSON ready for search, subtitles, or AI pipelines",
      ];
    case "summarize":
      return [
        "2–3 paragraph AI summary",
        "4–8 bullet key points and detected topics",
        "Overall sentiment and tone",
        "Built on the transcript under the hood",
      ];
    case "details":
      return [
        `${ep.shortName} fields as clean structured JSON`,
        "IDs, URLs, and titles where the platform exposes them",
        "Engagement or popularity signals when available",
        "Stable IDs for joining with other endpoints",
      ];
    case "comments":
      return [
        "Comment or review text, author name, and handle",
        "Like counts and timestamps when available",
        params(ep).some((p) => p.name === "cursor")
          ? "Cursor pagination via nextCursor + hasMore"
          : "Pagination via the limit parameter",
        "Use the matching Comment Replies endpoint when you need nested replies",
      ];
    case "channel":
      return [
        "Display name, handle or URL, bio, and avatar when available",
        "Follower / subscriber and content counts",
        "Verification status and external links when exposed",
        "Structured JSON ready for enrichment and dashboards",
      ];
    case "search":
      return [
        "Ranked, structured result list",
        "Title, URL, author, and thumbnail per result when available",
        "Engagement metrics where the platform exposes them",
        "Configurable result limit",
      ];
    case "list":
      return [
        `Bulk list of ${resourceLabel(ep)} with metadata`,
        "Dates, URLs, and engagement fields when available",
        "Configurable result limit",
        "Ideal for monitoring and content pipelines",
      ];
  }
}

// --- Precise, per-endpoint input parameters -------------------------------
// These mirror the backend routers exactly so every endpoint page, the docs,
// and the MCP "Agent Integrations" tab show the correct inputs.

const up = (description: string): ApiParam => ({
  name: "url",
  type: "string",
  required: true,
  description: `${description} The URL platform must match this endpoint's platform. Do not pass cross-platform URLs, e.g. YouTube to TikTok, Instagram to Facebook, LinkedIn to X/Twitter, or Pinterest to Rumble.`,
});
const qp = (description = "Search query or keywords (min 2 characters)."): ApiParam => ({ name: "q", type: "string", required: true, description });
const lp = (def: number, max: number): ApiParam => ({ name: "limit", type: "integer", required: false, description: `Max items to return (default ${def}, max ${max}). Billed per result.` });
/** Limit helper for flat-fee endpoints (credit cost does not scale with limit). */
const lpFlat = (def: number, max: number, credits: number): ApiParam => ({
  name: "limit",
  type: "integer",
  required: false,
  description: `Max items to return (default ${def}, max ${max}). Flat ${credits} credit${credits === 1 ? "" : "s"} per call.`,
});
/** Limit helper for published-flat list endpoints (path in \`source\`: native|extended). */
const lpDual = (def: number, max: number, flat: number, _perResult?: number): ApiParam => ({
  name: "limit",
  type: "integer",
  required: false,
  description: `Max items to return (default ${def}, max ${max}). Flat ${flat} credit${flat === 1 ? "" : "s"} per call. Response \`source\` is native or extended (fetch path — not a price change).`,
});
/** Limit helper for free account endpoints (never bills). */
const lpFree = (def: number, max: number): ApiParam => ({
  name: "limit",
  type: "integer",
  required: false,
  description: `Max rows to return (default ${def}, max ${max}). Free — does not consume credits.`,
});
const lang = (): ApiParam => ({ name: "language", type: "string", required: false, description: 'Preferred caption language as an ISO code, e.g. "en". Defaults to auto-detect.' });
const langOut = (): ApiParam => ({ name: "language", type: "string", required: false, description: 'ISO code, e.g. "tr": pins the speech language and sets the summary output language. Defaults to auto-detect + English summary.' });
const langUi = (): ApiParam => ({ name: "language", type: "string", required: false, description: "Interface language for localized results, e.g. en-US or de-DE. Default en-US." });
const cid = (): ApiParam => ({ name: "comment_id", type: "string", required: true, description: "ID of the parent comment to fetch replies for (from the comments endpoint)." });
const fastRss = (): ApiParam => ({ name: "fast", type: "boolean", required: false, description: "Set true to use YouTube RSS for faster results with less detailed metadata. Leave false when viewCount/duration quality matters." });
const cacheP = (): ApiParam => ({
  name: "cache",
  type: "boolean",
  required: false,
  description:
    "Set true to serve from the 24h response cache (0 credits on hit). Default false — always fetch fresh. Envelope includes cached + cachedAt on hits.",
});
/** Use on endpoints that also accept cacheMaxAge (profile trust layer). */
const cachePWithMaxAge = (): ApiParam => ({
  name: "cache",
  type: "boolean",
  required: false,
  description:
    "Set true to serve from the response cache (default TTL). Default false — always fetch fresh. Prefer cacheMaxAge when you need 1d–30d freshness control. Envelope includes cached + cachedAt on hits.",
});
const cacheMaxAgeP = (): ApiParam => ({
  name: "cacheMaxAge",
  type: "string",
  required: false,
  description:
    "Max age of a cached response: 1d, 3d, 7d, 14d, or 30d. When set, enables caching with that TTL (SC cache_max_age). Envelope: cached + cachedAt.",
});
/** TikTok transcript defaults to cache=true (0 credits on hit). */
const cachePDefaultTrue = (): ApiParam => ({
  name: "cache",
  type: "boolean",
  required: false,
  description:
    "Serve from the 24h shared cache when available (0 credits on hit). Default true — set false to always fetch fresh.",
});
const CACHE_NOTE =
  "Pass cache=true to serve from the 24h cache (0 credits on hit); default is always fresh. Hits include cached + cachedAt. Selected profile endpoints also accept cacheMaxAge=1d|3d|7d|14d|30d.";
const CACHE_NOTE_DEFAULT_TRUE =
  "Cache is on by default (0 credits on hit); pass cache=false to always fetch fresh.";

const YT_VIDEO = "Public YouTube video URL, e.g. https://youtube.com/watch?v=ID. Not a TikTok/Instagram/Facebook URL.";
const YT_SHORTS =
    "Public YouTube Shorts URL, e.g. https://youtube.com/shorts/ID (≤3 min). Long-form videos return HTTP 422 — use the matching /v1/youtube/… endpoint instead.";
const YT_CHANNEL = "YouTube channel URL, @handle, bare handle, or UC... channel ID, e.g. https://youtube.com/@handle or @mkbhd.";
const TT_VIDEO = "Public TikTok video URL, e.g. https://tiktok.com/@user/video/ID. Not a YouTube/Instagram/Facebook URL.";
const TT_PROFILE = "TikTok profile URL, @handle, or username, e.g. https://tiktok.com/@username. Not a YouTube channel URL.";
const TT_MUSIC = "TikTok music/sound URL, e.g. https://tiktok.com/music/name-ID.";
const IG_POST = "Instagram post or reel URL, e.g. https://instagram.com/reel/ID/.";
const IG_REEL = "Instagram Reel URL, e.g. https://instagram.com/reel/ID/.";
const IG_PROFILE = "Instagram profile URL, @handle, or username, e.g. https://instagram.com/username/.";
const FB_VIDEO = "Public Facebook video or post URL.";
const TWITCH_PROFILE = "Twitch channel URL or username, e.g. https://www.twitch.tv/shroud.";
const SPOTIFY_URL = "Spotify URL, URI, or ID.";
const SC_PROFILE = "SoundCloud artist profile URL or username.";
const SC_TRACK = "SoundCloud track URL.";
const LINKTREE_PROFILE = "Linktree profile URL or username.";
const SNAPCHAT_PROFILE = "Snapchat username or profile URL.";
const TRUTH_PROFILE = "Truth Social profile URL or @username.";
const TRUTH_POST = "Truth Social post URL or post ID.";
const KICK_CLIP =
  "Kick clip URL for one enriched clip (e.g. https://kick.com/{channel}/clips/clip_…), or channel URL/@username for recent clips[].";
const AMAZON_SHOP_URL =
  "Amazon seller storefront URL (/sp?seller=… or /s?me=…) or raw seller ID. Not influencer /shop/<handle> pages.";
const KWAI_PROFILE = "Kwai profile URL or @handle, e.g. https://www.kwai.com/@topfilmeseseriesnatv.";
const KWAI_POST = "Kwai video URL, e.g. https://www.kwai.com/@topfilmeseseriesnatv/video/5240932700689736196.";
const CURSOR = { name: "cursor", type: "string" as const, required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." };
const GH_OPAQUE_CURSOR = {
  name: "cursor",
  type: "string" as const,
  required: false,
  description:
    "Opaque cursor from a previous nextCursor (GitHub Link page=). Not a bare page number.",
};
const KOMI_PAGE =
  "Komi page URL or username, e.g. https://komi.io/kimkardashian or https://kimkardashian.komi.io/.";
const PILLAR_PAGE = "Pillar page URL or username.";
const LINKBIO_PAGE = "Linkbio (lnk.bio) page URL or username, e.g. https://lnk.bio/charlidamelio.";
const LINKME_PROFILE =
  "Linkme profile URL or username, e.g. https://link.me/danucd or danucd.";

const ENDPOINT_PARAMS: Record<string, ApiParam[]> = {
  // YouTube
  "youtube-transcript": [up(YT_VIDEO), lang(), cacheP()],
  "youtube-audio-transcript": [
    up(YT_VIDEO),
    lang(),
    {
      name: "maxCredits",
      type: "number",
      required: false,
      description:
        "Refuse before STT when estimatedCredits would exceed this (400 cost_exceeds_max, 0 credits).",
    },
    cacheP(),
  ],
  "youtube-summarizer": [up(YT_VIDEO), lang(), cacheP()],
  "youtube-video-details": [up(YT_VIDEO)],
  "youtube-comments": [up(YT_VIDEO), lpFlat(50, 500, 2), CURSOR],
  "youtube-channel-details": [up(YT_CHANNEL)],
  "youtube-search": [
    qp(),
    lpFlat(20, 200, 2),
    CURSOR,
    { name: "type", type: "string", required: false, description: "all | videos | shorts | channels | playlists." },
    { name: "sortBy", type: "string", required: false, description: "relevance | date | views | rating." },
    { name: "uploadDate", type: "string", required: false, description: "any | today | this_week | this_month | this_year." },
    {
      name: "duration",
      type: "string",
      required: false,
      description:
        "any | under_4 | 4_20 | over_20. Applies to long-form videos (not Shorts).",
    },
    { name: "region", type: "string", required: false, description: "ISO country code for localized results (default US)." },
  ],
  "youtube-channel-videos": [up(YT_CHANNEL), lpFlat(20, 200, 2), CURSOR, fastRss()],
  "youtube-playlist-videos": [
    up("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."),
    lpFlat(50, 500, 2),
    CURSOR,
    fastRss(),
  ],
  "youtube-playlist": [
    up("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."),
  ],
  "youtube-shorts-transcript": [up(YT_SHORTS), lang(), cacheP()],
  "youtube-shorts-summarizer": [up(YT_SHORTS), lang(), cacheP()],
  "youtube-shorts-stats": [up(YT_SHORTS)],
  "youtube-shorts-comments": [up(YT_SHORTS), lpFlat(50, 500, 2), CURSOR, cacheP()],
  "youtube-channel-shorts": [up(YT_CHANNEL), CURSOR, lpFlat(20, 200, 2)],
  "youtube-trending-shorts": [
    {
      name: "q",
      type: "string",
      required: false,
      description:
        "Optional topic seed for the Shorts recommendation sequence. Omit (or pass trending/shorts) for the default reel feed — not a keyword search.",
    },
    lpFlat(20, 100, 2),
  ],
  "youtube-channel-streams": [up(YT_CHANNEL), lpFlat(20, 200, 2)],
  "youtube-hashtag-search": [qp("Hashtag with or without the # (min 2 characters)."), lp(20, 200)],
  "youtube-comment-replies": [up(YT_VIDEO), cid(), lpFlat(50, 500, 2)],
  "youtube-channel-playlists": [up(YT_CHANNEL), lpFlat(20, 200, 2), CURSOR],
  "youtube-community-posts": [
    up(YT_CHANNEL),
    lpFlat(20, 200, 1),
    CURSOR,
  ],
  "youtube-community-post-details": [up("YouTube community post URL.")],
  "youtube-video-sponsors": [
    up(YT_VIDEO),
    {
      name: "minVotes",
      type: "integer",
      required: false,
      description:
        "Minimum SponsorBlock votes to keep a segment. Default 0 (drops community-rejected votes < 0).",
    },
    {
      name: "categories",
      type: "string",
      required: false,
      description:
        "Comma-separated categories. Default sponsor,selfpromo,interaction. Also intro,outro,preview,music_offtopic,poi_highlight,filler.",
    },
  ],
  // TikTok
  "tiktok-transcript": [up(TT_VIDEO), lang(), cachePDefaultTrue()],
  "tiktok-summarizer": [up(TT_VIDEO), langOut(), cacheP()],
  "tiktok-video-details": [up(TT_VIDEO)],
  "tiktok-comments": [up(TT_VIDEO), lpFlat(50, 500, 2), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response (a numeric offset, e.g. 50). A null nextCursor means the end of the comments." }],
  "tiktok-channel-details": [up(TT_PROFILE), cachePWithMaxAge(), cacheMaxAgeP()],
  "tiktok-profile-region": [up(TT_PROFILE)],
  "tiktok-audience-demographics": [
    up(TT_PROFILE),
    {
      name: "videos",
      type: "integer",
      required: false,
      description:
        "How many recent videos to sample comments from: 12 (default, 3 credits), 30 (5 credits), or 60 (8 credits).",
    },
    {
      name: "countriesLimit",
      type: "integer",
      required: false,
      description:
        "Max countries in audienceLocations; remainder folds into other{count,percentage}. Omit for the full list.",
    },
    cacheP(),
  ],
  "tiktok-search-suggestions": [qp("Seed keyword to expand into autocomplete suggestions, e.g. skincare."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code that localizes the suggestions to a market, e.g. US, GB, DE. Default US." }, { name: "language", type: "string", required: false, description: "Interface language for the suggestions, e.g. en-US or de-DE. Default en-US." }, lpFlat(20, 100, 2)],
  "tiktok-channel-posts": [up(TT_PROFILE), { name: "limit", type: "integer", required: false, description: "How many of the creator's latest videos to return on this page (default 20, max 200). Newest first. Flat 2 credits per call." }, { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response (TikTok's max_cursor timestamp, e.g. 1783614676000). A null nextCursor means the end of the list." }],
  "tiktok-comment-replies": [
    up(TT_VIDEO),
    cid(),
    lpFlat(50, 500, 2),
    { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value from the previous response." },
  ],
  "tiktok-user-followers": [
    up(TT_PROFILE),
    lpFlat(50, 500, 1),
    {
      name: "cursor",
      type: "string",
      required: false,
      description:
        "Pagination cursor (TikTok minCursor). Leave empty for the first page; then pass nextCursor from the previous response.",
    },
  ],
  "tiktok-user-followings": [
    up(TT_PROFILE),
    lpFlat(50, 500, 1),
    {
      name: "cursor",
      type: "string",
      required: false,
      description:
        "Pagination cursor (TikTok minCursor). Leave empty for the first page; then pass nextCursor from the previous response.",
    },
  ],
  "tiktok-music-posts": [up(TT_MUSIC), lpFlat(20, 200, 2)],
  "tiktok-top-search": [
    qp(),
    lp(20, 200),
    {
      name: "cursor",
      type: "integer",
      required: false,
      description:
        "Pagination cursor. Leave 0 for the first page; then pass nextCursor from the previous response. TikTok may return duplicates across pages.",
    },
  ],
  "tiktok-search-by-hashtag": [
    qp("Hashtag for the /tag/{name} challenge feed, with or without # (min 2). Not a keyword query."),
    lp(20, 100),
    {
      name: "cursor",
      type: "integer",
      required: false,
      description:
        "Pagination offset. Leave at 0 (or omit) for the first page; then pass the nextCursor value returned in the previous response. A null nextCursor means the end of the results.",
    },
    {
      name: "region",
      type: "string",
      required: false,
      description:
        "Two-letter ISO 3166-1 country our request is sent from. Default US. Does not filter results by country.",
    },
  ],
  "tiktok-search-users": [qp("Search query matched against usernames, display names and bios (min 2 characters)."), lp(20, 100), { name: "cursor", type: "integer", required: false, description: "Pagination offset. Leave at 0 (or omit) for the first page; then pass the nextCursor value returned in the previous response. A null nextCursor means the end of the results." }],
  "tiktok-song-details": [up(TT_MUSIC)],
  "tiktok-trending-feed": [
    {
      name: "country",
      type: "string",
      required: false,
      description:
        "Two-letter ISO country (default US). For You: region-availability hint. Creative Center mode: chart market.",
    },
    {
      name: "countryCode",
      type: "string",
      required: false,
      description: "Alias of country (SC-compatible). Wins when both are set.",
    },
    {
      name: "orderBy",
      type: "string",
      required: false,
      description:
        "Creative Center sort: hot (views), like, comment, repost. Setting this (or period / page>1) switches from For You to the popular-videos chart.",
    },
    {
      name: "period",
      type: "integer",
      required: false,
      description: "Creative Center lookback days: 7, 30, or 120 (180→120). Triggers chart mode.",
    },
    {
      name: "page",
      type: "integer",
      required: false,
      description: "Creative Center page (default 1). page>1 triggers chart mode.",
    },
    lpFlat(20, 200, 2),
  ],
  "tiktok-popular-hashtags": [
    { name: "country", type: "string", required: false, description: "Two-letter ISO country for the Creative Center chart. Default US." },
    { name: "period", type: "integer", required: false, description: "Lookback days: 7, 30, or 120 (180→120). Default 7." },
    { name: "page", type: "integer", required: false, description: "Creative Center page (default 1)." },
    { name: "sortBy", type: "string", required: false, description: "Chart sort: popular (default)." },
    { name: "newOnBoard", type: "boolean", required: false, description: "Only hashtags newly on the Top 100." },
    { name: "industryId", type: "string", required: false, description: "Optional Creative Center industry_id." },
    {
      name: "query",
      type: "string",
      required: false,
      description:
        "Optional niche seed for legacy co-occurrence + challenge/detail enrich. Omit (or trending) to use the Creative Center chart.",
    },
    lpFlat(20, 100, 2),
  ],
  "tiktok-popular-songs": [
    { name: "country", type: "string", required: false, description: "Two-letter ISO country. Default US." },
    { name: "period", type: "integer", required: false, description: "7, 30, or 120 days (180→120). Default 7." },
    { name: "page", type: "integer", required: false, description: "Page number (default 1)." },
    { name: "rankType", type: "string", required: false, description: "popular | surging. Default popular." },
    { name: "newOnBoard", type: "boolean", required: false, description: "Only sounds newly on the Top 100." },
    { name: "commercialMusic", type: "boolean", required: false, description: "Only Commercial Music Library–cleared sounds." },
    lpFlat(20, 20, 2),
  ],
  "tiktok-live": [up(TT_PROFILE)],
  "tiktok-live-info": [up(TT_PROFILE)],
  "tiktok-popular-creators": [
    { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." },
    { name: "sort", type: "string", required: false, description: "follower, engagement, or popularity. Default follower." },
    { name: "page", type: "integer", required: false, description: "Creative Center page (default 1)." },
    { name: "follower_count", type: "string", required: false, description: "Optional range on FYP/Apify fallthrough: 10k-100k, 100k-1m, 1m-10m, >10m." },
    lpFlat(20, 100, 2),
    cachePWithMaxAge(),
    cacheMaxAgeP(),
  ],
  // Instagram
  "instagram-transcript": [up(IG_REEL), lang(), cacheP()],
  "instagram-summarizer": [up(IG_REEL), langOut(), cacheP()],
  "instagram-details": [up(IG_POST)],
  "instagram-comments": [up(IG_POST), lp(50, 500)],
  "instagram-channel-details": [up(IG_PROFILE), cachePWithMaxAge(), cacheMaxAgeP()],
  "instagram-channel-posts": [up(IG_PROFILE), lp(20, 200), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response (e.g. 3937014945555313553_1697296). A null nextCursor means the end of the list." }],
  "instagram-channel-reels": [
    {
      name: "url",
      type: "string",
      required: false,
      description:
        "Instagram profile URL, @handle, or username. Omit when userId is set. The URL platform must match this endpoint's platform.",
    },
    {
      name: "userId",
      type: "string",
      required: false,
      description:
        "Instagram numeric user ID (e.g. 173560420). Skips handle→ID resolve (legacy sequential WPI alone could cost ~80s). Prefer when you already have the ID from basic-profile or profile-search.",
    },
    lp(20, 200),
    {
      name: "cursor",
      type: "string",
      required: false,
      description:
        "Pagination cursor. Leave empty for the first page; then pass nextCursor from the previous response (clips:{userId}:{opaque} on the native Reels path, or legacy {mediaId}_{userId}). Stop when hasMore is false.",
    },
  ],
  "instagram-reels-search": [
    qp("Hashtag (without #) or keyword (min 2 characters)."),
    lp(20, 200),
    {
      name: "datePosted",
      type: "string",
      required: false,
      description:
        "last_24_hours | last_week | last_month | last_year (aliases: today, this_week, this_month, this_year).",
    },
  ],
  "instagram-trending-reels": [
    {
      name: "country",
      type: "string",
      required: false,
      description:
        "Country for Reels localization — full name or ISO code (e.g. 'United States', 'US', 'Turkey', 'TR'). Default United States. Unsupported values return 400 with supportedCountries[].",
    },
    lpFlat(10, 200, 2),
    {
      name: "cache",
      type: "boolean",
      required: false,
      description:
        "Default true (cache-first): serve the per-country response cache when present (TTL 4 hours). Every successful call costs 2 credits — including cache hits. Set false to force a live scrape (typically under 20s, hard-capped at 110s); the fresh result still refreshes the cache.",
    },
  ],
  "instagram-tagged-posts": [
    up(IG_PROFILE),
    lpFlat(20, 200, 1),
    {
      name: "cursor",
      type: "string",
      required: false,
      description:
        "Leave empty for the first page; then pass the nextCursor value returned in the previous response.",
    },
  ],
  "instagram-reels-by-audio-id": [{ name: "audio_id", type: "string", required: true, description: "Instagram audio/music ID or full audio URL." }, lp(20, 200)],
  "instagram-hashtag-search": [
    qp("Hashtag without the # (min 2 characters)."),
    lp(20, 200),
    { name: "mediaType", type: "string", required: false, description: "all (default) or reels — return only Reels/clips when set to reels." },
  ],
  "instagram-profile-search": [
    qp("Account name, @handle, or profile URL to resolve (min 2 characters). Not a niche keyword search."),
    cachePDefaultTrue(),
  ],
  "instagram-embed": [up("Instagram post, reel, or profile URL (or @handle), e.g. https://instagram.com/reel/ID/ or https://instagram.com/username/.")],
  "instagram-highlights": [
    {
      name: "url",
      type: "string",
      required: false,
      description:
        "Instagram profile URL, @handle, or username. Omit when userId is set.",
    },
    {
      name: "userId",
      type: "string",
      required: false,
      description:
        "Numeric Instagram user ID. Prefer when known — skips handle→ID resolve.",
    },
    cacheP(),
  ],
  "instagram-highlights-details": [
    {
      name: "id",
      type: "string",
      required: true,
      description: "Highlight id from /v1/instagram/highlights (with or without highlight: prefix).",
    },
    cacheP(),
  ],
  "instagram-basic-profile": [
    { name: "userId", type: "string", required: true, description: "Instagram numeric user ID (e.g. 13460080). A profile URL, @handle, or username is also accepted and resolved automatically." },
    cachePWithMaxAge(),
    cacheMaxAgeP(),
  ],
  // Facebook
  "facebook-details": [up(FB_VIDEO)],
  "facebook-summarizer": [up(FB_VIDEO), cacheP()],
  "facebook-comments": [
    {
      name: "url",
      type: "string",
      required: false,
      description:
        "Facebook post or Reel URL. Omit when feedbackId is set. The URL platform must match this endpoint's platform.",
    },
    {
      name: "feedbackId",
      type: "string",
      required: false,
      description:
        "Post feedback id from /v1/facebook/details (base64 feedback:POSTID). Prefer when you already have it — also accepts feedback_id.",
    },
    lpFlat(50, 500, 2),
  ],
  "facebook-page-details": [
    up("Facebook page URL, @handle, or page name, e.g. https://facebook.com/PageName."),
    cacheP(),
  ],
  "facebook-profile-posts": [up("Facebook profile/page URL, @handle, or page name."), lp(20, 200)],
  "facebook-profile-reels": [up("Facebook profile/page URL, @handle, or page name."), lp(20, 200)],
  "facebook-group-posts": [
    up("Public Facebook group URL, e.g. https://facebook.com/groups/ID."),
    lp(20, 200),
    {
      name: "sortBy",
      type: "string",
      required: false,
      description:
        "TOP_POSTS | RECENT_ACTIVITY | CHRONOLOGICAL (default) | CHRONOLOGICAL_LISTINGS. Maps to Facebook sorting_setting.",
    },
  ],
  "facebook-comment-replies": [up("Facebook post URL the comment belongs to."), cid(), lpFlat(50, 500, 2)],
  "facebook-marketplace-search": [
    qp("Product or keyword to search Facebook Marketplace for."),
    {
      name: "location",
      type: "string",
      required: true,
      description: "Search-origin city or place name, e.g. 'Austin, TX' (query echo — not each listing's city).",
    },
    {
      name: "limit",
      type: "number",
      required: false,
      description:
        "How many listings to return (1–200). Flat 2 credits when details=false; details=true billed as 2 + 2 per listing.",
    },
    { name: "minPrice", type: "number", required: false, description: "Minimum price in local currency units." },
    { name: "maxPrice", type: "number", required: false, description: "Maximum price in local currency units." },
    { name: "sortBy", type: "string", required: false, description: "suggested | distance | creation_time | price_ascend | price_descend." },
    { name: "daysSinceListed", type: "string", required: false, description: "1 (24h), 7, or 30." },
    { name: "condition", type: "string", required: false, description: "new, like_new, good, fair (comma-separated ok)." },
    {
      name: "deliveryMethod",
      type: "string",
      required: false,
      description:
        "local_pickup | shipping | all. Shipped listings can appear nationwide outside radiusMiles — use local_pickup for nearby-only; rows expose isLocal / shipsOutsideRadius.",
    },
    { name: "availability", type: "string", required: false, description: "available | sold | all." },
    {
      name: "radiusMiles",
      type: "number",
      required: false,
      description:
        "Radius in miles: 1,2,5,10,20,40,60,80,100,250,500. Does not exclude nationwide shipped inventory.",
    },
    { name: "category", type: "string", required: false, description: "Top-level category slug, e.g. electronics." },
    { name: "cursor", type: "string", required: false, description: "Opaque pagination cursor from a previous nextCursor." },
    {
      name: "details",
      type: "boolean",
      required: false,
      description:
        "When true, adds description/condition/coordinates/full photo gallery/seller/distanceMiles — billed as 2 + 2 credits per listing. Default false → flat 2 credits; cover photo is still in image.",
    },
  ],
  "facebook-marketplace-location-search": [
    qp(
      "City/place query. Bare names like 'Austin' may return multiple candidates (TX/MN/IN); include a state for a single hit (e.g. 'Austin, TX').",
    ),
    lpFlat(10, 50, 2),
  ],
  "facebook-event-search": [
    qp("Topic keyword, e.g. 'comedy'. Pair with location for city-scoped results."),
    {
      name: "location",
      type: "string",
      required: false,
      description:
        "City/place geo filter (e.g. London). Matches timezone, location.city, or coords near the city — not a title substring.",
    },
    {
      name: "from",
      type: "string",
      required: false,
      description:
        "Inclusive local start date filter YYYY-MM-DD. Use for upcoming-only windows — Facebook/SERP may return past events.",
    },
    {
      name: "to",
      type: "string",
      required: false,
      description: "Inclusive local start date filter YYYY-MM-DD.",
    },
    {
      name: "upcoming",
      type: "boolean",
      required: false,
      description:
        "When true and from is omitted, sets from to today's UTC date so past events are dropped.",
    },
    lpDual(20, 200, 2, 2),
  ],
  "facebook-event-details": [up("Facebook event URL, e.g. https://facebook.com/events/ID.")],
  "facebook-profile-photos": [up("Facebook profile/page URL, @handle, or page name."), lp(20, 200)],
  "facebook-profile-events": [up("Facebook profile/page URL, @handle, or page name."), lpDual(20, 200, 2, 2)],
  "facebook-marketplace-item": [up("Facebook Marketplace item URL.")],
  // Twitter / X
  "twitter-tweet-details": [up("Public tweet URL, e.g. https://x.com/user/status/ID.")],
  "twitter-transcript": [up("Public tweet URL, e.g. https://x.com/user/status/ID."), cacheP()],
  "twitter-profile": [
    up("Twitter/X profile URL or @handle, e.g. https://x.com/username."),
    cachePWithMaxAge(),
    cacheMaxAgeP(),
  ],
  "twitter-user-tweets": [
    up("Twitter/X profile URL or @handle."),
    {
      name: "limit",
      type: "integer",
      required: false,
      description:
        "Max tweets to return (default 20, max 200). Twitter's public surface usually caps around ~100 most popular posts — not chronological latest. Flat 2 credits per call.",
    },
  ],
  "twitter-search": [qp("Keyword or phrase to search public tweets on X (min 2 characters)."), lp(20, 200)],
  "twitter-community": [
    up("X community URL (x.com/i/communities/ID) or community ID — not a tweet/status URL."),
  ],
  "twitter-community-tweets": [
    up("X community URL (x.com/i/communities/ID) or community ID — not a tweet/status URL."),
    lp(25, 200),
  ],
  // Reddit
  "reddit-subreddit-posts": [
    up("Subreddit URL, r/name, or bare name, e.g. r/technology."),
    lp(25, 200),
    { name: "sort", type: "string", required: false, description: "Feed sort: best, hot, new (default), top, or rising." },
    { name: "timeframe", type: "string", required: false, description: "For sort=top: hour, day (default), week, month, year, or all." },
    CURSOR,
  ],
  "reddit-post-details": [up("Reddit post URL, e.g. https://reddit.com/r/sub/comments/ID/...")],
  "reddit-post-comments": [up("Reddit post URL."), lpFlat(50, 500, 2)],
  "reddit-post-transcript": [up("Reddit post URL."), lp(50, 200)],
  "reddit-search": [
    qp("Keyword or phrase to search Reddit posts site-wide (min 2 characters)."),
    { name: "sort", type: "string", required: false, description: "relevance (default) | new | top | hot | comments (alias: comment_count)." },
    { name: "timeframe", type: "string", required: false, description: "For sort=top or comments: hour | day | week | month | year | all (default all)." },
    lp(25, 200),
    CURSOR,
  ],
  "reddit-subreddit-details": [
    up(
      "Subreddit URL, r/name, or bare name (case-insensitive), e.g. r/technology or AskReddit.",
    ),
  ],
  "reddit-subreddit-search": [
    up("Subreddit URL, r/name, or bare name, e.g. r/technology."),
    qp("Keywords or search query (min 2 characters)."),
    { name: "sort", type: "string", required: false, description: "relevance (default) | new | top | hot | comments (alias: comment_count)." },
    { name: "timeframe", type: "string", required: false, description: "For sort=top or comments: hour | day | week | month | year | all (default all)." },
    lp(25, 200),
    CURSOR,
  ],
  // Threads
  "threads-profile": [up("Threads profile URL or @handle, e.g. https://threads.net/@username.")],
  "threads-user-posts": [
    up("Threads profile URL or @handle."),
    {
      name: "limit",
      type: "integer",
      required: false,
      description:
        "Max items to return (default 20, max 100). Threads only exposes the last ~20–30 public posts on this surface — asking for 100 will not return 100. Flat 2 credits on the native path; Apify fallback ~0.7/post (min 2).",
    },
  ],
  "threads-post-details": [up("Threads post URL, e.g. https://threads.net/@user/post/CODE.")],
  "threads-search": [qp("Keyword or phrase to search public Threads posts (min 2 characters)."), lp(25, 200)],
  "threads-search-users": [qp("Keyword to find Threads users / creators (min 2 characters)."), lp(20, 100)],
  // Bluesky
  "bluesky-profile": [
    up("Bluesky profile URL, @handle, or handle, e.g. bsky.app/profile/handle."),
    cachePWithMaxAge(),
    cacheMaxAgeP(),
  ],
  "bluesky-user-posts": [
    up("Bluesky profile URL, @handle, or handle, e.g. https://bsky.app/profile/handle.bsky.social."),
    lp(25, 100),
    {
      name: "cursor",
      type: "string",
      required: false,
      description:
        "Opaque pagination cursor from the previous nextCursor. Leave empty for the first page. Do not invent a cursor from publishedAt — the feed is ordered by feed time (reposts sort by repost time).",
    },
    {
      name: "filter",
      type: "string",
      required: false,
      description:
        "Bluesky getAuthorFeed filter: posts_with_replies (default), posts_no_replies, posts_with_media, posts_and_author_threads, or posts_with_video. Controls replies/media/threads — not reposts. Use includeReposts=false to drop reposts.",
    },
    {
      name: "includeReposts",
      type: "boolean",
      required: false,
      description:
        "When false, omit repost rows (reasonRepost). Default true — reposts are included and marked with isRepost / repostedBy / repostedAt.",
    },
    cacheP(),
  ],
  "bluesky-post-details": [
    up("Bluesky post URL, e.g. https://bsky.app/profile/handle/post/RKEY."),
    {
      name: "depth",
      type: "integer",
      required: false,
      description:
        "Reply nesting levels under the post (0 = post only with no replies[], default 1, max 6). Maps to Bluesky getPostThread depth.",
    },
    cacheP(),
  ],
  // Pinterest
  "pinterest-pin-details": [up("Pinterest pin URL, e.g. https://pinterest.com/pin/ID/.")],
  "pinterest-user-pins": [up("Pinterest profile URL or username."), lp(25, 200)],
  "pinterest-search": [qp("Keywords or search query (min 2 characters)."), lp(25, 200)],
  "pinterest-board": [
    up(
      "Pinterest board URL (.../username/board-name/), not a /pin/ URL. Example: https://www.pinterest.com/potterybarn/rustic-lodge-lookbook/.",
    ),
    lp(25, 200),
  ],
  "pinterest-user-boards": [up("Pinterest profile URL or username."), lp(25, 200)],
  // LinkedIn
  "linkedin-profile": [up("LinkedIn profile URL, e.g. https://www.linkedin.com/in/paul-martin-a5aa98.")],
  "linkedin-company": [up("LinkedIn company URL, e.g. https://www.linkedin.com/company/shopify.")],
  "linkedin-post-details": [up("LinkedIn post or activity URL.")],
  "linkedin-post-transcript": [up("LinkedIn post or activity URL.")],
  "linkedin-company-posts": [
    up("LinkedIn company URL, e.g. https://linkedin.com/company/slug."),
    lp(20, 100),
    {
      name: "cursor",
      type: "string",
      required: false,
      description:
        "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response (numeric offset, e.g. 20). A null nextCursor means the end of the list (max 100 posts).",
    },
  ],
  "linkedin-search-posts": [qp(), { name: "sort", type: "string", required: false, description: "relevance or date. Default relevance." }, lp(20, 50)],
  // Rumble
  "rumble-video-details": [up("Rumble video URL, e.g. https://rumble.com/vXXXX-title.html.")],
  "rumble-video-transcript": [
    up("Rumble video URL, e.g. https://rumble.com/vXXXX-title.html."),
    lang(),
    cacheP(),
  ],
  "rumble-channel-videos": [up("Rumble channel URL, e.g. https://rumble.com/c/name."), lp(20, 200)],
  "rumble-search": [qp("Keywords or search query (min 2 characters)."), lp(20, 200)],
  "rumble-comments": [up("Rumble video URL, e.g. https://rumble.com/vXXXX-title.html."), lpFlat(50, 500, 2)],
  // Twitch
  "twitch-profile": [up(TWITCH_PROFILE), cachePWithMaxAge(), cacheMaxAgeP()],
  "twitch-user-videos": [
    up(TWITCH_PROFILE),
    {
      name: "limit",
      type: "integer",
      required: false,
      description:
        "Max items to return (default 20, max 100). Flat 2 credits per call. Hard ceiling: first 100 matching videos only — deeper history is not available (windowMax=100).",
    },
    {
      name: "filterBy",
      type: "string",
      required: false,
      description:
        "ARCHIVE | HIGHLIGHT | UPLOAD. Omit for all types — there is no default filter (filterBy is null when omitted).",
    },
    { name: "sortBy", type: "string", required: false, description: "TIME (default, newest first) or VIEWS." },
    {
      name: "cursor",
      type: "string",
      required: false,
      description:
        "Pagination cursor = last video id from the previous nextCursor. Leave empty for the first page. Pages the first 100 matching videos only (not a raw offset).",
    },
  ],
  "twitch-user-schedule": [
    up(TWITCH_PROFILE),
    {
      name: "limit",
      type: "integer",
      required: false,
      description: "Max schedule segments to return (default 50, max 100). Flat 1 credit per call.",
    },
  ],
  "twitch-clip": [up("Twitch clip URL, channel URL, or username."), cachePWithMaxAge(), cacheMaxAgeP()],
  // Spotify
  "spotify-artist": [
    up(SPOTIFY_URL),
    {
      name: "raw",
      type: "boolean",
      required: false,
      description:
        "Include the upstream GraphQL payload as data.raw. Default false — omit unless you need fields not in the normalized shape (~80% of the old response body).",
    },
    cacheP(),
  ],
  "spotify-track": [
    up(SPOTIFY_URL),
    {
      name: "raw",
      type: "boolean",
      required: false,
      description:
        "Include the upstream GraphQL payload as data.raw. Default false — getTrack embeds bulky artist discography.",
    },
    cacheP(),
  ],
  "spotify-album": [
    up(SPOTIFY_URL),
    {
      name: "raw",
      type: "boolean",
      required: false,
      description:
        "Include the upstream GraphQL payload as data.raw. Default false — omit unless you need fields not in the normalized shape.",
    },
    cacheP(),
  ],
  "spotify-search": [
    qp("Search term (min 2 chars)."),
    {
      name: "type",
      type: "string",
      required: false,
      description:
        "Result kind: tracks (default), albums, artists, podcasts, or episodes.",
    },
    lpFlat(20, 50, 2),
    {
      name: "raw",
      type: "boolean",
      required: false,
      description:
        "Include per-result upstream payload as results[].raw. Default false. Pathfinder GraphQL vs Apify scraper shapes differ — see FAQ.",
    },
    cacheP(),
  ],
  "spotify-podcast": [
    {
      name: "url",
      type: "url",
      required: true,
      description: "Spotify show/podcast URL, URI, or ID (e.g. https://open.spotify.com/show/…). Not an artist URL.",
    },
    cacheP(),
  ],
  "spotify-podcast-episodes": [
    {
      name: "url",
      type: "url",
      required: true,
      description: "Spotify show/podcast URL, URI, or ID (e.g. https://open.spotify.com/show/…). Not an artist URL.",
    },
    lpFlat(20, 50, 2),
    CURSOR,
    {
      name: "raw",
      type: "boolean",
      required: false,
      description:
        "Include slimmed per-episode upstream payload as episodes[].raw. Default false. visualIdentity / playedState / podcastV2 are never included.",
    },
    cacheP(),
  ],
  // SoundCloud
  "soundcloud-artist": [up(SC_PROFILE), cachePWithMaxAge(), cacheMaxAgeP()],
  "soundcloud-artist-tracks": [
    up(SC_PROFILE),
    lpFlat(20, 100, 2),
    {
      name: "cursor",
      type: "string" as const,
      required: false,
      description:
        "Opaque pagination cursor from the previous nextCursor. Leave empty for the first page. Do not edit or invent values.",
    },
  ],
  "soundcloud-track": [up(SC_TRACK), cachePWithMaxAge(), cacheMaxAgeP()],
  // Linktree / Snapchat
  "linktree-page": [up(LINKTREE_PROFILE), cachePWithMaxAge(), cacheMaxAgeP()],
  "snapchat-user-profile": [up(SNAPCHAT_PROFILE)],
  // Truth Social / Kick / Amazon / Age-Gender
  "truth-social-profile": [up(TRUTH_PROFILE)],
  "truth-social-user-posts": [
    up(TRUTH_PROFILE),
    {
      name: "limit",
      type: "integer",
      required: false,
      description:
        "Max posts to return (default 20, max 80). Capped at 80 because Truth Social's statuses page is ~40 items — use nextCursor for more pages. Flat 2 credits per call. Response `source` is native or extended.",
    },
    CURSOR,
  ],
  "truth-social-post": [up(TRUTH_POST)],
  "kick-clip": [
    up(KICK_CLIP),
    {
      name: "limit",
      type: "integer",
      required: false,
      description:
        "Channel mode only — max recent clips to return (default 30, max 100). Ignored when url is a clip. Flat 1 credit. No cursor — Kick returns a single page.",
    },
    cachePWithMaxAge(),
    cacheMaxAgeP(),
  ],
  "amazon-shop-page": [
    up(AMAZON_SHOP_URL),
    { name: "marketplace", type: "string", required: false, description: "Amazon marketplace code. Default US." },
    lp(20, 200),
    {
      name: "cursor",
      type: "string",
      required: false,
      description: "Pagination cursor from nextCursor (page or page:offset). Leave empty for the first page.",
    },
  ],
  // Account
  "account-balance": [],
  "account-request-history": [
    lpFree(50, 500),
    {
      name: "endpoint",
      type: "string",
      required: false,
      description: "Exact Captapi path filter, e.g. /v1/instagram/basic-profile.",
    },
    {
      name: "statusCode",
      type: "integer",
      required: false,
      description: "Filter by HTTP status code (e.g. 500).",
    },
    {
      name: "since",
      type: "string",
      required: false,
      description: "Inclusive lower bound on createdAt (ISO date or datetime).",
    },
    {
      name: "until",
      type: "string",
      required: false,
      description: "Exclusive upper bound on createdAt (ISO date or datetime).",
    },
  ],
  "account-daily-usage": [{ name: "days", type: "integer", required: false, description: "Number of days to include (default 30, max 365)." }],
  "account-most-used-routes": [
    { name: "days", type: "integer", required: false, description: "Number of days to include (default 30, max 365)." },
    lpFree(20, 100),
  ],
  // Utilities (analytics + uploaded video files)
  "analytics-post": [
    {
      name: "url",
      type: "string",
      required: true,
      description:
        "Public post/video/reel URL from one of 11 platforms: YouTube, TikTok, Instagram, Facebook, X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, or Rumble. Platform is auto-detected — cross-platform URLs are expected here (unlike single-platform endpoints). Not in scope: Kwai, Twitch, Spotify, Snapchat, and other Captapi platforms.",
    },
    cacheP(),
  ],
  "analytics-compare": [
    {
      name: "urls",
      type: "string",
      required: true,
      description:
        "Comma-separated post/video/reel URLs (up to 10), any mix of the same 11 platforms as Post Analytics. Example: a TikTok URL and a YouTube URL in one call.",
    },
    cacheP(),
  ],
  "video-transcript": [
    {
      name: "file",
      type: "file",
      required: true,
      description:
        "Video or audio file (multipart form field — use -F file=@path, not a query string). Max 200MB / 60 minutes.",
    },
    {
      name: "language",
      type: "string",
      required: false,
      description: 'ISO-639-1 Whisper language hint, e.g. "en" or "tr". Omit to auto-detect.',
    },
    {
      name: "translate",
      type: "boolean",
      required: false,
      description: "When true, translate speech to English (Whisper translations API). Default false.",
    },
    {
      name: "timestampGranularity",
      type: "string",
      required: false,
      description: "segment (default) or word — word-level timings when Whisper exposes them.",
    },
  ],
  "video-summarize": [
    {
      name: "file",
      type: "file",
      required: true,
      description:
        "Video or audio file (multipart form field — use -F file=@path, not a query string). Max 200MB / 60 minutes.",
    },
    {
      name: "language",
      type: "string",
      required: false,
      description: 'ISO-639-1 Whisper language hint, e.g. "en" or "tr". Omit to auto-detect.',
    },
    {
      name: "translate",
      type: "boolean",
      required: false,
      description: "When true, translate speech to English before summarizing. Default false.",
    },
    {
      name: "timestampGranularity",
      type: "string",
      required: false,
      description: "segment (default) or word.",
    },
  ],
  // Kwai / small creator pages
  "kwai-profile": [up(KWAI_PROFILE)],
  "kwai-user-posts": [
    up(KWAI_PROFILE),
    {
      name: "limit",
      type: "number" as const,
      required: false,
      description: "Max posts to return (1–200). Default 20. ~1 credit per post returned (min 2).",
    },
    {
      name: "cursor",
      type: "string" as const,
      required: false,
      description:
        "Opaque pagination cursor from the previous nextCursor. Pages within posts from one profile fetch.",
    },
  ],
  "kwai-post": [up(KWAI_POST)],
  "komi-page": [up(KOMI_PAGE), cachePWithMaxAge(), cacheMaxAgeP()],
  "pillar-page": [up(PILLAR_PAGE), cachePWithMaxAge(), cacheMaxAgeP()],
  "linkbio-page": [up(LINKBIO_PAGE), cachePWithMaxAge(), cacheMaxAgeP()],
  "linkme-profile": [up(LINKME_PROFILE), cachePWithMaxAge(), cacheMaxAgeP()],
  // GitHub
  "github-user": [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL, e.g. getify or https://github.com/getify." }],
  "github-repositories": [
    { name: "username", type: "string", required: true, description: "GitHub username or profile URL, e.g. torvalds." },
    {
      name: "sort",
      type: "string",
      required: false,
      description:
        "created | updated | pushed | full_name (default updated). Not stars — GitHub's user-repos API has no stars sort. Echoed as data.sort.",
    },
    {
      name: "direction",
      type: "string",
      required: false,
      description: "asc or desc (default desc). Echoed as data.direction.",
    },
    {
      name: "type",
      type: "string",
      required: false,
      description: "owner (default) | member | all — affiliation filter. Echoed as data.type.",
    },
    lp(30, 100),
    GH_OPAQUE_CURSOR,
  ],
  "github-repository": [{ name: "repo", type: "string", required: true, description: "Repository URL or owner/name, e.g. torvalds/linux or https://github.com/torvalds/linux." }],
  "github-pull-requests": [
    { name: "repo", type: "string", required: true, description: "Repository URL or owner/name, e.g. vercel/next.js." },
    {
      name: "state",
      type: "string",
      required: false,
      description: "open (API default), closed, or all. Echoed as data.state. Docs example uses closed so mergedAt is visible.",
    },
    lp(30, 100),
    GH_OPAQUE_CURSOR,
  ],
  "github-activity": [
    {
      name: "username",
      type: "string",
      required: true,
      description: "GitHub username or profile URL, e.g. getify.",
    },
    lp(30, 90),
    {
      name: "cursor",
      type: "string",
      required: false,
      description:
        "Opaque cursor from a previous nextCursor. Pagination stops after GitHub's 90-event public activity ceiling.",
    },
  ],
  "github-followers": [
    {
      name: "username",
      type: "string",
      required: true,
      description: "GitHub username or profile URL, e.g. getify.",
    },
    lp(30, 100),
    GH_OPAQUE_CURSOR,
  ],
  "github-following": [
    {
      name: "username",
      type: "string",
      required: true,
      description: "GitHub username or profile URL, e.g. getify.",
    },
    lp(30, 100),
    GH_OPAQUE_CURSOR,
  ],
  "github-contributions": [
    {
      name: "username",
      type: "string",
      required: true,
      description: "GitHub username or profile URL, e.g. getify or https://github.com/getify.",
    },
  ],
  "github-trending-repositories": [
    {
      name: "since",
      type: "string",
      required: false,
      description: "Trending window: daily (default), weekly, or monthly — matches github.com/trending?since=.",
    },
    {
      name: "language",
      type: "string",
      required: false,
      description: "Optional programming-language slug (e.g. python, typescript) → /trending/{language}.",
    },
    lpFlat(25, 100, 2),
  ],
  "github-trending-developers": [
    {
      name: "since",
      type: "string",
      required: false,
      description: "Trending window: daily (default), weekly, or monthly — matches github.com/trending/developers?since=.",
    },
    {
      name: "language",
      type: "string",
      required: false,
      description: "Optional programming-language slug → /trending/developers/{language}.",
    },
    lpFlat(25, 100, 2),
  ],
  // TikTok Shop
  "tiktok-shop-search": [
    qp("Product search query (min 2 characters), e.g. phone case."),
    {
      name: "region",
      type: "string",
      required: false,
      description:
        "Two-letter market region for the search (default US). Echoed on the response as data.region — not a creator home country.",
    },
    lp(20, 200),
  ],
  "tiktok-shop-products": [
    up("TikTok Shop store URL, e.g. https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079."),
    {
      name: "region",
      type: "string",
      required: false,
      description:
        "Two-letter market region (default US). Non-US coverage depends on TikTok exposing that shop in the selected region — empty results outside the US are often a platform limit, not a Captapi bug.",
    },
    lpFlat(20, 200, 2),
  ],
  "tiktok-shop-product-details": [
    up("TikTok Shop product URL, e.g. https://www.tiktok.com/shop/pdp/1731098552908944370."),
    {
      name: "region",
      type: "string",
      required: false,
      description:
        "Two-letter market region for the secondary fetch path (default US). Primary SSR uses the product URL's market; empty/partial non-US results are often a TikTok exposure limit.",
    },
  ],
  "tiktok-shop-product-reviews": [
    up("TikTok Shop product URL, e.g. https://www.tiktok.com/shop/pdp/1731962298839634826."),
    lp(20, 200),
  ],
  "tiktok-shop-user-showcase": [
    {
      name: "username",
      type: "string",
      required: true,
      description:
        "TikTok username, @handle, or profile URL, e.g. jeffreestar or https://www.tiktok.com/@jeffreestar.",
    },
    lp(20, 200),
  ],
  // Ad Library
  "facebook-ad-library-search": [
    qp("Keyword, brand, or advertiser to search Meta Ad Library (min 2 characters)."),
    { name: "country", type: "string", required: false, description: "Two-letter ISO country code (e.g. US, GB, DE). Default US." },
    lpFlat(20, 200, 2),
    {
      name: "status",
      type: "string",
      required: false,
      description: 'Ad delivery status: ACTIVE (default), INACTIVE, or ALL. Use ACTIVE for "what are they running now?".',
    },
    {
      name: "media_type",
      type: "string",
      required: false,
      description: "Creative filter: ALL (default), IMAGE, VIDEO, MEME, IMAGE_AND_MEME, or NONE.",
    },
    {
      name: "platforms",
      type: "string",
      required: false,
      description: "Comma-separated publisher platforms to keep: FACEBOOK, INSTAGRAM, MESSENGER, AUDIENCE_NETWORK, THREADS.",
    },
    {
      name: "ad_type",
      type: "string",
      required: false,
      description: "all (default) or political_and_issue_ads. Spend/impressions are typically only filled for political/issue ads.",
    },
    {
      name: "search_type",
      type: "string",
      required: false,
      description: "keyword_unordered (default) or keyword_exact_phrase.",
    },
    {
      name: "sort_by",
      type: "string",
      required: false,
      description: "Meta sort mode: total_impressions or relevancy_monthly_grouped.",
    },
    {
      name: "start_date",
      type: "string",
      required: false,
      description: "Only ads with delivery start on/after this date (YYYY-MM-DD).",
    },
    {
      name: "end_date",
      type: "string",
      required: false,
      description: "Only ads with delivery start on/before this date (YYYY-MM-DD).",
    },
    {
      name: "cursor",
      type: "string",
      required: false,
      description: "Pagination cursor from a previous nextCursor. Pages through the current Meta HTML result batch.",
    },
    {
      name: "trim",
      type: "boolean",
      required: false,
      description:
        "SC-compatible. Captapi is already lean vs Meta nested snapshots; when true, omit cards/images/videos typed arrays (media[] stays).",
    },
    cacheP(),
  ],
  "facebook-ad-library-company-ads": [
    up(
      "pageId from /search-companies (preferred), libraryUrl, vanity page URL (facebook.com/nike/), or Ad Library URL with view_all_page_id. Do not pass profileId from facebook.com/{digits}/ when it differs from pageId."
    ),
    { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." },
    lp(20, 200),
  ],
  "facebook-ad-library-search-companies": [
    qp("Company or brand name to search for (min 2 characters). Name-matched — off-brand pages are dropped."),
    { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." },
    lp(20, 200),
    cacheP(),
  ],
  "facebook-ad-library-ad-details": [up("Meta Ad Library ad URL or ad ID.")],
  "facebook-ad-library-ad-transcript": [up("Meta Ad Library ad URL or ad ID.")],
  "tiktok-ad-library-search": [
    qp("Keyword or advertiser to search TikTok Commercial Content Library (min 2 characters)."),
    {
      name: "country",
      type: "string",
      required: false,
      description: "Two-letter ISO country code (e.g. GB, DE, FR). Default GB (EU DSA library; US often empty).",
    },
    {
      name: "match",
      type: "string",
      required: false,
      description: 'Keyword token mode: "any" (default, OR whole-word) or "all" (AND). hair ≠ wheelchair. Empty results are free.',
    },
    lpFlat(20, 200, 2),
    cacheP(),
  ],
  "tiktok-ad-library-top-ads": [
    {
      name: "q",
      type: "string",
      required: false,
      description:
        "Optional keyword — case-insensitive whole-word match on title/brand/tags/industry (hair ≠ wheelchair). Each returned ad includes matchedFrom (which fields matched). Envelope candidatesScanned is the pre-filter pool size.",
    },
    {
      name: "match",
      type: "string",
      required: false,
      description:
        'Keyword token mode: "any" (default, OR) or "all" (AND). Zero literal hits → empty ads[] (never an unfiltered soft list).',
    },
    {
      name: "country",
      type: "string",
      required: false,
      description: "Two-letter ISO country code. Default US.",
    },
    {
      name: "period",
      type: "number",
      required: false,
      description: "Lookback window in days: 7, 30, or 180. Default 30.",
    },
    {
      name: "orderBy",
      type: "string",
      required: false,
      description: "Sort: for_you, likes, ctr, impressions, or cost. Default for_you.",
    },
    {
      name: "industry",
      type: "string",
      required: false,
      description: "Optional industry key or label from Creative Center.",
    },
    {
      name: "objective",
      type: "string",
      required: false,
      description: "Optional campaign objective (e.g. Traffic, Conversion, Reach).",
    },
    {
      name: "adFormat",
      type: "string",
      required: false,
      description: "Optional format filter: spark or non_spark.",
    },
    {
      name: "limit",
      type: "integer",
      required: false,
      description:
        "Max items to return (default 20, max 100). Flat 2 credits on Decodo-native; Apify ~1 credit per returned ad (min 2).",
    },
    cacheP(),
  ],
  "tiktok-ad-library-ad-details": [
    up("TikTok Ad Library URL or ad ID."),
    {
      name: "country",
      type: "string",
      required: false,
      description: "Two-letter ISO country code. Default GB.",
    },
  ],
  "linkedin-ad-library-search-ads": [
    { name: "q", type: "string", required: false, description: "Advertiser / account owner name (min 2 when used). Provide q/company, keyword, or companyId." },
    { name: "company", type: "string", required: false, description: "SC alias of q — advertiser / account owner name." },
    { name: "keyword", type: "string", required: false, description: "Optional keyword filter on ad creative copy." },
    { name: "companyId", type: "string", required: false, description: "LinkedIn numeric company id for exact advertiser match." },
    { name: "country", type: "string", required: false, description: "Single ISO country code. Default US. Ignored when countries is set." },
    { name: "countries", type: "string", required: false, description: "Comma-separated ISO country codes (e.g. US,CA,MX)." },
    { name: "startDate", type: "string", required: false, description: "Custom range start YYYY-MM-DD (use with endDate)." },
    { name: "endDate", type: "string", required: false, description: "Custom range end YYYY-MM-DD (use with startDate)." },
    { name: "cursor", type: "string", required: false, description: "Pagination token from paginationToken / nextCursor." },
    { name: "paginationToken", type: "string", required: false, description: "SC alias of cursor." },
    lp(20, 200),
  ],
  "linkedin-ad-library-ad-details": [up("LinkedIn Ad Library URL or ad ID.")],
  "google-ad-library-company-ads": [
    {
      name: "advertiser",
      type: "string",
      required: true,
      description:
        "Advertiser name, domain (e.g. nike.com), or Google advertiser ID (AR…). Prefer AR… from advertiser-search.",
    },
    { name: "country", type: "string", required: false, description: "Two-letter ISO country / region code (soft filter). Default US. Alias: region." },
    { name: "region", type: "string", required: false, description: "Alias for country." },
    { name: "start_date", type: "string", required: false, description: "YYYY-MM-DD — keep creatives whose shown window overlaps this start." },
    { name: "end_date", type: "string", required: false, description: "YYYY-MM-DD — keep creatives whose shown window overlaps this end." },
    {
      name: "sort",
      type: "string",
      required: false,
      description: "Client-side sort: last_shown (recent activity first) or first_shown. Default is ATC order.",
    },
    { name: "cursor", type: "string", required: false, description: "Pagination cursor from nextCursor." },
    { name: "topic", type: "string", required: false, description: 'Only "all" is supported (commercial ATC).' },
    lpFlat(20, 200, 2),
    cacheP(),
  ],
  "google-ad-library-ad-details": [{ name: "creative_id", type: "string", required: true, description: "Google Ads Transparency URL containing AR... advertiser and CR... creative IDs." }, { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }],
  "google-ad-library-advertiser-search": [
    qp("Brand, domain, or advertiser name (min 2 characters). Expanded + ranked so US prefers Inc. over SRL."),
    {
      name: "country",
      type: "string",
      required: false,
      description: "Two-letter ISO country code used for ranking (e.g. US). Default US.",
    },
    lpFlat(10, 50, 1),
    cacheP(),
  ],
};

export function params(ep: ApiEndpoint): ApiParam[] {
  const explicit = ENDPOINT_PARAMS[ep.slug];
  if (explicit) return withCacheParam(ep, explicit);
  // Fallback (should not happen for catalog endpoints): derive from category.
  const base: ApiParam[] = [];
  if (ep.category === "search") base.push(qp());
  else base.push(up(`Public ${PLATFORM_LABEL[ep.platform]} URL.`));
  if (["comments", "search", "list"].includes(ep.category)) base.push(lp(20, 200));
  if (ep.category === "transcript" || ep.category === "summarize") base.push(lang());
  return withCacheParam(ep, base);
}

/** Every data endpoint accepts an optional `cache` param (default false =
 * always fresh). Set `cache=true` to serve from the 24h response cache.
 * Account endpoints (balance, usage) are live reads with no cache layer. */
function withCacheParam(ep: ApiEndpoint, list: ApiParam[]): ApiParam[] {
  // Account + utilities manage cache (or skip it) explicitly per endpoint.
  if (
    ep.platform === "account" ||
    ep.platform === "utilities" ||
    list.some((p) => p.name === "cache")
  ) {
    return list;
  }
  return [...list, cacheP()];
}

function exampleData(ep: ApiEndpoint): Record<string, unknown> {
  const real = API_EXAMPLES[ep.slug];
  if (real) return real;
  // Never fall through to the generic list lorem (example.com) for the
  // showcase compare endpoint — that kills the cross-platform positioning.
  // analytics-* must come from API_EXAMPLES (gen_examples.py). Never fall
  // through to list/details lorem (example.com / "Latest upload").

  switch (ep.category) {
    case "transcript":
      // Two families — never cross-contaminate:
      //   • file upload (video-transcript): transcript + transcriptSegments + segments:number
      //   • timed captions/ASR (youtube, youtube-audio, tiktok, instagram, rumble):
      //       text + segments[{text,startMs,endMs}]
      if (ep.slug === "video-transcript") {
        return {
          filename: "sample.mp4",
          transcript:
            "Hey everyone, welcome back to the channel. Today we're breaking down structured data APIs.",
          wordCount: 14,
          segments: 2,
          language: "english",
          durationSeconds: 8.4,
          duration: 8.4,
          creditsCharged: 1,
          noSpeech: false,
          transcriptSegments: [
            {
              text: "Hey everyone, welcome back to the channel.",
              start: 0.0,
              duration: 4.12,
              end: 4.12,
              timestamp: "00:00",
            },
            {
              text: "Today we're breaking down structured data APIs.",
              start: 4.12,
              duration: 4.28,
              end: 8.4,
              timestamp: "00:04",
            },
          ],
        };
      }
      if (
        ep.slug === "youtube-audio-transcript" ||
        ep.slug === "rumble-video-transcript"
      ) {
        return {
          platform: ep.platform,
          ...(ep.slug === "youtube-audio-transcript"
            ? {
                videoId: "jNQXAC9IVRw",
                url: "https://www.youtube.com/watch?v=jNQXAC9IVRw",
                source: "asr",
                asrProvider: "groq-whisper-large-v3-turbo",
                languageIsDetected: true,
                creditsUsed: 2,
              }
            : {
                id: "v7cv2cc",
                url: "https://rumble.com/v7cv2cc-now-i-can-finally-talk-about-it-ep.-2555-07172026.html",
                source: "captions",
                languageName: "English (auto)",
              }),
          language: ep.slug === "rumble-video-transcript" ? "en-auto" : "en",
          durationSeconds: ep.slug === "rumble-video-transcript" ? 5185 : 19,
          segments: [
            { text: "Alright, so here we are in front of the elephants.", startMs: 0, endMs: 4000 },
            {
              text: "The cool thing about these guys is that they have really, really, really long fronts.",
              startMs: 4000,
              endMs: 12000,
            },
          ],
          text: "Alright, so here we are in front of the elephants. The cool thing about these guys is that they have really, really, really long fronts.",
        };
      }
      return {
        platform: ep.platform,
        url:
          ep.platform === "tiktok"
            ? "https://www.tiktok.com/@creator/video/7123456789012345678"
            : ep.platform === "instagram"
              ? "https://www.instagram.com/reel/ABC123xyz/"
              : "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        ...(ep.slug === "youtube-transcript" || ep.slug === "youtube-shorts-transcript"
          ? {
              videoId: "dQw4w9WgXcQ",
              title: "Example video",
              source: "captions",
              requestedLanguage: null,
              returnedLanguage: "en",
              isAutoGenerated: false,
              isTranslated: false,
              hasAutoCaptions: true,
              availableLanguages: [
                { languageCode: "en", languageName: "English", isAutoGenerated: false },
              ],
            }
          : {
              source: ep.platform === "tiktok" ? "captions" : undefined,
              language: "en",
            }),
        text: "Hey everyone, welcome back to the channel. Today we're breaking down structured data APIs.",
        segments: [
          {
            text: "Hey everyone, welcome back to the channel.",
            startMs: 0,
            endMs: 4120,
          },
          {
            text: "Today we're breaking down structured data APIs.",
            startMs: 4120,
            endMs: 8400,
          },
        ],
      };
    case "summarize":
      return {
        summary: "A concise walkthrough of how to extract structured data from social video at scale.",
        keyPoints: ["One key per platform", "24h shared cache", "No OAuth required"],
        topics: ["APIs", "data extraction", "automation"],
        sentiment: "positive",
      };
    case "details":
      return {
        id: "dQw4w9WgXcQ",
        title: "Example video",
        author: "@creator",
        views: 1842203,
        likes: 95210,
        comments: 4123,
        durationSec: 213,
        publishedAt: "2024-11-02T10:00:00Z",
      };
    case "comments":
      return {
        totalReturned: 2,
        totalComments: 2446085,
        nextCursor: null,
        hasMore: false,
        comments: [
          {
            id: "Ugcomment001",
            author: "@viewer1",
            authorChannelId: "UCexample001",
            text: "This is exactly what I needed!",
            likeCount: 42,
            replyCount: 3,
            hasCreatorHeart: false,
            publishedTimeText: "6 years ago",
            publishedTimeApprox: "2020-08-03T00:00:00.000Z",
            publishedTimeIsApproximate: true,
          },
          {
            id: "Ugcomment002",
            author: "@viewer2",
            authorChannelId: "UCexample002",
            text: "Great breakdown.",
            likeCount: 11,
            replyCount: 0,
            hasCreatorHeart: false,
            publishedTimeText: "1 month ago",
            publishedTimeApprox: "2026-07-03T00:00:00.000Z",
            publishedTimeIsApproximate: true,
          },
        ],
      };
    case "channel":
      return {
        handle: "@creator",
        name: "Creator",
        followers: 1280000,
        posts: 412,
        verified: true,
        bio: "Building in public.",
      };
    case "search":
      return {
        total: 2,
        results: [
          { title: "Top result", url: "https://example.com/1", author: "@creator", views: 530120 },
          { title: "Second result", url: "https://example.com/2", author: "@maker", views: 210430 },
        ],
      };
    case "list":
      return {
        total: 2,
        items: [
          { title: "Latest upload", url: "https://example.com/a", views: 90120, publishedAt: "2025-01-12" },
          { title: "Previous upload", url: "https://example.com/b", views: 75230, publishedAt: "2025-01-04" },
        ],
      };
  }
}

export function exampleResponse(ep: ApiEndpoint): string {
  return JSON.stringify({ success: true, data: exampleData(ep) }, null, 2);
}

/** Extra 200 OK tabs when an endpoint has multiple request modes. */
export function exampleResponseVariants(
  ep: ApiEndpoint,
): Array<{ label: string; code: string }> {
  const variants = API_EXAMPLE_VARIANTS[ep.slug] || [];
  return variants.map((v) => ({
    label: v.label,
    code: JSON.stringify({ success: true, data: v.data }, null, 2),
  }));
}

function article(label: string): string {
  return /^[aeiou]/i.test(label) ? "an" : "a";
}

/**
 * The exact 404 `detail` string the backend raises for this endpoint, taken
 * from the router sources. Returns null when the endpoint doesn't 404 in
 * practice (most searches return 200 with an empty list instead).
 */
function notFoundDetail(
  ep: ApiEndpoint,
): string | Record<string, unknown> | null {
  const p = ep.platform;

  if (ep.category === "search") {
    return null;
  }
  if (
    ep.slug === "youtube-transcript" ||
    ep.slug === "youtube-summarizer" ||
    ep.slug === "youtube-shorts-transcript" ||
    ep.slug === "youtube-shorts-summarizer"
  ) {
    return {
      code: "no_captions",
      reason:
        "YouTube published no caption tracks for this video. This endpoint returns YouTube's published captions only — it does not generate text from speech. Long live streams often have no auto-captions.",
      message: "Transcript not available for this video",
      availableLanguages: [],
      hasAutoCaptions: false,
      requestedLanguage: null,
    };
  }
  if (ep.category === "transcript" || ep.category === "summarize") {
    return p === "rumble"
      ? "Transcript not available for this Rumble video"
      : "Transcript not available for this video";
  }

  const PROFILE_404: Partial<Record<PlatformId, string>> = {
    youtube: "Channel not found",
    twitch: "Twitch channel not found",
    truth_social: "Truth Social profile not found",
    snapchat: "Snapchat profile not found",
    kwai: "Kwai profile not found",
    linktree: "Linktree profile not found",
    soundcloud: "SoundCloud artist not found",
    github: "Not found on GitHub",
    linkedin: "Not found on LinkedIn",
    bluesky: "Not found on Bluesky",
    reddit: "Subreddit not found",
    facebook: "Page not found",
  };
  if (ep.category === "channel") return PROFILE_404[p] ?? "Profile not found";

  const RESOURCE_404: Partial<Record<PlatformId, string>> = {
    youtube: "Video not found",
    tiktok: "Video not found",
    rumble: "Video not found",
    reddit: "Post not found",
    facebook: "Post not found",
    instagram: "Post not found",
    threads: "Post not found",
    bluesky: "Post not found",
    twitter: "Tweet not found",
    pinterest: "Pin not found",
    facebook_ad_library: "Ad not found",
    tiktok_ad_library: "Ad not found",
    google_ad_library: "Ad not found",
    linkedin_ad_library: "Ad not found",
    facebook_marketplace: "Marketplace listing not found",
    facebook_events: "Event not found",
    spotify: "Spotify item not found",
    kick: "Kick clip not found",
    kwai: "Kwai post not found",
    truth_social: "Truth Social post not found",
    github: "Not found on GitHub",
    linkedin: "Not found on LinkedIn",
    amazon_shop: "Amazon seller storefront not found",
  };
  return RESOURCE_404[p] ?? "Resource not found";
}

/**
 * Realistic non-2xx response bodies for an endpoint, mirroring what the
 * production API actually returns (FastAPI `detail` envelope, structured 429
 * body, `upstream_actor_error` on 502). Shown as extra tabs next to "200 OK".
 */
export function errorExamples(ep: ApiEndpoint): { label: string; code: string }[] {
  const platform = PLATFORM_LABEL[ep.platform];
  const ps = params(ep);
  const urlParam = ps.find((p) => p.name === "url" && p.required);
  const firstRequired = ps.find((p) => p.required) ?? ps[0];

  const list: { label: string; code: string }[] = [];

  if (urlParam) {
    // Platform-mismatch 400: the most common "wrong request" — passing a URL
    // from another platform (e.g. an AI agent sending a TikTok URL here).
    const wrong = ep.platform === "tiktok" ? "YouTube" : "TikTok";
    list.push({
      label: "400",
      code: JSON.stringify(
        {
          detail: `Expected ${article(platform)} ${platform} URL, but received ${article(wrong)} ${wrong} URL. Use the ${wrong} endpoint for that URL, or pass ${article(platform)} ${platform} URL like ${exampleValue(ep, urlParam)}.`,
        },
        null,
        2,
      ),
    });
  } else if (firstRequired) {
    // Missing required parameter -> FastAPI validation error (422).
    list.push({
      label: "422",
      code: JSON.stringify(
        {
          detail: [
            {
              type: "missing",
              loc: ["query", firstRequired.name],
              msg: "Field required",
              input: null,
            },
          ],
        },
        null,
        2,
      ),
    });
  }

  list.push(
    {
      label: "401",
      code: JSON.stringify({ detail: "Invalid or revoked API key" }, null, 2),
    },
  );

  const nf = notFoundDetail(ep);
  if (nf) {
    list.push({ label: "404", code: JSON.stringify({ detail: nf }, null, 2) });
  }

  list.push(
    {
      label: "429",
      code: JSON.stringify(
        {
          detail: {
            error: "rate_limit_exceeded",
            plan: "free",
            limit_per_minute: 40,
            retry_after_seconds: 60,
          },
        },
        null,
        2,
      ),
    },
    {
      label: "502",
      code: JSON.stringify({ success: false, error: "upstream_actor_error" }, null, 2),
    },
  );

  return list;
}

const PROFILE_URL: Record<PlatformId, string> = {
  youtube: "https://www.youtube.com/@MrBeast",
  tiktok: "https://www.tiktok.com/@khaby.lame",
  instagram: "https://www.instagram.com/natgeo/",
  facebook: "https://www.facebook.com/NASA",
  twitter: "https://x.com/NASA",
  reddit: "https://www.reddit.com/r/technology",
  threads: "https://www.threads.net/@zuck",
  bluesky: "https://bsky.app/profile/bsky.app",
  pinterest: "https://www.pinterest.com/nasa",
  linkedin: "https://www.linkedin.com/in/paul-martin-a5aa98",
  rumble: "https://rumble.com/c/Bongino",
  tiktok_shop: "https://shop.tiktok.com/us/pdp/example-product/1234567890",
  facebook_marketplace: "https://www.facebook.com/marketplace/",
  facebook_events: "https://www.facebook.com/events/",
  facebook_ad_library: "https://www.facebook.com/ads/library/",
  tiktok_ad_library: "https://library.tiktok.com/",
  google_ad_library: "https://adstransparency.google.com/",
  linkedin_ad_library: "https://www.linkedin.com/ad-library/",
  github: "https://github.com/vercel/next.js",
  twitch: "https://www.twitch.tv/shroud",
  spotify: "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02",
  soundcloud: "https://soundcloud.com/nasa",
  linktree: "https://linktr.ee/miguelangeles",
  snapchat: "https://www.snapchat.com/@nba",
  truth_social: "https://truthsocial.com/@realDonaldTrump",
  kick: "https://kick.com/xqc",
  amazon_shop: "https://www.amazon.com/sp?seller=A294P4X9EWVXLJ",
  account: "https://captapi.com/dashboard",
  utilities: "https://www.tiktok.com/@tiktok/video/7234567890123456789",
  kwai: "https://www.kwai.com/@topfilmeseseriesnatv",
  komi: "https://komi.io/kimkardashian",
  pillar: "https://pillar.io/angelstrife",
  linkbio: "https://lnk.bio/charlidamelio",
  linkme: "https://link.me/danucd",
};

/** A realistic example value for a single parameter of an endpoint. */
function exampleValue(ep: ApiEndpoint, p: ApiParam): string {
  switch (p.name) {
    case "q":
    case "query": {
      // Keep the Try-it default (and cURL snippet) in sync with the captured
      // example response so users don't see e.g. q=skincare next to a "travel"
      // example. Fall back to a sensible default when no snapshot exists.
      const captured = API_EXAMPLES[ep.slug]?.query;
      if (typeof captured === "string" && captured.trim()) return captured;
      return ep.platform === "youtube" ? "structured data api" : "skincare";
    }
    case "country":
      if (
        ep.slug === "tiktok-ad-library-search" ||
        ep.slug === "tiktok-ad-library-ad-details"
      ) {
        return "GB";
      }
      return "US";
    case "region":
      if (
        ep.slug === "tiktok-ad-library-search" ||
        ep.slug === "tiktok-ad-library-ad-details"
      ) {
        return "GB";
      }
      return "US";
    case "username": {
      if (ep.platform === "github") {
        const ex = API_EXAMPLES[ep.slug] as { login?: string; username?: string } | undefined;
        const captured = ex?.login ?? ex?.username;
        if (typeof captured === "string" && captured.trim()) return captured;
        return "getify";
      }
      return "hydrojug";
    }
    case "repo":
      if (ep.slug === "github-repository") {
        const captured = API_EXAMPLES[ep.slug]?.fullName;
        if (typeof captured === "string" && captured.trim()) return captured;
        return "torvalds/linux";
      }
      return "vercel/next.js";
    case "state":
      // Prefer closed so docs examples show mergedAt when present.
      return ep.slug === "github-pull-requests" ? "closed" : "open";
    case "sort":
      if (ep.slug === "github-repositories") return "pushed";
      return "relevance";
    case "direction":
      return "desc";
    case "type":
      if (ep.slug === "github-repositories") return "owner";
      if (ep.slug === "spotify-search") return "tracks";
      if (ep.slug.startsWith("youtube-")) return "video";
      return "all";
    case "location":
      return "Austin, TX";
    case "details":
      return "false";
    case "advertiser":
      return "nike.com";
    case "creative_id":
      return "https://adstransparency.google.com/advertiser/AR16735076323512287233/creative/CR13596485266373083137";
    case "comment_id":
      return "7311234567890123456";
    case "limit":
      return ep.slug === "github-trending-repositories" ? "25" : "20";
    case "since":
      return "daily";
    case "language":
      // GitHub trending uses a programming-language slug, not ISO speech codes.
      if (
        ep.slug === "github-trending-repositories" ||
        ep.slug === "github-trending-developers"
      ) {
        return "python";
      }
      return "en";
    case "id": {
      // Keep the Try-it default in sync with the captured example response.
      const captured = API_EXAMPLES[ep.slug]?.id;
      if (typeof captured === "string" && captured.trim()) return captured;
      return "highlight:18201653992314974";
    }
    case "userId": {
      const ex = API_EXAMPLES[ep.slug];
      const captured = (ex?.id ?? ex?.pk) as unknown;
      if (typeof captured === "string" && captured.trim()) return captured;
      return "13460080";
    }
    case "urls": {
      const ex = API_EXAMPLES[ep.slug] as { results?: Array<{ url?: string }> } | undefined;
      const captured = (ex?.results || [])
        .map((r) => (typeof r?.url === "string" ? r.url : ""))
        .filter(Boolean)
        .slice(0, 10);
      if (captured.length >= 2) return captured.join(",");
      return (
        "https://www.tiktok.com/@khaby.lame/video/7646812028874673439," +
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
      );
    }
    case "file":
      return "@video.mp4";
    case "url": {
      // Prefer a captured snapshot URL when it's a valid http(s) URL — keeps
      // Try-it / cURL in sync with the example response for every url param.
      const ex = API_EXAMPLES[ep.slug];
      const captured =
        (typeof ex?.url === "string" && ex.url) ||
        (typeof ex?.board === "string" && ex.board) ||
        (typeof ex?.artistUrl === "string" && ex.artistUrl) ||
        null;
      if (typeof captured === "string" && /^https?:\/\//.test(captured)) return captured;

      // Kick clip primary example is clip mode — do not pick the channel URL
      // just because the param description also mentions "channel".
      if (ep.slug === "kick-clip") {
        const clip = ex?.clip as { url?: string } | undefined;
        if (typeof clip?.url === "string" && /^https?:\/\//.test(clip.url)) return clip.url;
      }

      const d = p.description.toLowerCase();
      const creatorPagePlatforms: PlatformId[] = ["komi", "pillar", "linkbio", "linkme"];

      // X Communities — never fall through to the platform tweet exampleUrl.
      if (ep.slug === "twitter-community" || ep.slug === "twitter-community-tweets") {
        return "https://x.com/i/communities/1493446837214187523";
      }
      // Pinterest board — never fall through to the platform pin exampleUrl.
      if (ep.slug === "pinterest-board") {
        return "https://www.pinterest.com/potterybarn/rustic-lodge-lookbook/";
      }
      // Spotify podcast pair — never fall through to the platform artist exampleUrl.
      if (ep.slug === "spotify-podcast" || ep.slug === "spotify-podcast-episodes") {
        return "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk";
      }
      // SoundCloud track — never fall through to the platform profile exampleUrl.
      if (ep.slug === "soundcloud-track") {
        return "https://soundcloud.com/nasa/episode-179-life-support";
      }
      if (ep.slug === "twitch-user-schedule") {
        const u = API_EXAMPLES[ep.slug]?.username;
        if (typeof u === "string" && u.trim()) return `https://www.twitch.tv/${u}`;
        return "https://www.twitch.tv/criticalrole";
      }
      if (ep.slug === "facebook-marketplace-item" || d.includes("marketplace item"))
        // Available listing from marketplace-search fixture (sold URLs 404 after expiry).
        return "https://www.facebook.com/marketplace/item/2467979733629080/";
      if (d.includes("playlist"))
        return "https://www.youtube.com/playlist?list=PLrAXtmqj7v3Y";
      // Music/sound/audio heuristics — never apply to SoundCloud (use profile/track URLs).
      if (
        ep.platform !== "soundcloud" &&
        (d.includes("music") || d.includes("sound") || d.includes("audio"))
      )
        return ep.platform === "tiktok"
          ? "https://www.tiktok.com/music/original-sound-7300000000000000000"
          : "https://www.instagram.com/reels/audio/1234567890123456/";
      if (d.includes("event"))
        return "https://www.facebook.com/events/1269179411830316";
      if (d.includes("group"))
        return "https://www.facebook.com/groups/123456789012345";
      if (d.includes("subreddit"))
        return "https://www.reddit.com/r/technology/";
      if (d.includes("company"))
        return "https://www.linkedin.com/company/shopify";
      // Creator-page platforms: never treat "page" in the description as Facebook.
      if (creatorPagePlatforms.includes(ep.platform))
        return PROFILE_URL[ep.platform];
      if (d.includes("page") && ep.platform === "facebook") return PROFILE_URL.facebook;
      if (d.includes("channel") || d.includes("profile") || d.includes("@handle"))
        return PROFILE_URL[ep.platform];
      if (ep.platform === "soundcloud") return PROFILE_URL.soundcloud;
      return getGroup(ep.platform).exampleUrl;
    }
    default:
      return "value";
  }
}

/** The required params (or the primary param if none required) for an example call. */
function exampleArgs(ep: ApiEndpoint): { name: string; value: string }[] {
  const ps = params(ep);
  const required = ps.filter((p) => p.required);
  let chosen = required.length > 0 ? required : ps.slice(0, 1);
  // Pull-requests docs snapshot uses state=closed so mergedAt is visible.
  if (ep.slug === "github-pull-requests") {
    const state = ps.find((p) => p.name === "state");
    if (state && !chosen.some((p) => p.name === "state")) {
      chosen = [...chosen, state];
    }
  }
  // Repositories docs show sort=pushed (most recently pushed).
  if (ep.slug === "github-repositories") {
    for (const name of ["sort", "direction", "type"] as const) {
      const p = ps.find((x) => x.name === name);
      if (p && !chosen.some((c) => c.name === name)) chosen = [...chosen, p];
    }
  }
  return chosen.map((p) => ({
    name: p.name,
    value: exampleValue(ep, p),
  }));
}

export function exampleQueryString(ep: ApiEndpoint): string {
  return exampleArgs(ep)
    .map((a) => `${a.name}=${encodeURIComponent(a.value)}`)
    .join("&");
}

export function exampleUrl(ep: ApiEndpoint): string {
  if (isMultipartPost(ep)) return `${API_URL}${ep.path}`;
  const qs = exampleQueryString(ep);
  return qs ? `${API_URL}${ep.path}?${qs}` : `${API_URL}${ep.path}`;
}

/** True when the endpoint accepts a multipart file upload (POST + type:file). */
export function isMultipartPost(ep: ApiEndpoint): boolean {
  return ep.method === "POST" && params(ep).some((p) => p.type === "file");
}

export function curlExample(ep: ApiEndpoint): string {
  const key = "capt_live_...";
  if (isMultipartPost(ep)) {
    const fileParam = params(ep).find((p) => p.type === "file");
    const fileName = (fileParam ? exampleValue(ep, fileParam) : "@video.mp4").replace(/^@/, "");
    const extras = params(ep)
      .filter((p) => p.type !== "file" && p.required)
      .map((p) => ` \\\n  -F "${p.name}=${exampleValue(ep, p)}"`)
      .join("");
    return (
      `curl -X POST "${API_URL}${ep.path}" \\\n` +
      `  -H "Authorization: Bearer ${key}" \\\n` +
      `  -F "file=@${fileName}"${extras}`
    );
  }
  return `curl "${exampleUrl(ep)}" \\\n  -H "Authorization: Bearer ${key}"`;
}

/** A placeholder example value for a single param (used in form inputs). */
export function paramPlaceholder(ep: ApiEndpoint, p: ApiParam): string {
  return exampleValue(ep, p);
}

/**
 * Example values keyed by param name. Required params (or the primary param
 * when none are required) are pre-filled; optional params start blank.
 */
export function exampleValues(ep: ApiEndpoint): Record<string, string> {
  const ps = params(ep);
  const required = ps.filter((p) => p.required);
  const fill = new Set((required.length > 0 ? required : ps.slice(0, 1)).map((p) => p.name));
  const out: Record<string, string> = {};
  for (const p of ps) out[p.name] = fill.has(p.name) ? exampleValue(ep, p) : "";
  return out;
}

/**
 * Multi-language, copy-pasteable request examples built from a set of
 * parameter values. Empty values are omitted from the query string. Pass an
 * `apiKey` to inject a real, runnable key into the snippets.
 * Covers cURL, Python, Node, PHP, Go, and Java.
 */
/** Active (non-empty) parameter values for an endpoint, in declared order. */
export function activeArgs(
  ep: ApiEndpoint,
  values: Record<string, string>,
): { name: string; value: string }[] {
  return params(ep)
    .map((p) => ({ name: p.name, value: (values[p.name] ?? "").trim() }))
    .filter((a) => a.value !== "");
}

/** Full request URL (with encoded query string) for a set of param values. */
export function requestUrl(
  ep: ApiEndpoint,
  values: Record<string, string>,
): string {
  const base = `${API_URL}${ep.path}`;
  const qs = activeArgs(ep, values)
    .map((a) => `${a.name}=${encodeURIComponent(a.value)}`)
    .join("&");
  return qs ? `${base}?${qs}` : base;
}

export function requestSamples(
  ep: ApiEndpoint,
  values: Record<string, string>,
  apiKey?: string,
): { label: string; code: string }[] {
  const key = apiKey && apiKey.trim() ? apiKey.trim() : "capt_live_...";
  const args = activeArgs(ep, values);
  const base = `${API_URL}${ep.path}`;

  if (isMultipartPost(ep)) {
    const fileArg = args.find((a) => a.name === "file") ?? { name: "file", value: "@video.mp4" };
    const filePath = fileArg.value.replace(/^@/, "") || "video.mp4";
    const otherArgs = args.filter((a) => a.name !== "file");
    const curlExtras = otherArgs.map((a) => ` \\\n  -F "${a.name}=${a.value}"`).join("");
    const pyFiles = `    files={"file": open(${JSON.stringify(filePath)}, "rb")},`;
    const pyData =
      otherArgs.length > 0
        ? `\n    data={\n${otherArgs.map((a) => `        "${a.name}": ${JSON.stringify(a.value)},`).join("\n")}\n    },`
        : "";
    const nodeFormLines = [
      `form.append("file", await fs.openAsBlob(${JSON.stringify(filePath)}));`,
      ...otherArgs.map((a) => `form.append(${JSON.stringify(a.name)}, ${JSON.stringify(a.value)});`),
    ].join("\n");
    const phpFields = [
      `    "file" => new CURLFile(${JSON.stringify(filePath)}),`,
      ...otherArgs.map((a) => `    "${a.name}" => ${JSON.stringify(a.value)},`),
    ].join("\n");
    return [
      {
        label: "cURL",
        code:
          `curl -X POST "${base}" \\\n` +
          `  -H "Authorization: Bearer ${key}" \\\n` +
          `  -F "file=@${filePath}"${curlExtras}\n` +
          `# or: -H "x-api-key: ${key}"`,
      },
      {
        label: "Python",
        code: `import requests

res = requests.post(
    "${base}",
${pyFiles}${pyData}
    headers={"Authorization": "Bearer ${key}"},  # or "x-api-key": "${key}"
)
print(res.json())`,
      },
      {
        label: "Node",
        code: `import fs from "node:fs";

const form = new FormData();
${nodeFormLines}
const res = await fetch("${base}", {
  method: "POST",
  headers: { Authorization: "Bearer ${key}" }, // or { "x-api-key": "${key}" }
  body: form,
});
const data = await res.json();
console.log(data);`,
      },
      {
        label: "PHP",
        code: `<?php
$ch = curl_init("${base}");
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, [
${phpFields}
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ["Authorization: Bearer ${key}"]); // or x-api-key: ${key}
echo curl_exec($ch);
curl_close($ch);`,
      },
      {
        label: "Go",
        code: `package main

import (
	"bytes"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
)

func main() {
	var buf bytes.Buffer
	w := multipart.NewWriter(&buf)
	fw, _ := w.CreateFormFile("file", ${JSON.stringify(filePath)})
	f, _ := os.Open(${JSON.stringify(filePath)})
	io.Copy(fw, f)
	f.Close()
${otherArgs.map((a) => `\tw.WriteField(${JSON.stringify(a.name)}, ${JSON.stringify(a.value)})`).join("\n")}
	w.Close()
	req, _ := http.NewRequest("POST", "${base}", &buf)
	req.Header.Set("Authorization", "Bearer ${key}")
	req.Header.Set("Content-Type", w.FormDataContentType())
	res, _ := http.DefaultClient.Do(req)
	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)
	fmt.Println(string(body))
}`,
      },
      {
        label: "Java",
        code: `// Use java.net.http with a multipart body builder, or OkHttp:
// OkHttpClient client = new OkHttpClient();
// RequestBody fileBody = RequestBody.create(new File(${JSON.stringify(filePath)}), MediaType.parse("application/octet-stream"));
// MultipartBody body = new MultipartBody.Builder().setType(MultipartBody.FORM)
//     .addFormDataPart("file", ${JSON.stringify(filePath)}, fileBody)
${otherArgs.map((a) => `//     .addFormDataPart(${JSON.stringify(a.name)}, ${JSON.stringify(a.value)})`).join("\n")}
//     .build();
// Request request = new Request.Builder().url("${base}")
//     .header("Authorization", "Bearer ${key}")
//     .post(body).build();
// try (Response res = client.newCall(request).execute()) {
//   System.out.println(res.body().string());
// }`,
      },
    ];
  }

  const u = requestUrl(ep, values);
  const pyParams = args.map((a) => `        "${a.name}": ${JSON.stringify(a.value)},`).join("\n");
  const phpParams = args.map((a) => `    "${a.name}" => ${JSON.stringify(a.value)},`).join("\n");
  const method = ep.method === "POST" ? "POST" : "GET";

  return [
    {
      label: "cURL",
      code:
        method === "POST"
          ? `curl -X POST "${u}" \\\n  -H "Authorization: Bearer ${key}"\n# or: -H "x-api-key: ${key}"`
          : `curl "${u}" \\\n  -H "Authorization: Bearer ${key}"\n# or: -H "x-api-key: ${key}"`,
    },
    {
      label: "Python",
      code: `import requests

res = requests.${method === "POST" ? "post" : "get"}(
    "${base}",
    params={
${pyParams}
    },
    headers={"Authorization": "Bearer ${key}"},  # or "x-api-key": "${key}"
)
print(res.json())`,
    },
    {
      label: "Node",
      code: `const res = await fetch(
  "${u}",
  { method: "${method}", headers: { Authorization: "Bearer ${key}" } }, // or { "x-api-key": "${key}" }
);
const data = await res.json();
console.log(data);`,
    },
    {
      label: "PHP",
      code: `<?php
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "${base}?" . http_build_query([
${phpParams}
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
${method === "POST" ? "curl_setopt($ch, CURLOPT_POST, true);\n" : ""}curl_setopt($ch, CURLOPT_HTTPHEADER, ["Authorization: Bearer ${key}"]); // or x-api-key: ${key}
echo curl_exec($ch);
curl_close($ch);`,
    },
    {
      label: "Go",
      code: `package main

import (
	"fmt"
	"io"
	"net/http"
)

func main() {
	req, _ := http.NewRequest("${method}",
		"${u}", nil)
	req.Header.Set("Authorization", "Bearer ${key}") // or Set("x-api-key", "${key}")
	res, _ := http.DefaultClient.Do(req)
	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)
	fmt.Println(string(body))
}`,
    },
    {
      label: "Java",
      code: `import java.net.URI;
import java.net.http.*;

HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("${u}"))
    .header("Authorization", "Bearer ${key}") // or .header("x-api-key", "${key}")
    .${method === "POST" ? "POST(HttpRequest.BodyPublishers.noBody())" : "GET()"}
    .build();
HttpResponse<String> res = client.send(
    request, HttpResponse.BodyHandlers.ofString());
System.out.println(res.body());`,
    },
  ];
}

/** Static example request samples using default example values. */
export function codeSamples(ep: ApiEndpoint): { label: string; code: string }[] {
  return requestSamples(ep, exampleValues(ep));
}

export function faqs(ep: ApiEndpoint): FaqItem[] {
  const platform = PLATFORM_LABEL[ep.platform];
  const list: FaqItem[] = [
    {
      q: `What does the ${ep.name} do?`,
      a:
        ep.platform === "account"
          ? `The ${ep.name} returns ${resourceLabel(ep)} for your Captapi API key via one ${ep.method} request to ${ep.path}. It returns clean JSON and does not charge credits.`
          : `The ${ep.name} lets you ${ACTION[ep.category]} from a public ${platform} ${inputKind(ep)} using one ${ep.method} request to ${ep.path}. It returns clean JSON — no OAuth or infrastructure setup required.`,
    },
    {
      q: `How many credits does the ${ep.name} cost?`,
      a:
        ep.platform === "account" || ep.credits === 0
          ? `Account endpoints are free — they do not consume credits.`
          : ep.slug === "analytics-compare"
            ? `Billing is 1 credit per successfully resolved URL that is not served from cache. Cache hits (cache=true) are free, same as Post Analytics. Failed URLs appear in failed[] and are not billed. There is no bulk discount vs calling /v1/analytics/post once per URL — compare saves HTTP round-trips. A fully failed batch still records a minimal 1-credit charge.`
            : ep.slug === "video-transcript"
              ? `Billing is 1 credit per minute of audio (rounded up, minimum 1). Failed or empty results are never charged.`
              : ep.slug === "video-summarize"
                ? `Billing is 1 credit per minute of audio (rounded up) plus 1 credit for the AI summary. The response includes durationSeconds and creditsCharged so you can verify the line item. No-speech uploads return HTTP 422 and are not charged for the summary step.`
                : ep.creditsPerResult
                  ? `At the default limit this endpoint costs ${ep.credits} credits (${ep.creditsPerResult} per result). Billing scales with how many results you request. ${CACHE_NOTE} Failed or empty results are never charged.`
                  : `Each successful call costs ${ep.credits} credit${ep.credits === 1 ? "" : "s"}. ${
                      ep.slug === "tiktok-transcript" || ep.slug === "instagram-profile-search"
                        ? CACHE_NOTE_DEFAULT_TRUE
                        : CACHE_NOTE
                    } Failed or empty results are never charged.`,
    },
    {
      q: `Do I need a ${platform} API key or OAuth?`,
      a:
        ep.platform === "account"
          ? `You only need your Captapi API key (Authorization: Bearer). No third-party OAuth is required.`
          : `No. A single Captapi key works across every platform Captapi supports — YouTube, TikTok, Instagram, Facebook, Twitter/X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble, Spotify, Kwai, and more. We handle proxies, rate limits, retries, and authentication for you.`,
    },
  ];

  if (ep.slug === "analytics-post" || ep.slug === "analytics-compare") {
    list.push({
      q: `How is engagementRate calculated?`,
      a: `On Post Analytics and Compare, engagementRate is always interactions ÷ views (a ratio). Every metrics object includes engagementRateBasis: "interactions/views". TikTok popular-creators uses a different basis (Creative Center percent or avgLikesPerVideo/followers) — do not compare those numbers to post analytics without reading engagementRateBasis.`,
    });
    list.push({
      q: `What do commentsIsApproximate / interactionsIsApproximate mean?`,
      a: `Some platforms expose compact UI counts (YouTube "2.4M" comments). We still return an integer, but commentsIsApproximate=true means that integer is rounded — interactions and engagementRate inherit the same uncertainty via interactionsIsApproximate. Prefer exact likes when present; do not treat interactions as unit-precise when the flag is true.`,
    });
    list.push({
      q: `Which platforms are supported?`,
      a: `Eleven: YouTube, TikTok, Instagram, Facebook, X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, and Rumble. That is intentionally not the full Captapi catalog — Kwai, Twitch, Spotify, Snapchat, and others are out of scope for this unified metrics shape.`,
    });
  }
  if (ep.slug === "analytics-compare") {
    list.push({
      q: `What happens when some URLs fail?`,
      a: `Each results[] row has status ok or error and a platform field when detected. Failed URLs also appear in failed[] as {url, platform, reason}. Only successfully resolved URLs are billed (1 credit each; cache hits free).`,
    });
    list.push({
      q: `Is each results[] row the same as Post Analytics?`,
      a: `Yes — the same mapper and schema (platform, id, title, url, publishedAt, durationSeconds, thumbnailUrl, author{}, metrics{}), plus status. publishedAt is full ISO with milliseconds on both endpoints.`,
    });
  }
  if (
    ep.category === "transcript" &&
    ep.platform !== "account" &&
    ep.platform !== "utilities" &&
    // Captions-only / ASR / text-as-transcript surfaces must not claim a Whisper fallback.
    ep.slug !== "youtube-transcript" &&
    ep.slug !== "youtube-shorts-transcript" &&
    ep.slug !== "youtube-audio-transcript" &&
    ep.slug !== "rumble-video-transcript" &&
    ep.slug !== "twitter-transcript" &&
    ep.slug !== "linkedin-post-transcript" &&
    ep.slug !== "reddit-post-transcript" &&
    ep.slug !== "facebook-ad-library-ad-transcript"
  ) {
    list.push({
      q: `What if the ${platform} ${inputKind(ep)} has no captions?`,
      a: `When no captions are available, Captapi transcribes the audio with AI (Whisper) automatically, so you still get a usable transcript.`,
    });
  }
  if (ep.slug === "rumble-video-transcript") {
    list.push({
      q: `What if the Rumble video has no captions?`,
      a: `This endpoint only parses Rumble's published .vtt tracks — it does not run speech-to-text. No tracks → 404 no_captions (0 credits). Language mismatch → 404 language_not_available with availableLanguages.`,
    });
  }
  if (ep.category === "summarize") {
    list.push({
      q: `Which AI model powers the summaries?`,
      a: `Summaries are generated with GPT-4o-mini for a strong balance of quality, speed, and cost, built on top of the transcript.`,
    });
  }
  if (ep.slug === "amazon-shop-page") {
    list.push({
      q: `Is this the same as influencer amazon.com/shop/{handle} pages?`,
      a: `No. This endpoint scrapes third-party seller storefronts (/sp?seller= or /s?me=). Influencer Amazon Shops (amazon.com/shop/{handle}) are a different Amazon surface — creator vitrines with socials[], lists[], and curations[] — and return HTTP 400 here. Do not treat seller-storefront and influencer-shop APIs as equivalents in competitive comparisons.`,
    });
    list.push({
      q: `Why do you return ASIN and /dp/{ASIN} instead of shop getProductDetails links?`,
      a: `ASIN is Amazon's catalog identity. Emitting asin plus a canonical https://www.amazon.com/dp/{ASIN} URL lets you join products across sellers, marketplaces, and your own catalog. Affiliate paths like /shop/{handle}/getProductDetails/{ASIN}?showRelatedPost=true bury the ASIN in the path and are not the product page.`,
    });
  }
  if (ep.slug === "spotify-artist") {
    list.push({
      q: `Is this the same as Spotify's free Web API?`,
      a: `No. Spotify's official Web API returns followers, popularity, genres, and top tracks, but not monthlyListeners, topCities, or worldRank. Those three come from the web-player GraphQL path this endpoint uses — along with topTracks playCount, concerts, and relatedArtists as clean JSON.`,
    });
    list.push({
      q: `Why is raw omitted by default?`,
      a: `raw is the full GraphQL payload (~80% of the old response) and every normalized field is already derived from it. Pass raw=true only when you need an upstream key we do not lift. It also duplicates itself internally (e.g. biography vs profile.biography).`,
    });
    list.push({
      q: `Why are albums[] / singles[] shorter than albumsCount / singlesCount?`,
      a: `queryArtistOverview only embeds a short discography sample. albumsHasMore / singlesHasMore are true when the catalog is larger — chain each release uri into /spotify/album. There is no discography cursor on this overview surface.`,
    });
  }
  if (ep.slug === "spotify-track") {
    list.push({
      q: `Does track return playCount like artist topTracks?`,
      a: `Yes. playCount is the same stream-count metric as topTracks[].playCount on /spotify/artist — from Spotify's web GraphQL getTrack, not the official Web API.`,
    });
    list.push({
      q: `How do I join to artist or album?`,
      a: `artists[] is [{id, uri, name, url}] and album is {id, uri, name, url, releaseDate}. Pass artists[0].uri into /spotify/artist and album.uri into /spotify/album.`,
    });
    list.push({
      q: `Why are popularity / isrc / previewUrl often missing?`,
      a: `Pathfinder getTrack frequently omits Spotify Web API popularity (0–100), ISRC, and preview URLs. When present they are returned; playCount is the listen metric on this surface.`,
    });
    list.push({
      q: `Are contentRating and explicit the same field?`,
      a: `No. contentRating is Spotify's Pathfinder label enum (NONE | EXPLICIT | NINETEEN_PLUS | UNKNOWN on tracks). explicit is a convenience boolean that is true only for EXPLICIT — age-gate labels are not collapsed into that bit.`,
    });
  }
  if (ep.slug === "spotify-album") {
    list.push({
      q: `Where is the track list?`,
      a: `tracks[] — each row has id, trackNumber, discNumber, name, uri/url, durationMs, playCount, explicit, and artists[{id,uri,name,url}]. id matches the uri suffix for joins into /spotify/track. totalTracks matches the album; tracksHasMore is true only if a page was truncated.`,
    });
    list.push({
      q: `Is releaseDate the full date or just the year?`,
      a: `releaseDate is the ISO timestamp from Spotify (e.g. 2022-10-21T00:00:00Z) when precision is DAY. releaseYear is kept as a convenience integer.`,
    });
  }
  if (ep.slug === "spotify-search") {
    list.push({
      q: `Why does results[].uri look different from older scrapes?`,
      a: `uri is always a canonical Spotify URI (spotify:track:… / album:… / artist:…). Bare IDs are expanded. Chain them into /spotify/track, /album, or /artist without guessing prefixes.`,
    });
    list.push({
      q: `Is search raw the same as artist/track/album raw?`,
      a: `Not always. The primary path is Pathfinder GraphQL (same family as details). Apify fallthrough uses a flat scraper object (albumName, isExplicit). Envelope source is pathfinder or apify — do not write one raw parser for both. Prefer normalized fields; pass raw=true only when needed.`,
    });
    list.push({
      q: `How fresh are results?`,
      a: `Envelope fetchedAt is when this request completed. It is not copied onto results[] (no per-row scrapedAt). There is no cursor — max 50 results per call.`,
    });
    list.push({
      q: `Why is playCount missing on search results?`,
      a: `Pathfinder search hydrate does not expose stream counts. Absence is not zero — chain results[].uri into /spotify/track or read playCount from /spotify/album tracks[].`,
    });
    list.push({
      q: `Why is playable missing on search results?`,
      a: `decorateContextTracks (Pathfinder search hydrate) omits playability. Absence is not false — chain results[].uri into /spotify/track, which returns playable when Spotify exposes it.`,
    });
    list.push({
      q: `Is billing per result or flat?`,
      a: `Flat 2 credits on the native Pathfinder path. Apify fallthrough scales per result (~1.15×). The limit param does not mean "billed per result" on the primary path.`,
    });
  }
  if (ep.slug === "spotify-podcast") {
    list.push({
      q: `Is publisher the same as the podcast hosts?`,
      a: `No. publisher.name is the show's publisher (e.g. Hubspot). Hosts are a different concept — Captapi does not stuff publisher into artists[] the way a music schema would.`,
    });
    list.push({
      q: `What does rating mean on a podcast?`,
      a: `rating is an object: rating.average is Spotify's show score (about 0–5) and rating.totalRatings is how many people voted. It's the main numeric quality signal for podcast research on this endpoint — not on Spotify's free Web API.`,
    });
    list.push({
      q: `Why is there no limit parameter?`,
      a: `This endpoint returns a single show. For the episode list, use /spotify/podcast-episodes (limit + cursor).`,
    });
  }
  if (ep.slug === "spotify-podcast-episodes") {
    list.push({
      q: `Do you ship visualIdentity / raw color dumps?`,
      a: `No — same rule as /spotify/podcast. visualIdentity, playedState, and per-episode podcastV2 show copies are stripped. Pass raw=true only for a slimmed upstream payload; default responses omit raw entirely.`,
    });
    list.push({
      q: `How do I page past the newest 50 episodes?`,
      a: `Pass cursor=nextCursor from the previous response (integer offset). hasMore is false at the end of the archive. Flat 2 credits per page on native Pathfinder.`,
    });
    list.push({
      q: `Why can totalEpisodes differ from an older /spotify/podcast call?`,
      a: `This endpoint sets totalEpisodes from the same episodesV2 query as the page so the embedded podcast card cannot drift within one response. A separate /spotify/podcast call moments later can still see a new episode published.`,
    });
  }
  if (ep.slug === "soundcloud-track") {
    list.push({
      q: `What do streamable / downloadable mean if streamUrl is missing?`,
      a: `They are SoundCloud permission flags on the track. When the public api-v2 lets us mint a progressive MP3 we return streamUrl (and often hlsUrl) with mediaUrlsExpireAt. downloadUrl is only present when SoundCloud exposes a public download without OAuth — downloadable:true alone does not guarantee a URL.`,
    });
    list.push({
      q: `How do I join to soundcloud/artist?`,
      a: `Use artist.id or artist.handle (permalink slug). artist.name/username-style display names can differ in casing from the URL slug.`,
    });
  }
  if (ep.slug === "soundcloud-artist") {
    list.push({
      q: `What is subscriptionTier vs the old badges / creatorSubscription fields?`,
      a: `subscriptionTier is the single canonical plan: pro-unlimited | pro | mid-tier | free. We no longer ship duplicate badges.proUnlimited + creatorSubscription.product.id + badges.verified — verified stays top-level only.`,
    });
    list.push({
      q: `Why is handle different from username?`,
      a: `handle is the permalink slug in the URL (e.g. flume). username is SoundCloud's display username (e.g. Flume). Prefer handle/id for joins.`,
    });
  }
  if (ep.slug === "github-user") {
    // Replace the generic "Do I need a GitHub API key or OAuth?" answer — public
    // GitHub profiles need neither; sell the real value (one key / envelope).
    const oauthIdx = list.findIndex((f) => /API key or OAuth/i.test(f.q));
    if (oauthIdx >= 0) {
      list[oauthIdx] = {
        q: `Why use Captapi instead of api.github.com?`,
        a: `GitHub's public /users/{username} API is free (60 req/hour unauthenticated, 5,000/hour with a personal access token) and needs no OAuth for public profiles. Captapi's value is one Bearer key across ~32 platforms, shared rate-limit/retry handling, and the same camelCase envelope as other profile endpoints — not removing a GitHub login barrier. For GitHub-only jobs, call api.github.com directly.`,
      };
    }
    list.push({
      q: `How do I tell a user from an organization?`,
      a: `Read type — "User" or "Organization" (GitHub's casing). Examples: getify is a User; vercel is an Organization.`,
    });
    list.push({
      q: `When is email present?`,
      a: `Only when the account made an email public on their GitHub profile. Private emails are never returned; the field is omitted when unset.`,
    });
  }
  if (ep.slug === "facebook-marketplace-location-search") {
    list.push({
      q: `When should I call this instead of marketplace-search?`,
      a: `marketplace-search already accepts a city/place name with no lat/lng required. Use location resolve when the name is ambiguous (Austin TX vs Austin MN) or you need Facebook's cityPageId / coordinates before searching. Otherwise skip it — it is an optional 2-credit geocode/disambiguation step.`,
    });
    list.push({
      q: `What is id on a location row?`,
      a: `Facebook's Marketplace city_page.id — the same value marketplace-search listings expose as cityPageId. Join with location.id === listing.cityPageId. It is not a fabricated "city|city|state" string, and it is not duplicated as cityPageId on the location row.`,
    });
  }
  if (ep.slug === "github-repository") {
    list.push({
      q: `Is watchers the same as stars?`,
      a: `No. watchers is GitHub's subscribers_count (notification watchers). GitHub's REST watchers_count field is a deprecated alias of stargazers and is never returned here.`,
    });
    list.push({
      q: `Why is openIssuesAndPrs not just open issues?`,
      a: `GitHub's open_issues_count includes open pull requests. Use /github/pull-requests when you need PRs alone.`,
    });
  }
  if (ep.slug === "github-trending-repositories") {
    list.push({
      q: `Is this the same as sorting /search/repositories by stars?`,
      a: `No. That returns all-time most-starred repos (public-apis, free-programming-books, …). This endpoint scrapes github.com/trending and ranks by starsGained in the since window. source is always "github.com/trending".`,
    });
    list.push({
      q: `Why is there no cursor?`,
      a: `GitHub's trending HTML page is a single short list (usually ≤25). There is no Search API pagination here and no 1000-result Search cap either.`,
    });
  }
  if (ep.slug === "github-trending-developers") {
    list.push({
      q: `Is this followers:>1000 user search?`,
      a: `No. That returns all-time most-followed accounts. This scrapes github.com/trending/developers for a since window and hydrates followers/bio from /users/{login}. There is no Search relevance score field.`,
    });
  }
  if (ep.slug === "github-contributions") {
    list.push({
      q: `Is recentPublicEvents still returned?`,
      a: `No. That field was a count of /users/{u}/events/public rows (hard-capped at 90) and was not a contribution metric. This endpoint returns the heatmap: totalContributions, currentStreak, longestStreak, and days[] sorted by date.`,
    });
    list.push({
      q: `Where does the calendar come from?`,
      a: `The public HTML at github.com/users/{login}/contributions (same graph as the profile). source echoes that path.`,
    });
    list.push({
      q: `Does a zero today break currentStreak?`,
      a: `No — today-grace: if the last day is today and count is 0, it is skipped because the day is not over. A zero on any earlier day breaks the streak. days[] is sorted ascending so days.slice(-30) is the last 30 calendar days.`,
    });
  }
  if (ep.slug === "github-pull-requests") {
    list.push({
      q: `Why does the docs example use state=closed if the default is open?`,
      a: `API default is open. The docs cURL passes state=closed so mergedAt/closedAt show in the example response — data.state always echoes whichever filter ran.`,
    });
    list.push({
      q: `Why include draft?`,
      a: `Draft PRs are not ready for review. Counting them as shipped PRs skews throughput metrics — filter draft=false.`,
    });
  }
  if (ep.slug === "github-activity") {
    list.push({
      q: `Why is there an eventCeiling of 90?`,
      a: `GitHub's /users/{u}/events/public returns at most 90 events (and only ~90 days). We echo eventCeiling and stop hasMore there — deep pagination past that is not available.`,
    });
    list.push({
      q: `Where is the commit message / branch?`,
      a: `On PushEvent rows, payload.ref is the branch and payload.commits[] has sha + message. Other types expose payload.action and the related entity fields.`,
    });
  }
  if (ep.slug === "github-followers" || ep.slug === "github-following") {
    list.push({
      q: `Why is paging a large account expensive?`,
      a: `There is no sampling/since parameter — every page costs ~0.1 credits/row. ~250k followers ≈ 25k credits. For full archives call api.github.com (free, rate-limited) directly.`,
    });
    list.push({
      q: `What is id / type for?`,
      a: `id is GitHub's numeric account id (stable for joins/dedup). type is User or Organization — both come from the upstream followers/following payload.`,
    });
  }
  if (ep.slug === "github-repositories") {
    list.push({
      q: `Can I sort by stars?`,
      a: `No — GitHub's /users/{u}/repos only supports sort=created|updated|pushed|full_name. Use sort=pushed for recently active repos. For star ranking, call api.github.com search (user:LOGIN sort:stars) or github/repository per repo.`,
    });
    list.push({
      q: `Why is parent missing on forks?`,
      a: `GitHub's list payload omits parent. isFork is still true. Call github/repository on the fork for parent (upstream fullName).`,
    });
  }
  if (ep.slug === "tiktok-search-users") {
    list.push({
      q: `Why do I need secUid if I already have the @handle?`,
      a: `Handles change; id and secUid do not. TikTok's follower lists, video lists, and many internal calls require secUid. Prefer id/secUid for CRM joins and chaining — use username for display.`,
    });
  }
  if (ep.slug === "tiktok-channel-details") {
    list.push({
      q: `Does channel-details return id and secUid?`,
      a: `Yes. Resolving @handle → id + secUid is the main job of this endpoint. Prefer those for CRM joins and for chaining into user-followers, channel-posts, and other secUid-gated TikTok calls. Handles change; id/secUid do not.`,
    });
    list.push({
      q: `What does ttSeller mean?`,
      a: `ttSeller (alias isSeller) is TikTok's Shop seller flag on the profile. When true, chain into TikTok Shop endpoints (shop search / product details / user showcase) for that creator's commerce surface.`,
    });
  }
  if (ep.slug === "tiktok-live" || ep.slug === "tiktok-live-info") {
    list.push({
      q: `Is /live-info richer than /live?`,
      a: `No — they share one runner and return the same JSON (creator.id/secUid, room.streamQualities with flv/hls/cmaf/dash when TikTok exposes them). /live-info is only a billing/cache alias at 7 credits for ScrapeCreators path compatibility. Prefer /live (1 credit).`,
    });
    list.push({
      q: `Why is isLive false when room has stream URLs?`,
      a: `isLive is true only when status === 2. Ended rooms often keep title, totalEnterCount, and pull URLs — that is last-broadcast history, not a live session. viewerCount is omitted when offline so a stale concurrent count is not mistaken for live viewers.`,
    });
  }
  if (
    ep.slug === "youtube-transcript" ||
    ep.slug === "youtube-summarizer" ||
    ep.slug === "youtube-shorts-transcript" ||
    ep.slug === "youtube-shorts-summarizer"
  ) {
    list.push({
      q: `Why did I get 404 on a video with clear speech?`,
      a: `This endpoint returns captions YouTube published — it does not run speech-to-text. Read detail.code: no_captions means tracks=0 (common on long live streams); language_not_available means tracks exist but not in your language (see availableLanguages). On no_captions, detail.suggestion points at /v1/youtube/audio-transcript with estimatedCredits. 404 never charges credits.`,
    });
    list.push({
      q: `If I pass language=en and only Turkish captions exist, what happens?`,
      a: `We try YouTube's timedtext translation into en. If that fails → 404 language_not_available with availableLanguages (not a silent Turkish transcript). On success, requestedLanguage and returnedLanguage are both set; isTranslated is true when YouTube translated.`,
    });
  }
  if (ep.slug === "youtube-audio-transcript") {
    list.push({
      q: `How are credits calculated?`,
      a: `creditsUsed = ceil(durationSeconds / 60) × 2. Pass maxCredits to refuse before STT when the estimate would exceed your budget (400 cost_exceeds_max, 0 credits). Cache hits still bill — the cache is our margin.`,
    });
    list.push({
      q: `How is this different from /youtube/transcript?`,
      a: `/transcript returns YouTube's published captions (source:captions, flat 1 credit). /audio-transcript runs speech-to-text on the audio (source:asr, per-minute). Both use the same body shape: text + segments[{text,startMs,endMs}]. Fall back using the source discriminator — no key rename needed.`,
    });
    list.push({
      q: `What is the sync length limit?`,
      a: `90 minutes when Groq is configured (measured: ~82 min Huberman ≈ 49s e2e under Cloudflare's ~110s deadline). Longer videos return 400 duration_too_long with estimatedCredits and cost 0 — multi-hour livestreams need a future chunked path.`,
    });
  }
  if (ep.slug === "tiktok-user-followers" || ep.slug === "tiktok-user-followings") {
    list.push({
      q: `Do follower rows include secUid?`,
      a: `Yes — same identity fields as search-users (id + secUid) on every row when TikTok exposes them, plus createTime/createTimeUnix, region, and language for audience-quality signals. total is the profile's followerCount/followingCount; page with nextCursor + hasMore.`,
    });
    list.push({
      q: `Why is this 1 credit when older docs said ~20?`,
      a: `Native signer path (/api/user/list/) is flat 1 credit — ScrapeCreators parity. The old ~20 figure was Apify billed at ~0.4 credits per returned user (min 5). Apify fallback still uses that per-result rate when the native path is unavailable.`,
    });
  }
  if (ep.slug === "tiktok-audience-demographics") {
    list.push({
      q: `Is this follower geography?`,
      a: `No. TikTok does not publish follower country. We sample people commenting on recent videos (basis=commenters) and report sampleSize, videosSampled, and confidence. Percentages are numeric. Use videos=12|30|60 for deeper samples (3/5/8 credits). Do not treat this as a full follower census.`,
    });
  }
  if (ep.slug === "tiktok-popular-creators") {
    list.push({
      q: `Can I vet creators for bots / fake growth?`,
      a: `Yes. Each creator is profile-hydrated with createTime / createTimeUnix (account age), bioLinkRisk (TikTok's link risk score), and ttSeller. A high-follower account with a very recent createTime is the classic red flag. contact{emails,links} is filled when the bio exposes outreach channels.`,
    });
  }
  if (ep.slug === "instagram-tagged-posts") {
    list.push({
      q: `Why do some brands return only old tagged posts?`,
      a: `Instagram's usertags feed only returns tags the account still exposes. Mega brands that stopped approving tags (e.g. natgeo) can surface a truncated historical window — all from one day years ago — while accounts like nasa or cristiano return recent UGC. Captapi does not invent newer tags. Check staleFeed / newestPublishedAt on every response: when staleFeed is true, do not use the page for live brand or collaboration monitoring.`,
    });
  }
  if (ep.slug === "threads-profile") {
    list.push({
      q: `What does isThreadsOnlyUser mean?`,
      a: `When Meta exposes it, true means the account exists only on Threads (not an Instagram-linked auto-profile). On the public web hydrate this flag is often omitted — Captapi still returns the key as null so clients can rely on a stable schema.`,
    });
  }
  if (ep.slug === "threads-user-posts") {
    list.push({
      q: `Why is this 2 credits when older docs said ~14?`,
      a: `Native profile-hydrate path is flat 2 credits — same soft-cap surface ScrapeCreators uses, and parity with Twitter user-tweets. The old ~14 figure was Apify billed at ~0.7 credits per returned post (default limit 20). Apify fallback still uses that per-result rate when the native path is unavailable.`,
    });
    list.push({
      q: `I set limit=100 but only got ~25 posts. Is the endpoint broken?`,
      a: `No — Meta only exposes the last ~20–30 public posts on profile hydrate. limit is a client-side cap, not a promise that Threads has that many posts. See Platform limits on this page.`,
    });
    list.push({
      q: `How do I rebuild a multi-part Thread?`,
      a: `Group posts by threadId. Within a thread, replyToId points at the previous post's id (root has replyToId null / isReply false). isQuote + quoteId mark quote posts.`,
    });
  }
  if (ep.slug === "threads-post-details") {
    list.push({
      q: `Is this just user-posts for one URL?`,
      a: `No. post-details always returns comments[] and relatedPosts[] on top of the shared post card. relatedPosts comes from Meta's BarcelonaLoggedOutRelatedPosts module (other creators, no second request). comments is filled only when the permalink hydrate embeds same-thread replies — viral posts often return [] with the key still present.`,
    });
    list.push({
      q: `Why is comments[] empty when the post has thousands of replies?`,
      a: `Logged-out Threads permalink HTML usually ships the main post + related posts, not the public reply tree. Captapi keeps comments: [] rather than omitting the key or inventing a separate comments endpoint that cannot be filled on this path. ScrapeCreators often populates comments via a deeper GraphQL session we do not use here.`,
    });
    list.push({
      q: `Where are view counts?`,
      a: `engagement.views is always keyed. Meta often omits per-post view_counts on logged-out web hydrate (even when the app shows views), so the value is frequently null — same honesty as user-posts.`,
    });
  }
  if (ep.slug === "threads-search") {
    list.push({
      q: `Why is this 2 credits when older docs said ~18?`,
      a: `Flat 2 credits — same soft-cap surface as twitter/search and threads/user-posts. The old ~18 figure was a per-result extended-path rate at default limit 25; success is always billed at the published flat price now.`,
    });
    list.push({
      q: `Can I sort by newest or filter by date?`,
      a: `Not on this endpoint. Meta only exposes the default Top ranking on the logged-out search hydrate — months-old posts can sit next to recent ones. Client-side filter on publishedAt if you need a recency window.`,
    });
    list.push({
      q: `Why do giveaway / engagement-farm posts rank first?`,
      a: `Meta's Top SERP often boosts high-reply bait. Captapi returns what the hydrate embeds and does not apply a spam filter. replies ≫ likes is a common client-side signal to down-rank.`,
    });
  }
  if (ep.slug === "threads-search-users") {
    list.push({
      q: `Why is this 1 credit when older docs said ~14?`,
      a: `Flat 1 credit — parity with TikTok search-users and ScrapeCreators Threads search/users. The old ~14 figure was a per-result extended-path rate at default limit 20; success is always billed at the published flat price now.`,
    });
    list.push({
      q: `Why don't the usernames match my query?`,
      a: `This is not a semantic people-search. Users are distinct authors of posts that matched the keyword on Meta's Top SERP — the handle or bio may not contain the query. For follower counts and bio, call Threads Profile with the returned url.`,
    });
    list.push({
      q: `Why is followers null?`,
      a: `Search post authors rarely embed follower_count. The key stays present as null for a stable parser — use /v1/threads/profile for counts.`,
    });
  }
  if (ep.slug === "reddit-subreddit-details") {
    list.push({
      q: `Is the subreddit name case-sensitive?`,
      a: `No. AskReddit and askreddit both resolve — Reddit is case-insensitive. The response name field uses Reddit's canonical casing.`,
    });
    list.push({
      q: `Is activeUsers weekly active users?`,
      a: `No. It is Reddit's active_user_count — accounts currently online. That is the public metric Reddit exposes on about.json. Treat third-party “weekly active” fields skeptically when the ratio to members looks unrealistic.`,
    });
    list.push({
      q: `Where do rules come from?`,
      a: `From Reddit's /r/{name}/about/rules endpoint as a structured array (name, description, kind, …). The short public_description stays in description; submitText is the compose-box guidelines when set.`,
    });
  }
  if (ep.slug === "reddit-search" || ep.slug === "reddit-subreddit-search") {
    list.push({
      q: `Why can score be 0 when upvoteRatio is 0.36?`,
      a: `score is Reddit's own score field — Captapi does not compute ups−downs (public JSON almost always sends downs: 0). New posts often have hide_score: score/upvotes stay 0 while upvoteRatio is still filled. Check scoreHidden; do not treat a zero score as worthless until the hide window ends.`,
    });
    list.push({
      q: `Can I search comments, not just posts?`,
      a: `Not on this endpoint — results are posts only (kind=t3). For discussion text under a known post, use Post Comments. Site-wide comment search (ScrapeCreators-style comments[]) is a separate surface on the backlog.`,
    });
  }
  if (ep.slug === "pinterest-board") {
    list.push({
      q: `Why did my request fail with a pin URL?`,
      a: `This endpoint requires a board URL (.../username/board-name/). Pin URLs go to /v1/pinterest/pin-details. The docs cURL uses a board URL — do not paste a /pin/… link here.`,
    });
    list.push({
      q: `Where is the save/repin count?`,
      a: `On each pin as saves (from Pinterest aggregated_pin_data). That is the primary engagement metric on Pinterest — not likes.`,
    });
    list.push({
      q: `How do I get the full-resolution image?`,
      a: `Use imageOriginal or images.originals.url. Top-level image is a display CDN size (often 564x).`,
    });
  }
  if (ep.slug === "tiktok-ad-library-search") {
    list.push({
      q: `Is this TikTok Creative Center (CTR / Top Ads)?`,
      a: `No. This endpoint searches TikTok's Commercial Content Library (library.tiktok.com — EU DSA transparency). For Creative Center Top Ads with CTR, likes, industry/objective, and orderBy, use GET /v1/ad-library/tiktok/top-ads.`,
    });
    list.push({
      q: `Why is this only 2 credits when older docs said ~70?`,
      a: `Native Decodo search is flat 2 credits when ads are returned (empty is free). The old ~70 figure was Apify billed at ~3.5 credits per result (limit 20). Apify fallback is now capped at 5 credits total.`,
    });
    list.push({
      q: `Why did my keyword return zero ads?`,
      a: `Read candidatesScanned, filteredOut, literalMatches. match=any (default) keeps rows with any whole-word token in advertiser/title/copy; match=all requires every token. TikTok's keyword ranking is soft — we never echo that unfiltered list. If candidatesScanned>0 and totalReturned=0, the library had rows and local filter dropped them (try an advertiser name token). US is often empty; default GB.`,
    });
  }
  if (ep.slug === "facebook-ad-library-search") {
    list.push({
      q: `How do I find current campaigns instead of 2020 ads?`,
      a: `Use status=ACTIVE (default) plus start_date (YYYY-MM-DD). For spend/impressions in most markets set ad_type=political_and_issue_ads — commercial ads usually return null spend. Page with nextCursor within the current HTML batch; refine the query when nextCursor is null.`,
    });
  }
  if (ep.slug === "google-ad-library-advertiser-search") {
    list.push({
      q: `How do I get Nike, Inc. creatives (not NIKE SRL)?`,
      a: `Call advertiser-search?q=nike&country=US — results are expanded and ranked so Nike, Inc. leads, with regional entities (SRL, BV) listed after. Pass advertisers[0].id into /google/company-ads?advertiser=AR…. Using a bare name/domain on company-ads also resolves, but AR… is deterministic.`,
    });
  }
  if (ep.slug === "google-ad-library-company-ads") {
    list.push({
      q: `Why are text/spend null on Google creatives?`,
      a: `Keys stay present as null for a stable parser. Google Ads Transparency rarely exposes copy or spend on commercial image creatives (spend/impressions are mostly political). landingUrl is filled when ATC embeds a destination. Use sort=last_shown and start_date/end_date for recent activity; page with nextCursor.`,
    });
  }
  if (ep.slug === "tiktok-ad-library-top-ads") {
    list.push({
      q: `How is this different from TikTok Ad Library Search?`,
      a: `Top Ads is Creative Center performance inspiration (CTR tiers, likes, industry/objective, Spark Ads, video renditions). Ad Library Search is the EU Commercial Content Library (first/last shown, reach bands). Different TikTok products — pick Top Ads for creative intel, Search for DSA transparency.`,
    });
    list.push({
      q: `How many credits does Top Ads cost?`,
      a: `Flat 2 credits on Decodo-native when ads are returned. Apify fallback bills ~1 credit per returned ad (min 2) — about 20 credits at the default limit of 20. Empty results and upstream timeouts are never charged. cache=true hits are free.`,
    });
    list.push({
      q: `Why is this endpoint so slow — and what timeout should I set?`,
      a: `Creative Center HTML is an empty shell — ads arrive only via a signed list XHR. We open the page in a browser, intercept that response, and exit when the JSON arrives (typically 30–60 seconds — not networkidle). Set your HTTP client timeout to at least 120 seconds. nginx/ALB default to 60s and Heroku caps at 30s — those cut the connection on your side. On timeout we return 503 upstream_timeout (not billed). If totalReturned < limit and truncated is true, Creative Center still had pages we did not fetch.`,
    });
    list.push({
      q: `Why did my keyword return zero ads?`,
      a: `Read candidatesScanned, filteredOut, literalMatches, and matchBasis. match=any (default) keeps rows with any whole-word token; match=all requires every token. Creative Center's keyword ranking is soft and often unrelated — we never echo that unfiltered list. If candidatesScanned>0 and totalReturned=0, the leaderboard had rows and local filter dropped them (empty is free; truncated is false). Try a brand name or a token that appears in title/industry.`,
    });
    list.push({
      q: `What does ctr mean, and where are ad dates?`,
      a: `ctr is TikTok's normalized 0–1 Creative Center score (not a raw click-through percent). ctrTier/isSparkAd appear only when Creative Center ships them. The list surface does not expose ad run dates — firstSeen/lastSeen are not returned. The period param is only the lookback window for the ranking. For DSA firstShown/lastShown use /tiktok/ad-details (search omits them).`,
    });
    list.push({
      q: `How do I group ads by advertiser?`,
      a: `Use advertiser.id when present, else advertiser.name (same value as brandName). Spark Ads that ship "Not Mention" fall back to the organic creator nickname and author id. Creative Center often omits a stable business id — null advertiser.id is expected on some rows.`,
    });
    list.push({
      q: `Why did Top Ads return 502 with industry set?`,
      a: `The Apify fallback only accepts its fixed industry enum (All Industries, Gaming, E-commerce & Shopping, Beauty & Personal Care, …). We now map TikTok keys/aliases (label_25000000000, Games→Gaming) before the actor call; unsupported values return HTTP 400 with the allowed list — not upstream_actor_error 502. Omit industry or use Gaming / All Industries to unblock.`,
    });
  }
  if (ep.slug === "linkme-profile") {
    list.push({
      q: `Why did Linkme used to return Privacy Policy and Terms as links?`,
      a: `An older HTML scrape read the SSR shell meta tags and site footer. We now parse Linkme's dehydrated TanStack $tsr profile (same payload SC uses): bio, profileVisitCount, featured links[], webLinks[], infoLinks/email, stripeStatus, and isDefaultProfilePicture. Footer chrome is never returned. Flat 1 credit.`,
    });
  }
  list.push({
    q: `Is the ${ep.name} suitable for production use?`,
    a:
      ep.platform === "account"
        ? `Yes. It is a stable REST endpoint with predictable JSON. Account endpoints are always live (never cached) and do not charge credits.`
        : ep.platform === "utilities" && ep.method === "POST"
          ? `Yes. It is a stable REST endpoint with predictable JSON. Upload via multipart form field file (POST) — see the cURL sample. Use durationSeconds / creditsCharged to verify per-minute billing.`
          : `Yes. It is a stable REST endpoint with predictable JSON and automatic retries. ${CACHE_NOTE} Use it for analytics, monitoring, and content automation.`,
  });

  return list;
}

/**
 * Platform-level FAQs for the /apis/[platform]-api landing pages.
 * Answer-first copy so SEO snippets and AI answer engines (GEO/AEO) can quote
 * a complete, self-contained answer for each question.
 */
export function platformFaqs(group: PlatformGroup): FaqItem[] {
  const name = group.name;
  const count = group.endpoints.length;
  const creditValues = group.endpoints.map((e) => e.credits);
  const minCredits = Math.min(...creditValues);
  const maxCredits = Math.max(...creditValues);
  const capabilities = Array.from(
    new Set(group.endpoints.map((e) => e.shortName)),
  );
  const capabilityList =
    capabilities.slice(0, 6).join(", ") +
    (capabilities.length > 6 ? ", and more" : "");

  return [
    {
      q: `What is the ${name} API?`,
      a: `The ${name} API is a REST API from Captapi that returns public ${name} data as clean, structured JSON. It covers ${count} endpoint${count === 1 ? "" : "s"} — ${capabilityList} — behind one Bearer API key, with no OAuth flow and no infrastructure to build or maintain.`,
    },
    {
      q: `What data can I get from the ${name} API?`,
      a: `${group.blurb} Each endpoint is a single GET request that responds with predictable JSON fields, so the data is ready for dashboards, AI pipelines, and automations.`,
    },
    {
      q: `Do I need a ${name} developer account or OAuth?`,
      a: `No. You only need a Captapi key (capt_live_...), sent as an Authorization: Bearer header. The same key works across all ${PLATFORM_COUNT} platforms Captapi supports. We handle proxies, rate limits, retries, and parsing for you.`,
    },
    {
      q: `How much does the ${name} API cost?`,
      a: `${name} endpoints cost between ${minCredits} and ${maxCredits} credits per call, depending on the endpoint${maxCredits !== minCredits ? " and how many results you request" : ""}. New accounts start with 100 free credits (no credit card). ${CACHE_NOTE}`,
    },
    {
      q: `Can AI agents use the ${name} API?`,
      a: `Yes. Every ${name} endpoint is exposed as a tool in the official MCP server (@captapi/mcp) for Claude, Cursor, and VS Code, and is also available through the @captapi/cli CLI, an n8n community node, a Make.com app, and an Apify Actor.`,
    },
    {
      q: `Is the ${name} API suitable for production use?`,
      a: `Yes. It is a stable REST API with predictable JSON, automatic retries, and upstream fallbacks. ${CACHE_NOTE} Only successful responses consume credits — failed or empty results are never charged.`,
    },
  ];
}

// ---------------------------------------------------------------------------
// Response structure
// ---------------------------------------------------------------------------
// Derived from the real captured example for each endpoint so the documented
// fields always match what the API actually returns. The per-category switch
// below is only a fallback for endpoints without a snapshot.

/** Human descriptions for well-known response fields. */
const FIELD_DESCS: Record<string, string> = {
  // Identity / linking
  platform: "Platform identifier for this response (matches the endpoint's platform).",
  id: "Stable platform ID for the item.",
  url: "Canonical URL of the item.",
  uri: "Platform URI for the item.",
  slug: "URL slug of the item.",
  shortcode: "Instagram shortcode of the post (posts/reels only).",
  permalink: "Canonical Instagram permalink for the embed.",
  html: "Instagram's self-contained embed HTML document (drop into an <iframe srcdoc>).",
  query: "The search query you sent.",
  totalReturned: "Number of items returned in this response.",
  nextCursor:
    "Cursor to pass for the next page of results. May be null when the platform does not expose deep pagination (e.g. some Facebook Ad Library searches).",
  hasMore: "Whether more results are available beyond this page. When true, pass nextCursor to fetch the next page.",
  raw: "Raw upstream payload for advanced use (fields may change). Prefer the normalized top-level fields when available.",

  // People / profiles
  username: "Account username / handle.",
  handle: "Account handle.",
  login: "Account login name.",
  // Instagram basic profile (camelCase, aligned with Channel Details)
  pk: "Instagram user primary key (same as id).",
  biographyWithEntities: "Bio text plus parsed @mentions / #hashtags ({rawText, entities}).",
  highlightReelCount: "Number of Story Highlight albums on the profile.",
  totalClipsCount: "Total Reels/clips count when Instagram exposes it.",
  hasClips: "Whether the account has Reels/clips.",
  isPrivate: "Whether the account is private.",
  locked: "Whether the account is locked / follow-gated (Mastodon locked).",
  bot: "Whether the account is marked as a bot.",
  group: "Whether the account is a group account.",
  acct: "Federation handle (may differ from username for remote accounts).",
  lastStatusAt: "When the account last posted (ISO-8601 UTC).",
  emojis: "Custom emoji shortcodes used in the display name ({shortcode, url, staticUrl}).",
  fields: "Profile metadata rows ({name, value, verifiedAt}) — verified links land here.",
  isBusinessAccount: "Whether the account is a business account.",
  isProfessionalAccount: "Whether the account is a professional (creator/business) account.",
  isMemorialized: "Whether the account is memorialized.",
  accountType: "Instagram account type code when present.",
  categoryName: "Public category label (e.g. SPORTSWEAR_STORE).",
  shouldShowCategory: "Whether Instagram shows the account's category publicly.",
  profileImageHd: "HD profile picture URL.",
  profileImageUrl: "Standard-resolution profile picture URL.",
  externalUrl: "Website / link-in-bio URL when present.",
  fbid: "Linked Facebook/Meta ID for the account.",
  pronouns: "Pronouns listed on the profile.",
  bioLinks:
    "External links from the profile bio ({title, url, linkType} on Instagram; {url, verified, linkId} on Threads).",
  accountBadges: "Instagram account badges when present.",
  transparencyLabel:
    "Account transparency label when Meta exposes it (e.g. state-affiliated media).",
  showAccountTransparencyDetails: "Whether Instagram shows account transparency details.",
  isEmbedsDisabled: "Whether embedding this account's content is disabled.",
  isRegulatedC18: "Whether the account is age-restricted (18+).",
  showTextPostAppBadge: "Whether the Threads badge is shown on the profile.",
  removeMessageEntrypoint: "Whether the message button is hidden on the profile.",
  businessAddress: "Business address ({cityName, streetAddress, zipCode, latitude, longitude}).",
  linkedFbInfo: "Linked Facebook page info when present.",
  latestReelMedia: "Latest reel media timestamp/id when Instagram exposes it.",
  displayName:
    "Display name of the account. Canonical across profile endpoints (prefer over name).",
  name:
    "Name of the item or account. On profile endpoints: deprecated alias of displayName (one release).",
  fullName: "Full display name.",
  firstName: "First name.",
  lastName: "Last name.",
  author: "Author name or handle.",
  bio: "Profile bio. Canonical across profile endpoints (prefer over description on YouTube).",
  headline: "Profile headline.",
  verified: "Whether the account is verified on this platform.",
  isVerified: "Whether the account is verified.",
  private: "Whether the account is private.",
  followers: "Follower count.",
  following: "Number of accounts followed.",
  followings: "Number of accounts followed.",
  subscriberCount: "Subscriber count (channel, subreddit, or similar).",
  connections: "Number of connections.",
  members: "Member count.",
  postCount:
    "Total posts/statuses/videos for the account. Canonical across profile endpoints (prefer over posts / videoCount / tweetCount).",
  publicPostCount: "Public posts on the Kwai profile.",
  privatePostCount: "Private posts on the Kwai profile.",
  likedCount: "Total likes received across the profile.",
  verifiedDescription: "Kwai verification label (e.g. Conta Oficial).",
  verifiedNumber: "Kwai verification tier number when present.",
  eid: "Kwai opaque profile eid.",
  creator:
    "Creator handle or account for this item (platform-specific — e.g. who founded a community, or who cut a clip).",
  isMature: "Whether Kick marks the clip as mature content.",
  privacy: "Clip privacy (e.g. public).",
  startedAt: "When the stream, clip, or broadcast segment started (ISO 8601).",
  livestreamId: "Kick livestream id the clip was taken from.",
  vodStartsAt: "Offset into the VOD (seconds) where the clip starts.",
  categorySlug: "Kick category slug (e.g. just-chatting).",
  parentCategory: "Kick parent category (e.g. irl).",
  categoryBanner: "Category banner image URL when Kick exposes one.",
  categoryId: "Category id when the platform exposes one.",
  badges:
    "Platform badges on the result (SoundCloud pro/verified; YouTube 4K/LIVE/New; etc.).",
  creatorSubscription: "SoundCloud creator subscription ({product:{id}}, e.g. creator-pro-unlimited).",
  lastModified: "When the SoundCloud profile was last modified (ISO 8601).",
  creatorMidTier: "Whether the account has SoundCloud creator mid-tier.",
  proUnlimited: "Whether the account has SoundCloud Pro Unlimited.",
  pro: "Whether the account has SoundCloud Pro.",
  curator: "Who created/cut the Twitch clip (distinct from the broadcaster channel).",
  channel: "Channel name or channel object — shape depends on the endpoint (see that page's field notes).",
  videoQualities: "Available clip MP4 qualities ({quality, frameRate, url}).",
  playbackAccessToken: "Twitch playback token ({signature, value, expires, expiresAt}).",
  videoOffsetSeconds: "Seconds into the source VOD where the clip starts.",
  isFeatured: "Whether Twitch marks the clip as featured on the channel.",
  isPublished: "Whether the clip is published.",
  gameId: "Twitch game/category id.",
  gameSlug: "Twitch game/category slug.",
  gameBoxArtUrl: "Twitch category/game box art image URL (usually 144×192).",
  isPartner: "Whether the channel is a platform Partner/partner.",
  lastBroadcast: "Most recent broadcast metadata ({startedAt, title}).",
  playCount: "Play/stream count for the item.",
  trackNumber: "Track position on the album.",
  contentRating:
    "Spotify Pathfinder contentRating.label — tracks: NONE | EXPLICIT | NINETEEN_PLUS | UNKNOWN; podcasts may also use NOT_FOR_CHILDREN | SPOTIFY_EIGHTEEN_PLUS. Not a twin of explicit.",
  explicit:
    "Convenience boolean: true only when contentRating is EXPLICIT (or EXPLICIT is among contentRatingLabels).",
  artistItems:
    "Legacy alias — prefer artists[{id, uri, name, url}] on /spotify/track.",
  albumInfo:
    "Legacy alias — prefer album{id, uri, name, url, releaseDate} on /spotify/track.",
  previewUrl: "30s MP3 preview URL when Spotify exposes one.",
  albumsHasMore:
    "True when albumsCount exceeds the overview sample in albums[] — chain release URIs into /spotify/album.",
  singlesHasMore:
    "True when singlesCount exceeds the overview sample in singles[] — chain release URIs into /spotify/album.",
  mediaType: "Media type label for this item (platform-specific enum).",
  playable: "Whether the track is playable in the web player.",
  scrapedAt:
    "When this response was collected (ISO 8601). Envelope-level freshness on listings that expose it (e.g. Facebook profile-posts) — not a per-row stamp on Spotify search.",
  videoCount:
    "Population video count when the source is authoritative (e.g. TikTok challenge/detail statsV2 on popular-hashtags, or a channel's uploaded-video total). Never a sample tally — sample sizes use sampleVideoCount / sampleSize.",
  sampleVideoCount:
    "How many videos in this response's sample included the hashtag (co-occurrence count). Not the hashtag's TikTok-wide total — see videoCount.",
  samplePlays:
    "Sum of play/view counts across sample videos that included the hashtag. Not the hashtag's TikTok-wide totalPlays.",
  totalPlays:
    "Population total plays/views for a hashtag when from challenge/detail (statsV2). On popular-hashtags this is not the sample sum — see samplePlays.",
  hashtagId: "TikTok challenge / hashtag id (cid) when available.",
  growthRate:
    "Hashtag/song growth signal. On Creative Center charts: derived from trend[] when present. On challenge/detail co-occurrence path: null.",
  discovery:
    'How hashtags were found. popular-hashtags: "creative_center" (official chart) or "co_occurrence" (related tags from seed videos).',
  discoverySource:
    "Where the seed video sample came from (hashtag_page, top_search, or apify_hashtag_videos) — co-occurrence path only.",
  rankBy: "Metric used for rank (creative_center_rank on Creative Center; videoCount on co-occurrence enrich).",
  rankDiff: "Rank change vs the previous Creative Center period (positive = moved up).",
  trend: "Time series of relative popularity {time, value} from Creative Center.",
  viewCountText: "Compact view label as YouTube shows it (e.g. 750K).",
  viewCountInt: "Parsed integer from viewCountText (750000). Prefer with viewCountText when counts may be rounded.",
  tweetCount: "Total number of tweets.",
  mediaCount: "Total number of media posts.",
  location: "Location shown on the profile or item.",
  website: "Website listed on the profile.",
  email: "Public email when the account exposes one. Null when private, omitted, or CAPTCHA-gated.",
  joinedDate: "When the account was created.",

  // Content
  title: "Title of the item.",
  text: "Text content.",
  description: "Description text.",
  caption: "Post or creative caption when the platform exposes one.",
  publishedAt: "Publish date (ISO 8601) when the platform exposes an absolute timestamp.",
  publishedTimeText: "Original relative publish label from the platform when an exact timestamp was not available (e.g. \"1 year ago\").",
  publishedTimeApprox:
    "Approximate ISO-8601 derived from publishedTimeText, truncated to the label's precision (day/hour/minute). Not an observed instant — see publishedTimeIsApproximate.",
  publishedTimeIsApproximate:
    "true when publishedTimeApprox was derived from a relative label rather than an absolute timestamp YouTube exposed.",
  totalVideos: "Total videos in the playlist (full size). Differs from totalReturned, which is this response's page length.",
  viewCountApproximate:
    "Deprecated alias — use viewCountIsApproximate. True when viewCount came from a compact UI label (e.g. 2.5B).",
  viewCountIsApproximate:
    "True when viewCount was parsed from a compact UI label (e.g. 2.5B / 894M) rather than an exact integer.",
  followersApproximate:
    "Deprecated alias — use followersIsApproximate. True when followers came from a compact Facebook chrome label (e.g. 28M).",
  followersIsApproximate:
    "True when followers was parsed from a compact Facebook chrome label (e.g. 28M) rather than an exact integer.",
  talkingAbout:
    "Facebook 'people talking about this' count for the page when exposed (distinct from likes/followers).",
  createdAt: "Creation date (ISO 8601).",
  updatedAt: "Last update date (ISO 8601).",
  timestamp: "Human-readable timestamp (MM:SS format).",
  type: "Content type of the item.",
  postType:
    'Content type. YouTube community: "text" | "image" | "poll" | "video" | "playlist" | "quiz". Instagram: "Image" | "Video" | "Sidecar" (carousel).',
  category: "Generic category label for the item or community.",
  overlapsWith:
    "UUIDs of other segments whose time range overlaps this one (SponsorBlock nested/duplicate skips).",
  coverageSeconds:
    "Union duration of all returned segments in seconds — use for brand-deal density instead of summing durationSeconds (which double-counts overlaps).",
  minVotes: "Minimum SponsorBlock votes applied when filtering segments for this response.",
  actionType: 'SponsorBlock action (usually "skip").',
  startSeconds: "Segment start time in seconds.",
  endSeconds: "Segment end time in seconds.",
  startFormatted: "Segment start as M:SS or H:MM:SS.",
  endFormatted: "Segment end as M:SS or H:MM:SS.",
  hasLiveTab:
    "Whether the YouTube channel exposes a Live tab. False ⇒ channel-streams returns no rows (not Videos fallthrough).",
  productType: "Platform product type (e.g. clips, feed). Null when not applicable (Image/Sidecar) — never an empty string.",
  pollOptions:
    "Poll choices when postType is poll. Each item has text, voteCount (null when YouTube gates counts behind sign-in), and percentage.",
  totalVotes: "Total poll votes when YouTube exposes them (often approximate from a compact label).",
  totalVotesText: "Original poll vote-count label from YouTube (e.g. \"1.6M votes\").",
  totalVotesIsApproximate:
    "True when totalVotes was parsed from a compact K/M/B label; null on non-poll posts (no vote total).",
  likeCountText: "Original like-count label from the platform (e.g. \"727K\", \"3.2M\").",
  likeCountIsApproximate:
    "True when likeCount was parsed from a compact K/M/B label rather than an exact integer.",
  language: "Detected or requested language code.",
  region: "Region or country code for this result (meaning depends on the endpoint — market vs creator home).",
  regionConfidence: 'For an inferred region, confidence of the guess: "high", "medium", or "low". Null when the region came from TikTok.',
  regionSource: 'Where region came from: "tiktok" (authoritative, reported by TikTok) or "inferred" (best-effort estimate from public signals).',
  audienceLocations:
    "Ranked commenter-country breakdown (basis=commenters). Each item has country, countryCode, count, numeric percentage, and percentageText. Not a follower census.",
  audienceLanguages:
    "Ranked comment-language breakdown from the same comment sample (comment_language). Each item has language, count, percentage, percentageText.",
  other:
    "Remainder of the sample not shown in the truncated list (count + numeric percentage). Present when countriesLimit (or a docs example) keeps only the top N countries.",
  basis:
    'What the demographics sample measures. For audience-demographics: "commenters" (people who commented on sampled videos) — not a full follower census.',
  totalCountries: "How many distinct countries appeared in the commenter sample (before countriesLimit truncation).",
  confidence:
    'Sample-strength label from sampleSize: "low" (<400), "medium" (400–999), "high" (≥1000). Commenter geography is noisy at small n.',
  languageSampleSize: "How many comments contributed a language code to audienceLanguages.",
  videosRequested: "videos query parameter used for this call (12, 30, or 60).",
  country:
    "Country for the request context. On popular-creators top-level: ISO feed market you queried (e.g. US) — not each creator's home country (see region).",
  count: "Number of items in this bucket (e.g. commenters from this country in the sample).",
  countryCode: "ISO-3166 alpha-2 country code (e.g. US, MX).",
  percentage:
    "Numeric share of the sample (e.g. 26.02). Never a string — use percentageText for display. Values across audienceLocations (+ other) sum to ~100.",
  percentageText:
    'Display form of percentage with a % suffix (e.g. "26.02%"). Prefer percentage for math.',
  accessibilityCaption:
    "Facebook (or Instagram) image alt-text / accessibility description — not a user-written post caption. On Instagram channel-posts this is sparse (often null); populated e.g. on @instagram/DbbY9pdm6Q2.",
  shopProductUrl:
    "TikTok Shop product page URL when the video anchors a product (https://www.tiktok.com/shop/pdp/…). Null/omitted when the video does not sell.",
  authorRegion:
    "Author's TikTok profile region (ISO country) when present on the aweme — avoids a separate profile-region call per video.",
  descLanguage: "Language code TikTok assigns to the video caption when exposed.",
  isEligibleForCommission:
    "Whether the video is marked eligible for affiliate commission when TikTok exposes the flag.",
  sampleSize: "Total number of commenter countries counted across the sampled videos.",
  videosSampled: "How many of the creator's recent videos were sampled to build the breakdown.",
  usageCount:
    "How many TikTok videos use this sound when TikTok exposes the total. Null when the music/aweme embed and music page omit it — never a fake zero.",
  durationSeconds: "Length in seconds for this item (full media length, or a segment span when the endpoint documents a start/end).",
  artistId: "Primary artist / sound-owner user id when TikTok exposes one.",
  authorSecUid: "Primary artist / sound-owner secUid when TikTok exposes one.",
  lang: "Language code of the content.",
  hashtags: "Hashtags extracted from the text.",
  mentions: "Accounts mentioned in the text.",
  tags: "Tags attached to the item.",
  topics: "Detected topics and themes.",
  nsfw: "Whether the content is marked NSFW.",
  sensitive: "Whether the content is flagged sensitive.",
  isLive: "Whether the item or channel is currently live.",
  streamQualities: "Parsed live stream qualities when the endpoint exposes a quality ladder.",
  streams: "Playable stream rows or quality-keyed pull URLs — shape depends on the endpoint.",
  liveSubOnly: "Whether the TikTok live is subscribers-only.",
  gameTagId: "TikTok live game category id when the room is a gaming broadcast (0 / omitted when not).",
  hashTagId: "TikTok live topic/hashtag category id when present.",
  paidEvent: "Paid-live metadata ({eventId, paidType}) when TikTok marks the room as a paid event.",
  totalEnterCount:
    "Lifetime total entries for the last/current room session. May remain on offline payloads as last-known; viewerCount is only set while isLive.",
  viewerCount:
    "Concurrent viewers while isLive. Omitted when offline — a leftover userCount on an ended room is not current.",
  streamId: "TikTok live stream id (distinct from room id when both exist).",
  isVideo: "Whether the item is a video.",
  isPinned: "Whether the item is pinned.",
  isAd: "Whether the item is a paid promotion.",
  isReply: "Whether the tweet is a reply.",
  isRetweet: "Whether the tweet is a retweet.",
  isBlueVerified: "Whether the account has blue-check verification.",
  verification:
    "Bluesky verification block: verifications[{issuer, issuerHandle, issuerDisplayName, uri, isValid, createdAt}], verifiedStatus, trustedVerifierStatus.",
  labels:
    "Moderation labels on the profile: [{src, uri, cid, val, neg, createdAt, expiresAt}]. src is the labeler DID; val is the label value (e.g. !hide).",
  associated:
    "Bluesky association counts: lists, feedgens, starterPacks, labeler (plus chat/activitySubscription when present).",
  pinnedPost:
    "Strong ref of the post this account pinned/featured: {uri, cid, rkey}. Omitted when none.",
  joinedViaStarterPack:
    "Starter pack the account joined through when AppView exposes it: {uri, cid, name, creator{did, handle, displayName}}.",
  indexedAt:
    "When the Bluesky AppView last indexed this profile record (ISO-8601). Not last activity — use createdAt for account age and user-posts for recent activity.",
  verifiedStatus: "Bluesky verification status string (e.g. valid, none).",
  trustedVerifierStatus: "Whether this account is a trusted verifier (e.g. valid, none).",
  feedgens: "Number of custom feeds (feed generators) this account publishes.",
  starterPacks: "Number of starter packs this account publishes.",
  labeler: "Whether this account is a Bluesky labeler (moderation service).",
  targeting:
    "LinkedIn Ad Library targeting segments (language, location, company, and related keys).",
  adDuration: "LinkedIn 'Ran from … to …' availability string.",
  startDate: "Ad start date (YYYY-MM-DD) when LinkedIn exposes a ran-from range.",
  endDate: "Ad end date (YYYY-MM-DD) when LinkedIn exposes a ran-from range.",
  totalImpressions: "Estimated total impressions band from LinkedIn Ad Library (e.g. 1k-5k).",
  impressionsByCountry: "Per-country impression share rows ({country, impressions}).",
  destinationUrl: "Outbound click-through / landing URL when the platform exposes one.",
  carouselImages: "Ordered carousel creative image URLs when the ad is a carousel.",
  paidForBy: "Payer entity string from LinkedIn's 'Paid for by' line.",
  totalAds: "Total ads matching the LinkedIn Ad Library search criteria.",
  paginationToken: "Opaque LinkedIn Ad Library pagination token for the next page.",
  isLastPage: "Whether LinkedIn reports this search page as the last page.",
  channelId: "Stable channel id (YouTube UC… when applicable).",

  // Media
  thumbnailUrl: "Thumbnail image URL.",
  thumbnail: "Thumbnail image URL.",
  image: "Image URL.",
  avatar: "Avatar / profile picture URL. Canonical across profile endpoints.",
  profileImage:
    "Profile image URL. Deprecated alias of avatar on Instagram/Twitter/Threads/TikTok profile endpoints (one release).",
  isThreadsOnlyUser:
    "Whether the account exists only on Threads (not auto-created from Instagram). Often null on web hydrate when Meta omits the flag.",
  bioFragments:
    "Parsed bio fragments (plaintext / link / mention / tag) when Meta exposes text_app_biography.",
  profileImageVersions: "Profile image URLs at multiple resolutions ({url, width, height}).",
  hasOnboarded: "Whether the account has onboarded to Threads (text post app).",
  linkId: "Stable id for a bio link when Meta exposes one.",
  banner: "Banner / cover image URL. Canonical across profile endpoints.",
  bannerImage: "Banner image URL. Deprecated alias of banner on Twitter (one release).",
  bannerUrl: "Banner image URL. Deprecated alias of banner on YouTube (one release).",
  coverImage: "Cover image URL.",
  coverUrl: "Cover image URL.",
  logo: "Logo image URL.",
  videoUrl:
    "Playback URL when the platform exposes one. Content type varies by platform — check videoType (hls vs mp4) before treating it as a downloadable file.",
  videoType: 'Playback content type: "hls" (.m3u8 playlist) or "mp4" (progressive file).',
  hlsUrl: "HLS master/media playlist URL (.m3u8). Not a progressive video file — players and ffmpeg ingest this as a stream.",
  mp4Url: "Progressive MP4 file URL when the platform exposes one.",
  music: "Reel soundtrack metadata (id, type, trackTitle, albumArt) when Facebook exposes it.",
  videoHeight: "Video height in pixels when available.",
  videoWidth: "Video width in pixels when available.",
  videoHdUrl: "High-definition playable video URL when Facebook exposes one.",
  videoSdUrl: "Standard-definition playable video URL when Facebook exposes one.",
  captionsUrl: "URL to Facebook-generated captions (.srt) when exposed on the post/Reel.",
  feedbackId: "Facebook feedback id for the post (useful for comments threading).",
  downloadUrl: "CDN media URL when present (not a dedicated download API).",
  noWatermarkUrl: "Watermark-free variant of the video URL.",
  embedUrl: "Platform embed URL when a real embed id is known. Do not invent from a page/permalink id.",
  animatedPreviewUrl: "Storyboard strip / animated preview image for a VOD.",
  brandName: "Advertiser / brand name when Creative Center exposes one.",
  ctrTier: "CTR performance band (e.g. top_10%, top_25%, below_50%).",
  costTier: "Relative spend signal from Creative Center (0–5 style tier).",
  isSparkAd: "Whether the creative is a Spark Ad (boosted organic-style post).",
  industryKey: "Creative Center industry key / label id.",
  objectiveKey: "Creative Center campaign objective key.",
  periodDays: "Lookback window in days used for the Top Ads ranking.",
  ctr: "Click-through rate signal from Creative Center (typically 0–1).",
  videoId: "Platform video ID.",
  streamUrls: "Flat live stream playback URLs (compat). Prefer streamQualities / streams for quality/codec metadata.",
  playUrl: "Playback URL.",
  audioUrl: "Audio file URL.",
  media: "Media attached to the item.",
  images: "Attached image URL list for this item.",
  photos: "Photo URLs attached to the item.",

  // Duration
  duration: "Duration when present — prefer durationSeconds (number) and durationText on endpoints that expose both.",
  durationText: "Human-readable duration (e.g. 1:26:25).",
  durationMs: "Length in milliseconds.",
  durationFormatted: "Human-readable duration.",
  start: "Start time in seconds.",
  end: "End time in seconds.",
  expiresAt: "When signed URLs expire (ISO 8601).",

  // Engagement
  engagement: "Engagement metrics for the item.",
  views: "View count when the platform exposes one.",
  viewCount: "View count.",
  plays:
    "Deprecated one-release alias of engagement.views on Instagram video endpoints — same value; prefer views.",
  viewsSource:
    'On Instagram videos: "instagram" | "facebook" when engagement.views is set; null when views is null. Never a 100%-null discriminator.',
  viewsInstagram:
    "Removed — use engagement.views + viewsSource. (Previously Instagram-only plays.)",
  viewsFacebook:
    "Removed — use engagement.views + viewsSource. (Previously Facebook cross-post plays.)",
  likes: "Like count (number).",
  likeCount:
    "Like count as an integer. Compact UI labels (\"727K\") are expanded here; see likeCountText for the original string.",
  comments: "Comment count.",
  commentCount: "Comment count.",
  totalComments: "The video's total number of comments, across all pages.",
  shares: "Share count. Null when the platform does not expose a public share metric (e.g. YouTube).",
  shareCount: "Share count.",
  reposts: "Repost count.",
  replies: "Number of replies.",
  replyCount: "How many replies this comment has. Use Comment Replies with this comment's id to fetch them.",
  retweets: "Retweet count.",
  quotes: "Quote count.",
  bookmarks: "Bookmark count.",
  saves: "Save count. Null when the platform does not expose saves (e.g. YouTube).",
  interactions: "Sum of available engagement counts (likes + comments + shares + saves). Null when none of those are present.",
  upvotes: "Upvote count.",
  dislikes: "Dislike count.",
  score:
    "Vote score. On Reddit this is the platform's authoritative score field (not ups−downs — public JSON almost always zeros downs). Prefer score over upvotes when both are present.",
  rank: "Rank position in the list.",
  engagementRate:
    "Engagement rate. Meaning depends on engagementRateBasis — never compare values across different bases. Post/compare analytics: interactions/views (ratio 0–1+). TikTok popular-creators: Creative Center interact rate (percent) or avgLikesPerVideo/followers × 100.",
  engagementRateBasis:
    "Canonical formula key for engagementRate: interactions/views (post analytics) | creative_center | avgLikesPerVideo/followers.",
  failedCount: "Number of URLs that could not be resolved in this compare batch.",
  failed: "URLs that failed resolution ({url, platform, reason}).",
  avgViews: "Average views across the sampled For You videos that surfaced this creator.",
  contact: "Outreach contacts parsed from the bio when present (emails[], links[]).",
  suggestion: "A search term TikTok autocompletes for your keyword — a phrase real users search for.",
  searchUrl: "Direct TikTok search URL for this suggestion — open it to see the matching results.",
  seed: "The seed keyword this suggestion was expanded from.",

  // Transcript / summarize
  transcript: "Complete text transcript (file-upload endpoints). Timed caption/ASR endpoints use text instead.",
  wordCount: "Total number of words in the transcript (file-upload endpoints).",
  segments:
    "Timed caption/ASR: array of {text,startMs,endMs}. File-upload video-transcript: segment count. Sponsor endpoints: sponsor segment list.",
  transcriptSegments: "Timestamped transcript segments on file-upload endpoints (start/duration/timestamp). Timed endpoints use segments[] instead.",
  source:
    'Where the transcript came from: "captions" (platform subtitles), "asr" / "whisper" (AI speech-to-text), or "fallback" (secondary caption path). Use this to weight RAG quality.',
  isAutoGenerated: "Whether the selected YouTube caption track is auto-generated (ASR). Null when source is not captions.",
  isTranslated: "Whether the transcript was machine-translated to the requested language. Null when unknown.",
  availableLanguages: "Caption languages available on the video (languageCode, languageName, isAutoGenerated).",
  requestedLanguage: "Language the caller asked for (null when unspecified).",
  returnedLanguage: "Language of the caption track actually returned.",
  // Meta Ad Library (additive)
  isActive: "Whether the ad is currently eligible for delivery.",
  publisherPlatforms: "Where the ad ran (FACEBOOK, INSTAGRAM, MESSENGER, AUDIENCE_NETWORK, …).",
  linkDescription: "Link description / preview text under the creative.",
  brandedContent: "Branded-content metadata when present.",
  disclaimerLabel: 'Transparency disclaimer text (e.g. "Paid for by …").',
  byline: "Paid-for-by / byline string when Meta exposes one.",
  reachEstimate: "Meta reach estimate display string when published (often political/issue ads only).",
  reachEstimateRange: "Parsed reachEstimate as {min, max, raw}.",
  totalActiveTime: "Total active delivery time in seconds when Meta exposes it.",
  politicalCountries: "Countries where the ad is classified as political/issue.",
  pageLikeCount: "Advertiser Facebook Page like count (spam/size signal).",
  pageCategories: "Advertiser Page categories from Meta.",
  pageEntityType: "Advertiser entity type (e.g. PERSON_PROFILE, PAGE).",
  cards: "Carousel cards with per-card text, CTA, landing URL, and media.",
  videos:
    "Videos related to this result — meaning depends on the endpoint (integer count vs typed asset list). Prefer the field note on this page.",
  spendRange:
    "Parsed spend as {min, max, currency, raw}. Prefer this for sorting; spend stays the Meta display string. Usually null for commercial ads.",
  impressionsRange:
    "Parsed impressions as {min, max, raw}. Prefer this for sorting; impressions stays the Meta display string. Usually null for commercial ads.",
  searchResultsCount: "Best-effort total hits Meta reports for the query (not just this page).",
  status: "Status value for this endpoint (see the field note on this page for enum meaning).",
  limit: "Requested max items for this call.",
  authorFullname: "Stable Reddit account fullname (t2_…). Prefer this over author for joins.",
  downs: "Downvote count when Reddit exposes it (often 0 on public JSON).",
  distinguished: "moderator/admin distinction when present.",
  controversiality: "Reddit controversiality flag (0 or 1).",
  upvoteRatio: "Post upvote ratio (0–1) when Reddit exposes it.",
  experience: "LinkedIn experience entries when available (title, company, dates, description).",
  education: "LinkedIn education entries when available (school, degree, dates).",
  currentCompany: "Current company inferred from LinkedIn worksFor / headline — not SEO meta.",
  originalPrice: "List/original price before discount (numeric when unmasked).",
  discount: "Discount amount, percentage, or display string when the platform exposes one.",
  skus: "Per-variant SKU rows ({id, stock, price, originalPrice, status}).",
  shopInfo: "Shop rollup (sold, followers, productCount, identityLabel) when available.",
  relatedVideos: "Affiliate/related TikTok videos promoting the product when available.",
  summary: "AI-generated summary of the content.",
  keyPoints: "The most important takeaways.",
  sentiment: "Overall tone (positive, neutral, negative).",
  speaker: "Speaker label for the segment.",
  // TikTok / profile identity (additive)
  secUid: "TikTok secure user ID — required for many platform-internal list endpoints.",
  createTime: "When the account was created (ISO 8601).",
  friendCount: "Mutual-follow (friends) count when exposed.",
  diggCount: "Total likes this account has given.",
  profileImageMedium: "Medium-resolution profile image URL.",
  profileImageThumb: "Thumbnail profile image URL.",
  bioLinkRisk: "TikTok's own risk score for the bio link, when present.",
  isCommerceUser: "Whether TikTok marks the account as a commerce user.",
  isSeller: "Whether the account is a TikTok Shop seller (ttSeller).",
  isOrganization: "Whether the account is an organization account.",
  isAdVirtual: "Whether the account is a virtual/ad account.",
  commentSetting: "Account comment privacy setting code from TikTok.",
  duetSetting: "Account duet privacy setting code from TikTok.",
  stitchSetting: "Account stitch privacy setting code from TikTok.",
  downloadSetting: "Account download privacy setting code from TikTok.",
  followingVisibility: "Whether the following list is visible.",
  uniqueIdModifyTime: "When the @username was last changed (ISO 8601), if known.",
  nickNameModifyTime: "When the display name was last changed (ISO 8601), if known.",
  fetchedAt: "When this snapshot was fetched (ISO 8601 UTC).",

  // Comments
  authorAvatarUrl: "Profile picture URL of the person who wrote the comment.",
  authorUrl: "Profile URL of the author.",
  authorName: "Name of the author.",
  authorIsVerified: "Whether the author is verified.",
  authorIsChannelOwner: "Whether the author owns the channel.",
  hasCreatorHeart: "Whether the creator hearted the comment.",
  parentId: "ID of the parent comment for replies.",
  edited: "Whether the comment was edited.",
  stickied: "Whether the comment is stickied.",

  // Commerce / ads
  price: "Price of the item.",
  priceFormatted: "Formatted price string.",
  currency: "Currency code.",
  rating: "Average rating.",
  reviews: "Number of reviews.",
  reviewCount: "Number of reviews.",
  sold: "Units sold.",
  stock: "Units in stock.",
  advertiser: "Advertiser running the ad.",
  adFormat: "Format of the ad creative.",
  cta: "Call-to-action text.",
  landingUrl: "Landing page the ad links to.",
  firstShown: "When the ad was first shown.",
  lastShown: "When the ad was last shown.",
  impressions: "Estimated ad impressions.",
  spend: "Estimated ad spend.",

  // Music / audio
  album: "Album the track belongs to.",
  artists: "Artists credited on the item.",
  artist: "Artist name.",
  artistUrl: "Artist profile URL.",
  genre: "Music genre.",
  releaseYear: "Year of release.",
  releaseDate: "Release date.",
  totalTracks: "Number of tracks.",
  totalEpisodes: "Number of episodes.",
  monthlyListeners: "Monthly listener count.",
  worldRank: "Artist global rank by monthly listeners (web-player GraphQL; not on Spotify's public Web API).",
  topCities: "Top listener cities with country, region, and listener counts.",
  externalLinks: "Official external profile links (Facebook, Instagram, Twitter, etc.).",
  topTracks: "Artist's popular tracks with play counts and album art.",
  concerts: "Upcoming concerts with city, venue, and start time when Spotify exposes them.",
  relatedArtists: "Related artists with profile image and Spotify URL.",
  albums: "Recent albums (name, cover, release year, track count).",
  singles: "Recent singles and EPs (name, cover, release year, track count).",
  albumsCount: "Total album count for the artist.",
  singlesCount: "Total singles/EP count for the artist.",
  listeners: "Listener count for a city in topCities.",
  venue: "Concert venue name.",
  startsAt: "Concert start time as an ISO-8601 string.",
  isFestival: "Whether the concert is part of a festival.",
  albumUri: "Spotify album URI for a track.",
  isrc: "International Standard Recording Code.",
  musicName: "Name of the soundtrack used.",
  musicUrl: "URL of the soundtrack used.",
  musicId: "ID of the soundtrack used.",

  // Channels / streaming
  channelName: "Name of the channel.",
  channelUrl: "URL of the channel.",
  channelFollowers: "Follower count of the channel.",
  channelVerified: "Whether the channel is verified.",
  game: "Game or category being streamed.",
  viewers: "Current live viewer count.",
  broadcaster: "Name of the broadcaster.",
  isAffiliate: "Whether the channel is an affiliate.",

  // Developer / repos
  stars: "Star count.",
  forks: "Fork count.",
  watchers: "Watcher count.",
  openIssues: "Open issue count.",
  defaultBranch: "Default branch name.",
  homepage: "Project homepage URL.",
  license: "License identifier.",
  pushedAt: "Last push date (ISO 8601).",
  isFork: "Whether the repository is a fork.",
  isArchived: "Whether the repository is archived.",
  owner: "Owner of the repository.",
  publicRepos: "Number of public repositories.",
  publicGists: "Number of public gists.",

  // Download formats
  formats: "All available download formats.",
  itag: "YouTube format identifier.",
  mimeType: "Container and codecs (e.g. video/mp4; avc1...).",
  qualityLabel: "Resolution label (e.g. 720p).",
  quality: "Quality tier of the format.",
  width: "Width in pixels.",
  height: "Height in pixels.",
  fps: "Frames per second.",
  bitrate: "Bitrate in bits per second.",
  audioQuality: "Audio quality tier.",

  // Reddit / community
  subreddit: "Subreddit the post belongs to.",
  flair: "Post flair.",
  moderatorCount: "Number of moderators.",

  // Links-in-bio
  linkCount: "Number of links on the page.",
  links: "Links listed on the page.",
  socials: "Social profiles listed on the page.",
  socialAccounts: "Detected social accounts by platform.",
};

const RAW_KEYS = new Set(["raw", "rawFirstItem", "_metadata"]);

const isScalarValue = (v: unknown): boolean =>
  v === null || ["string", "number", "boolean"].includes(typeof v);

function humanizeField(name: string): string {
  const words = name
    .replace(/[_-]+/g, " ")
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .toLowerCase()
    .trim();
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function exampleHint(v: unknown): string {
  if (typeof v === "string")
    return v && v.length <= 40 && !v.startsWith("http") ? ` Example: "${v}".` : "";
  if (typeof v === "number" || typeof v === "boolean") return ` Example: ${v}.`;
  return "";
}

/** Per-slug overrides when a shared FIELD_DESCS key means something else elsewhere. */
const SLUG_FIELD_DESCS: Record<string, Record<string, string>> = {
  "tiktok-live": {
    status:
      "TikTok liveRoom/user status enum. 2 = currently live (isLive true). Other codes (commonly 4) mean the last room payload is ended/stale — still may include title, enter counts, and pull URLs.",
    isLive: "true only when status === 2 — a non-empty room payload does not mean the creator is live.",
    streamQualities:
      "Parsed TikTok live pull qualities ({quality, codec, resolution, bitrate, flv, hls, cmaf, dash, lls}). Prefer hls/cmaf for browsers — FLV is not web-playable.",
    streams: "TikTok live pull URLs keyed by quality (hd/sd/ld/origin/ao/…); h264 preferred when both codecs exist.",
  },
  "tiktok-live-info": {
    status:
      "TikTok liveRoom/user status enum. 2 = currently live (isLive true). Other codes (commonly 4) mean the last room payload is ended/stale — still may include title, enter counts, and pull URLs.",
    isLive: "true only when status === 2 — a non-empty room payload does not mean the creator is live.",
    streamQualities:
      "Parsed TikTok live pull qualities ({quality, codec, resolution, bitrate, flv, hls, cmaf, dash, lls}). Prefer hls/cmaf for browsers — FLV is not web-playable.",
    streams: "TikTok live pull URLs keyed by quality (hd/sd/ld/origin/ao/…); h264 preferred when both codecs exist.",
  },
  "tiktok-profile-region": {
    videos: "Total public video count on the profile (integer). Not a typed media asset list.",
    likes: "Total likes across the creator's videos (TikTok heartCount).",
    verified: "Whether TikTok shows a verified badge on this profile.",
    region:
      "Creator's country as an ISO code (e.g. IT, US). TikTok's authoritative value when it exposes one (rare); otherwise an AI-inferred guess from public profile cues. Check regionSource / regionConfidence.",
  },
  "tiktok-search-suggestions": {
    region:
      "Market you localized suggestions for (from the country query param, e.g. US). Not a creator's home country — this endpoint has no regionSource.",
    language:
      "Interface language used to localize suggestions (from the language query param, e.g. en-US).",
  },
  "tiktok-channel-details": {
    likes: "Total likes across the creator's videos (TikTok heartCount).",
    verified: "Whether TikTok shows a verified badge on this profile.",
    videos: "Not returned here — use postCount for the profile's public video count.",
  },
  "twitter-community": {
    creator:
      "X handle of the community founder (normalized from GraphQL creator_results).",
    createdAt: "When the community was created (ISO-8601 UTC, e.g. 2022-02-15T04:47:27.000Z).",
    memberCount: "How many members the community has.",
    joinPolicy: 'Who can join (e.g. "Open").',
    isNsfw: "Whether X marks the community as NSFW.",
    bannerImage: "Community banner image URL when exposed.",
    rules: "Community moderation rules as {name, description}.",
  },
  "twitter-community-tweets": {
    communityName: "Display name of the X Community.",
    memberCount: "How many members the community has (same signal as /community).",
    publishedAt: "Tweet publish time as ISO-8601 UTC.",
  },
  "twitter-user-tweets": {
    publishedAt:
      "Tweet publish time as ISO-8601 UTC (e.g. 2022-04-28T00:56:58.000Z). Not Twitter's raw created_at string.",
    hashtags: "Hashtag texts without #. Always an array (empty when the tweet has none).",
    media: "Media image/video preview URLs when present. Always an array (empty when none).",
    source:
      "Client app that posted the tweet (e.g. Twitter for iPhone) when Twitter exposes it — useful for bot signals. Often omitted on the public timeline embed.",
    conversationId: "Thread root id (conversation_id_str) for grouping replies.",
  },
  "twitter-search": {
    publishedAt: "Tweet publish time as ISO-8601 UTC.",
    hashtags: "Hashtag texts without #. Always an array (empty when none).",
  },
  "twitter-tweet-details": {
    publishedAt: "Tweet publish time as ISO-8601 UTC.",
    hashtags: "Hashtag texts without #. Always an array (empty when none).",
  },
  "twitter-profile": {
    verified: "Aggregate verification flag (blue, legacy, identity, or affiliate) — always present.",
    displayName: "Profile display name (same concept as other platforms; name kept for compatibility).",
  },
  "threads-profile": {
    displayName: "Profile display name (same concept as TikTok/IG/YouTube; name kept for compatibility).",
    name: "Alias of displayName (kept for older clients).",
    private: "Whether the Threads account is private (same signal as isPrivate; TikTok-style key).",
    isPrivate: "Whether the Threads account is private (same signal as private; Instagram-style key).",
    bioLinks:
      "External links from the Threads bio. Each item is {url, verified, linkId} — verified means Meta confirmed the link (fake/impersonation signal).",
    bioFragments:
      "Parsed bio pieces from Meta text_app_biography (plaintext / link / mention / tag) when the web hydrate exposes them.",
    isThreadsOnlyUser:
      "true when the account exists only on Threads (no Instagram twin). Pair with Instagram fbid for an IG↔FB↔Threads identity chain when all three are present.",
    transparencyLabel:
      "Meta transparency / state-affiliated media label when exposed — brand-safety signal. Often null on logged-out hydrate.",
    likes: "Not returned on profile — use followers for reach; post likes live on user-posts / post-details.",
    verified: "Whether Meta shows a verified badge on this Threads profile.",
  },
  "threads-user-posts": {
    author:
      "Top-level: full profile card for the requested handle (once). Per-post author is slim (username/displayName/verified, no profileImage) to avoid repeating CDN URLs.",
    threadId:
      "Id of the thread root post. Multi-part Threads share one threadId — group by this to rebuild the chain.",
    replyToId: "Parent post id when this row is a reply in a multi-part Thread (null on the root).",
    isReply: "true when the post replies to another post in a Thread chain.",
    isQuote: "true when the post quotes another post.",
    likes: "Heart count on the Threads post (engagement.likes).",
    verified: "Whether Meta shows a verified badge on the post author.",
    views:
      "Public view count when Meta exposes it on the hydrate (often null on logged-out profile feeds).",
    publishedAt: "Post publish time as ISO-8601 UTC.",
  },
  "threads-post-details": {
    likes: "Heart count on the Threads post (engagement.likes).",
    verified: "Whether Meta shows a verified badge on the post author.",
    views:
      "Public view count when Meta exposes it. Often null on logged-out permalink hydrate even when the Threads app shows views.",
    publishedAt: "Post publish time as ISO-8601 UTC.",
    comments:
      "Inline reply posts when Meta embeds them on the permalink. Always an array — [] when the logged-out hydrate omits the reply tree (common on viral posts).",
    relatedPosts:
      "Algorithmic related Threads from BarcelonaLoggedOutRelatedPosts (other creators). Always an array; empty on Apify thin fallbacks.",
    threadId: "Id of the thread root post.",
    replyToId: "Parent post id when this post is a reply.",
    isReply: "true when the post replies to another post.",
    isQuote: "true when the post quotes another post.",
  },
  "threads-search": {
    likes: "Heart count on the Threads post (engagement.likes).",
    verified:
      "true/false when Meta embeds the badge flag; null when the hydrate omits it (unknown — not the same as unverified).",
    quotes:
      "Quote-post count when Meta exposes it; null when omitted (unknown — not zero).",
    publishedAt: "Post publish time as ISO-8601 UTC (Meta Top SERP — may be months old).",
    views:
      "Public view count when Meta exposes it on the search hydrate (often null).",
  },
  "threads-search-users": {
    id: "Meta user pk when embedded on the search hydrate; null if the author blob omits it.",
    verified:
      "true/false when Meta embeds the badge flag; null when omitted (unknown).",
    profileImage: "Avatar URL when Meta embeds it on the search-post author card.",
    followers:
      "Follower count when present on the author blob — usually null on search; use Threads Profile for counts.",
    likes: "Not returned on search-users — this endpoint lists profiles, not posts.",
  },
  "kick-clip": {
    creator:
      "Who created/cut the Kick clip (distinct from the broadcaster channel) — {id, username, displayName, url, profilePicture}; name is a deprecated alias of displayName.",
    channel:
      "Kick broadcaster channel for the clip — {id, username, displayName, url, profilePicture}; name is a deprecated alias of displayName.",
    categoryId: "Kick category id.",
    category: "Kick category display name (e.g. Just Chatting).",
    videoUrl:
      "HLS playlist URL (.m3u8) for this clip. Same value as hlsUrl — not a progressive MP4 file. Use an HLS player or ffmpeg; do not save as .mp4.",
    videoType: 'Always "hls" for Kick clips today (Kick serves playlist.m3u8).',
    hlsUrl: "Kick clip HLS playlist (.m3u8). Prefer this when you need an explicit stream URL.",
    url: "Kick clip web page (https://kick.com/{channel}/clips/clip_…). Not the HLS playlist.",
    vod: "Source VOD — {id, url, urlWithOffset}. url is https://kick.com/{channel}/videos/{id}; urlWithOffset appends ?t={vodStartsAt} seconds.",
    urlWithOffset:
      "VOD page URL with ?t={vodStartsAt} so Kick's player can open at the clip start (seconds).",
    vodStartsAt: "Offset into the source VOD (seconds) where the clip starts. Paired with vod.urlWithOffset.",
    clips:
      "Channel mode only — recent clips for the channel (same row shape as clip). No top-level clip object in this mode.",
    totalReturned:
      "Channel mode only — number of clips in this response. No nextCursor — Kick's channel clips list is a single page (use limit).",
    channelUrl: "Canonical Kick channel URL derived from the request.",
    displayName: "Display name for channel/creator. Canonical; name is a deprecated alias.",
    name: "Deprecated alias of displayName on nested channel/creator objects.",
  },
  "amazon-shop-page": {
    asin: "Amazon Standard Identification Number — catalog identity for joins across sellers and marketplaces.",
    url: "Canonical product page https://www.amazon.com/dp/{ASIN} (not a shop/{handle}/getProductDetails/… affiliate path).",
    products:
      "Seller storefront product rows — asin, title, canonical /dp url, image, price fields, rating/reviews, isPrime/isBestSeller/isSponsored.",
    seller: "Third-party seller identity {id, name, url} for the /sp?seller= or /s?me= storefront.",
    marketplace: "Amazon marketplace code echoed from the request (default US).",
  },
  "github-user": {
    platform: 'Always "github" on this endpoint.',
    type: 'GitHub account kind: "User" or "Organization" (upstream casing preserved).',
    name: "GitHub profile display name (not a deprecated alias — GitHub has no displayName field here).",
    email:
      "Public email only when the account made it public on their GitHub profile. Omitted when private or unset.",
    hireable: "true when the user marked themselves hireable on GitHub; omitted/null when unset.",
    siteAdmin: "true when the account is a GitHub site admin (rare).",
    nodeId: "GitHub GraphQL node_id for the account.",
    publicRepos: "Count of public repositories.",
    publicGists: "Count of public gists.",
    twitterUsername: "Public X/Twitter username when set on the GitHub profile. Omitted when unset.",
  },
  "github-repository": {
    platform: 'Always "github" on this endpoint.',
    type: 'Always "repository" on each repo object.',
    language: 'Primary programming language (e.g. "C", "Python") — not a spoken-language code.',
    stars: "stargazers_count — total stars.",
    watchers:
      "subscribers_count — people watching for notifications. Omitted on list payloads that lack the field. Never GitHub's legacy watchers_count (that equals stars).",
    openIssuesAndPrs:
      "GitHub open_issues_count — open issues plus open pull requests. Use github/pull-requests for PRs alone.",
    license: "SPDX license id when GitHub maps one. Null when NOASSERTION/NONE — see licenseName.",
    licenseName: "Human-readable license label from GitHub (e.g. Other, MIT License).",
    parent: "Upstream fullName when isFork is true (from GitHub parent.full_name). Present on this detail endpoint only.",
    ownerType: 'Owner account kind: "User" or "Organization".',
    size: "Repository size in kilobytes (GitHub's size field).",
    visibility: 'Repository visibility (usually "public" on this surface).',
    hasIssues: "Whether the issues feature is enabled on the repo.",
    hasDiscussions: "Whether GitHub Discussions is enabled.",
  },
  "github-trending-repositories": {
    source: 'Always "github.com/trending" — HTML trending page, not REST star search.',
    since: "Trending window echoed from the request: daily | weekly | monthly.",
    language: "Programming-language filter slug echoed from the request (null when browsing all languages).",
    starsGained: "Stars gained in the since window — the metric that ranks github.com/trending.",
    rank: "1-based position on the trending page.",
    stars: "Total star count shown on the trending card.",
    forks: "Total fork count shown on the trending card.",
  },
  "github-trending-developers": {
    source: 'Always "github.com/trending/developers" — not REST /search/users.',
    since: "Trending window echoed from the request: daily | weekly | monthly.",
    rank: "1-based position on the trending developers page.",
    followers: "Follower count hydrated from GET /users/{login} (the ranking signal you can sort on).",
    popularRepo: "owner/name of the popular repo shown on the trending card.",
    publicRepos: "Public repository count from the hydrated profile.",
    bio: "Public profile bio when set.",
  },
  "github-contributions": {
    source: "Public contribution calendar HTML path (github.com/users/{login}/contributions).",
    totalContributions:
      "Contributions in the last year — the number on the profile graph heading. Equals sum(days[].count).",
    from: "Earliest date in days[] (YYYY-MM-DD). Always min(days[].date).",
    to: "Latest date in days[] (YYYY-MM-DD). Always max(days[].date) — the calendar window ends on today.",
    currentStreak:
      "Consecutive days with count>0 ending at the latest calendar day. Today-grace: if the last day is today and count is 0, that day is skipped (the day is not over); a zero on any earlier day breaks the streak. Computed after sorting days ascending.",
    longestStreak:
      "Longest run of consecutive days with count>0 anywhere in the window (independent of currentStreak).",
    days:
      "Per-day rows [{date (YYYY-MM-DD), count, level (0–4)}] sorted ascending by date — not GitHub's weekday-major DOM order. days.slice(-30) is the last 30 calendar days.",
    count: "Contributions on that date (from the calendar tool-tip).",
    level: "GitHub intensity 0–4 for the heatmap cell.",
  },
  "github-pull-requests": {
    state:
      "Top-level: filter echoed from the request (open|closed|all). On each PR: GitHub's PR state.",
    draft: "true when the PR is a draft — exclude from review-throughput metrics.",
    labels: "Label objects [{name, color, description}] from the PR.",
    author: "PR author card {id, login, avatar, url} — not a bare login string.",
    head: "Source branch {ref, sha, label}.",
    base: "Target branch {ref, sha, label}.",
    closedAt: "When the PR was closed (ISO). Distinct from mergedAt.",
    mergedAt: "When the PR was merged (ISO). Null/omitted if not merged.",
    requestedReviewers: "Requested reviewer cards [{id, login, avatar, url}].",
    assignees: "Assignee cards [{id, login, avatar, url}].",
    nextCursor: "Opaque Link-header cursor (not a bare page number).",
  },
  "github-activity": {
    type: 'GitHub event enum: PushEvent, PullRequestEvent, IssuesEvent, CreateEvent, WatchEvent, ForkEvent, …',
    payload:
      "Type-specific details — PushEvent: ref/size/commits[]; PullRequestEvent/IssuesEvent: action + entity fields.",
    eventCeiling:
      "Hard cap of 90 — GitHub's /users/{u}/events/public limit. hasMore is false once reached.",
    nextCursor: "Opaque Link-header cursor. Pagination stops at eventCeiling.",
    repo: "owner/name of the repository the event targets.",
  },
  "github-repositories": {
    sort: "Echo of sort=created|updated|pushed|full_name (default updated).",
    direction: "Echo of direction=asc|desc (default desc).",
    type: 'Top-level: affiliation filter owner|member|all. On each repo row: always "repository".',
    language: 'Primary programming language (e.g. "C", "Python") — not a spoken-language code.',
    watchers:
      "Omitted on this list endpoint — GitHub's list payload has no subscribers_count (and watchers_count would wrongly equal stars). Use github/repository for real watchers.",
    parent:
      "Omitted on this list — GitHub's /users/{u}/repos payload has no parent object. isFork is still set; call github/repository for upstream fullName.",
    openIssuesAndPrs:
      "GitHub open_issues_count — open issues plus open pull requests.",
    license: "SPDX id when mapped; null for NOASSERTION/NONE — see licenseName.",
    licenseName: "Human-readable license label from GitHub.",
    nextCursor: "Opaque Link-header cursor (not a bare page number).",
  },
  "github-followers": {
    id: "GitHub numeric account id — stable for joins and dedup across pages.",
    login: "GitHub username.",
    type: 'Account kind: "User" or "Organization".',
    url: "Profile URL (https://github.com/{login}).",
    avatar: "Avatar image URL.",
    nextCursor: "Opaque Link-header cursor (not a bare page number).",
  },
  "github-following": {
    id: "GitHub numeric account id — stable for joins and dedup across pages.",
    login: "GitHub username.",
    type: 'Account kind: "User" or "Organization".',
    url: "Profile URL (https://github.com/{login}).",
    avatar: "Avatar image URL.",
    nextCursor: "Opaque Link-header cursor (not a bare page number).",
  },
  "facebook-marketplace-location-search": {
    id: "Facebook Marketplace city_page.id — same value search listings expose as cityPageId. Omitted when unknown. Not duplicated as cityPageId.",
    timings: "Stage timings {path, hubMs, hubCount, totalMs}. path=ambiguous_table skips Decodo.",
    slug: "Marketplace hub path slug (e.g. austin, austin-minnesota).",
    name: "Display label, usually 'City, ST'.",
    city: "City name from the query / hub.",
    state: "US state abbreviation when known.",
    latitude: "Hub latitude when Facebook exposes it (included by default — no details flag).",
    longitude: "Hub longitude when Facebook exposes it.",
    query: "Echo of the q parameter you sent.",
    totalReturned: "Number of location candidates in this response.",
    locations: "Candidate Marketplace hubs for disambiguation or geocode.",
  },
  "facebook-page-details": {
    email: "Public email when the Facebook Page About section exposes one. Null when omitted.",
  },
  "komi-page": {
    id: "Komi talentProfile id as a string UUID (catalog-wide id convention).",
    displayName: "Creator display name from Komi.",
    username: "Komi account username (bare, no @).",
    bio: "Creator bio. Always present — empty string when Komi has none.",
    linkCount: "Number of content rows in links[] (hidden PRODUCT rows included when Komi marks visible:false).",
    links:
      "Content modules only — every row has the same keys: id, moduleId, versionId, order, type, title, url, visible, thumbnail, price, currency (absent → null). Social icons live in socials{}, not here. type distinguishes PRODUCT (price/currency filled) from LINK/YOUTUBE_VIDEO; null price means non-product, not a scrape miss. YouTube embeds fill title/thumbnail from item.metadata when needed.",
    type: "On links[]: Komi module type (LINK, PRODUCT, YOUTUBE_VIDEO, …).",
    socials:
      "CamelCase social URL map from Komi's socialProfileLinks — instagram/tiktok/youtube/twitter/facebook/snapchat/spotify/appleMusic/… plus website when a WEBSITE row (or website field) is published.",
    other:
      "Typed social rows that did not map into socials{} [{url, title?, type?}]. Empty when every published social mapped.",
    website: "Top-level convenience copy of socials.website when Komi publishes a WEBSITE row.",
    url: "On the page: https://komi.io/{username}. On a link row: outbound destination.",
  },
  "pillar-page": {
    id: "Pillar influencer id as a string UUID (catalog-wide id convention).",
    displayName: "Creator display name from Pillar (banner user_alias / full name). Canonical; name is a deprecated alias.",
    name: "Deprecated alias of displayName — prefer displayName.",
    handle: "Pillar page url_key (path slug). Canonical alongside username.",
    bio: "Creator bio. Always present — empty string when Pillar has none. description is a deprecated alias.",
    description: "Deprecated alias of bio — prefer bio.",
    location: "Public location string from Pillar page customizations (e.g. México). Null when unset.",
    email: "Public email from Pillar EMAIL social and/or account email when published.",
    linkCount: "Number of ACTIVE custom-link rows in links[] (DELETED + referral chrome excluded).",
    links:
      "Custom links [{id, type, title, url, clicks, order, thumbnail?, description?}]. clicks is Pillar's public per-link click count — the performance signal unique to this platform among link-in-bio sources.",
    type: "On links[]: host-derived social key when obvious (twitter, spotify, …), otherwise lowercase title.",
    clicks: "On links[]: cumulative public click count for that custom link.",
    products:
      "Featured commerce rows [{id, title, name, price, url, description, image, order?, showPrice?}]. title and name are the same string (SC parity).",
    socials:
      "CamelCase social URL map from Pillar banner socials + connected channels — instagram/tiktok/youtube/twitter/facebook/spotify/soundcloud/linkedin/snapchat/patreon/discord/twitch/medium/amazon/appleAppStore/googleAppStore/… Empty Pillar slots are omitted.",
    other:
      "Typed social channels that did not map into socials{} [{url, type?}]. Empty when every published channel mapped.",
    url: "On the page: https://pillar.io/{url_key}. On a link/product row: outbound destination.",
  },
  "linkbio-page": {
    id: "lnk.bio numeric profile id as a string (e.g. \"-1344625\"). From data-uid / avatar path.",
    displayName:
      "Real display name when lnk.bio publishes one. Omitted/null when the page only has @handle OG titles — we do not synthesise \"@\" + username.",
    name: "Deprecated alias of displayName — prefer displayName. Same null policy (no @handle fabrication).",
    handle: "lnk.bio path slug. Canonical alongside username.",
    website: "Official website URL when published (hero TYPE_BUTTON / official-website CTA or SOCIAL_WEB). Null when unset.",
    email: "Public email when lnk.bio exposes a mailto / EMAIL social. Null when unset.",
    whatsapp: "WhatsApp URL when published on the page. Null when unset.",
    linkCount: "Content buttons + primary social icon rows (family deep-link dupes excluded).",
    links:
      "[{url, title, id?, type?}]. Social icon rows carry platform titles (Facebook, Instagram, Triller, …) from icon labels — not null. Content biolinks keep their button text.",
    socials:
      "CamelCase URL map from data-network icons + @handle username CTAs — facebook/twitter/instagram/tiktok/youtube/snapchat/triller/website/whatsapp/…. Often filled where ScrapeCreators returns null.",
    other:
      "Typed social networks that did not map into socials{} [{url, title?, type?}]. Empty when every icon mapped.",
    url: "On the page: https://lnk.bio/{username}. On a link row: outbound destination.",
  },
  "linkme-profile": {
    id: "Linkme profile id as a hex string.",
    displayName:
      "firstName + lastName when present. Canonical human-readable name (no name/handle twins).",
    username: "Linkme account username (bare, no @). Canonical account handle.",
    firstName:
      "Given name from Linkme when distinct from displayName. Omitted when it would duplicate displayName with no lastName.",
    lastName: "Family name from Linkme when published.",
    bio: "Creator bio from the dehydrated profile. Empty string when unset.",
    avatar: "Profile image URL on media.link.me. Check isDefaultProfilePicture before treating it as a real photo.",
    isDefaultProfilePicture:
      "True when Linkme is serving a placeholder avatar (e.g. default/profile/avatar-2.png) — not the creator's photo.",
    profileVisitCount:
      "Public profile visit count as Linkme displays it (string, e.g. \"15.9k\" or \"29\"). One of the few audience metrics in the link-in-bio block.",
    totalLinks:
      "Linkme SSR profile.totalLinks — the platform's own counter from the dehydrated profile. Not derived from links[], webLinks[], or infoLinks[] (those are separate surfaces and their lengths can disagree with this number).",
    linkCount: "Number of featured CTA rows in links[] (not footer chrome). Prefer this when you need array length.",
    links:
      "Featured CTA buttons [{id?, title, url, thumbnail?, description?}]. Never Privacy Policy / Terms footer rows. Not a union of webLinks/infoLinks — iterate links alone for CTAs.",
    webLinks:
      "Social icon groups [{title, linkId?, links:[{linkValue, faceValue?, baseUrl?}]}] — Instagram, Spotify, Twitch, …. Separate from featured links[] (same destination may appear in both).",
    infoLinks:
      "Contact groups [{title, linkId?, links:[{linkValue, faceValue?}]}]. Email usually appears here; mirrored on top-level email. Separate from links[] / webLinks[].",
    email: "Public email from infoLinks when published. Null when unset.",
    stripeStatus: "{tipsEnabled, stripeEnabled, stripeAccountId?} — monetization / tips signal from Linkme.",
    verifiedAccount: "True when Linkme marks the account verified.",
    isAmbassador: "True when the profile is a Linkme ambassador.",
    isPrivate: "True when the profile is private.",
    createdAt: "Profile createdAt from Linkme (YYYY-MM-DD HH:mm:ss).",
    updatedAt: "Profile updatedAt from Linkme (YYYY-MM-DD HH:mm:ss).",
    socials:
      "CamelCase URL map derived from webLinks + featured CTAs — instagram/tiktok/youtube/twitter/facebook/spotify/appleMusic/twitch/threads/…",
    other: "Typed social rows that did not map into socials{} (e.g. Deezer, Youtube-music).",
    url: "On the page: https://link.me/{username}. On a link row: outbound destination.",
  },
  "linktree-page": {
    id: "Linktree account id as a string (catalog-wide id convention).",
    displayName: "Creator display name. Canonical; name is a deprecated alias.",
    name: "Deprecated alias of displayName — prefer displayName.",
    handle: "Linktree username. Canonical alongside username.",
    email:
      "Public email when the creator adds an EMAIL_ADDRESS mailto social on Linktree. Null/omitted when not published.",
    verticals:
      "Linktree niche/vertical labels for the page (e.g. music_artist, musician_band). Empty when Linktree exposes none.",
    linkPlatforms:
      "Platforms Linktree detected among the page's links/socials (e.g. Spotify, Instagram). Distinct from socialAccounts URLs.",
    linkCount: "Total link rows including GROUP children.",
    links:
      "Typed outbound links [{title, type, id, url, thumbnail?, parentId?, links?}]. url is always present — null only when Linktree exposes no destination (PRODUCT rows usually resolve shopUrl).",
    type: "On links[]: Linktree link type (CLASSIC, PRODUCT, SPOTIFY_ALBUM, SPOTIFY_SONG, YOUTUBE_VIDEO, SOUNDCLOUD_PLAYLIST, GROUP, …). On socials[]: icon type (INSTAGRAM, TIKTOK, EMAIL_ADDRESS, …).",
    socials:
      "Linktree social icon list [{type, url}] including EMAIL_ADDRESS mailto entries. Prefer top-level email for the address string.",
    socialAccounts:
      "CamelCase HTTP profile URL map for catalog joins (instagram, tiktok, spotify, soundcloud, appleMusic, youtube, website, whatsapp, …). Email/phone are intentionally omitted — use top-level email. Watch URLs under youtube are resolved to the channel via oEmbed when possible.",
    other:
      "Typed Linktree social icons that did not map into socialAccounts{} [{type, url}] (EMAIL_ADDRESS stays in socials[] / top-level email only).",
    website: "Top-level convenience copy of socialAccounts.website when a WEBSITE social is published.",
    url: "On the page: Linktree profile URL. On a link row: outbound destination (PRODUCT may use shopUrl when Linktree leaves url empty).",
  },
  "twitch-profile": {
    platform: "Platform identifier for this response (matches the endpoint's platform).",
    displayName: "Channel display name. Canonical across profile endpoints (prefer over name).",
    handle: "Twitch login. Canonical; login/username kept as deprecated aliases for one release.",
    login: "Deprecated alias of handle — prefer handle.",
    avatar: "Profile image URL. Canonical; profileImage is a deprecated alias for one release.",
    profileImage: "Deprecated alias of avatar — prefer avatar.",
    banner: "Channel banner URL. Canonical; bannerImage is a deprecated alias for one release.",
    bannerImage: "Deprecated alias of banner — prefer banner.",
    bio: "Channel description / about text. Canonical; description is a deprecated alias.",
    description: "Deprecated alias of bio — prefer bio.",
    isLive: "Whether the channel is currently live.",
    stream:
      "Live stream block when isLive — {title, game, gameBoxArtUrl, viewers, startedAt, thumbnail}. null when offline (not an object of nulls).",
    socials:
      "Linked social accounts [{platform, url, title}] from channel.socialMedias and DefaultPanel linkURLs (instagram/x/tiktok/youtube/…). Empty when the channel exposes none.",
    topClips: "Top public clips for the channel (slug, embedUrl, views, thumbnail).",
    schedule:
      "Lean upcoming schedule preview (max 10) — same segment shape as /twitch/user-schedule (id, startedAt/endedAt, isRecurring, canceledUntil, …). Canonical full schedule: GET /v1/twitch/user-schedule.",
    thumbnail:
      "VOD/clip thumbnail URL with Twitch's {width}x{height} placeholders substituted to 320x180 so the URL loads. See thumbnailTemplate for the raw template.",
    thumbnailTemplate:
      "Unsubstituted Twitch thumbnail template (…/{width}x{height}.jpg) when the source used placeholders — pick your own size.",
    embedUrl:
      "Platform embed URL when a real embed id is known. Do not invent from a page/permalink id.",
    game: "Category / game name string (not a GraphQL Game object).",
    gameBoxArtUrl: "Category box art URL (additive media field).",
    animatedPreviewUrl: "VOD storyboard / animated preview strip when Twitch exposes it.",
  },
  "snapchat-user-profile": {
    username: "Snapchat @handle without @. Canonical account identifier (no handle twin).",
    followers: "Subscriber count from Snapchat's public profile (no subscriberCount twin).",
    categoryId: "Snapchat public-profile category string id (e.g. public-profile-category-v3-business-group). Prefer human-readable category.",
    category: "Human-readable category label derived from categoryId (e.g. Business Group).",
    badge: "Snapchat official badge code: 0/absent = none, 1 = official verified. verified is derived from this.",
    verified: "Whether the profile shows Snapchat's official badge (badge === 1).",
    avatar: "Profile picture URL (no profilePictureUrl twin).",
    banner: "Square hero / cover image URL (no squareHeroImageUrl twin).",
    website: "Absolute https website URL (scheme added when Snapchat omits it, e.g. NBA.com → https://NBA.com).",
    createdAt: "Profile creation time as ISO-8601. Prefer this over creationTimestampMs for sorting.",
    creationTimestampMs: "Profile creation time as Unix milliseconds — same instant as createdAt, different representation.",
    highlights:
      "Curated Story Highlight collections (albums with snapList[]) — persistent highlight reels, not Spotlight.",
    spotlightHighlights:
      "Spotlight posts on the profile (short-form public snaps with engagement). Distinct from highlights[] curated albums.",
    highlightId: "Curated highlight id as a plain UUID string — never a protobuf {value} wrapper or Python dict repr.",
    storyTitle: "Highlight title as a plain string (unwrapped from Snapchat's {value} wrapper).",
    mediaType: 'Derived media kind: "image" when snapMediaType is 0, "video" when 1 (or 2). Always present when snapMediaType is known.',
    snapMediaType: "Raw Snapchat enum: 0 = image, 1/2 = video. Prefer mediaType.",
    snapCount: "Number of snaps in snapList for this story/highlight — always equals len(snapList).",
    embeddedTextCaption: "On-screen text burned into the snap when Snapchat exposes it.",
    contextCards: "Attribution cards (sound/lens/etc.) [{type,title,subtitle,url}] when present.",
    hashtags: "Hashtags on the snap or Spotlight item when Snapchat exposes them.",
    lensMetadata: "Lens used on the snap {id,name,creatorName} when present.",
  },
  "twitch-user-videos": {
    broadcaster: "Top-level channel card for this single-channel list (id, username, displayName, url, profileImage, followers, isPartner, isAffiliate). Not repeated on each video.",
    filterBy: "ARCHIVE | HIGHLIGHT | UPLOAD when set; null when omitted (all types — there is no default filter).",
    nextCursor: "Last video id on this page. Pass as cursor for the next page within the first 100 matching videos. Not a raw offset.",
    windowMax: "Always 100 — Twitch anonymous GQL only exposes the first 100 matching videos; deeper history is not available.",
    thumbnail: "VOD thumbnail with {width}x{height} substituted to 320x180. See thumbnailTemplate for the raw template.",
    language: "BCP-47 lowercase (same as twitch/clip and profile recentVideos).",
  },
  "twitch-user-schedule": {
    id: "Stable schedule segment id — use for dedup and change tracking.",
    startedAt: "Segment start (ISO-8601 UTC). Canonical; matches stream.startedAt naming. startAt is a deprecated alias.",
    endedAt: "Segment end (ISO-8601 UTC). Canonical; endAt is a deprecated alias.",
    startAt: "Deprecated alias of startedAt — prefer startedAt.",
    endAt: "Deprecated alias of endedAt — prefer endedAt.",
    isRecurring: "Whether the segment is a weekly recurring series (derived from Twitch repeatEndsAfterCount).",
    isCancelled: "Whether this occurrence is cancelled.",
    canceledUntil: "When set, this occurrence (or the series through this time) will not air — filter these out for calendar integrations. Still present in the list when Twitch returns them.",
    firstOccurrenceAt: "First occurrence of a recurring series when Twitch exposes it.",
    game: "Category / game name string for the segment.",
  },
  "twitch-clip": {
    curator: "Who created/cut the Twitch clip (distinct from the broadcaster channel).",
    channel: "Twitch broadcaster channel object (id, username, followers, isPartner, lastBroadcast). Prefer this over deprecated broadcaster / broadcasterProfileImage.",
    broadcaster: "Deprecated alias of channel.username — prefer channel{}. Kept for back-compat one release.",
    broadcasterProfileImage: "Deprecated alias of channel.profileImage — prefer channel{}. Kept for back-compat one release.",
    language: "BCP-47 language, lowercase (e.g. en, es). Normalized the same way as twitch/profile recentVideos[].language — Twitch's raw clip field is often uppercase.",
    videoUrl: "Unsigned highest-quality source MP4 path (often /nauth/). Does not play by itself — Twitch returns 401 without a signature. Use signedVideoUrl for ready-to-play playback.",
    signedVideoUrl: "Ready-to-play highest-quality URL with ?sig=&token= appended (same shape ScrapeCreators returns as videoURL). Required for current /nauth/ clip CDN paths. Expires with playbackAccessToken.expiresAt.",
    videoQualities: "Available renditions [{quality, frameRate, url, signedUrl}]. frameRate is rounded to 2 decimal places. url is unsigned; signedUrl has ?sig=&token=.",
    frameRate: "Frames per second for a videoQualities row, rounded to 2 decimal places (Twitch returns raw floats like 60.023…). Example: 60.",
    playbackAccessToken: "Parsed playback token — signature, expires (unix), expiresAt (ISO-8601), clipUri (Twitch's reference URI inside the token — often a mid/low rendition, not necessarily videoUrl), clipSlug, deviceId, version, authorization{}. The escaped JSON value string is not returned; use signedVideoUrl / videoQualities[].signedUrl instead of assembling query params yourself.",
    relatedClips: "Other public clips from the same broadcaster [{id,slug,url,title,views,thumbnail,language,…}] — discovery surface ScrapeCreators also ships.",
  },
  "spotify-track": {
    platform: 'Always "spotify" on this endpoint.',
    name: "Track title (song name). Not a profile displayName alias.",
    artists:
      "Credited artists as [{id, uri, name, url}] — chain uri into /spotify/artist.",
    album:
      "Containing album as {id, uri, name, url, releaseDate} — chain uri into /spotify/album.",
    playCount:
      "Lifetime stream count from Spotify web GraphQL (same metric as artist topTracks[].playCount).",
    popularity:
      "Spotify Web API 0–100 popularity when Pathfinder exposes it; often absent — prefer playCount.",
    isrc: "ISRC when Pathfinder exposes it; often absent on getTrack.",
    previewUrl: "30s MP3 preview URL when Spotify exposes one; often absent on getTrack.",
    contentRating:
      "Pathfinder contentRating.label: NONE | EXPLICIT | NINETEEN_PLUS | UNKNOWN. Not a 2-valued twin of explicit — age-gate labels stay here.",
    explicit:
      "Convenience boolean: true only when contentRating is EXPLICIT. NINETEEN_PLUS / UNKNOWN / NONE → false.",
    releaseDate: "Album release date (ISO) when Spotify exposes it on the track payload.",
    mediaType: "Spotify media type (e.g. AUDIO).",
  },
  "spotify-artist": {
    platform: 'Always "spotify" on this endpoint.',
    name: "Artist display name on Spotify. Not a deprecated displayName alias.",
    region: "ISO region/country for a topCities row (listener geography), not a request market.",
    country:
      "ISO country for a topCities listener city (e.g. US). Not a popular-creators feed market.",
    playCount: "Lifetime stream count for a topTracks[] row.",
    albumsHasMore:
      "True when albumsCount > len(albums[]) — overview sample is incomplete; chain into /spotify/album.",
    singlesHasMore:
      "True when singlesCount > len(singles[]) — overview sample is incomplete; chain into /spotify/album.",
  },
  "spotify-album": {
    platform: 'Always "spotify" on this endpoint.',
    name: "Album title. Not a profile displayName alias.",
    artists:
      "Album artists as [{id, uri, name, url}] — chain uri into /spotify/artist.",
    tracks:
      "Album track list from tracksV2 — [{id, trackNumber, discNumber, name, uri, url, durationMs, playCount, explicit, artists}]. id is the uri suffix for joins into /spotify/track.",
    playCount: "Lifetime stream count for a tracks[] row (same GraphQL metric as /spotify/track).",
    releaseDate: "Full album release timestamp (ISO) when Spotify precision is DAY — prefer over releaseYear alone.",
    releaseYear: "Convenience year derived from releaseDate / date.year.",
    explicit: "True if any track contentRating is EXPLICIT; false when no track is EXPLICIT.",
    tracksHasMore: "True when totalTracks exceeds the tracks[] page returned (rare after full pagination).",
    totalTracks: "Album track count from Spotify (matches tracks[] length when the catalog page is complete).",
  },
  "spotify-search": {
    platform: 'Always "spotify" on this endpoint.',
    name: "Result title (track, album, artist, or show name). Not a profile displayName alias.",
    uri: "Canonical Spotify URI (spotify:track:… / album:… / artist:… / show:… / episode:…) — never a bare id.",
    artists:
      "On Pathfinder track/album hits: [{id, uri, name, url}]. Apify fallthrough may still ship name strings.",
    explicit: "Whether the item is marked explicit (from contentRating or Apify isExplicit).",
    contentRating:
      "Pathfinder contentRating.label when present on the search hydrate (NONE | EXPLICIT | NINETEEN_PLUS | UNKNOWN).",
    playCount:
      "Not returned on search — Pathfinder search hydrate omits stream counts. Chain uri into /spotify/track or use album.tracks[].playCount. Absence is not zero.",
    playable:
      "Not returned on search — decorateContextTracks omits playability. Chain uri into /spotify/track. Absence is not false.",
    durationFormatted: "Human duration (m:ss) when known.",
    fetchedAt: "When this search request completed (envelope only — not duplicated on results[]).",
    source: 'Upstream used for this response: "pathfinder" (GraphQL) or "apify" (scraper fallthrough).',
    query: "Echo of the q parameter.",
  },
  "spotify-podcast": {
    platform: 'Always "spotify" on this endpoint.',
    name: "Podcast show title. Not a profile displayName alias.",
    contentRating:
      "Primary Pathfinder label (first of contentRatingLabels). Podcast enum includes EXPLICIT | NINETEEN_PLUS | NOT_FOR_CHILDREN | SPOTIFY_EIGHTEEN_PLUS | UNKNOWN (and NONE on some surfaces).",
    contentRatingLabels: "Full label list from contentRatingV2 when present.",
    explicit: "True only when EXPLICIT is among contentRatingLabels — age-gate labels are not collapsed into this bit.",
    playable: "Whether the show is playable in the current market when Spotify exposes it.",
    rating: "Show rating object {average, totalRatings} — Spotify web GraphQL; not on the free Web API.",
    publisher: "Show publisher {name} — not episode hosts and never stuffed into artists[].",
    showTypes: 'Show type flags when Spotify exposes them (e.g. "SHOW_TYPE_EXCLUSIVE").',
    totalEpisodes: "Episode count for the show when Spotify exposes it.",
  },
  "spotify-podcast-episodes": {
    platform: 'Always "spotify" on this endpoint.',
    name: "Episode title. Not a profile displayName alias.",
    id: "Episode id (same id as in spotify:episode:{id}).",
    contentRating:
      "Pathfinder contentRating.label (NONE | EXPLICIT | NINETEEN_PLUS | UNKNOWN, plus podcast age-gate labels when present).",
    explicit: "True only when contentRating is EXPLICIT.",
    playable: "Whether this episode is playable in the current market.",
    previewUrl: "MP3 preview URL from previewPlayback.audioPreview.cdnUrl when Spotify exposes one.",
    audioUrls: "Additional mp3 preview source URLs from audio.items[].",
    releaseDate: "Full episode release timestamp (ISO, often minute precision) — prefer over releaseYear alone.",
    releaseYear: "Convenience year derived from releaseDate.",
    mediaTypes: 'Media kinds on the episode (e.g. ["AUDIO","VIDEO"]).',
    hasVideo: "True when mediaTypes includes VIDEO.",
    hasTranscripts: "True when Spotify exposes transcript items for the episode.",
    paywallContent: "True when restrictions.paywallContent is set (exclusive/paywalled).",
    showTypes: 'Show-level type flags copied from the parent show (e.g. "SHOW_TYPE_EXCLUSIVE").',
    rating: "On the embedded podcast card: {average, totalRatings}.",
    totalEpisodes: "Archive size from this episodes query (same source as pagination — no intra-response drift).",
    nextCursor: "Offset string for the next page; null when hasMore is false.",
    hasMore: "True when more episodes remain beyond this page.",
  },
  "soundcloud-track": {
    platform: 'Always "soundcloud" on this endpoint.',
    artist:
      "Uploader as {id, handle, name, url, avatar, followers, verified} — chain id/handle into /soundcloud/artist.",
    plays: "Playback count for the track.",
    likes: "Like count for the track.",
    reposts: "Repost count for the track.",
    comments: "Comment count for the track.",
    downloads: "How many times the track was downloaded on SoundCloud (their counter).",
    downloadable:
      "SoundCloud permission flag — the uploader allows downloads. Does not guarantee downloadUrl (public api-v2 often requires OAuth).",
    streamable:
      "SoundCloud permission flag — the track may be streamed. When true we usually mint streamUrl / hlsUrl.",
    streamUrl:
      "Signed progressive MP3 CDN URL when we can mint one from api-v2 transcodings. Expires — see mediaUrlsExpireAt.",
    hlsUrl: "Signed HLS playlist URL when available. Expires — see mediaUrlsExpireAt.",
    downloadUrl:
      "Direct download URL only when SoundCloud exposes a public download without OAuth; omitted otherwise even if downloadable is true.",
    mediaUrlsExpireAt: "ISO expiry for signed streamUrl / hlsUrl CDN links.",
    waveformUrl: "URL of SoundCloud's waveform JSON (peaks), not an audio file.",
    license: "Track license string from SoundCloud (e.g. all-rights-reserved) — reuse-policy signal.",
    publishedAt: "Track created/publish time as ISO-8601.",
  },
  "soundcloud-artist": {
    platform: 'Always "soundcloud" on this endpoint.',
    handle: "Permalink slug in the profile URL (e.g. flume) — prefer this over username for joins.",
    username: "SoundCloud display username (e.g. Flume). May differ in casing from handle.",
    name: "Display name when SoundCloud exposes full_name; otherwise username.",
    verified: "Whether the account is verified. Top-level only (not duplicated under badges).",
    subscriptionTier:
      'Canonical plan: "pro-unlimited" | "pro" | "mid-tier" | "free" — replaces badges.proUnlimited + creatorSubscription.product.id.',
    externalLinks:
      "Profile social/website links from SoundCloud web-profiles [{url, network, title, username}] when published.",
    createdAt:
      "Account created time as ISO-8601 when SoundCloud exposes it on the public api-v2 (often redacted/null).",
    followers: "Follower count.",
    followings: "Number of accounts this artist follows.",
    trackCount: "Public track count.",
    playlistCount: "Public playlist count.",
    likesCount: "Likes count on the profile when SoundCloud exposes it.",
  },
  "soundcloud-artist-tracks": {
    platform: 'Always "soundcloud" on this endpoint.',
    artistId: "SoundCloud numeric artist id — join key for /soundcloud/artist.",
    artistUrl: "Artist profile URL (also on top-level artist.url).",
    artist:
      "Artist card once for the whole page {id,handle,name,url,avatar,followers,verified}. Not repeated on each track.",
    nextCursor:
      "Opaque pagination token. Pass as cursor on the next call. Not a SoundCloud URL — do not edit.",
    tracks:
      "Track rows matching /soundcloud/track shape without per-row artist{} (single-artist list).",
  },
  "kwai-profile": {
    platform: 'Always "kwai" on this endpoint.',
    id: "Kwai opaque profile eid (same value as eid).",
    eid: "Kwai opaque profile eid.",
    bio: "Profile bio when Kwai's public page exposes it.",
    verified: "Whether Kwai shows a verified badge on this profile.",
    verifiedDescription: "Kwai verification label text when present (e.g. Conta Oficial).",
    followers: "Follower count when Kwai exposes a non-stub value.",
    following: "Following count when Kwai exposes a non-stub value (omitted when the web surface stubs it to 1).",
    likedCount: "Total likes received across the creator's posts.",
    postCount: "Public post/video count (same as publicPostCount / videoCount).",
    videoCount: "Alias of postCount — public video/post count for cadence joins.",
    publicPostCount: "Public posts count.",
    privatePostCount: "Private posts count when Kwai exposes it.",
  },
  "facebook-marketplace-search": {
    location:
      "Top-level string echoes the query param. Each listing.location is {name,city,state,countryCode,latitude,longitude} — same keys as Event endpoints.",
    status: 'Listing availability: "available" | "pending" | "sold". Prefer this over isPublished.',
    isSold: "Convenience bool for status === sold.",
    isPending: "Convenience bool for status === pending.",
    isPublished:
      "Whether Facebook still publishes the listing page (their is_live). Not a livestream. Omitted when status is sold/pending — prefer status.",
    isLocal: "true when the listing's city/state matches the search origin (or distanceMiles ≤ radiusMiles when coords exist).",
    shipsOutsideRadius:
      "true when the listing offers shipping and isLocal is false — typical nationwide SHIPPING_ONSITE inventory.",
    distanceMiles: "Approximate miles from search origin when both sides have coordinates (details=true path).",
    priceAmount: "Price in minor units (cents) for exact arithmetic — prefer over float price.",
    photos: "Photo gallery URIs. Omitted on list cards when only the cover exists (use image). Full gallery with details=true.",
    image: "Cover photo URL.",
    deliveryTypes: 'Facebook delivery enums (e.g. IN_PERSON, SHIPPING_ONSITE).',
    seller: "Seller card when Facebook exposes marketplace_listing_seller on the enriched/item path.",
  },
  "facebook-marketplace-item": {
    location:
      "Venue block {name, city, state, countryCode, latitude, longitude} — same keys as Event endpoints. Flat city/state/lat/lng kept one release.",
    status: 'Listing availability: "available" | "pending" | "sold". Sold listings can still be published.',
    isSold: "Convenience bool for status === sold.",
    isPending: "Convenience bool for status === pending.",
    isPublished:
      "Whether Facebook still publishes the listing page (their is_live). Not a livestream — prefer status.",
    priceAmount: "Price in minor units (cents) for exact arithmetic.",
    seller: "Seller {id, name, url, joinedAt, rating} when Facebook exposes marketplace_listing_seller on the public page.",
    photos: "Full photo gallery when the item page exposes it.",
    city: "Listing city from reverse geocode or location text.",
    state: "Listing state/region code when exposed.",
  },
  "kwai-user-posts": {
    platform: 'Always "kwai" on this endpoint.',
    profileUrl: "Canonical Kwai profile URL for the request (https://www.kwai.com/@handle).",
    author:
      "Creator card once for the page {id, username, displayName, avatar, url}. Not repeated on each post.",
    nextCursor:
      "Opaque pagination token within the posts from one profile fetch. Pass as cursor. Null when exhausted.",
    text: 'Post caption when Kwai publishes a real one. Placeholder descriptions ("...") are omitted — not returned as text.',
    transcript:
      "Auto-caption text from Kwai JSON-LD when present (deduped if two tracks were concatenated). Omitted when Kwai does not expose captions — not null.",
    videoUrl: "Signed progressive playback URL (usually mp4). Check videoType; re-fetch before mediaUrlsExpireAt.",
    videoType: 'Playback type: "mp4" (progressive) or "hls" (.m3u8).',
    mediaUrlsExpireAt: "ISO expiry for signed videoUrl / CDN links, parsed from Kwai's tag= query param.",
    thumbnailUrl: "Post cover image URL.",
  },
  "kwai-post": {
    platform: 'Always "kwai" on this endpoint.',
    author: "Post author {id, username, displayName, avatar, url}.",
    text: 'Post caption when Kwai publishes a real one. Placeholder descriptions ("...") are omitted.',
    transcript:
      "Auto-caption text from Kwai JSON-LD when present (deduped). Omitted when Kwai does not expose captions.",
    videoUrl: "Signed progressive playback URL (usually mp4). Check videoType; re-fetch before mediaUrlsExpireAt.",
    videoType: 'Playback type: "mp4" (progressive) or "hls" (.m3u8).',
    mediaUrlsExpireAt: "ISO expiry for signed videoUrl, parsed from Kwai's tag= query param.",
    hashtags: "Hashtag texts without #, parsed from text when present.",
  },
  "tiktok-shop-search": {
    region:
      "Echo of the region query parameter you sent (default US) — the market used for this search. Not a creator country, not AI-inferred, and there is no regionSource on this endpoint.",
    price:
      "Current promotion minimum sale price across SKUs at fetch time (promotion_product_price.min_price). Same rule as Product Details — TikTok may change promos between calls.",
    originalPrice:
      "Pre-discount price when TikTok exposes an origin price or seller deduction; null when there is no promo. Same rule as Product Details.",
    discount: 'Percent off vs originalPrice when a promo exists (e.g. "55%"); null otherwise.',
    rating: "Product star score from the PDP when TikTok exposes one; null when the product has no reviews yet.",
    reviews: "Product review count from the PDP when exposed; null when unknown/zero with no score.",
    sold: "Units sold for this product (product_model.sold_count) — not the shop's aggregate sold.",
    image: "Primary product image URL (TikTok Shop search has no separate thumbnail field).",
    seller: "Seller shop card: id, name, and store url — not a content author.",
  },
  "youtube-search": {
    channel: "YouTube channel object for the result when present.",
    publishedAt:
      "Publish time as ISO-8601 when YouTube exposes an absolute timestamp; approximate when derived from a relative label — see publishedTimeText.",
  },
  "youtube-playlist": {
    channel: "Owning YouTube channel — id, title, handle, url (same shape as sibling list endpoints).",
    thumbnailUrl: "Playlist cover thumbnail from the sidebar when YouTube exposes one.",
    totalVideos: "Full playlist size from the header (not the page length).",
  },
  "youtube-playlist-videos": {
    channel: "Channel object on each video row (uploader), same as channel-videos.",
    publishedAt:
      "Exact ISO-8601 from reel_item_watch when available; publishedTimeText keeps shelf relative labels.",
    nextCursor: "Opaque cursor for the next page; null when hasMore is false.",
    hasMore: "True when nextCursor is present — more videos remain toward totalVideos.",
    timings: "Stage breakdown: path, fetchMs, browseMs, enrichMs, totalMs.",
  },
  "youtube-channel-details": {
    platform: "Platform identifier for this response (matches the endpoint's platform).",
    username: "Bare channel handle without @. Canonical account identifier (no handle twin).",
    displayName: "Channel title. Canonical human-readable name (no name twin).",
    bio: "Channel description. Canonical profile text (no description twin).",
    avatar: "Channel avatar URL. Canonical profile picture (no thumbnailUrl twin).",
    banner:
      "Channel banner when YouTube exposes one. null when none — never a downsized avatar.",
    followers:
      "Subscriber count from YouTube's rounded display text (292K → 292000). Not always exact — see subscriberCountIsApproximate.",
    subscriberCountIsApproximate:
      "True when followers came from a K/M/B compact shelf label.",
    postCount: "Public video count.",
    createdAt:
      "Channel creation date as YYYY-MM-DD (ISO). Display-formatted About labels are not emitted.",
    canonicalUrl: "Preferred public URL — https://www.youtube.com/@handle when known, else /channel/UC….",
    country: "ISO-3166 alpha-2 channel country (e.g. US, IN). Prefer this over countryName for joins.",
    countryName: "English display name for country (e.g. United States). Locale-stable English from our ISO map.",
    viewCount: "Lifetime channel view count when the About panel exposes it (exact integer).",
    tags: "SEO keywords from channelMetadata. Multi-word tags stay one entry (quote-aware parse).",
    links: "About / primary links as {text, url} with absolute https:// URLs.",
    email:
      "Contact email only when the creator published it in description/About text or a mailto link — not from YouTube's CAPTCHA email reveal.",
  },
  "youtube-channel-videos": {
    publishedAt:
      "ISO-8601 when available; approximate from relative labels on list cards — see publishedTimeText.",
  },
  "youtube-channel-shorts": {
    publishedAt:
      "ISO-8601 when available; approximate from relative labels on list cards — see publishedTimeText.",
  },
  "instagram-channel-reels": {
    views:
      "Reach-style video_view_count when distinct from plays; null otherwise. Read viewsSource — never assume views means unique people.",
    viewsSource:
      '"video_view_count" | null. Same honesty pattern as engagementRateBasis.',
    plays:
      "Total play count including replays (video_play_count). Often higher than views. Prefer viewsInstagram for Instagram-only reports.",
  },
  "instagram-trending-reels": {
    cached:
      "true when served from the per-country response cache (4h TTL); false on a live scrape. Billing is flat 2 credits either way.",
    country: "Localized country name used for native geo (e.g. United States).",
    countryCode: "ISO-3166 alpha-2 for the same country (e.g. US). Prefer this for joins.",
    note: "Honesty copy: cache-first vs live scrape, flat 2 credits, single-flight, 110s hard deadline, duplicates expected, ~180d content-age filter, points to reels-search for keyword scrapes.",
    reels: "Video Reels only. Photos / carousels / multi-year Explore resurfaces are never included.",
    "engagement.views":
      "Platform play count when Instagram exposes it; null when withheld. Read viewsSource when present.",
    "engagement.viewsSource":
      'Present only when views is set: "instagram" | "facebook". Omitted when views is null (not a 100%-null key).',
    durationSeconds:
      "Always present on each reel. Float seconds (3dp) when known; null when the source omitted it.",
    caption: "Reel caption. description is not duplicated on this endpoint.",
    "author.url": "Canonical https://www.instagram.com/{username}/ (www + trailing slash).",
    "author.isPrivate": "Whether the account is private. Canonical privacy flag (not private).",
    videoUrlExpiresAt: "ISO expiry parsed from the signed CDN oe= param when present.",
    thumbnailUrlExpiresAt: "ISO expiry for thumbnailUrl when oe= is present.",
  },
  "instagram-profile-search": {
    mode: 'Always "resolve". Instagram keyword / multi-result search is login-gated — there is no "search" mode and no nextCursor on this endpoint.',
    platform: 'Always "instagram" on each users[] row.',
    url: "Canonical profile URL: https://www.instagram.com/{username}/ (www + trailing slash) — join-safe with channel-details / basic-profile.",
    isPrivate: "Whether the account is private. Canonical privacy flag (no separate private alias).",
    avatar:
      "Profile photo URL (HD when available). Canonical across profile endpoints (prefer over profileImage). Signed Instagram CDN — expires; see imageExpiresAt.",
    profileImage:
      "Deprecated alias of avatar for one release — prefer avatar. Signed Instagram CDN; see imageExpiresAt.",
    profileImageHd: "HD profile photo URL when Instagram exposes one; may equal avatar/profileImage.",
    imageExpiresAt:
      "ISO-8601 expiry parsed from the CDN oe= hex timestamp when present. Re-host the image for long-term storage — do not treat the CDN URL as permanent.",
    users: "0 or 1 resolved public profile(s). Not a paginated discovery list.",
  },
  "instagram-reels-search": {
    views:
      "Reach-style video_view_count when distinct from plays; null otherwise. Read viewsSource.",
    viewsSource: '"video_view_count" | null — do not treat views as unique reach without this.',
    plays:
      "Total play count including replays (video_play_count). Often higher than views. Prefer viewsInstagram for Instagram-only reports.",
  },
  "instagram-details": {
    views:
      "Reach-style video_view_count when distinct from plays; null otherwise. Read viewsSource.",
    viewsSource: '"video_view_count" | null.',
    plays: "Total play count including replays when Instagram exposes it; null key kept on videos when unknown.",
  },
  "tiktok-song-details": {
    duration: "Alias of durationSeconds on this endpoint (length in seconds).",
    durationSeconds: "Track length in seconds.",
  },
  "rumble-video-details": {
    channel: "Channel display name (string), e.g. The Dan Bongino Show — not an object.",
    embedUrl:
      "Real Rumble embed URL (/embed/{embedId}/). embedId is often different from the page permalink id — never invent from id alone.",
    embedId: "Rumble's player embed id (may differ from the /v… page id).",
    durationSeconds: "Length in seconds (integer). Canonical with durationText — same pair as channel-videos.",
    durationText: "Human clock duration (e.g. 1:26:25). Not zero-padded HH:MM:SS.",
    "streams[].expiresAt":
      "Null when the progressive URL is unsigned and does not expire (typical here). ISO when a signed CDN query (expire / Expires / e / x-expires) is present.",
    "streams[].quality":
      "From meta.height (e.g. 1080p). Upstream slot keys like 240/1081 are never used — two 1080p bitrates are two rows.",
    "streams[].bitrateKbps": "Progressive bitrate from embedJS meta when present.",
    type: 'Content kind: "video" | "short" | "live".',
    likes: "Rumble upvotes when the vote UI is present; null when unknown (never invent 0).",
    likesIsApproximate:
      "true when likes came from a compact K/M/B display (e.g. 15.5K → 15500); false/omitted when the integer is exact.",
    dislikes: "Rumble downvotes when present; null when unknown.",
    comments: "Public comment count when Rumble exposes it; null when unknown.",
    views: "View count from JSON-LD / page chrome; null when impossible (0 with engagement).",
    streams:
      "Playable mp4/hls rows ({url, type, quality, width, height, bitrateKbps, sizeBytes, expiresAt}). Authoritative — no raw media map.",
    audioStreams: "AAC rows ({url, type: audio/aac, bitrateKbps, …}) — never mixed into streams[].",
    thumbnailTrack: "Timeline sprite strip when present — not a playable video.",
    captions: "Array of {code, language, url} caption tracks (.vtt).",
    isLive: "true while the upload is a livestream; false for VODs.",
  },
  "youtube-transcript": {
    source: 'Always "captions" — YouTube\'s published caption track (not speech-to-text). Pair with /audio-transcript source:"asr".',
    text: "Full caption text — segment texts joined with a single space. Same key as /audio-transcript.",
    segments:
      "Timed cues [{text, startMs, endMs}]. Same shape as /audio-transcript — not a count, not transcriptSegments.",
    startMs: "Cue start in integer milliseconds.",
    endMs: "Cue end in integer milliseconds (always > startMs).",
    requestedLanguage: "Language the caller asked for (null when unspecified).",
    returnedLanguage: "Language of the caption track actually returned.",
    videoId: "YouTube video id parsed from the url.",
    platform: 'Always "youtube" on this endpoint.',
  },
  "youtube-video-details": {
    degraded:
      "true when publishedAt or likeCount could not be read this call (usually watch-page microformat miss). Always present — false on healthy rows. Retry rather than persisting nulls.",
    degradedReason:
      'null when healthy; "partial-extraction" when core fields are missing after retry.',
    timings:
      "Lean fetch telemetry: path (android | watch | android+watch) and watchAttempts.",
    publishedAt:
      "ISO publish time from watch-page playerMicroformatRenderer (ANDROID omits it). null + degraded when the watch fetch failed.",
    likeCount:
      "Like count from the watch-page accessibility label (or InnerTube next fallback). null + degraded when unread.",
    genre: "Category name from playerMicroformatRenderer (e.g. Music).",
    categoryId: "YouTube category id — from the player when present, else mapped from genre.",
    channelHandle: "@handle from microformat ownerProfileUrl.",
    isFamilySafe: "From microformat; null when the watch player was not available.",
  },
  "youtube-audio-transcript": {
    source: 'Always "asr" — Whisper-class speech-to-text on the audio (not YouTube\'s published captions). Pair with /youtube/transcript source:"captions".',
    asrProvider:
      'ASR backend that produced this transcript (e.g. "groq-whisper-large-v3-turbo" or "openai-whisper-1").',
    languageIsDetected:
      "true when language was auto-detected from the audio; false when the language query param was honored.",
    language: 'BCP-47 / ISO speech language code from ASR (e.g. "en"), not a full name like "english".',
    durationSeconds: "Audio length in whole seconds — basis for per-minute billing.",
    segments:
      "Timed speech cues as an array of {text, startMs, endMs}. Not a count — contrast file-transcript family where segments is a number.",
    startMs: "Cue start in integer milliseconds.",
    endMs: "Cue end in integer milliseconds (always > startMs).",
    text: "Full transcript — segment texts joined with a single space. Prefer this over any legacy transcript alias.",
    creditsUsed:
      "Credits billed for this call: ceil(durationSeconds / 60) × 2. Present in data (and echoed on the envelope).",
    videoId: "YouTube video id parsed from the url.",
    platform: 'Always "youtube" on this endpoint.',
  },
  "tiktok-transcript": {
    text: "Full transcript — segment texts joined with a single space. Same key as YouTube/Rumble transcript endpoints.",
    segments: "Timed cues [{text, startMs, endMs}]. Same catalogue shape as /youtube/transcript.",
    source: 'captions (TikTok WebVTT) or whisper (ASR fallback).',
  },
  "instagram-transcript": {
    text: "Full transcript — segment texts joined with a single space. Same key as YouTube/Rumble transcript endpoints.",
    segments: "Timed cues [{text, startMs, endMs}]. Same catalogue shape as /youtube/transcript.",
  },
  "rumble-video-transcript": {
    source: 'Always "captions" — this endpoint parses Rumble\'s published .vtt only (no STT).',
    language: "Caption track code actually returned (e.g. en-auto).",
    languageName: "Human label from the track (e.g. English (auto)).",
    durationSeconds: "Video length in seconds when known (from video-details).",
    segments:
      "Timed cues [{text, startMs, endMs}]. Same shape as /v1/youtube/audio-transcript. Consecutive identical rolling auto-captions are collapsed.",
    startMs: "Cue start in integer milliseconds.",
    endMs: "Cue end in integer milliseconds (always > startMs).",
    text: "Full transcript — segment texts joined with a single space.",
    platform: 'Always "rumble" on this endpoint.',
    id: "Rumble video id (e.g. v7cv2cc).",
  },
  "rumble-comments": {
    publishedAt:
      "ISO-8601 UTC from a.comments-meta-post-time title= (e.g. Friday, July 17, 2026 08:33 AM -04 → minute precision). Relative textContent is never returned. createdAt is not emitted.",
  },
  "rumble-channel-videos": {
    channel: "Top-level: channel slug you queried. Per-video channel is the display name string.",
    embedUrl:
      "Present only when upstream ships a distinct embed id (≠ page id). Omitted otherwise — never invent /embed/{permalink}/.",
    durationSeconds: "Length in seconds (integer). Same pair as video-details.",
    durationText: "Human clock duration (e.g. 1:30:56).",
    type: 'Content kind: "video" | "short" | "live" (from /shorts/ URL or isLive).',
    isLive:
      "Always present. true only when upstream marks the row live; false otherwise (including fresh VODs with 0 views — not omitted).",
    likes: "Upvotes when the channel scrape exposes rumbleVotes; null when unknown.",
    views: "View count for the upload.",
    streams:
      "Lean signed playback rows ({url, type, expiresAt}). expiresAt comes from the JWT exp claim. For quality/height/bitrate/sizeBytes call /v1/rumble/video-details.",
    "streams[].expiresAt":
      "ISO-8601 from the signed playback JWT exp claim (no extra network call).",
  },
  "rumble-search": {
    channel: "Channel display name string when present.",
    channelHandle: "Channel slug from /c/{handle} when present.",
    durationSeconds: "Length in seconds when known. Same pair as video-details / channel-videos.",
    durationText: "Human clock duration when known.",
    type: 'Content kind: "video" | "short" | "live".',
    isLive: "Always present. true only when the search card is marked live; false otherwise.",
    publishedAt: "ISO-8601 UTC (+00:00). Search HTML offsets (e.g. -04:00) are normalized.",
    views:
      "View count when known; null when unknown or impossible (0 with non-zero likes/comments/dislikes).",
    shareUrl: "https://rumble.com/share/{id} when id is known.",
  },
  "linkedin-post-transcript": {
    transcript: "Full LinkedIn post body text (not speech-to-text from a video).",
    language:
      "Always null today — LinkedIn text posts have no speech language. Present so clients share a schema with Whisper transcript endpoints.",
    timingSource:
      'Always "none" on this endpoint today (native and Apify). "captions" is reserved for future cue support — do not branch on it; nothing emits it yet.',
    estimatedReadSeconds: "Whole-transcript reading-time estimate at 200 wpm. Not per-segment duration.",
    transcriptSegments:
      "Paragraph blocks for search/AI chunking. Each has index, wordCount, charStart/charEnd (transcript.slice(charStart,charEnd)===text). start/duration/timestamp omitted when timingSource is none.",
    segments: "Number of paragraph segments in transcriptSegments.",
    wordCount: "Word count of the full transcript (emoji-only tokens count as 0; URLs count as 1).",
    index: "0-based segment order within transcriptSegments.",
    charStart: "Start offset into transcript (transcript.slice(charStart, charEnd) === text).",
    charEnd: "End offset into transcript (exclusive).",
    duration: "Returned only when timingSource is 'captions'.",
    start: "Returned only when timingSource is 'captions'.",
    timestamp: "Returned only when timingSource is 'captions'.",
    author:
      "Post author {name, url, headline?}. headline only when LinkedIn exposes a real job title (not follower counts). url may be derived from /posts/{vanity}_…ugcPost-… when LinkedIn omits it.",
    publishedAt: "ISO-8601 when guest HTML/JSON-LD exposes it (including VideoObject datePublished on ugcPost URLs).",
  },
  "reddit-post-transcript": {
    timingSource:
      'Always "none" today. "captions" is reserved — do not branch on it; nothing emits it yet.',
    estimatedReadSeconds: "Whole-transcript reading-time estimate at 200 wpm. Not per-segment duration.",
    transcriptSegments:
      "Title / body / comment blocks with speaker. index/wordCount/charStart/charEnd for chunking; start/duration/timestamp omitted when timingSource is none.",
    duration: "Returned only when timingSource is 'captions'.",
    start: "Returned only when timingSource is 'captions'.",
    timestamp: "Returned only when timingSource is 'captions'.",
    index: "0-based segment order.",
    charStart: "Start offset into transcript (transcript.slice(charStart, charEnd) === text).",
    charEnd: "End offset into transcript (exclusive).",
    wordCount: "Word count (emoji-only tokens count as 0; URLs count as 1).",
  },
  "twitter-transcript": {
    timingSource:
      'Always "none" today. "captions" is reserved — do not branch on it; nothing emits it yet.',
    estimatedReadSeconds: "Whole-transcript reading-time estimate at 200 wpm. Not per-segment duration.",
    transcriptSegments:
      "Paragraph-split tweet text. index/wordCount/charStart/charEnd for chunking; start/duration/timestamp omitted when timingSource is none.",
    duration: "Returned only when timingSource is 'captions'.",
    start: "Returned only when timingSource is 'captions'.",
    timestamp: "Returned only when timingSource is 'captions'.",
    index: "0-based segment order.",
    charStart: "Start offset into transcript (transcript.slice(charStart, charEnd) === text).",
    charEnd: "End offset into transcript (exclusive).",
    wordCount: "Word count (emoji-only tokens count as 0; URLs count as 1).",
  },
  "truth-social-profile": {
    platform: 'Always "truth_social" on this endpoint.',
    username: "Local username (canonical). Upstream acct matches on reachable public accounts.",
    isPrivate:
      "Follow-approval / locked account (upstream locked). Catalogue name shared with Instagram/Threads.",
    bot: "Whether Truth Social marks the account as a bot — filter before creator metrics.",
    group: "Whether this is a Truth Social group account (not a personal creator).",
    location: "Profile location string when Truth Social exposes one; null when empty.",
    discoverable: "Whether Truth Social marks the account discoverable; null when upstream omits it.",
    lastStatusAt:
      "Last status day from Truth Social, normalized to ISO-8601 UTC midnight (e.g. 2026-08-02T00:00:00.000Z). Upstream often sends YYYY-MM-DD only.",
    fields:
      "Profile label/value rows ({name, value, verifiedAt}). verifiedAt is set when Truth Social confirmed the link; empty array when none.",
    emojis: "Custom emojis in the display name ({shortcode, url, staticUrl}).",
  },
  "truth-social-user-posts": {
    platform: 'Always "truth_social" on this endpoint (posts[].platform).',
    author:
      "Top-level: full profile card (same _normalize_account as /profile). On each post: slim {id, username, displayName, avatar, verified} only — stats live once at the top.",
    text:
      "Plain text from the status HTML. <a href> is replaced by the real URL so Truth Social span soft-wraps do not insert spaces into links.",
    links: "Authoritative http(s) URLs from <a href> attributes (deduped). Prefer this over regex on text.",
    reblog:
      "Nested original status when this row is a boost/repost. Engagement on the wrapper is usually empty — use reblog.engagement and reblog.author for the real post.",
    quote: "Nested quoted status when present (Truth Social quote-truth).",
    quoteId: "Id of the quoted status when present.",
    inReplyToId: "Parent status id when this post is a reply (rare on user-posts — native feed excludes replies).",
    inReplyToAccountId: "Parent author's account id when this post is a reply.",
    inReplyTo: "Nested parent status when Truth Social embeds it.",
    mentions: "Platform mention list [{id,username,acct,url}] — not regex-from-text. mentions[].acct kept for federation shape.",
    tags: "Platform hashtag list [{name,url}] — not regex-from-text.",
    poll: "Poll block {id,expiresAt,expired,multiple,votesCount,votersCount,options[{title,votes}]} when the status is a poll.",
    visibility: 'Mastodon visibility string when set (e.g. "public", "unlisted").',
    spoilerText: "Content warning / CW text when set.",
    sponsored: "Truth Social ad flag when the status payload includes it.",
    pinned: "Whether the status is pinned on the profile when exposed.",
    language:
      "Language code from Truth Social/Mastodon auto-detect — often wrong on short posts (e.g. fy for English). Not a Captapi detection.",
    isPrivate: "Top-level author isPrivate (upstream locked) when the account payload is rich.",
    bot: "Top-level author bot flag when present.",
    group: "Author.group on the top-level card; posts[].group when the status itself is a group post.",
    lastStatusAt:
      "Top-level author's last status time as ISO-8601 UTC (date-only upstream → midnight Z).",
    fields: "Top-level author profile fields ({name, value, verifiedAt}).",
    likes:
      "Favourites count (identical to upstream upvotes_count on Truth Social). Catalogue name — upvotes twin omitted.",
    downvotes:
      "Truth Social downvotes_count (integer, often 0). Not null when upstream sends zero.",
    card: "Link preview card ({url, title, description, image, type, providerName}) when the status has one.",
    externalVideoId:
      "Rumble video id when Truth Social hosts the clip on Rumble — pass to /v1/rumble/video-details.",
    previewUrl: "Media thumbnail URL, or null when Truth Social returns the missing.png placeholder.",
  },
  "truth-social-post": {
    platform: 'Always "truth_social" on this endpoint.',
    text:
      "Plain text from the status HTML with unbroken URLs (href preferred over span-broken visible text).",
    links: "Authoritative http(s) URLs from <a href> attributes (deduped).",
    reblog:
      "Nested original when this status is a boost — use for accurate attribution in monitoring.",
    quote: "Nested quoted status when present.",
    quoteId: "Id of the quoted status when present.",
    inReplyToId: "Parent status id when this is a reply.",
    inReplyToAccountId: "Parent author's account id when this is a reply.",
    inReplyTo: "Nested parent status when Truth Social embeds it.",
    mentions: "Platform mention list [{id,username,acct,url}].",
    tags: "Platform hashtag list [{name,url}].",
    poll: "Poll block when the status is a poll.",
    visibility: 'e.g. "public" / "unlisted" when set.',
    spoilerText: "Content warning text when set.",
    sponsored: "Truth Social ad flag when present.",
    pinned: "Pinned-on-profile flag when present.",
    language:
      "Language code from Truth Social/Mastodon auto-detect — unreliable on short posts. Not Captapi-detected.",
    isPrivate: "Author isPrivate (upstream locked) when the embedded account is rich.",
    bot: "Author bot flag when present.",
    group: "Author group flag, or post-level group when the status itself is a group post.",
    lastStatusAt:
      "Author's last status time as ISO-8601 UTC (date-only upstream → midnight Z).",
    fields: "Author profile fields ({name, value, verifiedAt}) when present.",
    likes:
      "Favourites count (identical to upstream upvotes_count). Catalogue name — upvotes twin omitted.",
    downvotes:
      "Truth Social downvotes_count (integer, often 0). Not null when upstream sends zero.",
    card: "Link preview card when the status has one.",
    externalVideoId:
      "Rumble video id when present — bridge to Captapi's Rumble video-details / comments.",
    previewUrl: "Media thumbnail URL, or null for Truth Social's missing.png placeholder.",
  },
  "youtube-community-posts": {
    likes:
      "Like count as a number when YouTube exposes it — prefer likeCount + likeCountText on this endpoint.",
    images: "Image URLs attached to the community post.",
    channel: "YouTube channel that authored the community post.",
  },
  "youtube-community-post-details": {
    likes:
      "Like count as a number when YouTube exposes it — prefer likeCount + likeCountText on this endpoint.",
    images: "Image URLs attached to the community post.",
  },
  "youtube-channel-streams": {
    durationSeconds: "Live stream or VOD length in seconds when YouTube exposes it.",
  },
  "youtube-video-sponsors": {
    durationSeconds: "Sponsor segment length in seconds (end - start).",
    category:
      'SponsorBlock segment category: "sponsor" | "selfpromo" | "interaction" | "intro" | "outro" | "preview" | "music_offtopic" | "poi_highlight" | "filler".',
  },
  "reddit-subreddit-details": {
    category:
      "Reddit advertiser_category niche label (e.g. Lifestyles). Empty/null when Reddit omits it — not a SponsorBlock enum.",
    createdAt: "When the subreddit was created (ISO-8601 UTC, e.g. 2008-01-26T06:07:54.000Z).",
    members: "Subscriber count (Reddit subscribers).",
    activeUsers:
      "Accounts currently online on the subreddit (Reddit active_user_count). Not weekly unique actives.",
    rules:
      "Moderation rules from /about/rules as {name, description, kind, violationReason, priority}. Always an array.",
    submitText: "Text shown when submitting a post (community posting guidelines) when configured.",
    id: "Stable Reddit fullname (t5_…). Prefer this over name for joins.",
    type: 'Subreddit access type: "public" | "restricted" | "private" | "archived" when Reddit exposes it.',
    nsfw: "Whether Reddit marks the community over-18.",
  },
  "reddit-search": {
    score:
      "Reddit's authoritative post score field (not ups−downs). Public JSON almost always zeros downs; when scoreHidden is true Reddit may return 0 here while upvoteRatio is still set.",
    upvotes:
      "Reddit ups when present (usually equals score). Not a substitute for score when hide_score zeros both.",
    downs: "Downvote count when Reddit exposes it (almost always 0 on public JSON).",
    upvoteRatio: "Upvote ratio 0–1 when Reddit exposes it — useful controversy signal even when score is hidden.",
    scoreHidden:
      "true when Reddit hide_score is set (new posts). score/upvotes may be 0 until the hide window ends.",
    authorFullname: "Stable Reddit account fullname (t2_…). Prefer this over author for joins.",
  },
  "reddit-subreddit-search": {
    score:
      "Reddit's authoritative post score field (not ups−downs). See scoreHidden when score is temporarily zeroed.",
    scoreHidden:
      "true when Reddit hide_score is set (new posts). score/upvotes may be 0 until the hide window ends.",
    authorFullname: "Stable Reddit account fullname (t2_…). Prefer this over author for joins.",
  },
  "reddit-subreddit-posts": {
    score:
      "Reddit's authoritative post score field (not ups−downs). See scoreHidden when score is temporarily zeroed.",
    scoreHidden:
      "true when Reddit hide_score is set (new posts). score/upvotes may be 0 until the hide window ends.",
    authorFullname: "Stable Reddit account fullname (t2_…). Prefer this over author for joins.",
  },
  "bluesky-profile": {
    platform: "Platform identifier for this response (matches the endpoint's platform).",
    id: "Stable account id — Bluesky DID (same value as did).",
    did: "AT Protocol DID. Same as id; kept for Bluesky-native clients.",
    handle: "Bluesky handle (e.g. bsky.app).",
    displayName: "Profile display name. Canonical; name is a deprecated alias for one release.",
    name: "Deprecated alias of displayName — prefer displayName. Removed after one release.",
    bio: "Profile description / bio text.",
    avatar: "Avatar image URL.",
    banner: "Banner image URL.",
    followers: "Follower count.",
    following: "Following count.",
    postCount: "Posts this account has published. Canonical; posts is a deprecated alias for one release.",
    posts: "Deprecated alias of postCount — prefer postCount. Removed after one release.",
    verified:
      "Prefer verifiedStatus / verification on Bluesky — this boolean is a coarse summary when present.",
    verification:
      "verifications[{issuer, issuerHandle, issuerDisplayName, uri, isValid, createdAt}], verifiedStatus, trustedVerifierStatus. Issuer DIDs are resolved so you do not need a second getProfile call.",
    labels:
      "Moderation labels: [{src, uri, cid, val, neg, createdAt, expiresAt}]. src = labeler DID; val = label value; neg = negation; expiresAt when the label expires.",
    associated:
      "Association counts so you can tell feed/labeler service accounts from people: lists, feedgens, starterPacks, labeler, plus chat{allowIncoming, allowGroupInvites} and activitySubscription{allowSubscriptions} when present.",
    feedgens: "Number of custom feeds (feed generators) this account publishes.",
    labeler: "Whether this account is a Bluesky labeler (moderation service).",
    createdAt: "When the account was created (ISO-8601).",
    indexedAt:
      "When the Bluesky AppView last indexed this profile record (ISO-8601). Not last activity — createdAt is account age; use user-posts for recent posts.",
    pinnedPost:
      "Post the account chose to feature: {uri, cid, rkey} from profileViewDetailed. Omitted when none.",
    joinedViaStarterPack:
      "Starter pack used at join when present: {uri, cid, name, creator{did, handle, displayName}}.",
  },
  "bluesky-user-posts": {
    platform: "Platform identifier for this response (matches the endpoint's platform).",
    handle: "The actor whose author feed you requested.",
    uri: "AT URI of the post (at://did…/app.bsky.feed.post/rkey).",
    url: "bsky.app permalink for the post.",
    cid: "Content ID (CID) of this post record — stable content-addressed hash.",
    text: "Post text body. Long URLs may be truncated here — use links[] from facets for the full URI.",
    publishedAt:
      "When the original post was created (record createdAt). Not repost time — feed order uses repostedAt for isRepost rows.",
    indexedAt:
      "When the AppView indexed this post. For reposts, feed order follows repostedAt — not this field.",
    author:
      "Author of the underlying post: {handle, displayName, did, avatar}. On reposts this is the original author — not the profile you queried. For verification/labels use post-details.",
    isRepost:
      "true when this feed row is a repost (reasonRepost). Engagement and author belong to the original post — use repostedBy for the account that boosted it.",
    repostedBy:
      "Who reposted: {handle, displayName, did, avatar}. Present only when isRepost is true (usually the requested handle).",
    repostedAt:
      "When the repost happened (ISO-8601). Present only when isRepost is true. This is the sort key for that row in the author feed.",
    isReply: "true when parentUri is set (this post replies to another).",
    parentUri: "AT URI of the immediate parent when this is a reply.",
    rootUri: "AT URI of the thread root when this is a reply.",
    links:
      "Outbound URLs from rich-text facets [{url, text}]. url is the full target — text may be Bluesky's truncated display form.",
    mentions: "Mention facets [{did, handle, text}]. did is the stable identity.",
    hashtags: "Hashtag strings from facets (no # prefix) — not regex over text.",
    langs: "Language tags from the post record (e.g. en).",
    labels: "Moderation labels on the post [{src, uri, cid, val, neg, createdAt, expiresAt}].",
    engagement:
      "Engagement on the underlying post: {likes, reposts, replies, quotes}. On isRepost rows these counts are the original author's — do not average them onto the requested handle without filtering. No view count on Bluesky.",
    embed:
      "Normalized embed: type external {url,title,description,thumb} | images {images[{url,alt}]} | video {playlist,thumbnail,alt} | quote {uri,url,text,author,cid,publishedAt}. Never a raw lexicon NSID.",
    nextCursor:
      "Opaque AppView cursor for the next page. Pass it through unchanged — do not build a cursor from publishedAt (feed order includes repost time).",
    hasMore: "true when nextCursor is present.",
    filter: "Echo of the filter query param when set (Bluesky getAuthorFeed filter).",
    includeReposts: "Echo of includeReposts (default true).",
  },
  "bluesky-post-details": {
    platform: "Platform identifier for this response (matches the endpoint's platform).",
    uri: "AT URI of the post (at://did…/app.bsky.feed.post/rkey).",
    url: "bsky.app permalink for the post.",
    cid: "Content ID (CID) of this post record — stable content-addressed hash.",
    text: "Post text body. Long URLs may be truncated here — prefer links[].url from facets.",
    publishedAt: "When the post record was created (ISO-8601).",
    indexedAt: "When the AppView indexed this post (ISO-8601).",
    author:
      "Rich author card: {handle, displayName, did, avatar, createdAt, labels[], verification{}, verified}. labels may include !no-unauthenticated (account opts out of unauthenticated visibility).",
    isReply: "true when this post is a reply (parentUri set).",
    parentUri: "AT URI of the immediate parent post when isReply.",
    rootUri: "AT URI of the thread root when isReply.",
    links:
      "Facet-derived outbound links [{url, text}]. url is the real target; text is the (possibly truncated) display slice.",
    mentions: "Facet mentions [{did, handle, text}] — did is authoritative.",
    hashtags: "Facet hashtags without #.",
    langs: "Language tags on the post record (e.g. en).",
    labels:
      "Post-level moderation labels [{src, uri, cid, val, neg, createdAt, expiresAt}] (nsfw/spam/etc. when applied).",
    engagement:
      "Engagement on this post: {likes, reposts, replies, quotes}. replies is the count; reply bodies live in replies[]. No view metric on Bluesky.",
    embed:
      "Normalized embed: type external | images | video | quote (same namespace as user-posts).",
    replies:
      "Nested reply tree from getPostThread. Each node matches the post shape (rich author, facets, engagement) plus its own replies[]. Depth controlled by the depth query param.",
    depth: "Echo of the depth query param used for this response.",
  },
  "facebook-ad-library-search": {
    status: "Ad delivery filter/status: ACTIVE, INACTIVE, or ALL.",
    videos: "Typed video assets ({url, sdUrl, previewUrl}). media[] remains the flat URL list.",
    images: "Typed image assets when Meta exposes them ({url, resizedUrl}).",
    destinationUrl: "Click-through / landing URL from the ad creative.",
  },
  "facebook-ad-library-ad-details": {
    videos: "Typed video assets ({url, sdUrl, previewUrl}). media[] remains the flat URL list.",
    images: "Typed image assets when Meta exposes them ({url, resizedUrl}).",
    destinationUrl: "Click-through / landing URL from the ad creative.",
  },
  "facebook-event-details": {
    startDate:
      "Event start as ISO-8601 with the host timezone offset (e.g. 2026-08-19T19:00:00-05:00). Calendar day matches startTime — not UTC midnight.",
    endDate:
      "Event end as ISO-8601 with the same host timezone offset when Facebook exposes end_timestamp.",
    timezone: "IANA timezone inferred from the startTime abbreviation (e.g. America/Chicago for CDT).",
    startTime: "Facebook's human-readable local schedule sentence (includes TZ abbrev).",
    duration: "Human duration from Facebook (e.g. 1 hr 30 min) or derived from start/end.",
    durationSeconds: "Duration in seconds when start and end timestamps are known.",
    eventType:
      "Discovery category label when present (e.g. Comedy). Never a Facebook visibility constant — see visibility.",
    visibility:
      "Lowercase audience enum derived from Facebook's *_TYPE (public|private|friends|group|community). Null when unknown.",
    isPast: "Whether the event start is in the past (Relay is_past, else derived from startDate vs now).",
    usersGoing: "Public going count when Facebook exposes it on the logged-out hydrate.",
    usersInterested: "Public interested count when Facebook exposes it on the logged-out hydrate.",
    usersResponded:
      "Sum of usersGoing + usersInterested when either is present. Not Facebook's friends-who-responded facepile.",
    verified: "Whether the host Page/profile shows a verified badge (on organizers[].verified).",
    externalLinks: "Outbound links attached to the event when Facebook exposes them (often empty).",
    organizers: "Host Page/profile rows: {id, name, url, verified}. Prefer organizers[].id for joins.",
    address: "Street / one-line address when distinct from location.name. Null when it would only echo city.",
  },
  "facebook-event-search": {
    startDate:
      "Event start as ISO-8601 with the host timezone offset (e.g. 2026-07-27T19:45:00-05:00). Calendar day matches startTime — not UTC midnight.",
    endDate: "Event end as ISO-8601 with the same host timezone offset when available (null when unknown).",
    timezone: "IANA timezone from venue coords or the startTime abbreviation (e.g. America/Chicago for CDT).",
    startTime: "Absolute local schedule sentence that always includes the year — never relative labels like Happening now.",
    duration: "Human duration when start/end are known; null otherwise.",
    eventType: "Discovery category (e.g. Comedy). Null when unknown — never PUBLIC_TYPE.",
    visibility: "Lowercase audience enum (public|private|friends|…). Null when unknown.",
    isPast: "Whether the event start is in the past.",
    usersGoing: "Public going count when Facebook exposes it.",
    usersInterested: "Public interested count when Facebook exposes it.",
    location: "Venue block {name, city, latitude, longitude, countryCode} — all five keys always.",
    source: "native or extended (fetch path). Also mirrored in X-Captapi-Source. Not a price change — success is always flat 2 credits.",
  },
  "facebook-profile-events": {
    startDate:
      "Event start as ISO-8601 with host timezone offset. Year is resolved for yearless cards (Tue, Aug 4 at 8:00 PM EDT → 2026-08-04T20:00:00-04:00).",
    endDate: "Event end as ISO-8601 with host timezone offset when available; null on thin profile cards.",
    timezone: "IANA timezone from the startTime abbreviation (e.g. America/New_York for EDT).",
    startTime: "Local schedule sentence that always includes the year (built from startDate when the card omits it).",
    duration: "Human duration when start/end are known; null otherwise.",
    eventType: "Discovery category when known; null on thin cards — never PUBLIC_TYPE.",
    visibility: "Lowercase audience enum (public|private|friends|…) from Facebook's *_TYPE.",
    isPast: "Whether the event start is in the past (derived from startDate).",
    address: "Street when distinct from location.name; null when it would only duplicate the venue.",
    source: "native or extended (fetch path). Also mirrored in X-Captapi-Source. Not a price change — success is always flat 2 credits.",
  },
  "pinterest-board": {
    destinationUrl: "Outbound link on the pin (product/article URL). Not an ad creative field.",
    saves: "How many times the pin was saved/repinned — Pinterest's primary engagement metric.",
    imageOriginal:
      "Full-resolution pin image via i.pinimg.com/originals/… (derived when Pinterest only ships sized CDN URLs).",
    image: "Display image URL (typically 564x or 736x CDN size). Prefer imageOriginal for archival/analysis.",
    author:
      "Top-level: full pinner card (username, displayName, followers). Per-pin author is slim (username/displayName) to avoid repeating followers on every row.",
    title: "Pin title when Pinterest exposes it on the board hydrate (often null on promotional pins).",
  },
  "pinterest-pin-details": {
    destinationUrl: "Outbound link on the pin (product/article URL). Not an ad creative field.",
    saves: "How many times the pin was saved/repinned — Pinterest's primary engagement metric.",
    imageOriginal:
      "Full-resolution pin image via i.pinimg.com/originals/… when available under images.originals.",
  },
  "pinterest-user-pins": {
    destinationUrl: "Outbound link on the pin (product/article URL). Not an ad creative field.",
    saves: "How many times the pin was saved/repinned — Pinterest's primary engagement metric.",
  },
  "pinterest-user-boards": {
    followers:
      "Board-scoped follower count when available. Null on the logged-out hydrate — Pinterest's board.follower_count there is account-scale (same value on every board) and is never returned.",
    coverImage:
      "Board cover image URL. Prefers Pinterest's image_cover_hd_url (474x) when present; may fall back to 200x150.",
    createdAt: "Board creation time as ISO-8601 UTC (normalized from Pinterest's RFC 2822).",
    privacy: "Board privacy: public or secret when exposed.",
    sectionCount: "Number of sections on the board.",
    pinCount: "Number of pins on the board.",
    description: "Board description text when the owner set one (often empty).",
    owner: "Board owner card: username + displayName.",
  },
  "linkedin-company": {
    type: 'Entity discriminator — always "company". Organization legal/type label is organizationType.',
    industry: "LinkedIn industry from the About section (e.g. Software Development).",
    employees:
      "Featured employees [{name,title,link}] when LinkedIn exposes them. Guest pages usually return []. Not the headcount — use employeeCount.",
    employeeCount: "LinkedIn headcount estimate for the company.",
    size: 'Company size band from About (e.g. "10,001+ employees").',
    founded: "Founding year when present on the About section.",
    organizationType: 'About "Type" (e.g. Public Company). Distinct from type:"company".',
    specialties: "About specialties list.",
    similarPages: "Companies LinkedIn lists under Similar pages — discovery graph ({name,link,image}).",
    funding:
      "Funding rounds/investors when upstream exposes them; null on guest HTML / empty Apify funding blobs. ScrapeCreators often fills this.",
    slogan: "Company tagline.",
    coverImage: "Company cover/background image URL.",
    location: "Structured HQ {city,state,country}. headquarters is the joined string.",
  },
  "linkedin-company-posts": {
    engagement:
      "Always keyed {likes,comments,reposts}. Counts from permalink hydrate when homepage JSON-LD omits them; null only when LinkedIn omits that metric.",
    likes: "Total reactions on the post (LinkedIn's public reaction count).",
    comments: "Public comment count.",
    reposts: "Repost/share count when LinkedIn exposes it (often null on guest hydrates).",
  },
  "tiktok-shop-products": {
    platform: 'Always "tiktok_shop" on this endpoint (not youtube/instagram).',
    shopInfo:
      "Store rollup from the same SSR call as products: sold, formatSold, reviews, followers, rating, productCount, videoCount, isOfficial, identityLabel, region, logo, storeScores[].",
    sold: "Units sold (product row) or lifetime shop sold (inside shopInfo).",
    rating: "Star rating (product or shop).",
    reviews: "Review count (product or shop).",
    savings: 'Human discount copy from TikTok (e.g. "Saving $4.02").',
    discount: 'Percent off string (e.g. "21%").',
    slug: "SEO slug from seo_url.slug (also embedded in the product URL).",
    storeScores: "TikTok store sub-scores [{score, scorePercentage, type}].",
    isOfficial: 'true when identityLabel indicates an official shop (e.g. "OFFICIAL SHOP").',
    formatSold: 'Compact shop sold string from TikTok (e.g. "5.6M").',
    region:
      "Echo of the region query parameter you sent (default US) — the market used for this catalog fetch. Not a creator country, not AI-inferred, and there is no regionSource here.",
    price:
      "Current promotion minimum sale price across SKUs at fetch time — same canonical rule as Shop Search and Product Details.",
  },
  "pinterest-search": {
    destinationUrl: "Outbound link on the pin (product/article URL). Not an ad creative field.",
    saves: "How many times the pin was saved/repinned — Pinterest's primary engagement metric.",
  },
  "linkedin-ad-library-search-ads": {
    destinationUrl: "Click-through / landing URL from the ad creative.",
  },
  "tiktok-ad-library-search": {
    candidatesScanned:
      "Always present (integer). SERP pool size before local whole-word filtering.",
    filteredOut: "Rows dropped by the local whole-word keyword filter.",
    literalMatches:
      "Present when q is set. Count of rows that passed local whole-word matching.",
    truncated:
      "true when totalReturned < limit and upstream still had more pages. Always false when empty.",
    matchedFrom:
      "Per-ad only: string[] of fields that matched (text, headline, cta, landingUrl, advertiser.name). Never the envelope scan count.",
    library: 'Surface discriminator — "dsa" for Commercial Content Library (platform stays tiktok).',
    media: "Array of {url,type,width,height,durationSeconds,expiresAt?} — expiresAt only when the signed CDN URL encodes one.",
    match: 'Echo of the match query param ("any" or "all").',
    matchBasis: 'How keywords were applied — "any", "all", or "none".',
  },
  "tiktok-ad-library-top-ads": {
    candidatesScanned:
      "Always present (integer). Row count after industry/objective/format filters, before local keyword filtering. With q set and totalReturned=0, candidatesScanned>0 means the leaderboard had rows and the whole-word filter dropped them.",
    filteredOut: "Rows dropped by the local whole-word keyword filter.",
    literalMatches:
      "Present only when q is set. Count of rows that passed local whole-word matching.",
    match: 'Echo of the match query param ("any" or "all").',
    matchBasis:
      'any|all when q was set (literal filter applied); none when q was omitted. Never creative_center — soft leaderboard echoes were removed.',
    truncated:
      "true only when a non-empty page has totalReturned < limit while Creative Center pagination still had more pages. Empty after filter → false.",
    matchedFrom:
      "Per-ad only, and only when q is set: string[] of fields that matched (title, brandName, industry, tags, objective). Never the envelope scan count.",
    advertiser:
      "Grouping axis {id,name}. id may be brand_id or Spark author uid; null when Creative Center withholds it. name mirrors brandName (Spark falls back to creator nickname).",
    brandName:
      'Same as advertiser.name when present. Spark Ads with "Not Mention" fall back to the organic creator. Omitted only when no name exists.',
    likesIsApproximate:
      "true when likes looks like a rounded Creative Center bucket (e.g. multiples of 1k/100k); false when the integer looks exact.",
    "video.urlHd":
      "Present only when a distinct HD rendition exists (different URL from video.url). Omitted when null — not a dead always-null field.",
    ctrTier:
      "Present only when Creative Center ships a CTR bucket. Omitted (not null) when withheld.",
    isSparkAd:
      "Present only when upstream sets Spark/non-Spark. Omitted when withheld. adFormat is omitted when it would only repeat Spark/Non-Spark.",
    countries:
      "Omitted when it only echoes the request country filter (already at response root). Kept for multi-country targeting.",
  },
  "tiktok-shop-product-details": {
    platform: "Always tiktok_shop for this endpoint.",
    region:
      "Echo of the region query parameter (default US) used for Apify fallback market selection. Native SSR follows the product URL's market. Not a creator country and not AI-inferred.",
    price:
      "Current promotion minimum sale price across SKUs (promotion_product_price.min_price.sale_price_decimal). Canonical across Shop Search / Shop Products / Product Details — point-in-time; TikTok promos can move between calls.",
    images: "Product gallery image URLs from the PDP (not a single OG thumbnail).",
    originalPrice: "List / pre-discount price when TikTok exposes a seller deduction or origin price; null when the PDP has no promo.",
    discount: 'Percent off string (e.g. "13%") when originalPrice > price; null otherwise.',
    savings: 'Human discount copy (e.g. "Saving $3.60") when a promo exists.',
    skus: "Per-variant rows: id, stock, price, warehouseId, purchaseLimit, saleProps[{propName,propValue}].",
    saleProperties: "Variant axes for the product (e.g. Phone Models / Color) with value ids.",
    categories: "Category tree crumbs [{id, name}] from TikTok's recommended_categories.",
    seller: "Shop card: id, name, store url, rating, productCount, logo — not the product title.",
    relatedVideos: "Affiliate / related creator videos when upstream provides them (often absent from US PDP SSR).",
    descVideo: "Product description video URL + durationMs when TikTok embeds one.",
    stock: "Sum of available_quantity across skus[] (use skus[].stock for per-variant inventory).",
  },
  "tiktok-shop-product-reviews": {
    rating: "This review's star score (1–5). Not the product's average rating — that lives on Product Details / Shop Search as products[].rating.",
    country: "ISO country of the reviewer when TikTok exposes it (e.g. US). Not a request-market param and not related to popular-creators feeds.",
    createdAt: "When the review was posted, UTC ISO-8601 with milliseconds and Z (e.g. 2026-05-15T21:49:56.991Z).",
    verifiedPurchase: "true when TikTok marks the reviewer as a verified buyer.",
    sku: "Variant / SKU label the buyer selected (e.g. \"Thicc 16oz | Ice Cream\").",
    images: "Photo URLs the reviewer attached to this review (empty/omitted when none).",
    author: "Reviewer display — often TikTok-masked (e.g. \"C**e\"). Full handle/avatar/profile URL are usually unavailable on public Shop reviews.",
    text: "Review body text.",
  },
  "tiktok-shop-user-showcase": {
    sold: "Units sold for the showcased product (from PDP hydrate).",
    rating: "Product star score when the PDP exposes one; null otherwise.",
    reviews: "Product review count when exposed; null otherwise.",
    originalPrice: "Pre-discount price when a promo exists — same canonical rule as Shop Search / Product Details.",
    discount: "Percent off vs originalPrice when a promo exists.",
    seller: "Seller shop card {id,name,url} — id from the showcase shelf, name/url from PDP hydrate when available.",
    commissionRate: "Affiliate commission when upstream exposes it; omitted when the public showcase payload has no rate.",
    slug: "SEO slug from the hydrated PDP URL when present.",
    image: "Product image from the showcase shelf (or PDP when the shelf omits one).",
  },
  "account-balance": {
    monthlyQuota: "Plan monthly subscription credit allotment (e.g. free=100).",
    subscriptionCredits: "Remaining subscription credits (reset at quotaResetsAt / subscriptionRenewsAt).",
    topupCredits: "Remaining purchased top-up credits (never expire).",
    totalCredits: "subscriptionCredits + topupCredits.",
    usedThisMonth: "Sum of creditsUsed on requests since the current billing window (or last 30 days).",
    quotaResetsAt: "When subscription credits renew — same value as subscriptionRenewsAt when set.",
    keyName: "Display name of the calling API key when set; null for session JWT calls.",
    rateLimitPerMinute: "Plan RPM ceiling enforced by Captapi (not GitHub/etc.).",
    rateLimitRemaining: "Always null on this endpoint — RPM remaining is per Redis window, not snapshotted here.",
    monthly_quota: "Deprecated snake_case alias of monthlyQuota — prefer camelCase.",
    subscription_credits: "Deprecated snake_case alias of subscriptionCredits.",
    topup_credits: "Deprecated snake_case alias of topupCredits.",
    total_credits: "Deprecated snake_case alias of totalCredits.",
    subscription_renews_at: "Deprecated snake_case alias of subscriptionRenewsAt.",
  },
  "video-transcript": {
    durationSeconds: "Audio duration in seconds from Whisper — basis for per-minute billing.",
    duration: "Alias of durationSeconds (same number) for bill verification.",
    creditsCharged: "Credits billed for this call: ceil(durationSeconds/60), minimum 1.",
    language: "Detected (or hinted) speech language from Whisper.",
    noSpeech: "true when Whisper found no trustworthy speech (empty transcript; still billed for duration).",
    wordCount: "Word count of the returned transcript (matches the text — not a truncated preview).",
    segments: "Number of timed segments in transcriptSegments.",
  },
  "video-summarize": {
    summary: "AI executive summary (GPT-4o-mini). Length scales with the transcript — short clips may be one paragraph; longer audio aims for 2–3.",
    keyPoints: "Bullet takeaways (typically 4–8 on longer audio; fewer on short clips).",
    transcript: "Full Whisper transcript of the upload — always present on success (not summary-only).",
    durationSeconds: "Audio duration in seconds from Whisper — basis for the per-minute part of billing.",
    duration: "Alias of durationSeconds (same number) for bill verification.",
    creditsCharged: "Credits billed: ceil(durationSeconds/60) + 1 for the summary.",
    language: "Detected (or hinted) speech language from Whisper.",
    noSpeech: "Should be false on success — empty speech returns HTTP 422 instead.",
  },
  "account-request-history": {
    requestId:
      "UUID of the logged call — same value as the response envelope requestId / x-captapi-request-id header. Use when contacting support.",
    resource:
      "Logged resource identifier: a public URL when the call had one, otherwise an internal cache key (e.g. instagram_user:handle).",
    resourceUrl: "Deprecated alias of resource (not always a URL). Prefer resource.",
    creditsUsed: "Credits charged for that call (0 on cache hits).",
    cacheHit: "true when the call was served from the 24h shared cache (0 credits).",
    filters: "Echo of the query filters applied to this page of results.",
  },
  "analytics-compare": {
    status: "Row status: ok when the URL resolved, error when it failed.",
    results:
      "Array of analytics/post objects (plus status). Same metrics{}, author{}, and ISO publishedAt as Post Analytics.",
    failed: "Unresolved URLs as {url, platform, reason}.",
    publishedAt: "Full ISO-8601 UTC with milliseconds (same as analytics/post) — never date-only.",
    commentsIsApproximate:
      "true when comments came from a compact UI count (e.g. YouTube \"2.4M\"). Null when comments is null.",
    interactionsIsApproximate:
      "true when any approximate numerator contributed to interactions (inherits commentsIsApproximate).",
    engagementRateBasis: 'Always "interactions/views" on this endpoint — not TikTok popular-creators percent.',
  },
  "analytics-post": {
    commentsIsApproximate:
      "true when comments came from a compact UI count (e.g. YouTube \"2.4M\"). The integer is still returned, but treat it as ± rounding error — not unit-precise.",
    interactionsIsApproximate:
      "true when interactions (and thus engagementRate) inherit uncertainty from an approximate numerator such as comments.",
    viewsIsApproximate: "true when views came from a compact UI count. Usually false on YouTube watch pages with exact viewCount.",
    engagementRateBasis: 'Always "interactions/views" (ratio). Do not compare to popular-creators without reading that field\'s basis.',
    username: "Author @handle when known — never the display name.",
    shares: "Null when the platform does not expose public share counts (e.g. YouTube).",
    saves: "Null when the platform does not expose public save/bookmark counts (e.g. YouTube).",
  },
};

/** Description for a single field, preferring the curated dictionary. */
function describeField(name: string, value: unknown, slug?: string): string {
  if (RAW_KEYS.has(name)) return FIELD_DESCS.raw;
  // Slug overrides always win — shared dictionary text must not leak across platforms.
  const slugDesc = slug ? SLUG_FIELD_DESCS[slug]?.[name] : undefined;
  if (slugDesc) return slugDesc;
  if (isScalarValue(value)) {
    if (FIELD_DESCS[name]) return FIELD_DESCS[name];
    if (typeof value === "string" && value.startsWith("http"))
      return `${humanizeField(name)} URL.`;
    return `${humanizeField(name)}.${exampleHint(value)}`;
  }
  if (Array.isArray(value)) {
    const first = value.find((x) => x && typeof x === "object" && !Array.isArray(x)) as
      | Record<string, unknown>
      | undefined;
    if (first) {
      return FIELD_DESCS[name] ?? `Array of objects with ${Object.keys(first).slice(0, 6).join(", ")}.`;
    }
    return FIELD_DESCS[name] ?? `${humanizeField(name)} (array).`;
  }
  if (value && typeof value === "object") {
    const keys = Object.keys(value as Record<string, unknown>);
    if (keys.length === 0) return FIELD_DESCS[name] ?? `${humanizeField(name)}.`;
    return FIELD_DESCS[name] ?? `Object with ${keys.slice(0, 6).join(", ")}.`;
  }
  return FIELD_DESCS[name] ?? `${humanizeField(name)}.`;
}

function fieldsFromObject(obj: Record<string, unknown>, slug?: string): ResponseField[] {
  return Object.entries(obj).map(([k, v]) => ({ name: k, desc: describeField(k, v, slug) }));
}

/** Foreign platform tokens that must not appear in another platform's field notes. */
const FIELD_DESC_PLATFORM_TOKENS: { re: RegExp; platform: PlatformId }[] = [
  { re: /\bKick\b/i, platform: "kick" },
  { re: /\bTwitch\b/i, platform: "twitch" },
  { re: /\bYouTube\b/i, platform: "youtube" },
  { re: /\bTikTok\b/i, platform: "tiktok" },
  { re: /\bBluesky\b/i, platform: "bluesky" },
  { re: /\bInstagram\b/i, platform: "instagram" },
  { re: /\bSpotify\b/i, platform: "spotify" },
  { re: /\bSoundCloud\b/i, platform: "soundcloud" },
];

/**
 * Keys where a shared FIELD_DESCS string has already been proven to leak the
 * wrong platform into unrelated endpoint pages (Kick clip → twitter/community, …).
 */
const FIELD_DESC_STICKY_KEYS = new Set([
  "creator",
  "curator",
  "videos",
  "likes",
  "verified",
  "duration",
  "durationSeconds",
  "durationText",
  "images",
  "status",
  "region",
  "mediaType",
  "channel",
  "category",
  "categoryId",
  "views",
  "plays",
  "isLive",
  "publishedAt",
  "embedUrl",
  "streams",
  "streamQualities",
  "locked",
  "bot",
  "group",
  "fields",
  "lastStatusAt",
  "videoUrl",
  "videoType",
  "hlsUrl",
  "email",
  "socialAccounts",
  "socials",
  "verticals",
  "linkPlatforms",
  "type",
]);

/**
 * Fail when a sticky field's rendered description names a different platform
 * than the endpoint (shared dictionary bleed).
 */
/** Pages that intentionally name other platforms (link-in-bio / creator graph). */
const FIELD_DESC_CROSS_PLATFORM_HOSTS = new Set<PlatformId>([
  "linktree",
  "pillar",
  "linkbio",
  "linkme",
  "komi",
]);

export function lintFieldDescPlatformBleed(): string[] {
  const errors: string[] = [];
  for (const ep of ALL_ENDPOINTS) {
    if (ep.platform === "account" || ep.platform === "utilities") continue;
    if (FIELD_DESC_CROSS_PLATFORM_HOSTS.has(ep.platform)) continue;
    const groups = responseStructure(ep);
    for (const group of groups) {
      for (const field of group.fields) {
        if (!FIELD_DESC_STICKY_KEYS.has(field.name)) continue;
        for (const tok of FIELD_DESC_PLATFORM_TOKENS) {
          if (!tok.re.test(field.desc)) continue;
          if (tok.platform === ep.platform) continue;
          if (
            (ep.platform === "facebook" ||
              ep.platform === "instagram" ||
              ep.platform === "facebook_ad_library" ||
              ep.platform === "tiktok_ad_library" ||
              ep.platform === "tiktok_shop") &&
            (tok.platform === "facebook" || tok.platform === "instagram" || tok.platform === "tiktok")
          ) {
            continue;
          }
          errors.push(
            `${ep.slug}.${field.name}: description mentions ${tok.platform} but endpoint is ${ep.platform} — "${field.desc.slice(0, 140)}"`,
          );
        }
        // Deterministic request echoes must never inherit profile-region AI copy.
        if (
          field.name === "region" &&
          ep.platform === "tiktok_shop" &&
          ((/\bAI-inferred\b/i.test(field.desc) && !/not\s+AI-inferred/i.test(field.desc)) ||
            (/\bregionSource\b/i.test(field.desc) && !/no regionSource/i.test(field.desc)) ||
            (/creator'?s country/i.test(field.desc) && !/not a creator/i.test(field.desc)))
        ) {
          errors.push(
            `${ep.slug}.region: TikTok Shop region must describe the request market echo, not profile-region AI inference — "${field.desc.slice(0, 140)}"`,
          );
        }
      }
    }
  }
  return errors;
}

function _collectExampleKeys(value: unknown, out: Set<string>): void {
  if (!value || typeof value !== "object") return;
  if (Array.isArray(value)) {
    for (const item of value) _collectExampleKeys(item, out);
    return;
  }
  for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
    out.add(k);
    _collectExampleKeys(v, out);
  }
}

/**
 * Explicit absence claims in platformLimits. The field must be the subject or
 * object of the claim — not merely mentioned on the same line (e.g. "fetchedAt
 * is envelope-only — results[] do not carry scrapedAt" must not flag fetchedAt).
 */
function _limitsDocumentAbsence(ep: ApiEndpoint, field: string): boolean {
  const escaped = field.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const patterns = [
    // "playCount is not on search.results[]" / "playable is not returned"
    new RegExp(`(?:^|[.!?\\s])\`?${escaped}\`?\\s+is\\s+not\\b`, "i"),
    // Shape absence: "do not carry scrapedAt" / "does not return playCount"
    // (not "does not expose …" — that often means unfilled/null, not missing key)
    new RegExp(
      `\\b(?:do not carry|does not (?:return|carry)|omits)\\s+\`?${escaped}\\b`,
      "i",
    ),
    // "no per-row scrapedAt" / "There is no scrapedAt"
    new RegExp(`\\bno(?:\\s+per-row)?\\s+\`?${escaped}\\b`, "i"),
  ];
  for (const line of ep.platformLimits ?? []) {
    if (patterns.some((re) => re.test(line))) return true;
  }
  return false;
}

/**
 * Fail when platformLimits document a field as absent but the generated
 * example still contains it (stale snapshot — the SP2-docs failure mode).
 *
 * Pairs with `npm run gen:examples` from api_snapshots.json. Live capture
 * stays a separate refresh step (credits); this guard makes that drift a
 * build error instead of an audit finding.
 */
export function lintDocsExampleFieldCoverage(): string[] {
  const errors: string[] = [];
  for (const ep of ALL_ENDPOINTS) {
    if (ep.platform === "account" || ep.platform === "utilities") continue;
    if (!ep.platformLimits?.length) continue;
    const example = API_EXAMPLES[ep.slug];
    if (!example || Object.keys(example).length === 0) continue;
    const keys = new Set<string>();
    _collectExampleKeys(example, keys);

    for (const field of keys) {
      if (_limitsDocumentAbsence(ep, field)) {
        errors.push(
          `${ep.slug}: example still contains \`${field}\` but platformLimits say it is absent — regenerate api_snapshots.json / gen_examples.py`,
        );
      }
    }
  }
  return errors;
}

/** Build the documented response structure from a real example payload. */
function structureFromExample(data: Record<string, unknown>, slug?: string): ResponseGroup[] {
  const top: ResponseField[] = [];
  const nested: ResponseGroup[] = [];

  for (const [key, value] of Object.entries(data)) {
    if (RAW_KEYS.has(key)) {
      top.push({ name: key, desc: FIELD_DESCS.raw });
      continue;
    }
    if (Array.isArray(value)) {
      const first = value.find((x) => x && typeof x === "object" && !Array.isArray(x)) as
        | Record<string, unknown>
        | undefined;
      if (first) {
        nested.push({
          title: humanizeField(key),
          note: `Each item in ${key} contains:`,
          fields: fieldsFromObject(first, slug),
        });
        continue;
      }
      top.push({ name: key, desc: describeField(key, value, slug) });
      continue;
    }
    if (value && typeof value === "object") {
      const inner = value as Record<string, unknown>;
      if (Object.keys(inner).length > 0) {
        nested.push({
          title: humanizeField(key),
          note: `The ${key} object contains:`,
          fields: fieldsFromObject(inner, slug),
        });
        continue;
      }
    }
    top.push({ name: key, desc: describeField(key, value, slug) });
  }

  const groups: ResponseGroup[] = [];
  if (top.length > 0) groups.push({ title: "Top-level fields", fields: top });
  groups.push(...nested);
  return groups;
}

export function responseStructure(ep: ApiEndpoint): ResponseGroup[] {
  const real = API_EXAMPLES[ep.slug];
  if (real && Object.keys(real).length > 0) {
    const derived = structureFromExample(real, ep.slug);
    // Merge alt-mode examples (e.g. Kick channel → clips[]) so Response
    // structure documents every mode, not only the primary curl snapshot.
    const variants = API_EXAMPLE_VARIANTS[ep.slug] || [];
    if (derived.length > 0 && variants.length > 0) {
      const seenTitles = new Set(derived.map((g) => g.title));
      const top = derived.find((g) => g.title === "Top-level fields");
      const topNames = new Set(top?.fields.map((f) => f.name) || []);
      for (const variant of variants) {
        const extra = structureFromExample(variant.data, ep.slug);
        for (const group of extra) {
          if (group.title === "Top-level fields" && top) {
            for (const field of group.fields) {
              if (!topNames.has(field.name)) {
                top.fields.push(field);
                topNames.add(field.name);
              }
            }
            continue;
          }
          if (!seenTitles.has(group.title)) {
            derived.push(group);
            seenTitles.add(group.title);
          }
        }
      }
      return derived;
    }
    if (derived.length > 0) return derived;
  }
  switch (ep.category) {
    case "transcript":
      if (
        ep.slug === "youtube-audio-transcript" ||
        ep.slug === "rumble-video-transcript"
      ) {
        return [
          {
            title: "Top-level fields",
            fields: [
              { name: "platform", desc: `Always "${ep.platform}" on this endpoint.` },
              ...(ep.slug === "youtube-audio-transcript"
                ? [
                    { name: "videoId", desc: "YouTube video id parsed from the url." },
                    {
                      name: "source",
                      desc: 'Always "asr" — speech-to-text on the audio (not published captions).',
                    },
                    {
                      name: "asrProvider",
                      desc: "ASR backend that produced this transcript.",
                    },
                    {
                      name: "languageIsDetected",
                      desc: "true when language was auto-detected from the audio.",
                    },
                    {
                      name: "creditsUsed",
                      desc: "Credits billed: ceil(durationSeconds / 60) × 2.",
                    },
                  ]
                : [
                    { name: "id", desc: "Rumble video id." },
                    {
                      name: "source",
                      desc: 'Always "captions" — published .vtt only (no STT).',
                    },
                    {
                      name: "languageName",
                      desc: "Human label from the caption track.",
                    },
                  ]),
              { name: "url", desc: "Canonical URL of the video." },
              { name: "language", desc: "Language code actually returned." },
              { name: "durationSeconds", desc: "Length in seconds when known." },
              {
                name: "text",
                desc: "Full transcript — segment texts joined with a single space.",
              },
              {
                name: "segments",
                desc: "Timed cues as an array of {text, startMs, endMs} — not a count.",
              },
            ],
          },
          {
            title: "Segments",
            note: "Each item in segments contains:",
            fields: [
              { name: "text", desc: "Spoken text for this cue." },
              { name: "startMs", desc: "Cue start in integer milliseconds." },
              { name: "endMs", desc: "Cue end in integer milliseconds." },
            ],
          },
        ];
      }
      return [
        {
          title: "Full transcript",
          fields: [
            { name: "transcript", desc: "Complete text transcript of the video." },
            { name: "wordCount", desc: "Total number of words in the transcript." },
            { name: "segments", desc: "Total number of transcript segments." },
          ],
        },
        {
          title: "Timestamped segments",
          note: "Each item in transcriptSegments contains:",
          fields: [
            { name: "text", desc: "The spoken text for this segment." },
            { name: "start", desc: "Start time in seconds." },
            { name: "duration", desc: "Duration of the segment in seconds." },
            ...(ep.platform === "youtube"
              ? [{ name: "end", desc: "End time in seconds (start + duration)." }]
              : []),
            { name: "timestamp", desc: "Human-readable timestamp (MM:SS format)." },
          ],
        },
      ];
    case "summarize":
      return [
        {
          title: "Summary",
          fields: [
            { name: "summary", desc: "AI-generated summary of the video (2–3 paragraphs)." },
            { name: "sentiment", desc: "Overall tone of the content (positive, neutral, negative)." },
          ],
        },
        {
          title: "Structured output",
          fields: [
            { name: "keyPoints", desc: "Array of the most important takeaways." },
            { name: "topics", desc: "Array of detected topics and themes." },
          ],
        },
      ];
    case "details":
      return [
        {
          title: "Video",
          fields: [
            { name: "id", desc: "Stable platform ID for the video." },
            { name: "title", desc: "Video title." },
            { name: "author", desc: "Creator handle or channel name." },
            { name: "durationSec", desc: "Video length in seconds." },
            { name: "publishedAt", desc: "Publish date (ISO 8601)." },
          ],
        },
        {
          title: "Engagement",
          fields: [
            { name: "views", desc: "Total view count." },
            { name: "likes", desc: "Total like count." },
            { name: "comments", desc: "Total comment count." },
          ],
        },
      ];
    case "comments":
      return [
        {
          title: "Result",
          fields: [
            { name: "totalReturned", desc: "Number of comments returned in this page." },
            { name: "totalComments", desc: "Total comments on the video when the platform exposes it." },
            { name: "nextCursor", desc: "Cursor for the next page of comments." },
            { name: "hasMore", desc: "Whether another page is available." },
          ],
        },
        {
          title: "Each comment",
          note: "Each item in comments contains:",
          fields: [
            { name: "id", desc: "Stable comment id." },
            { name: "author", desc: "Comment author name or handle." },
            { name: "authorChannelId", desc: "Author channel id when exposed." },
            { name: "text", desc: "The comment text." },
            { name: "likeCount", desc: "Number of likes on the comment." },
            { name: "replyCount", desc: "Number of replies in the thread." },
            { name: "hasCreatorHeart", desc: "Whether the creator hearted the comment." },
            {
              name: "publishedTimeText",
              desc: 'Relative label from the platform (e.g. "6 years ago", may include "(edited)").',
            },
            {
              name: "publishedTimeApprox",
              desc: "Approximate ISO-8601 derived from publishedTimeText, truncated to label precision (day/hour/minute).",
            },
            {
              name: "publishedTimeIsApproximate",
              desc: "true when publishedTimeApprox was derived from the relative label (typical for YouTube comments).",
            },
          ],
        },
      ];
    case "channel":
      return [
        {
          title: "Profile",
          fields: [
            { name: "handle", desc: "Profile / channel handle." },
            { name: "name", desc: "Display name." },
            { name: "bio", desc: "Profile bio or description." },
            { name: "verified", desc: "Whether the account is verified." },
          ],
        },
        {
          title: "Stats",
          fields: [
            { name: "followers", desc: "Follower / subscriber count." },
            { name: "posts", desc: "Total number of posts / videos." },
          ],
        },
      ];
    case "search":
      return [
        {
          title: "Result",
          fields: [{ name: "total", desc: "Number of results returned." }],
        },
        {
          title: "Each result",
          note: "Each item in results contains:",
          fields: [
            { name: "title", desc: "Result title." },
            { name: "url", desc: "Direct URL to the content." },
            { name: "author", desc: "Creator handle." },
            { name: "views", desc: "View count where available." },
          ],
        },
      ];
    case "list":
      return [
        {
          title: "Result",
          fields: [{ name: "total", desc: "Number of items returned." }],
        },
        {
          title: "Each item",
          note: "Each item in items contains:",
          fields: [
            { name: "title", desc: "Item title." },
            { name: "url", desc: "Direct URL to the content." },
            { name: "views", desc: "View count." },
            { name: "publishedAt", desc: "Publish date (ISO 8601)." },
          ],
        },
      ];
  }
}

// ---------------------------------------------------------------------------
// Use cases (per category)
// ---------------------------------------------------------------------------

/** Profile resolve / enrichment endpoints — not niche creator discovery. */
const PROFILE_ENRICHMENT_USE_CASES: UseCase[] = [
  {
    title: "Profile Enrichment",
    desc: "Add live stats, bio, and account flags to a contact you already have.",
  },
  {
    title: "Creator Verification",
    desc: "Confirm a known handle, audience size, and business/verified status before outreach.",
  },
  {
    title: "Competitive Analysis",
    desc: "Track follower growth and posting cadence for accounts you already follow.",
  },
  {
    title: "Partnership Qualification",
    desc: "Vet known partnership and sponsorship targets with fresh profile data.",
  },
];

/** True profile / page resolve endpoints under category "channel". */
const PROFILE_CHANNEL_SLUGS = new Set([
  "youtube-channel-details",
  "tiktok-channel-details",
  "instagram-channel-details",
  "linkedin-company",
  "snapchat-user-profile",
  "truth-social-profile",
  "twitch-profile",
  "bluesky-profile",
  "twitter-profile",
  "threads-profile",
  "linkme-profile",
  "kwai-profile",
  "soundcloud-artist",
]);

/** Name → @handle resolvers filed under search (e.g. Instagram Profile Search). */
const RESOLVE_SEARCH_SLUGS = new Set([
  "instagram-profile-search",
]);

/** Video/post performance details — safe for the generic Analytics use-cases. */
const VIDEOISH_DETAILS_SLUGS = new Set([
  "youtube-video-details",
  "youtube-community-post-details",
  "tiktok-video-details",
  "instagram-details",
  "instagram-highlights-details",
  "instagram-embed",
  "facebook-details",
  "twitter-tweet-details",
  "reddit-post-details",
  "threads-post-details",
  "pinterest-pin-details",
  "linkedin-post-details",
  "truth-social-post",
  "kwai-post",
]);

const VIDEO_DETAILS_USE_CASES: UseCase[] = [
  { title: "Analytics", desc: "Track views, likes, and engagement over time." },
  { title: "Competitor Monitoring", desc: "Benchmark the performance of other creators." },
  { title: "Dashboards", desc: "Power reporting and BI with real metadata." },
  { title: "Content Curation", desc: "Filter and rank videos by performance." },
];

/** Slug-specific use cases when category defaults would mislead. */
const SLUG_USE_CASES: Record<string, UseCase[]> = {
  "account-balance": [
    {
      title: "Low-balance alerts",
      desc: "Poll totalCredits / usedThisMonth and page when subscriptionCredits approach zero.",
    },
    {
      title: "Subscription vs top-up",
      desc: "Tell time-boxed subscriptionCredits apart from permanent topupCredits before auto-buy logic.",
    },
    {
      title: "Key identity",
      desc: "Read keyName + rateLimitPerMinute for the calling key in ops dashboards.",
    },
  ],
  "account-request-history": [
    {
      title: "Support matching",
      desc: "Copy requestId from a failed call and match it to the envelope / x-captapi-request-id header.",
    },
    {
      title: "Incident filters",
      desc: "Query last week's 5xx with statusCode + since/until, or a single endpoint path.",
    },
    {
      title: "Cache savings",
      desc: "Compare cacheHit true (0 credits, ~150ms) vs false (billed, multi-second) on the same resource.",
    },
  ],
  "account-daily-usage": [
    {
      title: "Spend charts",
      desc: "Plot creditsUsed per day for budgeting and anomaly detection.",
    },
    {
      title: "Reliability",
      desc: "Compare successfulRequests vs failedRequests over the window.",
    },
  ],
  "account-most-used-routes": [
    {
      title: "Cost hotspots",
      desc: "Rank which Captapi routes burn the most credits for your key.",
    },
    {
      title: "Product planning",
      desc: "See which integrations your customers actually call.",
    },
  ],
  "video-transcript": [
    {
      title: "Bring-your-own media",
      desc: "Transcribe uploaded podcasts or meeting recordings without a social URL.",
    },
    {
      title: "Bill verification",
      desc: "Read durationSeconds and creditsCharged to confirm the per-minute invoice line.",
    },
    {
      title: "Word timings",
      desc: "Pass timestampGranularity=word when you need karaoke-style captions.",
    },
  ],
  "video-summarize": [
    {
      title: "Meeting digests",
      desc: "Upload a recording and get summary + keyPoints plus the full transcript in one call.",
    },
    {
      title: "Bill verification",
      desc: "creditsCharged = ceil(durationSeconds/60) + 1 — both fields are in the response.",
    },
    {
      title: "Bring-your-own media",
      desc: "Summarize podcasts or offline files without a social URL.",
    },
  ],
  "analytics-post": [
    {
      title: "Cross-platform dashboards",
      desc: "One metrics{} shape for YouTube, TikTok, Instagram, and eight other networks — read engagementRateBasis before comparing rates.",
    },
    {
      title: "Honest reporting",
      desc: "When commentsIsApproximate is true, show rounded comments and inherited interactions uncertainty in reports.",
    },
    {
      title: "Handle vs display name",
      desc: "Join on author.username (@handle), never displayName.",
    },
  ],
  "analytics-compare": [
    {
      title: "A/B uploads",
      desc: "Pass two URLs (e.g. TikTok + YouTube) and compare the same metrics{} object side by side.",
    },
    {
      title: "Partial batches",
      desc: "Use failed[] + status when one URL dies — resolved rows still bill and return full post analytics.",
    },
    {
      title: "One round-trip",
      desc: "Up to 10 URLs per call; same per-URL credit as Post Analytics, cache shared.",
    },
  ],
  "amazon-shop-page": [
    {
      title: "Seller catalog ingest",
      desc: "Pull a merchant's ASIN list with canonical /dp URLs for price monitoring and catalog joins.",
    },
    {
      title: "Badge & Prime signals",
      desc: "Track isPrime / isBestSeller / isSponsored on storefront rows without HTML scraping.",
    },
    {
      title: "Pagination",
      desc: "Walk nextCursor/hasMore across ~16-product Amazon storefront pages at 1 credit each.",
    },
    {
      title: "Not influencer shops",
      desc: "For amazon.com/shop/{handle} creator vitrines (socials/lists/curations), use a different product — this endpoint rejects those URLs.",
    },
  ],
  "kick-clip": [
    {
      title: "Clip enrichment",
      desc: "Resolve a Kick clip URL to creator vs channel, views, category, and HLS playlist for players/ffmpeg.",
    },
    {
      title: "Channel clip feeds",
      desc: "Pass a channel URL to pull recent clips[] (limit up to 100) without a duplicate top-level clip.",
    },
    {
      title: "VOD deep-links",
      desc: "Open vod.urlWithOffset to jump to the exact second in the source VOD where the clip was cut.",
    },
    {
      title: "Moderation flags",
      desc: "Read isMature + privacy before surfacing a clip in a public feed.",
    },
  ],
  "twitch-user-videos": [
    { title: "Content Pipelines", desc: "Ingest a channel's recent VODs (up to 100) with broadcastType and game metadata." },
    { title: "Monitoring", desc: "Detect new ARCHIVE uploads via video id + createdAt within the 100-video window." },
    { title: "Highlights", desc: "filterBy=HIGHLIGHT to pull edited clips Twitch stores as VODs." },
    { title: "Analytics", desc: "Aggregate views across recent VODs without repeating channel{} on every row." },
  ],
  "twitch-user-schedule": [
    { title: "Calendar sync", desc: "Build a stream calendar; skip rows where canceledUntil or isCancelled is set." },
    { title: "Recurring series", desc: "Use isRecurring + id to track weekly slots without mistaking one-offs." },
    { title: "Category planning", desc: "Read game/gameId per segment for upcoming content mix." },
    { title: "Preview vs full", desc: "profile.schedule[] is a short preview — this endpoint is the canonical full schedule." },
  ],
  "bluesky-post-details": [
    {
      title: "Thread reading",
      desc: "Pull a post and its nested replies[] in one call — the only Captapi path to Bluesky reply content.",
    },
    {
      title: "Link integrity",
      desc: "Use links[] from facets for full URLs; Bluesky truncates long links inside text.",
    },
    {
      title: "Compliance signals",
      desc: "Respect author.labels and post labels (e.g. !no-unauthenticated) before storing or displaying content.",
    },
    {
      title: "Conversation context",
      desc: "parentUri / rootUri tell you whether the URL is a reply and which thread it belongs to.",
    },
  ],
  "bluesky-user-posts": [
    {
      title: "Creator monitoring",
      desc: "Track a handle's author feed — originals and reposts — with isRepost so boosts are not mistaken for new posts.",
    },
    {
      title: "Honest analytics",
      desc: "Average engagement only on rows where isRepost is false (or includeReposts=false) so you do not credit someone else's likes to the profile.",
    },
    {
      title: "Content calendars",
      desc: "Pull text, quote embeds, and links for scheduling or research — no video CDN URLs on this surface.",
    },
    {
      title: "Partnership vetting",
      desc: "Sample recent posts and quote targets before outreach; use filter=posts_no_replies to skip reply noise.",
    },
  ],
  "tiktok-shop-search": [
    {
      title: "Product Discovery",
      desc: "Find TikTok Shop listings by keyword with price, sold, and rating in one call.",
    },
    {
      title: "Promo & Price Screening",
      desc: "Filter hits by originalPrice/discount/savings before opening a PDP.",
    },
    {
      title: "Quality Ranking",
      desc: "Sort or threshold on rating/reviews without a second Product Details hop.",
    },
    {
      title: "Seller Follow-up",
      desc: "Take seller.id / seller.url into Shop Products for the full store catalog.",
    },
  ],
  "tiktok-shop-product-reviews": [
    {
      title: "Quality Signals",
      desc: "Read verified reviews + attached photos before stocking or promoting a SKU.",
    },
    {
      title: "Variant Complaints",
      desc: "Group review text by sku to see which Color/Size draws issues.",
    },
    {
      title: "Market Mix",
      desc: "Use review country to see where buyers are writing from.",
    },
    {
      title: "UGC Sampling",
      desc: "Pull images[] as real shopper photos for creative research.",
    },
  ],
  "tiktok-shop-user-showcase": [
    {
      title: "Affiliate Shelf Audit",
      desc: "See which products a creator is actively promoting in their Shop showcase.",
    },
    {
      title: "Creator Commerce Intel",
      desc: "Rank showcase SKUs by sold / rating without scraping the profile UI.",
    },
    {
      title: "Store Handoff",
      desc: "Take seller.url into Shop Products when you need the brand's full catalog.",
    },
    {
      title: "PDP Deep Dive",
      desc: "Pass a product URL to Product Details for skus[] / stock / categories.",
    },
  ],
  "tiktok-shop-products": [
    {
      title: "Competitor Store Intel",
      desc: "Read shopInfo sold/followers/rating alongside the priced catalog in one call.",
    },
    {
      title: "Price & Discount Monitoring",
      desc: "Track numeric price/originalPrice/discount/savings without TikTok's masked $3? strings.",
    },
    {
      title: "Official Shop Vetting",
      desc: "Check isOfficial / identityLabel before featuring a store in a campaign.",
    },
    {
      title: "Catalog Sampling",
      desc: "Pull up to ~30 SSR products with sold + rating for assortment research (no cursor yet).",
    },
  ],
  "tiktok-shop-product-details": [
    {
      title: "Variant Stock Tracking",
      desc: "Watch skus[].stock + saleProps so you know which Color/Size is actually depleting.",
    },
    {
      title: "Price & Promo Truth",
      desc: "Read price/originalPrice/discount/savings on the PDP — same commerce fields as the catalog row.",
    },
    {
      title: "Assortment & Categories",
      desc: "Use categories[] and saleProperties[] to classify SKUs without scraping the storefront UI.",
    },
    {
      title: "Seller Join",
      desc: "Take seller.id / seller.url into Shop Products for the full store catalog.",
    },
  ],
  "twitter-user-tweets": [
    {
      title: "Top-Post Analysis",
      desc: "Study an account's highest-engagement public tweets (popularity-ranked, not latest).",
    },
    {
      title: "Brand Safety Sampling",
      desc: "Review viral posts and media from a profile before a partnership.",
    },
    {
      title: "Engagement Benchmarks",
      desc: "Compare likes/replies/retweets/quotes across an account's standout posts.",
    },
    {
      title: "Not for New-Tweet Monitoring",
      desc: "Twitter does not expose a public chronological feed here — use another signal for \"just posted\".",
    },
  ],
  "tiktok-audience-demographics": [
    { title: "Geo Targeting", desc: "See which countries commenters engage from before localizing creatives." },
    { title: "Market Sizing", desc: "Estimate which markets show up in a creator's engaged audience." },
    { title: "Localization", desc: "Pick caption languages and market focus from commenter language mix." },
    { title: "Creator Vetting", desc: "Check whether engaged commenters match the campaign's target geos." },
  ],
  "tiktok-profile-region": [
    { title: "Creator Location", desc: "Estimate where a creator is based when TikTok hides region." },
    { title: "Compliance Checks", desc: "Flag likely country of origin for geo-restricted campaigns." },
    { title: "Localization", desc: "Match outreach language to the creator's interface language." },
    { title: "Partnership Screening", desc: "Sanity-check geography before briefing a creator." },
  ],
  "tiktok-song-details": [
    { title: "Sound Research", desc: "Pull title, artist, duration, and cover for a TikTok sound." },
    { title: "Usage Tracking", desc: "Read usageCount when TikTok exposes how many videos use the sound." },
    { title: "Commerce Rights", desc: "Check isCommerceMusic / hasCommerceRight before brand use." },
    { title: "Audio Pipelines", desc: "Pair with Music Posts to list videos on the same sound." },
  ],
  "tiktok-live": [
    { title: "Live Monitoring", desc: "Detect whether a TikTok account is currently live." },
    { title: "Stream Ingest", desc: "Pull live stream URLs and quality variants when the room is active." },
    { title: "Alerts", desc: "Trigger notifications when a watched creator goes live." },
  ],
  "tiktok-live-info": [
    { title: "Live Room Metadata", desc: "Fetch room title, host, and live status for a TikTok live." },
    { title: "Stream Monitoring", desc: "Poll live room state without scraping the app UI." },
  ],
  "spotify-album": [
    {
      title: "Track lists with stream counts",
      desc: "Read tracks[] with playCount, durationMs, and explicit without scraping the album page.",
    },
    {
      title: "Catalog joins",
      desc: "Chain artists[].uri → /spotify/artist and tracks[].uri → /spotify/track.",
    },
    {
      title: "Release metadata",
      desc: "Use full releaseDate (ISO) plus cover art for discography and CRM enrichment.",
    },
  ],
  "spotify-search": [
    {
      title: "Discovery → details",
      desc: "Search then chain canonical result URIs into /spotify/track, /album, or /artist.",
    },
    {
      title: "Freshness-aware ingest",
      desc: "Use envelope fetchedAt to know when results were pulled (no cursor beyond limit 50).",
    },
  ],
  "spotify-podcast": [
    {
      title: "Podcast research",
      desc: "Rank shows with rating{average, totalRatings} — a signal Spotify's free Web API does not expose.",
    },
    {
      title: "Publisher vs hosts",
      desc: "Use publisher{name} without mistaking it for episode hosts or artists[].",
    },
    {
      title: "Archive fan-out",
      desc: "Chain the show URI into /spotify/podcast-episodes for cursor-paginated episode history.",
    },
  ],
  "spotify-podcast-episodes": [
    {
      title: "Full archive crawl",
      desc: "Walk nextCursor/hasMore to ingest beyond the newest 50 episodes (flat 2 credits per page).",
    },
    {
      title: "Preview ingest",
      desc: "Collect previewUrl / audioUrls mp3 previews plus releaseDate and explicit without scraping the show page.",
    },
    {
      title: "Exclusive / video flags",
      desc: "Filter hasVideo, paywallContent, and showTypes for format and exclusivity research.",
    },
  ],
  "spotify-track": [
    {
      title: "Stream counts",
      desc: "Read playCount (same GraphQL stream metric as artist topTracks) without the official Web API.",
    },
    {
      title: "Catalog joins",
      desc: "Chain artists[].uri → /spotify/artist and album.uri → /spotify/album from one track resolve.",
    },
    {
      title: "Playlist enrichment",
      desc: "Fill CRM/playlist rows with title, durationMs, explicit, and releaseDate at 1 credit.",
    },
  ],
  "spotify-artist": [
    {
      title: "Audience geography",
      desc: "Use monthlyListeners, worldRank, and topCities — fields Spotify's free Web API does not expose.",
    },
    {
      title: "Hit tracks",
      desc: "Rank an artist's topTracks by playCount for A&R, playlisting, and competitive research.",
    },
    {
      title: "Discography fan-out",
      desc: "When albumsHasMore/singlesHasMore, walk release URIs into /spotify/album for full catalog detail.",
    },
  ],
  "soundcloud-track": [
    {
      title: "Engagement + license",
      desc: "Read plays/likes/reposts/comments/downloads and license for reuse research at 1 credit.",
    },
    {
      title: "Playback URLs",
      desc: "Use streamUrl / hlsUrl (with mediaUrlsExpireAt) when streamable; downloadable is a permission flag.",
    },
    {
      title: "Artist join",
      desc: "Chain artist.id or artist.handle into /soundcloud/artist without a second resolve scrape.",
    },
  ],
  "soundcloud-artist": [
    {
      title: "Plan + verification",
      desc: "Use subscriptionTier and verified for creator qualification without parsing badge duplicates.",
    },
    {
      title: "Creator graph",
      desc: "Pipe externalLinks (Facebook/Twitter/YouTube/site) into matching Captapi profile endpoints.",
    },
    {
      title: "Permalink joins",
      desc: "Prefer handle (URL slug) over username display casing when storing CRM keys.",
    },
  ],
  "soundcloud-artist-tracks": [
    {
      title: "Content Pipelines",
      desc: "Ingest an artist's track catalog with the same fields as /soundcloud/track.",
    },
    {
      title: "Monitoring",
      desc: "Detect new uploads via track id + publishedAt across opaque cursor pages.",
    },
    {
      title: "Artist join",
      desc: "Use top-level artistId / artist.handle once — not repeated on every track row.",
    },
    {
      title: "Analytics",
      desc: "Aggregate plays/likes across the artist's recent tracks without artist{} bloat.",
    },
  ],
  "kwai-profile": [
    {
      title: "Profile Enrichment",
      desc: "Resolve a Kwai @handle to bio, avatar, verified, and follower/like/post counts.",
    },
    {
      title: "Creator Verification",
      desc: "Confirm verified + verifiedDescription before outreach on Brazilian/Kwai audiences.",
    },
    {
      title: "Competitive Analysis",
      desc: "Track followers, likedCount, and postCount over time for accounts you already follow.",
    },
    {
      title: "Partnership Qualification",
      desc: "Vet Kwai creators with publicPostCount and audience size at 1 credit.",
    },
  ],
  "kwai-user-posts": [
    {
      title: "Content Pipelines",
      desc: "Ingest a creator's recent Kwai posts with engagement and signed mp4 URLs.",
    },
    {
      title: "Transcripts included",
      desc: "Use transcript when Kwai JSON-LD exposes auto-captions — included in the per-post credit, not a separate Whisper call.",
    },
    {
      title: "Monitoring",
      desc: "Detect new uploads via post id + publishedAt across opaque cursor pages.",
    },
    {
      title: "Archiving",
      desc: "Snapshot metadata plus CDN media — re-fetch videoUrl before mediaUrlsExpireAt.",
    },
  ],
  "kwai-post": [
    {
      title: "Post enrichment",
      desc: "Resolve a Kwai video URL to caption, hashtags, author, and engagement.",
    },
    {
      title: "Playback",
      desc: "Play or download via videoUrl when videoType is mp4; re-fetch before mediaUrlsExpireAt.",
    },
    {
      title: "Captions",
      desc: "Read transcript when Kwai exposes auto-captions (deduped); omitted when unavailable.",
    },
  ],
  "github-repository": [
    {
      title: "Repo enrichment",
      desc: "Resolve owner/name to stars, real watchers (subscribers), license, and parent when forked.",
    },
    {
      title: "Issue vs PR load",
      desc: "Read openIssuesAndPrs (issues+PRs); use github/pull-requests when you need PRs alone.",
    },
    {
      title: "License hygiene",
      desc: "Prefer license (SPDX); when null, check licenseName — NOASSERTION is not passed through.",
    },
  ],
  "github-trending-repositories": [
    {
      title: "Momentum discovery",
      desc: "Find repos gaining stars today/this week/month via starsGained — not all-time star charts.",
    },
    {
      title: "Language radar",
      desc: "Pass language=python (or typescript, …) to scope /trending/{language}.",
    },
    {
      title: "Detail fan-out",
      desc: "Chain fullName into github/repository for license, watchers/subscribers, and parent.",
    },
  ],
  "github-trending-developers": [
    {
      title: "Windowed discovery",
      desc: "Rank developers from github.com/trending/developers by since=daily|weekly|monthly — not all-time follower search.",
    },
    {
      title: "Popular repo signal",
      desc: "Read popularRepo + description from the trending card, then open github/repository for detail.",
    },
    {
      title: "Hiring shortlist",
      desc: "Filter hydrated followers, publicRepos, location, and bio without a second profile call.",
    },
  ],
  "github-contributions": [
    {
      title: "Hiring screens",
      desc: "Read totalContributions + currentStreak from the real heatmap — not a 90-event API ceiling.",
    },
    {
      title: "Cadence charts",
      desc: "Plot days[{date,count,level}] for the last year without scraping the profile HTML yourself.",
    },
    {
      title: "Quiet periods",
      desc: "Spot gaps in the calendar (count=0 stretches) before outreach.",
    },
  ],
  "github-pull-requests": [
    {
      title: "Review throughput",
      desc: "Count non-draft PRs (draft=false) opened or merged in a window without HTML scraping.",
    },
    {
      title: "Label triage",
      desc: "Filter labels[] for bug/feature queues before assigning reviewers.",
    },
    {
      title: "Branch mapping",
      desc: "Read head.ref → base.ref to see which branches land where.",
    },
  ],
  "github-activity": [
    {
      title: "Push forensics",
      desc: "Read PushEvent payload.commits[].message + ref — not just 'someone pushed'.",
    },
    {
      title: "Issue/PR actions",
      desc: "Track opened/closed/merged via IssuesEvent and PullRequestEvent payload.action.",
    },
    {
      title: "Bounded feed",
      desc: "Respect eventCeiling=90 — this is recent public activity, not a full history archive.",
    },
  ],
  "github-repositories": [
    {
      title: "Recent activity",
      desc: "sort=pushed to list a developer's most recently pushed repos.",
    },
    {
      title: "Owned vs member",
      desc: "type=owner|member|all to separate personal repos from org memberships.",
    },
    {
      title: "Fork parent lookup",
      desc: "When isFork is true, call github/repository for parent — list payloads omit it.",
    },
  ],
  "github-followers": [
    {
      title: "Audience sample",
      desc: "Page a first screen of followers with stable id for CRM joins — not a full mega-account dump.",
    },
    {
      title: "Org vs user",
      desc: "Filter type=Organization vs User in the follower graph.",
    },
    {
      title: "When to call GitHub directly",
      desc: "Full archives of 100k+ followers are cheaper on api.github.com (free, rate-limited).",
    },
  ],
  "github-following": [
    {
      title: "Interest graph",
      desc: "See who a developer follows — same {id, login, type} cards as followers.",
    },
    {
      title: "Dedup across pages",
      desc: "Use numeric id, not login alone, when merging following pages.",
    },
    {
      title: "When to call GitHub directly",
      desc: "Exhaustive following dumps belong on api.github.com, not Captapi credit pages.",
    },
  ],
  "komi-page": [
    {
      title: "Commerce inventory",
      desc: "Collect PRODUCT rows with price/currency plus LINK CTAs (e.g. Visit SKIMS) for affiliate and merch research.",
    },
    {
      title: "Creator graph fan-out",
      desc: "Pipe socials.instagram/tiktok/youtube/spotify into matching Captapi profile endpoints.",
    },
    {
      title: "Contact + website",
      desc: "Read socials.website and outbound link destinations without scraping the Komi SPA.",
    },
    {
      title: "Link change tracking",
      desc: "Stable link id + visible/order for dedupe and inventory diffs (hidden products included).",
    },
  ],
  "pillar-page": [
    {
      title: "Link performance ranking",
      desc: "Sort links[] by clicks to see which destinations actually convert — the signal Linktree/Komi do not expose.",
    },
    {
      title: "Merch + product inventory",
      desc: "Read products[] (title, price, url, image) alongside custom links for affiliate and storefront research.",
    },
    {
      title: "Monetization channel map",
      desc: "Pipe socials.patreon/discord/twitch/spotify/amazon into deeper Captapi enrichment.",
    },
    {
      title: "Contact + location",
      desc: "Collect public email and location without scraping the Pillar SPA.",
    },
  ],
  "linktree-page": [
    {
      title: "Creator graph fan-out",
      desc: "Pipe socialAccounts.instagram/tiktok/spotify/soundcloud into our matching profile endpoints — SC cannot complete Spotify/SoundCloud.",
    },
    {
      title: "Contact discovery",
      desc: "Collect outbound destinations (incl. PRODUCT merch shopUrl) plus top-level email when published.",
    },
    {
      title: "Niche + platform signals",
      desc: "Use verticals[] and linkPlatforms[] to classify creators before deeper enrichment.",
    },
    {
      title: "Link-in-bio inventory",
      desc: "Typed links[] with GROUP nesting, thumbnails, and stable string ids.",
    },
  ],
  "linkbio-page": [
    {
      title: "Social graph where SC returns null",
      desc: "Read socials.instagram/tiktok/youtube/… even when ScrapeCreators leaves those fields null despite URLs in links[].",
    },
    {
      title: "Titled link inventory",
      desc: "Use links[].title on social rows (Facebook, Triller, …) plus content button labels for UI and dedupe.",
    },
    {
      title: "Website + contact",
      desc: "Top-level website / email / whatsapp when lnk.bio publishes them — not buried only as an untitled link.",
    },
    {
      title: "Unmapped networks",
      desc: "Inspect other[] for niche social icons that do not fit the fixed socials{} key list.",
    },
  ],
  "linkme-profile": [
    {
      title: "Audience sizing",
      desc: "Use profileVisitCount (e.g. 15.9k) with totalLinks — one of the few public link-in-bio audience metrics.",
    },
    {
      title: "Lead enrichment",
      desc: "Read infoLinks / top-level email plus stripeStatus.tipsEnabled for contact and monetization signals.",
    },
    {
      title: "Social + CTA inventory",
      desc: "Pipe socials{} / webLinks[] into Captapi profile endpoints and treat links[] as featured CTAs (not footer chrome).",
    },
    {
      title: "Avatar quality gate",
      desc: "Skip isDefaultProfilePicture=true avatars so placeholder images never enter your creator DB.",
    },
  ],
  "facebook-marketplace-search": [
    {
      title: "Local inventory",
      desc: "Search by city name + keyword; filter isLocal or deliveryMethod=local_pickup to drop nationwide shipped rows.",
    },
    {
      title: "Price band monitoring",
      desc: "minPrice/maxPrice + sortBy=price_ascend for deal alerts without scraping the UI.",
    },
    {
      title: "Tiered detail fetch",
      desc: "List at flat 2 credits; pass details=true only when you need description/coords/gallery (2 + 2 per listing).",
    },
    {
      title: "Status filtering",
      desc: "Read status (available|pending|sold) — Facebook may keep sold listings published.",
    },
  ],
  "facebook-marketplace-location-search": [
    {
      title: "City disambiguation",
      desc: "Bare 'Austin' can mean TX, MN, or IN — pick the hub whose cityPageId/state matches before searching listings.",
    },
    {
      title: "Canonical place id",
      desc: "Use location.id (Facebook city_page.id) — the same identifier marketplace-search cards expose as cityPageId.",
    },
    {
      title: "Optional geocode",
      desc: "Skip this call when marketplace-search's city string is enough; use it only for coords or multi-city resolve.",
    },
  ],
  "github-user": [
    {
      title: "Multi-platform enrichment",
      desc: "Same Captapi key and envelope as Spotify/SoundCloud/Bluesky profiles — join developer handles without a separate GitHub client.",
    },
    {
      title: "User vs Organization",
      desc: "Read type (User | Organization) so org accounts are not mistaken for people.",
    },
    {
      title: "Hiring screens",
      desc: "Pull hireable, publicRepos, followers, and public email (when set) for lightweight developer profiling.",
    },
    {
      title: "When to call GitHub directly",
      desc: "GitHub-only workloads should hit api.github.com free — Captapi shines when you already fan out across many platforms.",
    },
  ],
  "facebook-marketplace-item": [
    {
      title: "Listing Enrichment",
      desc: "Resolve a Marketplace URL to title, priceAmount, status, and seller{} when Facebook exposes it.",
    },
    {
      title: "Seller research",
      desc: "Use seller.id / seller.url to see who is listing and join to other Marketplace calls.",
    },
    {
      title: "Price Monitoring",
      desc: "Track price + priceAmount (minor units) and status without scraping the UI.",
    },
  ],
  "facebook-event-details": [
    { title: "Event Enrichment", desc: "Resolve a Facebook event URL to local start/end, venue, and host id." },
    { title: "Calendar Pipelines", desc: "Build iCal / CRM rows from startDate + timezone without day-shift bugs." },
  ],
  "facebook-event-search": [
    { title: "Local Discovery", desc: "Find public events by topic + city (comedy Chicago) for weekend guides." },
    { title: "Date-Window Ingest", desc: "Filter with from/to on local startDate for this-week calendars." },
    { title: "Venue Research", desc: "Collect going/interested signals when Facebook exposes them." },
  ],
  "facebook-profile-events": [
    { title: "Venue Calendar", desc: "Pull a Page's upcoming shows with sortable startDate (year included)." },
    { title: "Tour Tracking", desc: "Monitor Madison Square Garden / club pages without scraping HTML." },
  ],
  "truth-social-profile": [
    {
      title: "Public-Figure Enrichment",
      desc: "Pull stats and locked/bot/group flags for prominent accounts that Truth Social still exposes without login.",
    },
    {
      title: "Verified-Link Capture",
      desc: "Read fields[].verifiedAt for confirmed profile links when the account publishes them.",
    },
    {
      title: "Auth-Gated Awareness",
      desc: "Expect 404 for non-prominent handles — Truth Social gates most profiles behind login.",
    },
  ],
  "truth-social-user-posts": [
    {
      title: "Public-Figure Monitoring",
      desc: "Track posting cadence for prominent Truth Social accounts that remain public.",
    },
    {
      title: "Link Extraction",
      desc: "Use links[] (and card.url) for real destinations — not span-broken text URLs.",
    },
    {
      title: "Rumble Handoff",
      desc: "When externalVideoId is set, call Captapi Rumble video-details for streams and comments.",
    },
    {
      title: "Auth-Gated Awareness",
      desc: "Most non-prominent handles require auth and 404 — not a general creator catalog.",
    },
  ],
  "truth-social-post": [
    {
      title: "Single-Truth Lookup",
      desc: "Resolve a post URL/ID to text, links[], author, and engagement when still public.",
    },
    {
      title: "Rumble Handoff",
      desc: "externalVideoId bridges into Captapi Rumble endpoints (SC has no Rumble).",
    },
    {
      title: "Auth-Gated Awareness",
      desc: "Most non-prominent posts require auth and return 404 — same platform limit as profile.",
    },
  ],
  "youtube-video-sponsors": [
    { title: "Sponsorship Detection", desc: "Surface sponsor segments disclosed on a YouTube video." },
    { title: "Brand Safety", desc: "See which brands appear alongside a creator's content." },
  ],
  "reddit-subreddit-details": [
    { title: "Community Enrichment", desc: "Pull id, members, activeUsers, rules[], and ISO createdAt." },
    { title: "Research", desc: "Map communities (nsfw/type/language) before sampling posts or comments." },
  ],
  "twitter-community": [
    { title: "Community Enrichment", desc: "Resolve a X/Twitter Community to name and metadata." },
    { title: "Monitoring", desc: "Track community identity for listening workflows." },
  ],
  "tiktok-popular-hashtags": [
    { title: "Trend Charts", desc: "Pull Creative Center Top-100 hashtags by country and period." },
    { title: "Rising Tags", desc: "Use rankDiff + trend[] to spot surging hashtags early." },
    { title: "Campaign Tracking", desc: "Monitor hashtagId + videoCount/totalPlays for branded tags over time." },
    { title: "Related Discovery", desc: "Pass query=niche for co-occurrence related tags when you need adjacency, not the chart." },
  ],
  "tiktok-popular-songs": [
    { title: "Sound Trends", desc: "Track popular and surging TikTok sounds by market." },
    { title: "Brand-Safe Audio", desc: "Filter commercialMusic / ifCml before putting a sound in paid ads." },
    { title: "Trend Analysis", desc: "Use trend[] time series and rankDiff for music marketing." },
  ],
  "tiktok-music-posts": [
    { title: "Sound Tracking", desc: "List public videos that use a specific TikTok sound." },
    { title: "Trend Monitoring", desc: "Watch new posts appear on a sound over time." },
    { title: "Content Sourcing", desc: "Pull examples of a sound for research or UGC." },
  ],
  "tiktok-trending-feed": [
    { title: "Trend Discovery", desc: "Sample what's circulating in TikTok's trending feed for a region." },
    { title: "Content Research", desc: "Inspect captions, sounds, and engagement on trending posts." },
  ],
  "tiktok-popular-creators": [
    { title: "Creator Verification", desc: "Reject inflated accounts using createTime (account age) + bioLinkRisk." },
    { title: "Partnership Qualification", desc: "Shortlist by engagementRate, then vet with ttSeller and contact{}." },
    { title: "Creator Discovery", desc: "Rank Creative Center / For You creators for a market." },
  ],
  "facebook-profile-photos": [
    { title: "Photo Archive", desc: "Pull a Page's public /photos grid with image URLs." },
    { title: "Alt-text Mining", desc: "Read accessibilityCaption for image descriptions Facebook exposes." },
    { title: "Brand Visuals", desc: "Collect creative stills from a Page without inventing captions." },
  ],
};

/** List endpoints that really are a channel/profile catalog feed. */
const CHANNEL_CATALOG_LIST_SLUGS = new Set([
  "youtube-channel-videos",
  "youtube-channel-shorts",
  "youtube-channel-streams",
  "youtube-channel-playlists",
  "youtube-playlist",
  "youtube-playlist-videos",
  "youtube-community-posts",
  "tiktok-channel-posts",
  "tiktok-user-followers",
  "tiktok-user-followings",
  "instagram-channel-posts",
  "instagram-channel-reels",
  "instagram-tagged-posts",
  "facebook-profile-posts",
  "facebook-profile-reels",
  "facebook-group-posts",
  "twitter-user-tweets",
  "threads-user-posts",
  "reddit-subreddit-posts",
  "rumble-channel-videos",
  "linkedin-company-posts",
  "pinterest-user-pins",
  "pinterest-user-boards",
]);

const CHANNEL_CATALOG_USE_CASES: UseCase[] = [
  { title: "Content Pipelines", desc: "Ingest a channel's catalog in bulk." },
  { title: "Monitoring", desc: "Detect new uploads automatically." },
  { title: "Archiving", desc: "Snapshot a creator's library — metadata plus CDN media URLs (re-fetch before mediaUrlsExpireAt)." },
  { title: "Analytics", desc: "Aggregate performance across many videos." },
];

const GENERIC_LIST_USE_CASES: UseCase[] = [
  { title: "Discovery", desc: "Surface items matching a topic, tag, sound, or trend query." },
  { title: "Monitoring", desc: "Watch a list feed over time for new activity." },
  { title: "Research", desc: "Sample structured list results for analysis." },
  { title: "Pipelines", desc: "Ingest list results into your own store or CRM." },
];

export function useCases(ep: ApiEndpoint): UseCase[] {
  const override = SLUG_USE_CASES[ep.slug];
  if (override) return override;

  if (PROFILE_CHANNEL_SLUGS.has(ep.slug) || RESOLVE_SEARCH_SLUGS.has(ep.slug)) {
    return PROFILE_ENRICHMENT_USE_CASES;
  }

  switch (ep.category) {
    case "transcript":
      return [
        { title: "Accessibility", desc: "Provide captions and transcripts for hearing-impaired users." },
        { title: "Content Analysis", desc: "Analyze spoken content for keywords, topics, and sentiment." },
        { title: "Search & Discovery", desc: "Make video content searchable by text." },
        { title: "Content Creation", desc: "Extract quotes and key phrases from videos." },
        { title: "Language Learning", desc: "Provide text alongside audio for language learners." },
        { title: "Research", desc: "Analyze large volumes of video content efficiently." },
        { title: "SEO", desc: "Extract text content for search engine optimization." },
      ];
    case "summarize":
      return [
        { title: "Content Triage", desc: "Decide what's worth watching without watching it." },
        { title: "Newsletters & Digests", desc: "Auto-generate summaries for roundups and emails." },
        { title: "Research", desc: "Condense long videos into key points at scale." },
        { title: "SEO", desc: "Generate descriptions and meta content from videos." },
        { title: "Social", desc: "Draft captions and posts from video content." },
      ];
    case "details":
      if (VIDEOISH_DETAILS_SLUGS.has(ep.slug) || ep.slug.includes("ad-library-ad-details")) {
        return VIDEO_DETAILS_USE_CASES;
      }
      // Non-video details (album, live, marketplace, repo, …) without a slug
      // override: keep a neutral metadata default — never claim video metrics.
      return [
        { title: "Metadata Enrichment", desc: "Resolve a URL to structured fields for storage and CRM." },
        { title: "Dashboards", desc: "Power reporting with clean JSON instead of HTML scrapes." },
        { title: "Research", desc: "Collect entity metadata at scale for analysis." },
      ];
    case "comments":
      return [
        { title: "Sentiment Analysis", desc: "Understand how audiences react to content." },
        { title: "Community Insights", desc: "Surface FAQs, requests, and recurring themes." },
        { title: "Moderation", desc: "Detect spam, abuse, or policy violations at scale." },
        { title: "Market Research", desc: "Mine genuine opinions and product feedback." },
      ];
    case "search":
      return [
        { title: "Trend Discovery", desc: "Find trending content by keyword or hashtag." },
        { title: "Content Sourcing", desc: "Build feeds and playlists programmatically." },
        { title: "Monitoring", desc: "Track topics, brands, and competitors." },
        { title: "Research", desc: "Sample large sets of content for analysis." },
      ];
    case "list":
      if (CHANNEL_CATALOG_LIST_SLUGS.has(ep.slug)) {
        return CHANNEL_CATALOG_USE_CASES;
      }
      return GENERIC_LIST_USE_CASES;
    case "channel":
      // Non-profile channel-category endpoints should set SLUG_USE_CASES.
      return PROFILE_ENRICHMENT_USE_CASES;
  }
}
