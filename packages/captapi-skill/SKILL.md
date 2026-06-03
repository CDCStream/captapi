---
name: captapi
description: Use when extracting public social-media data from YouTube, TikTok, Instagram, or Facebook — transcripts, AI summaries, comments, video/post details, profile & channel stats, search, hashtag/music lookups, or video downloads. Captapi is one REST API (and MCP server) covering all four platforms with a single key. Trigger on requests like "get this YouTube transcript", "scrape this TikTok profile", "fetch Instagram reel comments", or "summarize this video".
---

# Captapi

Captapi is one API for structured data from **YouTube, TikTok, Instagram, and Facebook**. One key works across all platforms. No OAuth, no per-platform SDKs. Responses are clean JSON and cached for 24h (repeat calls cost 0 credits). 62 endpoints total.

- Base URL: `https://api.captapi.com`
- Docs: https://captapi.com/docs · Full machine reference: https://captapi.com/llms-full.txt

## Step 0 — Get the API key (ask the human)

Using Captapi requires a `capt_live_...` API key, and **creating one requires a human** (sign-up cannot be automated). Before doing anything else:

1. If you do **not** already have a key, ask the user: *"Create a Captapi API key at https://captapi.com/dashboard/api-keys (100 free credits, no card) and paste it here."*
2. Never guess, invent, or try to sign up for a key. Store the key the user gives you and use it for all requests.

## How to call Captapi

Every endpoint is a single authenticated `GET` request. Pass parameters as URL query params (URL-encode values). Send the key as a Bearer token:

```bash
curl "https://api.captapi.com/v1/youtube/transcript?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DdQw4w9WgXcQ" \
  -H "Authorization: Bearer capt_live_..."
```

Response shape:

```json
{ "success": true, "cached": false, "creditsUsed": 2, "data": { "language": "en", "text": "..." } }
```

If you have the **MCP server** connected instead, call the tool named in the tables below (e.g. `youtube_transcript`) with the same parameters — no URL building needed.

## Choosing the right endpoint

- **Single piece of content** (one video / reel / post): use `*_transcript`, `*_summarize`, `*_video_details` / `*_details`, or `*_comments` with the content `url`.
- **A creator / account**: use `*_channel_details` (stats) or `*_channel_posts` / `*_channel_reels` (their content) with the profile `url`.
- **Discovery**: use `*_search`, `*_hashtag_search`, or `*_user_search` with a `q` query.
- **Downloads**: use `*_video_download` for a direct media URL.

## Parameter rules (important gotchas)

- `url` — pass the **full public URL** of the video/reel/post/profile. Each endpoint's table notes the expected URL type.
- `q` — search query or keyword (min 2 chars). For hashtag endpoints, pass the tag **without** `#`.
- `limit` — optional; controls how many items list/search/comment endpoints return. **Billed per result**, so request only what you need. Defaults and maxes vary per endpoint.
- `language` — optional ISO code (e.g. `en`) for the **YouTube** transcript/summary endpoints (incl. Shorts); defaults to auto-detect. Other platforms' transcript/summary endpoints take only `url`.
- `comment_id` — required for `*_comment_replies`; get it from the corresponding `*_comments` response.

## Credits & errors

- Each endpoint costs a fixed number of credits (see tables). **Cached results (within 24h) cost 0.** Failed or empty results are **never charged**.
- Error responses are non-2xx with `{ "detail": "..." }`:
  - `401` — missing/invalid key. Re-check the key with the user.
  - `402` — out of credits. Tell the user to top up at https://captapi.com/dashboard/billing.
  - `422` — unprocessable (e.g. the video has no captions). Not charged; do not retry blindly.
  - `429` — rate limited. Back off and retry after a short delay.

## Endpoint reference

### YouTube

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `youtube_transcript` | `/v1/youtube/transcript` | `url` (string), `language`? (string) | 2 |
| `youtube_summarize` | `/v1/youtube/summarize` | `url` (string), `language`? (string) | 4 |
| `youtube_video_details` | `/v1/youtube/video-details` | `url` (string) | 1 |
| `youtube_comments` | `/v1/youtube/comments` | `url` (string), `limit`? (number) | 20 |
| `youtube_channel_details` | `/v1/youtube/channel-details` | `url` (string) | 1 |
| `youtube_search` | `/v1/youtube/search` | `q` (string), `limit`? (number) | 20 |
| `youtube_channel_videos` | `/v1/youtube/channel-videos` | `url` (string), `limit`? (number) | 20 |
| `youtube_playlist_videos` | `/v1/youtube/playlist-videos` | `url` (string), `limit`? (number) | 50 |
| `youtube_video_download` | `/v1/youtube/video-download` | `url` (string) | 3 |
| `youtube_shorts_transcript` | `/v1/youtube/shorts/transcript` | `url` (string), `language`? (string) | 2 |
| `youtube_shorts_summarize` | `/v1/youtube/shorts/summarize` | `url` (string), `language`? (string) | 4 |
| `youtube_shorts_details` | `/v1/youtube/shorts/video-details` | `url` (string) | 1 |
| `youtube_shorts_comments` | `/v1/youtube/shorts/comments` | `url` (string), `limit`? (number) | 20 |
| `youtube_channel_shorts` | `/v1/youtube/channel-shorts` | `url` (string), `limit`? (number) | 20 |
| `youtube_channel_streams` | `/v1/youtube/channel-streams` | `url` (string), `limit`? (number) | 20 |
| `youtube_hashtag_search` | `/v1/youtube/hashtag-search` | `q` (string), `limit`? (number) | 20 |
| `youtube_comment_replies` | `/v1/youtube/comment-replies` | `url` (string), `comment_id` (string), `limit`? (number) | 20 |
| `youtube_channel_playlists` | `/v1/youtube/channel-playlists` | `url` (string), `limit`? (number) | 20 |
| `youtube_community_posts` | `/v1/youtube/community-posts` | `url` (string), `limit`? (number) | 10 |

### TikTok

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `tiktok_transcript` | `/v1/tiktok/transcript` | `url` (string) | 2 |
| `tiktok_summarize` | `/v1/tiktok/summarize` | `url` (string) | 4 |
| `tiktok_video_details` | `/v1/tiktok/video-details` | `url` (string) | 1 |
| `tiktok_comments` | `/v1/tiktok/comments` | `url` (string), `limit`? (number) | 10 |
| `tiktok_channel_details` | `/v1/tiktok/channel-details` | `url` (string) | 1 |
| `tiktok_search` | `/v1/tiktok/search` | `q` (string), `limit`? (number) | 14 |
| `tiktok_video_download` | `/v1/tiktok/video-download` | `url` (string) | 3 |
| `tiktok_channel_posts` | `/v1/tiktok/channel-posts` | `url` (string), `limit`? (number) | 14 |
| `tiktok_comment_replies` | `/v1/tiktok/comment-replies` | `url` (string), `comment_id` (string), `limit`? (number) | 50 |
| `tiktok_user_followers` | `/v1/tiktok/user-followers` | `url` (string), `limit`? (number) | 20 |
| `tiktok_user_followings` | `/v1/tiktok/user-followings` | `url` (string), `limit`? (number) | 20 |
| `tiktok_music_posts` | `/v1/tiktok/music-posts` | `url` (string), `limit`? (number) | 32 |
| `tiktok_hashtag_search` | `/v1/tiktok/hashtag-search` | `q` (string), `limit`? (number) | 14 |
| `tiktok_top_search` | `/v1/tiktok/top-search` | `q` (string), `limit`? (number) | 14 |
| `tiktok_user_search` | `/v1/tiktok/user-search` | `q` (string), `limit`? (number) | 8 |
| `tiktok_song_details` | `/v1/tiktok/song-details` | `url` (string) | 2 |
| `tiktok_trending_feed` | `/v1/tiktok/trending-feed` | `country`? (string), `limit`? (number) | 14 |
| `tiktok_popular_hashtags` | `/v1/tiktok/popular-hashtags` | `query`? (string), `limit`? (number) | 14 |

### Instagram

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `instagram_transcript` | `/v1/instagram/transcript` | `url` (string) | 2 |
| `instagram_summarize` | `/v1/instagram/summarize` | `url` (string) | 4 |
| `instagram_details` | `/v1/instagram/details` | `url` (string) | 1 |
| `instagram_comments` | `/v1/instagram/comments` | `url` (string), `limit`? (number) | 45 |
| `instagram_channel_details` | `/v1/instagram/channel-details` | `url` (string) | 1 |
| `instagram_channel_posts` | `/v1/instagram/channel-posts` | `url` (string), `limit`? (number) | 12 |
| `instagram_channel_reels` | `/v1/instagram/channel-reels` | `url` (string), `limit`? (number) | 12 |
| `instagram_reels_search` | `/v1/instagram/reels-search` | `q` (string), `limit`? (number) | 12 |
| `instagram_video_download` | `/v1/instagram/video-download` | `url` (string) | 3 |
| `instagram_tagged_posts` | `/v1/instagram/tagged-posts` | `url` (string), `limit`? (number) | 18 |
| `instagram_music_posts` | `/v1/instagram/music-posts` | `url` (string), `limit`? (number) | 18 |
| `instagram_hashtag_search` | `/v1/instagram/hashtag-search` | `q` (string), `limit`? (number) | 12 |
| `instagram_profile_search` | `/v1/instagram/profile-search` | `q` (string), `limit`? (number) | 12 |
| `instagram_story_highlights` | `/v1/instagram/story-highlights` | `url` (string) | 5 |
| `instagram_highlights_details` | `/v1/instagram/highlights-details` | `url` (string), `limit`? (number) | 9 |
| `instagram_embed` | `/v1/instagram/embed` | `url` (string) | 1 |

### Facebook

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `facebook_details` | `/v1/facebook/details` | `url` (string) | 1 |
| `facebook_transcript` | `/v1/facebook/transcript` | `url` (string) | 2 |
| `facebook_summarize` | `/v1/facebook/summarize` | `url` (string) | 4 |
| `facebook_comments` | `/v1/facebook/comments` | `url` (string), `limit`? (number) | 30 |
| `facebook_page_details` | `/v1/facebook/page-details` | `url` (string) | 1 |
| `facebook_profile_posts` | `/v1/facebook/profile-posts` | `url` (string), `limit`? (number) | 12 |
| `facebook_profile_reels` | `/v1/facebook/profile-reels` | `url` (string), `limit`? (number) | 36 |
| `facebook_group_posts` | `/v1/facebook/group-posts` | `url` (string), `limit`? (number) | 12 |
| `facebook_comment_replies` | `/v1/facebook/comment-replies` | `url` (string), `comment_id` (string), `limit`? (number) | 30 |

---
Generated from the Captapi catalog. Do not edit by hand — run `node generate.mjs`.
