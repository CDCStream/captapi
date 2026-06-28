"""Catalog of every Captapi endpoint exposed as a hosted MCP tool.

Mirrors `packages/captapi-mcp/src/catalog.ts` (the npm/stdio server) so the
hosted (remote, HTTP) MCP server advertises the exact same 62 tools with the
same parameters, credit costs and descriptions. Keep the two in sync.
"""

from __future__ import annotations

from dataclasses import dataclass

Platform = str  # "youtube" | "tiktok" | "instagram" | "facebook"


@dataclass(frozen=True)
class ToolParam:
    name: str
    type: str  # "string" | "number" | "boolean"
    required: bool
    description: str


@dataclass(frozen=True)
class Endpoint:
    tool: str
    platform: Platform
    name: str
    path: str
    credits: int
    summary: str
    params: tuple[ToolParam, ...]


# --- Param builders (keep declarations terse + consistent) -----------------

def _url(description: str) -> ToolParam:
    return ToolParam("url", "string", True, description)


def _q(description: str = "Search query or keywords (min 2 chars).") -> ToolParam:
    return ToolParam("q", "string", True, description)


def _limit(default: int, maximum: int) -> ToolParam:
    return ToolParam(
        "limit",
        "number",
        False,
        f"Max items to return. Default {default}, max {maximum}. Billed per result.",
    )


def _fast_rss() -> ToolParam:
    return ToolParam(
        "fast",
        "boolean",
        False,
        "Set true to use YouTube RSS for faster results with less detailed metadata. Leave false when viewCount/duration quality matters.",
    )


def _language() -> ToolParam:
    return ToolParam(
        "language",
        "string",
        False,
        'Preferred caption language as an ISO code, e.g. "en". Defaults to auto-detect.',
    )


def _comment_id() -> ToolParam:
    return ToolParam(
        "comment_id",
        "string",
        True,
        "ID of the parent comment to fetch replies for (from the comments endpoint).",
    )


YT_VIDEO = "Public YouTube video URL, e.g. https://youtube.com/watch?v=ID."
YT_SHORTS = "Public YouTube Shorts URL, e.g. https://youtube.com/shorts/ID."
YT_CHANNEL = "YouTube channel URL, e.g. https://youtube.com/@handle or /channel/UC..."
TT_VIDEO = "Public TikTok video URL, e.g. https://tiktok.com/@user/video/ID."
TT_PROFILE = "TikTok profile URL, e.g. https://tiktok.com/@username."
TT_MUSIC = "TikTok music/sound URL, e.g. https://tiktok.com/music/name-ID."
IG_POST = "Instagram post or reel URL, e.g. https://instagram.com/reel/ID/."
IG_REEL = "Instagram Reel URL, e.g. https://instagram.com/reel/ID/."
IG_PROFILE = "Instagram profile URL, e.g. https://instagram.com/username/."
FB_VIDEO = "Public Facebook video or post URL."


_YOUTUBE: tuple[tuple, ...] = (
    ("youtube_transcript", "YouTube Transcript", "/v1/youtube/transcript", 2, "Extract the full timestamped transcript of a YouTube video.", (_url(YT_VIDEO), _language())),
    ("youtube_summarize", "YouTube Summarizer", "/v1/youtube/summarize", 4, "AI summary (key points, topics, sentiment) of a YouTube video.", (_url(YT_VIDEO), _language())),
    ("youtube_video_details", "YouTube Video Details", "/v1/youtube/video-details", 1, "Metadata + engagement stats for a YouTube video.", (_url(YT_VIDEO),)),
    ("youtube_comments", "YouTube Comments", "/v1/youtube/comments", 20, "Comments on a YouTube video.", (_url(YT_VIDEO), _limit(50, 500))),
    ("youtube_channel_details", "YouTube Channel Details", "/v1/youtube/channel-details", 1, "Channel info & subscriber/stats for a YouTube channel.", (_url(YT_CHANNEL),)),
    ("youtube_search", "YouTube Search", "/v1/youtube/search", 20, "Search YouTube videos by keyword.", (_q(), _limit(20, 200))),
    ("youtube_channel_videos", "YouTube Channel Videos", "/v1/youtube/channel-videos", 20, "List a channel's uploaded videos.", (_url(YT_CHANNEL), _limit(20, 200), _fast_rss())),
    ("youtube_playlist_videos", "YouTube Playlist Videos", "/v1/youtube/playlist-videos", 50, "List videos in a YouTube playlist.", (_url("YouTube playlist URL, e.g. https://youtube.com/playlist?list=ID."), _limit(50, 500), _fast_rss())),
    ("youtube_video_download", "YouTube Video Download", "/v1/youtube/video-download", 3, "Direct download URLs for a YouTube video.", (_url(YT_VIDEO),)),
    ("youtube_shorts_transcript", "YouTube Shorts Transcript", "/v1/youtube/shorts/transcript", 2, "Transcript of a YouTube Short.", (_url(YT_SHORTS), _language())),
    ("youtube_shorts_summarize", "YouTube Shorts Summarizer", "/v1/youtube/shorts/summarize", 4, "AI summary of a YouTube Short.", (_url(YT_SHORTS), _language())),
    ("youtube_shorts_details", "YouTube Shorts Stats", "/v1/youtube/shorts/video-details", 1, "Metadata + stats for a YouTube Short.", (_url(YT_SHORTS),)),
    ("youtube_shorts_comments", "YouTube Shorts Comments", "/v1/youtube/shorts/comments", 20, "Comments on a YouTube Short.", (_url(YT_SHORTS), _limit(50, 500))),
    ("youtube_channel_shorts", "YouTube Channel Shorts", "/v1/youtube/channel-shorts", 20, "List a channel's Shorts.", (_url(YT_CHANNEL), _limit(20, 200))),
    ("youtube_channel_streams", "YouTube Channel Streams", "/v1/youtube/channel-streams", 20, "List a channel's live/past streams.", (_url(YT_CHANNEL), _limit(20, 200))),
    ("youtube_hashtag_search", "YouTube Hashtag Search", "/v1/youtube/hashtag-search", 20, "Search YouTube videos by hashtag.", (_q("Hashtag with or without the # (min 2 chars)."), _limit(20, 200))),
    ("youtube_comment_replies", "YouTube Comment Replies", "/v1/youtube/comment-replies", 20, "Replies to a specific YouTube comment.", (_url(YT_VIDEO), _comment_id(), _limit(50, 500))),
    ("youtube_channel_playlists", "YouTube Channel Playlists", "/v1/youtube/channel-playlists", 20, "List a channel's playlists.", (_url(YT_CHANNEL), _limit(20, 200))),
    ("youtube_community_posts", "YouTube Community Posts", "/v1/youtube/community-posts", 10, "List a channel's community (posts) tab.", (_url(YT_CHANNEL), _limit(20, 200))),
)

_TIKTOK: tuple[tuple, ...] = (
    ("tiktok_transcript", "TikTok Transcript", "/v1/tiktok/transcript", 2, "Transcript of a TikTok video (via captions).", (_url(TT_VIDEO),)),
    ("tiktok_summarize", "TikTok Summarizer", "/v1/tiktok/summarize", 4, "AI summary of a TikTok video.", (_url(TT_VIDEO),)),
    ("tiktok_video_details", "TikTok Video Details", "/v1/tiktok/video-details", 1, "Metadata + stats for a TikTok video.", (_url(TT_VIDEO),)),
    ("tiktok_comments", "TikTok Comments", "/v1/tiktok/comments", 10, "Comments on a TikTok video.", (_url(TT_VIDEO), _limit(50, 500))),
    ("tiktok_channel_details", "TikTok Channel Details", "/v1/tiktok/channel-details", 1, "Profile info & stats for a TikTok user.", (_url(TT_PROFILE),)),
    ("tiktok_search", "TikTok Search", "/v1/tiktok/search", 14, "Search TikTok videos by keyword/hashtag.", (_q(), _limit(20, 200))),
    ("tiktok_video_download", "TikTok Video Download", "/v1/tiktok/video-download", 3, "No-watermark download URL for a TikTok video.", (_url(TT_VIDEO),)),
    ("tiktok_channel_posts", "TikTok Channel Posts", "/v1/tiktok/channel-posts", 14, "Latest posts from a TikTok profile.", (_url(TT_PROFILE), _limit(20, 200))),
    ("tiktok_comment_replies", "TikTok Comment Replies", "/v1/tiktok/comment-replies", 50, "Replies to a specific TikTok comment.", (_url(TT_VIDEO), _comment_id(), _limit(50, 500))),
    ("tiktok_user_followers", "TikTok User Followers", "/v1/tiktok/user-followers", 20, "List a TikTok user's followers.", (_url(TT_PROFILE), _limit(50, 500))),
    ("tiktok_user_followings", "TikTok User Followings", "/v1/tiktok/user-followings", 20, "List who a TikTok user follows.", (_url(TT_PROFILE), _limit(50, 500))),
    ("tiktok_music_posts", "TikTok Music Posts", "/v1/tiktok/music-posts", 32, "Posts using a specific TikTok sound/music.", (_url(TT_MUSIC), _limit(20, 200))),
    ("tiktok_hashtag_search", "TikTok Hashtag Search", "/v1/tiktok/hashtag-search", 14, "Search TikTok videos by hashtag.", (_q("Hashtag with or without the # (min 2 chars)."), _limit(20, 200))),
    ("tiktok_top_search", "TikTok Top Search", "/v1/tiktok/top-search", 14, "Top mixed TikTok results for a keyword.", (_q(), _limit(20, 200))),
    ("tiktok_user_search", "TikTok User Search", "/v1/tiktok/user-search", 8, "Search TikTok users/creators by keyword.", (_q(), _limit(20, 100))),
    ("tiktok_song_details", "TikTok Song Details", "/v1/tiktok/song-details", 2, "Details of a TikTok sound/song.", (_url(TT_MUSIC),)),
    ("tiktok_trending_feed", "TikTok Trending Feed", "/v1/tiktok/trending-feed", 14, "TikTok trending (For You) videos by region.", (ToolParam("country", "string", False, "Two-letter ISO country code, e.g. US, GB, TR. Default US."), _limit(20, 200))),
    ("tiktok_popular_hashtags", "TikTok Popular Hashtags", "/v1/tiktok/popular-hashtags", 14, "Trending TikTok hashtags for a topic/keyword.", (ToolParam("query", "string", False, 'Topic or keyword to discover trending hashtags for. Default "trending".'), _limit(20, 100))),
)

_INSTAGRAM: tuple[tuple, ...] = (
    ("instagram_transcript", "Instagram Transcript", "/v1/instagram/transcript", 2, "Transcript of an Instagram Reel.", (_url(IG_REEL),)),
    ("instagram_summarize", "Instagram Summarizer", "/v1/instagram/summarize", 4, "AI summary of an Instagram Reel.", (_url(IG_REEL),)),
    ("instagram_details", "Instagram Details", "/v1/instagram/details", 1, "Details for an Instagram post or reel.", (_url(IG_POST),)),
    ("instagram_comments", "Instagram Comments", "/v1/instagram/comments", 45, "Comments on an Instagram post or reel.", (_url(IG_POST), _limit(50, 500))),
    ("instagram_channel_details", "Instagram Channel Details", "/v1/instagram/channel-details", 1, "Profile info & stats for an Instagram account.", (_url(IG_PROFILE),)),
    ("instagram_channel_posts", "Instagram Channel Posts", "/v1/instagram/channel-posts", 12, "Latest posts from an Instagram profile.", (_url(IG_PROFILE), _limit(20, 200))),
    ("instagram_channel_reels", "Instagram Channel Reels", "/v1/instagram/channel-reels", 12, "Latest Reels from an Instagram profile.", (_url(IG_PROFILE), _limit(20, 200))),
    ("instagram_reels_search", "Instagram Reels Search", "/v1/instagram/reels-search", 12, "Search Instagram Reels by hashtag/keyword.", (_q("Hashtag (without #) or keyword (min 2 chars)."), _limit(20, 200))),
    ("instagram_video_download", "Instagram Video Download", "/v1/instagram/video-download", 3, "Direct video URL for an Instagram Reel.", (_url(IG_REEL),)),
    ("instagram_tagged_posts", "Instagram Tagged Posts", "/v1/instagram/tagged-posts", 18, "Posts an Instagram user is tagged in.", (_url(IG_PROFILE), _limit(20, 200))),
    ("instagram_music_posts", "Instagram Music Posts", "/v1/instagram/music-posts", 18, "Posts/Reels using an Instagram audio.", (_url("Instagram audio/music page URL."), _limit(20, 200))),
    ("instagram_hashtag_search", "Instagram Hashtag Search", "/v1/instagram/hashtag-search", 12, "Search Instagram posts by hashtag.", (_q("Hashtag without the # (min 2 chars)."), _limit(20, 200))),
    ("instagram_profile_search", "Instagram Profile Search", "/v1/instagram/profile-search", 12, "Search Instagram profiles by keyword.", (_q(), _limit(20, 100))),
    ("instagram_story_highlights", "Instagram Story Highlights", "/v1/instagram/story-highlights", 5, "List a profile's story highlight covers.", (_url(IG_PROFILE),)),
    ("instagram_highlights_details", "Instagram Highlights Details", "/v1/instagram/highlights-details", 9, "Items inside a profile's story highlights.", (_url(IG_PROFILE), ToolParam("limit", "number", False, "Max highlights to expand. Default 10, max 50."))),
    ("instagram_embed", "Instagram Embed", "/v1/instagram/embed", 1, "Embed HTML for an Instagram post/reel.", (_url(IG_POST),)),
)

_FACEBOOK: tuple[tuple, ...] = (
    ("facebook_details", "Facebook Details", "/v1/facebook/details", 1, "Details for a Facebook video or post.", (_url(FB_VIDEO),)),
    ("facebook_transcript", "Facebook Transcript", "/v1/facebook/transcript", 2, "Transcript of a Facebook video.", (_url(FB_VIDEO),)),
    ("facebook_summarize", "Facebook Summarizer", "/v1/facebook/summarize", 4, "AI summary of a Facebook video or post.", (_url(FB_VIDEO),)),
    ("facebook_comments", "Facebook Comments", "/v1/facebook/comments", 30, "Comments on a Facebook post.", (_url(FB_VIDEO), _limit(50, 500))),
    ("facebook_page_details", "Facebook Page Details", "/v1/facebook/page-details", 1, "Info & stats for a Facebook page.", (_url("Facebook page URL, e.g. https://facebook.com/PageName."),)),
    ("facebook_profile_posts", "Facebook Profile Posts", "/v1/facebook/profile-posts", 12, "Latest posts from a Facebook profile/page.", (_url("Facebook profile or page URL."), _limit(20, 200))),
    ("facebook_profile_reels", "Facebook Profile Reels", "/v1/facebook/profile-reels", 36, "Latest Reels from a Facebook profile/page.", (_url("Facebook profile or page URL."), _limit(20, 200))),
    ("facebook_group_posts", "Facebook Group Posts", "/v1/facebook/group-posts", 12, "Posts from a public Facebook group.", (_url("Public Facebook group URL, e.g. https://facebook.com/groups/ID."), _limit(20, 200))),
    ("facebook_comment_replies", "Facebook Comment Replies", "/v1/facebook/comment-replies", 30, "Replies to a specific Facebook comment.", (_url("Facebook post URL the comment belongs to."), _comment_id(), _limit(50, 500))),
)


def _build(rows: tuple[tuple, ...], platform: Platform) -> list[Endpoint]:
    return [
        Endpoint(
            tool=tool,
            platform=platform,
            name=name,
            path=path,
            credits=credits,
            summary=summary,
            params=params,
        )
        for (tool, name, path, credits, summary, params) in rows
    ]


ENDPOINTS: list[Endpoint] = [
    *_build(_YOUTUBE, "youtube"),
    *_build(_TIKTOK, "tiktok"),
    *_build(_INSTAGRAM, "instagram"),
    *_build(_FACEBOOK, "facebook"),
]

BY_TOOL: dict[str, Endpoint] = {e.tool: e for e in ENDPOINTS}


def describe(e: Endpoint) -> str:
    """A concise, agent-facing description (summary + cost) for an endpoint."""
    plural = "" if e.credits == 1 else "s"
    return (
        f"{e.summary} Costs ~{e.credits} credit{plural}; "
        "cached results are free, failures are never charged."
    )


def tool_input_schema(e: Endpoint) -> dict:
    """JSON Schema (draft-07 style) describing the tool's input parameters."""
    properties: dict[str, dict] = {}
    required: list[str] = []
    for p in e.params:
        if p.type == "number":
            schema: dict = {"type": "integer", "minimum": 1, "description": p.description}
        elif p.type == "boolean":
            schema = {"type": "boolean", "description": p.description}
        else:
            schema = {"type": "string", "description": p.description}
            if p.name == "url":
                schema["format"] = "uri"
        properties[p.name] = schema
        if p.required:
            required.append(p.name)
    out: dict = {"type": "object", "properties": properties, "additionalProperties": False}
    if required:
        out["required"] = required
    return out
