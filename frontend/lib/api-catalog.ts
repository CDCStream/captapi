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
  { slug: "youtube-transcript", name: "YouTube Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/youtube/transcript", credits: 1 },
  { slug: "youtube-summarizer", name: "YouTube Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/youtube/summarize", credits: 3 },
  { slug: "youtube-video-details", name: "YouTube Video Details API", shortName: "Video Details", category: "details", method: "GET", path: "/v1/youtube/video-details", credits: 1 },
  { slug: "youtube-comments", name: "YouTube Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/youtube/comments", credits: 2, tagline: "Get comments on any YouTube video — text, author, likes, and timestamp, with cursor pagination (nextCursor + hasMore). Flat 2 credits per call." },
  { slug: "youtube-channel-details", name: "YouTube Channel Details API", shortName: "Channel Details", category: "channel", method: "GET", path: "/v1/youtube/channel-details", credits: 1, tagline: "YouTube channel stats as real numbers plus handle, verified, banner, links, email, and SEO tags.", longDescription: "Pass a channel URL, handle, or UC id and get clean JSON: numeric subscriberCount / videoCount / viewCount, handle, verified, joinedDate, bannerUrl, structured links, plus additive email when present in About/description and tags from channel SEO keywords. Flat 1 credit per call." },
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
      "Search YouTube by keyword and get a cursor-paginated page of clean JSON: results[] with type (video|short|channel|playlist|live), id, canonical url (no radio/mix junk), title, publishedAt, viewCount, durationSeconds, thumbnailUrl, channelName, channelId, channel{id,title,handle,url}, and badges[]. Also partitioned as videos[] / shorts[] / channels[] / playlists[]. Filter with type, sortBy (relevance|date|views|rating), uploadDate (today|this_week|this_month|this_year), duration (under_4|4_20|over_20), and region. Pass nextCursor for the next page. Flat 2 credits per page. cache=true uses the 24h shared cache.",
    delivers: [
      "Cursor pagination via nextCursor + hasMore",
      "Typed results with stable id and canonical URL",
      "channelId + channel{handle,url} when YouTube exposes them",
      "Filters: type, sortBy, uploadDate, duration, region",
    ],
  },
  { slug: "youtube-channel-videos", name: "YouTube Channel Videos API", shortName: "Channel Videos", category: "list", method: "GET", path: "/v1/youtube/channel-videos", credits: 2 },
  { slug: "youtube-playlist-videos", name: "YouTube Playlist Videos API", shortName: "Playlist Videos", category: "list", method: "GET", path: "/v1/youtube/playlist-videos", credits: 2 , tagline: "List videos in a YouTube playlist — id, ISO publishedAt, views, duration. Flat 2 credits.", longDescription: "Paste a YouTube playlist URL and get the videos as clean JSON: id, url, title, publishedAt (ISO-8601; approximate when derived from YouTube's relative label), publishedTimeText (e.g. \"1 year ago\"), viewCount (viewCountApproximate=true when YouTube only shows 2.5B-style compact counts), durationSeconds, thumbnailUrl, channelName. Also returns playlist id and totalVideos when available. Prefer Playlist when you also need owner metadata. Optional fast=true uses YouTube RSS (exact publishedAt, fewer items). Flat 2 credits on the native path." },
  { slug: "youtube-playlist", name: "YouTube Playlist API", shortName: "Playlist", category: "list", method: "GET", path: "/v1/youtube/playlist", credits: 2 , tagline: "YouTube playlist metadata + videos — owner{id,name,handle}, totalVideos, ISO publishedAt. Flat 2 credits.", longDescription: "Paste a YouTube playlist URL and get playlist id/title, channelName, owner{id,name,url,handle}, totalVideos (full playlist size), totalReturned (this page), and videos[] with id, url, title, publishedAt (ISO-8601; approximate from relative labels when YouTube doesn't expose an exact timestamp), publishedTimeText, viewCount (+ viewCountApproximate for compact K/M/B labels), durationSeconds, thumbnailUrl, and channel{}. Prefer this over Playlist Videos when you need owner + total size. Optional fast=true uses YouTube RSS. Flat 2 credits on the native path." },
  { slug: "youtube-shorts-transcript", name: "YouTube Shorts Transcript API", shortName: "Shorts Transcript", category: "transcript", method: "GET", path: "/v1/youtube/shorts/transcript", credits: 1 },
  { slug: "youtube-shorts-summarizer", name: "YouTube Shorts Summarizer API", shortName: "Shorts Summarizer", category: "summarize", method: "GET", path: "/v1/youtube/shorts/summarize", credits: 3 },
  { slug: "youtube-shorts-stats", name: "YouTube Shorts Stats API", shortName: "Shorts Stats", category: "details", method: "GET", path: "/v1/youtube/shorts/video-details", credits: 1 },
  { slug: "youtube-shorts-comments", name: "YouTube Shorts Comments API", shortName: "Shorts Comments", category: "comments", method: "GET", path: "/v1/youtube/shorts/comments", credits: 2 },
  { slug: "youtube-channel-shorts", name: "YouTube Channel Shorts API", shortName: "Channel Shorts", category: "list", method: "GET", path: "/v1/youtube/channel-shorts", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-trending-shorts", name: "YouTube Trending Shorts API", shortName: "Trending Shorts", category: "list", method: "GET", path: "/v1/youtube/trending-shorts", credits: 2 },
  { slug: "youtube-channel-streams", name: "YouTube Channel Streams API", shortName: "Channel Streams", category: "list", method: "GET", path: "/v1/youtube/channel-streams", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-hashtag-search", name: "YouTube Hashtag Search API", shortName: "Hashtag Search", category: "search", method: "GET", path: "/v1/youtube/hashtag-search", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-comment-replies", name: "YouTube Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/youtube/comment-replies", credits: 2 },
  { slug: "youtube-channel-playlists", name: "YouTube Channel Playlists API", shortName: "Channel Playlists", category: "list", method: "GET", path: "/v1/youtube/channel-playlists", credits: 2 },
  {
    slug: "youtube-community-posts",
    name: "YouTube Community Posts API",
    shortName: "Community Posts",
    category: "list",
    method: "GET",
    path: "/v1/youtube/community-posts",
    credits: 1,
    tagline:
      "List a YouTube channel's community posts — numeric likes, ISO dates, channel{}, linked video{}, cursor pagination (1 credit native).",
    longDescription:
      "Pass a channel URL, @handle, or UC… ID and get that channel's community /posts tab as clean JSON. Each post includes id/url, author + channel{id,title,url,handle}, text, likeCount (number) + likeCountText (e.g. \"3.2M\"; likeCountApproximate=true for compact K/M/B labels), publishedTime (ISO-8601; approximate when derived from YouTube's relative label) + publishedTimeText, postType, images[] / image, hashtags[], and when the post links a video — video{id,title,thumbnail,url,viewCountText,viewCountInt,lengthText,lengthSeconds} plus linkedVideos[]. Cursor pagination via nextCursor + hasMore. Flat 1 credit on the native path; Apify fallback bills about 0.5 credits per returned post (min 2).",
    delivers: [
      "Community posts with text, images, and post type",
      "likeCount number + likeCountText; ISO publishedTime + publishedTimeText",
      "channel{id,title,url,handle} and linked video{} when present",
      "Cursor pagination (nextCursor + hasMore); 1 credit native",
    ],
  },
  { slug: "youtube-community-post-details", name: "YouTube Community Post Details API", shortName: "Community Post Details", category: "details", method: "GET", path: "/v1/youtube/community-post-details", credits: 1 , tagline: "Get a YouTube community post — text, images, poll options, likes, and comments as structured JSON.", longDescription: "Paste a YouTube community post URL and get the post as clean JSON: the text, attached images, poll options when present, like and comment counts, publish date, and the channel that posted it. Use it to archive community updates, track polls, or feed a content calendar. No YouTube OAuth required. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  { slug: "youtube-video-sponsors", name: "YouTube Video Sponsors API", shortName: "Video Sponsors", category: "details", method: "GET", path: "/v1/youtube/video-sponsors", credits: 1 , tagline: "Find sponsor, self-promo, and interaction segments inside a YouTube video — start/end times and category for each segment.", longDescription: "Paste a YouTube video URL and get the sponsor and promo segments viewers have marked for that video: each segment includes a category (sponsor, self-promo, interaction, and similar), plus start and end timestamps. Useful for skipping ads in players, estimating brand-deal density, or cleaning footage for reuse. No YouTube OAuth required." },
];

const TIKTOK: Spec[] = [
  { slug: "tiktok-transcript", name: "TikTok Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/tiktok/transcript", credits: 2 },
  { slug: "tiktok-summarizer", name: "TikTok Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/tiktok/summarize", credits: 4 },
  { slug: "tiktok-video-details", name: "TikTok Video Details API", shortName: "Video Details", category: "details", method: "GET", path: "/v1/tiktok/video-details", credits: 1, tagline: "Get everything about one TikTok video from its URL — caption, view/like/comment/share/save counts, creator, sound, hashtags, and thumbnail.", longDescription: "Paste any public TikTok video URL and the TikTok Video Details API returns the full picture as clean JSON: the caption, when it was posted, how long it runs, and its engagement — views, likes, comments, shares, and saves. You also get the creator (username, display name, follower count, verified badge, and avatar), the sound/music name, the list of hashtags, and a thumbnail image. Use it to build analytics dashboards, track a campaign, or enrich a content database. This endpoint focuses on metadata and stats. No TikTok login and no proxies or infrastructure to maintain on your side. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Caption, publish date, and video duration", "Views, likes, comments, shares, and saves", "Creator profile — handle, name, followers, verified, avatar", "Sound name, hashtags, and thumbnail image"] },
  { slug: "tiktok-comments", name: "TikTok Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/tiktok/comments", credits: 2, tagline: "Get the comments on any TikTok video — text, author, avatar, likes, and timestamp for each one, with cursor pagination to page through them all.", longDescription: "Paste a public TikTok video URL and the TikTok Comments API returns its comments as clean JSON. Each comment includes the text, the author's username and avatar, how many likes it has, and when it was posted. The response also reports totalComments — the video's full comment count. Fetch up to 500 comments per call with the limit parameter, then pass the returned nextCursor value back in to page through the rest — a flat 2 credits per call, no matter how many comments you fetch. Need replies under a specific comment? Pass that comment's id to the TikTok Comment Replies API. Ideal for sentiment analysis, social listening, moderation, and spotting engaged fans. No TikTok login and no proxies or infrastructure to maintain on your side.", delivers: ["Comment text, author username, and avatar", "Like count and publish time per comment", "totalComments plus cursor pagination (nextCursor) through every comment", "limit up to 500 — a flat 2 credits per call", "Pair with Comment Replies to pull replies"] },
  { slug: "tiktok-channel-details", name: "TikTok Channel Details API", shortName: "Channel Details", category: "channel", method: "GET", path: "/v1/tiktok/channel-details", credits: 1 , tagline: "Get a TikTok profile's key stats — followers, following, likes, video count, bio, and verification." },
  { slug: "tiktok-profile-region", name: "TikTok Profile Region API", shortName: "Profile Region", category: "channel", method: "GET", path: "/v1/tiktok/profile-region", credits: 2 , tagline: "Find out where a TikTok creator is likely based and what language they use — country, language, and core profile stats.", longDescription: "Give the TikTok Profile Region API a profile URL, @handle, or username and it returns location and language as clean JSON. TikTok almost never shows an account's country publicly, so when that value is missing we estimate the country from public cues like the bio, display name, and language. The response tells you whether the country came from TikTok itself or from that estimate, and how confident the estimate is (high, medium, or low). You also get the interface language and core profile stats — followers, following, total likes, and video count — plus display name, verified and private flags, and the avatar. Use it for audience and geo analysis, content localization, compliance checks, or vetting creators before a partnership. Flat 2 credits per call. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Creator country — TikTok's own when available, otherwise an AI estimate", "Whether the country came from TikTok or was estimated, plus confidence", "Interface language plus followers, following, likes, and video count", "Display name, verified and private flags, and avatar"] },
  { slug: "tiktok-audience-demographics", name: "TikTok Audience Demographics API", shortName: "Audience Demographics", category: "channel", method: "GET", path: "/v1/tiktok/audience-demographics", credits: 3 , tagline: "See which countries a TikTok creator's audience comes from — a ranked country breakdown based on people who comment on their videos.", longDescription: "Give the TikTok Audience Demographics API a profile URL, @handle, or username and it returns a ranked country breakdown of the creator's audience as clean JSON. TikTok does not publish follower geography, but commenters often expose a country — so we sample people commenting on the creator's recent videos and tally countries into a list with country name, country code, count, and percentage. You also get how many videos and commenters were sampled. This reflects who engages, not a full follower census. Use it for market sizing, geo targeting, localization, and influencer vetting. Flat 3 credits per call. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Ranked countries with name, code, count, and percentage", "Country mix based on real commenters, not a follower census", "How many videos and commenters were sampled", "Computed from public TikTok engagement data"] },
  { slug: "tiktok-search-suggestions", name: "TikTok Search Suggestions API", shortName: "Search Suggestions", category: "search", method: "GET", path: "/v1/tiktok/search-suggestions", credits: 2, tagline: "Get the autocomplete terms TikTok suggests in its search bar for a keyword — the real phrases people search, ranked, so you can find trending queries and long-tail keyword ideas.", delivers: ["The autocomplete terms TikTok suggests for your keyword", "Each suggestion with its rank — the order it appears in the search bar", "A ready-to-open searchUrl that runs that exact search on TikTok", "The seed keyword plus the region and language it was localized for", "Localize by country + language to see what a specific market searches"] , longDescription: "Give the TikTok Search Suggestions API a seed keyword and it returns the autocomplete phrases TikTok shows in its search bar as clean JSON — the actual phrases people search for. Each suggestion includes the search term, its rank (1 = top of the list), a ready-to-open search URL, the seed keyword it came from, and the country and language it was localized for. Use the country and language parameters to see what a specific market is searching (for example US in English, or DE in German). Great for TikTok keyword research, trending queries, and content planning. No TikTok login required. Billed per suggestion returned. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  { slug: "tiktok-channel-posts", name: "TikTok Channel Posts API", shortName: "Channel Posts", category: "list", method: "GET", path: "/v1/tiktok/channel-posts", credits: 2, tagline: "Get the latest videos from any public TikTok profile — caption, view / like / comment counts, thumbnail, sound, and hashtags for each post, with cursor pagination to page through them all." , longDescription: "Send a profile URL, @handle, or username and the TikTok Channel Posts API returns that creator's most recent videos as clean, structured JSON. If TikTok blocks a direct fetch, the first page automatically retries through a backup path so you still get a response. Each post includes the TikTok page URL and video ID, caption, publish date, duration, thumbnail, hashtags, and the sound/music name, plus full engagement — views, likes, comments, shares, and saves — and the author's profile (username, display name, followers, verified badge, avatar). Fetch up to 200 posts per call with the limit parameter, then pass the returned nextCursor value back in to page through older videos (hasMore tells you when you've reached the end) — a flat 2 credits per call, no matter how many posts you fetch. Ideal for creator monitoring, content calendars, competitor tracking, and feeding analytics or influencer tools. This endpoint focuses on metadata and stats. No TikTok login and no infrastructure to maintain on your side.", delivers: ["Latest public videos from any TikTok profile", "Caption, publish date, duration, thumbnail, hashtags, and sound name", "Views, likes, comments, shares, and saves per video", "Author profile — handle, name, followers, verified, avatar", "Cursor pagination (nextCursor + hasMore) — flat 2 credits per call", "Automatic first-page backup if the direct fetch fails"] },
  { slug: "tiktok-comment-replies", name: "TikTok Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/tiktok/comment-replies", credits: 2, tagline: "Get the replies under any TikTok comment — text, author, likes, and timestamp for each one, with cursor pagination.", longDescription: "Pass a TikTok video URL and a parent comment id and get that comment's replies as clean JSON. Each reply includes text, author, like count, and publish time. Fetch up to 500 replies per call, then pass nextCursor to page through the rest — a flat 2 credits per call. No TikTok login required.", delivers: ["Reply text, author, and profile image", "Like count and publish time per reply", "Cursor pagination (nextCursor + hasMore)", "Flat 2 credits per call"] },
  { slug: "tiktok-user-followers", name: "TikTok User Followers API", shortName: "User Followers", category: "list", method: "GET", path: "/v1/tiktok/user-followers", credits: 20, creditsPerResult: 0.4 },
  { slug: "tiktok-user-followings", name: "TikTok User Followings API", shortName: "User Followings", category: "list", method: "GET", path: "/v1/tiktok/user-followings", credits: 20, creditsPerResult: 0.4 },
  { slug: "tiktok-music-posts", name: "TikTok Music Posts API", shortName: "Music Posts", category: "list", method: "GET", path: "/v1/tiktok/music-posts", credits: 2, tagline: "List TikTok videos that use a specific sound — caption, author, and engagement for each post.", longDescription: "Paste a TikTok music/sound URL and get the public videos that use that sound as structured JSON. Each result includes caption, author, thumbnail, and engagement counts. Use Song Details first if you only need the sound's metadata. Flat 2 credits per call." },
  { slug: "tiktok-top-search", name: "TikTok Top Search API", shortName: "Top Search", category: "search", method: "GET", path: "/v1/tiktok/top-search", credits: 2 , tagline: "Search TikTok's top mixed results for a keyword — videos and related hits ranked the way TikTok's search ranks them.", longDescription: "Pass a keyword and get TikTok's top mixed search results as structured JSON — the same style of ranked hits you see in TikTok search, not a single content type only. Each result includes the fields TikTok exposes for that hit (URL, caption or title, author, engagement when available). Flat 2 credits per call." },
  { slug: "tiktok-search-by-hashtag", name: "TikTok Search by Hashtag API", shortName: "Search by Hashtag", category: "search", method: "GET", path: "/v1/tiktok/search/hashtag", credits: 14, creditsPerResult: 0.7, tagline: "Search TikTok videos by hashtag — video URL, caption, author, and view / like / comment counts for each result, with cursor pagination to page through them all.", delivers: ["Public videos posted under your hashtag", "Video URL, caption, thumbnail, duration, and publish date", "Author profile plus view / like / comment / share / save counts", "Cursor pagination (nextCursor + hasMore) through every result"] , longDescription: "Pass a hashtag (with or without the #) and the TikTok Search by Hashtag API returns the videos posted under that tag as clean, structured JSON. Each result includes the video URL, caption, publish date, duration, thumbnail, the author's profile, and full engagement counts — views, likes, comments, shares, and saves — plus the hashtags and sound used. Need more than the first page? Pass the nextCursor value from the previous response to keep paging, and use hasMore to know when you've reached the end. An optional region parameter only chooses which country our request is sent from — it does not filter results by country. Use it to track a campaign or branded hashtag, discover trending content in a niche, or build a themed content feed. No TikTok login required. Billed per result — about 0.7 credits each." },
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
      "TikTok sound metadata — usageCount, artists[{id,secUid,handle}], commerce rights, chorus timing, audio analysis (1 credit native).",
    longDescription:
      "Paste a TikTok music/sound URL and get the sound as clean JSON: title, author, artists[{id,uid,secUid,handle,displayName,verified,avatarUrl}], duration, cover/coverUrl/playUrl, usageCount (videos using the sound — null when TikTok omits it on this path), createdAt, commerce flags (isCommerceMusic / hasCommerceRight / commercialRightType), isOriginalSound / isPgc, matchedSong.chorusInfo{startMs,durationMs}, musicReleaseInfo{isNewReleaseSong}, and extra{bpm,loudnessLufs,beats} when TikTok exposes them. Pair with Music Posts to list videos on the sound. Flat 1 credit on the native path; Apify fallback bills 2.",
    delivers: [
      "usageCount when TikTok exposes video-use totals",
      "artists[] with stable id / secUid / handle",
      "Commerce rights + matchedSong chorus timing",
      "Audio analysis (loudness / beats) when present; 1 credit native",
    ],
  },
  { slug: "tiktok-trending-feed", name: "TikTok Trending Feed API", shortName: "Trending Feed", category: "list", method: "GET", path: "/v1/tiktok/trending-feed", credits: 2 , tagline: "Get videos from TikTok's trending feed — caption, author, and engagement for each item. Flat 2 credits per call." },
  { slug: "tiktok-popular-hashtags", name: "TikTok Popular Hashtags API", shortName: "Popular Hashtags", category: "list", method: "GET", path: "/v1/tiktok/popular-hashtags", credits: 14, creditsPerResult: 0.7 , tagline: "Get currently popular TikTok hashtags — name and popularity signals for each tag." },
  { slug: "tiktok-live", name: "TikTok Live API", shortName: "Live", category: "details", method: "GET", path: "/v1/tiktok/live", credits: 1 , tagline: "Is this TikTok creator live right now — authoritative isLive/status, last room, and parsed stream qualities.", longDescription: "Send a TikTok profile URL or @handle and learn if that creator is currently live. isLive is true only when TikTok's liveRoom.status is 2 (also exposed as top-level status and room.status). When offline, room may still describe the last broadcast (title, startedAt, viewer/enter counts, stream pull URLs) — trust isLive/status, not a non-empty room. Response also includes creator.id / secUid / following, liveSubOnly, gameTagId / hashTagId when set, streamUrls[], streamQualities[{quality,codec,resolution,bitrate,flv,hls,dash}], and streams{hd,sd,ld,origin,ao,…}. Flat 1 credit per call. Live Info is the same payload at 7 credits for SC compatibility." },
  { slug: "tiktok-live-info", name: "TikTok Live Info API", shortName: "Live Info", category: "details", method: "GET", path: "/v1/tiktok/live-info", credits: 7 , tagline: "Same TikTok live payload as Live — status, room, parsed stream qualities — billed at 7 credits for SC compatibility.", longDescription: "Alias of TikTok Live with its own billing/cache key. Same authoritative isLive / status, creator.id/secUid, room fields, and parsed streamQualities / streams map. Prefer /live (1 credit) unless you need this path for compatibility. Flat 7 credits per call." },
  { slug: "tiktok-popular-creators", name: "TikTok Popular Creators API", shortName: "Popular Creators", category: "list", method: "GET", path: "/v1/tiktok/popular-creators", credits: 28, creditsPerResult: 1.4 , tagline: "Discover popular TikTok creators — handle, follower count, and profile fields for each account." },
];

const INSTAGRAM: Spec[] = [
  { slug: "instagram-transcript", name: "Instagram Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/instagram/transcript", credits: 2, tagline: "Turn any Instagram Reel's speech into text — the full transcript plus timestamped segments, ready for search, subtitles, or AI pipelines." , longDescription: "Send a Reel URL and the Instagram Transcript API returns everything spoken in the video as clean text: the full transcript, timestamped segments (start time and duration for each line), and word count. Auto-detects the spoken language, or pass an optional language code (like 'tr' or 'en') to pin it — recommended for short clips. Great for making Reels searchable, generating subtitles, feeding AI tools, or turning video into text. No Instagram login or OAuth required. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  { slug: "instagram-summarizer", name: "Instagram Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/instagram/summarize", credits: 4, tagline: "Get an AI summary of any Instagram Reel — a short paragraph plus key points, without watching the video.", longDescription: "Send a Reel URL and the Instagram Summarizer API transcribes the video and returns an AI-written summary as clean JSON: a concise paragraph plus a list of key points. Pass an optional language code (like 'tr') to pin the speech language and get the summary in that language — otherwise it auto-detects and summarizes in English. Perfect for content research at scale, briefing tools, and AI agents that need to understand video content without processing media. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  { slug: "instagram-details", name: "Instagram Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/instagram/details", credits: 1 , tagline: "Get an Instagram post or Reel — caption, likes, comments, media URLs, author, and publish date.", longDescription: "Paste an Instagram post or Reel URL and get the item as clean JSON: caption, like and comment counts, media URLs (image or video), author profile, duration when it is a Reel, and publish date. Use it for analytics dashboards, content databases, or campaign tracking. Flat 1 credit per call — no Instagram login or OAuth. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Caption, media URLs, and publish date", "Like and comment counts", "Author profile fields", "Duration for Reels when available"] },
  { slug: "instagram-comments", name: "Instagram Post Comments API", shortName: "Post Comments", category: "comments", method: "GET", path: "/v1/instagram/comments", credits: 45, creditsPerResult: 0.9, tagline: "Get the comments on any Instagram post or Reel — text, author, avatar, likes, and timestamp for each comment.", longDescription: "Send a post or Reel URL and the Instagram Post Comments API returns its comments as clean, structured JSON. Each comment includes the text, author username and avatar, like count, and when it was posted. Use the limit parameter (up to 500) to control how many you fetch — billing scales with results returned. Ideal for sentiment analysis, social listening, comment moderation, and finding engaged fans or customer feedback. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  { slug: "instagram-channel-details", name: "Instagram Channel Details API", shortName: "Channel Details", category: "channel", method: "GET", path: "/v1/instagram/channel-details", credits: 1, tagline: "Get any public Instagram profile's key stats in one call — followers, following, post count, bio, and verification status.", longDescription: "Send a profile URL or @handle and the Instagram Channel Details API returns the account's profile as clean, structured JSON: display name, bio, follower and following counts, total posts, profile image, and whether it's verified. It's the go-to endpoint for influencer vetting, competitor tracking, audience dashboards, and enriching user records with live Instagram stats. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  { slug: "instagram-channel-posts", name: "Instagram Channel Posts API", shortName: "Channel Posts", category: "list", method: "GET", path: "/v1/instagram/channel-posts", credits: 6, creditsPerResult: 0.3, tagline: "Get the latest posts from any public Instagram profile — caption, media URLs, likes, comments, and publish date for each post, with cursor pagination for older ones.", longDescription: "Send a profile URL or @handle and the Instagram Channel Posts API returns that account's most recent posts as clean, structured JSON. Each post includes the caption, image or video URLs, like and comment counts, post type, and publish date. Need more than the first page? Pass the nextCursor value from the previous response to keep paging through older posts. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  { slug: "instagram-channel-reels", name: "Instagram Channel Reels API", shortName: "Channel Reels", category: "list", method: "GET", path: "/v1/instagram/channel-reels", credits: 6, creditsPerResult: 0.3, tagline: "Get the latest Reels from any public Instagram profile — video URL, caption, views, likes, comments, and duration for each Reel, with cursor pagination for older ones.", longDescription: "Send a profile URL or @handle and the Instagram Channel Reels API returns that account's most recent Reels as clean, structured JSON. Photo and carousel posts are filtered out — you only get videos, each with its direct video URL, caption, view / like / comment counts, duration, and publish date. Need more than the first page? Pass the nextCursor value from the previous response to keep paging through older Reels. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  { slug: "instagram-reels-search", name: "Instagram Reels Search API", shortName: "Reels Search", category: "search", method: "GET", path: "/v1/instagram/reels-search", credits: 2, tagline: "Native Instagram Reels hashtag search — views + plays, author verified/followers, audio, location. Flat 2 credits.", longDescription: "Send a hashtag (without the #) or keyword and get matching Reels from Instagram's native hashtag grid as clean JSON — videos only. Same enriched shape as Hashtag Search: author (verified, profileImage, followers, postCount), engagement.views plus engagement.plays when Instagram exposes both, music{}, location{}, paid/ad/affiliate flags, preview comments when present, duration, and publish date. Optional datePosted=last_24_hours|last_week|last_month|last_year. Flat 2 credits per call (same as hashtag-search). Pass cache=true for the 24h shared cache." },
  { slug: "instagram-trending-reels", name: "Instagram Trending Reels API", shortName: "Trending Reels", category: "list", method: "GET", path: "/v1/instagram/trending-reels", credits: 28, creditsPerResult: 1.4, tagline: "Get the Reels currently trending on Instagram's Explore feed for a chosen country — video URL, caption, author, views, likes, and comments for each one.", longDescription: "The Instagram Trending Reels API returns what's blowing up on Instagram right now. Pass a country name (default United States) and you get the Reels currently featured on that country's Explore feed as clean, structured JSON — each with its direct video URL, caption, author profile, and view / like / comment counts. No hashtag or keyword needed: this is Instagram's own trending selection, useful for spotting viral content, tracking trends by region, or seeding content-research tools. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  {
    slug: "instagram-tagged-posts",
    name: "Instagram Tagged Posts API",
    shortName: "Tagged Posts",
    category: "list",
    method: "GET",
    path: "/v1/instagram/tagged-posts",
    credits: 1,
    tagline:
      "Posts that tag an Instagram account — author id, views, hashtags/mentions, cursor pagination (1 credit native).",
    longDescription:
      "Pass a profile URL or @handle (no numeric user_id required) and get the profile's Tagged tab as clean JSON: each post includes id/shortcode, postType, caption, publishedAt, author{id,username,displayName,url}, engagement{views,likes,comments}, hashtags[], and mentions[]. Cursor pagination via nextCursor + hasMore (same shape as channel-posts). Flat 1 credit on the native usertags path; Apify fallback bills about 0.9 credits per returned post (min 2). Note: Instagram's usertags feed only returns tags the account still exposes — some large brands (e.g. natgeo) surface a truncated historical window while accounts like nasa return recent UGC.",
    delivers: [
      "author.id + username for the tagging creator",
      "engagement.views on video/Reel tags when Instagram exposes them",
      "hashtags[] / mentions[] / postType",
      "Cursor pagination (nextCursor + hasMore)",
    ],
  },
  { slug: "instagram-reels-by-audio-id", name: "Instagram Reels By Audio ID API", shortName: "Reels By Audio ID", category: "list", method: "GET", path: "/v1/instagram/reels-by-audio-id", credits: 28, creditsPerResult: 1.4, tagline: "Give it an Instagram sound and get back every Reel that uses it — each with its video, caption, creator, and view / like / comment counts.", longDescription: "On Instagram every Reel is built on an audio track, and each track has its own page listing the Reels that use it. This API takes that sound — either the numeric audio ID (the musicId you see on a Reel) or a full audio-page URL like https://www.instagram.com/reels/audio/AUDIO_ID/ — and returns those Reels as clean JSON. For each Reel you get a direct video URL, caption, the creator's profile, play / like / comment counts, duration, and publish date. Use it to see how far a trending sound has spread, find every creator who used your music, or measure a branded-audio campaign. No Instagram login, no OAuth, and no infrastructure to maintain. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Every public Reel made with that audio track", "Direct MP4 video URL and thumbnail for each Reel", "Caption, duration, publish date, and the sound's audio ID", "Creator handle plus play / like / comment counts"] },
  { slug: "instagram-hashtag-search", name: "Instagram Hashtag Search API", shortName: "Hashtag Search", category: "search", method: "GET", path: "/v1/instagram/hashtag-search", credits: 2, tagline: "Native Instagram hashtag grid — posts with media, caption, author followers, views, paid-partnership flags, audio, and location. Flat 2 credits per call.", longDescription: "Pass a hashtag without the # (e.g. travel or foodie) and the Instagram Hashtag Search API returns the public posts and Reels from that tag's Explore grid as clean JSON — the same grid you'd see on the hashtag's page in the app (not a Google-indexed subset). Each result includes the post URL, media type, caption, author (with followers / postCount when available), like / comment / view counts, paid-partnership / ad / affiliate flags, audio (musicId), location, sample preview comments, a thumbnail, and hashtags / @mentions. Optional mediaType=reels filters to Reels only. Use it to track a campaign or branded hashtag, separate organic from sponsored hits, discover creators by size, or watch a trend grow. No Instagram login, no OAuth, and no infrastructure to maintain. Flat 2 credits per call. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Native hashtag grid posts and Reels (not Google index)", "Author followers / postCount plus like / comment / view counts", "isPaidPartnership / isAd / isAffiliate flags", "musicId, location, previewComments, mediaType=reels filter"] },
  { slug: "instagram-profile-search", name: "Instagram Profile Search API", shortName: "Profile Search", category: "search", method: "GET", path: "/v1/instagram/profile-search", credits: 1, tagline: "Look up an Instagram account by name or @handle and get its profile back — display name, follower count, verified badge, private flag, and avatar.", delivers: ["The public Instagram profile that matches your query", "Username, display name, and profile URL", "Follower count plus verified and private flags", "Profile picture URL"] , longDescription: "Pass an account name, @handle, or profile URL (e.g. nike, @nasa, or instagram.com/natgeo) and the Instagram Profile Search API resolves it to the matching public profile as clean JSON. It returns the account itself, not its posts: username, display name, profile URL, follower count, whether the account is verified or private, and the profile picture. Use it to turn a brand or creator name into a confirmed @handle, enrich a CRM or lead list, or feed an influencer-discovery tool. Fast and costs just 1 credit — no Instagram login or OAuth. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  { slug: "instagram-embed", name: "Instagram Embed HTML API", shortName: "Embed HTML", category: "details", method: "GET", path: "/v1/instagram/embed", credits: 1, tagline: "Get Instagram's own self-contained embed HTML for any post, reel, or profile — ready to drop into an iframe on your site.", longDescription: "Pass an Instagram post, reel, or profile URL (or an @handle) and get back Instagram's own self-contained embed page as ready-to-use HTML — the full <html> document Instagram serves at /embed/, which you can drop straight into an <iframe srcdoc> or render server-side. The response also returns embedUrl, so you can point an <iframe src> at it directly instead. Posts and reels come back as a rich media card (with caption); profiles come back as a profile card that links to the account. No login or OAuth needed — it's fast, costs just 1 credit. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh. If Instagram's embed page is ever unavailable, the response falls back to the classic blockquote + embed.js snippet.", delivers: ["Instagram's full self-contained embed HTML document", "embedUrl you can load directly in an <iframe src>", "Canonical Instagram permalink for the post/reel/profile", "Type flag (post/reel/profile) plus shortcode or username"] },
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
      "Pass an Instagram numeric user ID (e.g. 13460080) or a profile URL / @handle and get that account's public profile as clean Captapi JSON — same naming as Channel Details: displayName, bio, followers / following / postCount, verified, isPrivate, profileImage / profileImageHd, externalUrl, bioLinks[], categoryName, isBusinessAccount / isProfessionalAccount, businessAddress{cityName,streetAddress,zipCode,…}, fbid, highlightReelCount, hasClips, and transparency flags when Instagram exposes them. Empty/null fields are omitted. Flat 1 credit. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.",
    delivers: [
      "camelCase profile fields (displayName, followers, verified, …)",
      "externalUrl + bioLinks[] when present",
      "Business address / category for business accounts",
      "Lookup by numeric user ID or @handle (1 credit)",
    ],
  },
];

const FACEBOOK: Spec[] = [
  { slug: "facebook-details", name: "Facebook Details API", shortName: "Details", category: "details", method: "GET", path: "/v1/facebook/details", credits: 2, tagline: "Facebook post or Reel — caption, engagement, author id, SD/HD video, captions, and music when Facebook exposes them.", longDescription: "Paste a Facebook post or Reel URL and get clean JSON: caption, publishedAt, engagement, author (including stable author.id when present), videoUrl plus additive videoSdUrl/videoHdUrl, videoWidth/videoHeight, captionsUrl (.srt), feedbackId, and music when available. Note: for some Reels, the view count on the individual post page can be null or lower than the public Reels grid badge — use Facebook Profile Reels and match by post id if you need that badge count. Flat 2 credits per call." },
  { slug: "facebook-summarizer", name: "Facebook Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/facebook/summarize", credits: 4 },
  { slug: "facebook-comments", name: "Facebook Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/facebook/comments", credits: 2 },
  { slug: "facebook-page-details", name: "Facebook Page Details API", shortName: "Page Details", category: "channel", method: "GET", path: "/v1/facebook/page-details", credits: 2 },
  { slug: "facebook-profile-posts", name: "Facebook Profile Posts API", shortName: "Profile Posts", category: "list", method: "GET", path: "/v1/facebook/profile-posts", credits: 2 },
  { slug: "facebook-profile-reels", name: "Facebook Profile Reels API", shortName: "Profile Reels", category: "list", method: "GET", path: "/v1/facebook/profile-reels", credits: 2 },
  { slug: "facebook-group-posts", name: "Facebook Group Posts API", shortName: "Group Posts", category: "list", method: "GET", path: "/v1/facebook/group-posts", credits: 2 },
  { slug: "facebook-comment-replies", name: "Facebook Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/facebook/comment-replies", credits: 2 },
  { slug: "facebook-profile-photos", name: "Facebook Profile Photos API", shortName: "Profile Photos", category: "list", method: "GET", path: "/v1/facebook/profile-photos", credits: 2 },
];

const FACEBOOK_MARKETPLACE: Spec[] = [
  { slug: "facebook-marketplace-search", name: "Facebook Marketplace Search API", shortName: "Marketplace Search", category: "search", method: "GET", path: "/v1/facebook/marketplace-search", credits: 2, tagline: "Search Facebook Marketplace by keyword and city name — price filters, sort, condition, radius, and createdAt. Flat 2 credits.", longDescription: "Search Facebook Marketplace with a product keyword and a city/place name (no lat/lng required). Each result includes title, price (+ priceAmount in minor units), strikethrough price when discounted, categoryId, location, deliveryTypes, isSold/isLive/isPending/isHidden, cover photo, and createdAt. Optional filters: minPrice, maxPrice, sortBy, daysSinceListed, condition, deliveryMethod, availability, radiusMiles, category. Cursor pagination via nextCursor/hasMore within the fetched SSR page. Default list path is flat 2 credits and already includes the cover photo. Pass details=true for description, condition, coordinates, and the full photo gallery — billed as 2 + 2 credits per listing." },
  { slug: "facebook-marketplace-location-search", name: "Facebook Marketplace Location Search API", shortName: "Marketplace Locations", category: "search", method: "GET", path: "/v1/facebook/marketplace-location-search", credits: 2 },
  { slug: "facebook-marketplace-item", name: "Facebook Marketplace Item API", shortName: "Marketplace Item", category: "details", method: "GET", path: "/v1/facebook/marketplace-item", credits: 2 , tagline: "Get a Facebook Marketplace listing — title, price, condition, and location as structured JSON.", longDescription: "Paste a Facebook Marketplace item URL and get the listing as clean JSON: title, price, description, condition, delivery types, photos, and location when available. Flat 2 credits per call." },
];

const FACEBOOK_EVENTS: Spec[] = [
  { slug: "facebook-event-search", name: "Facebook Event Search API", shortName: "Event Search", category: "search", method: "GET", path: "/v1/facebook/event-search", credits: 2 },
  { slug: "facebook-event-details", name: "Facebook Event Details API", shortName: "Event Details", category: "details", method: "GET", path: "/v1/facebook/event-details", credits: 2 , tagline: "Get a Facebook event — title, time, place, host, and attendance signals as structured JSON.", longDescription: "Paste a Facebook event URL and get the event details as clean JSON: title, description, start/end time, location, host page, and interest or going counts when available. Flat 2 credits per call." },
  { slug: "facebook-profile-events", name: "Facebook Profile Events API", shortName: "Profile Events", category: "list", method: "GET", path: "/v1/facebook/profile-events", credits: 2 },
];

const TWITTER: Spec[] = [
  { slug: "twitter-tweet-details", name: "Twitter/X Tweet Details API", shortName: "Tweet Details", category: "details", method: "GET", path: "/v1/twitter/tweet-details", credits: 1 , tagline: "Get a tweet — text, author, likes, replies, and media as structured JSON.", longDescription: "Paste a tweet URL and get the tweet as clean JSON: text, author, like / reply counts, media when present, and publish time. Flat 1 credit per call." },
  { slug: "twitter-transcript", name: "Twitter/X Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/twitter/transcript", credits: 1 },
  {
    slug: "twitter-profile",
    name: "Twitter/X Profile API",
    shortName: "Profile",
    category: "channel",
    method: "GET",
    path: "/v1/twitter/profile",
    credits: 1,
    tagline:
      "X profile with verification triad — blue check, identity verified, affiliate label — plus listed/media/likes counts.",
    longDescription:
      "Paste a profile URL or @handle and get the public X profile as clean JSON: username, name, bio, location, website, followers/following/tweetCount, likesCount/mediaCount/listedCount, pinnedTweetIds, bannerImage, profileImageShape, and ISO createdAt. Verification is explicit: verified + isBlueVerified + isIdentityVerified + verification{verifiedType, reason, verifiedSince} and affiliate{description,url,badgeUrl} when X exposes an org affiliation. Also returns bioUrls[], highlightedTweets, creatorSubscriptionsCount, businessAffiliatesCount, and possiblySensitive when present. Flat 1 credit. Pass cache=true for the 24h shared cache.",
    delivers: [
      "Blue check vs identity vs affiliate verification",
      "listedCount, mediaCount, likesCount, pinnedTweetIds",
      "bannerImage + bioUrls + ISO createdAt",
    ],
  },
  { slug: "twitter-user-tweets", name: "Twitter/X User Tweets API", shortName: "User Tweets", category: "list", method: "GET", path: "/v1/twitter/user-tweets", credits: 2, tagline: "List recent tweets from a Twitter/X profile — text, author, likes, reposts, hashtags, and media. Flat 2 credits per call.", longDescription: "Pass a profile URL or @handle and get recent public tweets as clean JSON. Each result includes the tweet URL and id, full text, language, publish time, the author (username, display name, followers, verified, avatar), engagement (likes, replies, retweets, quotes when available), reply/retweet flags, hashtags, and media URLs when present. Flat 2 credits per call. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
  { slug: "twitter-search", name: "Twitter/X Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/twitter/search", credits: 2, tagline: "Search public tweets on X by keyword — text, author, likes, reposts, hashtags, and media for each matching post. Flat 2 credits per call.", longDescription: "Pass a keyword or phrase and the Twitter/X Search API returns matching public tweets as clean JSON. Each result includes the tweet URL and id, full text, language, publish time, the author (username, display name, followers, verified, avatar), engagement (views, likes, replies, retweets, quotes, bookmarks), reply/retweet flags, hashtags, and media URLs when present. Use it for topic monitoring, brand listening, or content discovery on X. Flat 2 credits per call. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Public tweets matching your keyword", "Tweet URL, text, language, and publish time", "Author profile — handle, name, followers, verified, avatar", "Views, likes, replies, retweets, quotes, bookmarks, hashtags, and media"] },
  { slug: "twitter-community", name: "Twitter/X Community API", shortName: "Community", category: "details", method: "GET", path: "/v1/twitter/community", credits: 1 , tagline: "Get a Twitter/X Community — name, description, member count, and rules as structured JSON.", longDescription: "Paste a Twitter/X Community URL and get the community metadata as clean JSON: name, description, member count, and related fields when available. Pair with Community Tweets to list posts inside it." },
  { slug: "twitter-community-tweets", name: "Twitter/X Community Tweets API", shortName: "Community Tweets", category: "list", method: "GET", path: "/v1/twitter/community-tweets", credits: 18, creditsPerResult: 0.7, tagline: "List recent posts from a Twitter/X Community — text, author, engagement, and media.", longDescription: "Pass a Community URL or ID and get recent posts as clean JSON. Each result includes tweet text, author, engagement, and media when present. Billed per result — about 0.7 credits each." },
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
  { slug: "reddit-post-transcript", name: "Reddit Post Transcript API", shortName: "Post Transcript", category: "transcript", method: "GET", path: "/v1/reddit/post-transcript", credits: 2 , tagline: "Get a Reddit post's discussion as readable text — title, body, and comments in one transcript-style payload. Flat 2 credits per call.", longDescription: "Paste a Reddit post URL and get the discussion as structured text: the post title and body plus comments flattened into a transcript-style response. This is discussion text, not speech-to-text from a video. Flat 2 credits per call." },
  { slug: "reddit-search", name: "Reddit Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/reddit/search", credits: 2, tagline: "Search Reddit posts site-wide by keyword — title, text, subreddit, author, upvotes, and comments, with cursor pagination. Flat 2 credits per call.", longDescription: "Pass a keyword or phrase and the Reddit Search API returns matching public posts from across Reddit as clean JSON — the same kind of site-wide search you'd run on reddit.com. Each result includes the post URL and id, title, body text when present, subreddit, author, upvotes, comment count, publish time, NSFW flag, flair, and thumbnail when available. Need more than the first page? Pass the nextCursor value from the previous response to keep paging, and use hasMore to know when you've reached the end. To search inside one community only, use Reddit Subreddit Search instead. Flat 2 credits per call. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Public Reddit posts matching your keyword across all of Reddit", "Title, body text, subreddit, author, and post URL", "Upvotes, comment count, publish time, NSFW flag, and thumbnail", "Cursor pagination (nextCursor + hasMore) through every page"] },
  { slug: "reddit-subreddit-details", name: "Reddit Subreddit Details API", shortName: "Subreddit Details", category: "details", method: "GET", path: "/v1/reddit/subreddit-details", credits: 1 , tagline: "Get a subreddit — title, description, subscribers, and community rules signals as structured JSON." },
  { slug: "reddit-subreddit-search", name: "Reddit Subreddit Search API", shortName: "Subreddit Search", category: "search", method: "GET", path: "/v1/reddit/subreddit-search", credits: 2 },
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
      "Threads profile — bio, followers, verified, isPrivate, bioLinks, transparencyLabel, and HD avatar versions (1 credit).",
    longDescription:
      "Pass a Threads profile URL or @handle and get the public profile as clean JSON: id, username, name, bio, followers, verified, profileImage, plus isThreadsOnlyUser (Threads-only vs Instagram-linked when Meta exposes it), isPrivate, bioLinks[], transparencyLabel, profileImageVersions[] ({url,width,height}), and hasOnboarded. Flat 1 credit. following and post counts are not publicly exposed on this surface (same gap as ScrapeCreators).",
  },
  { slug: "threads-user-posts", name: "Threads User Posts API", shortName: "User Posts", category: "list", method: "GET", path: "/v1/threads/user-posts", credits: 14, creditsPerResult: 0.7 },
  { slug: "threads-post-details", name: "Threads Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/threads/post-details", credits: 1 , tagline: "Get a Threads post — text, author, likes, replies, and media as structured JSON." },
  { slug: "threads-search", name: "Threads Post Search API", shortName: "Post Search", category: "search", method: "GET", path: "/v1/threads/search", credits: 18, creditsPerResult: 0.7, tagline: "Search public Threads posts by keyword — text, author, likes, replies, and media for each matching post.", longDescription: "Pass a keyword or phrase and the Threads Post Search API returns matching public posts as clean JSON. Each result includes the post URL and id, the text, when it was published, the author (username, display name, verified), engagement (likes, replies, reposts, quotes), and media URLs when the post has images or video. Use it for topic monitoring, brand listening, or content discovery on Threads. Path stays /v1/threads/search. Billed per result — about 0.7 credits each. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Public Threads posts matching your keyword", "Post URL, text, and publish time", "Author username, display name, and verified flag", "Likes, replies, reposts, quotes, and media URLs"] },
  { slug: "threads-search-users", name: "Threads Search Users API", shortName: "Search Users", category: "search", method: "GET", path: "/v1/threads/search-users", credits: 14, creditsPerResult: 0.7, tagline: "Find Threads profiles by keyword — username, display name, profile URL, and verified flag for each match.", longDescription: "Pass a keyword and the Threads Search Users API returns distinct Threads profiles related to that topic as clean JSON. Each result includes username, display name, a ready-to-open profile URL (threads.net/@handle), and whether the account is verified. This endpoint does not include follower counts or avatars — call Threads Profile with the returned URL or @handle for full profile stats. Use it to discover creators in a niche, turn a name into a confirmed @handle, or seed a lead list. Billed per result — about 0.7 credits each. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Distinct Threads users matching your keyword", "Username, display name, and verified flag", "Canonical profile URL for each user", "Pair with Threads Profile for followers and avatar"] },
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
      "Give a Bluesky profile URL, @handle, or handle and get the public AT Protocol profile as clean JSON: platform, handle, url, did, name, bio, followers/following/posts, avatar, banner, createdAt/indexedAt, plus verified + verification{verifications[], verifiedStatus, trustedVerifierStatus}, moderation labels[], and associated{lists, feedgens, starterPacks, labeler} so you can tell feed/labeler service accounts from people. Flat 1 credit per call.",
    delivers: [
      "Handle, DID, display name, bio, avatar, and banner",
      "Follower, following, and post counts",
      "verified + verification{} (issuer, validity, trusted verifier status)",
      "Moderation labels[] and associated{lists, feedgens, starterPacks, labeler}",
    ],
  },
  { slug: "bluesky-user-posts", name: "Bluesky User Posts API", shortName: "User Posts", category: "list", method: "GET", path: "/v1/bluesky/user-posts", credits: 3, creditsPerResult: 0.1, tagline: "Get recent posts from any Bluesky profile — text, author, likes, reposts, replies, and embeds, with cursor pagination.", longDescription: "Send a Bluesky profile URL, @handle, or handle and the Bluesky User Posts API returns that account's recent posts as clean JSON. Each post includes the Bluesky URL and AT URI, text, publish time, the author (handle, display name, DID, avatar), engagement (likes, reposts, replies, quotes), and embed details when the post has a link, image, or quote. Need more than the first page? Pass the nextCursor value from the previous response to keep paging, and use hasMore to know when you've reached the end. Ideal for creator monitoring, content calendars, and feeding analytics tools. Billed per result — about 0.1 credits each. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Recent public posts from any Bluesky profile", "Post URL, AT URI, text, and publish time", "Author handle, display name, DID, and avatar", "Likes, reposts, replies, quotes, and embeds when present", "Cursor pagination (nextCursor + hasMore) through older posts"] },
  { slug: "bluesky-post-details", name: "Bluesky Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/bluesky/post-details", credits: 1 , tagline: "Get a Bluesky post — text, author, likes, reposts, and replies as structured JSON." },
];

const PINTEREST: Spec[] = [
  { slug: "pinterest-pin-details", name: "Pinterest Pin Details API", shortName: "Pin Details", category: "details", method: "GET", path: "/v1/pinterest/pin-details", credits: 1, tagline: "Get a Pinterest pin — title, description, link, board, origin creator, and engagement as structured JSON.", longDescription: "Pass a Pinterest pin URL and get clean JSON: title, description, seoAltText, link/destinationUrl, createdAt (ISO-8601), board{name,url,pinCount,followers}, author (board pinner), originAuthor (native creator / original uploader), saves plus repinCount/shareCount/reactionCount, image plus images{236x,564x,originals}. Flat 1 credit. Fields Pinterest does not expose on a given pin stay omitted/null." },
  { slug: "pinterest-user-pins", name: "Pinterest User Pins API", shortName: "User Pins", category: "list", method: "GET", path: "/v1/pinterest/user-pins", credits: 13, creditsPerResult: 0.5 },
  { slug: "pinterest-search", name: "Pinterest Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/pinterest/search", credits: 13, creditsPerResult: 0.5 },
  { slug: "pinterest-board", name: "Pinterest Board API", shortName: "Board", category: "list", method: "GET", path: "/v1/pinterest/board", credits: 13, creditsPerResult: 0.5 },
  { slug: "pinterest-user-boards", name: "Pinterest User Boards API", shortName: "User Boards", category: "list", method: "GET", path: "/v1/pinterest/user-boards", credits: 13, creditsPerResult: 0.5 },
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
      "Public LinkedIn person profile — name, headline, about, followers, and company — without SEO meta pollution.",
    longDescription:
      "Return a public LinkedIn person profile as clean JSON. about comes from the real profile bio (JSON-LD), not LinkedIn's og:description SEO blurb. connections are only returned when LinkedIn exposes a trustworthy count (never the fake “N connections on LinkedIn” meta placeholder). When the Apify fallback has experience/education sections, those arrays are included additively. Native path bills 1 credit; catalog list price is 2.",
  },
  { slug: "linkedin-company", name: "LinkedIn Company API", shortName: "Company", category: "channel", method: "GET", path: "/v1/linkedin/company", credits: 2 },
  { slug: "linkedin-post-details", name: "LinkedIn Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/linkedin/post-details", credits: 1 , tagline: "Get a LinkedIn post — text, author, reactions, and comments count as structured JSON." },
  { slug: "linkedin-post-transcript", name: "LinkedIn Post Transcript API", shortName: "Post Transcript", category: "transcript", method: "GET", path: "/v1/linkedin/post-transcript", credits: 1 },
  { slug: "linkedin-company-posts", name: "LinkedIn Company Posts API", shortName: "Company Posts", category: "list", method: "GET", path: "/v1/linkedin/company-posts", credits: 16, creditsPerResult: 0.8, tagline: "Get recent public posts from any LinkedIn company page — text, author, engagement, and publish time — with cursor pagination (nextCursor + hasMore) up to 100 posts.", longDescription: "Pass a LinkedIn company URL and get that page's recent public posts as structured JSON. Each post includes the LinkedIn URL and activity id, text, publish time, the company author, and engagement when available. Need more than the first page? Pass the nextCursor value from the previous response to keep paging (numeric offset), and use hasMore to know when you've reached the end — up to 100 posts total. Billed per result. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh." },
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
      "Rumble video metadata — real likes/comments (null when unknown), durationSeconds, captions, and media qualities.",
    longDescription:
      "Paste a Rumble video URL and get clean JSON: title, description, views, likes/dislikes/comments (null when Rumble does not expose them — never fake zeros), duration + durationSeconds, publishedAt, thumbnail, width/height, channel name/url/handle plus channelFollowers and channelVerified, numericId/embedId/shareUrl/embedUrl, captions (language → .vtt path), media (mp4 and/or tar qualities, timeline, audio, hls — each with bitrate/size/resolution when present), and a flat streams[] list. Flat 1 credit. Pass cache=true for the 24h shared cache.",
    delivers: [
      "Engagement counts stay null when unknown (no fake zeros)",
      "durationSeconds plus human duration string",
      "captions{} with .vtt paths and media{mp4|tar,timeline,audio,hls}",
      "channelFollowers + channelVerified without a second channel call",
    ],
  },
  { slug: "rumble-channel-videos", name: "Rumble Channel Videos API", shortName: "Channel Videos", category: "list", method: "GET", path: "/v1/rumble/channel-videos", credits: 12, creditsPerResult: 0.6 },
  { slug: "rumble-search", name: "Rumble Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/rumble/search", credits: 12, creditsPerResult: 0.6 },
  { slug: "rumble-comments", name: "Rumble Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/rumble/comments", credits: 2 },
];

const TIKTOK_SHOP: Spec[] = [
  {
    slug: "tiktok-shop-search",
    name: "TikTok Shop Search API",
    shortName: "Shop Search",
    category: "search",
    method: "GET",
    path: "/v1/tiktok-shop/shop-search",
    credits: 56,
    creditsPerResult: 2.8,
    tagline:
      "TikTok Shop keyword search — price, originalPrice/discount, sold, rating/reviews, and seller id.",
    longDescription:
      "Search TikTok Shop by keyword and get products as clean JSON: id, url, title, price + originalPrice/discount, currency, sold, rating + reviews when TikTok exposes them, image, and seller{id,name,url}. Pass region (default US). Native path bills a flat 2 credits when it succeeds; Apify fallback is about 2.8 credits per result (e.g. ~56 for limit=20). String fields are HTML-entity decoded (&amp; → &). Pass cache=true for the 24h shared cache.",
    delivers: [
      "rating + reviews on search hits when available",
      "originalPrice + discount alongside sale price",
      "seller.id / name / url",
    ],
  },
  { slug: "tiktok-shop-products", name: "TikTok Shop Products API", shortName: "Shop Products", category: "list", method: "GET", path: "/v1/tiktok-shop/shop-products", credits: 2 },
  {
    slug: "tiktok-shop-product-details",
    name: "TikTok Shop Product Details API",
    shortName: "Product Details",
    category: "details",
    method: "GET",
    path: "/v1/tiktok-shop/product-details",
    credits: 14,
    tagline:
      "TikTok Shop product — float price + currency, seller id, originalPrice/discount, SKUs, and region.",
    longDescription:
      "Get a TikTok Shop PDP as structured JSON: title, numeric price + currency, originalPrice/discount when unmasked, stock, rating/reviews, seller id/url/rating, skus[], and images. Pass region (default US) for the Apify fallback market. Native HTML path bills 2 credits when it succeeds; Apify fallback is 14. Related affiliate videos are included when upstream provides them.",
  },
  { slug: "tiktok-shop-product-reviews", name: "TikTok Shop Product Reviews API", shortName: "Product Reviews", category: "comments", method: "GET", path: "/v1/tiktok-shop/product-reviews", credits: 45, creditsPerResult: 2.25 },
  { slug: "tiktok-shop-user-showcase", name: "TikTok Shop User Showcase API", shortName: "User Showcase", category: "list", method: "GET", path: "/v1/tiktok-shop/user-showcase", credits: 45, creditsPerResult: 2.25, tagline: "List products a TikTok creator is promoting in their Shop showcase — product URL, title, price, image, and seller shop id for each item.", longDescription: "Pass a TikTok username (with or without @, or a profile URL) and the TikTok Shop User Showcase API returns the products that creator is featuring in their TikTok Shop showcase as clean JSON. This is the affiliate / creator storefront shelf — not the full inventory of a brand store. Each product includes the product URL and id, title, price, currency, thumbnail image, and the seller's shop id when available. For a brand's full catalog, use TikTok Shop Products with a store URL instead. For deeper product fields (stock, seller rating), call Product Details with a product URL. Billed per result — about 2.25 credits each. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.", delivers: ["Products a TikTok creator is promoting in their Shop showcase", "Product URL, id, title, price, currency, and image", "Seller shop id when TikTok exposes it", "Useful for affiliate tracking and creator commerce research", "Not a full brand store catalog — use Shop Products for that"] },
];

const GITHUB: Spec[] = [
  { slug: "github-user", name: "GitHub User API", shortName: "User", category: "channel", method: "GET", path: "/v1/github/user", credits: 1, tagline: "GitHub public profile — login, bio, email when public, followers, and repos as clean JSON (1 credit).", longDescription: "Pass a GitHub username or profile URL and get the public /users/{username} profile as camelCase JSON: login, name, company, blog, location, email (only when the user made it public), bio, avatar, publicRepos/publicGists, followers/following, twitterUsername, hireable, nodeId, siteAdmin, and createdAt/updatedAt. type is user or organization. Flat 1 credit. Honesty note: this wraps GitHub's free public REST API (5,000 req/hour with a personal access token). Prefer Captapi for one-key multi-platform workflows; call api.github.com directly for GitHub-only jobs so you do not spend credits on free data." },
  { slug: "github-repositories", name: "GitHub Repositories API", shortName: "Repositories", category: "list", method: "GET", path: "/v1/github/repositories", credits: 12, creditsPerResult: 0.4 },
  { slug: "github-pull-requests", name: "GitHub Pull Requests API", shortName: "Pull Requests", category: "list", method: "GET", path: "/v1/github/pull-requests", credits: 12, creditsPerResult: 0.4 },
  { slug: "github-activity", name: "GitHub Activity API", shortName: "Activity", category: "list", method: "GET", path: "/v1/github/activity", credits: 12, creditsPerResult: 0.4 , tagline: "List a GitHub user's recent public activity — pushes, issues, pull requests, and similar events." },
  { slug: "github-followers", name: "GitHub Followers API", shortName: "Followers", category: "list", method: "GET", path: "/v1/github/followers", credits: 12, creditsPerResult: 0.4 },
  { slug: "github-following", name: "GitHub Following API", shortName: "Following", category: "list", method: "GET", path: "/v1/github/following", credits: 12, creditsPerResult: 0.4 },
  { slug: "github-contributions", name: "GitHub Contributions API", shortName: "Contributions", category: "details", method: "GET", path: "/v1/github/contributions", credits: 3 , tagline: "Get a GitHub user's contribution activity — contribution counts and calendar-style signals as structured JSON.", longDescription: "Pass a GitHub username or profile URL and get contribution activity as clean JSON — useful for developer profiling and hiring screens. Flat 3 credits per call." },
  { slug: "github-repository", name: "GitHub Repository API", shortName: "Repository", category: "details", method: "GET", path: "/v1/github/repository", credits: 3 , tagline: "Get a GitHub repository — description, stars, forks, language, license, and topics as structured JSON.", longDescription: "Pass a repository URL or owner/name and get the repo metadata as clean JSON: description, stars, forks, open issues, primary language, license, topics, and timestamps. Flat 3 credits per call." },
  { slug: "github-trending-repositories", name: "GitHub Trending Repositories API", shortName: "Trending Repositories", category: "search", method: "GET", path: "/v1/github/trending-repositories", credits: 12, creditsPerResult: 0.6 },
  { slug: "github-trending-developers", name: "GitHub Trending Developers API", shortName: "Trending Developers", category: "search", method: "GET", path: "/v1/github/trending-developers", credits: 12, creditsPerResult: 0.6 },
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
      "Twitch channel — live stream, last broadcast, recent videos with embedUrl, game box art, and storyboard previews (1 credit).",
    longDescription:
      "Pass a Twitch channel URL or username and get a clean profile: id, login, displayName, description, followers, profileImage/bannerImage, isPartner/isAffiliate, createdAt, isLive, stream{title, game, gameBoxArtUrl, viewers, startedAt, thumbnail}, lastBroadcast{}, recentVideos[] (with embedUrl, language, animatedPreviewUrl, gameBoxArtUrl), topClips[], and schedule[]. Flat 1 credit. game stays the category name string; gameBoxArtUrl and animatedPreviewUrl are additive media fields (no GraphQL junk).",
  },
  { slug: "twitch-user-videos", name: "Twitch User Videos API", shortName: "User Videos", category: "list", method: "GET", path: "/v1/twitch/user-videos", credits: 2 },
  { slug: "twitch-user-schedule", name: "Twitch User Schedule API", shortName: "User Schedule", category: "list", method: "GET", path: "/v1/twitch/user-schedule", credits: 1 },
  {
    slug: "twitch-clip",
    name: "Twitch Clip API",
    shortName: "Clip",
    category: "details",
    method: "GET",
    path: "/v1/twitch/clip",
    credits: 1,
    tagline:
      "Twitch clip — curator vs channel, followers, multi-quality video, and token expiry as clean JSON.",
    longDescription:
      "Pass a Twitch clip URL (or channel URL/username for a recent clip) and get a clean structured object — not Twitch's raw GraphQL envelope. Includes curator (who cut the clip) separate from channel/broadcaster (id, followers, isPartner, lastBroadcast), language, isFeatured/isPublished, videoOffsetSeconds, gameId/gameSlug/gameBoxArtUrl, videoQualities[{quality,frameRate,url}], and playbackAccessToken with expires/expiresAt. Flat broadcaster string kept for back-compat. Flat 1 credit.",
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
      "Pass a Spotify artist URL, URI, or ID and get a clean profile: name, description, image, followers, monthlyListeners, worldRank, topCities[], externalLinks[], verified, topTracks[] (with playCount), concerts[], relatedArtists[], and albums/singles (with counts). Flat 1 credit. monthlyListeners, topCities, and worldRank are not on Spotify's public Web API — they come from the web-player GraphQL path this endpoint uses. raw keeps the upstream payload for advanced use (shape may change); prefer the normalized fields.",
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
      "Spotify track — playCount, artist/album IDs, explicit rating, and duration as clean JSON.",
    longDescription:
      "Pass a Spotify track URL, URI, or ID and get clean JSON: id, name, playCount (stream count from Spotify's web GraphQL), trackNumber, contentRating/explicit, durationMs, artistItems[{id,uri,name,url}], albumInfo[{id,uri,name,url,releaseDate}], and previewUrl when Spotify exposes one. Flat artists[] name strings and album name kept for back-compat. Flat 1 credit. Note: Spotify's 0–100 popularity score is not on this Pathfinder surface — playCount is the listen metric.",
  },
  { slug: "spotify-album", name: "Spotify Album API", shortName: "Album", category: "details", method: "GET", path: "/v1/spotify/album", credits: 2 , tagline: "Get a Spotify album — title, artists, tracks, release date, and cover art as structured JSON." },
  { slug: "spotify-search", name: "Spotify Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/spotify/search", credits: 2 },
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
      "Pass a Spotify show/podcast URL, URI, or ID and get clean JSON: id, name, description, publisher{name}, rating{average, totalRatings}, topics[{title, uri}], contentRating/explicit, mediaType, totalEpisodes, and cover image. Publisher is the show's publisher (not host names stuffed into artists[]). Flat 1 credit. Does not ship Spotify's UI color palette (visualIdentity) or a bulky raw dump.",
  },
  { slug: "spotify-podcast-episodes", name: "Spotify Podcast Episodes API", shortName: "Podcast Episodes", category: "list", method: "GET", path: "/v1/spotify/podcast-episodes", credits: 2 },
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
      "SoundCloud artist profile — bio, counts, verified, badges, and creator subscription tier.",
    longDescription:
      "Pass a SoundCloud artist URL or username and get the public profile as clean JSON: id, username, name, description, avatar, city/countryCode, verified, followers/followings/trackCount/playlistCount/likesCount, plus badges (pro / creatorMidTier / proUnlimited / verified), creatorSubscription.product.id (e.g. creator-pro-unlimited), and lastModified. Flat 1 credit.",
  },
  { slug: "soundcloud-artist-tracks", name: "SoundCloud Artist Tracks API", shortName: "Artist Tracks", category: "list", method: "GET", path: "/v1/soundcloud/artist-tracks", credits: 2 },
  { slug: "soundcloud-track", name: "SoundCloud Track API", shortName: "Track", category: "details", method: "GET", path: "/v1/soundcloud/track", credits: 1 , tagline: "Get a SoundCloud track — title, artist, plays, likes, duration, and artwork as structured JSON." },
];

const LINKTREE: Spec[] = [
  { slug: "linktree-page", name: "Linktree Page API", shortName: "Page", category: "details", method: "GET", path: "/v1/linktree/page", credits: 1, tagline: "Public Linktree page — links (incl. GROUP children), socials, email, verticals. Flat 1 credit.", longDescription: "Paste a Linktree URL or username and get the public page as clean JSON: profile fields, verticals/linkPlatforms, email when the creator publishes a mailto social, typed links (CLASSIC, SPOTIFY_*, GROUP, …), and nested GROUP.links for folder children (parentId on nested rows). socials is the icon list from Linktree; socialAccounts is a camelCase URL map (instagram/tiktok/soundcloud/…). Thumbnails and linkCount included. Flat 1 credit. Ideal for lead enrichment and competitor link-in-bio research." },
];

const SNAPCHAT: Spec[] = [
  { slug: "snapchat-user-profile", name: "Snapchat User Profile API", shortName: "User Profile", category: "channel", method: "GET", path: "/v1/snapchat/user-profile", credits: 1, tagline: "Public Snapchat profile — subscribers, highlights with full snap lists, Spotlight engagement, and related accounts. Flat 1 credit.", longDescription: "Pass a Snapchat username or profile URL and get the public profile as clean JSON: display name, bio, human-readable category, numeric subscriberCount, badge/verified, avatar + hero image, snapcode, website, businessProfileId, and account createdAt. Curated highlights include every snap's mediaUrl and timestamp (not just the first). Spotlight highlights carry video metadata plus engagement (views/shares/comments). Also returns the active story snap list and related accounts. Flat 1 credit." },
];

const TRUTH_SOCIAL: Spec[] = [
  {
    slug: "truth-social-profile",
    name: "Truth Social Profile API",
    shortName: "Profile",
    category: "channel",
    method: "GET",
    path: "/v1/truth-social/profile",
    credits: 1,
    tagline: "Public Truth Social profile — stats, bot/private flags, static media. Flat 1 credit.",
    longDescription:
      "Pass a Truth Social @username or profile URL and get the public account as clean JSON: display name, HTML-stripped bio, avatar/banner plus avatarStatic/headerStatic, verified/bot/isPrivate/group, discoverable, followers/following/postCount, location/website, createdAt/lastStatusAt, emojis[], and profile fields[]. Important limitation: as of late 2025 Truth Social typically only exposes public profiles/posts for prominent accounts without login — most other accounts require auth and return 404 here. Flat 1 credit.",
  },
  { slug: "truth-social-user-posts", name: "Truth Social User Posts API", shortName: "User Posts", category: "list", method: "GET", path: "/v1/truth-social/user-posts", credits: 17, creditsPerResult: 0.85 },
  { slug: "truth-social-post", name: "Truth Social Post API", shortName: "Post", category: "details", method: "GET", path: "/v1/truth-social/post", credits: 5 , tagline: "Get a Truth Social post — text, author, and engagement fields as structured JSON." },
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
    tagline:
      "Get a Kick clip — creator vs channel, category, maturity, VOD link, views, and duration as structured JSON.",
    longDescription:
      "Pass a Kick clip URL for one enriched clip, or a channel URL/@username for recent clips[]. Clip responses separate creator (who cut the clip) from channel (the broadcaster), and include privacy, isMature, startedAt, vod.id, livestreamId, vodStartsAt, plus categorySlug/parentCategory. Channel mode returns clips[] only — no duplicate top-level clip. Flat 1 credit on the native path.",
  },
];

const AMAZON_SHOP: Spec[] = [
  {
    slug: "amazon-shop-page",
    name: "Amazon Shop Page API",
    shortName: "Shop Page",
    category: "list",
    method: "GET",
    path: "/v1/amazon-shop/page",
    credits: 1,
    tagline: "Amazon seller storefront products — ASIN, price, badges, canonical /dp URLs. 1 credit/page.",
    longDescription:
      "Pass an Amazon seller storefront URL (/sp?seller=… or /s?me=…) or raw seller ID and get that seller's product listings as clean JSON: ASIN, title, canonical /dp URL, image, price/currency/priceFormatted, rating/reviews, and isPrime/isBestSeller/isSponsored flags. Includes seller id/name/profile URL, scrapedAt, and cursor pagination (nextCursor/hasMore). Scope: third-party seller storefronts — not influencer Amazon Shops (/shop/<handle>), which are a different Amazon surface. Billing is 1 credit per ~16-product storefront page.",
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
      "Call with your Captapi key and get plan, monthlyQuota, subscriptionCredits (reset each billing period), topupCredits (never expire), totalCredits, and subscriptionRenewsAt as camelCase JSON. Free — does not consume credits. Use this to tell whether remaining balance is time-boxed subscription quota or permanent top-ups.",
  },
  { slug: "account-request-history", name: "Request History API", shortName: "Request History", category: "list", method: "GET", path: "/v1/account/request-history", credits: 0 , tagline: "See recent API requests made with your Captapi key — path, status, and credits used.", longDescription: "List recent requests for your Captapi account as structured JSON: endpoint path, status, credits charged, and timestamps. Free — does not consume credits." },
  { slug: "account-daily-usage", name: "Daily Usage API", shortName: "Daily Usage", category: "list", method: "GET", path: "/v1/account/daily-usage", credits: 0 , tagline: "See day-by-day credit usage for your Captapi account.", longDescription: "Get daily credit usage for your Captapi key as structured JSON — useful for spend monitoring and budgeting. Free — does not consume credits." },
  { slug: "account-most-used-routes", name: "Most Used Routes API", shortName: "Most Used Routes", category: "list", method: "GET", path: "/v1/account/most-used-routes", credits: 0 , tagline: "See which Captapi endpoints your key calls most often.", longDescription: "Get a ranked list of the routes your Captapi key uses most, with call counts over a chosen window. Free — does not consume credits." },
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
    longDescription: "Pass any supported post, video, or reel URL (YouTube, TikTok, Instagram, Facebook, X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, or Rumble) and get one normalized metrics object — views, likes, comments, shares, saves, interactions, and engagementRate (interactions / views) — with the platform auto-detected. Schema is stable across networks; unavailable values are null (YouTube has no public share/save counts and verified stays null without a channel badge lookup). Flat 1 credit per call. Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.",
  },
  {
    slug: "analytics-compare",
    name: "Compare Analytics API",
    shortName: "Compare Analytics",
    category: "list",
    method: "GET",
    path: "/v1/analytics/compare",
    credits: 1,
    tagline: "Compare unified metrics across up to 10 URLs in one call — 1 credit per resolved URL (cache hits free).",
    longDescription: "Pass up to 10 comma-separated post/video/reel URLs (any mix of supported platforms) and get count/resolved plus results[] — each item is the same shape as /v1/analytics/post (platform, title, publishedAt, author including verified, metrics{views,likes,comments,shares,saves,interactions,engagementRate}). Unavailable values are null; keys are never omitted. Bills 1 credit per successfully resolved URL that is not served from the 24h cache (shared with post analytics); there is no bulk discount vs N separate /post calls — the win is one HTTP round-trip. Pass cache=true for free cache hits.",
  },
  {
    slug: "video-transcript",
    name: "Video File Transcript API",
    shortName: "File Transcript",
    category: "transcript",
    method: "POST",
    path: "/v1/video/transcript",
    credits: 1,
    tagline: "Whisper transcription of an uploaded video or audio file — 1 credit per minute of audio.",
    longDescription: "Upload a video or audio file (multipart form field `file`) and get a Whisper transcript as structured JSON — full text, segments, word count, language, and duration. Billed at 1 credit per minute of audio (rounded up, minimum 1).",
  },
  {
    slug: "video-summarize",
    name: "Video File Summarizer API",
    shortName: "File Summarizer",
    category: "summarize",
    method: "POST",
    path: "/v1/video/summarize",
    credits: 2,
    tagline: "Transcribe an uploaded file with Whisper, then return an AI summary — 1 credit per minute + 1 for the summary.",
    longDescription: "Upload a video or audio file (multipart form field `file`) to transcribe with Whisper and get an AI summary (key points, topics, sentiment) plus the transcript. Billed at 1 credit per minute of audio (rounded up) plus 1 credit for the summary.",
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
      "Pass a Kwai profile URL or @handle and get the public account as clean JSON: id/eid, username, displayName, bio, avatar, verified + verifiedDescription/verifiedNumber when Kwai exposes them, gender, followers/following/likedCount, publicPostCount/privatePostCount, and isPrivate. Parsed from Kwai's public web page (JSON-LD + Nuxt SSR state) — not HTML scraping of visible counters. Note: Kwai's web surface sometimes stubs follower/following to 1; when that happens we prefer schema.org counts for followers and omit following rather than ship a fake 1. Flat 1 credit.",
  },
  { slug: "kwai-user-posts", name: "Kwai User Posts API", shortName: "User Posts", category: "list", method: "GET", path: "/v1/kwai/user-posts", credits: 45, creditsPerResult: 2.25 },
  { slug: "kwai-post", name: "Kwai Post API", shortName: "Post", category: "details", method: "GET", path: "/v1/kwai/post", credits: 17 , tagline: "Get a Kwai post — caption, author, and engagement fields as structured JSON." },
];

const KOMI: Spec[] = [
  { slug: "komi-page", name: "Komi Page API", shortName: "Page", category: "channel", method: "GET", path: "/v1/komi/page", credits: 4 , tagline: "Extract the public links and profile fields from a Komi page.", longDescription: "Paste a Komi page URL and get the creator's public page as structured JSON — profile fields plus the links listed on the page." },
];

const PILLAR: Spec[] = [
  { slug: "pillar-page", name: "Pillar Page API", shortName: "Page", category: "channel", method: "GET", path: "/v1/pillar/page", credits: 4 , tagline: "Extract the public links and profile fields from a Pillar page.", longDescription: "Paste a Pillar page URL and get the creator's public page as structured JSON — profile fields plus the links listed on the page." },
];

const LINKBIO: Spec[] = [
  { slug: "linkbio-page", name: "Linkbio Page API", shortName: "Page", category: "channel", method: "GET", path: "/v1/linkbio/page", credits: 4 , tagline: "Extract the public links and profile fields from a Linkbio page.", longDescription: "Paste a Linkbio page URL and get the creator's public page as structured JSON — profile fields plus the links listed on the page." },
];

const LINKME: Spec[] = [
  { slug: "linkme-profile", name: "Linkme Profile API", shortName: "Profile", category: "channel", method: "GET", path: "/v1/linkme/profile", credits: 4 , tagline: "Extract the public links and profile fields from a Linkme profile.", longDescription: "Paste a Linkme profile URL and get the public profile as structured JSON — profile fields plus the links listed on the page." },
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
      "Search Meta Ad Library by keyword — active/inactive filter, media type, date range, platforms, carousel cards, and structured spend/impressions when Meta publishes them.",
    longDescription:
      "Search Meta's Ad Library and get competitor creatives as clean JSON. Filter by status (default ACTIVE), media type, ad type, exact phrase, sort mode, and delivery start date range. Each ad keeps the original fields (text, headline, cta, media[], spend/impressions strings) and adds isActive, publisherPlatforms, cards[], typed images/videos, pageLikeCount, disclaimer/byline, and spendRange/impressionsRange for sorting. Important: spend and impressions are only populated for political and issue ads in most markets — commercial ads usually return null. Max 200 ads per call; searchResultsCount is best-effort when Meta embeds a total. Flat 2 credits on the native path.",
  },
  { slug: "facebook-ad-library-company-ads", name: "Facebook Company Ads API", shortName: "Company Ads", category: "list", method: "GET", path: "/v1/ad-library/facebook/company-ads", credits: 2 },
  { slug: "facebook-ad-library-search-companies", name: "Facebook Ad Library Search Companies API", shortName: "Search Companies", category: "search", method: "GET", path: "/v1/ad-library/facebook/search-companies", credits: 2 },
  { slug: "facebook-ad-library-ad-details", name: "Facebook Ad Details API", shortName: "Ad Details", category: "details", method: "GET", path: "/v1/ad-library/facebook/ad-details", credits: 2 , tagline: "Get a Meta Ad Library ad — creative text, media, advertiser, and delivery fields as structured JSON.", longDescription: "Paste a Meta Ad Library ad URL or ad ID and get the creative as clean JSON: body text, headline, CTA, landing URL, media, advertiser, and delivery signals when available. Flat 2 credits per call." },
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
      "Search TikTok Commercial Content Library ads — ISO dates, advertiser location, reach bands (2 credits native).",
    longDescription:
      "Search TikTok's Commercial Content Library (library.tiktok.com / EU DSA) by keyword. Returns ads with id, url, text, adFormat, ISO firstShown/lastShown, impressions + impressionsRange, advertiser{name, location}, and media[]. Flat 2 credits on the native path (Apify fallback capped at 5). Default country is GB — this library is EU-led; region=US is often empty. For Creative Center Top Ads (CTR, likes, industry/objective, orderBy), use /v1/ad-library/tiktok/top-ads instead.",
  },
  {
    slug: "tiktok-ad-library-top-ads",
    name: "TikTok Creative Center Top Ads API",
    shortName: "Top Ads",
    category: "search",
    method: "GET",
    path: "/v1/ad-library/tiktok/top-ads",
    credits: 2,
    tagline:
      "TikTok Creative Center Top Ads — CTR, likes, industry/objective, and video URLs (2 credits native).",
    longDescription:
      "Pull high-performing auction ads from TikTok Creative Center Top Ads as clean JSON: id, title, brandName, likes, ctr/ctrTier, costTier, favorite, isSparkAd, industry/industryKey, objective, countries, and video{url,urlHd,cover,durationSeconds,width,height}. Filter with country (default US), period (7/30/180), orderBy (for_you|likes|ctr|impressions|cost), and optional q/industry/objective/adFormat. Flat 2 credits on the Decodo-native path; Apify fallback is ~1 credit per returned ad (minimum 2). This is Creative Center — not the EU Commercial Content Library (use /tiktok/search for DSA transparency).",
  },
  { slug: "tiktok-ad-library-ad-details", name: "TikTok Ad Details API", shortName: "Ad Details", category: "details", method: "GET", path: "/v1/ad-library/tiktok/ad-details", credits: 17 , tagline: "Get a TikTok Ad Library ad — creative, advertiser, and delivery fields as structured JSON." },
];

const GOOGLE_AD_LIBRARY: Spec[] = [
  { slug: "google-ad-library-company-ads", name: "Google Company Ads API", shortName: "Company Ads", category: "list", method: "GET", path: "/v1/ad-library/google/company-ads", credits: 2, tagline: "List an advertiser's Google Ads Transparency creatives with media — 2 credits, cursor paging, and date filters.", longDescription: "Pass an advertiser name, domain (nike.com), or AR… id and get public commercial creatives as clean JSON: nested advertiser{id,name,url}, firstShown/lastShown, adFormat, and media[] (creatives included — no 25-credit upcharge). Supports country/region, start_date/end_date (YYYY-MM-DD overlap filter), cursor pagination (nextCursor + hasMore), and adsCountEstimate from Google's advertiser suggestions. Returns only public Ads Transparency creatives — some ads require login and cannot be fetched; creative shapes can vary. Political ads are not available on this endpoint (topic=all only). Flat 2 credits on the native path (max 200 per page)." },
  { slug: "google-ad-library-ad-details", name: "Google Ad Details API", shortName: "Ad Details", category: "details", method: "GET", path: "/v1/ad-library/google/ad-details", credits: 17 , tagline: "Get a Google Ads Transparency ad — creative, advertiser, and delivery fields as structured JSON." },
  { slug: "google-ad-library-advertiser-search", name: "Google Advertiser Search API", shortName: "Advertiser Search", category: "search", method: "GET", path: "/v1/ad-library/google/advertiser-search", credits: 1 },
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
  { slug: "linkedin-ad-library-ad-details", name: "LinkedIn Ad Details API", shortName: "Ad Details", category: "details", method: "GET", path: "/v1/ad-library/linkedin/ad-details", credits: 17 , tagline: "Get a LinkedIn Ad Library ad — creative, advertiser, and delivery fields as structured JSON." },
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
    name: "Amazon Shop",
    blurb: "Seller storefront product listings (not influencer /shop/ vitrines) — price, badges, pagination.",
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
    blurb: "Public Linktree links (incl. GROUP children), socials, email, and verticals.",
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
    blurb: "Public Truth Social profiles/posts for prominent accounts (most others require auth).",
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
    blurb: "Extract public Komi page links and creator profile metadata.",
    icon: "link",
    color: "text-violet-500",
    exampleUrl: "https://komi.io/example",
    endpoints: KOMI.map((s) => ({ ...s, platform: "komi" as const })),
  },
  {
    id: "pillar",
    name: "Pillar",
    blurb: "Extract public Pillar page links and creator profile metadata.",
    icon: "link",
    color: "text-cyan-600",
    exampleUrl: "https://pillar.io/example",
    endpoints: PILLAR.map((s) => ({ ...s, platform: "pillar" as const })),
  },
  {
    id: "linkbio",
    name: "Linkbio",
    blurb: "Extract public Linkbio page links and profile metadata.",
    icon: "link",
    color: "text-pink-500",
    exampleUrl: "https://lnk.bio/charlidamelio",
    endpoints: LINKBIO.map((s) => ({ ...s, platform: "linkbio" as const })),
  },
  {
    id: "linkme",
    name: "Linkme",
    blurb: "Extract public Linkme profile links and metadata.",
    icon: "link",
    color: "text-blue-500",
    exampleUrl: "https://link.me/example",
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
    prefer: "Use location search first (details=true when you need lat/lng), then marketplace search with the selected place.",
    endpointSlug: "facebook-marketplace-location-search",
    why: "Resolves a city/place to a Facebook Marketplace location with coordinates when available.",
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
    prefer: "Use platform-specific Truth Social, Kick, or Rumble endpoints instead of generic web search.",
    endpointSlug: "truth-social-user-posts",
    why: "Fetches public Truth Social posts for monitoring and research workflows.",
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
      "Live data for your Captapi API key",
      "No credit charge for account endpoints",
      "Clean JSON ready for dashboards and alerts",
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
const lang = (): ApiParam => ({ name: "language", type: "string", required: false, description: 'Preferred caption language as an ISO code, e.g. "en". Defaults to auto-detect.' });
const langOut = (): ApiParam => ({ name: "language", type: "string", required: false, description: 'ISO code, e.g. "tr": pins the speech language and sets the summary output language. Defaults to auto-detect + English summary.' });
const langUi = (): ApiParam => ({ name: "language", type: "string", required: false, description: "Interface language for localized results, e.g. en-US or de-DE. Default en-US." });
const cid = (): ApiParam => ({ name: "comment_id", type: "string", required: true, description: "ID of the parent comment to fetch replies for (from the comments endpoint)." });
const fastRss = (): ApiParam => ({ name: "fast", type: "boolean", required: false, description: "Set true to use YouTube RSS for faster results with less detailed metadata. Leave false when viewCount/duration quality matters." });
const cacheP = (): ApiParam => ({ name: "cache", type: "boolean", required: false, description: "Set true to serve from the 24h response cache. Default false — always fetch fresh data." });
/** TikTok transcript defaults to cache=true (0 credits on hit). */
const cachePDefaultTrue = (): ApiParam => ({
  name: "cache",
  type: "boolean",
  required: false,
  description:
    "Serve from the 24h shared cache when available (0 credits on hit). Default true — set false to always fetch fresh.",
});
const CACHE_NOTE =
  "Pass cache=true to serve from the 24h shared cache (0 credits on hit); default is always fresh.";
const CACHE_NOTE_DEFAULT_TRUE =
  "Cache is on by default (0 credits on hit); pass cache=false to always fetch fresh.";

const YT_VIDEO = "Public YouTube video URL, e.g. https://youtube.com/watch?v=ID. Not a TikTok/Instagram/Facebook URL.";
const YT_SHORTS = "Public YouTube Shorts URL, e.g. https://youtube.com/shorts/ID. Not a TikTok/Instagram/Facebook URL.";
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
const KICK_CLIP = "Kick clip URL, channel URL, or channel username.";
const AMAZON_SHOP_URL =
  "Amazon seller storefront URL (/sp?seller=… or /s?me=…) or raw seller ID. Not influencer /shop/<handle> pages.";
const KWAI_PROFILE = "Kwai profile URL or @handle, e.g. https://www.kwai.com/@topfilmeseseriesnatv.";
const KWAI_POST = "Kwai video URL, e.g. https://www.kwai.com/@topfilmeseseriesnatv/video/5240932700689736196.";
const CURSOR = { name: "cursor", type: "string" as const, required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." };
const KOMI_PAGE = "Komi page URL or username.";
const PILLAR_PAGE = "Pillar page URL or username.";
const LINKBIO_PAGE = "Linkbio (lnk.bio) page URL or username, e.g. https://lnk.bio/charlidamelio.";
const LINKME_PROFILE = "Linkme profile URL or username.";

const ENDPOINT_PARAMS: Record<string, ApiParam[]> = {
  // YouTube
  "youtube-transcript": [up(YT_VIDEO), lang(), cacheP()],
  "youtube-summarizer": [up(YT_VIDEO), lang(), cacheP()],
  "youtube-video-details": [up(YT_VIDEO)],
  "youtube-comments": [up(YT_VIDEO), lpFlat(50, 500, 2), CURSOR],
  "youtube-channel-details": [up(YT_CHANNEL)],
  "youtube-search": [
    qp(),
    lp(20, 200),
    { name: "cursor", type: "string", required: false, description: "Pagination cursor from nextCursor." },
    { name: "type", type: "string", required: false, description: "all | videos | shorts | channels | playlists." },
    { name: "sortBy", type: "string", required: false, description: "relevance | date | views | rating." },
    { name: "uploadDate", type: "string", required: false, description: "any | today | this_week | this_month | this_year." },
    { name: "duration", type: "string", required: false, description: "any | under_4 | 4_20 | over_20." },
    { name: "region", type: "string", required: false, description: "ISO country code for localized results (default US)." },
  ],
  "youtube-channel-videos": [up(YT_CHANNEL), lp(20, 200), fastRss()],
  "youtube-playlist-videos": [up("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."), lp(50, 500), fastRss()],
  "youtube-playlist": [up("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."), lp(50, 500), fastRss()],
  "youtube-shorts-transcript": [up(YT_SHORTS), lang(), cacheP()],
  "youtube-shorts-summarizer": [up(YT_SHORTS), lang(), cacheP()],
  "youtube-shorts-stats": [up(YT_SHORTS)],
  "youtube-shorts-comments": [up(YT_SHORTS), lp(50, 500), CURSOR],
  "youtube-channel-shorts": [up(YT_CHANNEL), lp(20, 200)],
  "youtube-trending-shorts": [{ name: "q", type: "string", required: false, description: "Seed keyword for trending Shorts. Defaults to trending." }, lpFlat(20, 100, 2)],
  "youtube-channel-streams": [up(YT_CHANNEL), lp(20, 200)],
  "youtube-hashtag-search": [qp("Hashtag with or without the # (min 2 characters)."), lp(20, 200)],
  "youtube-comment-replies": [up(YT_VIDEO), cid(), lp(50, 500)],
  "youtube-channel-playlists": [up(YT_CHANNEL), lp(20, 200)],
  "youtube-community-posts": [
    up(YT_CHANNEL),
    lpFlat(20, 200, 1),
    {
      name: "cursor",
      type: "string",
      required: false,
      description:
        "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response.",
    },
  ],
  "youtube-community-post-details": [up("YouTube community post URL.")],
  "youtube-video-sponsors": [up(YT_VIDEO)],
  // TikTok
  "tiktok-transcript": [up(TT_VIDEO), lang(), cachePDefaultTrue()],
  "tiktok-summarizer": [up(TT_VIDEO), langOut(), cacheP()],
  "tiktok-video-details": [up(TT_VIDEO)],
  "tiktok-comments": [up(TT_VIDEO), lpFlat(50, 500, 2), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response (a numeric offset, e.g. 50). A null nextCursor means the end of the comments." }],
  "tiktok-channel-details": [up(TT_PROFILE)],
  "tiktok-profile-region": [up(TT_PROFILE)],
  "tiktok-audience-demographics": [up(TT_PROFILE)],
  "tiktok-search-suggestions": [qp("Seed keyword to expand into autocomplete suggestions, e.g. skincare."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code that localizes the suggestions to a market, e.g. US, GB, DE. Default US." }, { name: "language", type: "string", required: false, description: "Interface language for the suggestions, e.g. en-US or de-DE. Default en-US." }, lpFlat(20, 100, 2)],
  "tiktok-channel-posts": [up(TT_PROFILE), { name: "limit", type: "integer", required: false, description: "How many of the creator's latest videos to return on this page (default 20, max 200). Newest first. Flat 2 credits per call." }, { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response (TikTok's max_cursor timestamp, e.g. 1783614676000). A null nextCursor means the end of the list." }],
  "tiktok-comment-replies": [
    up(TT_VIDEO),
    cid(),
    lpFlat(50, 500, 2),
    { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value from the previous response." },
  ],
  "tiktok-user-followers": [up(TT_PROFILE), lp(50, 500)],
  "tiktok-user-followings": [up(TT_PROFILE), lp(50, 500)],
  "tiktok-music-posts": [up(TT_MUSIC), lpFlat(20, 200, 2)],
  "tiktok-top-search": [qp(), lp(20, 200)],
  "tiktok-search-by-hashtag": [qp("Hashtag to search for, with or without the # (min 2 characters)."), lp(20, 100), { name: "cursor", type: "integer", required: false, description: "Pagination offset. Leave at 0 (or omit) for the first page; then pass the nextCursor value returned in the previous response. A null nextCursor means the end of the results." }, { name: "region", type: "string", required: false, description: "Two-letter ISO 3166-1 country our request is sent from. Default US. Does not filter results by country." }],
  "tiktok-search-users": [qp("Search query matched against usernames, display names and bios (min 2 characters)."), lp(20, 100), { name: "cursor", type: "integer", required: false, description: "Pagination offset. Leave at 0 (or omit) for the first page; then pass the nextCursor value returned in the previous response. A null nextCursor means the end of the results." }],
  "tiktok-song-details": [up(TT_MUSIC)],
  "tiktok-trending-feed": [{ name: "country", type: "string", required: false, description: "Two-letter ISO country code, e.g. US, GB, TR. Default US." }, lp(20, 200)],
  "tiktok-popular-hashtags": [{ name: "query", type: "string", required: false, description: 'Topic or keyword to discover trending hashtags for. Default "trending".' }, lp(20, 100)],
  "tiktok-live": [up(TT_PROFILE)],
  "tiktok-live-info": [up(TT_PROFILE)],
  "tiktok-popular-creators": [{ name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }, { name: "sort", type: "string", required: false, description: "follower, engagement, or popularity. Default follower." }, { name: "follower_count", type: "string", required: false, description: "Optional range: 10k-100k, 100k-1m, 1m-10m, >10m." }, lp(20, 100)],
  // Instagram
  "instagram-transcript": [up(IG_REEL), lang(), cacheP()],
  "instagram-summarizer": [up(IG_REEL), langOut(), cacheP()],
  "instagram-details": [up(IG_POST)],
  "instagram-comments": [up(IG_POST), lp(50, 500)],
  "instagram-channel-details": [up(IG_PROFILE)],
  "instagram-channel-posts": [up(IG_PROFILE), lp(20, 200), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response (e.g. 3937014945555313553_1697296). A null nextCursor means the end of the list." }],
  "instagram-channel-reels": [up(IG_PROFILE), lp(20, 200), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response (e.g. 3937158245004702478_12281817). A null nextCursor means the end of the list." }],
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
  "instagram-trending-reels": [{ name: "country", type: "string", required: false, description: "Country for Explore localization — full name or ISO code (e.g. 'United States', 'US', 'Turkey', 'TR'). Default United States. 35 countries supported." }, lp(20, 200)],
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
  "instagram-profile-search": [qp("Account name, @handle, or profile URL to look up (min 2 characters).")],
  "instagram-embed": [up("Instagram post, reel, or profile URL (or @handle), e.g. https://instagram.com/reel/ID/ or https://instagram.com/username/.")],
  "instagram-basic-profile": [{ name: "userId", type: "string", required: true, description: "Instagram numeric user ID (e.g. 13460080). A profile URL, @handle, or username is also accepted and resolved automatically." }],
  // Facebook
  "facebook-details": [up(FB_VIDEO)],
  "facebook-summarizer": [up(FB_VIDEO), cacheP()],
  "facebook-comments": [up(FB_VIDEO), lpFlat(50, 500, 2)],
  "facebook-page-details": [up("Facebook page URL, @handle, or page name, e.g. https://facebook.com/PageName.")],
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
    { name: "location", type: "string", required: true, description: "City or place name, e.g. 'Austin, TX'." },
    lpFlat(20, 200, 2),
    { name: "minPrice", type: "number", required: false, description: "Minimum price in local currency units." },
    { name: "maxPrice", type: "number", required: false, description: "Maximum price in local currency units." },
    { name: "sortBy", type: "string", required: false, description: "suggested | distance | creation_time | price_ascend | price_descend." },
    { name: "daysSinceListed", type: "string", required: false, description: "1 (24h), 7, or 30." },
    { name: "condition", type: "string", required: false, description: "new, like_new, good, fair (comma-separated ok)." },
    { name: "deliveryMethod", type: "string", required: false, description: "local_pickup | shipping | all." },
    { name: "availability", type: "string", required: false, description: "available | sold | all." },
    { name: "radiusMiles", type: "number", required: false, description: "Radius in miles: 1,2,5,10,20,40,60,80,100,250,500." },
    { name: "category", type: "string", required: false, description: "Top-level category slug, e.g. electronics." },
    { name: "cursor", type: "string", required: false, description: "Pagination cursor from a previous nextCursor." },
    { name: "details", type: "boolean", required: false, description: "When true, adds description/condition/coordinates/full photo gallery (2 + 2 credits per listing). Default false → flat 2 credits; cover photo is still included." },
  ],
  "facebook-marketplace-location-search": [qp("City/place search query, e.g. Austin."), lpFlat(10, 50, 2), { name: "details", type: "boolean", required: false, description: "Legacy flag. Coordinates are included when available. Flat 2 credits either way." }],
  "facebook-event-search": [qp("Topic and/or place, e.g. 'comedy Chicago'."), lp(20, 200)],
  "facebook-event-details": [up("Facebook event URL, e.g. https://facebook.com/events/ID.")],
  "facebook-profile-photos": [up("Facebook profile/page URL, @handle, or page name."), lp(20, 200)],
  "facebook-profile-events": [up("Facebook profile/page URL, @handle, or page name."), lp(20, 200)],
  "facebook-marketplace-item": [up("Facebook Marketplace item URL.")],
  // Twitter / X
  "twitter-tweet-details": [up("Public tweet URL, e.g. https://x.com/user/status/ID.")],
  "twitter-transcript": [up("Public tweet URL, e.g. https://x.com/user/status/ID."), cacheP()],
  "twitter-profile": [up("Twitter/X profile URL or @handle, e.g. https://x.com/username.")],
  "twitter-user-tweets": [up("Twitter/X profile URL or @handle."), lp(20, 200)],
  "twitter-search": [qp("Keyword or phrase to search public tweets on X (min 2 characters)."), lp(20, 200)],
  "twitter-community": [up("X community URL (x.com/i/communities/ID) or community ID.")],
  "twitter-community-tweets": [up("X community URL (x.com/i/communities/ID) or community ID."), lp(25, 200)],
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
  "reddit-search": [qp("Keyword or phrase to search Reddit posts site-wide (min 2 characters)."), lp(25, 200), CURSOR],
  "reddit-subreddit-details": [up("Subreddit URL, r/name, or bare name, e.g. r/technology.")],
  "reddit-subreddit-search": [up("Subreddit URL, r/name, or bare name, e.g. r/technology."), qp("Keywords or search query (min 2 characters)."), lp(25, 200), CURSOR],
  // Threads
  "threads-profile": [up("Threads profile URL or @handle, e.g. https://threads.net/@username.")],
  "threads-user-posts": [up("Threads profile URL or @handle."), lp(20, 100)],
  "threads-post-details": [up("Threads post URL, e.g. https://threads.net/@user/post/CODE.")],
  "threads-search": [qp("Keyword or phrase to search public Threads posts (min 2 characters)."), lp(25, 200)],
  "threads-search-users": [qp("Keyword to find Threads users / creators (min 2 characters)."), lp(20, 100)],
  // Bluesky
  "bluesky-profile": [up("Bluesky profile URL, @handle, or handle, e.g. bsky.app/profile/handle.")],
  "bluesky-user-posts": [up("Bluesky profile URL, @handle, or handle, e.g. https://bsky.app/profile/handle.bsky.social."), lp(25, 100), CURSOR],
  "bluesky-post-details": [up("Bluesky post URL, e.g. https://bsky.app/profile/handle/post/RKEY.")],
  // Pinterest
  "pinterest-pin-details": [up("Pinterest pin URL, e.g. https://pinterest.com/pin/ID/.")],
  "pinterest-user-pins": [up("Pinterest profile URL or username."), lp(25, 200)],
  "pinterest-search": [qp("Keywords or search query (min 2 characters)."), lp(25, 200)],
  "pinterest-board": [up("Pinterest board URL, e.g. https://pinterest.com/username/board-name/."), lp(25, 200)],
  "pinterest-user-boards": [up("Pinterest profile URL or username."), lp(25, 200)],
  // LinkedIn
  "linkedin-profile": [up("LinkedIn profile URL, e.g. https://www.linkedin.com/in/paul-martin-a5aa98.")],
  "linkedin-company": [up("LinkedIn company URL, e.g. https://linkedin.com/company/slug.")],
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
  "rumble-channel-videos": [up("Rumble channel URL, e.g. https://rumble.com/c/name."), lp(20, 200)],
  "rumble-search": [qp("Keywords or search query (min 2 characters)."), lp(20, 200)],
  "rumble-comments": [up("Rumble video URL, e.g. https://rumble.com/vXXXX-title.html."), lpFlat(50, 500, 2)],
  // Twitch
  "twitch-profile": [up(TWITCH_PROFILE)],
  "twitch-user-videos": [up(TWITCH_PROFILE), lpFlat(20, 30, 2)],
  "twitch-user-schedule": [up(TWITCH_PROFILE)],
  "twitch-clip": [up("Twitch clip URL, channel URL, or username.")],
  // Spotify
  "spotify-artist": [up(SPOTIFY_URL), cacheP()],
  "spotify-track": [up(SPOTIFY_URL), cacheP()],
  "spotify-album": [up(SPOTIFY_URL), cacheP()],
  "spotify-search": [qp(), { name: "type", type: "string", required: false, description: "tracks, albums, artists, podcasts, or episodes. Default tracks." }, lp(20, 50)],
  "spotify-podcast": [up(SPOTIFY_URL), lpFlat(20, 50, 1), cacheP()],
  "spotify-podcast-episodes": [up(SPOTIFY_URL), lp(20, 50)],
  // SoundCloud
  "soundcloud-artist": [up(SC_PROFILE)],
  "soundcloud-artist-tracks": [up(SC_PROFILE), lpFlat(20, 100, 2), CURSOR],
  "soundcloud-track": [up(SC_TRACK)],
  // Linktree / Snapchat
  "linktree-page": [up(LINKTREE_PROFILE)],
  "snapchat-user-profile": [up(SNAPCHAT_PROFILE)],
  // Truth Social / Kick / Amazon / Age-Gender
  "truth-social-profile": [up(TRUTH_PROFILE)],
  "truth-social-user-posts": [up(TRUTH_PROFILE), lp(20, 80), CURSOR],
  "truth-social-post": [up(TRUTH_POST)],
  "kick-clip": [up(KICK_CLIP), lpFlat(30, 100, 1)],
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
  "account-request-history": [lp(50, 500)],
  "account-daily-usage": [{ name: "days", type: "integer", required: false, description: "Number of days to include (default 30, max 365)." }],
  "account-most-used-routes": [{ name: "days", type: "integer", required: false, description: "Number of days to include (default 30, max 365)." }, lp(20, 100)],
  // Utilities (analytics + uploaded video files)
  "analytics-post": [
    up("A public post, video, or reel URL (YouTube, TikTok, Instagram, Facebook, X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, or Rumble)."),
    cacheP(),
  ],
  "analytics-compare": [
    {
      name: "urls",
      type: "string",
      required: true,
      description: "Comma-separated post/video/reel URLs (up to 10), any mix of supported platforms.",
    },
    cacheP(),
  ],
  "video-transcript": [
    {
      name: "file",
      type: "file",
      required: true,
      description: "Video or audio file to transcribe (multipart form upload).",
    },
  ],
  "video-summarize": [
    {
      name: "file",
      type: "file",
      required: true,
      description: "Video or audio file to transcribe and summarize (multipart form upload).",
    },
  ],
  // Kwai / small creator pages
  "kwai-profile": [up(KWAI_PROFILE)],
  "kwai-user-posts": [up(KWAI_PROFILE), lp(20, 200)],
  "kwai-post": [up(KWAI_POST)],
  "komi-page": [up(KOMI_PAGE)],
  "pillar-page": [up(PILLAR_PAGE)],
  "linkbio-page": [up(LINKBIO_PAGE)],
  "linkme-profile": [up(LINKME_PROFILE)],
  // GitHub
  "github-user": [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL, e.g. getify or https://github.com/getify." }],
  "github-repositories": [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, lp(30, 100), CURSOR],
  "github-repository": [{ name: "repo", type: "string", required: true, description: "Repository URL or owner/name, e.g. vercel/next.js." }],
  "github-pull-requests": [{ name: "repo", type: "string", required: true, description: "Repository URL or owner/name, e.g. vercel/next.js." }, { name: "state", type: "string", required: false, description: "open, closed, or all. Default open." }, lp(30, 100), CURSOR],
  "github-activity": [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, lp(30, 100), CURSOR],
  "github-followers": [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, lp(30, 100), CURSOR],
  "github-following": [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, lp(30, 100), CURSOR],
  "github-contributions": [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }],
  "github-trending-repositories": [{ name: "q", type: "string", required: false, description: "GitHub search query. Default stars:>1000." }, lp(20, 100)],
  "github-trending-developers": [{ name: "q", type: "string", required: false, description: "GitHub user search query. Default followers:>1000." }, lp(20, 100)],
  // TikTok Shop
  "tiktok-shop-search": [qp("Product search query (min 2 characters)."), { name: "region", type: "string", required: false, description: "Two-letter ISO region code. Default US." }, lp(20, 200)],
  "tiktok-shop-products": [up("TikTok Shop store URL."), lp(20, 200)],
  "tiktok-shop-product-details": [
    up("TikTok Shop product URL."),
    {
      name: "region",
      type: "string",
      required: false,
      description: "Market region ISO code for the Apify fallback path (default US).",
    },
  ],
  "tiktok-shop-product-reviews": [up("TikTok Shop product URL."), lp(20, 200)],
  "tiktok-shop-user-showcase": [{ name: "username", type: "string", required: true, description: "TikTok username, @handle, or profile URL, e.g. hydrojug or https://www.tiktok.com/@hydrojug." }, lp(20, 200)],
  // Ad Library
  "facebook-ad-library-search": [
    qp("Keyword, brand, or advertiser to search Meta Ad Library (min 2 characters)."),
    { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." },
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
  ],
  "facebook-ad-library-company-ads": [up("Facebook page URL or Meta Ad Library URL, e.g. https://www.facebook.com/Meta."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }, lp(20, 200)],
  "facebook-ad-library-search-companies": [qp("Company or brand name to search for (min 2 characters)."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }, lp(20, 200)],
  "facebook-ad-library-ad-details": [up("Meta Ad Library ad URL or ad ID.")],
  "facebook-ad-library-ad-transcript": [up("Meta Ad Library ad URL or ad ID.")],
  "tiktok-ad-library-search": [
    qp("Keyword or advertiser to search TikTok Commercial Content Library (min 2 characters)."),
    {
      name: "country",
      type: "string",
      required: false,
      description: "Two-letter ISO country code. Default GB (EU DSA library; US often empty).",
    },
    lp(20, 200),
    cacheP(),
  ],
  "tiktok-ad-library-top-ads": [
    {
      name: "q",
      type: "string",
      required: false,
      description: "Optional keyword filter (brand, product, or creative theme).",
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
    lp(20, 100),
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
    { name: "q", type: "string", required: false, description: "Advertiser / account owner name (min 2 when used). Provide q, keyword, or companyId." },
    { name: "keyword", type: "string", required: false, description: "Optional keyword filter on ad creative copy." },
    { name: "companyId", type: "string", required: false, description: "LinkedIn numeric company id for exact advertiser match." },
    { name: "country", type: "string", required: false, description: "Single ISO country code. Default US. Ignored when countries is set." },
    { name: "countries", type: "string", required: false, description: "Comma-separated ISO country codes (e.g. US,CA,MX)." },
    { name: "startDate", type: "string", required: false, description: "Custom range start YYYY-MM-DD (use with endDate)." },
    { name: "endDate", type: "string", required: false, description: "Custom range end YYYY-MM-DD (use with startDate)." },
    { name: "cursor", type: "string", required: false, description: "Pagination token from paginationToken / nextCursor." },
    lp(20, 200),
  ],
  "linkedin-ad-library-ad-details": [up("LinkedIn Ad Library URL or ad ID.")],
  "google-ad-library-company-ads": [
    { name: "advertiser", type: "string", required: true, description: "Advertiser name, domain (e.g. nike.com), or Google advertiser ID (AR…)." },
    { name: "country", type: "string", required: false, description: "Two-letter ISO country / region code (soft filter). Default US. Alias: region." },
    { name: "region", type: "string", required: false, description: "Alias for country." },
    { name: "start_date", type: "string", required: false, description: "YYYY-MM-DD — keep creatives whose shown window overlaps this start." },
    { name: "end_date", type: "string", required: false, description: "YYYY-MM-DD — keep creatives whose shown window overlaps this end." },
    { name: "cursor", type: "string", required: false, description: "Pagination cursor from nextCursor." },
    { name: "topic", type: "string", required: false, description: 'Only "all" is supported (commercial ATC).' },
    lp(20, 200),
  ],
  "google-ad-library-ad-details": [{ name: "creative_id", type: "string", required: true, description: "Google Ads Transparency URL containing AR... advertiser and CR... creative IDs." }, { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }],
  "google-ad-library-advertiser-search": [qp("Advertiser or brand to search for (min 2 characters)."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }, lp(10, 50)],
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
  switch (ep.category) {
    case "transcript":
      return {
        transcript:
          "Hey everyone, welcome back to the channel. Today we're breaking down structured data APIs.",
        wordCount: 1240,
        segments: 86,
        transcriptSegments: [
          { text: "Hey everyone, welcome back to the channel.", start: 0.0, duration: 4.12, timestamp: "00:00" },
          { text: "Today we're breaking down structured data APIs.", start: 4.12, duration: 4.28, timestamp: "00:04" },
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
        total: 2,
        comments: [
          { author: "@viewer1", text: "This is exactly what I needed!", likes: 42, replies: 3 },
          { author: "@viewer2", text: "Great breakdown.", likes: 11, replies: 0 },
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

function article(label: string): string {
  return /^[aeiou]/i.test(label) ? "an" : "a";
}

/**
 * The exact 404 `detail` string the backend raises for this endpoint, taken
 * from the router sources. Returns null when the endpoint doesn't 404 in
 * practice (most searches return 200 with an empty list instead).
 */
function notFoundDetail(ep: ApiEndpoint): string | null {
  const p = ep.platform;

  if (ep.category === "search") {
    return null;
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
  komi: "https://komi.io/example",
  pillar: "https://pillar.io/example",
  linkbio: "https://lnk.bio/charlidamelio",
  linkme: "https://link.me/example",
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
      return "US";
    case "region":
      return "US";
    case "username": {
      if (ep.platform === "github") {
        const captured = API_EXAMPLES[ep.slug]?.login;
        if (typeof captured === "string" && captured.trim()) return captured;
        return "getify";
      }
      return "hydrojug";
    }
    case "repo":
      return "vercel/next.js";
    case "state":
      // Prefer closed so docs examples show mergedAt when present.
      return ep.slug === "github-pull-requests" ? "closed" : "open";
    case "sort":
      return "relevance";
    case "location":
      return "Austin, TX";
    case "details":
      return "false";
    case "advertiser":
      return "nike.com";
    case "creative_id":
      return "https://adstransparency.google.com/advertiser/AR16735076323512287233/creative/CR10754779872199966721";
    case "comment_id":
      return "7311234567890123456";
    case "limit":
      return "20";
    case "language":
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
      return "https://www.youtube.com/watch?v=dQw4w9WgXcQ,https://www.youtube.com/watch?v=jNQXAC9IVRw";
    }
    case "file":
      return "@video.mp4";
    case "url": {
      // Prefer a captured snapshot URL when it's a valid http(s) URL — keeps
      // Try-it / cURL in sync with the example response for every url param.
      const ex = API_EXAMPLES[ep.slug];
      const captured =
        (typeof ex?.url === "string" && ex.url) ||
        (typeof ex?.artistUrl === "string" && ex.artistUrl) ||
        null;
      if (typeof captured === "string" && /^https?:\/\//.test(captured)) return captured;

      const d = p.description.toLowerCase();
      const creatorPagePlatforms: PlatformId[] = ["komi", "pillar", "linkbio", "linkme"];

      if (ep.slug === "facebook-marketplace-item" || d.includes("marketplace item"))
        return "https://www.facebook.com/marketplace/item/2228870800986975/";
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
        return "https://www.linkedin.com/company/microsoft";
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
  // Location-search docs snapshot uses details=true (lat/lng). Marketplace
  // search docs use the default native list path (details=false).
  if (ep.slug === "facebook-marketplace-location-search") {
    const details = ps.find((p) => p.name === "details");
    if (details && !chosen.some((p) => p.name === "details")) {
      chosen = [...chosen, details];
    }
  }
  // Pull-requests docs snapshot uses state=closed so mergedAt is visible.
  if (ep.slug === "github-pull-requests") {
    const state = ps.find((p) => p.name === "state");
    if (state && !chosen.some((p) => p.name === "state")) {
      chosen = [...chosen, state];
    }
  }
  return chosen.map((p) => ({
    name: p.name,
    value:
      ep.slug === "facebook-marketplace-location-search" && p.name === "details"
        ? "true"
        : exampleValue(ep, p),
  }));
}

export function exampleQueryString(ep: ApiEndpoint): string {
  return exampleArgs(ep)
    .map((a) => `${a.name}=${encodeURIComponent(a.value)}`)
    .join("&");
}

export function exampleUrl(ep: ApiEndpoint): string {
  return `${API_URL}${ep.path}?${exampleQueryString(ep)}`;
}

export function curlExample(ep: ApiEndpoint): string {
  return `curl "${exampleUrl(ep)}" \\\n  -H "Authorization: Bearer capt_live_..."`;
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
  const u = requestUrl(ep, values);
  const pyParams = args.map((a) => `        "${a.name}": ${JSON.stringify(a.value)},`).join("\n");
  const phpParams = args.map((a) => `    "${a.name}" => ${JSON.stringify(a.value)},`).join("\n");

  return [
    {
      label: "cURL",
      code: `curl "${u}" \\\n  -H "Authorization: Bearer ${key}"\n# or: -H "x-api-key: ${key}"`,
    },
    {
      label: "Python",
      code: `import requests

res = requests.get(
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
  { headers: { Authorization: "Bearer ${key}" } }, // or { "x-api-key": "${key}" }
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
curl_setopt($ch, CURLOPT_HTTPHEADER, ["Authorization: Bearer ${key}"]); // or x-api-key: ${key}
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
	req, _ := http.NewRequest("GET",
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
    .GET()
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
            ? `Billing is 1 credit per successfully resolved URL that is not served from cache. Cache hits (cache=true) are free, same as Post Analytics. There is no bulk discount vs calling /v1/analytics/post once per URL — compare saves HTTP round-trips. A fully failed batch still records a minimal 1-credit charge.`
            : ep.slug === "video-transcript"
              ? `Billing is 1 credit per minute of audio (rounded up, minimum 1). Failed or empty results are never charged.`
              : ep.slug === "video-summarize"
                ? `Billing is 1 credit per minute of audio (rounded up) plus 1 credit for the AI summary. Failed or empty results are never charged.`
                : ep.creditsPerResult
                  ? `At the default limit this endpoint costs ${ep.credits} credits (${ep.creditsPerResult} per result). Billing scales with how many results you request. ${CACHE_NOTE} Failed or empty results are never charged.`
                  : `Each successful call costs ${ep.credits} credit${ep.credits === 1 ? "" : "s"}. ${
                      ep.slug === "tiktok-transcript" ? CACHE_NOTE_DEFAULT_TRUE : CACHE_NOTE
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

  if (
    ep.category === "transcript" &&
    ep.platform !== "account" &&
    ep.platform !== "utilities"
  ) {
    list.push({
      q: `What if the ${platform} ${inputKind(ep)} has no captions?`,
      a: `When no captions are available, Captapi transcribes the audio with AI (Whisper) automatically, so you still get a usable transcript.`,
    });
  }
  if (ep.category === "summarize") {
    list.push({
      q: `Which AI model powers the summaries?`,
      a: `Summaries are generated with GPT-4o-mini for a strong balance of quality, speed, and cost, built on top of the transcript.`,
    });
  }
  if (ep.slug === "spotify-artist") {
    list.push({
      q: `Is this the same as Spotify's free Web API?`,
      a: `No. Spotify's official Web API returns followers, popularity, genres, and top tracks, but not monthlyListeners, topCities, or worldRank. Those three come from the web-player GraphQL path this endpoint uses — along with topTracks playCount, concerts, and relatedArtists as clean JSON.`,
    });
  }
  if (ep.slug === "spotify-podcast") {
    list.push({
      q: `Is publisher the same as the podcast hosts?`,
      a: `No. publisher.name is the show's publisher (e.g. Hubspot). Hosts are a different concept — Captapi does not stuff publisher into artists[] the way a music schema would.`,
    });
    list.push({
      q: `What does rating mean on a podcast?`,
      a: `rating.average is Spotify's show rating (about 0–5) and rating.totalRatings is how many people voted. It's the main numeric quality signal for podcast research on this endpoint.`,
    });
  }
  if (ep.slug === "tiktok-search-users") {
    list.push({
      q: `Why do I need secUid if I already have the @handle?`,
      a: `Handles change; id and secUid do not. TikTok's follower lists, video lists, and many internal calls require secUid. Prefer id/secUid for CRM joins and chaining — use username for display.`,
    });
  }
  if (ep.slug === "instagram-tagged-posts") {
    list.push({
      q: `Why do some brands return only old tagged posts?`,
      a: `Instagram's usertags feed only returns tags the account still exposes. Mega brands that stopped approving tags (e.g. natgeo) can surface a truncated historical window — verified live — while accounts like nasa or cristiano return recent UGC. Captapi does not invent newer tags than Instagram provides.`,
    });
  }
  if (ep.slug === "threads-profile") {
    list.push({
      q: `What does isThreadsOnlyUser mean?`,
      a: `When Meta exposes it, true means the account exists only on Threads (not an Instagram-linked auto-profile). On the public web hydrate this flag is often omitted — Captapi still returns the key as null so clients can rely on a stable schema.`,
    });
  }
  if (ep.slug === "tiktok-ad-library-search") {
    list.push({
      q: `Is this TikTok Creative Center (CTR / Top Ads)?`,
      a: `No. This endpoint searches TikTok's Commercial Content Library (library.tiktok.com — EU DSA transparency). For Creative Center Top Ads with CTR, likes, industry/objective, and orderBy, use GET /v1/ad-library/tiktok/top-ads.`,
    });
  }
  if (ep.slug === "tiktok-ad-library-top-ads") {
    list.push({
      q: `How is this different from TikTok Ad Library Search?`,
      a: `Top Ads is Creative Center performance inspiration (CTR tiers, likes, industry/objective, Spark Ads, video renditions). Ad Library Search is the EU Commercial Content Library (first/last shown, reach bands). Different TikTok products — pick Top Ads for creative intel, Search for DSA transparency.`,
    });
    list.push({
      q: `How many credits does Top Ads cost?`,
      a: `Flat 2 credits on the Decodo-native Creative Center path. If that path is unavailable, the Apify fallback bills about 1 credit per returned ad (minimum 2).`,
    });
  }
  list.push({
    q: `Is the ${ep.name} suitable for production use?`,
    a: `Yes. It is a stable REST endpoint with predictable JSON and automatic retries. ${CACHE_NOTE} Use it for analytics, monitoring, and content automation.`,
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
  platform: "Platform identifier (e.g. youtube, instagram).",
  id: "Stable platform ID for the item.",
  url: "Canonical URL of the item.",
  uri: "Platform URI for the item.",
  slug: "URL slug of the item.",
  shortcode: "Instagram shortcode of the post (posts/reels only).",
  permalink: "Canonical Instagram permalink for the embed.",
  html: "Instagram's self-contained embed HTML document (drop into an <iframe srcdoc>).",
  query: "The search query you sent.",
  totalReturned: "Number of items returned in this response.",
  nextCursor: "Cursor to pass for the next page of results.",
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
  bioLinks: "External links shown on the profile ({title, url, linkType}).",
  accountBadges: "Instagram account badges when present.",
  transparencyLabel: "Account transparency label when Instagram exposes it.",
  showAccountTransparencyDetails: "Whether Instagram shows account transparency details.",
  isEmbedsDisabled: "Whether embedding this account's content is disabled.",
  isRegulatedC18: "Whether the account is age-restricted (18+).",
  showTextPostAppBadge: "Whether the Threads badge is shown on the profile.",
  removeMessageEntrypoint: "Whether the message button is hidden on the profile.",
  businessAddress: "Business address ({cityName, streetAddress, zipCode, latitude, longitude}).",
  linkedFbInfo: "Linked Facebook page info when present.",
  latestReelMedia: "Latest reel media timestamp/id when Instagram exposes it.",
  displayName: "Display name of the account.",
  name: "Name of the item or account.",
  fullName: "Full display name.",
  firstName: "First name.",
  lastName: "Last name.",
  author: "Author name or handle.",
  bio: "Profile bio or description.",
  headline: "Profile headline.",
  verified: "Whether the account is verified.",
  isVerified: "Whether the account is verified.",
  private: "Whether the account is private.",
  followers: "Follower count.",
  following: "Number of accounts followed.",
  followings: "Number of accounts followed.",
  subscriberCount: "Subscriber count.",
  connections: "Number of connections.",
  members: "Member count.",
  postCount: "Total number of posts.",
  publicPostCount: "Public posts on the Kwai profile.",
  privatePostCount: "Private posts on the Kwai profile.",
  likedCount: "Total likes received across the profile.",
  verifiedDescription: "Kwai verification label (e.g. Conta Oficial).",
  verifiedNumber: "Kwai verification tier number when present.",
  eid: "Kwai opaque profile eid.",
  creator: "Who created/cut the Kick clip (distinct from the broadcaster channel).",
  isMature: "Whether Kick marks the clip as mature content.",
  privacy: "Clip privacy (e.g. public).",
  startedAt: "When the clip segment began on the source stream (ISO 8601).",
  livestreamId: "Kick livestream id the clip was taken from.",
  vodStartsAt: "Offset into the VOD (seconds) where the clip starts.",
  categorySlug: "Kick category slug (e.g. just-chatting).",
  parentCategory: "Kick parent category (e.g. irl).",
  categoryBanner: "Category banner image URL when Kick exposes one.",
  categoryId: "Kick category id.",
  badges: "SoundCloud account badges (pro, creatorMidTier, proUnlimited, verified).",
  creatorSubscription: "SoundCloud creator subscription ({product:{id}}, e.g. creator-pro-unlimited).",
  lastModified: "When the SoundCloud profile was last modified (ISO 8601).",
  creatorMidTier: "Whether the account has SoundCloud creator mid-tier.",
  proUnlimited: "Whether the account has SoundCloud Pro Unlimited.",
  pro: "Whether the account has SoundCloud Pro.",
  curator: "Who created/cut the Twitch clip (distinct from the broadcaster channel).",
  channel: "Twitch broadcaster channel object (id, username, followers, isPartner, lastBroadcast).",
  videoQualities: "Available clip MP4 qualities ({quality, frameRate, url}).",
  playbackAccessToken: "Twitch playback token ({signature, value, expires, expiresAt}).",
  videoOffsetSeconds: "Seconds into the source VOD where the clip starts.",
  isFeatured: "Whether Twitch marks the clip as featured on the channel.",
  isPublished: "Whether the clip is published.",
  gameId: "Twitch game/category id.",
  gameSlug: "Twitch game/category slug.",
  gameBoxArtUrl: "Game box art image URL.",
  isPartner: "Whether the Twitch channel is a Partner.",
  lastBroadcast: "Most recent broadcast metadata ({startedAt, title}).",
  playCount: "Spotify stream/play count for the track.",
  trackNumber: "Track position on the album.",
  contentRating: "Spotify content rating label (e.g. NONE, EXPLICIT).",
  explicit: "Whether the track is marked explicit.",
  artistItems: "Structured Spotify artists ({id, uri, name, url}) for chaining.",
  albumInfo: "Structured Spotify album ({id, uri, name, url, releaseDate}).",
  previewUrl: "30s MP3 preview URL when Spotify exposes one.",
  mediaType: "Spotify media type (e.g. AUDIO).",
  playable: "Whether the track is playable in the web player.",
  videoCount: "Total number of videos.",
  tweetCount: "Total number of tweets.",
  mediaCount: "Total number of media posts.",
  location: "Location shown on the profile or item.",
  website: "Website listed on the profile.",
  email: "Public email when the account exposes one (GitHub: only if set public on the profile; YouTube: from About/description). Null when private or CAPTCHA-gated.",
  joinedDate: "When the account was created.",

  // Content
  title: "Title of the item.",
  text: "Text content.",
  description: "Description text.",
  caption: "Post caption.",
  publishedAt:
    "Publish date (ISO 8601). On YouTube list cards that only expose relative labels (e.g. \"1 year ago\"), this is an approximate timestamp derived from that label — see publishedTimeText for the original string.",
  publishedTimeText: "Original relative publish label from the platform when an exact timestamp was not available (e.g. \"1 year ago\").",
  totalVideos: "Total videos in the playlist (full size). Differs from totalReturned, which is this response's page length.",
  viewCountApproximate:
    "True when viewCount was parsed from a compact UI label (e.g. 2.5B / 894M) rather than an exact integer.",
  createdAt: "Creation date (ISO 8601).",
  updatedAt: "Last update date (ISO 8601).",
  timestamp: "Human-readable timestamp (MM:SS format).",
  type: "Content type of the item.",
  postType: 'Post type ("Image", "Video" or "Sidecar" for carousels).',
  productType: "Platform product type (e.g. clips, feed).",
  language: "Detected or requested language code.",
  region: "Creator's country as an ISO code (e.g. IT, US). TikTok's authoritative value when it exposes one (rare); otherwise an AI-inferred guess from public profile cues (bio, display name, language). Check regionSource. Can be null when there is no usable signal.",
  regionConfidence: 'For an inferred region, confidence of the guess: "high", "medium", or "low". Null when the region came from TikTok.',
  regionSource: 'Where region came from: "tiktok" (authoritative, reported by TikTok) or "inferred" (best-effort estimate from public signals).',
  audienceLocations: "Ranked breakdown of the audience by country, sampled from the people commenting on the creator's recent videos. Each item has country, countryCode, count, and percentage.",
  country: "Country name (e.g. Mexico, United States).",
  count: "Number of items in this bucket (e.g. commenters from this country in the sample).",
  countryCode: "ISO-3166 alpha-2 country code (e.g. US, MX).",
  percentage: "Share of the sample this country represents, as a string like \"15.96%\".",
  sampleSize: "Total number of commenter countries counted across the sampled videos.",
  videosSampled: "How many of the creator's recent videos were sampled to build the breakdown.",
  lang: "Language code of the content.",
  hashtags: "Hashtags extracted from the text.",
  mentions: "Accounts mentioned in the text.",
  tags: "Tags attached to the item.",
  topics: "Detected topics and themes.",
  category: "Category of the item.",
  nsfw: "Whether the content is marked NSFW.",
  sensitive: "Whether the content is flagged sensitive.",
  isLive: "Whether the account/channel is currently live. For TikTok Live, true only when status === 2 — a non-empty room does not mean live.",
  streamQualities: "Parsed TikTok live pull qualities ({quality, codec, resolution, bitrate, flv, hls, dash, cmaf}).",
  streams: "TikTok live pull URLs keyed by quality (hd/sd/ld/origin/ao/…); h264 preferred when both codecs exist.",
  liveSubOnly: "Whether the TikTok live is subscribers-only.",
  gameTagId: "TikTok live game/category tag id when set.",
  hashTagId: "TikTok live hashtag/category id when set.",
  streamId: "TikTok live stream id (distinct from room id when both exist).",
  isVideo: "Whether the item is a video.",
  isPinned: "Whether the item is pinned.",
  isAd: "Whether the item is a paid promotion.",
  isReply: "Whether the tweet is a reply.",
  isRetweet: "Whether the tweet is a retweet.",
  isBlueVerified: "Whether the account has blue-check verification.",
  verified: "Whether the Bluesky profile has a valid verification (verifiedStatus == valid).",
  verification:
    "Bluesky verification block: verifications[{issuer, uri, isValid, createdAt, …}], verifiedStatus, trustedVerifierStatus.",
  labels: "Moderation labels on the profile (val, src, uri, createdAt, …).",
  associated:
    "Bluesky association counts: lists, feedgens, starterPacks, labeler (plus chat/activitySubscription when present).",
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
  destinationUrl: "Click-through / landing URL from the ad creative.",
  carouselImages: "Ordered carousel creative image URLs when the ad is a carousel.",
  paidForBy: "Payer entity string from LinkedIn's 'Paid for by' line.",
  totalAds: "Total ads matching the LinkedIn Ad Library search criteria.",
  paginationToken: "Opaque LinkedIn Ad Library pagination token for the next page.",
  isLastPage: "Whether LinkedIn reports this search page as the last page.",
  channelId: "Stable YouTube channel id (UC…).",
  nextCursor: "Opaque cursor for the next page of results.",
  hasMore: "Whether another page is available (nextCursor present).",
  badges: "YouTube badges on the result (e.g. 4K, LIVE, New).",

  // Media
  thumbnailUrl: "Thumbnail image URL.",
  thumbnail: "Thumbnail image URL.",
  image: "Image URL.",
  avatar: "Avatar image URL.",
  profileImage: "Profile image URL.",
  isThreadsOnlyUser:
    "Whether the account exists only on Threads (not auto-created from Instagram). Often null on web hydrate when Meta omits the flag.",
  isPrivate: "Whether the Threads account is private.",
  bioLinks: "Links from the profile bio ({url, verified, linkId}).",
  transparencyLabel: "Meta transparency label when present (e.g. state-affiliated media).",
  profileImageVersions: "Profile image URLs at multiple resolutions ({url, width, height}).",
  hasOnboarded: "Whether the account has onboarded to Threads (text post app).",
  linkId: "Stable id for a bio link when Meta exposes one.",
  banner: "Banner image URL.",
  bannerImage: "Banner image URL.",
  bannerUrl: "Banner image URL.",
  coverImage: "Cover image URL.",
  coverUrl: "Cover image URL.",
  logo: "Logo image URL.",
  videoUrl: "Direct video file URL (CDN link); may be null when the platform does not expose one.",
  music: "Reel soundtrack metadata (id, type, trackTitle, albumArt) when Facebook exposes it.",
  videoHeight: "Video height in pixels when available.",
  videoWidth: "Video width in pixels when available.",
  videoHdUrl: "High-definition playable video URL when Facebook exposes one.",
  videoSdUrl: "Standard-definition playable video URL when Facebook exposes one.",
  captionsUrl: "URL to Facebook-generated captions (.srt) when exposed on the post/Reel.",
  feedbackId: "Facebook feedback id for the post (useful for comments threading).",
  downloadUrl: "CDN media URL when present (not a dedicated download API).",
  noWatermarkUrl: "Watermark-free variant of the video URL.",
  embedUrl: "Embed page URL — load it directly in an <iframe src>.",
  gameBoxArtUrl: "Twitch category/game box art image URL (usually 144×192).",
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
  images: "Image URLs attached to the item.",
  photos: "Photo URLs attached to the item.",

  // Duration
  duration: "Length in seconds.",
  durationSeconds: "Length in seconds.",
  durationMs: "Length in milliseconds.",
  durationFormatted: "Human-readable duration.",
  start: "Start time in seconds.",
  end: "End time in seconds.",
  expiresAt: "When signed URLs expire (ISO 8601).",

  // Engagement
  engagement: "Engagement metrics for the item.",
  views: "View count.",
  viewCount: "View count.",
  plays: "Play count.",
  playCount: "Play count.",
  likes: "Like count.",
  likeCount: "Like count.",
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
  score: "Vote score.",
  rank: "Rank position in the list.",
  engagementRate: "Engagement rate as interactions / views (ratio, not percent). Null when views or interactions are missing.",
  suggestion: "A search term TikTok autocompletes for your keyword — a phrase real users search for.",
  searchUrl: "Direct TikTok search URL for this suggestion — open it to see the matching results.",
  seed: "The seed keyword this suggestion was expanded from.",

  // Transcript / summarize
  transcript: "Complete text transcript.",
  wordCount: "Total number of words in the transcript.",
  segments: "Transcript segment count, or sponsor segment list on video-sponsors endpoints.",
  transcriptSegments: "Timestamped transcript segments.",
  source:
    'Where the transcript came from: "captions" (platform subtitles), "whisper" (AI speech-to-text fallback), or "fallback" (secondary caption path). Use this to weight RAG quality.',
  isAutoGenerated: "Whether the selected YouTube caption track is auto-generated (ASR). Null when source is not captions.",
  isTranslated: "Whether the transcript was machine-translated to the requested language. Null when unknown.",
  availableLanguages: "Caption languages available on the video (languageCode, languageName, isAutoGenerated).",
  // Meta Ad Library (additive)
  isActive: "Whether the ad is currently eligible for delivery.",
  publisherPlatforms: "Where the ad ran (FACEBOOK, INSTAGRAM, MESSENGER, AUDIENCE_NETWORK, …).",
  caption: "Creative caption when Meta exposes one.",
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
  videos: "Typed video assets ({url, sdUrl, previewUrl}). media[] remains the flat URL list.",
  spendRange:
    "Parsed spend as {min, max, currency, raw}. Prefer this for sorting; spend stays the Meta display string. Usually null for commercial ads.",
  impressionsRange:
    "Parsed impressions as {min, max, raw}. Prefer this for sorting; impressions stays the Meta display string. Usually null for commercial ads.",
  searchResultsCount: "Best-effort total hits Meta reports for the query (not just this page).",
  hasMore: "Whether more results likely exist beyond this page.",
  nextCursor: "Pagination cursor for the next page when available; currently null for Facebook search.",
  status: "Delivery status filter applied to the search (ACTIVE, INACTIVE, or ALL).",
  limit: "Requested max items for this call.",
  authorFullname: "Stable Reddit account fullname (t2_…). Prefer this over author for joins.",
  score: "Reddit score (ups − downs when both are exposed).",
  downs: "Downvote count when Reddit exposes it (often 0 on public JSON).",
  distinguished: "moderator/admin distinction when present.",
  controversiality: "Reddit controversiality flag (0 or 1).",
  upvoteRatio: "Post upvote ratio (0–1) when Reddit exposes it.",
  subscriberCount: "Subreddit subscriber count at fetch time.",
  isVideo: "Whether the Reddit post is a video post.",
  experience: "LinkedIn experience entries when available (title, company, dates, description).",
  education: "LinkedIn education entries when available (school, degree, dates).",
  currentCompany: "Current company inferred from LinkedIn worksFor / headline — not SEO meta.",
  originalPrice: "List/original price before discount (numeric when unmasked).",
  discount: "Discount display string when TikTok Shop exposes one (e.g. -47%).",
  skus: "Per-variant SKU rows ({id, stock, price, originalPrice, status}).",
  shopInfo: "Shop rollup (sold, followers, productCount, identityLabel) when available.",
  relatedVideos: "Affiliate/related TikTok videos promoting the product when available.",
  // Prefer context: Ad Library typed images, TikTok Shop gallery, or generic media.
  images: "Image assets — typed {url,resizedUrl} on Ad Library, gallery URLs on TikTok Shop, else URL list.",
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
  originalPrice: "Price before discount.",
  discount: "Discount amount or percentage.",
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
  verified: "Whether the artist is verified on Spotify.",
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
  explicit: "Whether the track is marked explicit.",
  isrc: "International Standard Recording Code.",
  musicName: "Name of the soundtrack used.",
  musicUrl: "URL of the soundtrack used.",
  musicId: "ID of the soundtrack used.",

  // Channels / streaming
  channelName: "Name of the channel.",
  channelUrl: "URL of the channel.",
  channelId: "ID of the channel.",
  channelFollowers: "Follower count of the channel.",
  channelVerified: "Whether the channel is verified.",
  game: "Game or category being streamed.",
  viewers: "Current live viewer count.",
  viewerCount: "Current live viewer count.",
  startedAt: "When the stream started (ISO 8601).",
  broadcaster: "Name of the broadcaster.",
  isPartner: "Whether the channel is a platform partner.",
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

/** Description for a single field, preferring the curated dictionary. */
function describeField(name: string, value: unknown): string {
  if (RAW_KEYS.has(name)) return FIELD_DESCS.raw;
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
      return `Array of objects with ${Object.keys(first).slice(0, 6).join(", ")}.`;
    }
    return FIELD_DESCS[name] ?? `${humanizeField(name)} (array).`;
  }
  if (value && typeof value === "object") {
    const keys = Object.keys(value as Record<string, unknown>);
    if (keys.length === 0) return FIELD_DESCS[name] ?? `${humanizeField(name)}.`;
    return `Object with ${keys.slice(0, 6).join(", ")}.`;
  }
  return FIELD_DESCS[name] ?? `${humanizeField(name)}.`;
}

function fieldsFromObject(obj: Record<string, unknown>): ResponseField[] {
  return Object.entries(obj).map(([k, v]) => ({ name: k, desc: describeField(k, v) }));
}

/** Build the documented response structure from a real example payload. */
function structureFromExample(data: Record<string, unknown>): ResponseGroup[] {
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
          fields: fieldsFromObject(first),
        });
        continue;
      }
      top.push({ name: key, desc: describeField(key, value) });
      continue;
    }
    if (value && typeof value === "object") {
      const inner = value as Record<string, unknown>;
      if (Object.keys(inner).length > 0) {
        nested.push({
          title: humanizeField(key),
          note: `The ${key} object contains:`,
          fields: fieldsFromObject(inner),
        });
        continue;
      }
    }
    top.push({ name: key, desc: describeField(key, value) });
  }

  const groups: ResponseGroup[] = [];
  if (top.length > 0) groups.push({ title: "Top-level fields", fields: top });
  groups.push(...nested);
  return groups;
}

export function responseStructure(ep: ApiEndpoint): ResponseGroup[] {
  const real = API_EXAMPLES[ep.slug];
  if (real && Object.keys(real).length > 0) {
    const derived = structureFromExample(real);
    if (derived.length > 0) return derived;
  }
  switch (ep.category) {
    case "transcript":
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
          fields: [{ name: "total", desc: "Number of comments returned." }],
        },
        {
          title: "Each comment",
          note: "Each item in comments contains:",
          fields: [
            { name: "author", desc: "Comment author name or handle." },
            { name: "text", desc: "The comment text." },
            { name: "likes", desc: "Number of likes on the comment." },
            { name: "replies", desc: "Number of replies in the thread." },
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

export function useCases(ep: ApiEndpoint): UseCase[] {
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
      return [
        { title: "Analytics", desc: "Track views, likes, and engagement over time." },
        { title: "Competitor Monitoring", desc: "Benchmark the performance of other creators." },
        { title: "Dashboards", desc: "Power reporting and BI with real metadata." },
        { title: "Content Curation", desc: "Filter and rank videos by performance." },
      ];
    case "comments":
      return [
        { title: "Sentiment Analysis", desc: "Understand how audiences react to content." },
        { title: "Community Insights", desc: "Surface FAQs, requests, and recurring themes." },
        { title: "Moderation", desc: "Detect spam, abuse, or policy violations at scale." },
        { title: "Market Research", desc: "Mine genuine opinions and product feedback." },
      ];
    case "channel":
      return [
        { title: "Influencer Discovery", desc: "Find and vet creators by audience size." },
        { title: "CRM Enrichment", desc: "Add social stats to your contact profiles." },
        { title: "Competitive Analysis", desc: "Track follower growth and posting cadence." },
        { title: "Outreach", desc: "Qualify partnership and sponsorship targets." },
      ];
    case "search":
      return [
        { title: "Trend Discovery", desc: "Find trending content by keyword or hashtag." },
        { title: "Content Sourcing", desc: "Build feeds and playlists programmatically." },
        { title: "Monitoring", desc: "Track topics, brands, and competitors." },
        { title: "Research", desc: "Sample large sets of content for analysis." },
      ];
    case "list":
      return [
        { title: "Content Pipelines", desc: "Ingest a channel's catalog in bulk." },
        { title: "Monitoring", desc: "Detect new uploads automatically." },
        { title: "Archiving", desc: "Snapshot a creator's full library." },
        { title: "Analytics", desc: "Aggregate performance across many videos." },
      ];
  }
}
