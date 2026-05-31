// Auto-maintained catalog of every Captapi endpoint exposed as an MCP tool.
// Mirrors frontend/lib/api-catalog.ts. Keep in sync when endpoints change.

export type Category =
  | "transcript"
  | "summarize"
  | "details"
  | "comments"
  | "channel"
  | "search"
  | "list"
  | "download";

export type Platform = "youtube" | "tiktok" | "instagram" | "facebook";

export interface Endpoint {
  /** MCP tool name, e.g. "youtube_transcript". */
  tool: string;
  platform: Platform;
  /** Human marketing name, e.g. "YouTube Transcript API". */
  name: string;
  category: Category;
  /** REST path on the Captapi API, e.g. "/v1/youtube/transcript". */
  path: string;
  /** Typical credit cost of a standard request. */
  credits: number;
}

const YOUTUBE: Omit<Endpoint, "platform">[] = [
  { tool: "youtube_transcript", name: "YouTube Transcript", category: "transcript", path: "/v1/youtube/transcript", credits: 2 },
  { tool: "youtube_summarize", name: "YouTube Summarizer", category: "summarize", path: "/v1/youtube/summarize", credits: 4 },
  { tool: "youtube_video_details", name: "YouTube Video Details", category: "details", path: "/v1/youtube/video-details", credits: 1 },
  { tool: "youtube_comments", name: "YouTube Comments", category: "comments", path: "/v1/youtube/comments", credits: 20 },
  { tool: "youtube_channel_details", name: "YouTube Channel Details", category: "channel", path: "/v1/youtube/channel-details", credits: 1 },
  { tool: "youtube_search", name: "YouTube Search", category: "search", path: "/v1/youtube/search", credits: 20 },
  { tool: "youtube_channel_videos", name: "YouTube Channel Videos", category: "list", path: "/v1/youtube/channel-videos", credits: 20 },
  { tool: "youtube_playlist_videos", name: "YouTube Playlist Videos", category: "list", path: "/v1/youtube/playlist-videos", credits: 50 },
  { tool: "youtube_video_download", name: "YouTube Video Download", category: "download", path: "/v1/youtube/video-download", credits: 3 },
  { tool: "youtube_shorts_transcript", name: "YouTube Shorts Transcript", category: "transcript", path: "/v1/youtube/shorts/transcript", credits: 2 },
  { tool: "youtube_shorts_summarize", name: "YouTube Shorts Summarizer", category: "summarize", path: "/v1/youtube/shorts/summarize", credits: 4 },
  { tool: "youtube_shorts_details", name: "YouTube Shorts Stats", category: "details", path: "/v1/youtube/shorts/video-details", credits: 1 },
  { tool: "youtube_shorts_comments", name: "YouTube Shorts Comments", category: "comments", path: "/v1/youtube/shorts/comments", credits: 20 },
  { tool: "youtube_channel_shorts", name: "YouTube Channel Shorts", category: "list", path: "/v1/youtube/channel-shorts", credits: 20 },
  { tool: "youtube_channel_streams", name: "YouTube Channel Streams", category: "list", path: "/v1/youtube/channel-streams", credits: 20 },
  { tool: "youtube_hashtag_search", name: "YouTube Hashtag Search", category: "search", path: "/v1/youtube/hashtag-search", credits: 20 },
  { tool: "youtube_comment_replies", name: "YouTube Comment Replies", category: "comments", path: "/v1/youtube/comment-replies", credits: 20 },
  { tool: "youtube_channel_playlists", name: "YouTube Channel Playlists", category: "list", path: "/v1/youtube/channel-playlists", credits: 20 },
  { tool: "youtube_community_posts", name: "YouTube Community Posts", category: "list", path: "/v1/youtube/community-posts", credits: 10 },
];

const TIKTOK: Omit<Endpoint, "platform">[] = [
  { tool: "tiktok_transcript", name: "TikTok Transcript", category: "transcript", path: "/v1/tiktok/transcript", credits: 2 },
  { tool: "tiktok_summarize", name: "TikTok Summarizer", category: "summarize", path: "/v1/tiktok/summarize", credits: 4 },
  { tool: "tiktok_video_details", name: "TikTok Video Details", category: "details", path: "/v1/tiktok/video-details", credits: 1 },
  { tool: "tiktok_comments", name: "TikTok Comments", category: "comments", path: "/v1/tiktok/comments", credits: 10 },
  { tool: "tiktok_channel_details", name: "TikTok Channel Details", category: "channel", path: "/v1/tiktok/channel-details", credits: 1 },
  { tool: "tiktok_search", name: "TikTok Search", category: "search", path: "/v1/tiktok/search", credits: 14 },
  { tool: "tiktok_video_download", name: "TikTok Video Download", category: "download", path: "/v1/tiktok/video-download", credits: 3 },
  { tool: "tiktok_channel_posts", name: "TikTok Channel Posts", category: "list", path: "/v1/tiktok/channel-posts", credits: 14 },
  { tool: "tiktok_comment_replies", name: "TikTok Comment Replies", category: "comments", path: "/v1/tiktok/comment-replies", credits: 50 },
  { tool: "tiktok_user_followers", name: "TikTok User Followers", category: "list", path: "/v1/tiktok/user-followers", credits: 20 },
  { tool: "tiktok_user_followings", name: "TikTok User Followings", category: "list", path: "/v1/tiktok/user-followings", credits: 20 },
  { tool: "tiktok_music_posts", name: "TikTok Music Posts", category: "list", path: "/v1/tiktok/music-posts", credits: 32 },
  { tool: "tiktok_hashtag_search", name: "TikTok Hashtag Search", category: "search", path: "/v1/tiktok/hashtag-search", credits: 14 },
  { tool: "tiktok_top_search", name: "TikTok Top Search", category: "search", path: "/v1/tiktok/top-search", credits: 14 },
  { tool: "tiktok_user_search", name: "TikTok User Search", category: "search", path: "/v1/tiktok/user-search", credits: 8 },
  { tool: "tiktok_song_details", name: "TikTok Song Details", category: "details", path: "/v1/tiktok/song-details", credits: 2 },
  { tool: "tiktok_trending_feed", name: "TikTok Trending Feed", category: "list", path: "/v1/tiktok/trending-feed", credits: 14 },
  { tool: "tiktok_popular_hashtags", name: "TikTok Popular Hashtags", category: "list", path: "/v1/tiktok/popular-hashtags", credits: 14 },
];

const INSTAGRAM: Omit<Endpoint, "platform">[] = [
  { tool: "instagram_transcript", name: "Instagram Transcript", category: "transcript", path: "/v1/instagram/transcript", credits: 2 },
  { tool: "instagram_summarize", name: "Instagram Summarizer", category: "summarize", path: "/v1/instagram/summarize", credits: 4 },
  { tool: "instagram_details", name: "Instagram Details", category: "details", path: "/v1/instagram/details", credits: 1 },
  { tool: "instagram_comments", name: "Instagram Comments", category: "comments", path: "/v1/instagram/comments", credits: 45 },
  { tool: "instagram_channel_details", name: "Instagram Channel Details", category: "channel", path: "/v1/instagram/channel-details", credits: 1 },
  { tool: "instagram_channel_posts", name: "Instagram Channel Posts", category: "list", path: "/v1/instagram/channel-posts", credits: 12 },
  { tool: "instagram_channel_reels", name: "Instagram Channel Reels", category: "list", path: "/v1/instagram/channel-reels", credits: 12 },
  { tool: "instagram_reels_search", name: "Instagram Reels Search", category: "search", path: "/v1/instagram/reels-search", credits: 12 },
  { tool: "instagram_video_download", name: "Instagram Video Download", category: "download", path: "/v1/instagram/video-download", credits: 3 },
  { tool: "instagram_tagged_posts", name: "Instagram Tagged Posts", category: "list", path: "/v1/instagram/tagged-posts", credits: 18 },
  { tool: "instagram_music_posts", name: "Instagram Music Posts", category: "list", path: "/v1/instagram/music-posts", credits: 18 },
  { tool: "instagram_hashtag_search", name: "Instagram Hashtag Search", category: "search", path: "/v1/instagram/hashtag-search", credits: 12 },
  { tool: "instagram_profile_search", name: "Instagram Profile Search", category: "search", path: "/v1/instagram/profile-search", credits: 12 },
  { tool: "instagram_story_highlights", name: "Instagram Story Highlights", category: "list", path: "/v1/instagram/story-highlights", credits: 5 },
  { tool: "instagram_highlights_details", name: "Instagram Highlights Details", category: "list", path: "/v1/instagram/highlights-details", credits: 9 },
  { tool: "instagram_embed", name: "Instagram Embed", category: "details", path: "/v1/instagram/embed", credits: 1 },
];

const FACEBOOK: Omit<Endpoint, "platform">[] = [
  { tool: "facebook_details", name: "Facebook Details", category: "details", path: "/v1/facebook/details", credits: 1 },
  { tool: "facebook_transcript", name: "Facebook Transcript", category: "transcript", path: "/v1/facebook/transcript", credits: 2 },
  { tool: "facebook_summarize", name: "Facebook Summarizer", category: "summarize", path: "/v1/facebook/summarize", credits: 4 },
  { tool: "facebook_comments", name: "Facebook Comments", category: "comments", path: "/v1/facebook/comments", credits: 30 },
  { tool: "facebook_page_details", name: "Facebook Page Details", category: "channel", path: "/v1/facebook/page-details", credits: 1 },
  { tool: "facebook_profile_posts", name: "Facebook Profile Posts", category: "list", path: "/v1/facebook/profile-posts", credits: 12 },
  { tool: "facebook_profile_reels", name: "Facebook Profile Reels", category: "list", path: "/v1/facebook/profile-reels", credits: 36 },
  { tool: "facebook_group_posts", name: "Facebook Group Posts", category: "list", path: "/v1/facebook/group-posts", credits: 12 },
  { tool: "facebook_comment_replies", name: "Facebook Comment Replies", category: "comments", path: "/v1/facebook/comment-replies", credits: 30 },
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

const PLATFORM_LABEL: Record<Platform, string> = {
  youtube: "YouTube",
  tiktok: "TikTok",
  instagram: "Instagram",
  facebook: "Facebook",
};

/** A concise, agent-facing description for an endpoint. */
export function describe(e: Endpoint): string {
  const p = PLATFORM_LABEL[e.platform];
  const cost = `Costs ~${e.credits} credit${e.credits === 1 ? "" : "s"} (cached results are free).`;
  switch (e.category) {
    case "transcript":
      return `Extract the full timestamped transcript from a public ${p} video by URL. ${cost}`;
    case "summarize":
      return `Generate an AI summary (key points, topics, sentiment) of a public ${p} video by URL. ${cost}`;
    case "details":
      return `Fetch metadata and engagement stats (views, likes, comments, duration) for a ${p} item by URL. ${cost}`;
    case "comments":
      return `Pull comments (author, text, likes, replies) from a public ${p} item by URL. ${cost}`;
    case "channel":
      return `Fetch ${p} profile/channel details — followers, bio, verification, stats — by URL. ${cost}`;
    case "search":
      return `Search ${p} by keyword/query and return ranked, structured results. ${cost}`;
    case "list":
      return `Bulk-list ${p} content with full metadata for each item, by URL. ${cost}`;
    case "download":
      return `Get a direct, watermark-free download URL for a public ${p} video by URL. ${cost}`;
  }
}
