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
  | "github"
  | "ad_library"
  | "google"
  | "twitch"
  | "spotify"
  | "soundcloud"
  | "linktree"
  | "snapchat"
  | "truth_social"
  | "kick"
  | "amazon_shop"
  | "age_gender"
  | "account"
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
const commentId = (): ToolParam => ({
  name: "comment_id",
  type: "string",
  required: true,
  description: "ID of the parent comment to fetch replies for (from the comments endpoint).",
});

const YT_VIDEO = "Public YouTube video URL, e.g. https://youtube.com/watch?v=ID. Not a TikTok/Instagram/Facebook URL.";
const YT_SHORTS = "Public YouTube Shorts URL, e.g. https://youtube.com/shorts/ID. Not a TikTok/Instagram/Facebook URL.";
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
const AMAZON_SHOP = "Amazon seller storefront URL, seller profile URL, or seller ID.";
const KWAI_PROFILE = "Kwai/Kuaishou profile URL or user ID.";
const KWAI_POST = "Kwai/Kuaishou post URL or video/photo ID.";
const KOMI_PAGE = "Komi page URL or username.";
const PILLAR_PAGE = "Pillar page URL or username.";
const LINKBIO_PAGE = "Linkbio page URL or username.";
const LINKME_PROFILE = "Linkme profile URL or username.";

const YOUTUBE: Omit<Endpoint, "platform">[] = [
  { tool: "youtube_transcript", name: "YouTube Transcript", path: "/v1/youtube/transcript", credits: 2, summary: "Extract the full timestamped transcript of a YouTube video.", params: [url(YT_VIDEO), language()] },
  { tool: "youtube_summarize", name: "YouTube Summarizer", path: "/v1/youtube/summarize", credits: 4, summary: "AI summary (key points, topics, sentiment) of a YouTube video.", params: [url(YT_VIDEO), language()] },
  { tool: "youtube_video_details", name: "YouTube Video Details", path: "/v1/youtube/video-details", credits: 1, summary: "Metadata + engagement stats for a YouTube video.", params: [url(YT_VIDEO)] },
  { tool: "youtube_comments", name: "YouTube Comments", path: "/v1/youtube/comments", credits: 20, summary: "Comments on a YouTube video.", params: [url(YT_VIDEO), limit(50, 500)] },
  { tool: "youtube_channel_details", name: "YouTube Channel Details", path: "/v1/youtube/channel-details", credits: 1, summary: "Channel info & subscriber/stats for a YouTube channel.", params: [url(YT_CHANNEL)] },
  { tool: "youtube_search", name: "YouTube Search", path: "/v1/youtube/search", credits: 20, summary: "Search YouTube videos by keyword.", params: [q(), limit(20, 200)] },
  { tool: "youtube_channel_videos", name: "YouTube Channel Videos", path: "/v1/youtube/channel-videos", credits: 20, summary: "List a channel's uploaded videos.", params: [url(YT_CHANNEL), limit(20, 200), fastRss()] },
  { tool: "youtube_playlist_videos", name: "YouTube Playlist Videos", path: "/v1/youtube/playlist-videos", credits: 50, summary: "List videos in a YouTube playlist.", params: [url("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."), limit(50, 500), fastRss()] },
  { tool: "youtube_playlist", name: "YouTube Playlist", path: "/v1/youtube/playlist", credits: 50, summary: "Playlist metadata plus videos from a YouTube playlist.", params: [url("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."), limit(50, 500), fastRss()] },
  { tool: "youtube_video_download", name: "YouTube Video Download", path: "/v1/youtube/video-download", credits: 3, summary: "Direct download URLs for a YouTube video.", params: [url(YT_VIDEO)] },
  { tool: "youtube_shorts_transcript", name: "YouTube Shorts Transcript", path: "/v1/youtube/shorts/transcript", credits: 2, summary: "Transcript of a YouTube Short.", params: [url(YT_SHORTS), language()] },
  { tool: "youtube_shorts_summarize", name: "YouTube Shorts Summarizer", path: "/v1/youtube/shorts/summarize", credits: 4, summary: "AI summary of a YouTube Short.", params: [url(YT_SHORTS), language()] },
  { tool: "youtube_shorts_details", name: "YouTube Shorts Stats", path: "/v1/youtube/shorts/video-details", credits: 1, summary: "Metadata + stats for a YouTube Short.", params: [url(YT_SHORTS)] },
  { tool: "youtube_shorts_comments", name: "YouTube Shorts Comments", path: "/v1/youtube/shorts/comments", credits: 20, summary: "Comments on a YouTube Short.", params: [url(YT_SHORTS), limit(50, 500)] },
  { tool: "youtube_channel_shorts", name: "YouTube Channel Shorts", path: "/v1/youtube/channel-shorts", credits: 20, summary: "List a channel's Shorts.", params: [url(YT_CHANNEL), limit(20, 200)] },
  { tool: "youtube_trending_shorts", name: "YouTube Trending Shorts", path: "/v1/youtube/trending-shorts", credits: 28, summary: "Discover trending YouTube Shorts by seed keyword.", params: [{ name: "q", type: "string", required: false, description: "Seed keyword for trending Shorts. Default trending." }, limit(20, 100)] },
  { tool: "youtube_channel_streams", name: "YouTube Channel Streams", path: "/v1/youtube/channel-streams", credits: 20, summary: "List a channel's live/past streams.", params: [url(YT_CHANNEL), limit(20, 200)] },
  { tool: "youtube_hashtag_search", name: "YouTube Hashtag Search", path: "/v1/youtube/hashtag-search", credits: 20, summary: "Search YouTube videos by hashtag.", params: [q("Hashtag with or without the # (min 2 chars)."), limit(20, 200)] },
  { tool: "youtube_comment_replies", name: "YouTube Comment Replies", path: "/v1/youtube/comment-replies", credits: 20, summary: "Replies to a specific YouTube comment.", params: [url(YT_VIDEO), commentId(), limit(50, 500)] },
  { tool: "youtube_channel_playlists", name: "YouTube Channel Playlists", path: "/v1/youtube/channel-playlists", credits: 20, summary: "List a channel's playlists.", params: [url(YT_CHANNEL), limit(20, 200)] },
  { tool: "youtube_community_posts", name: "YouTube Community Posts", path: "/v1/youtube/community-posts", credits: 10, summary: "List a channel's community (posts) tab.", params: [url(YT_CHANNEL), limit(20, 200)] },
  { tool: "youtube_community_post_details", name: "YouTube Community Post Details", path: "/v1/youtube/community-post-details", credits: 7, summary: "Details for a single YouTube community post.", params: [url("YouTube community post URL.")] },
  { tool: "youtube_video_sponsors", name: "YouTube Video Sponsors", path: "/v1/youtube/video-sponsors", credits: 1, summary: "Sponsor / self-promo / interaction segments in a YouTube video (via SponsorBlock).", params: [url(YT_VIDEO)] },
];

const TIKTOK: Omit<Endpoint, "platform">[] = [
  { tool: "tiktok_transcript", name: "TikTok Transcript", path: "/v1/tiktok/transcript", credits: 2, summary: "Transcript of a TikTok video (via captions).", params: [url(TT_VIDEO), language()] },
  { tool: "tiktok_summarize", name: "TikTok Summarizer", path: "/v1/tiktok/summarize", credits: 4, summary: "AI summary of a TikTok video.", params: [url(TT_VIDEO)] },
  { tool: "tiktok_video_details", name: "TikTok Video Details", path: "/v1/tiktok/video-details", credits: 1, summary: "Metadata + stats for a TikTok video.", params: [url(TT_VIDEO)] },
  { tool: "tiktok_comments", name: "TikTok Comments", path: "/v1/tiktok/comments", credits: 10, summary: "Comments on a TikTok video.", params: [url(TT_VIDEO), limit(50, 500)] },
  { tool: "tiktok_channel_details", name: "TikTok Channel Details", path: "/v1/tiktok/channel-details", credits: 1, summary: "Profile info & stats for a TikTok user.", params: [url(TT_PROFILE)] },
  { tool: "tiktok_profile_region", name: "TikTok Profile Region", path: "/v1/tiktok/profile-region", credits: 7, summary: "Region and language signals for a TikTok profile.", params: [url(TT_PROFILE)] },
  { tool: "tiktok_audience_demographics", name: "TikTok Audience Demographics", path: "/v1/tiktok/audience-demographics", credits: 7, summary: "Audience and demographic signals for a TikTok profile.", params: [url(TT_PROFILE)] },
  { tool: "tiktok_search", name: "TikTok Search", path: "/v1/tiktok/search", credits: 14, summary: "Search TikTok videos by keyword/hashtag.", params: [q(), limit(20, 200)] },
  { tool: "tiktok_search_suggestions", name: "TikTok Search Suggestions", path: "/v1/tiktok/search-suggestions", credits: 28, summary: "TikTok search/autocomplete suggestions for a seed keyword.", params: [q("Seed keyword for autocomplete suggestions."), { name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }, language(), limit(20, 100)] },
  { tool: "tiktok_video_download", name: "TikTok Video Download", path: "/v1/tiktok/video-download", credits: 3, summary: "No-watermark download URL for a TikTok video.", params: [url(TT_VIDEO)] },
  { tool: "tiktok_channel_posts", name: "TikTok Channel Posts", path: "/v1/tiktok/channel-posts", credits: 14, summary: "Latest posts from a TikTok profile.", params: [url(TT_PROFILE), limit(20, 200)] },
  { tool: "tiktok_comment_replies", name: "TikTok Comment Replies", path: "/v1/tiktok/comment-replies", credits: 50, summary: "Replies to a specific TikTok comment.", params: [url(TT_VIDEO), commentId(), limit(50, 500)] },
  { tool: "tiktok_user_followers", name: "TikTok User Followers", path: "/v1/tiktok/user-followers", credits: 20, summary: "List a TikTok user's followers.", params: [url(TT_PROFILE), limit(50, 500)] },
  { tool: "tiktok_user_followings", name: "TikTok User Followings", path: "/v1/tiktok/user-followings", credits: 20, summary: "List who a TikTok user follows.", params: [url(TT_PROFILE), limit(50, 500)] },
  { tool: "tiktok_music_posts", name: "TikTok Music Posts", path: "/v1/tiktok/music-posts", credits: 32, summary: "Posts using a specific TikTok sound/music.", params: [url(TT_MUSIC), limit(20, 200)] },
  { tool: "tiktok_hashtag_search", name: "TikTok Hashtag Search", path: "/v1/tiktok/hashtag-search", credits: 14, summary: "Search TikTok videos by hashtag.", params: [q("Hashtag with or without the # (min 2 chars)."), limit(20, 200)] },
  { tool: "tiktok_top_search", name: "TikTok Top Search", path: "/v1/tiktok/top-search", credits: 14, summary: "Top mixed TikTok results for a keyword.", params: [q(), limit(20, 200)] },
  { tool: "tiktok_user_search", name: "TikTok User Search", path: "/v1/tiktok/user-search", credits: 8, summary: "Search TikTok users/creators by keyword.", params: [q(), limit(20, 100)] },
  { tool: "tiktok_song_details", name: "TikTok Song Details", path: "/v1/tiktok/song-details", credits: 2, summary: "Details of a TikTok sound/song.", params: [url(TT_MUSIC)] },
  { tool: "tiktok_trending_feed", name: "TikTok Trending Feed", path: "/v1/tiktok/trending-feed", credits: 14, summary: "TikTok trending (For You) videos by region.", params: [{ name: "country", type: "string", required: false, description: "Two-letter ISO country code, e.g. US, GB, TR. Default US." }, limit(20, 200)] },
  { tool: "tiktok_popular_hashtags", name: "TikTok Popular Hashtags", path: "/v1/tiktok/popular-hashtags", credits: 14, summary: "Trending TikTok hashtags for a topic/keyword.", params: [{ name: "query", type: "string", required: false, description: 'Topic or keyword to discover trending hashtags for. Default "trending".' }, limit(20, 100)] },
  { tool: "tiktok_live", name: "TikTok Live", path: "/v1/tiktok/live", credits: 1, summary: "Live status & room info for a TikTok creator.", params: [url(TT_PROFILE)] },
  { tool: "tiktok_live_info", name: "TikTok Live Info", path: "/v1/tiktok/live-info", credits: 7, summary: "Live room details for a TikTok creator.", params: [url(TT_PROFILE)] },
  { tool: "tiktok_popular_creators", name: "TikTok Popular Creators", path: "/v1/tiktok/popular-creators", credits: 28, summary: "Popular TikTok creators by country and ranking mode.", params: [{ name: "country", type: "string", required: false, description: "Two-letter ISO country code. Default US." }, { name: "sort", type: "string", required: false, description: "follower, engagement, or popularity. Default follower." }, { name: "follower_count", type: "string", required: false, description: "Optional range: 10k-100k, 100k-1m, 1m-10m, >10m." }, limit(20, 100)] },
];

const INSTAGRAM: Omit<Endpoint, "platform">[] = [
  { tool: "instagram_transcript", name: "Instagram Transcript", path: "/v1/instagram/transcript", credits: 2, summary: "Transcript of an Instagram Reel.", params: [url(IG_REEL), language()] },
  { tool: "instagram_summarize", name: "Instagram Summarizer", path: "/v1/instagram/summarize", credits: 4, summary: "AI summary of an Instagram Reel.", params: [url(IG_REEL)] },
  { tool: "instagram_details", name: "Instagram Details", path: "/v1/instagram/details", credits: 1, summary: "Details for an Instagram post or reel.", params: [url(IG_POST)] },
  { tool: "instagram_comments", name: "Instagram Comments", path: "/v1/instagram/comments", credits: 45, summary: "Comments on an Instagram post or reel.", params: [url(IG_POST), limit(50, 500)] },
  { tool: "instagram_channel_details", name: "Instagram Channel Details", path: "/v1/instagram/channel-details", credits: 1, summary: "Profile info & stats for an Instagram account.", params: [url(IG_PROFILE)] },
  { tool: "instagram_channel_posts", name: "Instagram Channel Posts", path: "/v1/instagram/channel-posts", credits: 12, summary: "Latest posts from an Instagram profile.", params: [url(IG_PROFILE), limit(20, 200)] },
  { tool: "instagram_channel_reels", name: "Instagram Channel Reels", path: "/v1/instagram/channel-reels", credits: 12, summary: "Latest Reels from an Instagram profile.", params: [url(IG_PROFILE), limit(20, 200)] },
  { tool: "instagram_reels_search", name: "Instagram Reels Search", path: "/v1/instagram/reels-search", credits: 12, summary: "Search Instagram Reels by hashtag/keyword.", params: [q("Hashtag (without #) or keyword (min 2 chars)."), limit(20, 200)] },
  { tool: "instagram_trending_reels", name: "Instagram Trending Reels", path: "/v1/instagram/trending-reels", credits: 28, summary: "Trending Instagram Reels / Explore posts by country.", params: [{ name: "country", type: "string", required: false, description: "Country name for Explore localization. Default United States." }, limit(20, 200)] },
  { tool: "instagram_video_download", name: "Instagram Video Download", path: "/v1/instagram/video-download", credits: 3, summary: "Direct video URL for an Instagram Reel.", params: [url(IG_REEL)] },
  { tool: "instagram_tagged_posts", name: "Instagram Tagged Posts", path: "/v1/instagram/tagged-posts", credits: 18, summary: "Posts an Instagram user is tagged in.", params: [url(IG_PROFILE), limit(20, 200)] },
  { tool: "instagram_music_posts", name: "Instagram Music Posts", path: "/v1/instagram/music-posts", credits: 18, summary: "Posts/Reels using an Instagram audio.", params: [url("Instagram audio/music page URL."), limit(20, 200)] },
  { tool: "instagram_reels_by_audio_id", name: "Instagram Reels By Audio ID", path: "/v1/instagram/reels-by-audio-id", credits: 28, summary: "Posts/Reels using an Instagram audio ID.", params: [{ name: "audio_id", type: "string", required: true, description: "Instagram audio/music ID or full audio URL." }, limit(20, 200)] },
  { tool: "instagram_hashtag_search", name: "Instagram Hashtag Search", path: "/v1/instagram/hashtag-search", credits: 12, summary: "Search Instagram posts by hashtag.", params: [q("Hashtag without the # (min 2 chars)."), limit(20, 200)] },
  { tool: "instagram_profile_search", name: "Instagram Profile Search", path: "/v1/instagram/profile-search", credits: 12, summary: "Search Instagram profiles by keyword.", params: [q(), limit(20, 100)] },
  { tool: "instagram_story_highlights", name: "Instagram Story Highlights", path: "/v1/instagram/story-highlights", credits: 5, summary: "List a profile's story highlight covers.", params: [url(IG_PROFILE)] },
  { tool: "instagram_highlights_details", name: "Instagram Highlights Details", path: "/v1/instagram/highlights-details", credits: 9, summary: "Items inside a profile's story highlights.", params: [url(IG_PROFILE), { name: "limit", type: "number", required: false, description: "Max highlights to expand. Default 10, max 50." }] },
  { tool: "instagram_embed", name: "Instagram Embed", path: "/v1/instagram/embed", credits: 1, summary: "Embed HTML for an Instagram post/reel.", params: [url(IG_POST)] },
  { tool: "instagram_basic_profile", name: "Instagram Basic Profile", path: "/v1/instagram/basic-profile", credits: 1, summary: "Lightweight Instagram profile lookup (core fields).", params: [url(IG_PROFILE)] },
];

const FACEBOOK: Omit<Endpoint, "platform">[] = [
  { tool: "facebook_details", name: "Facebook Details", path: "/v1/facebook/details", credits: 1, summary: "Details for a Facebook video or post.", params: [url(FB_VIDEO)] },
  { tool: "facebook_transcript", name: "Facebook Transcript", path: "/v1/facebook/transcript", credits: 2, summary: "Transcript of a Facebook video.", params: [url(FB_VIDEO)] },
  { tool: "facebook_summarize", name: "Facebook Summarizer", path: "/v1/facebook/summarize", credits: 4, summary: "AI summary of a Facebook video or post.", params: [url(FB_VIDEO)] },
  { tool: "facebook_comments", name: "Facebook Comments", path: "/v1/facebook/comments", credits: 30, summary: "Comments on a Facebook post.", params: [url(FB_VIDEO), limit(50, 500)] },
  { tool: "facebook_page_details", name: "Facebook Page Details", path: "/v1/facebook/page-details", credits: 1, summary: "Info & stats for a Facebook page.", params: [url("Facebook page URL, e.g. https://facebook.com/PageName.")] },
  { tool: "facebook_profile_posts", name: "Facebook Profile Posts", path: "/v1/facebook/profile-posts", credits: 12, summary: "Latest posts from a Facebook profile/page.", params: [url("Facebook profile or page URL."), limit(20, 200)] },
  { tool: "facebook_profile_reels", name: "Facebook Profile Reels", path: "/v1/facebook/profile-reels", credits: 36, summary: "Latest Reels from a Facebook profile/page.", params: [url("Facebook profile or page URL."), limit(20, 200)] },
  { tool: "facebook_group_posts", name: "Facebook Group Posts", path: "/v1/facebook/group-posts", credits: 12, summary: "Posts from a public Facebook group.", params: [url("Public Facebook group URL, e.g. https://facebook.com/groups/ID."), limit(20, 200)] },
  { tool: "facebook_comment_replies", name: "Facebook Comment Replies", path: "/v1/facebook/comment-replies", credits: 30, summary: "Replies to a specific Facebook comment.", params: [url("Facebook post URL the comment belongs to."), commentId(), limit(50, 500)] },
  { tool: "facebook_marketplace_search", name: "Facebook Marketplace Search", path: "/v1/facebook/marketplace-search", credits: 28, summary: "Search Facebook Marketplace listings by keyword and location.", params: [q("Product or keyword to search for (min 2 chars)."), { name: "location", type: "string", required: true, description: "City or place name, e.g. 'Austin, TX'." }, limit(20, 200), { name: "details", type: "string", required: false, description: "Set true to fetch full description, photos and coordinates per listing (slower, costs more)." }] },
  { tool: "facebook_marketplace_location_search", name: "Facebook Marketplace Location Search", path: "/v1/facebook/marketplace-location-search", credits: 17, summary: "Find Facebook Marketplace location candidates for a city or place query.", params: [q("City/place search query, e.g. Austin."), limit(10, 50)] },
  { tool: "facebook_event_search", name: "Facebook Event Search", path: "/v1/facebook/event-search", credits: 40, summary: "Search Facebook events by topic and/or location.", params: [q("Topic and/or place, e.g. 'comedy Chicago' (min 2 chars)."), limit(20, 200)] },
  { tool: "facebook_event_details", name: "Facebook Event Details", path: "/v1/facebook/event-details", credits: 2, summary: "Details for a Facebook event (date, location, attendees, tickets).", params: [url("Facebook event URL, e.g. https://facebook.com/events/ID.")] },
  { tool: "facebook_profile_photos", name: "Facebook Profile Photos", path: "/v1/facebook/profile-photos", credits: 12, summary: "Photos from a Facebook profile or page.", params: [url("Facebook profile or page URL."), limit(20, 200)] },
  { tool: "facebook_profile_events", name: "Facebook Profile Events", path: "/v1/facebook/profile-events", credits: 40, summary: "Events from a Facebook profile or page.", params: [url("Facebook profile or page URL."), limit(20, 200)] },
  { tool: "facebook_marketplace_item", name: "Facebook Marketplace Item", path: "/v1/facebook/marketplace-item", credits: 17, summary: "Details for a single Facebook Marketplace listing.", params: [url("Facebook Marketplace item URL.")] },
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
  { tool: "twitter_transcript", name: "Twitter/X Transcript", path: "/v1/twitter/transcript", credits: 7, summary: "Extract tweet text as transcript text.", params: [url(TW_TWEET)] },
  { tool: "twitter_profile", name: "Twitter/X Profile", path: "/v1/twitter/profile", credits: 1, summary: "Profile info & stats for a Twitter/X account.", params: [url(TW_PROFILE)] },
  { tool: "twitter_user_tweets", name: "Twitter/X User Tweets", path: "/v1/twitter/user-tweets", credits: 14, summary: "Recent tweets from a Twitter/X profile.", params: [url(TW_PROFILE), limit(20, 200)] },
  { tool: "twitter_search", name: "Twitter/X Search", path: "/v1/twitter/search", credits: 14, summary: "Search tweets by keyword.", params: [q(), limit(20, 200)] },
  { tool: "twitter_community", name: "Twitter/X Community", path: "/v1/twitter/community", credits: 1, summary: "Details for an X (Twitter) community.", params: [url(TW_COMMUNITY)] },
  { tool: "twitter_community_tweets", name: "Twitter/X Community Tweets", path: "/v1/twitter/community-tweets", credits: 18, summary: "Tweets posted in an X community.", params: [url(TW_COMMUNITY), limit(25, 200)] },
];

const REDDIT: Omit<Endpoint, "platform">[] = [
  { tool: "reddit_subreddit_posts", name: "Reddit Subreddit Posts", path: "/v1/reddit/subreddit-posts", credits: 10, summary: "Recent posts in a subreddit.", params: [url(RD_SUB), limit(25, 200)] },
  { tool: "reddit_post_details", name: "Reddit Post Details", path: "/v1/reddit/post-details", credits: 1, summary: "Metadata + stats for a Reddit post.", params: [url(RD_POST)] },
  { tool: "reddit_post_comments", name: "Reddit Post Comments", path: "/v1/reddit/post-comments", credits: 20, summary: "Comments on a Reddit post.", params: [url(RD_POST), limit(50, 500)] },
  { tool: "reddit_post_transcript", name: "Reddit Post Transcript", path: "/v1/reddit/post-transcript", credits: 20, summary: "Extract Reddit post text and top comments as a discussion transcript.", params: [url(RD_POST), limit(50, 200)] },
  { tool: "reddit_search", name: "Reddit Search", path: "/v1/reddit/search", credits: 10, summary: "Search Reddit posts by keyword.", params: [q(), limit(25, 200)] },
  { tool: "reddit_subreddit_details", name: "Reddit Subreddit Details", path: "/v1/reddit/subreddit-details", credits: 1, summary: "Info & member stats for a subreddit.", params: [url(RD_SUB)] },
  { tool: "reddit_subreddit_search", name: "Reddit Subreddit Search", path: "/v1/reddit/subreddit-search", credits: 10, summary: "Search posts within a specific subreddit.", params: [url(RD_SUB), q(), limit(25, 200)] },
];

const THREADS: Omit<Endpoint, "platform">[] = [
  { tool: "threads_profile", name: "Threads Profile", path: "/v1/threads/profile", credits: 1, summary: "Profile info & stats for a Threads account.", params: [url(TH_PROFILE)] },
  { tool: "threads_user_posts", name: "Threads User Posts", path: "/v1/threads/user-posts", credits: 14, summary: "Recent posts from a Threads profile.", params: [url(TH_PROFILE), limit(20, 100)] },
  { tool: "threads_post_details", name: "Threads Post Details", path: "/v1/threads/post-details", credits: 1, summary: "Metadata + engagement for a Threads post.", params: [url(TH_POST)] },
  { tool: "threads_search", name: "Threads Search", path: "/v1/threads/search", credits: 18, summary: "Search Threads posts by keyword.", params: [q(), limit(25, 200)] },
  { tool: "threads_search_users", name: "Threads Search Users", path: "/v1/threads/search-users", credits: 14, summary: "Find Threads users matching a keyword.", params: [q(), limit(20, 100)] },
];

const BLUESKY: Omit<Endpoint, "platform">[] = [
  { tool: "bluesky_profile", name: "Bluesky Profile", path: "/v1/bluesky/profile", credits: 1, summary: "Profile info & stats for a Bluesky account.", params: [url(BS_PROFILE)] },
  { tool: "bluesky_user_posts", name: "Bluesky User Posts", path: "/v1/bluesky/user-posts", credits: 3, summary: "Recent posts from a Bluesky profile.", params: [url(BS_PROFILE), limit(25, 100)] },
  { tool: "bluesky_post_details", name: "Bluesky Post Details", path: "/v1/bluesky/post-details", credits: 1, summary: "Metadata + engagement for a Bluesky post.", params: [url(BS_POST)] },
];

const PINTEREST: Omit<Endpoint, "platform">[] = [
  { tool: "pinterest_pin_details", name: "Pinterest Pin Details", path: "/v1/pinterest/pin-details", credits: 1, summary: "Metadata + saves for a Pinterest pin.", params: [url(PIN_PIN)] },
  { tool: "pinterest_user_pins", name: "Pinterest User Pins", path: "/v1/pinterest/user-pins", credits: 13, summary: "Pins from a Pinterest profile.", params: [url(PIN_PROFILE), limit(25, 200)] },
  { tool: "pinterest_search", name: "Pinterest Search", path: "/v1/pinterest/search", credits: 13, summary: "Search Pinterest pins by keyword.", params: [q(), limit(25, 200)] },
  { tool: "pinterest_board", name: "Pinterest Board", path: "/v1/pinterest/board", credits: 13, summary: "List pins inside a Pinterest board.", params: [url(PIN_BOARD), limit(25, 200)] },
  { tool: "pinterest_user_boards", name: "Pinterest User Boards", path: "/v1/pinterest/user-boards", credits: 13, summary: "List the boards on a Pinterest profile.", params: [url(PIN_PROFILE), limit(25, 200)] },
];

const LINKEDIN: Omit<Endpoint, "platform">[] = [
  { tool: "linkedin_profile", name: "LinkedIn Profile", path: "/v1/linkedin/profile", credits: 2, summary: "Public LinkedIn person profile details.", params: [url(LI_PROFILE)] },
  { tool: "linkedin_company", name: "LinkedIn Company", path: "/v1/linkedin/company", credits: 2, summary: "Public LinkedIn company page details.", params: [url(LI_COMPANY)] },
  { tool: "linkedin_post_details", name: "LinkedIn Post Details", path: "/v1/linkedin/post-details", credits: 1, summary: "Metadata + engagement for a LinkedIn post.", params: [url(LI_POST)] },
  { tool: "linkedin_post_transcript", name: "LinkedIn Post Transcript", path: "/v1/linkedin/post-transcript", credits: 7, summary: "Extract post text as a transcript for a LinkedIn post.", params: [url(LI_POST)] },
  { tool: "linkedin_company_posts", name: "LinkedIn Company Posts", path: "/v1/linkedin/company-posts", credits: 16, summary: "Recent public posts from a LinkedIn company page.", params: [url(LI_COMPANY), limit(20, 100)] },
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
  { tool: "tiktok_shop_products", name: "TikTok Shop Products", path: "/v1/tiktok-shop/shop-products", credits: 56, summary: "List products from a TikTok Shop store.", params: [url("TikTok Shop store URL."), limit(20, 200)] },
  { tool: "tiktok_shop_product_details", name: "TikTok Shop Product Details", path: "/v1/tiktok-shop/product-details", credits: 14, summary: "Full TikTok Shop product details, seller and price metadata.", params: [url("TikTok Shop product URL.")] },
  { tool: "tiktok_shop_product_reviews", name: "TikTok Shop Product Reviews", path: "/v1/tiktok-shop/product-reviews", credits: 45, summary: "Customer reviews for a TikTok Shop product.", params: [url("TikTok Shop product URL."), limit(20, 200)] },
  { tool: "tiktok_shop_user_showcase", name: "TikTok Shop User Showcase", path: "/v1/tiktok-shop/user-showcase", credits: 45, summary: "Products promoted in a TikTok creator showcase.", params: [{ name: "username", type: "string", required: true, description: "TikTok username with or without @." }, limit(20, 200)] },
];

const GITHUB: Omit<Endpoint, "platform">[] = [
  { tool: "github_user", name: "GitHub User", path: "/v1/github/user", credits: 3, summary: "Public GitHub user profile details.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }] },
  { tool: "github_repositories", name: "GitHub Repositories", path: "/v1/github/repositories", credits: 12, summary: "List a GitHub user's repositories.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, limit(30, 100)] },
  { tool: "github_repository", name: "GitHub Repository", path: "/v1/github/repository", credits: 3, summary: "Repository details, stars, forks and metadata.", params: [{ name: "repo", type: "string", required: true, description: "Repository URL or owner/name." }] },
  { tool: "github_pull_requests", name: "GitHub Pull Requests", path: "/v1/github/pull-requests", credits: 12, summary: "List repository pull requests.", params: [{ name: "repo", type: "string", required: true, description: "Repository URL or owner/name." }, { name: "state", type: "string", required: false, description: "open, closed, or all. Default open." }, limit(30, 100)] },
  { tool: "github_activity", name: "GitHub Activity", path: "/v1/github/activity", credits: 12, summary: "Recent public activity for a GitHub user.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, limit(30, 100)] },
  { tool: "github_followers", name: "GitHub Followers", path: "/v1/github/followers", credits: 12, summary: "List GitHub followers.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, limit(30, 100)] },
  { tool: "github_following", name: "GitHub Following", path: "/v1/github/following", credits: 12, summary: "List accounts a GitHub user follows.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, limit(30, 100)] },
  { tool: "github_contributions", name: "GitHub Contributions", path: "/v1/github/contributions", credits: 3, summary: "Summary of recent public GitHub contributions.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }] },
  { tool: "github_trending_repositories", name: "GitHub Trending Repositories", path: "/v1/github/trending-repositories", credits: 12, summary: "Search trending repositories by stars or query.", params: [q("GitHub repository search query. Default stars:>1000."), limit(20, 100)] },
  { tool: "github_trending_developers", name: "GitHub Trending Developers", path: "/v1/github/trending-developers", credits: 12, summary: "Search popular GitHub developers.", params: [q("GitHub user search query. Default followers:>1000."), limit(20, 100)] },
];


const GOOGLE: Omit<Endpoint, "platform">[] = [
  { tool: "google_search", name: "Google Search", path: "/v1/google/search", credits: 42, summary: "Google SERP organic search results by keyword, country, and language.", params: [q(), { name: "country", type: "string", required: false, description: "Two-letter country code. Default us." }, { name: "language", type: "string", required: false, description: "Google language code. Default en." }, limit(10, 100)] },
];

const TWITCH: Omit<Endpoint, "platform">[] = [
  { tool: "twitch_profile", name: "Twitch Profile", path: "/v1/twitch/profile", credits: 9, summary: "Twitch channel profile, followers, live status and recent metadata.", params: [url(TWITCH_PROFILE)] },
  { tool: "twitch_user_videos", name: "Twitch User Videos", path: "/v1/twitch/user-videos", credits: 34, summary: "Recent Twitch VODs for a channel.", params: [url(TWITCH_PROFILE), limit(20, 30)] },
  { tool: "twitch_user_schedule", name: "Twitch User Schedule", path: "/v1/twitch/user-schedule", credits: 34, summary: "Upcoming Twitch schedule data when exposed on the public channel.", params: [url(TWITCH_PROFILE)] },
  { tool: "twitch_clip", name: "Twitch Clip", path: "/v1/twitch/clip", credits: 9, summary: "Twitch clip metadata from a clip URL or channel fallback.", params: [url("Twitch clip URL, channel URL, or username.")] },
];

const SPOTIFY: Omit<Endpoint, "platform">[] = [
  { tool: "spotify_artist", name: "Spotify Artist", path: "/v1/spotify/artist", credits: 6, summary: "Spotify artist details, followers and listener metadata.", params: [url(SPOTIFY_URL)] },
  { tool: "spotify_track", name: "Spotify Track", path: "/v1/spotify/track", credits: 6, summary: "Spotify track metadata, artists, album and play count when available.", params: [url(SPOTIFY_URL)] },
  { tool: "spotify_album", name: "Spotify Album", path: "/v1/spotify/album", credits: 6, summary: "Spotify album metadata and track count.", params: [url(SPOTIFY_URL)] },
  { tool: "spotify_search", name: "Spotify Search", path: "/v1/spotify/search", credits: 23, summary: "Search Spotify tracks, albums, artists, podcasts or episodes.", params: [q(), { name: "type", type: "string", required: false, description: "tracks, albums, artists, podcasts, or episodes. Default tracks." }, limit(20, 50)] },
  { tool: "spotify_podcast", name: "Spotify Podcast", path: "/v1/spotify/podcast", credits: 6, summary: "Spotify podcast/show details and episode summary metadata.", params: [url(SPOTIFY_URL), limit(20, 50)] },
  { tool: "spotify_podcast_episodes", name: "Spotify Podcast Episodes", path: "/v1/spotify/podcast-episodes", credits: 23, summary: "List episodes for a Spotify podcast/show.", params: [url(SPOTIFY_URL), limit(20, 50)] },
];

const SOUNDCLOUD: Omit<Endpoint, "platform">[] = [
  { tool: "soundcloud_artist", name: "SoundCloud Artist", path: "/v1/soundcloud/artist", credits: 7, summary: "SoundCloud artist profile metadata.", params: [url(SC_PROFILE)] },
  { tool: "soundcloud_artist_tracks", name: "SoundCloud Artist Tracks", path: "/v1/soundcloud/artist-tracks", credits: 28, summary: "Tracks from a SoundCloud artist profile.", params: [url(SC_PROFILE), limit(20, 100)] },
  { tool: "soundcloud_track", name: "SoundCloud Track", path: "/v1/soundcloud/track", credits: 7, summary: "SoundCloud track metadata and engagement stats.", params: [url(SC_TRACK)] },
];

const LINKTREE: Omit<Endpoint, "platform">[] = [
  { tool: "linktree_page", name: "Linktree Page", path: "/v1/linktree/page", credits: 4, summary: "Public Linktree profile links, socials and profile metadata.", params: [url(LINKTREE_PROFILE)] },
];

const SNAPCHAT: Omit<Endpoint, "platform">[] = [
  { tool: "snapchat_user_profile", name: "Snapchat User Profile", path: "/v1/snapchat/user-profile", credits: 11, summary: "Public Snapchat profile metadata, subscriber count, avatar and highlights.", params: [url(SNAPCHAT_PROFILE)] },
];

const TRUTH_SOCIAL: Omit<Endpoint, "platform">[] = [
  { tool: "truth_social_profile", name: "Truth Social Profile", path: "/v1/truth-social/profile", credits: 5, summary: "Public Truth Social profile metadata and stats.", params: [url(TRUTH_PROFILE)] },
  { tool: "truth_social_user_posts", name: "Truth Social User Posts", path: "/v1/truth-social/user-posts", credits: 17, summary: "Recent public posts from a Truth Social profile.", params: [url(TRUTH_PROFILE), limit(20, 80)] },
  { tool: "truth_social_post", name: "Truth Social Post", path: "/v1/truth-social/post", credits: 5, summary: "Truth Social post metadata, text, media and engagement.", params: [url(TRUTH_POST)] },
];

const KICK: Omit<Endpoint, "platform">[] = [
  { tool: "kick_clip", name: "Kick Clip", path: "/v1/kick/clip", credits: 34, summary: "Kick clip metadata from a clip URL or recent channel clips.", params: [url(KICK_CLIP), limit(30, 100)] },
];

const AMAZON_SHOP_ENDPOINTS: Omit<Endpoint, "platform">[] = [
  { tool: "amazon_shop_page", name: "Amazon Shop Page", path: "/v1/amazon-shop/page", credits: 89, summary: "Amazon seller storefront metadata and product listings.", params: [url(AMAZON_SHOP), { name: "marketplace", type: "string", required: false, description: "Amazon marketplace code. Default US." }, limit(20, 200)] },
];

const AGE_GENDER: Omit<Endpoint, "platform">[] = [
  { tool: "age_gender_get", name: "Age and Gender", path: "/v1/age-gender", credits: 4, summary: "Predict age, gender and nationality signals from first names.", params: [{ name: "name", type: "string", required: true, description: "First name, or fallback when names is omitted." }, { name: "names", type: "string", required: false, description: "Optional comma-separated list of names." }] },
];

const ACCOUNT: Omit<Endpoint, "platform">[] = [
  { tool: "account_balance", name: "Credit Balance", path: "/v1/account/balance", credits: 0, summary: "Get current Captapi credit balance and plan limits.", params: [] },
  { tool: "account_request_history", name: "Request History", path: "/v1/account/request-history", credits: 0, summary: "List recent Captapi API requests for the current key owner.", params: [limit(50, 500)] },
  { tool: "account_daily_usage", name: "Daily Usage", path: "/v1/account/daily-usage", credits: 0, summary: "Daily request and credit usage summary.", params: [{ name: "days", type: "number", required: false, description: "Number of days to include. Default 30, max 365." }] },
  { tool: "account_most_used_routes", name: "Most Used Routes", path: "/v1/account/most-used-routes", credits: 0, summary: "Most used API routes by request count and credits.", params: [{ name: "days", type: "number", required: false, description: "Number of days to include. Default 30, max 365." }, limit(20, 100)] },
];

const KWAI: Omit<Endpoint, "platform">[] = [
  { tool: "kwai_profile", name: "Kwai Profile", path: "/v1/kwai/profile", credits: 17, summary: "Kwai/Kuaishou public profile details and stats.", params: [url(KWAI_PROFILE)] },
  { tool: "kwai_user_posts", name: "Kwai User Posts", path: "/v1/kwai/user-posts", credits: 45, summary: "Recent Kwai/Kuaishou videos from a profile.", params: [url(KWAI_PROFILE), limit(20, 200)] },
  { tool: "kwai_post", name: "Kwai Post", path: "/v1/kwai/post", credits: 17, summary: "Kwai/Kuaishou post metadata and engagement.", params: [url(KWAI_POST)] },
];

const KOMI: Omit<Endpoint, "platform">[] = [
  { tool: "komi_page", name: "Komi Page", path: "/v1/komi/page", credits: 4, summary: "Public Komi page links and profile metadata.", params: [url(KOMI_PAGE)] },
];

const PILLAR: Omit<Endpoint, "platform">[] = [
  { tool: "pillar_page", name: "Pillar Page", path: "/v1/pillar/page", credits: 4, summary: "Public Pillar page links and profile metadata.", params: [url(PILLAR_PAGE)] },
];

const LINKBIO: Omit<Endpoint, "platform">[] = [
  { tool: "linkbio_page", name: "Linkbio Page", path: "/v1/linkbio/page", credits: 4, summary: "Public Linkbio page links and profile metadata.", params: [url(LINKBIO_PAGE)] },
];

const LINKME: Omit<Endpoint, "platform">[] = [
  { tool: "linkme_profile", name: "Linkme Profile", path: "/v1/linkme/profile", credits: 4, summary: "Public Linkme profile links and metadata.", params: [url(LINKME_PROFILE)] },
];

const AD_LIBRARY: Omit<Endpoint, "platform">[] = [
  { tool: "facebook_ad_library_search", name: "Facebook Ad Library Search", path: "/v1/ad-library/facebook/search", credits: 70, summary: "Search Meta/Facebook ads by keyword.", params: [q(), { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(20, 200)] },
  { tool: "facebook_ad_library_company_ads", name: "Facebook Company Ads", path: "/v1/ad-library/facebook/company-ads", credits: 70, summary: "Ads for a Facebook page or Meta Ad Library URL.", params: [url("Facebook page URL or Meta Ad Library URL."), { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(20, 200)] },
  { tool: "facebook_ad_library_search_companies", name: "Facebook Ad Library Search Companies", path: "/v1/ad-library/facebook/search-companies", credits: 70, summary: "Find advertisers/pages in the Meta Ad Library by name.", params: [q(), { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(20, 200)] },
  { tool: "facebook_ad_library_ad_details", name: "Facebook Ad Details", path: "/v1/ad-library/facebook/ad-details", credits: 17, summary: "Meta/Facebook ad details.", params: [url("Meta Ad Library ad URL.")] },
  { tool: "facebook_ad_library_ad_transcript", name: "Facebook Ad Transcript", path: "/v1/ad-library/facebook/ad-transcript", credits: 17, summary: "Extract creative text from a Meta/Facebook ad as transcript text.", params: [url("Meta Ad Library ad URL or ad ID.")] },
  { tool: "tiktok_ad_library_search", name: "TikTok Ad Library Search", path: "/v1/ad-library/tiktok/search", credits: 70, summary: "Search TikTok Ad Library and Creative Center.", params: [q(), { name: "country", type: "string", required: false, description: "ISO country code. Default DE." }, limit(20, 200)] },
  { tool: "tiktok_ad_library_ad_details", name: "TikTok Ad Details", path: "/v1/ad-library/tiktok/ad-details", credits: 17, summary: "TikTok ad details by ad URL or ID.", params: [url("TikTok Ad Library URL or ad ID."), { name: "country", type: "string", required: false, description: "ISO country code. Default DE." }] },
  { tool: "google_ad_library_company_ads", name: "Google Company Ads", path: "/v1/ad-library/google/company-ads", credits: 67, summary: "Google Ads Transparency Center ads for an advertiser.", params: [{ name: "advertiser", type: "string", required: true, description: "Advertiser name, domain, or Google advertiser ID." }, { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(20, 200)] },
  { tool: "google_ad_library_ad_details", name: "Google Ad Details", path: "/v1/ad-library/google/ad-details", credits: 17, summary: "Google ad details by Transparency Center URL.", params: [{ name: "creative_id", type: "string", required: true, description: "Google Ads Transparency Center URL containing AR advertiser ID and CR creative ID." }, { name: "country", type: "string", required: false, description: "ISO country code. Default US." }] },
  { tool: "google_ad_library_advertiser_search", name: "Google Advertiser Search", path: "/v1/ad-library/google/advertiser-search", credits: 45, summary: "Search Google Ads advertisers.", params: [q(), { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(10, 50)] },
  { tool: "linkedin_ad_library_search_ads", name: "LinkedIn Ad Library Search", path: "/v1/ad-library/linkedin/search-ads", credits: 70, summary: "Search LinkedIn Ad Library ads.", params: [q(), { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(20, 200)] },
  { tool: "linkedin_ad_library_ad_details", name: "LinkedIn Ad Details", path: "/v1/ad-library/linkedin/ad-details", credits: 17, summary: "LinkedIn ad details by URL or ID.", params: [url("LinkedIn Ad Library URL or ad ID.")] },
];

function withPlatform(
  list: Omit<Endpoint, "platform">[],
  platform: Platform,
): Endpoint[] {
  return list.map((e) => ({ ...e, platform }));
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
  ...withPlatform(GITHUB, "github"),
  ...withPlatform(GOOGLE, "google"),
  ...withPlatform(TWITCH, "twitch"),
  ...withPlatform(SPOTIFY, "spotify"),
  ...withPlatform(SOUNDCLOUD, "soundcloud"),
  ...withPlatform(LINKTREE, "linktree"),
  ...withPlatform(SNAPCHAT, "snapchat"),
  ...withPlatform(TRUTH_SOCIAL, "truth_social"),
  ...withPlatform(KICK, "kick"),
  ...withPlatform(AMAZON_SHOP_ENDPOINTS, "amazon_shop"),
  ...withPlatform(AGE_GENDER, "age_gender"),
  ...withPlatform(ACCOUNT, "account"),
  ...withPlatform(KWAI, "kwai"),
  ...withPlatform(KOMI, "komi"),
  ...withPlatform(PILLAR, "pillar"),
  ...withPlatform(LINKBIO, "linkbio"),
  ...withPlatform(LINKME, "linkme"),
  ...withPlatform(AD_LIBRARY, "ad_library"),
];

/** A concise, agent-facing description (summary + cost) for an endpoint. */
export function describe(e: Endpoint): string {
  return `${e.summary} Costs ~${e.credits} credit${e.credits === 1 ? "" : "s"}; cached results are free, failures are never charged.`;
}
