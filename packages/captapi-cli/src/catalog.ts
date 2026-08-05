// Auto-maintained catalog of every Captapi endpoint exposed as an MCP tool.
// Each endpoint declares its EXACT input parameters (matching the REST API),
// so agents know precisely what to pass. Mirrors the backend routers.

export type Platform =
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

export interface ToolParam {
  name: string;
  type: "string" | "number" | "boolean";
  required: boolean;
  description: string;
}

export interface Endpoint {
  /** MCP tool name, e.g. "youtube_transcript". */
  tool: string;
  platform: Platform;
  /** Human marketing name, e.g. "YouTube Transcript". */
  name: string;
  /** REST path on the Captapi API, e.g. "/v1/youtube/transcript". */
  path: string;
  /** Typical credit cost of a standard request. */
  credits: number;
  /** One-line, agent-facing summary of what the tool does. */
  summary: string;
  /** Exact query parameters the endpoint accepts. */
  params: ToolParam[];
}

// --- Param builders (keep declarations terse + consistent) -----------------

const url = (description: string): ToolParam => ({
  name: "url",
  type: "string",
  required: true,
  description: `${description} The URL platform must match this tool's platform. Do not pass cross-platform URLs, e.g. YouTube to TikTok, Instagram to Facebook, LinkedIn to X/Twitter, or Pinterest to Rumble.`,
});
const q = (description = "Search query or keywords (min 2 chars)."): ToolParam => ({
  name: "q",
  type: "string",
  required: true,
  description,
});
const limit = (def: number, max: number): ToolParam => ({
  name: "limit",
  type: "number",
  required: false,
  description: `Max items to return. Default ${def}, max ${max}. Billed per result.`,
});
/** Limit helper for flat-fee endpoints (credit cost does not scale with limit). */
const limitFlat = (def: number, max: number, credits: number): ToolParam => ({
  name: "limit",
  type: "number",
  required: false,
  description: `Max items to return. Default ${def}, max ${max}. Flat ${credits} credit${credits === 1 ? "" : "s"} per call.`,
});
/** Limit helper for free account endpoints (never bills). */
const limitFree = (def: number, max: number): ToolParam => ({
  name: "limit",
  type: "number",
  required: false,
  description: `Max rows to return. Default ${def}, max ${max}. Free — does not consume credits.`,
});
const languageUi = (): ToolParam => ({
  name: "language",
  type: "string",
  required: false,
  description: "Interface language for localized results, e.g. en-US or de-DE. Default en-US.",
});
const fastRss = (): ToolParam => ({
  name: "fast",
  type: "boolean",
  required: false,
  description: "Set true to use YouTube RSS for faster results with less detailed metadata. Leave false when viewCount/duration quality matters.",
});
const language = (): ToolParam => ({
  name: "language",
  type: "string",
  required: false,
  description: 'Preferred caption language as an ISO code, e.g. "en". Defaults to auto-detect.',
});
const cacheParam = (): ToolParam => ({
  name: "cache",
  type: "boolean",
  required: false,
  description: "Set true to serve from the 24h response cache. Default false — always fetch fresh data.",
});
const commentId = (): ToolParam => ({
  name: "comment_id",
  type: "string",
  required: true,
  description: "ID of the parent comment to fetch replies for (from the comments endpoint).",
});

const YT_VIDEO = "Public YouTube video URL, e.g. https://youtube.com/watch?v=ID. Not a TikTok/Instagram/Facebook URL.";
const YT_SHORTS = "Public YouTube Shorts URL, e.g. https://youtube.com/shorts/ID (<=3 min). Long-form videos return HTTP 422.";
const YT_CHANNEL = "YouTube channel URL, e.g. https://youtube.com/@handle or /channel/UC...";
const TT_VIDEO = "Public TikTok video URL, e.g. https://tiktok.com/@user/video/ID. Not a YouTube/Instagram/Facebook URL.";
const TT_PROFILE = "TikTok profile URL, e.g. https://tiktok.com/@username. Not a YouTube channel URL.";
const TT_MUSIC = "TikTok music/sound URL, e.g. https://tiktok.com/music/name-ID.";
const IG_POST = "Instagram post or reel URL, e.g. https://instagram.com/reel/ID/.";
const IG_REEL = "Instagram Reel URL, e.g. https://instagram.com/reel/ID/.";
const IG_PROFILE = "Instagram profile URL, e.g. https://instagram.com/username/.";
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
const AMAZON_SHOP =
  "Amazon seller storefront URL (/sp?seller=… or /s?me=…) or raw seller ID. Not influencer /shop/<handle> pages.";
const KWAI_PROFILE = "Kwai profile URL or @handle, e.g. https://www.kwai.com/@easycashindonesia.";
const KWAI_POST = "Kwai video URL, e.g. https://www.kwai.com/@handle/video/5238962376325675745.";
const KOMI_PAGE = "Komi page URL or username.";
const PILLAR_PAGE = "Pillar page URL or username.";
const LINKBIO_PAGE = "Linkbio page URL or username.";
const LINKME_PROFILE = "Linkme profile URL or username.";

const YOUTUBE: Omit<Endpoint, "platform">[] = [
  { tool: "youtube_transcript", name: "YouTube Transcript", path: "/v1/youtube/transcript", credits: 1, summary: "Extract the full timestamped transcript of a YouTube video.", params: [url(YT_VIDEO), language(), cacheParam()] },
  { tool: "youtube_summarize", name: "YouTube Summarizer", path: "/v1/youtube/summarize", credits: 3, summary: "AI summary (key points, topics, sentiment) of a YouTube video.", params: [url(YT_VIDEO), language(), cacheParam()] },
  { tool: "youtube_video_details", name: "YouTube Video Details", path: "/v1/youtube/video-details", credits: 1, summary: "Metadata + engagement stats for a YouTube video.", params: [url(YT_VIDEO)] },
  { tool: "youtube_comments", name: "YouTube Comments", path: "/v1/youtube/comments", credits: 2, summary: "Comments on a YouTube video, with cursor pagination (nextCursor + hasMore).", params: [url(YT_VIDEO), limit(50, 500), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." }, cacheParam()] },
  { tool: "youtube_channel_details", name: "YouTube Channel Details", path: "/v1/youtube/channel-details", credits: 1, summary: "Channel info & numeric stats for a YouTube channel — plus handle, verified, links, email, and SEO tags when available.", params: [url(YT_CHANNEL)] },
  {
    tool: "youtube_search",
    name: "YouTube Search",
    path: "/v1/youtube/search",
    credits: 2,
    summary: "YouTube search — typed hits, ids, canonical URLs, cursor pagination, filters.",
    params: [
      q(),
      limit(20, 200),
      { name: "cursor", type: "string", required: false, description: "Pagination cursor from nextCursor." },
      { name: "type", type: "string", required: false, description: "all | videos | shorts | channels | playlists." },
      { name: "sortBy", type: "string", required: false, description: "relevance | date | views | rating." },
      { name: "uploadDate", type: "string", required: false, description: "any | today | this_week | this_month | this_year." },
      { name: "duration", type: "string", required: false, description: "any | under_4 | 4_20 | over_20." },
      { name: "region", type: "string", required: false, description: "ISO country code (default US)." },
    ],
  },
  { tool: "youtube_channel_videos", name: "YouTube Channel Videos", path: "/v1/youtube/channel-videos", credits: 2, summary: "List a channel's uploaded videos.", params: [url(YT_CHANNEL), limit(20, 200), fastRss()] },
  { tool: "youtube_playlist_videos", name: "YouTube Playlist Videos", path: "/v1/youtube/playlist-videos", credits: 2, summary: "List videos in a YouTube playlist.", params: [url("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."), limit(50, 500), fastRss()] },
  { tool: "youtube_playlist", name: "YouTube Playlist", path: "/v1/youtube/playlist", credits: 2, summary: "Playlist metadata plus videos from a YouTube playlist.", params: [url("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."), limit(50, 500), fastRss()] },
  { tool: "youtube_shorts_transcript", name: "YouTube Shorts Transcript", path: "/v1/youtube/shorts/transcript", credits: 1, summary: "Transcript of a YouTube Short.", params: [url(YT_SHORTS), language(), cacheParam()] },
  { tool: "youtube_shorts_summarize", name: "YouTube Shorts Summarizer", path: "/v1/youtube/shorts/summarize", credits: 3, summary: "AI summary of a YouTube Short.", params: [url(YT_SHORTS), language(), cacheParam()] },
  { tool: "youtube_shorts_details", name: "YouTube Shorts Stats", path: "/v1/youtube/shorts/video-details", credits: 1, summary: "Same schema as Video Details for a Short (isShort:true); long-form returns 422.", params: [url(YT_SHORTS)] },
  { tool: "youtube_shorts_comments", name: "YouTube Shorts Comments", path: "/v1/youtube/shorts/comments", credits: 2, summary: "Comments on a YouTube Short — same engine as /comments (flat 2 credits).", params: [url(YT_SHORTS), limit(50, 500), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." }, cacheParam()] },
  { tool: "youtube_channel_shorts", name: "YouTube Channel Shorts", path: "/v1/youtube/channel-shorts", credits: 2, summary: "List a channel's Shorts with player-enriched fields.", params: [url(YT_CHANNEL), limit(20, 200)] },
  { tool: "youtube_trending_shorts", name: "YouTube Trending Shorts", path: "/v1/youtube/trending-shorts", credits: 2, summary: "YouTube Shorts reel/trending feed (not a keyword search).", params: [{ name: "q", type: "string", required: false, description: "Optional topic seed for the reel sequence. Omit for default trending feed." }, limit(20, 100)] },
  { tool: "youtube_channel_streams", name: "YouTube Channel Streams", path: "/v1/youtube/channel-streams", credits: 2, summary: "Channel Live tab only (empty when hasLiveTab=false) — player-enriched streams.", params: [url(YT_CHANNEL), limitFlat(20, 200, 2), cacheParam()] },
  { tool: "youtube_hashtag_search", name: "YouTube Hashtag Search", path: "/v1/youtube/hashtag-search", credits: 20, summary: "Search YouTube videos by hashtag.", params: [q("Hashtag with or without the # (min 2 chars)."), limit(20, 200)] },
  { tool: "youtube_comment_replies", name: "YouTube Comment Replies", path: "/v1/youtube/comment-replies", credits: 2, summary: "Replies to a specific YouTube comment.", params: [url(YT_VIDEO), commentId(), limit(50, 500)] },
  { tool: "youtube_channel_playlists", name: "YouTube Channel Playlists", path: "/v1/youtube/channel-playlists", credits: 2, summary: "List a channel's playlists — id, title, videoCount, thumbnailUrl.", params: [url(YT_CHANNEL), limit(20, 200)] },
  { tool: "youtube_community_posts", name: "YouTube Community Posts", path: "/v1/youtube/community-posts", credits: 1, summary: "Community posts — likeCount+likeCountText, pollOptions, ISO dates, channel{}, cursor.", params: [url(YT_CHANNEL), limitFlat(20, 200, 1), { name: "cursor", type: "string", required: false, description: "Leave empty for the first page; then pass the nextCursor value from the previous response." }, cacheParam()] },
  { tool: "youtube_community_post_details", name: "YouTube Community Post Details", path: "/v1/youtube/community-post-details", credits: 1, summary: "One community post — same schema as list + comments (pollOptions, numeric likeCount).", params: [url("YouTube community post URL."), cacheParam()] },
  { tool: "youtube_video_sponsors", name: "YouTube Video Sponsors", path: "/v1/youtube/video-sponsors", credits: 1, summary: "SponsorBlock segments — sorted, overlapsWith, minVotes, coverageSeconds.", params: [url(YT_VIDEO), { name: "minVotes", type: "number", required: false, description: "Minimum votes (default 0; drops votes < 0)." }, { name: "categories", type: "string", required: false, description: "Comma-separated categories (default sponsor,selfpromo,interaction)." }, cacheParam()] },
];

const TIKTOK: Omit<Endpoint, "platform">[] = [
  { tool: "tiktok_transcript", name: "TikTok Transcript", path: "/v1/tiktok/transcript", credits: 2, summary: "Transcript of a TikTok video (via captions).", params: [url(TT_VIDEO), language(), { name: "cache", type: "boolean", required: false, description: "Serve from the 24h shared cache when available (0 credits on hit). Default true — set false to always fetch fresh." }] },
  { tool: "tiktok_summarize", name: "TikTok Summarizer", path: "/v1/tiktok/summarize", credits: 4, summary: "AI summary of a TikTok video.", params: [url(TT_VIDEO), language(), cacheParam()] },
  { tool: "tiktok_video_details", name: "TikTok Video Details", path: "/v1/tiktok/video-details", credits: 1, summary: "Metadata + stats for a TikTok video.", params: [url(TT_VIDEO)] },
  { tool: "tiktok_comments", name: "TikTok Comments", path: "/v1/tiktok/comments", credits: 2, summary: "Comments on a TikTok video — text, author, avatar, likes, and timestamp, plus totalComments and cursor pagination (limit up to 500).", params: [url(TT_VIDEO), limitFlat(50, 500, 2), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response (a numeric offset)." }] },
  { tool: "tiktok_channel_details", name: "TikTok Channel Details", path: "/v1/tiktok/channel-details", credits: 1, summary: "Resolve @handle → id + secUid; createTime, ttSeller, bioLink.risk, category, commerce flags.", params: [url(TT_PROFILE)] },
  { tool: "tiktok_profile_region", name: "TikTok Profile Region", path: "/v1/tiktok/profile-region", credits: 2, summary: "Where a TikTok creator is likely based and what language they use — country, language, and core profile stats from a profile URL or @handle. When TikTok hides the country, it is estimated from public bio/name/language cues, with a confidence grade.", params: [url(TT_PROFILE)] },
  { tool: "tiktok_audience_demographics", name: "TikTok Audience Demographics", path: "/v1/tiktok/audience-demographics", credits: 3, summary: "Ranked country breakdown of a TikTok creator's audience, based on people who comment on their recent videos (not a full follower census). From a profile URL or @handle.", params: [url(TT_PROFILE)] },
  { tool: "tiktok_search_suggestions", name: "TikTok Search Suggestions", path: "/v1/tiktok/search-suggestions", credits: 28, summary: "The autocomplete terms TikTok suggests in its search bar for a seed keyword — the real phrases people search, ranked. Localize by country + language.", params: [q("Seed keyword to expand into autocomplete suggestions, e.g. skincare."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code that localizes suggestions to a market, e.g. US, GB, DE. Default US." }, languageUi(), { name: "limit", type: "number", required: false, description: "Upper bound on suggestions to return (1-100, default 20). TikTok surfaces only a limited number of real autocomplete suggestions per keyword, so you'll often get fewer. Billed per result." }] },
  { tool: "tiktok_channel_posts", name: "TikTok Channel Posts", path: "/v1/tiktok/channel-posts", credits: 2, summary: "Latest videos from a TikTok profile — caption, engagement, thumbnail, sound, and hashtags for each post. Cursor pagination via nextCursor.", params: [url(TT_PROFILE), limitFlat(20, 200, 2), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." }] },
  { tool: "tiktok_comment_replies", name: "TikTok Comment Replies", path: "/v1/tiktok/comment-replies", credits: 2, summary: "Replies under a TikTok comment — text, author, likes, timestamp, with cursor pagination (nextCursor + hasMore). Flat 2 credits.", params: [url(TT_VIDEO), commentId(), limitFlat(50, 500, 2), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." }] },
  { tool: "tiktok_user_followers", name: "TikTok User Followers", path: "/v1/tiktok/user-followers", credits: 1, summary: "Followers — id, secUid, createTime, region, language; total + nextCursor. Flat 1 credit native.", params: [url(TT_PROFILE), limitFlat(50, 500, 1), { name: "cursor", type: "string", required: false, description: "Pagination cursor (TikTok minCursor). Leave empty for the first page; then pass nextCursor from the previous response." }] },
  { tool: "tiktok_user_followings", name: "TikTok User Followings", path: "/v1/tiktok/user-followings", credits: 1, summary: "Followings — id, secUid, createTime, region, language; total + nextCursor. Flat 1 credit native.", params: [url(TT_PROFILE), limitFlat(50, 500, 1), { name: "cursor", type: "string", required: false, description: "Pagination cursor (TikTok minCursor). Leave empty for the first page; then pass nextCursor from the previous response." }] },
  { tool: "tiktok_music_posts", name: "TikTok Music Posts", path: "/v1/tiktok/music-posts", credits: 32, summary: "Posts using a specific TikTok sound/music.", params: [url(TT_MUSIC), limit(20, 200)] },
  { tool: "tiktok_top_search", name: "TikTok Top Search", path: "/v1/tiktok/top-search", credits: 2, summary: "Top/General search: videos + photo carousels (contentType/images), cursor pagination.", params: [q(), limit(20, 200)] },
  { tool: "tiktok_search_by_hashtag", name: "TikTok Search by Hashtag", path: "/v1/tiktok/search/hashtag", credits: 14, summary: "Search TikTok videos by hashtag — video URL, caption, author, and engagement counts per result, with cursor pagination (nextCursor + hasMore).", params: [q("Hashtag with or without the # (min 2 chars)."), limit(20, 100), { name: "cursor", type: "number", required: false, description: "Pagination offset. Leave at 0 for the first page; then pass the nextCursor value from the previous response. A null nextCursor means the end." }, { name: "region", type: "string", required: false, description: "Two-letter ISO country our request is sent from. Default US. Does not filter results by country." }] },
  { tool: "tiktok_search_users", name: "TikTok Search Users", path: "/v1/tiktok/search/users", credits: 1, summary: "Search TikTok users — id, secUid, followers/following, verified, sample videos; cursor pagination.", params: [q("Search query matched against usernames, display names and bios."), limit(20, 100), { name: "cursor", type: "number", required: false, description: "Pagination offset. Leave at 0 for the first page; then pass the nextCursor value from the previous response. A null nextCursor means the end." }] },
  { tool: "tiktok_song_details", name: "TikTok Song Details", path: "/v1/tiktok/song-details", credits: 1, summary: "Sound metadata — usageCount, artists[], commerce rights, chorus timing; 1 credit native.", params: [url(TT_MUSIC)] },
  { tool: "tiktok_trending_feed", name: "TikTok Trending Feed", path: "/v1/tiktok/trending-feed", credits: 2, summary: "TikTok trending (For You) videos by region.", params: [{ name: "country", type: "string", required: false, description: "Two-letter ISO country code, e.g. US, GB, TR. Default US." }, limit(20, 200)] },
  { tool: "tiktok_popular_hashtags", name: "TikTok Popular Hashtags", path: "/v1/tiktok/popular-hashtags", credits: 2, summary: "TikTok Creative Center hashtag chart (population videoCount).", params: [{ name: "query", type: "string", required: false, description: "Optional niche seed for related-tag co-occurrence. Omit/trending for Creative Center chart." }, limit(20, 100)] },
  { tool: "tiktok_popular_songs", name: "TikTok Popular Songs", path: "/v1/tiktok/popular-songs", credits: 2, summary: "Creative Center popular/surging sounds — rankDiff, trend[], commercialMusic. Flat 2 credits.", params: [
    { name: "country", type: "string", required: false, description: "Two-letter ISO country. Default US." },
    { name: "period", type: "string", required: false, description: "7, 30, or 120 days. Default 7." },
    { name: "page", type: "number", required: false, description: "Page number (default 1)." },
    { name: "rankType", type: "string", required: false, description: "popular | surging. Default popular." },
    { name: "newOnBoard", type: "boolean", required: false, description: "Only sounds newly on the Top 100." },
    { name: "commercialMusic", type: "boolean", required: false, description: "Only Commercial Music Library-cleared sounds." },
    limitFlat(20, 20, 2),
  ] },
  { tool: "tiktok_live", name: "TikTok Live", path: "/v1/tiktok/live", credits: 1, summary: "isLive/status, creator.id/secUid, streamQualities with flv/hls/cmaf/dash. Flat 1 credit.", params: [url(TT_PROFILE)] },
  { tool: "tiktok_live_info", name: "TikTok Live Info", path: "/v1/tiktok/live-info", credits: 7, summary: "True alias of /live (same payload) at 7 credits for SC path compatibility.", params: [url(TT_PROFILE)] },
  { tool: "tiktok_popular_creators", name: "TikTok Popular Creators", path: "/v1/tiktok/popular-creators", credits: 28, summary: "Popular TikTok creators by country and ranking mode.", params: [{ name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }, { name: "sort", type: "string", required: false, description: "follower, engagement, or popularity. Default follower." }, { name: "follower_count", type: "string", required: false, description: "Optional range: 10k-100k, 100k-1m, 1m-10m, >10m." }, limit(20, 100)] },
];

const INSTAGRAM: Omit<Endpoint, "platform">[] = [
  { tool: "instagram_transcript", name: "Instagram Transcript", path: "/v1/instagram/transcript", credits: 2, summary: "Transcript of an Instagram Reel.", params: [url(IG_REEL), language(), cacheParam()] },
  { tool: "instagram_summarize", name: "Instagram Summarizer", path: "/v1/instagram/summarize", credits: 4, summary: "AI summary of an Instagram Reel.", params: [url(IG_REEL), language(), cacheParam()] },
  { tool: "instagram_details", name: "Instagram Post Details", path: "/v1/instagram/details", credits: 1, summary: "Details for an Instagram post or reel.", params: [url(IG_POST)] },
  { tool: "instagram_comments", name: "Instagram Post Comments", path: "/v1/instagram/comments", credits: 45, summary: "Comments on an Instagram post or reel.", params: [url(IG_POST), limit(50, 500)] },
  { tool: "instagram_channel_details", name: "Instagram Channel Details", path: "/v1/instagram/channel-details", credits: 1, summary: "Profile info & stats for an Instagram account.", params: [url(IG_PROFILE)] },
  { tool: "instagram_channel_posts", name: "Instagram Channel Posts", path: "/v1/instagram/channel-posts", credits: 6, summary: "Latest posts from an Instagram profile.", params: [url(IG_PROFILE), limit(20, 200), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." }] },
  { tool: "instagram_channel_reels", name: "Instagram Channel Reels", path: "/v1/instagram/channel-reels", credits: 6, summary: "Latest Reels from an Instagram profile — url or userId; nextCursor + hasMore.", params: [
    { name: "url", type: "string", required: false, description: "Instagram profile URL, @handle, or username. Omit when userId is set. The URL platform must match this tool's platform." },
    { name: "userId", type: "string", required: false, description: "Instagram numeric user ID (e.g. 173560420). Faster than url — skips handle→ID resolve." },
    limit(20, 200),
    { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass nextCursor. Stop when hasMore is false." },
  ] },
  { tool: "instagram_reels_search", name: "Instagram Reels Search", path: "/v1/instagram/reels-search", credits: 2, summary: "Native Instagram Reels hashtag search — views/plays, author verified/followers, datePosted. Flat 2 credits.", params: [q("Hashtag (without #) or keyword (min 2 chars)."), limitFlat(20, 200, 2), { name: "datePosted", type: "string", required: false, description: "last_24_hours | last_week | last_month | last_year." }] },
  { tool: "instagram_trending_reels", name: "Instagram Trending Reels", path: "/v1/instagram/trending-reels", credits: 1, summary: "Snapshot-backed trending Reels (typical freshness <24h) — videos only, flat 1 credit. Use reels-search for live scrapes.", params: [{ name: "country", type: "string", required: false, description: "Country name or ISO code. Unsupported → 400 with supportedCountries." }, limit(20, 200)] },
  { tool: "instagram_tagged_posts", name: "Instagram Tagged Posts", path: "/v1/instagram/tagged-posts", credits: 1, summary: "Tagged posts — author id, views, hashtags/mentions; cursor pagination.", params: [url(IG_PROFILE), limitFlat(20, 200, 1), { name: "cursor", type: "string", required: false, description: "Leave empty for the first page; then pass the nextCursor value from the previous response." }] },
  { tool: "instagram_reels_by_audio_id", name: "Instagram Reels By Audio ID", path: "/v1/instagram/reels-by-audio-id", credits: 28, summary: "Reels by audio + isTrendingInClips / trendRank / music{}.", params: [{ name: "audio_id", type: "string", required: true, description: "Instagram audio/music ID or full audio URL." }, limit(20, 200)] },
  { tool: "instagram_hashtag_search", name: "Instagram Hashtag Search", path: "/v1/instagram/hashtag-search", credits: 2, summary: "Search Instagram posts by hashtag (native grid).", params: [q("Hashtag without the # (min 2 chars)."), limit(20, 200), { name: "mediaType", type: "string", required: false, description: "all (default) or reels — return only Reels/clips when set to reels." }] },
  { tool: "instagram_profile_search", name: "Instagram Profile Search", path: "/v1/instagram/profile-search", credits: 1, summary: "Resolve a brand or @handle to one Instagram profile with id, bio, links, and stats (not niche discovery). Flat 1 credit.", params: [q()] },
  { tool: "instagram_embed", name: "Instagram Embed HTML", path: "/v1/instagram/embed", credits: 1, summary: "Embed HTML for an Instagram post, reel, or profile.", params: [url("Instagram post, reel, or profile URL (or @handle), e.g. https://instagram.com/reel/ID/ or https://instagram.com/username/.")] },
  { tool: "instagram_highlights", name: "Instagram Highlights", path: "/v1/instagram/highlights", credits: 1, summary: "Persistent Story Highlight albums for a public profile — id, title, cover, owner. Flat 1 credit.", params: [
    { name: "url", type: "string", required: false, description: "Instagram profile URL, @handle, or username. Omit when userId is set." },
    { name: "userId", type: "string", required: false, description: "Numeric Instagram user ID. Prefer when known — skips handle→ID resolve." },
    cacheParam(),
  ] },
  { tool: "instagram_highlights_details", name: "Instagram Highlight Details", path: "/v1/instagram/highlights-details", credits: 1, summary: "Items inside one Instagram Story Highlight album — media URLs, type, takenAt. Flat 1 credit.", params: [
    { name: "id", type: "string", required: true, description: "Highlight id from /v1/instagram/highlights (with or without highlight: prefix)." },
    cacheParam(),
  ] },
  { tool: "instagram_basic_profile", name: "Instagram Basic Profile", path: "/v1/instagram/basic-profile", credits: 1, summary: "Instagram profile by user ID/@handle — camelCase (followers, externalUrl, businessAddress).", params: [{ name: "userId", type: "string", required: true, description: "Instagram numeric user ID (e.g. 13460080). A profile URL, @handle, or username is also accepted and resolved automatically." }] },
];

const FACEBOOK: Omit<Endpoint, "platform">[] = [
  { tool: "facebook_details", name: "Facebook Details", path: "/v1/facebook/details", credits: 2, summary: "Facebook post or Reel details — engagement, author id, SD/HD video, captions, and music when exposed.", params: [url(FB_VIDEO)] },
  { tool: "facebook_summarize", name: "Facebook Summarizer", path: "/v1/facebook/summarize", credits: 4, summary: "AI summary of a Facebook video or post.", params: [url(FB_VIDEO), cacheParam()] },
  { tool: "facebook_comments", name: "Facebook Comments", path: "/v1/facebook/comments", credits: 2, summary: "Facebook comments — 10-type reactions{}, stable author.id, replyCount, hasMore.", params: [
    { name: "url", type: "string", required: false, description: "Facebook post or Reel URL. Omit when feedbackId is set." },
    { name: "feedbackId", type: "string", required: false, description: "Post feedback id from /v1/facebook/details. Prefer when you already have it." },
    limitFlat(50, 500, 2),
  ] },
  { tool: "facebook_page_details", name: "Facebook Page Details", path: "/v1/facebook/page-details", credits: 2, summary: "Facebook page profile — distinct likes vs followers, talkingAbout, category, website, public email. Flat 2 credits.", params: [url("Facebook page URL, e.g. https://facebook.com/PageName.")] },
  { tool: "facebook_profile_posts", name: "Facebook Profile Posts", path: "/v1/facebook/profile-posts", credits: 12, summary: "Latest posts from a Facebook profile/page.", params: [url("Facebook profile or page URL."), limit(20, 200)] },
  { tool: "facebook_profile_reels", name: "Facebook Profile Reels", path: "/v1/facebook/profile-reels", credits: 2, summary: "Latest page Reels with full engagement; newest-first, archive cliff.", params: [url("Facebook profile or page URL."), limit(20, 200)] },
  { tool: "facebook_group_posts", name: "Facebook Group Posts", path: "/v1/facebook/group-posts", credits: 2, summary: "Public Facebook group posts — author IDs, permalink, sortBy, engagement (shares null when unknown).", params: [url("Public Facebook group URL, e.g. https://facebook.com/groups/ID."), limitFlat(20, 200, 2), { name: "sortBy", type: "string", required: false, description: "TOP_POSTS | RECENT_ACTIVITY | CHRONOLOGICAL (default) | CHRONOLOGICAL_LISTINGS." }] },
  { tool: "facebook_comment_replies", name: "Facebook Comment Replies", path: "/v1/facebook/comment-replies", credits: 2, summary: "Replies to a Facebook comment — same author/reactions shape as comments.", params: [url("Facebook post URL the comment belongs to."), commentId(), limitFlat(50, 500, 2)] },
  { tool: "facebook_profile_photos", name: "Facebook Profile Photos", path: "/v1/facebook/profile-photos", credits: 12, summary: "Photos from a Facebook profile or page.", params: [url("Facebook profile or page URL."), limit(20, 200)] },
];

const FACEBOOK_MARKETPLACE: Omit<Endpoint, "platform">[] = [
  { tool: "facebook_marketplace_search", name: "Facebook Marketplace Search", path: "/v1/facebook/marketplace-search", credits: 2, summary: "Search Facebook Marketplace listings by keyword and city name.", params: [
    q("Product or keyword to search for (min 2 chars)."),
    { name: "location", type: "string", required: true, description: "City or place name, e.g. 'Austin, TX'." },
    limitFlat(20, 200, 2),
    { name: "minPrice", type: "number", required: false, description: "Minimum price in local currency units." },
    { name: "maxPrice", type: "number", required: false, description: "Maximum price in local currency units." },
    { name: "sortBy", type: "string", required: false, description: "suggested | distance | creation_time | price_ascend | price_descend." },
    { name: "daysSinceListed", type: "string", required: false, description: "1 (24h), 7, or 30." },
    { name: "condition", type: "string", required: false, description: "new, like_new, good, fair." },
    { name: "deliveryMethod", type: "string", required: false, description: "local_pickup | shipping | all." },
    { name: "availability", type: "string", required: false, description: "available | sold | all." },
    { name: "radiusMiles", type: "number", required: false, description: "Radius in miles (1–500 discrete values)." },
    { name: "category", type: "string", required: false, description: "Top-level category slug, e.g. electronics." },
    { name: "cursor", type: "string", required: false, description: "Pagination cursor from a previous nextCursor." },
    { name: "details", type: "string", required: false, description: "Set true for description/condition/coordinates/full gallery (2 + 2 credits per listing). Cover photo is included even when false." },
  ] },
  { tool: "facebook_marketplace_location_search", name: "Facebook Marketplace Location Search", path: "/v1/facebook/marketplace-location-search", credits: 2, summary: "Disambiguate city names into Marketplace hubs with Facebook cityPageId + lat/lng. marketplace-search already accepts a city string — use this for ambiguous names (Austin TX vs MN) or when you need cityPageId. Flat 2 credits.", params: [q("City/place query. Bare 'Austin' may return TX/MN/IN; include a state for a single hit."), limitFlat(10, 50, 2), cacheParam()] },
  { tool: "facebook_marketplace_item", name: "Facebook Marketplace Item", path: "/v1/facebook/marketplace-item", credits: 1, summary: "Details for a single Facebook Marketplace listing.", params: [url("Facebook Marketplace item URL.")] },
];

const FACEBOOK_EVENTS: Omit<Endpoint, "platform">[] = [
  { tool: "facebook_event_search", name: "Facebook Event Search", path: "/v1/facebook/event-search", credits: 40, summary: "Search Facebook events by topic and/or location.", params: [q("Topic and/or place, e.g. 'comedy Chicago' (min 2 chars)."), limit(20, 200)] },
  { tool: "facebook_event_details", name: "Facebook Event Details", path: "/v1/facebook/event-details", credits: 2, summary: "Details for a Facebook event (date, location, attendees, tickets).", params: [url("Facebook event URL, e.g. https://facebook.com/events/ID.")] },
  { tool: "facebook_profile_events", name: "Facebook Profile Events", path: "/v1/facebook/profile-events", credits: 40, summary: "Events from a Facebook profile or page.", params: [url("Facebook profile or page URL."), limit(20, 200)] },
];

const TW_TWEET = "Public tweet URL, e.g. https://x.com/user/status/ID.";
const TW_PROFILE = "Twitter/X profile URL or @handle, e.g. https://x.com/username.";
const TW_COMMUNITY = "X community URL (x.com/i/communities/ID) or community ID.";
const RD_SUB = "Subreddit URL, r/name, or bare name, e.g. r/technology.";
const RD_POST = "Reddit post URL, e.g. https://reddit.com/r/sub/comments/ID/...";
const TH_PROFILE = "Threads profile URL or @handle, e.g. https://threads.net/@username.";
const TH_POST = "Threads post URL, e.g. https://threads.net/@user/post/CODE.";
const BS_PROFILE = "Bluesky profile URL, @handle, or handle, e.g. bsky.app/profile/handle.";
const BS_POST = "Bluesky post URL, e.g. https://bsky.app/profile/handle/post/RKEY.";
const PIN_PIN = "Pinterest pin URL, e.g. https://pinterest.com/pin/ID/.";
const PIN_PROFILE = "Pinterest profile URL or username.";
const PIN_BOARD = "Pinterest board URL, e.g. https://pinterest.com/username/board-name/.";
const LI_PROFILE = "LinkedIn profile URL, e.g. https://linkedin.com/in/slug.";
const LI_COMPANY = "LinkedIn company URL, e.g. https://linkedin.com/company/slug.";
const LI_POST = "LinkedIn post or activity URL.";
const RB_VIDEO = "Rumble video URL, e.g. https://rumble.com/vXXXX-title.html.";
const RB_CHANNEL = "Rumble channel URL, e.g. https://rumble.com/c/name.";

const TWITTER: Omit<Endpoint, "platform">[] = [
  { tool: "twitter_tweet_details", name: "Twitter/X Tweet Details", path: "/v1/twitter/tweet-details", credits: 1, summary: "Metadata + engagement stats for a tweet.", params: [url(TW_TWEET)] },
  { tool: "twitter_transcript", name: "Twitter/X Transcript", path: "/v1/twitter/transcript", credits: 1, summary: "Extract tweet text as transcript text.", params: [url(TW_TWEET), cacheParam()] },
  { tool: "twitter_profile", name: "Twitter/X Profile", path: "/v1/twitter/profile", credits: 1, summary: "Public Twitter/X profile — bio, followers, following, tweet count, avatar.", params: [url(TW_PROFILE)] },
  { tool: "twitter_user_tweets", name: "Twitter/X User Tweets", path: "/v1/twitter/user-tweets", credits: 2, summary: "Recent tweets from a Twitter/X profile.", params: [url(TW_PROFILE), limit(20, 200)] },
  { tool: "twitter_search", name: "Twitter/X Search", path: "/v1/twitter/search", credits: 2, summary: "Search public tweets on X by keyword — text, author, engagement, hashtags, and media.", params: [q(), limit(20, 200)] },
  { tool: "twitter_community", name: "Twitter/X Community", path: "/v1/twitter/community", credits: 1, summary: "Details for an X (Twitter) community.", params: [url(TW_COMMUNITY)] },
  { tool: "twitter_community_tweets", name: "Twitter/X Community Tweets", path: "/v1/twitter/community-tweets", credits: 2, summary: "Community posts — flat 2 native; ~0.7/tweet Apify fallback.", params: [url(TW_COMMUNITY), limit(25, 200)] },
];

const REDDIT: Omit<Endpoint, "platform">[] = [
  { tool: "reddit_subreddit_posts", name: "Reddit Subreddit Posts", path: "/v1/reddit/subreddit-posts", credits: 2, summary: "Posts in a subreddit with sort/timeframe and cursor pagination (nextCursor + hasMore).", params: [
    url(RD_SUB),
    limitFlat(25, 200, 2),
    { name: "sort", type: "string", required: false, description: "Feed sort: best, hot, new (default), top, or rising." },
    { name: "timeframe", type: "string", required: false, description: "For sort=top: hour, day (default), week, month, year, or all." },
    { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." },
  ] },
  { tool: "reddit_post_details", name: "Reddit Post Details", path: "/v1/reddit/post-details", credits: 1, summary: "Metadata + stats for a Reddit post.", params: [url(RD_POST)] },
  { tool: "reddit_post_comments", name: "Reddit Post Comments", path: "/v1/reddit/post-comments", credits: 2, summary: "Comments on a Reddit post.", params: [url(RD_POST), limit(50, 500)] },
  { tool: "reddit_post_transcript", name: "Reddit Post Transcript", path: "/v1/reddit/post-transcript", credits: 2, summary: "Extract Reddit post text and top comments as a discussion transcript.", params: [url(RD_POST), limit(50, 200)] },
  { tool: "reddit_search", name: "Reddit Search", path: "/v1/reddit/search", credits: 2, summary: "Site-wide Reddit search with sort/timeframe, scores, authorFullname, cursor.", params: [
    q(),
    { name: "sort", type: "string", required: false, description: "relevance (default) | new | top | hot | comments (alias: comment_count)." },
    { name: "timeframe", type: "string", required: false, description: "For sort=top or comments: hour | day | week | month | year | all (default all)." },
    limit(25, 200),
    { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." },
  ] },
  { tool: "reddit_subreddit_details", name: "Reddit Subreddit Details", path: "/v1/reddit/subreddit-details", credits: 1, summary: "Subreddit card — t5_ id, members, activeUsers, rules[], ISO createdAt.", params: [url(RD_SUB)] },
  { tool: "reddit_subreddit_search", name: "Reddit Subreddit Search", path: "/v1/reddit/subreddit-search", credits: 2, summary: "Search inside one subreddit — same sort/timeframe and fields as site-wide Search.", params: [
    url(RD_SUB),
    q(),
    { name: "sort", type: "string", required: false, description: "relevance (default) | new | top | hot | comments (alias: comment_count)." },
    { name: "timeframe", type: "string", required: false, description: "For sort=top or comments: hour | day | week | month | year | all (default all)." },
    limit(25, 200),
    { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." },
  ] },
];

const THREADS: Omit<Endpoint, "platform">[] = [
  { tool: "threads_profile", name: "Threads Profile", path: "/v1/threads/profile", credits: 1, summary: "Threads profile — bio, followers, verified, isPrivate, bioLinks, transparencyLabel, HD avatar versions.", params: [url(TH_PROFILE)] },
  { tool: "threads_user_posts", name: "Threads User Posts", path: "/v1/threads/user-posts", credits: 2, summary: "Recent Threads posts — views+engagement, threadId/isReply. Flat 2 native.", params: [url(TH_PROFILE), limit(20, 100)] },
  { tool: "threads_post_details", name: "Threads Post Details", path: "/v1/threads/post-details", credits: 1, summary: "Metadata + engagement for a Threads post.", params: [url(TH_POST)] },
  { tool: "threads_search", name: "Threads Post Search", path: "/v1/threads/search", credits: 2, summary: "Threads keyword search — flat 2 native (~0.7/post Apify). Meta Top SERP; no sort/date.", params: [q(), limit(25, 200)] },
  { tool: "threads_search_users", name: "Threads Search Users", path: "/v1/threads/search-users", credits: 1, summary: "Distinct authors from keyword search — id, avatar, verified. Flat 1 native.", params: [q(), limit(20, 100)] },
];

const BLUESKY: Omit<Endpoint, "platform">[] = [
  { tool: "bluesky_profile", name: "Bluesky Profile", path: "/v1/bluesky/profile", credits: 1, summary: "Bluesky profile — counts, banner, verification{}, labels[], associated{}.", params: [url(BS_PROFILE)] },
  { tool: "bluesky_user_posts", name: "Bluesky User Posts", path: "/v1/bluesky/user-posts", credits: 3, summary: "Recent posts from a Bluesky profile — text, author, likes, reposts, embeds; cursor pagination.", params: [url(BS_PROFILE), limit(25, 100), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." }] },
  { tool: "bluesky_post_details", name: "Bluesky Post Details", path: "/v1/bluesky/post-details", credits: 1, summary: "Metadata + engagement for a Bluesky post.", params: [url(BS_POST)] },
];

const PINTEREST: Omit<Endpoint, "platform">[] = [
  { tool: "pinterest_pin_details", name: "Pinterest Pin Details", path: "/v1/pinterest/pin-details", credits: 1, summary: "Pin title, description, link, board, originAuthor, images, and engagement (1 credit).", params: [url(PIN_PIN)] },
  { tool: "pinterest_user_pins", name: "Pinterest User Pins", path: "/v1/pinterest/user-pins", credits: 13, summary: "Pins from a Pinterest profile.", params: [url(PIN_PROFILE), limit(25, 200)] },
  { tool: "pinterest_search", name: "Pinterest Search", path: "/v1/pinterest/search", credits: 13, summary: "Search Pinterest pins by keyword.", params: [q(), limit(25, 200)] },
  { tool: "pinterest_board", name: "Pinterest Board", path: "/v1/pinterest/board", credits: 13, summary: "Board pins — saves, imageOriginal, destinationUrl, top-level author. Board URL only.", params: [url(PIN_BOARD), limit(25, 200)] },
  { tool: "pinterest_user_boards", name: "Pinterest User Boards", path: "/v1/pinterest/user-boards", credits: 13, summary: "List the boards on a Pinterest profile.", params: [url(PIN_PROFILE), limit(25, 200)] },
];

const LINKEDIN: Omit<Endpoint, "platform">[] = [
  { tool: "linkedin_profile", name: "LinkedIn Profile", path: "/v1/linkedin/profile", credits: 2, summary: "Public LinkedIn person profile details.", params: [url(LI_PROFILE)] },
  { tool: "linkedin_company", name: "LinkedIn Company", path: "/v1/linkedin/company", credits: 2, summary: "Public LinkedIn company page details.", params: [url(LI_COMPANY)] },
  { tool: "linkedin_post_details", name: "LinkedIn Post Details", path: "/v1/linkedin/post-details", credits: 1, summary: "Metadata + engagement for a LinkedIn post.", params: [url(LI_POST)] },
  { tool: "linkedin_post_transcript", name: "LinkedIn Post Transcript", path: "/v1/linkedin/post-transcript", credits: 1, summary: "Extract post text as a transcript for a LinkedIn post.", params: [url(LI_POST)] },
  { tool: "linkedin_company_posts", name: "LinkedIn Company Posts", path: "/v1/linkedin/company-posts", credits: 16, summary: "Recent public posts from a LinkedIn company page, with cursor pagination (nextCursor + hasMore) up to 100 posts.", params: [url(LI_COMPANY), limit(20, 100), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response (numeric offset, e.g. 20)." }] },
  { tool: "linkedin_search_posts", name: "LinkedIn Search Posts", path: "/v1/linkedin/search-posts", credits: 16, summary: "Search public LinkedIn posts by keyword.", params: [q(), { name: "sort", type: "string", required: false, description: "relevance or date. Default relevance." }, limit(20, 50)] },
];

const RUMBLE: Omit<Endpoint, "platform">[] = [
  { tool: "rumble_video_details", name: "Rumble Video Details", path: "/v1/rumble/video-details", credits: 1, summary: "Metadata + stats for a Rumble video.", params: [url(RB_VIDEO)] },
  { tool: "rumble_channel_videos", name: "Rumble Channel Videos", path: "/v1/rumble/channel-videos", credits: 12, summary: "List videos from a Rumble channel.", params: [url(RB_CHANNEL), limit(20, 200)] },
  { tool: "rumble_search", name: "Rumble Search", path: "/v1/rumble/search", credits: 12, summary: "Search Rumble videos by keyword.", params: [q(), limit(20, 200)] },
  { tool: "rumble_comments", name: "Rumble Comments", path: "/v1/rumble/comments", credits: 30, summary: "Comments on a Rumble video.", params: [url(RB_VIDEO), limit(50, 500)] },
];

const TIKTOK_SHOP: Omit<Endpoint, "platform">[] = [
  { tool: "tiktok_shop_search", name: "TikTok Shop Search", path: "/v1/tiktok-shop/shop-search", credits: 56, summary: "Search TikTok Shop products by keyword.", params: [q("Product search query."), { name: "region", type: "string", required: false, description: "Two-letter TikTok Shop region. Default US." }, limit(20, 200)] },
  { tool: "tiktok_shop_products", name: "TikTok Shop Products", path: "/v1/tiktok-shop/shop-products", credits: 2, summary: "Store catalog + shopInfo. Flat 2 credits on native SSR (limit does not multiply).", params: [url("TikTok Shop store URL."), limitFlat(20, 200, 2)] },
  {
    tool: "tiktok_shop_product_details",
    name: "TikTok Shop Product Details",
    path: "/v1/tiktok-shop/product-details",
    credits: 2,
    summary: "PDP with price/originalPrice/discount, skus[]+saleProps, images, categories. 2 credits native.",
    params: [
      url("TikTok Shop product URL."),
      { name: "region", type: "string", required: false, description: "Market region ISO code for Apify fallback (default US)." },
    ],
  },
  { tool: "tiktok_shop_product_reviews", name: "TikTok Shop Product Reviews", path: "/v1/tiktok-shop/product-reviews", credits: 45, summary: "Shop product reviews — stars, text, SKU, verified, country, review photos. Not video comments.", params: [url("TikTok Shop product URL."), limit(20, 200)] },
  { tool: "tiktok_shop_user_showcase", name: "TikTok Shop User Showcase", path: "/v1/tiktok-shop/user-showcase", credits: 45, summary: "Creator affiliate shelf — sold, rating, originalPrice, seller name/url (PDP-hydrated).", params: [{ name: "username", type: "string", required: true, description: "TikTok username, @handle, or profile URL, e.g. jeffreestar or https://www.tiktok.com/@jeffreestar." }, limit(20, 200)] },
];

const GITHUB: Omit<Endpoint, "platform">[] = [
  { tool: "github_user", name: "GitHub User", path: "/v1/github/user", credits: 1, summary: "Public GitHub profile as camelCase JSON (type User|Organization, email when public). 1 credit — thin wrap of free GitHub REST; prefer Captapi for one-key multi-platform, api.github.com for GitHub-only.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL, e.g. getify." }, cacheParam()] },
  { tool: "github_repositories", name: "GitHub Repositories", path: "/v1/github/repositories", credits: 12, summary: "List repos with sort/direction/type echoed; opaque Link cursor. parent/watchers only on github/repository.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, { name: "sort", type: "string", required: false, description: "created|updated|pushed|full_name (default updated)." }, { name: "direction", type: "string", required: false, description: "asc or desc (default desc)." }, { name: "type", type: "string", required: false, description: "owner|member|all (default owner)." }, limit(30, 100), { name: "cursor", type: "string", required: false, description: "Opaque cursor from previous nextCursor (GitHub Link page=)." }] },
  { tool: "github_repository", name: "GitHub Repository", path: "/v1/github/repository", credits: 1, summary: "Repo details — stars, real watchers (subscribers), openIssuesAndPrs, license (NOASSERTION→null), parent when fork. Flat 1 credit.", params: [{ name: "repo", type: "string", required: true, description: "Repository URL or owner/name, e.g. torvalds/linux." }, cacheParam()] },
  { tool: "github_pull_requests", name: "GitHub Pull Requests", path: "/v1/github/pull-requests", credits: 12, summary: "List PRs with draft, labels, author{}, head/base; state echoed; opaque Link cursor.", params: [{ name: "repo", type: "string", required: true, description: "Repository URL or owner/name." }, { name: "state", type: "string", required: false, description: "open (default), closed, or all — echoed as data.state." }, limit(30, 100), { name: "cursor", type: "string", required: false, description: "Opaque cursor from previous nextCursor (GitHub Link page=)." }] },
  { tool: "github_activity", name: "GitHub Activity", path: "/v1/github/activity", credits: 12, summary: "Public events with typed payload (Push commits/ref, PR/issue action). 90-event ceiling; opaque Link cursor.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL, e.g. getify." }, limit(30, 90), { name: "cursor", type: "string", required: false, description: "Opaque cursor from previous nextCursor. Stops at 90-event ceiling." }] },
  { tool: "github_followers", name: "GitHub Followers", path: "/v1/github/followers", credits: 3, summary: "Follower cards {id,login,type,url,avatar}. ~0.1/row; opaque Link cursor. Large accounts expensive to page fully.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL, e.g. getify." }, limit(30, 100), { name: "cursor", type: "string", required: false, description: "Opaque cursor from previous nextCursor (GitHub Link page=)." }] },
  { tool: "github_following", name: "GitHub Following", path: "/v1/github/following", credits: 3, summary: "Same card and ~0.1/row pricing as followers. Opaque Link cursor.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL, e.g. getify." }, limit(30, 100), { name: "cursor", type: "string", required: false, description: "Opaque cursor from previous nextCursor (GitHub Link page=)." }] },
  { tool: "github_contributions", name: "GitHub Contributions", path: "/v1/github/contributions", credits: 2, summary: "Real contribution graph — totalContributions, currentStreak, days[{date,count,level}] from the public calendar HTML. Flat 2 credits.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL, e.g. getify." }, cacheParam()] },
  { tool: "github_trending_repositories", name: "GitHub Trending Repositories", path: "/v1/github/trending-repositories", credits: 2, summary: "github.com/trending — repos ranked by starsGained (since=daily|weekly|monthly), not all-time star search. Flat 2 credits.", params: [{ name: "since", type: "string", required: false, description: "daily (default), weekly, or monthly." }, { name: "language", type: "string", required: false, description: "Optional programming-language slug, e.g. python." }, limitFlat(25, 100, 2), cacheParam()] },
  { tool: "github_trending_developers", name: "GitHub Trending Developers", path: "/v1/github/trending-developers", credits: 2, summary: "github.com/trending/developers — windowed ranks with popularRepo + hydrated followers/bio. Flat 2 credits.", params: [{ name: "since", type: "string", required: false, description: "daily (default), weekly, or monthly." }, { name: "language", type: "string", required: false, description: "Optional programming-language slug, e.g. python." }, limitFlat(25, 100, 2), cacheParam()] },
];


const TWITCH: Omit<Endpoint, "platform">[] = [
  { tool: "twitch_profile", name: "Twitch Profile", path: "/v1/twitch/profile", credits: 1, summary: "Twitch channel — live stream, last broadcast, recent videos with embedUrl, game box art, storyboard previews.", params: [url(TWITCH_PROFILE)] },
  { tool: "twitch_user_videos", name: "Twitch User Videos", path: "/v1/twitch/user-videos", credits: 2, summary: "Channel VODs with filterBy/sortBy, cursor, broadcaster id/followers.", params: [
    url(TWITCH_PROFILE),
    limitFlat(20, 100, 2),
    { name: "filterBy", type: "string", required: false, description: "ARCHIVE | HIGHLIGHT | UPLOAD. Omit for all types." },
    { name: "sortBy", type: "string", required: false, description: "TIME (default) or VIEWS." },
    { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass nextCursor from the previous response." },
  ] },
  { tool: "twitch_user_schedule", name: "Twitch User Schedule", path: "/v1/twitch/user-schedule", credits: 1, summary: "Upcoming Twitch schedule data when exposed on the public channel.", params: [url(TWITCH_PROFILE)] },
  { tool: "twitch_clip", name: "Twitch Clip", path: "/v1/twitch/clip", credits: 1, summary: "Twitch clip — curator vs channel, qualities, token expiry.", params: [url("Twitch clip URL, channel URL, or username.")] },
];

const SPOTIFY: Omit<Endpoint, "platform">[] = [
  { tool: "spotify_artist", name: "Spotify Artist", path: "/v1/spotify/artist", credits: 1, summary: "Spotify artist — followers, monthlyListeners, worldRank, topCities, topTracks with playCount, concerts, related artists.", params: [url(SPOTIFY_URL), cacheParam()] },
  { tool: "spotify_track", name: "Spotify Track", path: "/v1/spotify/track", credits: 1, summary: "Spotify track — playCount, artist/album IDs, explicit rating.", params: [url(SPOTIFY_URL), cacheParam()] },
  { tool: "spotify_album", name: "Spotify Album", path: "/v1/spotify/album", credits: 6, summary: "Spotify album metadata and track count.", params: [url(SPOTIFY_URL), cacheParam()] },
  { tool: "spotify_search", name: "Spotify Search", path: "/v1/spotify/search", credits: 2, summary: "Search Spotify by type (tracks/albums/artists/podcasts/episodes) - canonical URIs, explicit/playable, scrapedAt. Flat 2 credits.", params: [q(), { name: "type", type: "string", required: false, description: "Result kind: tracks (default), albums, artists, podcasts, or episodes." }, limit(20, 50)] },
  { tool: "spotify_podcast", name: "Spotify Podcast", path: "/v1/spotify/podcast", credits: 1, summary: "Spotify podcast — publisher, rating, topics, explicit, totalEpisodes.", params: [url(SPOTIFY_URL), limitFlat(20, 50, 1), cacheParam()] },
  { tool: "spotify_podcast_episodes", name: "Spotify Podcast Episodes", path: "/v1/spotify/podcast-episodes", credits: 23, summary: "List episodes for a Spotify podcast/show.", params: [url(SPOTIFY_URL), limit(20, 50)] },
];

const SOUNDCLOUD: Omit<Endpoint, "platform">[] = [
  { tool: "soundcloud_artist", name: "SoundCloud Artist", path: "/v1/soundcloud/artist", credits: 1, summary: "SoundCloud artist — bio, counts, badges, creator subscription tier.", params: [url(SC_PROFILE)] },
  { tool: "soundcloud_artist_tracks", name: "SoundCloud Artist Tracks", path: "/v1/soundcloud/artist-tracks", credits: 28, summary: "Tracks from a SoundCloud artist profile, with cursor pagination (nextCursor + hasMore).", params: [url(SC_PROFILE), limit(20, 100), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." }] },
  { tool: "soundcloud_track", name: "SoundCloud Track", path: "/v1/soundcloud/track", credits: 1, summary: "SoundCloud track metadata and engagement stats.", params: [url(SC_TRACK)] },
];

const LINKTREE: Omit<Endpoint, "platform">[] = [
  { tool: "linktree_page", name: "Linktree Page", path: "/v1/linktree/page", credits: 1, summary: "Public Linktree profile links (incl. GROUP children), socials, email, verticals.", params: [url(LINKTREE_PROFILE)] },
];

const SNAPCHAT: Omit<Endpoint, "platform">[] = [
  { tool: "snapchat_user_profile", name: "Snapchat User Profile", path: "/v1/snapchat/user-profile", credits: 1, summary: "Public Snapchat profile — highlights with snap lists, Spotlight engagement, related accounts.", params: [url(SNAPCHAT_PROFILE)] },
];

const TRUTH_SOCIAL: Omit<Endpoint, "platform">[] = [
  {
    tool: "truth_social_profile",
    name: "Truth Social Profile",
    path: "/v1/truth-social/profile",
    credits: 1,
    summary:
      "Public Truth Social profile (bot/isPrivate/group, static media, emojis). Prominent accounts only — most others require auth.",
    params: [url(TRUTH_PROFILE)],
  },
  { tool: "truth_social_user_posts", name: "Truth Social User Posts", path: "/v1/truth-social/user-posts", credits: 17, summary: "Recent public posts from a Truth Social profile, with cursor pagination (nextCursor + hasMore).", params: [url(TRUTH_PROFILE), limit(20, 80), { name: "cursor", type: "string", required: false, description: "Pagination cursor. Leave empty for the first page; then pass the nextCursor value returned in the previous response." }] },
  { tool: "truth_social_post", name: "Truth Social Post", path: "/v1/truth-social/post", credits: 5, summary: "Truth Social post metadata, text, media and engagement.", params: [url(TRUTH_POST)] },
];

const KICK: Omit<Endpoint, "platform">[] = [
  { tool: "kick_clip", name: "Kick Clip", path: "/v1/kick/clip", credits: 1, summary: "Kick clip — creator vs channel, category, maturity, VOD; or recent channel clips.", params: [url(KICK_CLIP), limitFlat(30, 100, 1)] },
];

const AMAZON_SHOP_ENDPOINTS: Omit<Endpoint, "platform">[] = [
  {
    tool: "amazon_shop_page",
    name: "Amazon Shop Page",
    path: "/v1/amazon-shop/page",
    credits: 1,
    summary: "Amazon seller storefront products with price, badges, scrapedAt, and cursor pagination.",
    params: [
      url(AMAZON_SHOP),
      { name: "marketplace", type: "string", required: false, description: "Amazon marketplace code. Default US." },
      limit(20, 200),
      {
        name: "cursor",
        type: "string",
        required: false,
        description: "Pagination cursor from nextCursor (page or page:offset). Leave empty for the first page.",
      },
    ],
  },
];

const ACCOUNT: Omit<Endpoint, "platform">[] = [
  { tool: "account_balance", name: "Credit Balance", path: "/v1/account/balance", credits: 0, summary: "Get current Captapi credit balance and plan limits.", params: [] },
  {
    tool: "account_request_history",
    name: "Request History",
    path: "/v1/account/request-history",
    credits: 0,
    summary: "Live request log with requestId, creditsUsed, cacheHit. Filter by endpoint/statusCode/since/until. Free.",
    params: [
      limitFree(50, 500),
      { name: "endpoint", type: "string", required: false, description: "Exact Captapi path, e.g. /v1/instagram/basic-profile." },
      { name: "statusCode", type: "number", required: false, description: "HTTP status filter, e.g. 500." },
      { name: "since", type: "string", required: false, description: "Inclusive createdAt lower bound (ISO date or datetime)." },
      { name: "until", type: "string", required: false, description: "Exclusive createdAt upper bound (ISO date or datetime)." },
    ],
  },
  { tool: "account_daily_usage", name: "Daily Usage", path: "/v1/account/daily-usage", credits: 0, summary: "Daily request and credit usage summary.", params: [{ name: "days", type: "number", required: false, description: "Number of days to include. Default 30, max 365." }] },
  { tool: "account_most_used_routes", name: "Most Used Routes", path: "/v1/account/most-used-routes", credits: 0, summary: "Most used API routes by request count and credits.", params: [{ name: "days", type: "number", required: false, description: "Number of days to include. Default 30, max 365." }, limitFree(20, 100)] },
];

const UTILITIES: Omit<Endpoint, "platform">[] = [
  {
    tool: "analytics_post",
    name: "Post Analytics",
    path: "/v1/analytics/post",
    credits: 1,
    summary: "Unified metrics for one post across 11 platforms (auto-detect). engagementRateBasis + commentsIsApproximate/interactionsIsApproximate. Flat 1 credit.",
    params: [
      { name: "url", type: "string", required: true, description: "Post/video/reel URL from YouTube, TikTok, Instagram, Facebook, X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, or Rumble. Platform auto-detected — cross-platform URLs are expected. Not Kwai/Twitch/Spotify/Snapchat." },
      cacheParam(),
    ],
  },
  {
    tool: "analytics_compare",
    name: "Compare Analytics",
    path: "/v1/analytics/compare",
    credits: 1,
    summary: "Same analytics/post object per URL (up to 10). 1 credit per resolved URL; cache hits free. Mix platforms freely.",
    params: [
      { name: "urls", type: "string", required: true, description: "Comma-separated URLs (up to 10), any mix of the 11 Post Analytics platforms." },
      cacheParam(),
    ],
  },
  {
    tool: "video_transcript",
    name: "Video File Transcript",
    path: "/v1/video/transcript",
    credits: 1,
    summary: "POST multipart Whisper transcript. Returns language, durationSeconds, creditsCharged. 1 credit/min. Max 200MB/60min.",
    params: [
      { name: "file", type: "string", required: true, description: "Local path to video/audio — sent as multipart form field file (POST), not a query string." },
      { name: "language", type: "string", required: false, description: "ISO-639-1 Whisper language hint, e.g. en or tr." },
      { name: "translate", type: "boolean", required: false, description: "Translate speech to English when true." },
      { name: "timestampGranularity", type: "string", required: false, description: "segment (default) or word." },
    ],
  },
  {
    tool: "video_summarize",
    name: "Video File Summarizer",
    path: "/v1/video/summarize",
    credits: 2,
    summary: "POST multipart Whisper + AI summary PLUS full transcript. durationSeconds/creditsCharged. 1 credit/min + 1.",
    params: [
      { name: "file", type: "string", required: true, description: "Local path to video/audio — multipart form field file (POST), not a query string." },
      { name: "language", type: "string", required: false, description: "ISO-639-1 Whisper language hint." },
      { name: "translate", type: "boolean", required: false, description: "Translate speech to English when true." },
      { name: "timestampGranularity", type: "string", required: false, description: "segment (default) or word." },
    ],
  },
];

const KWAI: Omit<Endpoint, "platform">[] = [
  { tool: "kwai_profile", name: "Kwai Profile", path: "/v1/kwai/profile", credits: 1, summary: "Kwai profile — bio, counts, verification, and post privacy flags.", params: [url(KWAI_PROFILE)] },
  { tool: "kwai_user_posts", name: "Kwai User Posts", path: "/v1/kwai/user-posts", credits: 45, summary: "Recent Kwai videos from a profile.", params: [url(KWAI_PROFILE), limit(20, 200)] },
  { tool: "kwai_post", name: "Kwai Post", path: "/v1/kwai/post", credits: 17, summary: "Kwai post metadata and engagement.", params: [url(KWAI_POST)] },
];

const KOMI: Omit<Endpoint, "platform">[] = [
  { tool: "komi_page", name: "Komi Page", path: "/v1/komi/page", credits: 1, summary: "Komi page — id/displayName/bio, socials{} (incl. website), content LINK/PRODUCT rows with price/currency. Flat 1 credit.", params: [url(KOMI_PAGE), cacheParam()] },
];

const PILLAR: Omit<Endpoint, "platform">[] = [
  { tool: "pillar_page", name: "Pillar Page", path: "/v1/pillar/page", credits: 1, summary: "Pillar page — id/displayName/bio/location/email, socials{}, links[] with clicks, products[]. Flat 1 credit.", params: [url(PILLAR_PAGE), cacheParam()] },
];

const LINKBIO: Omit<Endpoint, "platform">[] = [
  { tool: "linkbio_page", name: "Linkbio Page", path: "/v1/linkbio/page", credits: 1, summary: "lnk.bio page — id, socials{} (often filled where SC is null), titled links[], website/email/whatsapp, other[]. Flat 1 credit.", params: [url(LINKBIO_PAGE), cacheParam()] },
];

const LINKME: Omit<Endpoint, "platform">[] = [
  { tool: "linkme_profile", name: "Linkme Profile", path: "/v1/linkme/profile", credits: 4, summary: "Public Linkme profile links and metadata.", params: [url(LINKME_PROFILE)] },
];

const FACEBOOK_AD_LIBRARY: Omit<Endpoint, "platform">[] = [
  {
    tool: "facebook_ad_library_search",
    name: "Facebook Ad Library Search",
    path: "/v1/ad-library/facebook/search",
    credits: 2,
    summary: "Search Meta/Facebook ads by keyword with status, media, date, and sort filters.",
    params: [
      q(),
      { name: "country", type: "string", required: false, description: "ISO country code. Default US." },
      limit(20, 200),
      { name: "status", type: "string", required: false, description: "ACTIVE (default), INACTIVE, or ALL." },
      { name: "media_type", type: "string", required: false, description: "ALL (default), IMAGE, VIDEO, MEME, IMAGE_AND_MEME, or NONE." },
      { name: "ad_type", type: "string", required: false, description: "all (default) or political_and_issue_ads." },
      { name: "search_type", type: "string", required: false, description: "keyword_unordered (default) or keyword_exact_phrase." },
      { name: "sort_by", type: "string", required: false, description: "total_impressions or relevancy_monthly_grouped." },
      { name: "start_date", type: "string", required: false, description: "Delivery start on/after YYYY-MM-DD." },
      { name: "end_date", type: "string", required: false, description: "Delivery start on/before YYYY-MM-DD." },
    ],
  },
  { tool: "facebook_ad_library_company_ads", name: "Facebook Company Ads", path: "/v1/ad-library/facebook/company-ads", credits: 2, summary: "Ads for a Facebook page or Meta Ad Library URL.", params: [url("Facebook page URL or Meta Ad Library URL."), { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(20, 200)] },
  { tool: "facebook_ad_library_search_companies", name: "Facebook Ad Library Search Companies", path: "/v1/ad-library/facebook/search-companies", credits: 2, summary: "Find advertisers/pages in the Meta Ad Library by name.", params: [q(), { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(20, 200)] },
  { tool: "facebook_ad_library_ad_details", name: "Facebook Ad Details", path: "/v1/ad-library/facebook/ad-details", credits: 2, summary: "Meta/Facebook ad details.", params: [url("Meta Ad Library ad URL.")] },
  { tool: "facebook_ad_library_ad_transcript", name: "Facebook Ad Transcript", path: "/v1/ad-library/facebook/ad-transcript", credits: 17, summary: "Extract creative text from a Meta/Facebook ad as transcript text.", params: [url("Meta Ad Library ad URL or ad ID.")] },
];

const TIKTOK_AD_LIBRARY: Omit<Endpoint, "platform">[] = [
  {
    tool: "tiktok_ad_library_search",
    name: "TikTok Ad Library Search",
    path: "/v1/ad-library/tiktok/search",
    credits: 2,
    summary: "EU DSA Ad Library search — match=any|all, matchedFrom/filteredOut, empty free, ~40s cap.",
    params: [
      q(),
      { name: "country", type: "string", required: false, description: "ISO country code. Default GB (US often empty)." },
      { name: "match", type: "string", required: false, description: 'Keyword mode: "any" (default) or "all".' },
      limit(20, 200),
    ],
  },
  {
    tool: "tiktok_ad_library_top_ads",
    name: "TikTok Creative Center Top Ads",
    path: "/v1/ad-library/tiktok/top-ads",
    credits: 20,
    summary: "Creative Center Top Ads — browser list XHR early-exit, 30–60s typical; flat 2 / ~1 Apify. Client timeout ≥120s.",
    params: [
      { name: "q", type: "string", required: false, description: "Optional keyword (substring). See match + matchedFrom." },
      { name: "match", type: "string", required: false, description: 'Keyword mode: "any" (default) or "all".' },
      { name: "country", type: "string", required: false, description: "ISO country code. Default US." },
      { name: "period", type: "number", required: false, description: "Lookback days: 7, 30, or 180. Default 30." },
      { name: "orderBy", type: "string", required: false, description: "for_you | likes | ctr | impressions | cost." },
      { name: "industry", type: "string", required: false, description: "Optional industry key or label." },
      { name: "objective", type: "string", required: false, description: "Optional campaign objective." },
      { name: "adFormat", type: "string", required: false, description: "spark | non_spark." },
      { name: "limit", type: "number", required: false, description: "Max items (default 20, max 100). Flat 2 native; Apify ~1/ad (min 2)." },
      { name: "cache", type: "boolean", required: false, description: "Serve from 24h cache when available (0 credits on hit)." },
    ],
  },
  { tool: "tiktok_ad_library_ad_details", name: "TikTok Ad Details", path: "/v1/ad-library/tiktok/ad-details", credits: 2, summary: "TikTok ad details by ad URL or ID.", params: [url("TikTok Ad Library URL or ad ID."), { name: "country", type: "string", required: false, description: "ISO country code. Default GB." }] },
];

const GOOGLE_AD_LIBRARY: Omit<Endpoint, "platform">[] = [
  { tool: "google_ad_library_company_ads", name: "Google Company Ads", path: "/v1/ad-library/google/company-ads", credits: 2, summary: "List Google Ads Transparency creatives for an advertiser (name, domain, or AR id) with media, cursor paging, and optional date filters. Public commercial ads only.", params: [{ name: "advertiser", type: "string", required: true, description: "Advertiser name, domain (e.g. nike.com), or AR id." }, { name: "country", type: "string", required: false, description: "ISO country / region code. Default US." }, { name: "region", type: "string", required: false, description: "Alias for country." }, { name: "start_date", type: "string", required: false, description: "YYYY-MM-DD overlap filter start." }, { name: "end_date", type: "string", required: false, description: "YYYY-MM-DD overlap filter end." }, { name: "cursor", type: "string", required: false, description: "Pagination cursor from nextCursor." }, { name: "limit", type: "number", required: false, description: "Max results per page (default 20, max 200)." }, { name: "cache", type: "boolean", required: false, description: "Serve from 24h cache when available." }] },
  { tool: "google_ad_library_ad_details", name: "Google Ad Details", path: "/v1/ad-library/google/ad-details", credits: 2, summary: "Google ad details by Transparency Center URL.", params: [{ name: "creative_id", type: "string", required: true, description: "Google Ads Transparency Center URL containing AR advertiser ID and CR creative ID." }, { name: "country", type: "string", required: false, description: "ISO country code. Default US." }] },
  { tool: "google_ad_library_advertiser_search", name: "Google Advertiser Search", path: "/v1/ad-library/google/advertiser-search", credits: 1, summary: "Search Google Ads advertisers.", params: [q(), { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(10, 50)] },
];

const LINKEDIN_AD_LIBRARY: Omit<Endpoint, "platform">[] = [
  {
    tool: "linkedin_ad_library_search_ads",
    name: "LinkedIn Ad Library Search",
    path: "/v1/ad-library/linkedin/search-ads",
    credits: 2,
    summary: "LinkedIn Ad Library — targeting{}, ISO dates, impressions, CTA, cursor pagination.",
    params: [
      { name: "q", type: "string", required: false, description: "Advertiser / account owner (min 2 when used). Or use keyword/companyId." },
      { name: "keyword", type: "string", required: false, description: "Optional keyword filter on ad copy." },
      { name: "companyId", type: "string", required: false, description: "LinkedIn numeric company id." },
      { name: "country", type: "string", required: false, description: "ISO country code. Default US." },
      { name: "countries", type: "string", required: false, description: "Comma-separated ISO codes (e.g. US,CA,MX)." },
      { name: "startDate", type: "string", required: false, description: "YYYY-MM-DD custom range start (with endDate)." },
      { name: "endDate", type: "string", required: false, description: "YYYY-MM-DD custom range end (with startDate)." },
      { name: "cursor", type: "string", required: false, description: "Pagination token from nextCursor/paginationToken." },
      limit(20, 200),
    ],
  },
  { tool: "linkedin_ad_library_ad_details", name: "LinkedIn Ad Details", path: "/v1/ad-library/linkedin/ad-details", credits: 2, summary: "LinkedIn ad details by URL or ID.", params: [url("LinkedIn Ad Library URL or ad ID.")] },
];

function withPlatform(
  list: Omit<Endpoint, "platform">[],
  platform: Platform,
): Endpoint[] {
  // Every data endpoint accepts optional cache (default false = always fresh);
  // account + utilities manage cache (or skip it) explicitly per endpoint.
  const addCache = platform !== "account" && platform !== "utilities";
  return list.map((e) => ({
    ...e,
    platform,
    params:
      addCache && !e.params.some((p) => p.name === "cache")
        ? [...e.params, cacheParam()]
        : e.params,
  }));
}

export const ENDPOINTS: Endpoint[] = [
  ...withPlatform(YOUTUBE, "youtube"),
  ...withPlatform(TIKTOK, "tiktok"),
  ...withPlatform(INSTAGRAM, "instagram"),
  ...withPlatform(FACEBOOK, "facebook"),
  ...withPlatform(TWITTER, "twitter"),
  ...withPlatform(REDDIT, "reddit"),
  ...withPlatform(THREADS, "threads"),
  ...withPlatform(BLUESKY, "bluesky"),
  ...withPlatform(PINTEREST, "pinterest"),
  ...withPlatform(LINKEDIN, "linkedin"),
  ...withPlatform(RUMBLE, "rumble"),
  ...withPlatform(TIKTOK_SHOP, "tiktok_shop"),
  ...withPlatform(FACEBOOK_MARKETPLACE, "facebook_marketplace"),
  ...withPlatform(FACEBOOK_EVENTS, "facebook_events"),
  ...withPlatform(FACEBOOK_AD_LIBRARY, "facebook_ad_library"),
  ...withPlatform(TIKTOK_AD_LIBRARY, "tiktok_ad_library"),
  ...withPlatform(GOOGLE_AD_LIBRARY, "google_ad_library"),
  ...withPlatform(LINKEDIN_AD_LIBRARY, "linkedin_ad_library"),
  ...withPlatform(AMAZON_SHOP_ENDPOINTS, "amazon_shop"),
  ...withPlatform(GITHUB, "github"),
  ...withPlatform(TWITCH, "twitch"),
  ...withPlatform(SPOTIFY, "spotify"),
  ...withPlatform(SOUNDCLOUD, "soundcloud"),
  ...withPlatform(LINKTREE, "linktree"),
  ...withPlatform(SNAPCHAT, "snapchat"),
  ...withPlatform(TRUTH_SOCIAL, "truth_social"),
  ...withPlatform(KICK, "kick"),
  ...withPlatform(ACCOUNT, "account"),
  ...withPlatform(UTILITIES, "utilities"),
  ...withPlatform(KWAI, "kwai"),
  ...withPlatform(KOMI, "komi"),
  ...withPlatform(PILLAR, "pillar"),
  ...withPlatform(LINKBIO, "linkbio"),
  ...withPlatform(LINKME, "linkme"),
];

/** A concise, agent-facing description (summary + cost) for an endpoint. */
export function describe(e: Endpoint): string {
  return `${e.summary} Costs ~${e.credits} credit${e.credits === 1 ? "" : "s"}; pass cache=true for a free 24h cache hit (default always fresh); failures are never charged.`;
}
