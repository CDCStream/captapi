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
  | "ad_library";

export type Category =
  | "transcript"
  | "summarize"
  | "details"
  | "comments"
  | "channel"
  | "search"
  | "list"
  | "download";

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
    | "megaphone";
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
  { slug: "youtube-playlist-videos", name: "YouTube Playlist Videos API", shortName: "Playlist Videos", category: "list", method: "GET", path: "/v1/youtube/playlist-videos", credits: 50, creditsPerResult: 1 },
  { slug: "youtube-video-download", name: "YouTube Video Download API", shortName: "Video Download", category: "download", method: "GET", path: "/v1/youtube/video-download", credits: 3 },
  { slug: "youtube-shorts-transcript", name: "YouTube Shorts Transcript API", shortName: "Shorts Transcript", category: "transcript", method: "GET", path: "/v1/youtube/shorts/transcript", credits: 2 },
  { slug: "youtube-shorts-summarizer", name: "YouTube Shorts Summarizer API", shortName: "Shorts Summarizer", category: "summarize", method: "GET", path: "/v1/youtube/shorts/summarize", credits: 4 },
  { slug: "youtube-shorts-stats", name: "YouTube Shorts Stats API", shortName: "Shorts Stats", category: "details", method: "GET", path: "/v1/youtube/shorts/video-details", credits: 1 },
  { slug: "youtube-shorts-comments", name: "YouTube Shorts Comments API", shortName: "Shorts Comments", category: "comments", method: "GET", path: "/v1/youtube/shorts/comments", credits: 20, creditsPerResult: 0.4 },
  { slug: "youtube-channel-shorts", name: "YouTube Channel Shorts API", shortName: "Channel Shorts", category: "list", method: "GET", path: "/v1/youtube/channel-shorts", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-channel-streams", name: "YouTube Channel Streams API", shortName: "Channel Streams", category: "list", method: "GET", path: "/v1/youtube/channel-streams", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-hashtag-search", name: "YouTube Hashtag Search API", shortName: "Hashtag Search", category: "search", method: "GET", path: "/v1/youtube/hashtag-search", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-comment-replies", name: "YouTube Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/youtube/comment-replies", credits: 20, creditsPerResult: 0.4 },
  { slug: "youtube-channel-playlists", name: "YouTube Channel Playlists API", shortName: "Channel Playlists", category: "list", method: "GET", path: "/v1/youtube/channel-playlists", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-community-posts", name: "YouTube Community Posts API", shortName: "Community Posts", category: "list", method: "GET", path: "/v1/youtube/community-posts", credits: 10, creditsPerResult: 0.5 },
  { slug: "youtube-video-sponsors", name: "YouTube Video Sponsors API", shortName: "Video Sponsors", category: "details", method: "GET", path: "/v1/youtube/video-sponsors", credits: 1 },
];

const TIKTOK: Spec[] = [
  { slug: "tiktok-transcript", name: "TikTok Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/tiktok/transcript", credits: 2 },
  { slug: "tiktok-summarizer", name: "TikTok Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/tiktok/summarize", credits: 4 },
  { slug: "tiktok-video-details", name: "TikTok Video Details API", shortName: "Video Details", category: "details", method: "GET", path: "/v1/tiktok/video-details", credits: 1 },
  { slug: "tiktok-comments", name: "TikTok Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/tiktok/comments", credits: 10, creditsPerResult: 0.2 },
  { slug: "tiktok-channel-details", name: "TikTok Channel Details API", shortName: "Channel Details", category: "channel", method: "GET", path: "/v1/tiktok/channel-details", credits: 1 },
  { slug: "tiktok-search", name: "TikTok Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/tiktok/search", credits: 14, creditsPerResult: 0.7 },
  { slug: "tiktok-video-download", name: "TikTok Video Download API", shortName: "Video Download", category: "download", method: "GET", path: "/v1/tiktok/video-download", credits: 3 },
  { slug: "tiktok-channel-posts", name: "TikTok Channel Posts API", shortName: "Channel Posts", category: "list", method: "GET", path: "/v1/tiktok/channel-posts", credits: 14, creditsPerResult: 0.7 },
  { slug: "tiktok-comment-replies", name: "TikTok Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/tiktok/comment-replies", credits: 50 },
  { slug: "tiktok-user-followers", name: "TikTok User Followers API", shortName: "User Followers", category: "list", method: "GET", path: "/v1/tiktok/user-followers", credits: 20, creditsPerResult: 0.4 },
  { slug: "tiktok-user-followings", name: "TikTok User Followings API", shortName: "User Followings", category: "list", method: "GET", path: "/v1/tiktok/user-followings", credits: 20, creditsPerResult: 0.4 },
  { slug: "tiktok-music-posts", name: "TikTok Music Posts API", shortName: "Music Posts", category: "list", method: "GET", path: "/v1/tiktok/music-posts", credits: 32, creditsPerResult: 1.6 },
  { slug: "tiktok-hashtag-search", name: "TikTok Hashtag Search API", shortName: "Hashtag Search", category: "search", method: "GET", path: "/v1/tiktok/hashtag-search", credits: 14, creditsPerResult: 0.7 },
  { slug: "tiktok-top-search", name: "TikTok Top Search API", shortName: "Top Search", category: "search", method: "GET", path: "/v1/tiktok/top-search", credits: 14, creditsPerResult: 0.7 },
  { slug: "tiktok-user-search", name: "TikTok User Search API", shortName: "User Search", category: "search", method: "GET", path: "/v1/tiktok/user-search", credits: 8, creditsPerResult: 0.4 },
  { slug: "tiktok-song-details", name: "TikTok Song Details API", shortName: "Song Details", category: "details", method: "GET", path: "/v1/tiktok/song-details", credits: 2 },
  { slug: "tiktok-trending-feed", name: "TikTok Trending Feed API", shortName: "Trending Feed", category: "list", method: "GET", path: "/v1/tiktok/trending-feed", credits: 14, creditsPerResult: 0.7 },
  { slug: "tiktok-popular-hashtags", name: "TikTok Popular Hashtags API", shortName: "Popular Hashtags", category: "list", method: "GET", path: "/v1/tiktok/popular-hashtags", credits: 14, creditsPerResult: 0.7 },
  { slug: "tiktok-live", name: "TikTok Live API", shortName: "Live", category: "details", method: "GET", path: "/v1/tiktok/live", credits: 1 },
];

const INSTAGRAM: Spec[] = [
  { slug: "instagram-transcript", name: "Instagram Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/instagram/transcript", credits: 2 },
  { slug: "instagram-summarizer", name: "Instagram Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/instagram/summarize", credits: 4 },
  { slug: "instagram-details", name: "Instagram Details API", shortName: "Details", category: "details", method: "GET", path: "/v1/instagram/details", credits: 1 },
  { slug: "instagram-comments", name: "Instagram Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/instagram/comments", credits: 45, creditsPerResult: 0.9 },
  { slug: "instagram-channel-details", name: "Instagram Channel Details API", shortName: "Channel Details", category: "channel", method: "GET", path: "/v1/instagram/channel-details", credits: 1 },
  { slug: "instagram-channel-posts", name: "Instagram Channel Posts API", shortName: "Channel Posts", category: "list", method: "GET", path: "/v1/instagram/channel-posts", credits: 12, creditsPerResult: 0.6 },
  { slug: "instagram-channel-reels", name: "Instagram Channel Reels API", shortName: "Channel Reels", category: "list", method: "GET", path: "/v1/instagram/channel-reels", credits: 12, creditsPerResult: 0.6 },
  { slug: "instagram-reels-search", name: "Instagram Reels Search API", shortName: "Reels Search", category: "search", method: "GET", path: "/v1/instagram/reels-search", credits: 12, creditsPerResult: 0.6 },
  { slug: "instagram-video-download", name: "Instagram Video Download API", shortName: "Video Download", category: "download", method: "GET", path: "/v1/instagram/video-download", credits: 3 },
  { slug: "instagram-tagged-posts", name: "Instagram Tagged Posts API", shortName: "Tagged Posts", category: "list", method: "GET", path: "/v1/instagram/tagged-posts", credits: 18, creditsPerResult: 0.9 },
  { slug: "instagram-music-posts", name: "Instagram Music Posts API", shortName: "Music Posts", category: "list", method: "GET", path: "/v1/instagram/music-posts", credits: 18, creditsPerResult: 0.9 },
  { slug: "instagram-hashtag-search", name: "Instagram Hashtag Search API", shortName: "Hashtag Search", category: "search", method: "GET", path: "/v1/instagram/hashtag-search", credits: 12, creditsPerResult: 0.6 },
  { slug: "instagram-profile-search", name: "Instagram Profile Search API", shortName: "Profile Search", category: "search", method: "GET", path: "/v1/instagram/profile-search", credits: 12, creditsPerResult: 0.6 },
  { slug: "instagram-story-highlights", name: "Instagram Story Highlights API", shortName: "Story Highlights", category: "list", method: "GET", path: "/v1/instagram/story-highlights", credits: 5 },
  { slug: "instagram-highlights-details", name: "Instagram Highlights Details API", shortName: "Highlights Details", category: "list", method: "GET", path: "/v1/instagram/highlights-details", credits: 9, creditsPerResult: 0.9 },
  { slug: "instagram-embed", name: "Instagram Embed API", shortName: "Embed", category: "details", method: "GET", path: "/v1/instagram/embed", credits: 1 },
  { slug: "instagram-basic-profile", name: "Instagram Basic Profile API", shortName: "Basic Profile", category: "channel", method: "GET", path: "/v1/instagram/basic-profile", credits: 1 },
];

const FACEBOOK: Spec[] = [
  { slug: "facebook-details", name: "Facebook Details API", shortName: "Details", category: "details", method: "GET", path: "/v1/facebook/details", credits: 1 },
  { slug: "facebook-transcript", name: "Facebook Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/facebook/transcript", credits: 2 },
  { slug: "facebook-summarizer", name: "Facebook Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/facebook/summarize", credits: 4 },
  { slug: "facebook-comments", name: "Facebook Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/facebook/comments", credits: 30, creditsPerResult: 0.6 },
  { slug: "facebook-page-details", name: "Facebook Page Details API", shortName: "Page Details", category: "channel", method: "GET", path: "/v1/facebook/page-details", credits: 1 },
  { slug: "facebook-profile-posts", name: "Facebook Profile Posts API", shortName: "Profile Posts", category: "list", method: "GET", path: "/v1/facebook/profile-posts", credits: 12, creditsPerResult: 0.6 },
  { slug: "facebook-profile-reels", name: "Facebook Profile Reels API", shortName: "Profile Reels", category: "list", method: "GET", path: "/v1/facebook/profile-reels", credits: 36, creditsPerResult: 1.8 },
  { slug: "facebook-group-posts", name: "Facebook Group Posts API", shortName: "Group Posts", category: "list", method: "GET", path: "/v1/facebook/group-posts", credits: 12, creditsPerResult: 0.6 },
  { slug: "facebook-comment-replies", name: "Facebook Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/facebook/comment-replies", credits: 30, creditsPerResult: 0.6 },
  { slug: "facebook-marketplace-search", name: "Facebook Marketplace Search API", shortName: "Marketplace Search", category: "search", method: "GET", path: "/v1/facebook/marketplace-search", credits: 20, creditsPerResult: 1 },
  { slug: "facebook-event-search", name: "Facebook Event Search API", shortName: "Event Search", category: "search", method: "GET", path: "/v1/facebook/event-search", credits: 40, creditsPerResult: 2 },
  { slug: "facebook-event-details", name: "Facebook Event Details API", shortName: "Event Details", category: "details", method: "GET", path: "/v1/facebook/event-details", credits: 2 },
  { slug: "facebook-profile-photos", name: "Facebook Profile Photos API", shortName: "Profile Photos", category: "list", method: "GET", path: "/v1/facebook/profile-photos", credits: 12, creditsPerResult: 0.6 },
  { slug: "facebook-marketplace-item", name: "Facebook Marketplace Item API", shortName: "Marketplace Item", category: "details", method: "GET", path: "/v1/facebook/marketplace-item", credits: 1 },
];

const TWITTER: Spec[] = [
  { slug: "twitter-tweet-details", name: "Twitter/X Tweet Details API", shortName: "Tweet Details", category: "details", method: "GET", path: "/v1/twitter/tweet-details", credits: 1 },
  { slug: "twitter-profile", name: "Twitter/X Profile API", shortName: "Profile", category: "channel", method: "GET", path: "/v1/twitter/profile", credits: 1 },
  { slug: "twitter-user-tweets", name: "Twitter/X User Tweets API", shortName: "User Tweets", category: "list", method: "GET", path: "/v1/twitter/user-tweets", credits: 14, creditsPerResult: 0.7 },
  { slug: "twitter-search", name: "Twitter/X Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/twitter/search", credits: 14, creditsPerResult: 0.7 },
  { slug: "twitter-community", name: "Twitter/X Community API", shortName: "Community", category: "details", method: "GET", path: "/v1/twitter/community", credits: 1 },
  { slug: "twitter-community-tweets", name: "Twitter/X Community Tweets API", shortName: "Community Tweets", category: "list", method: "GET", path: "/v1/twitter/community-tweets", credits: 18, creditsPerResult: 0.7 },
];

const REDDIT: Spec[] = [
  { slug: "reddit-subreddit-posts", name: "Reddit Subreddit Posts API", shortName: "Subreddit Posts", category: "list", method: "GET", path: "/v1/reddit/subreddit-posts", credits: 10, creditsPerResult: 0.4 },
  { slug: "reddit-post-details", name: "Reddit Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/reddit/post-details", credits: 1 },
  { slug: "reddit-post-comments", name: "Reddit Post Comments API", shortName: "Post Comments", category: "comments", method: "GET", path: "/v1/reddit/post-comments", credits: 20, creditsPerResult: 0.4 },
  { slug: "reddit-search", name: "Reddit Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/reddit/search", credits: 10, creditsPerResult: 0.4 },
  { slug: "reddit-subreddit-details", name: "Reddit Subreddit Details API", shortName: "Subreddit Details", category: "details", method: "GET", path: "/v1/reddit/subreddit-details", credits: 1 },
  { slug: "reddit-subreddit-search", name: "Reddit Subreddit Search API", shortName: "Subreddit Search", category: "search", method: "GET", path: "/v1/reddit/subreddit-search", credits: 10, creditsPerResult: 0.4 },
];

const THREADS: Spec[] = [
  { slug: "threads-profile", name: "Threads Profile API", shortName: "Profile", category: "channel", method: "GET", path: "/v1/threads/profile", credits: 1 },
  { slug: "threads-user-posts", name: "Threads User Posts API", shortName: "User Posts", category: "list", method: "GET", path: "/v1/threads/user-posts", credits: 14, creditsPerResult: 0.7 },
  { slug: "threads-post-details", name: "Threads Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/threads/post-details", credits: 1 },
  { slug: "threads-search", name: "Threads Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/threads/search", credits: 18, creditsPerResult: 0.7 },
  { slug: "threads-search-users", name: "Threads Search Users API", shortName: "Search Users", category: "search", method: "GET", path: "/v1/threads/search-users", credits: 14, creditsPerResult: 0.7 },
];

const BLUESKY: Spec[] = [
  { slug: "bluesky-profile", name: "Bluesky Profile API", shortName: "Profile", category: "channel", method: "GET", path: "/v1/bluesky/profile", credits: 1 },
  { slug: "bluesky-user-posts", name: "Bluesky User Posts API", shortName: "User Posts", category: "list", method: "GET", path: "/v1/bluesky/user-posts", credits: 3, creditsPerResult: 0.1 },
  { slug: "bluesky-post-details", name: "Bluesky Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/bluesky/post-details", credits: 1 },
];

const PINTEREST: Spec[] = [
  { slug: "pinterest-pin-details", name: "Pinterest Pin Details API", shortName: "Pin Details", category: "details", method: "GET", path: "/v1/pinterest/pin-details", credits: 1 },
  { slug: "pinterest-user-pins", name: "Pinterest User Pins API", shortName: "User Pins", category: "list", method: "GET", path: "/v1/pinterest/user-pins", credits: 13, creditsPerResult: 0.5 },
  { slug: "pinterest-search", name: "Pinterest Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/pinterest/search", credits: 13, creditsPerResult: 0.5 },
  { slug: "pinterest-board", name: "Pinterest Board API", shortName: "Board", category: "list", method: "GET", path: "/v1/pinterest/board", credits: 13, creditsPerResult: 0.5 },
  { slug: "pinterest-user-boards", name: "Pinterest User Boards API", shortName: "User Boards", category: "list", method: "GET", path: "/v1/pinterest/user-boards", credits: 13, creditsPerResult: 0.5 },
];

const LINKEDIN: Spec[] = [
  { slug: "linkedin-profile", name: "LinkedIn Profile API", shortName: "Profile", category: "channel", method: "GET", path: "/v1/linkedin/profile", credits: 2 },
  { slug: "linkedin-company", name: "LinkedIn Company API", shortName: "Company", category: "channel", method: "GET", path: "/v1/linkedin/company", credits: 2 },
  { slug: "linkedin-post-details", name: "LinkedIn Post Details API", shortName: "Post Details", category: "details", method: "GET", path: "/v1/linkedin/post-details", credits: 1 },
  { slug: "linkedin-company-posts", name: "LinkedIn Company Posts API", shortName: "Company Posts", category: "list", method: "GET", path: "/v1/linkedin/company-posts", credits: 16, creditsPerResult: 0.8 },
  { slug: "linkedin-search-posts", name: "LinkedIn Search Posts API", shortName: "Search Posts", category: "search", method: "GET", path: "/v1/linkedin/search-posts", credits: 16, creditsPerResult: 0.8 },
];

const RUMBLE: Spec[] = [
  { slug: "rumble-video-details", name: "Rumble Video Details API", shortName: "Video Details", category: "details", method: "GET", path: "/v1/rumble/video-details", credits: 1 },
  { slug: "rumble-channel-videos", name: "Rumble Channel Videos API", shortName: "Channel Videos", category: "list", method: "GET", path: "/v1/rumble/channel-videos", credits: 12, creditsPerResult: 0.6 },
  { slug: "rumble-search", name: "Rumble Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/rumble/search", credits: 12, creditsPerResult: 0.6 },
  { slug: "rumble-transcript", name: "Rumble Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/rumble/transcript", credits: 3 },
  { slug: "rumble-comments", name: "Rumble Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/rumble/comments", credits: 30, creditsPerResult: 0.6 },
];

const TIKTOK_SHOP: Spec[] = [
  { slug: "tiktok-shop-search", name: "TikTok Shop Search API", shortName: "Shop Search", category: "search", method: "GET", path: "/v1/tiktok-shop/shop-search", credits: 16, creditsPerResult: 0.8 },
  { slug: "tiktok-shop-products", name: "TikTok Shop Products API", shortName: "Shop Products", category: "list", method: "GET", path: "/v1/tiktok-shop/shop-products", credits: 16, creditsPerResult: 0.8 },
  { slug: "tiktok-shop-product-details", name: "TikTok Shop Product Details API", shortName: "Product Details", category: "details", method: "GET", path: "/v1/tiktok-shop/product-details", credits: 2 },
  { slug: "tiktok-shop-product-reviews", name: "TikTok Shop Product Reviews API", shortName: "Product Reviews", category: "comments", method: "GET", path: "/v1/tiktok-shop/product-reviews", credits: 16, creditsPerResult: 0.8 },
  { slug: "tiktok-shop-user-showcase", name: "TikTok Shop User Showcase API", shortName: "User Showcase", category: "list", method: "GET", path: "/v1/tiktok-shop/user-showcase", credits: 16, creditsPerResult: 0.8 },
];

const GITHUB: Spec[] = [
  { slug: "github-user", name: "GitHub User API", shortName: "User", category: "channel", method: "GET", path: "/v1/github/user", credits: 1 },
  { slug: "github-repositories", name: "GitHub Repositories API", shortName: "Repositories", category: "list", method: "GET", path: "/v1/github/repositories", credits: 3, creditsPerResult: 0.1 },
  { slug: "github-pull-requests", name: "GitHub Pull Requests API", shortName: "Pull Requests", category: "list", method: "GET", path: "/v1/github/pull-requests", credits: 3, creditsPerResult: 0.1 },
  { slug: "github-activity", name: "GitHub Activity API", shortName: "Activity", category: "list", method: "GET", path: "/v1/github/activity", credits: 3, creditsPerResult: 0.1 },
  { slug: "github-followers", name: "GitHub Followers API", shortName: "Followers", category: "list", method: "GET", path: "/v1/github/followers", credits: 3, creditsPerResult: 0.1 },
  { slug: "github-following", name: "GitHub Following API", shortName: "Following", category: "list", method: "GET", path: "/v1/github/following", credits: 3, creditsPerResult: 0.1 },
  { slug: "github-contributions", name: "GitHub Contributions API", shortName: "Contributions", category: "details", method: "GET", path: "/v1/github/contributions", credits: 2 },
  { slug: "github-repository", name: "GitHub Repository API", shortName: "Repository", category: "details", method: "GET", path: "/v1/github/repository", credits: 1 },
  { slug: "github-trending-repositories", name: "GitHub Trending Repositories API", shortName: "Trending Repositories", category: "search", method: "GET", path: "/v1/github/trending-repositories", credits: 2, creditsPerResult: 0.1 },
  { slug: "github-trending-developers", name: "GitHub Trending Developers API", shortName: "Trending Developers", category: "search", method: "GET", path: "/v1/github/trending-developers", credits: 2, creditsPerResult: 0.1 },
];

const AD_LIBRARY: Spec[] = [
  { slug: "facebook-ad-library-search", name: "Facebook Ad Library Search API", shortName: "Facebook Search", category: "search", method: "GET", path: "/v1/ad-library/facebook/search", credits: 20, creditsPerResult: 1 },
  { slug: "facebook-ad-library-company-ads", name: "Facebook Company Ads API", shortName: "Facebook Company Ads", category: "list", method: "GET", path: "/v1/ad-library/facebook/company-ads", credits: 20, creditsPerResult: 1 },
  { slug: "facebook-ad-library-search-companies", name: "Facebook Ad Library Search Companies API", shortName: "Facebook Search Companies", category: "search", method: "GET", path: "/v1/ad-library/facebook/search-companies", credits: 20, creditsPerResult: 1 },
  { slug: "facebook-ad-library-ad-details", name: "Facebook Ad Details API", shortName: "Facebook Ad Details", category: "details", method: "GET", path: "/v1/ad-library/facebook/ad-details", credits: 2 },
  { slug: "tiktok-ad-library-search", name: "TikTok Ad Library Search API", shortName: "TikTok Search", category: "search", method: "GET", path: "/v1/ad-library/tiktok/search", credits: 20, creditsPerResult: 1 },
  { slug: "tiktok-ad-library-ad-details", name: "TikTok Ad Details API", shortName: "TikTok Ad Details", category: "details", method: "GET", path: "/v1/ad-library/tiktok/ad-details", credits: 2 },
  { slug: "google-ad-library-company-ads", name: "Google Company Ads API", shortName: "Google Company Ads", category: "list", method: "GET", path: "/v1/ad-library/google/company-ads", credits: 20, creditsPerResult: 1 },
  { slug: "google-ad-library-ad-details", name: "Google Ad Details API", shortName: "Google Ad Details", category: "details", method: "GET", path: "/v1/ad-library/google/ad-details", credits: 2 },
  { slug: "google-ad-library-advertiser-search", name: "Google Advertiser Search API", shortName: "Google Advertiser Search", category: "search", method: "GET", path: "/v1/ad-library/google/advertiser-search", credits: 10, creditsPerResult: 1 },
  { slug: "linkedin-ad-library-search-ads", name: "LinkedIn Ad Library Search API", shortName: "LinkedIn Search Ads", category: "search", method: "GET", path: "/v1/ad-library/linkedin/search-ads", credits: 20, creditsPerResult: 1 },
  { slug: "linkedin-ad-library-ad-details", name: "LinkedIn Ad Details API", shortName: "LinkedIn Ad Details", category: "details", method: "GET", path: "/v1/ad-library/linkedin/ad-details", credits: 2 },
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

export function getGroup(id: PlatformId): PlatformGroup {
  return PLATFORM_GROUPS.find((g) => g.id === id)!;
}

export function relatedEndpoints(slug: string, max = 6): ApiEndpoint[] {
  const ep = getEndpoint(slug);
  if (!ep) return [];
  return getGroup(ep.platform)
    .endpoints.filter((e) => e.slug !== slug)
    .slice(0, max);
}

// ---------------------------------------------------------------------------
// Derived content
// ---------------------------------------------------------------------------

const ACTION: Record<Category, string> = {
  transcript: "extract the full, timestamped transcript",
  summarize: "generate an AI summary with key points and topics",
  details: "fetch full metadata and engagement stats",
  comments: "pull comments with author, text, likes, and replies",
  channel: "fetch profile/channel details and audience stats",
  search: "search and return matching results",
  list: "list items in bulk with metadata",
  download: "get a direct, no-watermark download URL",
};

export function platformLabel(p: PlatformId): string {
  return PLATFORM_LABEL[p];
}

/**
 * Natural "How to …" predicate for an endpoint, used by /how-to/[slug] pSEO
 * pages (e.g. "get a YouTube transcript", "download a TikTok video").
 */
export function howToAction(ep: ApiEndpoint): string {
  const p = PLATFORM_LABEL[ep.platform];
  const sn = ep.shortName.toLowerCase();
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
    case "download":
      return `download a ${p} ${sn.replace("video download", "video")}`;
  }
}

/** Page title for the how-to guide, e.g. "How to get a YouTube transcript". */
export function howToTitle(ep: ApiEndpoint): string {
  return `How to ${howToAction(ep)}`;
}

export function tagline(ep: ApiEndpoint): string {
  const platform = PLATFORM_LABEL[ep.platform];
  switch (ep.category) {
    case "transcript":
      return `Extract timestamped transcripts from any public ${platform} video in a single request.`;
    case "summarize":
      return `Turn any ${platform} video into an AI summary with key points, topics, and sentiment.`;
    case "details":
      return `Get full ${platform} video metadata — title, views, likes, duration, and more.`;
    case "comments":
      return `Pull ${platform} comments at scale with author, text, likes, and reply threads.`;
    case "channel":
      return `Fetch ${platform} profile data — follower counts, bio, verification, and stats.`;
    case "search":
      return `Search ${platform} programmatically and get structured, ranked results.`;
    case "list":
      return `Bulk-list ${platform} content with full metadata for each item.`;
    case "download":
      return `Get a direct, watermark-free download URL for any public ${platform} video.`;
  }
}

export function longDescription(ep: ApiEndpoint): string {
  const platform = PLATFORM_LABEL[ep.platform];
  return `The ${ep.name} lets you ${ACTION[ep.category]} from ${platform} with a single REST call. No OAuth, no scraping infrastructure, and no platform SDKs — send the URL, get clean structured JSON back. Results are cached for 24 hours, so repeat lookups are instant and free.`;
}

export function delivers(ep: ApiEndpoint): string[] {
  if (ep.delivers) return ep.delivers;
  switch (ep.category) {
    case "transcript":
      return [
        "Full transcript text with start/end timestamps",
        "Auto-detected language and segment count",
        "AI audio transcription fallback when no captions exist",
        "Clean JSON ready for RAG, search, or subtitles",
      ];
    case "summarize":
      return [
        "2–3 paragraph AI summary of the video",
        "4–8 bullet key points and detected topics",
        "Overall sentiment and tone",
        "Powered by the transcript under the hood",
      ];
    case "details":
      return [
        "Title, description, and thumbnail URLs",
        "View, like, comment, and share counts",
        "Duration, publish date, and author handle",
        "Stable IDs for joining with other endpoints",
      ];
    case "comments":
      return [
        "Comment text, author name, and handle",
        "Like counts and reply threads",
        "Pagination via the limit parameter",
        "Timestamps for trend and sentiment analysis",
      ];
    case "channel":
      return [
        "Display name, handle, bio, and avatar",
        "Follower / subscriber and content counts",
        "Verification status and external links",
        "Aggregate engagement signals",
      ];
    case "search":
      return [
        "Ranked, structured result list",
        "Title, URL, author, and thumbnail per result",
        "Engagement metrics where available",
        "Configurable result limit",
      ];
    case "list":
      return [
        "Bulk list of items with full metadata",
        "View counts, dates, and direct URLs",
        "Configurable result limit",
        "Ideal for monitoring and content pipelines",
      ];
    case "download":
      return [
        "Direct, watermark-free media URL",
        "Available quality/format variants",
        "File size and duration metadata",
        "Short-lived signed link",
      ];
  }
}

// --- Precise, per-endpoint input parameters -------------------------------
// These mirror the backend routers exactly so every endpoint page, the docs,
// and the MCP "Agent Integrations" tab show the correct inputs.

const up = (description: string): ApiParam => ({ name: "url", type: "string", required: true, description });
const qp = (description = "Search query or keywords (min 2 characters)."): ApiParam => ({ name: "q", type: "string", required: true, description });
const lp = (def: number, max: number): ApiParam => ({ name: "limit", type: "integer", required: false, description: `Max items to return (default ${def}, max ${max}). Billed per result.` });
const lang = (): ApiParam => ({ name: "language", type: "string", required: false, description: 'Preferred caption language as an ISO code, e.g. "en". Defaults to auto-detect.' });
const cid = (): ApiParam => ({ name: "comment_id", type: "string", required: true, description: "ID of the parent comment to fetch replies for (from the comments endpoint)." });

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

const ENDPOINT_PARAMS: Record<string, ApiParam[]> = {
  // YouTube
  "youtube-transcript": [up(YT_VIDEO), lang()],
  "youtube-summarizer": [up(YT_VIDEO), lang()],
  "youtube-video-details": [up(YT_VIDEO)],
  "youtube-comments": [up(YT_VIDEO), lp(50, 500)],
  "youtube-channel-details": [up(YT_CHANNEL)],
  "youtube-search": [qp(), lp(20, 200)],
  "youtube-channel-videos": [up(YT_CHANNEL), lp(20, 200)],
  "youtube-playlist-videos": [up("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."), lp(50, 500)],
  "youtube-video-download": [up(YT_VIDEO)],
  "youtube-shorts-transcript": [up(YT_SHORTS), lang()],
  "youtube-shorts-summarizer": [up(YT_SHORTS), lang()],
  "youtube-shorts-stats": [up(YT_SHORTS)],
  "youtube-shorts-comments": [up(YT_SHORTS), lp(50, 500)],
  "youtube-channel-shorts": [up(YT_CHANNEL), lp(20, 200)],
  "youtube-channel-streams": [up(YT_CHANNEL), lp(20, 200)],
  "youtube-hashtag-search": [qp("Hashtag with or without the # (min 2 characters)."), lp(20, 200)],
  "youtube-comment-replies": [up(YT_VIDEO), cid(), lp(50, 500)],
  "youtube-channel-playlists": [up(YT_CHANNEL), lp(20, 200)],
  "youtube-community-posts": [up(YT_CHANNEL), lp(20, 200)],
  "youtube-video-sponsors": [up(YT_VIDEO)],
  // TikTok
  "tiktok-transcript": [up(TT_VIDEO)],
  "tiktok-summarizer": [up(TT_VIDEO)],
  "tiktok-video-details": [up(TT_VIDEO)],
  "tiktok-comments": [up(TT_VIDEO), lp(50, 500)],
  "tiktok-channel-details": [up(TT_PROFILE)],
  "tiktok-search": [qp(), lp(20, 200)],
  "tiktok-video-download": [up(TT_VIDEO)],
  "tiktok-channel-posts": [up(TT_PROFILE), lp(20, 200)],
  "tiktok-comment-replies": [up(TT_VIDEO), cid(), lp(50, 500)],
  "tiktok-user-followers": [up(TT_PROFILE), lp(50, 500)],
  "tiktok-user-followings": [up(TT_PROFILE), lp(50, 500)],
  "tiktok-music-posts": [up(TT_MUSIC), lp(20, 200)],
  "tiktok-hashtag-search": [qp("Hashtag with or without the # (min 2 characters)."), lp(20, 200)],
  "tiktok-top-search": [qp(), lp(20, 200)],
  "tiktok-user-search": [qp(), lp(20, 100)],
  "tiktok-song-details": [up(TT_MUSIC)],
  "tiktok-trending-feed": [{ name: "country", type: "string", required: false, description: "Two-letter ISO country code, e.g. US, GB, TR. Default US." }, lp(20, 200)],
  "tiktok-popular-hashtags": [{ name: "query", type: "string", required: false, description: 'Topic or keyword to discover trending hashtags for. Default "trending".' }, lp(20, 100)],
  "tiktok-live": [up(TT_PROFILE)],
  // Instagram
  "instagram-transcript": [up(IG_REEL)],
  "instagram-summarizer": [up(IG_REEL)],
  "instagram-details": [up(IG_POST)],
  "instagram-comments": [up(IG_POST), lp(50, 500)],
  "instagram-channel-details": [up(IG_PROFILE)],
  "instagram-channel-posts": [up(IG_PROFILE), lp(20, 200)],
  "instagram-channel-reels": [up(IG_PROFILE), lp(20, 200)],
  "instagram-reels-search": [qp("Hashtag (without #) or keyword (min 2 characters)."), lp(20, 200)],
  "instagram-video-download": [up(IG_REEL)],
  "instagram-tagged-posts": [up(IG_PROFILE), lp(20, 200)],
  "instagram-music-posts": [up("Instagram audio/music page URL."), lp(20, 200)],
  "instagram-hashtag-search": [qp("Hashtag without the # (min 2 characters)."), lp(20, 200)],
  "instagram-profile-search": [qp(), lp(20, 100)],
  "instagram-story-highlights": [up(IG_PROFILE)],
  "instagram-highlights-details": [up(IG_PROFILE), { name: "limit", type: "integer", required: false, description: "Max highlights to expand (default 10, max 50)." }],
  "instagram-embed": [up(IG_POST)],
  "instagram-basic-profile": [up("Instagram profile URL or @handle.")],
  // Facebook
  "facebook-details": [up(FB_VIDEO)],
  "facebook-transcript": [up(FB_VIDEO)],
  "facebook-summarizer": [up(FB_VIDEO)],
  "facebook-comments": [up(FB_VIDEO), lp(50, 500)],
  "facebook-page-details": [up("Facebook page URL, e.g. https://facebook.com/PageName.")],
  "facebook-profile-posts": [up("Facebook profile or page URL."), lp(20, 200)],
  "facebook-profile-reels": [up("Facebook profile or page URL."), lp(20, 200)],
  "facebook-group-posts": [up("Public Facebook group URL, e.g. https://facebook.com/groups/ID."), lp(20, 200)],
  "facebook-comment-replies": [up("Facebook post URL the comment belongs to."), cid(), lp(50, 500)],
  "facebook-marketplace-search": [qp("Product or keyword to search Facebook Marketplace for."), { name: "location", type: "string", required: true, description: "City or place name, e.g. 'Austin, TX'." }, lp(20, 200), { name: "details", type: "string", required: false, description: "Set true to fetch full description, photos and coordinates per listing (slower, costs more)." }],
  "facebook-event-search": [qp("Topic and/or place, e.g. 'comedy Chicago'."), lp(20, 200)],
  "facebook-event-details": [up("Facebook event URL, e.g. https://facebook.com/events/ID.")],
  "facebook-profile-photos": [up("Facebook profile or page URL."), lp(20, 200)],
  "facebook-marketplace-item": [up("Facebook Marketplace item URL.")],
  // Twitter / X
  "twitter-tweet-details": [up("Public tweet URL, e.g. https://x.com/user/status/ID.")],
  "twitter-profile": [up("Twitter/X profile URL or @handle, e.g. https://x.com/username.")],
  "twitter-user-tweets": [up("Twitter/X profile URL or @handle."), lp(20, 200)],
  "twitter-search": [qp("Keywords or search query (min 2 characters)."), lp(20, 200)],
  "twitter-community": [up("X community URL (x.com/i/communities/ID) or community ID.")],
  "twitter-community-tweets": [up("X community URL (x.com/i/communities/ID) or community ID."), lp(25, 200)],
  // Reddit
  "reddit-subreddit-posts": [up("Subreddit URL, r/name, or bare name, e.g. r/technology."), lp(25, 200)],
  "reddit-post-details": [up("Reddit post URL, e.g. https://reddit.com/r/sub/comments/ID/...")],
  "reddit-post-comments": [up("Reddit post URL."), lp(50, 500)],
  "reddit-search": [qp("Keywords or search query (min 2 characters)."), lp(25, 200)],
  "reddit-subreddit-details": [up("Subreddit URL, r/name, or bare name, e.g. r/technology.")],
  "reddit-subreddit-search": [up("Subreddit URL, r/name, or bare name, e.g. r/technology."), qp("Keywords or search query (min 2 characters)."), lp(25, 200)],
  // Threads
  "threads-profile": [up("Threads profile URL or @handle, e.g. https://threads.net/@username.")],
  "threads-user-posts": [up("Threads profile URL or @handle."), lp(20, 100)],
  "threads-post-details": [up("Threads post URL, e.g. https://threads.net/@user/post/CODE.")],
  "threads-search": [qp("Keyword or phrase to search Threads (min 2 characters)."), lp(25, 200)],
  "threads-search-users": [qp("Keyword to find Threads users (min 2 characters)."), lp(20, 100)],
  // Bluesky
  "bluesky-profile": [up("Bluesky profile URL, @handle, or handle, e.g. bsky.app/profile/handle.")],
  "bluesky-user-posts": [up("Bluesky profile URL, @handle, or handle."), lp(25, 100)],
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
  // Rumble
  "rumble-video-details": [up("Rumble video URL, e.g. https://rumble.com/vXXXX-title.html.")],
  "rumble-channel-videos": [up("Rumble channel URL, e.g. https://rumble.com/c/name."), lp(20, 200)],
  "rumble-search": [qp("Keywords or search query (min 2 characters)."), lp(20, 200)],
};

export function params(ep: ApiEndpoint): ApiParam[] {
  const explicit = ENDPOINT_PARAMS[ep.slug];
  if (explicit) return explicit;
  // Fallback (should not happen for catalog endpoints): derive from category.
  const base: ApiParam[] = [];
  if (ep.category === "search") base.push(qp());
  else base.push(up(`Public ${PLATFORM_LABEL[ep.platform]} URL.`));
  if (["comments", "search", "list"].includes(ep.category)) base.push(lp(20, 200));
  if (ep.category === "transcript" || ep.category === "summarize") base.push(lang());
  return base;
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
    case "download":
      return {
        downloadUrl: "https://cdn.captapi.com/dl/abc123.mp4",
        format: "mp4",
        quality: "1080p",
        sizeBytes: 18432044,
        expiresIn: 3600,
      };
  }
}

export function exampleResponse(ep: ApiEndpoint): string {
  return JSON.stringify(
    { success: true, cached: false, creditsUsed: ep.credits, data: exampleData(ep) },
    null,
    2,
  );
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
};

/** A realistic example value for a single parameter of an endpoint. */
function exampleValue(ep: ApiEndpoint, p: ApiParam): string {
  switch (p.name) {
    case "q":
      return ep.platform === "youtube" ? "structured data api" : "skincare";
    case "query":
      return "skincare";
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
      if (d.includes("channel") || d.includes("profile") || d.includes("@handle"))
        return PROFILE_URL[ep.platform];
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
      a: `The ${ep.name} lets you ${ACTION[ep.category]} from a public ${platform} ${
        ep.category === "search" ? "query" : ep.category === "channel" ? "profile" : "video"
      } using one ${ep.method} request to ${ep.path}. It returns clean JSON — no OAuth or scraping setup required.`,
    },
    {
      q: `How many credits does the ${ep.name} cost?`,
      a: `Each successful call costs ${ep.credits} credit${ep.credits === 1 ? "" : "s"}. Responses are cached for 24 hours, and cached results cost 0 credits. Failed or empty results are never charged.`,
    },
    {
      q: `Do I need a ${platform} API key or OAuth?`,
      a: `No. A single Captapi key works across every platform Captapi supports — YouTube, TikTok, Instagram, Facebook, Twitter/X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, and Rumble. We handle proxies, rate limits, retries, and authentication for you.`,
    },
  ];

  if (ep.category === "transcript") {
    list.push({
      q: `What if the ${platform} video has no captions?`,
      a: `When no captions are available, Captapi transcribes the audio with AI (Whisper) automatically, so you still get a usable transcript.`,
    });
  }
  if (ep.category === "summarize") {
    list.push({
      q: `Which AI model powers the summaries?`,
      a: `Summaries are generated with GPT-4o-mini for a strong balance of quality, speed, and cost, built on top of the video transcript.`,
    });
  }
  if (ep.category === "download") {
    list.push({
      q: `Are the downloads watermark-free?`,
      a: `Yes — the ${ep.name} returns a direct, watermark-free media URL where the platform allows it, along with available quality variants.`,
    });
  }
  list.push({
    q: `Is the ${ep.name} suitable for production use?`,
    a: `Yes. It is a stable REST endpoint with predictable JSON, automatic retries, and a shared 24-hour cache. Use it for RAG pipelines, analytics, monitoring, and content automation.`,
  });

  return list;
}

// ---------------------------------------------------------------------------
// Response structure (per category)
// ---------------------------------------------------------------------------

export function responseStructure(ep: ApiEndpoint): ResponseGroup[] {
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
    case "download":
      return [
        {
          title: "Download",
          fields: [
            { name: "downloadUrl", desc: "Direct, watermark-free media URL." },
            { name: "format", desc: "Container/format of the file (e.g. mp4)." },
            { name: "quality", desc: "Resolution of the returned media." },
            { name: "sizeBytes", desc: "File size in bytes." },
            { name: "expiresIn", desc: "Seconds until the signed link expires." },
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
    case "download":
      return [
        { title: "Backup & Archiving", desc: "Save copies of public videos you own or license." },
        { title: "Repurposing", desc: "Clip and remix content for other platforms." },
        { title: "ML Datasets", desc: "Collect video and audio for model training." },
        { title: "Offline Analysis", desc: "Process media without streaming it live." },
      ];
  }
}
