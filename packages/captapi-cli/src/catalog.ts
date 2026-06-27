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
  | "ad_library";

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

const TW_TWEET = "Public tweet URL, e.g. https://x.com/user/status/ID.";
const TW_PROFILE = "Twitter/X profile URL or @handle, e.g. https://x.com/username.";
const RD_SUB = "Subreddit URL, r/name, or bare name, e.g. r/technology.";
const RD_POST = "Reddit post URL, e.g. https://reddit.com/r/sub/comments/ID/...";
const TH_PROFILE = "Threads profile URL or @handle, e.g. https://threads.net/@username.";
const TH_POST = "Threads post URL, e.g. https://threads.net/@user/post/CODE.";
const BS_PROFILE = "Bluesky profile URL, @handle, or handle, e.g. bsky.app/profile/handle.";
const BS_POST = "Bluesky post URL, e.g. https://bsky.app/profile/handle/post/RKEY.";
const PIN_PIN = "Pinterest pin URL, e.g. https://pinterest.com/pin/ID/.";
const PIN_PROFILE = "Pinterest profile URL or username.";
const LI_PROFILE = "LinkedIn profile URL, e.g. https://linkedin.com/in/slug.";
const LI_COMPANY = "LinkedIn company URL, e.g. https://linkedin.com/company/slug.";
const LI_POST = "LinkedIn post or activity URL.";
const RB_VIDEO = "Rumble video URL, e.g. https://rumble.com/vXXXX-title.html.";
const RB_CHANNEL = "Rumble channel URL, e.g. https://rumble.com/c/name.";

const TWITTER: Omit<Endpoint, "platform">[] = [
  { tool: "twitter_tweet_details", name: "Twitter/X Tweet Details", path: "/v1/twitter/tweet-details", credits: 1, summary: "Metadata + engagement stats for a tweet.", params: [url(TW_TWEET)] },
  { tool: "twitter_profile", name: "Twitter/X Profile", path: "/v1/twitter/profile", credits: 1, summary: "Profile info & stats for a Twitter/X account.", params: [url(TW_PROFILE)] },
  { tool: "twitter_user_tweets", name: "Twitter/X User Tweets", path: "/v1/twitter/user-tweets", credits: 14, summary: "Recent tweets from a Twitter/X profile.", params: [url(TW_PROFILE), limit(20, 200)] },
  { tool: "twitter_search", name: "Twitter/X Search", path: "/v1/twitter/search", credits: 14, summary: "Search tweets by keyword.", params: [q(), limit(20, 200)] },
];

const REDDIT: Omit<Endpoint, "platform">[] = [
  { tool: "reddit_subreddit_posts", name: "Reddit Subreddit Posts", path: "/v1/reddit/subreddit-posts", credits: 10, summary: "Recent posts in a subreddit.", params: [url(RD_SUB), limit(25, 200)] },
  { tool: "reddit_post_details", name: "Reddit Post Details", path: "/v1/reddit/post-details", credits: 1, summary: "Metadata + stats for a Reddit post.", params: [url(RD_POST)] },
  { tool: "reddit_post_comments", name: "Reddit Post Comments", path: "/v1/reddit/post-comments", credits: 20, summary: "Comments on a Reddit post.", params: [url(RD_POST), limit(50, 500)] },
  { tool: "reddit_search", name: "Reddit Search", path: "/v1/reddit/search", credits: 10, summary: "Search Reddit posts by keyword.", params: [q(), limit(25, 200)] },
];

const THREADS: Omit<Endpoint, "platform">[] = [
  { tool: "threads_profile", name: "Threads Profile", path: "/v1/threads/profile", credits: 1, summary: "Profile info & stats for a Threads account.", params: [url(TH_PROFILE)] },
  { tool: "threads_user_posts", name: "Threads User Posts", path: "/v1/threads/user-posts", credits: 14, summary: "Recent posts from a Threads profile.", params: [url(TH_PROFILE), limit(20, 100)] },
  { tool: "threads_post_details", name: "Threads Post Details", path: "/v1/threads/post-details", credits: 1, summary: "Metadata + engagement for a Threads post.", params: [url(TH_POST)] },
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
];

const LINKEDIN: Omit<Endpoint, "platform">[] = [
  { tool: "linkedin_profile", name: "LinkedIn Profile", path: "/v1/linkedin/profile", credits: 2, summary: "Public LinkedIn person profile details.", params: [url(LI_PROFILE)] },
  { tool: "linkedin_company", name: "LinkedIn Company", path: "/v1/linkedin/company", credits: 2, summary: "Public LinkedIn company page details.", params: [url(LI_COMPANY)] },
  { tool: "linkedin_post_details", name: "LinkedIn Post Details", path: "/v1/linkedin/post-details", credits: 1, summary: "Metadata + engagement for a LinkedIn post.", params: [url(LI_POST)] },
  { tool: "linkedin_company_posts", name: "LinkedIn Company Posts", path: "/v1/linkedin/company-posts", credits: 16, summary: "Recent public posts from a LinkedIn company page.", params: [url(LI_COMPANY), limit(20, 100)] },
  { tool: "linkedin_search_posts", name: "LinkedIn Search Posts", path: "/v1/linkedin/search-posts", credits: 16, summary: "Search public LinkedIn posts by keyword.", params: [q(), { name: "sort", type: "string", required: false, description: "relevance or date. Default relevance." }, limit(20, 50)] },
];

const RUMBLE: Omit<Endpoint, "platform">[] = [
  { tool: "rumble_video_details", name: "Rumble Video Details", path: "/v1/rumble/video-details", credits: 1, summary: "Metadata + stats for a Rumble video.", params: [url(RB_VIDEO)] },
  { tool: "rumble_channel_videos", name: "Rumble Channel Videos", path: "/v1/rumble/channel-videos", credits: 12, summary: "List videos from a Rumble channel.", params: [url(RB_CHANNEL), limit(20, 200)] },
  { tool: "rumble_search", name: "Rumble Search", path: "/v1/rumble/search", credits: 12, summary: "Search Rumble videos by keyword.", params: [q(), limit(20, 200)] },
  { tool: "rumble_transcript", name: "Rumble Transcript", path: "/v1/rumble/transcript", credits: 3, summary: "Extract a timestamped Rumble video transcript.", params: [url(RB_VIDEO), language()] },
  { tool: "rumble_comments", name: "Rumble Comments", path: "/v1/rumble/comments", credits: 30, summary: "Comments on a Rumble video.", params: [url(RB_VIDEO), limit(50, 500)] },
];

const TIKTOK_SHOP: Omit<Endpoint, "platform">[] = [
  { tool: "tiktok_shop_search", name: "TikTok Shop Search", path: "/v1/tiktok-shop/shop-search", credits: 16, summary: "Search TikTok Shop products by keyword.", params: [q("Product search query."), { name: "region", type: "string", required: false, description: "Two-letter TikTok Shop region. Default US." }, limit(20, 200)] },
  { tool: "tiktok_shop_products", name: "TikTok Shop Products", path: "/v1/tiktok-shop/shop-products", credits: 16, summary: "List products from a TikTok Shop store.", params: [url("TikTok Shop store URL."), limit(20, 200)] },
  { tool: "tiktok_shop_product_details", name: "TikTok Shop Product Details", path: "/v1/tiktok-shop/product-details", credits: 2, summary: "Full TikTok Shop product details, seller and price metadata.", params: [url("TikTok Shop product URL.")] },
  { tool: "tiktok_shop_product_reviews", name: "TikTok Shop Product Reviews", path: "/v1/tiktok-shop/product-reviews", credits: 16, summary: "Customer reviews for a TikTok Shop product.", params: [url("TikTok Shop product URL."), limit(20, 200)] },
  { tool: "tiktok_shop_user_showcase", name: "TikTok Shop User Showcase", path: "/v1/tiktok-shop/user-showcase", credits: 16, summary: "Products promoted in a TikTok creator showcase.", params: [{ name: "username", type: "string", required: true, description: "TikTok username with or without @." }, limit(20, 200)] },
];

const GITHUB: Omit<Endpoint, "platform">[] = [
  { tool: "github_user", name: "GitHub User", path: "/v1/github/user", credits: 1, summary: "Public GitHub user profile details.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }] },
  { tool: "github_repositories", name: "GitHub Repositories", path: "/v1/github/repositories", credits: 3, summary: "List a GitHub user's repositories.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, limit(30, 100)] },
  { tool: "github_repository", name: "GitHub Repository", path: "/v1/github/repository", credits: 1, summary: "Repository details, stars, forks and metadata.", params: [{ name: "repo", type: "string", required: true, description: "Repository URL or owner/name." }] },
  { tool: "github_pull_requests", name: "GitHub Pull Requests", path: "/v1/github/pull-requests", credits: 3, summary: "List repository pull requests.", params: [{ name: "repo", type: "string", required: true, description: "Repository URL or owner/name." }, { name: "state", type: "string", required: false, description: "open, closed, or all. Default open." }, limit(30, 100)] },
  { tool: "github_activity", name: "GitHub Activity", path: "/v1/github/activity", credits: 3, summary: "Recent public activity for a GitHub user.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, limit(30, 100)] },
  { tool: "github_followers", name: "GitHub Followers", path: "/v1/github/followers", credits: 3, summary: "List GitHub followers.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, limit(30, 100)] },
  { tool: "github_following", name: "GitHub Following", path: "/v1/github/following", credits: 3, summary: "List accounts a GitHub user follows.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }, limit(30, 100)] },
  { tool: "github_contributions", name: "GitHub Contributions", path: "/v1/github/contributions", credits: 2, summary: "Summary of recent public GitHub contributions.", params: [{ name: "username", type: "string", required: true, description: "GitHub username or profile URL." }] },
  { tool: "github_trending_repositories", name: "GitHub Trending Repositories", path: "/v1/github/trending-repositories", credits: 2, summary: "Search trending repositories by stars or query.", params: [q("GitHub repository search query. Default stars:>1000."), limit(20, 100)] },
  { tool: "github_trending_developers", name: "GitHub Trending Developers", path: "/v1/github/trending-developers", credits: 2, summary: "Search popular GitHub developers.", params: [q("GitHub user search query. Default followers:>1000."), limit(20, 100)] },
];

const AD_LIBRARY: Omit<Endpoint, "platform">[] = [
  { tool: "facebook_ad_library_search", name: "Facebook Ad Library Search", path: "/v1/ad-library/facebook/search", credits: 20, summary: "Search Meta/Facebook ads by keyword.", params: [q(), { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(20, 200)] },
  { tool: "facebook_ad_library_company_ads", name: "Facebook Company Ads", path: "/v1/ad-library/facebook/company-ads", credits: 20, summary: "Ads for a Facebook page or Meta Ad Library URL.", params: [url("Facebook page URL or Meta Ad Library URL."), { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(20, 200)] },
  { tool: "facebook_ad_library_ad_details", name: "Facebook Ad Details", path: "/v1/ad-library/facebook/ad-details", credits: 2, summary: "Meta/Facebook ad details.", params: [url("Meta Ad Library ad URL.")] },
  { tool: "tiktok_ad_library_search", name: "TikTok Ad Library Search", path: "/v1/ad-library/tiktok/search", credits: 20, summary: "Search TikTok Ad Library and Creative Center.", params: [q(), { name: "country", type: "string", required: false, description: "ISO country code. Default DE." }, limit(20, 200)] },
  { tool: "tiktok_ad_library_ad_details", name: "TikTok Ad Details", path: "/v1/ad-library/tiktok/ad-details", credits: 2, summary: "TikTok ad details by ad URL or ID.", params: [url("TikTok Ad Library URL or ad ID."), { name: "country", type: "string", required: false, description: "ISO country code. Default DE." }] },
  { tool: "google_ad_library_company_ads", name: "Google Company Ads", path: "/v1/ad-library/google/company-ads", credits: 20, summary: "Google Ads Transparency Center ads for an advertiser.", params: [{ name: "advertiser", type: "string", required: true, description: "Advertiser name, domain, or Google advertiser ID." }, { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(20, 200)] },
  { tool: "google_ad_library_ad_details", name: "Google Ad Details", path: "/v1/ad-library/google/ad-details", credits: 2, summary: "Google ad details by Transparency Center URL.", params: [{ name: "creative_id", type: "string", required: true, description: "Google Ads Transparency Center URL containing AR advertiser ID and CR creative ID." }, { name: "country", type: "string", required: false, description: "ISO country code. Default US." }] },
  { tool: "google_ad_library_advertiser_search", name: "Google Advertiser Search", path: "/v1/ad-library/google/advertiser-search", credits: 10, summary: "Search Google Ads advertisers.", params: [q(), { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(10, 50)] },
  { tool: "linkedin_ad_library_search_ads", name: "LinkedIn Ad Library Search", path: "/v1/ad-library/linkedin/search-ads", credits: 20, summary: "Search LinkedIn Ad Library ads.", params: [q(), { name: "country", type: "string", required: false, description: "ISO country code. Default US." }, limit(20, 200)] },
  { tool: "linkedin_ad_library_ad_details", name: "LinkedIn Ad Details", path: "/v1/ad-library/linkedin/ad-details", credits: 2, summary: "LinkedIn ad details by URL or ID.", params: [url("LinkedIn Ad Library URL or ad ID.")] },
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
  ...withPlatform(AD_LIBRARY, "ad_library"),
];

/** A concise, agent-facing description (summary + cost) for an endpoint. */
export function describe(e: Endpoint): string {
  return `${e.summary} Costs ~${e.credits} credit${e.credits === 1 ? "" : "s"}; cached results are free, failures are never charged.`;
}
