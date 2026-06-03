// Auto-maintained catalog of every Captapi endpoint exposed as an MCP tool.
// Each endpoint declares its EXACT input parameters (matching the REST API),
// so agents know precisely what to pass. Mirrors the backend routers.

export type Platform = "youtube" | "tiktok" | "instagram" | "facebook";

export interface ToolParam {
  name: string;
  type: "string" | "number";
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
  description,
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

const YT_VIDEO = "Public YouTube video URL, e.g. https://youtube.com/watch?v=ID.";
const YT_SHORTS = "Public YouTube Shorts URL, e.g. https://youtube.com/shorts/ID.";
const YT_CHANNEL = "YouTube channel URL, e.g. https://youtube.com/@handle or /channel/UC...";
const TT_VIDEO = "Public TikTok video URL, e.g. https://tiktok.com/@user/video/ID.";
const TT_PROFILE = "TikTok profile URL, e.g. https://tiktok.com/@username.";
const TT_MUSIC = "TikTok music/sound URL, e.g. https://tiktok.com/music/name-ID.";
const IG_POST = "Instagram post or reel URL, e.g. https://instagram.com/reel/ID/.";
const IG_REEL = "Instagram Reel URL, e.g. https://instagram.com/reel/ID/.";
const IG_PROFILE = "Instagram profile URL, e.g. https://instagram.com/username/.";
const FB_VIDEO = "Public Facebook video or post URL.";

const YOUTUBE: Omit<Endpoint, "platform">[] = [
  { tool: "youtube_transcript", name: "YouTube Transcript", path: "/v1/youtube/transcript", credits: 2, summary: "Extract the full timestamped transcript of a YouTube video.", params: [url(YT_VIDEO), language()] },
  { tool: "youtube_summarize", name: "YouTube Summarizer", path: "/v1/youtube/summarize", credits: 4, summary: "AI summary (key points, topics, sentiment) of a YouTube video.", params: [url(YT_VIDEO), language()] },
  { tool: "youtube_video_details", name: "YouTube Video Details", path: "/v1/youtube/video-details", credits: 1, summary: "Metadata + engagement stats for a YouTube video.", params: [url(YT_VIDEO)] },
  { tool: "youtube_comments", name: "YouTube Comments", path: "/v1/youtube/comments", credits: 20, summary: "Comments on a YouTube video.", params: [url(YT_VIDEO), limit(50, 500)] },
  { tool: "youtube_channel_details", name: "YouTube Channel Details", path: "/v1/youtube/channel-details", credits: 1, summary: "Channel info & subscriber/stats for a YouTube channel.", params: [url(YT_CHANNEL)] },
  { tool: "youtube_search", name: "YouTube Search", path: "/v1/youtube/search", credits: 20, summary: "Search YouTube videos by keyword.", params: [q(), limit(20, 200)] },
  { tool: "youtube_channel_videos", name: "YouTube Channel Videos", path: "/v1/youtube/channel-videos", credits: 20, summary: "List a channel's uploaded videos.", params: [url(YT_CHANNEL), limit(20, 200)] },
  { tool: "youtube_playlist_videos", name: "YouTube Playlist Videos", path: "/v1/youtube/playlist-videos", credits: 50, summary: "List videos in a YouTube playlist.", params: [url("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."), limit(50, 500)] },
  { tool: "youtube_video_download", name: "YouTube Video Download", path: "/v1/youtube/video-download", credits: 3, summary: "Direct download URLs for a YouTube video.", params: [url(YT_VIDEO)] },
  { tool: "youtube_shorts_transcript", name: "YouTube Shorts Transcript", path: "/v1/youtube/shorts/transcript", credits: 2, summary: "Transcript of a YouTube Short.", params: [url(YT_SHORTS), language()] },
  { tool: "youtube_shorts_summarize", name: "YouTube Shorts Summarizer", path: "/v1/youtube/shorts/summarize", credits: 4, summary: "AI summary of a YouTube Short.", params: [url(YT_SHORTS), language()] },
  { tool: "youtube_shorts_details", name: "YouTube Shorts Stats", path: "/v1/youtube/shorts/video-details", credits: 1, summary: "Metadata + stats for a YouTube Short.", params: [url(YT_SHORTS)] },
  { tool: "youtube_shorts_comments", name: "YouTube Shorts Comments", path: "/v1/youtube/shorts/comments", credits: 20, summary: "Comments on a YouTube Short.", params: [url(YT_SHORTS), limit(50, 500)] },
  { tool: "youtube_channel_shorts", name: "YouTube Channel Shorts", path: "/v1/youtube/channel-shorts", credits: 20, summary: "List a channel's Shorts.", params: [url(YT_CHANNEL), limit(20, 200)] },
  { tool: "youtube_channel_streams", name: "YouTube Channel Streams", path: "/v1/youtube/channel-streams", credits: 20, summary: "List a channel's live/past streams.", params: [url(YT_CHANNEL), limit(20, 200)] },
  { tool: "youtube_hashtag_search", name: "YouTube Hashtag Search", path: "/v1/youtube/hashtag-search", credits: 20, summary: "Search YouTube videos by hashtag.", params: [q("Hashtag with or without the # (min 2 chars)."), limit(20, 200)] },
  { tool: "youtube_comment_replies", name: "YouTube Comment Replies", path: "/v1/youtube/comment-replies", credits: 20, summary: "Replies to a specific YouTube comment.", params: [url(YT_VIDEO), commentId(), limit(50, 500)] },
  { tool: "youtube_channel_playlists", name: "YouTube Channel Playlists", path: "/v1/youtube/channel-playlists", credits: 20, summary: "List a channel's playlists.", params: [url(YT_CHANNEL), limit(20, 200)] },
  { tool: "youtube_community_posts", name: "YouTube Community Posts", path: "/v1/youtube/community-posts", credits: 10, summary: "List a channel's community (posts) tab.", params: [url(YT_CHANNEL), limit(20, 200)] },
];

const TIKTOK: Omit<Endpoint, "platform">[] = [
  { tool: "tiktok_transcript", name: "TikTok Transcript", path: "/v1/tiktok/transcript", credits: 2, summary: "Transcript of a TikTok video (via captions).", params: [url(TT_VIDEO)] },
  { tool: "tiktok_summarize", name: "TikTok Summarizer", path: "/v1/tiktok/summarize", credits: 4, summary: "AI summary of a TikTok video.", params: [url(TT_VIDEO)] },
  { tool: "tiktok_video_details", name: "TikTok Video Details", path: "/v1/tiktok/video-details", credits: 1, summary: "Metadata + stats for a TikTok video.", params: [url(TT_VIDEO)] },
  { tool: "tiktok_comments", name: "TikTok Comments", path: "/v1/tiktok/comments", credits: 10, summary: "Comments on a TikTok video.", params: [url(TT_VIDEO), limit(50, 500)] },
  { tool: "tiktok_channel_details", name: "TikTok Channel Details", path: "/v1/tiktok/channel-details", credits: 1, summary: "Profile info & stats for a TikTok user.", params: [url(TT_PROFILE)] },
  { tool: "tiktok_search", name: "TikTok Search", path: "/v1/tiktok/search", credits: 14, summary: "Search TikTok videos by keyword/hashtag.", params: [q(), limit(20, 200)] },
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
];

const INSTAGRAM: Omit<Endpoint, "platform">[] = [
  { tool: "instagram_transcript", name: "Instagram Transcript", path: "/v1/instagram/transcript", credits: 2, summary: "Transcript of an Instagram Reel.", params: [url(IG_REEL)] },
  { tool: "instagram_summarize", name: "Instagram Summarizer", path: "/v1/instagram/summarize", credits: 4, summary: "AI summary of an Instagram Reel.", params: [url(IG_REEL)] },
  { tool: "instagram_details", name: "Instagram Details", path: "/v1/instagram/details", credits: 1, summary: "Details for an Instagram post or reel.", params: [url(IG_POST)] },
  { tool: "instagram_comments", name: "Instagram Comments", path: "/v1/instagram/comments", credits: 45, summary: "Comments on an Instagram post or reel.", params: [url(IG_POST), limit(50, 500)] },
  { tool: "instagram_channel_details", name: "Instagram Channel Details", path: "/v1/instagram/channel-details", credits: 1, summary: "Profile info & stats for an Instagram account.", params: [url(IG_PROFILE)] },
  { tool: "instagram_channel_posts", name: "Instagram Channel Posts", path: "/v1/instagram/channel-posts", credits: 12, summary: "Latest posts from an Instagram profile.", params: [url(IG_PROFILE), limit(20, 200)] },
  { tool: "instagram_channel_reels", name: "Instagram Channel Reels", path: "/v1/instagram/channel-reels", credits: 12, summary: "Latest Reels from an Instagram profile.", params: [url(IG_PROFILE), limit(20, 200)] },
  { tool: "instagram_reels_search", name: "Instagram Reels Search", path: "/v1/instagram/reels-search", credits: 12, summary: "Search Instagram Reels by hashtag/keyword.", params: [q("Hashtag (without #) or keyword (min 2 chars)."), limit(20, 200)] },
  { tool: "instagram_video_download", name: "Instagram Video Download", path: "/v1/instagram/video-download", credits: 3, summary: "Direct video URL for an Instagram Reel.", params: [url(IG_REEL)] },
  { tool: "instagram_tagged_posts", name: "Instagram Tagged Posts", path: "/v1/instagram/tagged-posts", credits: 18, summary: "Posts an Instagram user is tagged in.", params: [url(IG_PROFILE), limit(20, 200)] },
  { tool: "instagram_music_posts", name: "Instagram Music Posts", path: "/v1/instagram/music-posts", credits: 18, summary: "Posts/Reels using an Instagram audio.", params: [url("Instagram audio/music page URL."), limit(20, 200)] },
  { tool: "instagram_hashtag_search", name: "Instagram Hashtag Search", path: "/v1/instagram/hashtag-search", credits: 12, summary: "Search Instagram posts by hashtag.", params: [q("Hashtag without the # (min 2 chars)."), limit(20, 200)] },
  { tool: "instagram_profile_search", name: "Instagram Profile Search", path: "/v1/instagram/profile-search", credits: 12, summary: "Search Instagram profiles by keyword.", params: [q(), limit(20, 100)] },
  { tool: "instagram_story_highlights", name: "Instagram Story Highlights", path: "/v1/instagram/story-highlights", credits: 5, summary: "List a profile's story highlight covers.", params: [url(IG_PROFILE)] },
  { tool: "instagram_highlights_details", name: "Instagram Highlights Details", path: "/v1/instagram/highlights-details", credits: 9, summary: "Items inside a profile's story highlights.", params: [url(IG_PROFILE), { name: "limit", type: "number", required: false, description: "Max highlights to expand. Default 10, max 50." }] },
  { tool: "instagram_embed", name: "Instagram Embed", path: "/v1/instagram/embed", credits: 1, summary: "Embed HTML for an Instagram post/reel.", params: [url(IG_POST)] },
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
];

/** A concise, agent-facing description (summary + cost) for an endpoint. */
export function describe(e: Endpoint): string {
  return `${e.summary} Costs ~${e.credits} credit${e.credits === 1 ? "" : "s"}; cached results are free, failures are never charged.`;
}
