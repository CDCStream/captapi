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
  | "github"
  | "ad_library"
  | "twitch"
  | "spotify"
  | "soundcloud"
  | "linktree"
  | "snapchat"
  | "truth_social"
  | "kick"
  | "amazon_shop"
  | "account"
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
    | "video"
    | "cloud"
    | "search"
    | "link"
    | "ghost";
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
export function creditLabel(e: Pick<ApiEndpoint, "credits">): string {
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
  github: "GitHub",
  ad_library: "Ad Library",
  twitch: "Twitch",
  spotify: "Spotify",
  soundcloud: "SoundCloud",
  linktree: "Linktree",
  snapchat: "Snapchat",
  truth_social: "Truth Social",
  kick: "Kick",
  amazon_shop: "Amazon Shop",
  account: "Account",
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
  { slug: "youtube-transcript", name: "YouTube Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/youtube/transcript", credits: 2 },
  { slug: "youtube-summarizer", name: "YouTube Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/youtube/summarize", credits: 4 },
  { slug: "youtube-video-details", name: "YouTube Video Details API", shortName: "Video Details", category: "details", method: "GET", path: "/v1/youtube/video-details", credits: 1 },
  { slug: "youtube-comments", name: "YouTube Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/youtube/comments", credits: 20, creditsPerResult: 0.4 },
  { slug: "youtube-channel-details", name: "YouTube Channel Details API", shortName: "Channel Details", category: "channel", method: "GET", path: "/v1/youtube/channel-details", credits: 1 },
  { slug: "youtube-search", name: "YouTube Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/youtube/search", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-channel-videos", name: "YouTube Channel Videos API", shortName: "Channel Videos", category: "list", method: "GET", path: "/v1/youtube/channel-videos", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-playlist-videos", name: "YouTube Playlist Videos API", shortName: "Playlist Videos", category: "list", method: "GET", path: "/v1/youtube/playlist-videos", credits: 50, creditsPerResult: 1 , tagline: "List the videos in a YouTube playlist — URL, title, and position for each item.", longDescription: "Paste a YouTube playlist URL and get the videos in that playlist as a structured list. Use Playlist when you also need playlist title and description in the same response. No YouTube OAuth required." },
  { slug: "youtube-playlist", name: "YouTube Playlist API", shortName: "Playlist", category: "list", method: "GET", path: "/v1/youtube/playlist", credits: 50, creditsPerResult: 1 , tagline: "Get a YouTube playlist's metadata plus its videos — title, description, and each video's URL, title, and position.", longDescription: "Paste a YouTube playlist URL and get both the playlist details (title, description, channel) and the videos in it as structured JSON. Prefer this when you need playlist info and the video list together. For only the video list, use Playlist Videos. No YouTube OAuth required." },
  { slug: "youtube-shorts-transcript", name: "YouTube Shorts Transcript API", shortName: "Shorts Transcript", category: "transcript", method: "GET", path: "/v1/youtube/shorts/transcript", credits: 2 },
  { slug: "youtube-shorts-summarizer", name: "YouTube Shorts Summarizer API", shortName: "Shorts Summarizer", category: "summarize", method: "GET", path: "/v1/youtube/shorts/summarize", credits: 4 },
  { slug: "youtube-shorts-stats", name: "YouTube Shorts Stats API", shortName: "Shorts Stats", category: "details", method: "GET", path: "/v1/youtube/shorts/video-details", credits: 1 },
  { slug: "youtube-shorts-comments", name: "YouTube Shorts Comments API", shortName: "Shorts Comments", category: "comments", method: "GET", path: "/v1/youtube/shorts/comments", credits: 20, creditsPerResult: 0.4 },
  { slug: "youtube-channel-shorts", name: "YouTube Channel Shorts API", shortName: "Channel Shorts", category: "list", method: "GET", path: "/v1/youtube/channel-shorts", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-trending-shorts", name: "YouTube Trending Shorts API", shortName: "Trending Shorts", category: "list", method: "GET", path: "/v1/youtube/trending-shorts", credits: 28, creditsPerResult: 1.4 },
  { slug: "youtube-channel-streams", name: "YouTube Channel Streams API", shortName: "Channel Streams", category: "list", method: "GET", path: "/v1/youtube/channel-streams", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-hashtag-search", name: "YouTube Hashtag Search API", shortName: "Hashtag Search", category: "search", method: "GET", path: "/v1/youtube/hashtag-search", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-comment-replies", name: "YouTube Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/youtube/comment-replies", credits: 20, creditsPerResult: 0.4 },
  { slug: "youtube-channel-playlists", name: "YouTube Channel Playlists API", shortName: "Channel Playlists", category: "list", method: "GET", path: "/v1/youtube/channel-playlists", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-community-posts", name: "YouTube Community Posts API", shortName: "Community Posts", category: "list", method: "GET", path: "/v1/youtube/community-posts", credits: 10, creditsPerResult: 0.5 },
  { slug: "youtube-community-post-details", name: "YouTube Community Post Details API", shortName: "Community Post Details", category: "details", method: "GET", path: "/v1/youtube/community-post-details", credits: 1 , tagline: "Get a YouTube community post — text, images, poll options, likes, and comments as structured JSON.", longDescription: "Paste a YouTube community post URL and get the post as clean JSON: the text, attached images, poll options when present, like and comment counts, publish date, and the channel that posted it. Use it to archive community updates, track polls, or feed a content calendar. No YouTube OAuth required — results are cached for 24 hours." },
  { slug: "youtube-video-sponsors", name: "YouTube Video Sponsors API", shortName: "Video Sponsors", category: "details", method: "GET", path: "/v1/youtube/video-sponsors", credits: 1 , tagline: "Find sponsor, self-promo, and interaction segments inside a YouTube video — start/end times and category for each segment.", longDescription: "Paste a YouTube video URL and get the sponsor and promo segments viewers have marked for that video: each segment includes a category (sponsor, self-promo, interaction, and similar), plus start and end timestamps. Useful for skipping ads in players, estimating brand-deal density, or cleaning footage for reuse. No YouTube OAuth required." },
];

const TIKTOK: Spec[] = [
  { slug: "tiktok-transcript", name: "TikTok Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/tiktok/transcript", credits: 2 },
  { slug: "tiktok-summarizer", name: "TikTok Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/tiktok/summarize", credits: 4 },
  { slug: "tiktok-video-details", name: "TikTok Video Details API", shortName: "Video Details", category: "details", method: "GET", path: "/v1/tiktok/video-details", credits: 1, tagline: "Get everything about one TikTok video from its URL — caption, view/like/comment/share/save counts, creator, sound, hashtags, and thumbnail.", longDescription: "Paste any public TikTok video URL and the TikTok Video Details API returns the full picture as clean JSON: the caption, when it was posted, how long it runs, and its engagement — views, likes, comments, shares, and saves. You also get the creator (username, display name, follower count, verified badge, and avatar), the sound/music name, the list of hashtags, and a thumbnail image. Use it to build analytics dashboards, track a campaign, or enrich a content database. This endpoint focuses on metadata and stats. No TikTok login and no proxies or infrastructure to maintain on your side, and results are cached for 24 hours, so repeat lookups are instant and free.", delivers: ["Caption, publish date, and video duration", "Views, likes, comments, shares, and saves", "Creator profile — handle, name, followers, verified, avatar", "Sound name, hashtags, and thumbnail image"] },
  { slug: "tiktok-comments", name: "TikTok Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/tiktok/comments", credits: 2, tagline: "Get the comments on any TikTok video — text, author, avatar, likes, and timestamp for each one, with cursor pagination to page through them all.", longDescription: "Paste a public TikTok video URL and the TikTok Comments API returns its comments as clean JSON. Each comment includes the text, the author's username and avatar, how many likes it has, and when it was posted. The response also reports totalComments — the video's full comment count. Fetch up to 500 comments per call with the limit parameter, then pass the returned nextCursor value back in to page through the rest — a flat 2 credits per call, no matter how many comments you fetch. Need the actual reply threads under a comment? Pass that comment's id to the TikTok Comment Replies API. Ideal for sentiment analysis, social listening, moderation, and spotting engaged fans. No TikTok login and no proxies or infrastructure to maintain on your side.", delivers: ["Comment text, author username, and avatar", "Like count and publish time per comment", "totalComments plus cursor pagination (nextCursor) through every comment", "limit up to 500 — a flat 2 credits per call", "Pair with Comment Replies to pull reply threads"] },
  { slug: "tiktok-channel-details", name: "TikTok Channel Details API", shortName: "Channel Details", category: "channel", method: "GET", path: "/v1/tiktok/channel-details", credits: 1 , tagline: "Get a TikTok profile's key stats — followers, following, likes, video count, bio, and verification." },
  { slug: "tiktok-profile-region", name: "TikTok Profile Region API", shortName: "Profile Region", category: "channel", method: "GET", path: "/v1/tiktok/profile-region", credits: 2 , tagline: "Find out where a TikTok creator is likely based and what language they use — country, language, and core profile stats.", longDescription: "Give the TikTok Profile Region API a profile URL, @handle, or username and it returns location and language as clean JSON. TikTok almost never shows an account's country publicly, so when that value is missing we estimate the country from public cues like the bio, display name, and language. The response tells you whether the country came from TikTok itself or from that estimate, and how confident the estimate is (high, medium, or low). You also get the interface language and core profile stats — followers, following, total likes, and video count — plus display name, verified and private flags, and the avatar. Use it for audience and geo analysis, content localization, compliance checks, or vetting creators before a partnership. Flat 2 credits per call, and results are cached for 24 hours.", delivers: ["Creator country — TikTok's own when available, otherwise an AI estimate", "Whether the country came from TikTok or was estimated, plus confidence", "Interface language plus followers, following, likes, and video count", "Display name, verified and private flags, and avatar"] },
  { slug: "tiktok-audience-demographics", name: "TikTok Audience Demographics API", shortName: "Audience Demographics", category: "channel", method: "GET", path: "/v1/tiktok/audience-demographics", credits: 3 , tagline: "See which countries a TikTok creator's audience comes from — a ranked country breakdown based on people who comment on their videos.", longDescription: "Give the TikTok Audience Demographics API a profile URL, @handle, or username and it returns a ranked country breakdown of the creator's audience as clean JSON. TikTok does not publish follower geography, but commenters often expose a country — so we sample people commenting on the creator's recent videos and tally countries into a list with country name, country code, count, and percentage. You also get how many videos and commenters were sampled. This reflects who engages, not a full follower census. Use it for market sizing, geo targeting, localization, and influencer vetting. Flat 3 credits per call, and results are cached for 24 hours.", delivers: ["Ranked countries with name, code, count, and percentage", "Country mix based on real commenters, not a follower census", "How many videos and commenters were sampled", "Computed from public TikTok engagement data"] },
  { slug: "tiktok-search-suggestions", name: "TikTok Search Suggestions API", shortName: "Search Suggestions", category: "search", method: "GET", path: "/v1/tiktok/search-suggestions", credits: 28, creditsPerResult: 1.4, tagline: "Get the autocomplete terms TikTok suggests in its search bar for a keyword — the real phrases people search, ranked, so you can find trending queries and long-tail keyword ideas.", delivers: ["The autocomplete terms TikTok suggests for your keyword", "Each suggestion with its rank — the order it appears in the search bar", "A ready-to-open searchUrl that runs that exact search on TikTok", "The seed keyword plus the region and language it was localized for", "Localize by country + language to see what a specific market searches"] , longDescription: "Give the TikTok Search Suggestions API a seed keyword and it returns the autocomplete phrases TikTok shows in its search bar as clean JSON — the actual phrases people search for. Each suggestion includes the search term, its rank (1 = top of the list), a ready-to-open search URL, the seed keyword it came from, and the country and language it was localized for. Use the country and language parameters to see what a specific market is searching (for example US in English, or DE in German). Great for TikTok keyword research, trending queries, and content planning. No TikTok login required. Billed per suggestion returned, and results are cached for 24 hours." },
  { slug: "tiktok-channel-posts", name: "TikTok Channel Posts API", shortName: "Channel Posts", category: "list", method: "GET", path: "/v1/tiktok/channel-posts", credits: 2, tagline: "Get the latest videos from any public TikTok profile — caption, view / like / comment counts, thumbnail, sound, and hashtags for each post, with cursor pagination to page through them all." , longDescription: "Send a profile URL, @handle, or username and the TikTok Channel Posts API returns that creator's most recent videos as clean, structured JSON. If TikTok blocks a direct fetch, the first page automatically retries through a backup path so you still get a response. Each post includes the TikTok page URL and video ID, caption, publish date, duration, thumbnail, hashtags, and the sound/music name, plus full engagement — views, likes, comments, shares, and saves — and the author's profile (username, display name, followers, verified badge, avatar). Fetch up to 200 posts per call with the limit parameter, then pass the returned nextCursor value back in to page through older videos (hasMore tells you when you've reached the end) — a flat 2 credits per call, no matter how many posts you fetch. Ideal for creator monitoring, content calendars, competitor tracking, and feeding analytics or influencer tools. This endpoint focuses on metadata and stats. No TikTok login and no infrastructure to maintain on your side.", delivers: ["Latest public videos from any TikTok profile", "Caption, publish date, duration, thumbnail, hashtags, and sound name", "Views, likes, comments, shares, and saves per video", "Author profile — handle, name, followers, verified, avatar", "Cursor pagination (nextCursor + hasMore) — flat 2 credits per call", "Automatic first-page backup if the direct fetch fails"] },
  { slug: "tiktok-comment-replies", name: "TikTok Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/tiktok/comment-replies", credits: 2, tagline: "Get the replies under any TikTok comment — text, author, likes, and timestamp for each one, with cursor pagination.", longDescription: "Pass a TikTok video URL and a parent comment id and get that comment's replies as clean JSON. Each reply includes text, author, like count, and publish time. Fetch up to 500 replies per call, then pass nextCursor to page through the rest — a flat 2 credits per call. No TikTok login required.", delivers: ["Reply text, author, and profile image", "Like count and publish time per reply", "Cursor pagination (nextCursor + hasMore)", "Flat 2 credits per call"] },
  { slug: "tiktok-user-followers", name: "TikTok User Followers API", shortName: "User Followers", category: "list", method: "GET", path: "/v1/tiktok/user-followers", credits: 20, creditsPerResult: 0.4 },
  { slug: "tiktok-user-followings", name: "TikTok User Followings API", shortName: "User Followings", category: "list", method: "GET", path: "/v1/tiktok/user-followings", credits: 20, creditsPerResult: 0.4 },
  { slug: "tiktok-music-posts", name: "TikTok Music Posts API", shortName: "Music Posts", category: "list", method: "GET", path: "/v1/tiktok/music-posts", credits: 32, creditsPerResult: 1.6 , tagline: "List TikTok videos that use a specific sound — caption, author, and engagement for each post.", longDescription: "Paste a TikTok music/sound URL and get the public videos that use that sound as structured JSON. Each result includes caption, author, thumbnail, and engagement counts. Use Song Details first if you only need the sound's metadata. Billed per result." },
  { slug: "tiktok-top-search", name: "TikTok Top Search API", shortName: "Top Search", category: "search", method: "GET", path: "/v1/tiktok/top-search", credits: 14, creditsPerResult: 0.7 , tagline: "Search TikTok's top mixed results for a keyword — videos and related hits ranked the way TikTok's search ranks them.", longDescription: "Pass a keyword and get TikTok's top mixed search results as structured JSON — the same style of ranked hits you see in TikTok search, not a single content type only. Each result includes the fields TikTok exposes for that hit (URL, caption or title, author, engagement when available). Billed per result." },
  { slug: "tiktok-search-by-hashtag", name: "TikTok Search by Hashtag API", shortName: "Search by Hashtag", category: "search", method: "GET", path: "/v1/tiktok/search/hashtag", credits: 14, creditsPerResult: 0.7, tagline: "Search TikTok videos by hashtag — video URL, caption, author, and view / like / comment counts for each result, with cursor pagination to page through them all.", delivers: ["Public videos posted under your hashtag", "Video URL, caption, thumbnail, duration, and publish date", "Author profile plus view / like / comment / share / save counts", "Cursor pagination (nextCursor + hasMore) through every result"] , longDescription: "Pass a hashtag (with or without the #) and the TikTok Search by Hashtag API returns the videos posted under that tag as clean, structured JSON. Each result includes the video URL, caption, publish date, duration, thumbnail, the author's profile, and full engagement counts — views, likes, comments, shares, and saves — plus the hashtags and sound used. Need more than the first page? Pass the nextCursor value from the previous response to keep paging, and use hasMore to know when you've reached the end. An optional region parameter only chooses which country our request is sent from — it does not filter results by country. Use it to track a campaign or branded hashtag, discover trending content in a niche, or build a themed content feed. No TikTok login required. Billed per result — about 0.7 credits each." },
  { slug: "tiktok-search-users", name: "TikTok Search Users API", shortName: "Search Users", category: "search", method: "GET", path: "/v1/tiktok/search/users", credits: 8, creditsPerResult: 0.4, tagline: "Search TikTok users by keyword — username, display name, bio, follower count, verified flag, and avatar for each matching creator, with cursor pagination.", longDescription: "Pass a search query and the TikTok Search Users API returns the creators whose username, display name, or bio match it as clean, structured JSON. Each result includes the username, display name, profile URL, bio, follower count, verified flag, and avatar. Need more than the first page? Pass the nextCursor value from the previous response to keep paging, and use hasMore to know when you've reached the end. Use it to turn a brand or creator name into confirmed @handles, discover creators in a niche, enrich a CRM or lead list, or feed an influencer-discovery tool. No TikTok login and no proxies or infrastructure to maintain on your side. Billed per result — about 0.4 credits each.", delivers: ["Public creators matching your search query", "Username, display name, profile URL, and bio", "Follower count, verified flag, and avatar", "Cursor pagination (nextCursor + hasMore) through every result"] },
  { slug: "tiktok-song-details", name: "TikTok Song Details API", shortName: "Song Details", category: "details", method: "GET", path: "/v1/tiktok/song-details", credits: 2 , tagline: "Get details for a TikTok sound — title, artist, duration, cover art, and how many videos use it.", longDescription: "Paste a TikTok music/sound URL and get the sound's metadata as clean JSON: title, artist or original creator, duration, cover image, and usage count when available. Pair with Music Posts to list videos that use the same sound. Flat 2 credits per call." },
  { slug: "tiktok-trending-feed", name: "TikTok Trending Feed API", shortName: "Trending Feed", category: "list", method: "GET", path: "/v1/tiktok/trending-feed", credits: 14, creditsPerResult: 0.7 , tagline: "Get videos from TikTok's trending feed — caption, author, and engagement for each item." },
  { slug: "tiktok-popular-hashtags", name: "TikTok Popular Hashtags API", shortName: "Popular Hashtags", category: "list", method: "GET", path: "/v1/tiktok/popular-hashtags", credits: 14, creditsPerResult: 0.7 , tagline: "Get currently popular TikTok hashtags — name and popularity signals for each tag." },
  { slug: "tiktok-live", name: "TikTok Live API", shortName: "Live", category: "details", method: "GET", path: "/v1/tiktok/live", credits: 1 , tagline: "Check whether a TikTok user is live right now — live status and basic room info when they are.", longDescription: "Send a TikTok profile URL or @handle and learn if that creator is currently live. When they are live you get basic room fields; when they are not, you get a clear offline status. For richer room details (title, viewer counts, and more), use Live Info. Flat 1 credit per call." },
  { slug: "tiktok-live-info", name: "TikTok Live Info API", shortName: "Live Info", category: "details", method: "GET", path: "/v1/tiktok/live-info", credits: 7 , tagline: "Get details for a TikTok live room — title, host, viewer counts, and stream metadata when available.", longDescription: "Send a TikTok live or profile URL and get richer live-room details as structured JSON: title, host, viewer signals, and related stream fields when the room is active. Use Live for a cheap online/offline check first. Flat 7 credits per call." },
  { slug: "tiktok-popular-creators", name: "TikTok Popular Creators API", shortName: "Popular Creators", category: "list", method: "GET", path: "/v1/tiktok/popular-creators", credits: 28, creditsPerResult: 1.4 , tagline: "Discover popular TikTok creators — handle, follower count, and profile fields for each account." },
];

const INSTAGRAM: Spec[] = [
  { slug: "instagram-transcript", name: "Instagram Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/instagram/transcript", credits: 2, tagline: "Turn any Instagram Reel's speech into text — the full transcript plus timestamped segments, ready for search, subtitles, or AI pipelines." , longDescription: "Send a Reel URL and the Instagram Transcript API returns everything spoken in the video as clean text: the full transcript, timestamped segments (start time and duration for each line), and word count. Auto-detects the spoken language, or pass an optional language code (like 'tr' or 'en') to pin it — recommended for short clips. Great for making Reels searchable, generating subtitles, feeding AI tools, or turning video into text. No Instagram login or OAuth required — results are cached for 24 hours, so repeat lookups are instant and free." },
  { slug: "instagram-summarizer", name: "Instagram Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/instagram/summarize", credits: 4, tagline: "Get an AI summary of any Instagram Reel — a short paragraph plus key points, without watching the video.", longDescription: "Send a Reel URL and the Instagram Summarizer API transcribes the video and returns an AI-written summary as clean JSON: a concise paragraph plus a list of key points. Pass an optional language code (like 'tr') to pin the speech language and get the summary in that language — otherwise it auto-detects and summarizes in English. Perfect for content research at scale, briefing tools, and AI agents that need to understand video content without processing media. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side — results are cached for 24 hours, so repeat lookups are instant and free." },
  { slug: "instagram-details", name: "Instagram Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/instagram/details", credits: 1 , tagline: "Get an Instagram post or Reel — caption, likes, comments, media URLs, author, and publish date.", longDescription: "Paste an Instagram post or Reel URL and get the item as clean JSON: caption, like and comment counts, media URLs (image or video), author profile, duration when it is a Reel, and publish date. Use it for analytics dashboards, content databases, or campaign tracking. Flat 1 credit per call — no Instagram login or OAuth, and results are cached for 24 hours.", delivers: ["Caption, media URLs, and publish date", "Like and comment counts", "Author profile fields", "Duration for Reels when available"] },
  { slug: "instagram-comments", name: "Instagram Post Comments API", shortName: "Post Comments", category: "comments", method: "GET", path: "/v1/instagram/comments", credits: 45, creditsPerResult: 0.9, tagline: "Get the comments on any Instagram post or Reel — text, author, avatar, likes, and timestamp for each comment.", longDescription: "Send a post or Reel URL and the Instagram Post Comments API returns its comments as clean, structured JSON. Each comment includes the text, author username and avatar, like count, and when it was posted. Use the limit parameter (up to 500) to control how many you fetch — billing scales with results returned. Ideal for sentiment analysis, social listening, comment moderation, and finding engaged fans or customer feedback. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side — results are cached for 24 hours, so repeat lookups are instant and free." },
  { slug: "instagram-channel-details", name: "Instagram Channel Details API", shortName: "Channel Details", category: "channel", method: "GET", path: "/v1/instagram/channel-details", credits: 1, tagline: "Get any public Instagram profile's key stats in one call — followers, following, post count, bio, and verification status.", longDescription: "Send a profile URL or @handle and the Instagram Channel Details API returns the account's profile as clean, structured JSON: display name, bio, follower and following counts, total posts, profile image, and whether it's verified. It's the go-to endpoint for influencer vetting, competitor tracking, audience dashboards, and enriching user records with live Instagram stats. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side — results are cached for 24 hours, so repeat lookups are instant and free." },
  { slug: "instagram-channel-posts", name: "Instagram Channel Posts API", shortName: "Channel Posts", category: "list", method: "GET", path: "/v1/instagram/channel-posts", credits: 6, creditsPerResult: 0.3, tagline: "Get the latest posts from any public Instagram profile — caption, media URLs, likes, comments, and publish date for each post, with cursor pagination for older ones.", longDescription: "Send a profile URL or @handle and the Instagram Channel Posts API returns that account's most recent posts as clean, structured JSON. Each post includes the caption, image or video URLs, like and comment counts, post type, and publish date. Need more than the first page? Pass the nextCursor value from the previous response to keep paging through older posts. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side — results are cached for 24 hours, so repeat lookups are instant and free." },
  { slug: "instagram-channel-reels", name: "Instagram Channel Reels API", shortName: "Channel Reels", category: "list", method: "GET", path: "/v1/instagram/channel-reels", credits: 6, creditsPerResult: 0.3, tagline: "Get the latest Reels from any public Instagram profile — video URL, caption, views, likes, comments, and duration for each Reel, with cursor pagination for older ones.", longDescription: "Send a profile URL or @handle and the Instagram Channel Reels API returns that account's most recent Reels as clean, structured JSON. Photo and carousel posts are filtered out — you only get videos, each with its direct video URL, caption, view / like / comment counts, duration, and publish date. Need more than the first page? Pass the nextCursor value from the previous response to keep paging through older Reels. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side — results are cached for 24 hours, so repeat lookups are instant and free." },
  { slug: "instagram-reels-search", name: "Instagram Reels Search API", shortName: "Reels Search", category: "search", method: "GET", path: "/v1/instagram/reels-search", credits: 12, creditsPerResult: 0.6, tagline: "Search Instagram Reels by hashtag or keyword — video URL, caption, author, views, likes, and comments for each matching Reel.", longDescription: "Send a hashtag (without the #) or keyword and the Instagram Reels Search API returns matching Reels as clean, structured JSON — videos only, no photos or carousels. Each result includes the direct video URL, caption, author profile, view / like / comment counts, duration, and publish date. Use it to research what's working in a niche, find creators around a topic, or feed content-discovery tools. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side — results are cached for 24 hours, so repeat lookups are instant and free." },
  { slug: "instagram-trending-reels", name: "Instagram Trending Reels API", shortName: "Trending Reels", category: "list", method: "GET", path: "/v1/instagram/trending-reels", credits: 28, creditsPerResult: 1.4, tagline: "Get the Reels currently trending on Instagram's Explore feed for a chosen country — video URL, caption, author, views, likes, and comments for each one.", longDescription: "The Instagram Trending Reels API returns what's blowing up on Instagram right now. Pass a country name (default United States) and you get the Reels currently featured on that country's Explore feed as clean, structured JSON — each with its direct video URL, caption, author profile, and view / like / comment counts. No hashtag or keyword needed: this is Instagram's own trending selection, useful for spotting viral content, tracking trends by region, or seeding content-research tools. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side — results are cached for 24 hours, so repeat lookups are instant and free." },
  { slug: "instagram-tagged-posts", name: "Instagram Tagged Posts API", shortName: "Tagged Posts", category: "list", method: "GET", path: "/v1/instagram/tagged-posts", credits: 18, creditsPerResult: 0.9, tagline: "Get the posts where an Instagram account is tagged by other users — caption, media URLs, author, likes, comments, and publish date for each post.", longDescription: "Send a profile URL or @handle and the Instagram Tagged Posts API returns the posts other people tagged that account in — the same content you see in the profile's \"Tagged\" tab — as clean, structured JSON. Each post includes who published it, the caption, image or video URLs, like and comment counts, post type, and publish date. It's the easiest way to see UGC and brand mentions: track who is tagging a brand, collect fan or customer content, or monitor collaborations. No Instagram login, no OAuth, and no proxies or infrastructure to maintain on your side — results are cached for 24 hours, so repeat lookups are instant and free." },
  { slug: "instagram-reels-by-audio-id", name: "Instagram Reels By Audio ID API", shortName: "Reels By Audio ID", category: "list", method: "GET", path: "/v1/instagram/reels-by-audio-id", credits: 28, creditsPerResult: 1.4, tagline: "Give it an Instagram sound and get back every Reel that uses it — each with its video, caption, creator, and view / like / comment counts.", longDescription: "On Instagram every Reel is built on an audio track, and each track has its own page listing the Reels that use it. This API takes that sound — either the numeric audio ID (the musicId you see on a Reel) or a full audio-page URL like https://www.instagram.com/reels/audio/AUDIO_ID/ — and returns those Reels as clean JSON. For each Reel you get a direct video URL, caption, the creator's profile, play / like / comment counts, duration, and publish date. Use it to see how far a trending sound has spread, find every creator who used your music, or measure a branded-audio campaign. No Instagram login, no OAuth, and no infrastructure to maintain — results are cached for 24 hours, so repeat lookups are instant and free.", delivers: ["Every public Reel made with that audio track", "Direct MP4 video URL and thumbnail for each Reel", "Caption, duration, publish date, and the sound's audio ID", "Creator handle plus play / like / comment counts"] },
  { slug: "instagram-hashtag-search", name: "Instagram Hashtag Search API", shortName: "Hashtag Search", category: "search", method: "GET", path: "/v1/instagram/hashtag-search", credits: 12, creditsPerResult: 0.6, tagline: "Find public Instagram posts tagged with a hashtag — each result comes with its media, caption, author, and like / comment counts.", longDescription: "Pass a hashtag without the # (e.g. travel or foodie) and the Instagram Hashtag Search API returns the public posts and Reels that use that tag as clean JSON — the same grid you'd see on the hashtag's page in the app. Each result includes the post URL, media type (image, video, or carousel), caption, the author's profile, like / comment / view counts, a thumbnail, and the full list of hashtags and @mentions in the post. Use it to track a campaign or branded hashtag, discover creators in a niche, build a themed content feed, or watch a trend grow. No Instagram login, no OAuth, and no infrastructure to maintain — results are cached for 24 hours, so repeat lookups are instant and free.", delivers: ["Public posts and Reels tagged with your hashtag", "Post URL, media type, caption, and publish date", "Author handle plus like / comment / view counts", "Every hashtag and @mention extracted from each post"] },
  { slug: "instagram-profile-search", name: "Instagram Profile Search API", shortName: "Profile Search", category: "search", method: "GET", path: "/v1/instagram/profile-search", credits: 1, tagline: "Look up an Instagram account by name or @handle and get its profile back — display name, follower count, verified badge, private flag, and avatar.", delivers: ["The public Instagram profile that matches your query", "Username, display name, and profile URL", "Follower count plus verified and private flags", "Profile picture URL"] , longDescription: "Pass an account name, @handle, or profile URL (e.g. nike, @nasa, or instagram.com/natgeo) and the Instagram Profile Search API resolves it to the matching public profile as clean JSON. It returns the account itself, not its posts: username, display name, profile URL, follower count, whether the account is verified or private, and the profile picture. Use it to turn a brand or creator name into a confirmed @handle, enrich a CRM or lead list, or feed an influencer-discovery tool. Fast and costs just 1 credit — no Instagram login or OAuth, and results are cached for 24 hours." },
  { slug: "instagram-embed", name: "Instagram Embed HTML API", shortName: "Embed HTML", category: "details", method: "GET", path: "/v1/instagram/embed", credits: 1, tagline: "Get Instagram's own self-contained embed HTML for any post, reel, or profile — ready to drop into an iframe on your site.", longDescription: "Pass an Instagram post, reel, or profile URL (or an @handle) and get back Instagram's own self-contained embed page as ready-to-use HTML — the full <html> document Instagram serves at /embed/, which you can drop straight into an <iframe srcdoc> or render server-side. The response also returns embedUrl, so you can point an <iframe src> at it directly instead. Posts and reels come back as a rich media card (with caption); profiles come back as a profile card that links to the account. No login or OAuth needed — it's fast, costs just 1 credit, and results are cached for 24 hours. If Instagram's embed page is ever unavailable, the response falls back to the classic blockquote + embed.js snippet.", delivers: ["Instagram's full self-contained embed HTML document", "embedUrl you can load directly in an <iframe src>", "Canonical Instagram permalink for the post/reel/profile", "Type flag (post/reel/profile) plus shortcode or username"] },
  { slug: "instagram-basic-profile", name: "Instagram Basic Profile API", shortName: "Basic Profile", category: "channel", method: "GET", path: "/v1/instagram/basic-profile", credits: 1 , tagline: "Look up a full public Instagram profile by user ID (or @handle) — bio, follower counts, verification, and profile pictures.", longDescription: "Pass an Instagram numeric user ID (e.g. 314216) and get that account's public profile as clean JSON: username, full name, biography, follower / following / media counts, verification and privacy flags, business status, and profile pictures. A profile URL, @handle, or username is also accepted and resolved automatically. Fast, costs just 1 credit, and needs no Instagram login or OAuth. Empty fields are omitted. Results are cached for 24 hours.", delivers: ["Username, full name, and biography", "Follower, following, and media counts", "Verification, privacy, and business flags", "Standard and HD profile picture URLs, plus stable user IDs"] },
];

const FACEBOOK: Spec[] = [
  { slug: "facebook-details", name: "Facebook Details API", shortName: "Details", category: "details", method: "GET", path: "/v1/facebook/details", credits: 1 , tagline: "Get a Facebook post or video — caption, engagement, author, and media fields as structured JSON." },
  { slug: "facebook-transcript", name: "Facebook Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/facebook/transcript", credits: 2 },
  { slug: "facebook-summarizer", name: "Facebook Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/facebook/summarize", credits: 4 },
  { slug: "facebook-comments", name: "Facebook Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/facebook/comments", credits: 30, creditsPerResult: 0.6 },
  { slug: "facebook-page-details", name: "Facebook Page Details API", shortName: "Page Details", category: "channel", method: "GET", path: "/v1/facebook/page-details", credits: 1 },
  { slug: "facebook-profile-posts", name: "Facebook Profile Posts API", shortName: "Profile Posts", category: "list", method: "GET", path: "/v1/facebook/profile-posts", credits: 12, creditsPerResult: 0.6 },
  { slug: "facebook-profile-reels", name: "Facebook Profile Reels API", shortName: "Profile Reels", category: "list", method: "GET", path: "/v1/facebook/profile-reels", credits: 36, creditsPerResult: 1.8 },
  { slug: "facebook-group-posts", name: "Facebook Group Posts API", shortName: "Group Posts", category: "list", method: "GET", path: "/v1/facebook/group-posts", credits: 12, creditsPerResult: 0.6 },
  { slug: "facebook-comment-replies", name: "Facebook Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/facebook/comment-replies", credits: 30, creditsPerResult: 0.6 },
  { slug: "facebook-marketplace-search", name: "Facebook Marketplace Search API", shortName: "Marketplace Search", category: "search", method: "GET", path: "/v1/facebook/marketplace-search", credits: 28, creditsPerResult: 1.4 },
  { slug: "facebook-marketplace-location-search", name: "Facebook Marketplace Location Search API", shortName: "Marketplace Locations", category: "search", method: "GET", path: "/v1/facebook/marketplace-location-search", credits: 17 , tagline: "Look up Facebook Marketplace location IDs for a city or place — IDs you can pass into Marketplace Search.", longDescription: "Pass a city or place name and get matching Marketplace location IDs as structured JSON. Use those IDs with Marketplace Search to filter listings by area." },
  { slug: "facebook-event-search", name: "Facebook Event Search API", shortName: "Event Search", category: "search", method: "GET", path: "/v1/facebook/event-search", credits: 40, creditsPerResult: 2 },
  { slug: "facebook-event-details", name: "Facebook Event Details API", shortName: "Event Details", category: "details", method: "GET", path: "/v1/facebook/event-details", credits: 2 , tagline: "Get a Facebook event — title, time, place, host, and attendance signals as structured JSON.", longDescription: "Paste a Facebook event URL and get the event details as clean JSON: title, description, start/end time, location, host page, and interest or going counts when available. Flat 2 credits per call." },
  { slug: "facebook-profile-photos", name: "Facebook Profile Photos API", shortName: "Profile Photos", category: "list", method: "GET", path: "/v1/facebook/profile-photos", credits: 12, creditsPerResult: 0.6 },
  { slug: "facebook-profile-events", name: "Facebook Profile Events API", shortName: "Profile Events", category: "list", method: "GET", path: "/v1/facebook/profile-events", credits: 40, creditsPerResult: 2 },
  { slug: "facebook-marketplace-item", name: "Facebook Marketplace Item API", shortName: "Marketplace Item", category: "details", method: "GET", path: "/v1/facebook/marketplace-item", credits: 1 , tagline: "Get a Facebook Marketplace listing — title, price, photos, seller, and location as structured JSON.", longDescription: "Paste a Facebook Marketplace item URL and get the listing as clean JSON: title, price, description, photos, seller, and location when available. Flat 1 credit per call." },
];

const TWITTER: Spec[] = [
  { slug: "twitter-tweet-details", name: "Twitter/X Tweet Details API", shortName: "Tweet Details", category: "details", method: "GET", path: "/v1/twitter/tweet-details", credits: 1 , tagline: "Get a tweet — text, author, likes, reposts, replies, and media as structured JSON.", longDescription: "Paste a tweet URL and get the tweet as clean JSON: text, author profile, like / repost / reply counts, media attachments when present, and publish time. Flat 1 credit per call." },
  { slug: "twitter-transcript", name: "Twitter/X Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/twitter/transcript", credits: 7 },
  { slug: "twitter-profile", name: "Twitter/X Profile API", shortName: "Profile", category: "channel", method: "GET", path: "/v1/twitter/profile", credits: 1 },
  { slug: "twitter-user-tweets", name: "Twitter/X User Tweets API", shortName: "User Tweets", category: "list", method: "GET", path: "/v1/twitter/user-tweets", credits: 14, creditsPerResult: 0.7 },
  { slug: "twitter-search", name: "Twitter/X Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/twitter/search", credits: 14, creditsPerResult: 0.7 },
  { slug: "twitter-community", name: "Twitter/X Community API", shortName: "Community", category: "details", method: "GET", path: "/v1/twitter/community", credits: 1 , tagline: "Get a Twitter/X Community — name, description, member count, and rules as structured JSON.", longDescription: "Paste a Twitter/X Community URL and get the community metadata as clean JSON: name, description, member count, and related fields when available. Pair with Community Tweets to list posts inside it." },
  { slug: "twitter-community-tweets", name: "Twitter/X Community Tweets API", shortName: "Community Tweets", category: "list", method: "GET", path: "/v1/twitter/community-tweets", credits: 18, creditsPerResult: 0.7 },
];

const REDDIT: Spec[] = [
  { slug: "reddit-subreddit-posts", name: "Reddit Subreddit Posts API", shortName: "Subreddit Posts", category: "list", method: "GET", path: "/v1/reddit/subreddit-posts", credits: 10, creditsPerResult: 0.4 },
  { slug: "reddit-post-details", name: "Reddit Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/reddit/post-details", credits: 1 , tagline: "Get a Reddit post — title, body, score, comments count, subreddit, and author as structured JSON.", longDescription: "Paste a Reddit post URL and get the post as clean JSON: title, body text, score, comment count, subreddit, author, and flair when available. Flat 1 credit per call." },
  { slug: "reddit-post-comments", name: "Reddit Post Comments API", shortName: "Post Comments", category: "comments", method: "GET", path: "/v1/reddit/post-comments", credits: 20, creditsPerResult: 0.4 },
  { slug: "reddit-post-transcript", name: "Reddit Post Transcript API", shortName: "Post Transcript", category: "transcript", method: "GET", path: "/v1/reddit/post-transcript", credits: 20, creditsPerResult: 0.4 , tagline: "Get a Reddit post's discussion as readable text — title, body, and comments in one transcript-style payload.", longDescription: "Paste a Reddit post URL and get the discussion as structured text: the post title and body plus comments flattened into a transcript-style response. This is discussion text, not speech-to-text from a video. Billed per result." },
  { slug: "reddit-search", name: "Reddit Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/reddit/search", credits: 10, creditsPerResult: 0.4 },
  { slug: "reddit-subreddit-details", name: "Reddit Subreddit Details API", shortName: "Subreddit Details", category: "details", method: "GET", path: "/v1/reddit/subreddit-details", credits: 1 , tagline: "Get a subreddit — title, description, subscribers, and community rules signals as structured JSON." },
  { slug: "reddit-subreddit-search", name: "Reddit Subreddit Search API", shortName: "Subreddit Search", category: "search", method: "GET", path: "/v1/reddit/subreddit-search", credits: 10, creditsPerResult: 0.4 },
];

const THREADS: Spec[] = [
  { slug: "threads-profile", name: "Threads Profile API", shortName: "Profile", category: "channel", method: "GET", path: "/v1/threads/profile", credits: 1 },
  { slug: "threads-user-posts", name: "Threads User Posts API", shortName: "User Posts", category: "list", method: "GET", path: "/v1/threads/user-posts", credits: 14, creditsPerResult: 0.7 },
  { slug: "threads-post-details", name: "Threads Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/threads/post-details", credits: 1 , tagline: "Get a Threads post — text, author, likes, replies, and media as structured JSON." },
  { slug: "threads-search", name: "Threads Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/threads/search", credits: 18, creditsPerResult: 0.7 },
  { slug: "threads-search-users", name: "Threads Search Users API", shortName: "Search Users", category: "search", method: "GET", path: "/v1/threads/search-users", credits: 14, creditsPerResult: 0.7 },
];

const BLUESKY: Spec[] = [
  { slug: "bluesky-profile", name: "Bluesky Profile API", shortName: "Profile", category: "channel", method: "GET", path: "/v1/bluesky/profile", credits: 1 },
  { slug: "bluesky-user-posts", name: "Bluesky User Posts API", shortName: "User Posts", category: "list", method: "GET", path: "/v1/bluesky/user-posts", credits: 3, creditsPerResult: 0.1 },
  { slug: "bluesky-post-details", name: "Bluesky Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/bluesky/post-details", credits: 1 , tagline: "Get a Bluesky post — text, author, likes, reposts, and replies as structured JSON." },
];

const PINTEREST: Spec[] = [
  { slug: "pinterest-pin-details", name: "Pinterest Pin Details API", shortName: "Pin Details", category: "details", method: "GET", path: "/v1/pinterest/pin-details", credits: 1 , tagline: "Get a Pinterest pin — title, description, image, board, and save/engagement fields as structured JSON." },
  { slug: "pinterest-user-pins", name: "Pinterest User Pins API", shortName: "User Pins", category: "list", method: "GET", path: "/v1/pinterest/user-pins", credits: 13, creditsPerResult: 0.5 },
  { slug: "pinterest-search", name: "Pinterest Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/pinterest/search", credits: 13, creditsPerResult: 0.5 },
  { slug: "pinterest-board", name: "Pinterest Board API", shortName: "Board", category: "list", method: "GET", path: "/v1/pinterest/board", credits: 13, creditsPerResult: 0.5 },
  { slug: "pinterest-user-boards", name: "Pinterest User Boards API", shortName: "User Boards", category: "list", method: "GET", path: "/v1/pinterest/user-boards", credits: 13, creditsPerResult: 0.5 },
];

const LINKEDIN: Spec[] = [
  { slug: "linkedin-profile", name: "LinkedIn Profile API", shortName: "Profile", category: "channel", method: "GET", path: "/v1/linkedin/profile", credits: 2 },
  { slug: "linkedin-company", name: "LinkedIn Company API", shortName: "Company", category: "channel", method: "GET", path: "/v1/linkedin/company", credits: 2 },
  { slug: "linkedin-post-details", name: "LinkedIn Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/linkedin/post-details", credits: 1 , tagline: "Get a LinkedIn post — text, author, reactions, and comments count as structured JSON." },
  { slug: "linkedin-post-transcript", name: "LinkedIn Post Transcript API", shortName: "Post Transcript", category: "transcript", method: "GET", path: "/v1/linkedin/post-transcript", credits: 7 },
  { slug: "linkedin-company-posts", name: "LinkedIn Company Posts API", shortName: "Company Posts", category: "list", method: "GET", path: "/v1/linkedin/company-posts", credits: 16, creditsPerResult: 0.8 },
  { slug: "linkedin-search-posts", name: "LinkedIn Search Posts API", shortName: "Search Posts", category: "search", method: "GET", path: "/v1/linkedin/search-posts", credits: 16, creditsPerResult: 0.8 },
];

const RUMBLE: Spec[] = [
  { slug: "rumble-video-details", name: "Rumble Video Details API", shortName: "Video Details", category: "details", method: "GET", path: "/v1/rumble/video-details", credits: 1 },
  { slug: "rumble-channel-videos", name: "Rumble Channel Videos API", shortName: "Channel Videos", category: "list", method: "GET", path: "/v1/rumble/channel-videos", credits: 12, creditsPerResult: 0.6 },
  { slug: "rumble-search", name: "Rumble Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/rumble/search", credits: 12, creditsPerResult: 0.6 },
  { slug: "rumble-comments", name: "Rumble Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/rumble/comments", credits: 30, creditsPerResult: 0.6 },
];

const TIKTOK_SHOP: Spec[] = [
  { slug: "tiktok-shop-search", name: "TikTok Shop Search API", shortName: "Shop Search", category: "search", method: "GET", path: "/v1/tiktok-shop/shop-search", credits: 56, creditsPerResult: 2.8 },
  { slug: "tiktok-shop-products", name: "TikTok Shop Products API", shortName: "Shop Products", category: "list", method: "GET", path: "/v1/tiktok-shop/shop-products", credits: 56, creditsPerResult: 2.8 },
  { slug: "tiktok-shop-product-details", name: "TikTok Shop Product Details API", shortName: "Product Details", category: "details", method: "GET", path: "/v1/tiktok-shop/product-details", credits: 14 , tagline: "Get a TikTok Shop product — title, price, images, seller, and sales signals as structured JSON." },
  { slug: "tiktok-shop-product-reviews", name: "TikTok Shop Product Reviews API", shortName: "Product Reviews", category: "comments", method: "GET", path: "/v1/tiktok-shop/product-reviews", credits: 45, creditsPerResult: 2.25 },
  { slug: "tiktok-shop-user-showcase", name: "TikTok Shop User Showcase API", shortName: "User Showcase", category: "list", method: "GET", path: "/v1/tiktok-shop/user-showcase", credits: 45, creditsPerResult: 2.25 },
];

const GITHUB: Spec[] = [
  { slug: "github-user", name: "GitHub User API", shortName: "User", category: "channel", method: "GET", path: "/v1/github/user", credits: 3 },
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
  { slug: "twitch-profile", name: "Twitch Profile API", shortName: "Profile", category: "channel", method: "GET", path: "/v1/twitch/profile", credits: 1 },
  { slug: "twitch-user-videos", name: "Twitch User Videos API", shortName: "User Videos", category: "list", method: "GET", path: "/v1/twitch/user-videos", credits: 34, creditsPerResult: 1.7 },
  { slug: "twitch-user-schedule", name: "Twitch User Schedule API", shortName: "User Schedule", category: "list", method: "GET", path: "/v1/twitch/user-schedule", credits: 1 },
  { slug: "twitch-clip", name: "Twitch Clip API", shortName: "Clip", category: "details", method: "GET", path: "/v1/twitch/clip", credits: 1 , tagline: "Get a Twitch clip — title, broadcaster, views, duration, and thumbnail as structured JSON." },
];

const SPOTIFY: Spec[] = [
  { slug: "spotify-artist", name: "Spotify Artist API", shortName: "Artist", category: "channel", method: "GET", path: "/v1/spotify/artist", credits: 6 },
  { slug: "spotify-track", name: "Spotify Track API", shortName: "Track", category: "details", method: "GET", path: "/v1/spotify/track", credits: 6 , tagline: "Get a Spotify track — title, artists, album, duration, and popularity as structured JSON." },
  { slug: "spotify-album", name: "Spotify Album API", shortName: "Album", category: "details", method: "GET", path: "/v1/spotify/album", credits: 6 , tagline: "Get a Spotify album — title, artists, tracks, release date, and cover art as structured JSON." },
  { slug: "spotify-search", name: "Spotify Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/spotify/search", credits: 23, creditsPerResult: 1.15 },
  { slug: "spotify-podcast", name: "Spotify Podcast API", shortName: "Podcast", category: "details", method: "GET", path: "/v1/spotify/podcast", credits: 6 , tagline: "Get a Spotify podcast show — title, publisher, description, and episode counts as structured JSON." },
  { slug: "spotify-podcast-episodes", name: "Spotify Podcast Episodes API", shortName: "Podcast Episodes", category: "list", method: "GET", path: "/v1/spotify/podcast-episodes", credits: 23, creditsPerResult: 1.15 },
];

const SOUNDCLOUD: Spec[] = [
  { slug: "soundcloud-artist", name: "SoundCloud Artist API", shortName: "Artist", category: "channel", method: "GET", path: "/v1/soundcloud/artist", credits: 1 },
  { slug: "soundcloud-artist-tracks", name: "SoundCloud Artist Tracks API", shortName: "Artist Tracks", category: "list", method: "GET", path: "/v1/soundcloud/artist-tracks", credits: 28, creditsPerResult: 1.4 },
  { slug: "soundcloud-track", name: "SoundCloud Track API", shortName: "Track", category: "details", method: "GET", path: "/v1/soundcloud/track", credits: 1 , tagline: "Get a SoundCloud track — title, artist, plays, likes, duration, and artwork as structured JSON." },
];

const LINKTREE: Spec[] = [
  { slug: "linktree-page", name: "Linktree Page API", shortName: "Page", category: "details", method: "GET", path: "/v1/linktree/page", credits: 4 , tagline: "Extract the links from a public Linktree page — title, URL, and order for each link.", longDescription: "Paste a Linktree URL and get the page's public links as structured JSON: each link's title, destination URL, and position. Ideal for lead enrichment and competitor link-in-bio research." },
];

const SNAPCHAT: Spec[] = [
  { slug: "snapchat-user-profile", name: "Snapchat User Profile API", shortName: "User Profile", category: "channel", method: "GET", path: "/v1/snapchat/user-profile", credits: 11 },
];

const TRUTH_SOCIAL: Spec[] = [
  { slug: "truth-social-profile", name: "Truth Social Profile API", shortName: "Profile", category: "channel", method: "GET", path: "/v1/truth-social/profile", credits: 5 },
  { slug: "truth-social-user-posts", name: "Truth Social User Posts API", shortName: "User Posts", category: "list", method: "GET", path: "/v1/truth-social/user-posts", credits: 17, creditsPerResult: 0.85 },
  { slug: "truth-social-post", name: "Truth Social Post API", shortName: "Post", category: "details", method: "GET", path: "/v1/truth-social/post", credits: 5 , tagline: "Get a Truth Social post — text, author, and engagement fields as structured JSON." },
];

const KICK: Spec[] = [
  { slug: "kick-clip", name: "Kick Clip API", shortName: "Clip", category: "details", method: "GET", path: "/v1/kick/clip", credits: 34 , tagline: "Get a Kick clip — title, channel, views, duration, and thumbnail as structured JSON." },
];

const AMAZON_SHOP: Spec[] = [
  { slug: "amazon-shop-page", name: "Amazon Shop Page API", shortName: "Shop Page", category: "list", method: "GET", path: "/v1/amazon-shop/page", credits: 89, creditsPerResult: 4.45 , tagline: "List products from an Amazon Shop / influencer storefront page — title, price, and product URL for each item." },
];

const ACCOUNT: Spec[] = [
  { slug: "account-balance", name: "Credit Balance API", shortName: "Credit Balance", category: "details", method: "GET", path: "/v1/account/balance", credits: 0 , tagline: "Check how many Captapi credits remain on your API key.", longDescription: "Call the Credit Balance API with your Captapi key and get the remaining credit balance as JSON. Free — does not consume credits." },
  { slug: "account-request-history", name: "Request History API", shortName: "Request History", category: "list", method: "GET", path: "/v1/account/request-history", credits: 0 , tagline: "See recent API requests made with your Captapi key — path, status, and credits used.", longDescription: "List recent requests for your Captapi account as structured JSON: endpoint path, status, credits charged, and timestamps. Free — does not consume credits." },
  { slug: "account-daily-usage", name: "Daily Usage API", shortName: "Daily Usage", category: "list", method: "GET", path: "/v1/account/daily-usage", credits: 0 , tagline: "See day-by-day credit usage for your Captapi account.", longDescription: "Get daily credit usage for your Captapi key as structured JSON — useful for spend monitoring and budgeting. Free — does not consume credits." },
  { slug: "account-most-used-routes", name: "Most Used Routes API", shortName: "Most Used Routes", category: "list", method: "GET", path: "/v1/account/most-used-routes", credits: 0 , tagline: "See which Captapi endpoints your key calls most often.", longDescription: "Get a ranked list of the routes your Captapi key uses most, with call counts over a chosen window. Free — does not consume credits." },
];

const KWAI: Spec[] = [
  { slug: "kwai-profile", name: "Kwai Profile API", shortName: "Profile", category: "channel", method: "GET", path: "/v1/kwai/profile", credits: 17 },
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

const AD_LIBRARY: Spec[] = [
  { slug: "facebook-ad-library-search", name: "Facebook Ad Library Search API", shortName: "Facebook Search", category: "search", method: "GET", path: "/v1/ad-library/facebook/search", credits: 70, creditsPerResult: 3.5 },
  { slug: "facebook-ad-library-company-ads", name: "Facebook Company Ads API", shortName: "Facebook Company Ads", category: "list", method: "GET", path: "/v1/ad-library/facebook/company-ads", credits: 70, creditsPerResult: 3.5 },
  { slug: "facebook-ad-library-search-companies", name: "Facebook Ad Library Search Companies API", shortName: "Facebook Search Companies", category: "search", method: "GET", path: "/v1/ad-library/facebook/search-companies", credits: 70, creditsPerResult: 3.5 },
  { slug: "facebook-ad-library-ad-details", name: "Facebook Ad Details API", shortName: "Facebook Ad Details", category: "details", method: "GET", path: "/v1/ad-library/facebook/ad-details", credits: 17 , tagline: "Get a Meta Ad Library ad — creative text, media, advertiser, and delivery fields as structured JSON." },
  { slug: "facebook-ad-library-ad-transcript", name: "Facebook Ad Transcript API", shortName: "Facebook Ad Transcript", category: "transcript", method: "GET", path: "/v1/ad-library/facebook/ad-transcript", credits: 17 },
  { slug: "tiktok-ad-library-search", name: "TikTok Ad Library Search API", shortName: "TikTok Search", category: "search", method: "GET", path: "/v1/ad-library/tiktok/search", credits: 70, creditsPerResult: 3.5 },
  { slug: "tiktok-ad-library-ad-details", name: "TikTok Ad Details API", shortName: "TikTok Ad Details", category: "details", method: "GET", path: "/v1/ad-library/tiktok/ad-details", credits: 17 , tagline: "Get a TikTok Ad Library ad — creative, advertiser, and delivery fields as structured JSON." },
  { slug: "google-ad-library-company-ads", name: "Google Company Ads API", shortName: "Google Company Ads", category: "list", method: "GET", path: "/v1/ad-library/google/company-ads", credits: 67, creditsPerResult: 3.35 },
  { slug: "google-ad-library-ad-details", name: "Google Ad Details API", shortName: "Google Ad Details", category: "details", method: "GET", path: "/v1/ad-library/google/ad-details", credits: 17 , tagline: "Get a Google Ads Transparency ad — creative, advertiser, and delivery fields as structured JSON." },
  { slug: "google-ad-library-advertiser-search", name: "Google Advertiser Search API", shortName: "Google Advertiser Search", category: "search", method: "GET", path: "/v1/ad-library/google/advertiser-search", credits: 45, creditsPerResult: 4.5 },
  { slug: "linkedin-ad-library-search-ads", name: "LinkedIn Ad Library Search API", shortName: "LinkedIn Search Ads", category: "search", method: "GET", path: "/v1/ad-library/linkedin/search-ads", credits: 70, creditsPerResult: 3.5 },
  { slug: "linkedin-ad-library-ad-details", name: "LinkedIn Ad Details API", shortName: "LinkedIn Ad Details", category: "details", method: "GET", path: "/v1/ad-library/linkedin/ad-details", credits: 17 , tagline: "Get a LinkedIn Ad Library ad — creative, advertiser, and delivery fields as structured JSON." },
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
    icon: "music",
    color: "text-pink-500",
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
    blurb: "Pull details, transcripts, summaries, and comments from public Facebook videos and pages.",
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
    icon: "shoppingBag",
    color: "text-pink-500",
    exampleUrl: "https://shop.tiktok.com/us/pdp/example-product/1234567890",
    endpoints: TIKTOK_SHOP.map((s) => ({ ...s, platform: "tiktok_shop" as const })),
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
    blurb: "Extract Spotify artist, track, album, podcast, episode, and search metadata.",
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
    blurb: "Extract public Linktree profile links, socials, and profile metadata.",
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
    blurb: "Pull public Truth Social profiles, user posts, and post metadata for monitoring and research.",
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
    id: "amazon_shop",
    name: "Amazon Shop",
    blurb: "Fetch Amazon seller storefront metadata and product listings for commerce research.",
    icon: "shoppingBag",
    color: "text-amber-500",
    exampleUrl: "https://www.amazon.com/s?me=ATVPDKIKX0DER",
    endpoints: AMAZON_SHOP.map((s) => ({ ...s, platform: "amazon_shop" as const })),
  },
  {
    id: "account",
    name: "Account",
    blurb: "Check credit balance, request history, daily usage, and most used API routes.",
    icon: "search",
    color: "text-emerald-600",
    exampleUrl: "https://captapi.com/dashboard",
    endpoints: ACCOUNT.map((s) => ({ ...s, platform: "account" as const })),
  },
  {
    id: "kwai",
    name: "Kwai",
    blurb: "Extract Kwai/Kuaishou profile details, user posts, and post metadata.",
    icon: "video",
    color: "text-orange-500",
    exampleUrl: "https://www.kwai.com/@easycashindonesia",
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
    exampleUrl: "https://lnk.bio/example",
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
  {
    id: "ad_library",
    name: "Ad Library",
    blurb: "Search public Meta, TikTok, Google, and LinkedIn ad libraries for competitor creative intelligence.",
    icon: "megaphone",
    color: "text-amber-600",
    exampleUrl: "https://adstransparency.google.com/",
    endpoints: AD_LIBRARY.map((s) => ({ ...s, platform: "ad_library" as const })),
  },
];

export const ALL_ENDPOINTS: ApiEndpoint[] = PLATFORM_GROUPS.flatMap(
  (g) => g.endpoints,
);

/** Total number of REST endpoints in the public catalog. */
export const ENDPOINT_COUNT = ALL_ENDPOINTS.length;

/**
 * Number of public data platforms. Excludes the internal "Account" group,
 * which exposes usage/billing routes rather than a social platform.
 */
export const PLATFORM_COUNT = PLATFORM_GROUPS.filter(
  (g) => g.id !== "account",
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
 * dropdown. Excludes the internal "Account" group.
 */
export const PLATFORM_PAGES: PlatformGroup[] = PLATFORM_GROUPS.filter(
  (g) => g.id !== "account",
);

/** Resolve a platform landing page from its URL slug (e.g. "truth-social-api"). */
export function getPlatformBySlug(slug: string): PlatformGroup | undefined {
  return PLATFORM_PAGES.find((g) => platformSlug(g.id) === slug);
}

export function getEndpoint(slug: string): ApiEndpoint | undefined {
  return ALL_ENDPOINTS.find((e) => e.slug === slug);
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
    why: "Returns products promoted in a creator's TikTok Shop showcase.",
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
    prefer: "Use location search first, then marketplace search with the selected location.",
    endpointSlug: "facebook-marketplace-location-search",
    why: "Finds location candidates for Facebook Marketplace searches.",
  },
  {
    intent: "Kwai/Kuaishou creator monitoring",
    whenUserSays: [
      "Kwai profilini çek",
      "Kuaishou user posts",
      "Analyze this Kwai creator",
    ],
    prefer: "Use Kwai endpoints for Kwai/Kuaishou URLs or numeric user IDs.",
    endpointSlug: "kwai-user-posts",
    why: "Lists Kwai/Kuaishou user posts with normalized metadata.",
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
  if (ep.platform === "account") return "Captapi account";
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
 * pages (e.g. "get a YouTube transcript", "download a TikTok video").
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
        return `Pull reply threads under a ${platform} comment — author, text, likes, and time.`;
      return `Pull ${platform} comments at scale with author, text, likes, and reply threads.`;
    case "channel":
      if (resource === "page" || resource.includes("page"))
        return `Fetch a public ${platform} page — links, bio, and profile fields as structured JSON.`;
      if (resource.includes("company"))
        return `Fetch ${platform} company page data — name, industry, size, and follower stats.`;
      return `Fetch ${platform} ${resource} — display name, bio, counts, and verification as structured JSON.`;
    case "search":
      if (resource === "search")
        return `Search ${platform} programmatically and get structured, ranked results.`;
      return `Run a ${platform} ${resource} and get structured, ranked results as clean JSON.`;
    case "list":
      return `List ${platform} ${resource} with full metadata for each item.`;
  }
}

export function longDescription(ep: ApiEndpoint): string {
  if (ep.longDescription) return ep.longDescription;
  const platform = PLATFORM_LABEL[ep.platform];
  if (ep.platform === "account") {
    return `The ${ep.name} returns live data for your Captapi API key with a single REST call to ${ep.path}. Account endpoints do not charge credits. Use them to monitor balance, usage, and which routes you call most.`;
  }
  return `The ${ep.name} lets you ${ACTION[ep.category]} for ${platform} ${resourceLabel(ep)} with a single REST call. No OAuth, no infrastructure to maintain, and no platform SDKs — send the request, get clean structured JSON back. Results are cached for 24 hours, so repeat lookups are instant and free.`;
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
        "Like counts and reply threads when available",
        "Pagination via the limit parameter",
        "Timestamps for trend and sentiment analysis",
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
const lang = (): ApiParam => ({ name: "language", type: "string", required: false, description: 'Preferred caption language as an ISO code, e.g. "en". Defaults to auto-detect.' });
const langOut = (): ApiParam => ({ name: "language", type: "string", required: false, description: 'ISO code, e.g. "tr": pins the speech language and sets the summary output language. Defaults to auto-detect + English summary.' });
const cid = (): ApiParam => ({ name: "comment_id", type: "string", required: true, description: "ID of the parent comment to fetch replies for (from the comments endpoint)." });
const fastRss = (): ApiParam => ({ name: "fast", type: "boolean", required: false, description: "Set true to use YouTube RSS for faster results with less detailed metadata. Leave false when viewCount/duration quality matters." });
const cacheP = (): ApiParam => ({ name: "cache", type: "boolean", required: false, description: "Set true to serve from the 24h response cache. Default false — always fetch fresh data." });

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
const AMAZON_SHOP_URL = "Amazon seller storefront URL, seller profile URL, or seller ID.";
const KWAI_PROFILE = "Kwai profile URL or @handle, e.g. https://www.kwai.com/@easycashindonesia.";
const KWAI_POST = "Kwai video URL, e.g. https://www.kwai.com/@handle/video/5238962376325675745.";
const CURSOR = { name: "cursor", type: "string" as const, required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." };
const KOMI_PAGE = "Komi page URL or username.";
const PILLAR_PAGE = "Pillar page URL or username.";
const LINKBIO_PAGE = "Linkbio page URL or username.";
const LINKME_PROFILE = "Linkme profile URL or username.";

const ENDPOINT_PARAMS: Record<string, ApiParam[]> = {
  // YouTube
  "youtube-transcript": [up(YT_VIDEO), lang(), cacheP()],
  "youtube-summarizer": [up(YT_VIDEO), lang(), cacheP()],
  "youtube-video-details": [up(YT_VIDEO)],
  "youtube-comments": [up(YT_VIDEO), lp(50, 500), CURSOR],
  "youtube-channel-details": [up(YT_CHANNEL)],
  "youtube-search": [qp(), lp(20, 200)],
  "youtube-channel-videos": [up(YT_CHANNEL), lp(20, 200), fastRss()],
  "youtube-playlist-videos": [up("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."), lp(50, 500), fastRss()],
  "youtube-playlist": [up("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."), lp(50, 500), fastRss()],
  "youtube-shorts-transcript": [up(YT_SHORTS), lang(), cacheP()],
  "youtube-shorts-summarizer": [up(YT_SHORTS), lang(), cacheP()],
  "youtube-shorts-stats": [up(YT_SHORTS)],
  "youtube-shorts-comments": [up(YT_SHORTS), lp(50, 500)],
  "youtube-channel-shorts": [up(YT_CHANNEL), lp(20, 200)],
  "youtube-trending-shorts": [{ name: "q", type: "string", required: false, description: "Seed keyword for trending Shorts. Defaults to trending." }, lp(20, 100)],
  "youtube-channel-streams": [up(YT_CHANNEL), lp(20, 200)],
  "youtube-hashtag-search": [qp("Hashtag with or without the # (min 2 characters)."), lp(20, 200)],
  "youtube-comment-replies": [up(YT_VIDEO), cid(), lp(50, 500)],
  "youtube-channel-playlists": [up(YT_CHANNEL), lp(20, 200)],
  "youtube-community-posts": [up(YT_CHANNEL), lp(20, 200)],
  "youtube-community-post-details": [up("YouTube community post URL.")],
  "youtube-video-sponsors": [up(YT_VIDEO)],
  // TikTok
  "tiktok-transcript": [up(TT_VIDEO), lang(), cacheP()],
  "tiktok-summarizer": [up(TT_VIDEO), langOut(), cacheP()],
  "tiktok-video-details": [up(TT_VIDEO)],
  "tiktok-comments": [up(TT_VIDEO), lp(50, 500), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response (a numeric offset, e.g. 50). A null nextCursor means the end of the comments." }],
  "tiktok-channel-details": [up(TT_PROFILE)],
  "tiktok-profile-region": [up(TT_PROFILE)],
  "tiktok-audience-demographics": [up(TT_PROFILE)],
  "tiktok-search-suggestions": [qp("Seed keyword to expand into autocomplete suggestions, e.g. skincare."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code that localizes the suggestions to a market, e.g. US, GB, DE. Default US." }, { name: "language", type: "string", required: false, description: "Interface language for the suggestions, e.g. en-US or de-DE. Default en-US." }, { name: "limit", type: "integer", required: false, description: "Upper bound on how many suggestions to return (1-100, default 20). TikTok only surfaces a limited number of real autocomplete suggestions per keyword, so you'll often get fewer than the limit. Billed per result returned." }],
  "tiktok-channel-posts": [up(TT_PROFILE), { name: "limit", type: "integer", required: false, description: "How many of the creator's latest videos to return on this page (default 20, max 200). Newest first. Flat 2 credits per call." }, { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response (TikTok's max_cursor timestamp, e.g. 1783614676000). A null nextCursor means the end of the list." }],
  "tiktok-comment-replies": [
    up(TT_VIDEO),
    cid(),
    lp(50, 500),
    { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value from the previous response." },
  ],
  "tiktok-user-followers": [up(TT_PROFILE), lp(50, 500)],
  "tiktok-user-followings": [up(TT_PROFILE), lp(50, 500)],
  "tiktok-music-posts": [up(TT_MUSIC), lp(20, 200)],
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
  "instagram-reels-search": [qp("Hashtag (without #) or keyword (min 2 characters)."), lp(20, 200)],
  "instagram-trending-reels": [{ name: "country", type: "string", required: false, description: "Country for Explore localization — full name or ISO code (e.g. 'United States', 'US', 'Turkey', 'TR'). Default United States. 35 countries supported." }, lp(20, 200)],
  "instagram-tagged-posts": [up(IG_PROFILE), lp(20, 200)],
  "instagram-reels-by-audio-id": [{ name: "audio_id", type: "string", required: true, description: "Instagram audio/music ID or full audio URL." }, lp(20, 200)],
  "instagram-hashtag-search": [qp("Hashtag without the # (min 2 characters)."), lp(20, 200)],
  "instagram-profile-search": [qp("Account name, @handle, or profile URL to look up (min 2 characters).")],
  "instagram-embed": [up("Instagram post, reel, or profile URL (or @handle), e.g. https://instagram.com/reel/ID/ or https://instagram.com/username/.")],
  "instagram-basic-profile": [{ name: "userId", type: "string", required: true, description: "Instagram numeric user ID (e.g. 314216). A profile URL, @handle, or username is also accepted and resolved automatically." }],
  // Facebook
  "facebook-details": [up(FB_VIDEO)],
  "facebook-transcript": [up(FB_VIDEO), cacheP()],
  "facebook-summarizer": [up(FB_VIDEO), cacheP()],
  "facebook-comments": [up(FB_VIDEO), lp(50, 500)],
  "facebook-page-details": [up("Facebook page URL, @handle, or page name, e.g. https://facebook.com/PageName.")],
  "facebook-profile-posts": [up("Facebook profile/page URL, @handle, or page name."), lp(20, 200)],
  "facebook-profile-reels": [up("Facebook profile/page URL, @handle, or page name."), lp(20, 200)],
  "facebook-group-posts": [up("Public Facebook group URL, e.g. https://facebook.com/groups/ID."), lp(20, 200)],
  "facebook-comment-replies": [up("Facebook post URL the comment belongs to."), cid(), lp(50, 500)],
  "facebook-marketplace-search": [qp("Product or keyword to search Facebook Marketplace for."), { name: "location", type: "string", required: true, description: "City or place name, e.g. 'Austin, TX'." }, lp(20, 200), { name: "details", type: "string", required: false, description: "Set true to fetch full description, photos and coordinates per listing (slower, costs more)." }],
  "facebook-marketplace-location-search": [qp("City/place search query, e.g. Austin."), lp(10, 50)],
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
  "twitter-search": [qp("Keywords or search query (min 2 characters)."), lp(20, 200)],
  "twitter-community": [up("X community URL (x.com/i/communities/ID) or community ID.")],
  "twitter-community-tweets": [up("X community URL (x.com/i/communities/ID) or community ID."), lp(25, 200)],
  // Reddit
  "reddit-subreddit-posts": [up("Subreddit URL, r/name, or bare name, e.g. r/technology."), lp(25, 200), CURSOR],
  "reddit-post-details": [up("Reddit post URL, e.g. https://reddit.com/r/sub/comments/ID/...")],
  "reddit-post-comments": [up("Reddit post URL."), lp(50, 500)],
  "reddit-post-transcript": [up("Reddit post URL."), lp(50, 200)],
  "reddit-search": [qp("Keywords or search query (min 2 characters)."), lp(25, 200), CURSOR],
  "reddit-subreddit-details": [up("Subreddit URL, r/name, or bare name, e.g. r/technology.")],
  "reddit-subreddit-search": [up("Subreddit URL, r/name, or bare name, e.g. r/technology."), qp("Keywords or search query (min 2 characters)."), lp(25, 200), CURSOR],
  // Threads
  "threads-profile": [up("Threads profile URL or @handle, e.g. https://threads.net/@username.")],
  "threads-user-posts": [up("Threads profile URL or @handle."), lp(20, 100)],
  "threads-post-details": [up("Threads post URL, e.g. https://threads.net/@user/post/CODE.")],
  "threads-search": [qp("Keyword or phrase to search Threads (min 2 characters)."), lp(25, 200)],
  "threads-search-users": [qp("Keyword to find Threads users (min 2 characters)."), lp(20, 100)],
  // Bluesky
  "bluesky-profile": [up("Bluesky profile URL, @handle, or handle, e.g. bsky.app/profile/handle.")],
  "bluesky-user-posts": [up("Bluesky profile URL, @handle, or handle."), lp(25, 100), CURSOR],
  "bluesky-post-details": [up("Bluesky post URL, e.g. https://bsky.app/profile/handle/post/RKEY.")],
  // Pinterest
  "pinterest-pin-details": [up("Pinterest pin URL, e.g. https://pinterest.com/pin/ID/.")],
  "pinterest-user-pins": [up("Pinterest profile URL or username."), lp(25, 200)],
  "pinterest-search": [qp("Keywords or search query (min 2 characters)."), lp(25, 200)],
  "pinterest-board": [up("Pinterest board URL, e.g. https://pinterest.com/username/board-name/."), lp(25, 200)],
  "pinterest-user-boards": [up("Pinterest profile URL or username."), lp(25, 200)],
  // LinkedIn
  "linkedin-profile": [up("LinkedIn profile URL, e.g. https://linkedin.com/in/slug.")],
  "linkedin-company": [up("LinkedIn company URL, e.g. https://linkedin.com/company/slug.")],
  "linkedin-post-details": [up("LinkedIn post or activity URL.")],
  "linkedin-post-transcript": [up("LinkedIn post or activity URL.")],
  // Rumble
  "rumble-video-details": [up("Rumble video URL, e.g. https://rumble.com/vXXXX-title.html.")],
  "rumble-channel-videos": [up("Rumble channel URL, e.g. https://rumble.com/c/name."), lp(20, 200)],
  "rumble-search": [qp("Keywords or search query (min 2 characters)."), lp(20, 200)],
  // Twitch
  "twitch-profile": [up(TWITCH_PROFILE)],
  "twitch-user-videos": [up(TWITCH_PROFILE), lp(20, 30)],
  "twitch-user-schedule": [up(TWITCH_PROFILE)],
  "twitch-clip": [up("Twitch clip URL, channel URL, or username.")],
  // Spotify
  "spotify-artist": [up(SPOTIFY_URL), cacheP()],
  "spotify-track": [up(SPOTIFY_URL), cacheP()],
  "spotify-album": [up(SPOTIFY_URL), cacheP()],
  "spotify-search": [qp(), { name: "type", type: "string", required: false, description: "tracks, albums, artists, podcasts, or episodes. Default tracks." }, lp(20, 50)],
  "spotify-podcast": [up(SPOTIFY_URL), lp(20, 50), cacheP()],
  "spotify-podcast-episodes": [up(SPOTIFY_URL), lp(20, 50)],
  // SoundCloud
  "soundcloud-artist": [up(SC_PROFILE)],
  "soundcloud-artist-tracks": [up(SC_PROFILE), lp(20, 100), CURSOR],
  "soundcloud-track": [up(SC_TRACK)],
  // Linktree / Snapchat
  "linktree-page": [up(LINKTREE_PROFILE)],
  "snapchat-user-profile": [up(SNAPCHAT_PROFILE)],
  // Truth Social / Kick / Amazon / Age-Gender
  "truth-social-profile": [up(TRUTH_PROFILE)],
  "truth-social-user-posts": [up(TRUTH_PROFILE), lp(20, 80), CURSOR],
  "truth-social-post": [up(TRUTH_POST)],
  "kick-clip": [up(KICK_CLIP), lp(30, 100)],
  "amazon-shop-page": [up(AMAZON_SHOP_URL), { name: "marketplace", type: "string", required: false, description: "Amazon marketplace code. Default US." }, lp(20, 200)],
  // Account
  "account-balance": [],
  "account-request-history": [lp(50, 500)],
  "account-daily-usage": [{ name: "days", type: "integer", required: false, description: "Number of days to include (default 30, max 365)." }],
  "account-most-used-routes": [{ name: "days", type: "integer", required: false, description: "Number of days to include (default 30, max 365)." }, lp(20, 100)],
  // Kwai / small creator pages
  "kwai-profile": [up(KWAI_PROFILE)],
  "kwai-user-posts": [up(KWAI_PROFILE), lp(20, 200)],
  "kwai-post": [up(KWAI_POST)],
  "komi-page": [up(KOMI_PAGE)],
  "pillar-page": [up(PILLAR_PAGE)],
  "linkbio-page": [up(LINKBIO_PAGE)],
  "linkme-profile": [up(LINKME_PROFILE)],
  // GitHub
  "github-user": [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL, e.g. vercel or https://github.com/vercel." }],
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
  "tiktok-shop-product-details": [up("TikTok Shop product URL.")],
  "tiktok-shop-product-reviews": [up("TikTok Shop product URL."), lp(20, 200)],
  "tiktok-shop-user-showcase": [{ name: "username", type: "string", required: true, description: "TikTok username, with or without @." }, lp(20, 200)],
  // Ad Library
  "facebook-ad-library-search": [qp("Keyword, brand, or advertiser to search Meta Ad Library (min 2 characters)."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }, lp(20, 200)],
  "facebook-ad-library-company-ads": [up("Facebook page URL or Meta Ad Library URL."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }, lp(20, 200)],
  "facebook-ad-library-search-companies": [qp("Company or brand name to search for (min 2 characters)."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }, lp(20, 200)],
  "facebook-ad-library-ad-details": [up("Meta Ad Library ad URL or ad ID.")],
  "facebook-ad-library-ad-transcript": [up("Meta Ad Library ad URL or ad ID.")],
  "tiktok-ad-library-search": [qp("Keyword or advertiser to search TikTok Ad Library (min 2 characters)."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default DE." }, lp(20, 200)],
  "tiktok-ad-library-ad-details": [up("TikTok Ad Library URL or ad ID."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default DE." }],
  "linkedin-ad-library-search-ads": [qp("Keyword, company, or advertiser to search LinkedIn Ad Library (min 2 characters)."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }, lp(20, 200)],
  "linkedin-ad-library-ad-details": [up("LinkedIn Ad Library URL or ad ID.")],
  "google-ad-library-company-ads": [{ name: "advertiser", type: "string", required: true, description: "Advertiser name, domain, or Google advertiser ID." }, { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }, lp(20, 200)],
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
  if (ep.platform === "account" || list.some((p) => p.name === "cache")) return list;
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
    ad_library: "Ad not found",
    spotify: "Spotify item not found",
    kick: "Kick clip not found",
    kwai: "Kwai post not found",
    truth_social: "Truth Social post not found",
    github: "Not found on GitHub",
    linkedin: "Not found on LinkedIn",
    amazon_shop: "Amazon Shop page not found",
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
  linkedin: "https://www.linkedin.com/in/williamhgates",
  rumble: "https://rumble.com/c/Bongino",
  tiktok_shop: "https://shop.tiktok.com/us/pdp/example-product/1234567890",
  github: "https://github.com/vercel/next.js",
  ad_library: "https://adstransparency.google.com/",
  twitch: "https://www.twitch.tv/shroud",
  spotify: "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02",
  soundcloud: "https://soundcloud.com/nasa",
  linktree: "https://linktr.ee/tonyhawk",
  snapchat: "https://www.snapchat.com/@nba",
  truth_social: "https://truthsocial.com/@realDonaldTrump",
  kick: "https://kick.com/xqc",
  amazon_shop: "https://www.amazon.com/s?me=ATVPDKIKX0DER",
  account: "https://captapi.com/dashboard",
  kwai: "https://www.kwai.com/@easycashindonesia",
  komi: "https://komi.io/example",
  pillar: "https://pillar.io/example",
  linkbio: "https://lnk.bio/example",
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
    case "username":
      return ep.platform === "github" ? "vercel" : "hydrojug";
    case "repo":
      return "vercel/next.js";
    case "state":
      return "open";
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
      return "314216";
    }
    case "url": {
      const d = p.description.toLowerCase();
      if (d.includes("playlist"))
        return "https://www.youtube.com/playlist?list=PLrAXtmqj7v3Y";
      if (d.includes("music") || d.includes("sound") || d.includes("audio"))
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
      if (d.includes("page")) return PROFILE_URL.facebook;
      if (d.includes("channel") || d.includes("profile") || d.includes("@handle")) {
        // Keep the Try-it default (and cURL snippet) in sync with the captured
        // example response, so the shown profile matches the sample output.
        const captured = API_EXAMPLES[ep.slug]?.url;
        if (typeof captured === "string" && /^https?:\/\//.test(captured)) return captured;
        return PROFILE_URL[ep.platform];
      }
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
  const chosen = required.length > 0 ? required : ps.slice(0, 1);
  return chosen.map((p) => ({ name: p.name, value: exampleValue(ep, p) }));
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
      code: `curl "${u}" \\\n  -H "Authorization: Bearer ${key}"`,
    },
    {
      label: "Python",
      code: `import requests

res = requests.get(
    "${base}",
    params={
${pyParams}
    },
    headers={"Authorization": "Bearer ${key}"},
)
print(res.json())`,
    },
    {
      label: "Node",
      code: `const res = await fetch(
  "${u}",
  { headers: { Authorization: "Bearer ${key}" } },
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
curl_setopt($ch, CURLOPT_HTTPHEADER, ["Authorization: Bearer ${key}"]);
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
	req.Header.Set("Authorization", "Bearer ${key}")
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
    .header("Authorization", "Bearer ${key}")
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
          : `Each successful call costs ${ep.credits} credit${ep.credits === 1 ? "" : "s"}. Responses are cached for 24 hours, and cached results cost 0 credits. Failed or empty results are never charged.`,
    },
    {
      q: `Do I need a ${platform} API key or OAuth?`,
      a:
        ep.platform === "account"
          ? `You only need your Captapi API key (Authorization: Bearer). No third-party OAuth is required.`
          : `No. A single Captapi key works across every platform Captapi supports — YouTube, TikTok, Instagram, Facebook, Twitter/X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, and Rumble. We handle proxies, rate limits, retries, and authentication for you.`,
    },
  ];

  if (ep.category === "transcript" && ep.platform !== "account") {
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
  list.push({
    q: `Is the ${ep.name} suitable for production use?`,
    a: `Yes. It is a stable REST endpoint with predictable JSON, automatic retries, and a shared 24-hour cache. Use it for analytics, monitoring, and content automation.`,
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
      a: `${name} endpoints cost between ${minCredits} and ${maxCredits} credits per call, depending on the endpoint${maxCredits !== minCredits ? " and how many results you request" : ""}. New accounts start with 100 free credits (no credit card), and repeat calls are served from a 24-hour cache for 0 credits.`,
    },
    {
      q: `Can AI agents use the ${name} API?`,
      a: `Yes. Every ${name} endpoint is exposed as a tool in the official MCP server (@captapi/mcp) for Claude, Cursor, and VS Code, and is also available through the @captapi/cli CLI, an n8n community node, a Make.com app, and an Apify Actor.`,
    },
    {
      q: `Is the ${name} API suitable for production use?`,
      a: `Yes. It is a stable REST API with predictable JSON, automatic retries, upstream fallbacks, and a shared 24-hour cache. Only successful responses consume credits — failed or empty results are never charged.`,
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
  raw: "Raw upstream payload for advanced use (fields may change).",

  // People / profiles
  username: "Account username / handle.",
  handle: "Account handle.",
  login: "Account login name.",
  // Instagram basic profile (snake_case, competitor-compatible shape)
  pk: "Instagram user primary key (same as id).",
  full_name: "Account display (full) name.",
  biography: "Profile bio text.",
  biography_with_entities: "Bio text plus parsed @mentions / #hashtags.",
  follower_count: "Follower count.",
  following_count: "Number of accounts this profile follows.",
  media_count: "Total number of posts on the profile.",
  highlight_reel_count: "Number of Story Highlight albums on the profile.",
  is_private: "Whether the account is private.",
  is_verified: "Whether the account is verified.",
  is_business: "Whether the account is a business account.",
  is_professional_account: "Whether the account is a professional (creator/business) account.",
  should_show_category: "Whether Instagram shows the account's category publicly.",
  profile_pic_url: "Standard-resolution profile picture URL.",
  hd_profile_pic_url_info: "Object with the HD profile picture URL.",
  fbid_v2: "Linked Facebook/Meta ID for the account.",
  pronouns: "Pronouns listed on the profile.",
  bio_links: "External links shown on the profile.",
  is_embeds_disabled: "Whether embedding this account's content is disabled.",
  is_regulated_c18: "Whether the account is age-restricted (18+).",
  show_account_transparency_details: "Whether Instagram shows account transparency details.",
  show_text_post_app_badge: "Whether the Threads badge is shown on the profile.",
  remove_message_entrypoint: "Whether the message button is hidden on the profile.",
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
  videoCount: "Total number of videos.",
  tweetCount: "Total number of tweets.",
  mediaCount: "Total number of media posts.",
  location: "Location shown on the profile or item.",
  website: "Website listed on the profile.",
  email: "Public email address, when exposed.",
  joinedDate: "When the account was created.",

  // Content
  title: "Title of the item.",
  text: "Text content.",
  description: "Description text.",
  caption: "Post caption.",
  publishedAt: "Publish date (ISO 8601).",
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
  isLive: "Whether the account/channel is currently live.",
  isVideo: "Whether the item is a video.",
  isPinned: "Whether the item is pinned.",
  isAd: "Whether the item is a paid promotion.",
  isReply: "Whether the tweet is a reply.",
  isRetweet: "Whether the tweet is a retweet.",
  isBlueVerified: "Whether the account has blue-check verification.",

  // Media
  thumbnailUrl: "Thumbnail image URL.",
  thumbnail: "Thumbnail image URL.",
  image: "Image URL.",
  avatar: "Avatar image URL.",
  profileImage: "Profile image URL.",
  banner: "Banner image URL.",
  bannerImage: "Banner image URL.",
  bannerUrl: "Banner image URL.",
  coverImage: "Cover image URL.",
  coverUrl: "Cover image URL.",
  logo: "Logo image URL.",
  videoUrl: "Direct video file URL (CDN link); may be null when a download URL isn't exposed — use the platform's download endpoint for the file.",
  downloadUrl: "Direct download URL for the media file.",
  noWatermarkUrl: "Watermark-free variant of the video URL.",
  embedUrl: "Embed page URL — load it directly in an <iframe src>.",
  videoId: "Platform video ID.",
  streamUrls: "Live stream playback URLs.",
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
  shares: "Share count.",
  shareCount: "Share count.",
  reposts: "Repost count.",
  replies: "Number of replies.",
  replyCount: "How many replies this comment has. Use Comment Replies with this comment's id to fetch them.",
  retweets: "Retweet count.",
  quotes: "Quote count.",
  bookmarks: "Bookmark count.",
  saves: "Save count.",
  upvotes: "Upvote count.",
  dislikes: "Dislike count.",
  score: "Vote score.",
  rank: "Rank position in the list.",
  engagementRate: "Engagement rate (interactions / views).",
  suggestion: "A search term TikTok autocompletes for your keyword — a phrase real users search for.",
  searchUrl: "Direct TikTok search URL for this suggestion — open it to see the matching results.",
  seed: "The seed keyword this suggestion was expanded from.",

  // Transcript / summarize
  transcript: "Complete text transcript.",
  wordCount: "Total number of words in the transcript.",
  segments: "Total number of transcript segments.",
  transcriptSegments: "Timestamped transcript segments.",
  summary: "AI-generated summary of the content.",
  keyPoints: "The most important takeaways.",
  sentiment: "Overall tone (positive, neutral, negative).",
  speaker: "Speaker label for the segment.",

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
  activeUsers: "Currently active user count.",
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
