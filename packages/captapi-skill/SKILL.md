---
name: captapi
description: Use when extracting public social-media and web data from YouTube, TikTok, Instagram, Facebook, X/Twitter, Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble, GitHub, Google Search, Twitch, Spotify, SoundCloud, Linktree, Snapchat, Truth Social, Kick, Kwai, Komi, Pillar, Linkbio, Linkme, Amazon Shop, TikTok Shop, Age/Gender enrichment, public Ad Libraries, or Captapi account usage — transcripts, AI summaries, comments, video/post details, profile & channel stats, search, hashtag/music lookups, commerce data, video downloads, credit balance, and request history. Captapi is one REST API (and MCP server) covering all 29 data platforms with a single key. Trigger on requests like "get this YouTube transcript", "scrape this TikTok profile", "fetch Instagram reel comments", or "summarize this video".
---

# Captapi

Captapi is one API for structured data from **YouTube, TikTok, Instagram, Facebook, X (Twitter), Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble, GitHub, Google Search, Twitch, Spotify, SoundCloud, Linktree, Snapchat, Truth Social, Kick, Kwai, Komi, Pillar, Linkbio, Linkme, Amazon Shop, TikTok Shop, Age/Gender enrichment, public Ad Libraries, and account usage utilities**. One key works across all 29 data platforms. No OAuth, no per-platform SDKs. Responses are clean JSON and cached for 24h (repeat calls cost 0 credits). 179 endpoints total.

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

## Use from the command line (@captapi/cli)

For shell tasks, scripts, or when no MCP client is available, the official CLI calls the same API. Every endpoint is a subcommand (the tool name with dashes), parameters are flags, and results print as JSON to stdout:

```bash
npx @captapi/cli login                 # save the human-provided key to ~/.captapi/config.json
npx @captapi/cli balance               # remaining credits
npx @captapi/cli list                  # all 179 commands
npx @captapi/cli youtube-transcript --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
npx @captapi/cli tiktok-comment-replies --url "<video>" --comment_id "<id>" --limit 20
```

The CLI reads the key from `~/.captapi/config.json` (via `login`) or the `CAPTAPI_API_KEY` env var. `npx @captapi/cli agent add cursor` writes the MCP config into Cursor/Claude for you. Same auth, credits, and error codes as the REST API.

## Use in n8n workflows (n8n-nodes-captapi)

For no-code/low-code automations, the official `n8n-nodes-captapi` community node exposes all 179 endpoints in n8n. Install it from **Settings → Community Nodes** (package `n8n-nodes-captapi`; self-hosted: `npm install n8n-nodes-captapi`, then restart). Create a **Captapi API** credential with the human-provided `capt_live_...` key, add the **Captapi** node, pick a **Platform** and **Operation**, and it returns the same structured JSON as the REST API for downstream nodes.

## Use in Make.com scenarios (custom app)

For Make.com (Integromat), the Captapi custom app exposes all 179 endpoints as action modules grouped by platform. Create a **Captapi API Key** connection with the human-provided `capt_live_...` key (verified against `/v1/account/limits`), then drop the module you need into a scenario, fill in the `url` (or search query) and optional `limit`, and it returns the same structured JSON `data` as the REST API for downstream modules.

## Use on Apify (BYO-key Actor)

On Apify, the Captapi Actor is a bring-your-own-key wrapper around the REST API (no scraping). Set the `apiKey` input to the human-provided `capt_live_...` key, choose an `operation` (any of the 179 endpoints), fill the fields it needs (`url` / search query / `limit` / ...), and the Actor returns one dataset item with the same structured JSON `data` as the REST API. Credits are billed to the user's own Captapi account. The Actor is also callable through Apify's MCP server (mcp.apify.com), so agents already connected to Apify can run it by name.

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
| `youtube_channel_videos` | `/v1/youtube/channel-videos` | `url` (string), `limit`? (number), `fast`? (boolean) | 20 |
| `youtube_playlist_videos` | `/v1/youtube/playlist-videos` | `url` (string), `limit`? (number), `fast`? (boolean) | 50 |
| `youtube_playlist` | `/v1/youtube/playlist` | `url` (string), `limit`? (number), `fast`? (boolean) | 50 |
| `youtube_video_download` | `/v1/youtube/video-download` | `url` (string) | 3 |
| `youtube_shorts_transcript` | `/v1/youtube/shorts/transcript` | `url` (string), `language`? (string) | 2 |
| `youtube_shorts_summarize` | `/v1/youtube/shorts/summarize` | `url` (string), `language`? (string) | 4 |
| `youtube_shorts_details` | `/v1/youtube/shorts/video-details` | `url` (string) | 1 |
| `youtube_shorts_comments` | `/v1/youtube/shorts/comments` | `url` (string), `limit`? (number) | 20 |
| `youtube_channel_shorts` | `/v1/youtube/channel-shorts` | `url` (string), `limit`? (number) | 20 |
| `youtube_trending_shorts` | `/v1/youtube/trending-shorts` | `q`? (string), `limit`? (number) | 28 |
| `youtube_channel_streams` | `/v1/youtube/channel-streams` | `url` (string), `limit`? (number) | 20 |
| `youtube_hashtag_search` | `/v1/youtube/hashtag-search` | `q` (string), `limit`? (number) | 20 |
| `youtube_comment_replies` | `/v1/youtube/comment-replies` | `url` (string), `comment_id` (string), `limit`? (number) | 20 |
| `youtube_channel_playlists` | `/v1/youtube/channel-playlists` | `url` (string), `limit`? (number) | 20 |
| `youtube_community_posts` | `/v1/youtube/community-posts` | `url` (string), `limit`? (number) | 10 |
| `youtube_community_post_details` | `/v1/youtube/community-post-details` | `url` (string) | 7 |
| `youtube_video_sponsors` | `/v1/youtube/video-sponsors` | `url` (string) | 1 |

### TikTok

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `tiktok_transcript` | `/v1/tiktok/transcript` | `url` (string) | 2 |
| `tiktok_summarize` | `/v1/tiktok/summarize` | `url` (string) | 4 |
| `tiktok_video_details` | `/v1/tiktok/video-details` | `url` (string) | 1 |
| `tiktok_comments` | `/v1/tiktok/comments` | `url` (string), `limit`? (number) | 10 |
| `tiktok_channel_details` | `/v1/tiktok/channel-details` | `url` (string) | 1 |
| `tiktok_profile_region` | `/v1/tiktok/profile-region` | `url` (string) | 7 |
| `tiktok_audience_demographics` | `/v1/tiktok/audience-demographics` | `url` (string) | 7 |
| `tiktok_search` | `/v1/tiktok/search` | `q` (string), `limit`? (number) | 14 |
| `tiktok_search_suggestions` | `/v1/tiktok/search-suggestions` | `q` (string), `country`? (string), `language`? (string), `limit`? (number) | 28 |
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
| `tiktok_live` | `/v1/tiktok/live` | `url` (string) | 1 |
| `tiktok_live_info` | `/v1/tiktok/live-info` | `url` (string) | 7 |
| `tiktok_popular_creators` | `/v1/tiktok/popular-creators` | `country`? (string), `sort`? (string), `follower_count`? (string), `limit`? (number) | 28 |

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
| `instagram_trending_reels` | `/v1/instagram/trending-reels` | `country`? (string), `limit`? (number) | 28 |
| `instagram_video_download` | `/v1/instagram/video-download` | `url` (string) | 3 |
| `instagram_tagged_posts` | `/v1/instagram/tagged-posts` | `url` (string), `limit`? (number) | 18 |
| `instagram_music_posts` | `/v1/instagram/music-posts` | `url` (string), `limit`? (number) | 18 |
| `instagram_reels_by_audio_id` | `/v1/instagram/reels-by-audio-id` | `audio_id` (string), `limit`? (number) | 28 |
| `instagram_hashtag_search` | `/v1/instagram/hashtag-search` | `q` (string), `limit`? (number) | 12 |
| `instagram_profile_search` | `/v1/instagram/profile-search` | `q` (string), `limit`? (number) | 12 |
| `instagram_story_highlights` | `/v1/instagram/story-highlights` | `url` (string) | 5 |
| `instagram_highlights_details` | `/v1/instagram/highlights-details` | `url` (string), `limit`? (number) | 9 |
| `instagram_embed` | `/v1/instagram/embed` | `url` (string) | 1 |
| `instagram_basic_profile` | `/v1/instagram/basic-profile` | `url` (string) | 1 |

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
| `facebook_marketplace_search` | `/v1/facebook/marketplace-search` | `q` (string), `location` (string), `limit`? (number), `details`? (string) | 28 |
| `facebook_marketplace_location_search` | `/v1/facebook/marketplace-location-search` | `q` (string), `limit`? (number) | 17 |
| `facebook_event_search` | `/v1/facebook/event-search` | `q` (string), `limit`? (number) | 40 |
| `facebook_event_details` | `/v1/facebook/event-details` | `url` (string) | 2 |
| `facebook_profile_photos` | `/v1/facebook/profile-photos` | `url` (string), `limit`? (number) | 12 |
| `facebook_profile_events` | `/v1/facebook/profile-events` | `url` (string), `limit`? (number) | 40 |
| `facebook_marketplace_item` | `/v1/facebook/marketplace-item` | `url` (string) | 17 |

### Twitter / X

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `twitter_tweet_details` | `/v1/twitter/tweet-details` | `url` (string) | 1 |
| `twitter_transcript` | `/v1/twitter/transcript` | `url` (string) | 7 |
| `twitter_profile` | `/v1/twitter/profile` | `url` (string) | 1 |
| `twitter_user_tweets` | `/v1/twitter/user-tweets` | `url` (string), `limit`? (number) | 14 |
| `twitter_search` | `/v1/twitter/search` | `q` (string), `limit`? (number) | 14 |
| `twitter_community` | `/v1/twitter/community` | `url` (string) | 1 |
| `twitter_community_tweets` | `/v1/twitter/community-tweets` | `url` (string), `limit`? (number) | 18 |

### Reddit

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `reddit_subreddit_posts` | `/v1/reddit/subreddit-posts` | `url` (string), `limit`? (number) | 10 |
| `reddit_post_details` | `/v1/reddit/post-details` | `url` (string) | 1 |
| `reddit_post_comments` | `/v1/reddit/post-comments` | `url` (string), `limit`? (number) | 20 |
| `reddit_post_transcript` | `/v1/reddit/post-transcript` | `url` (string), `limit`? (number) | 20 |
| `reddit_search` | `/v1/reddit/search` | `q` (string), `limit`? (number) | 10 |
| `reddit_subreddit_details` | `/v1/reddit/subreddit-details` | `url` (string) | 1 |
| `reddit_subreddit_search` | `/v1/reddit/subreddit-search` | `url` (string), `q` (string), `limit`? (number) | 10 |

### Threads

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `threads_profile` | `/v1/threads/profile` | `url` (string) | 1 |
| `threads_user_posts` | `/v1/threads/user-posts` | `url` (string), `limit`? (number) | 14 |
| `threads_post_details` | `/v1/threads/post-details` | `url` (string) | 1 |
| `threads_search` | `/v1/threads/search` | `q` (string), `limit`? (number) | 18 |
| `threads_search_users` | `/v1/threads/search-users` | `q` (string), `limit`? (number) | 14 |

### Bluesky

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `bluesky_profile` | `/v1/bluesky/profile` | `url` (string) | 1 |
| `bluesky_user_posts` | `/v1/bluesky/user-posts` | `url` (string), `limit`? (number) | 3 |
| `bluesky_post_details` | `/v1/bluesky/post-details` | `url` (string) | 1 |

### Pinterest

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `pinterest_pin_details` | `/v1/pinterest/pin-details` | `url` (string) | 1 |
| `pinterest_user_pins` | `/v1/pinterest/user-pins` | `url` (string), `limit`? (number) | 13 |
| `pinterest_search` | `/v1/pinterest/search` | `q` (string), `limit`? (number) | 13 |
| `pinterest_board` | `/v1/pinterest/board` | `url` (string), `limit`? (number) | 13 |
| `pinterest_user_boards` | `/v1/pinterest/user-boards` | `url` (string), `limit`? (number) | 13 |

### LinkedIn

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `linkedin_profile` | `/v1/linkedin/profile` | `url` (string) | 2 |
| `linkedin_company` | `/v1/linkedin/company` | `url` (string) | 2 |
| `linkedin_post_details` | `/v1/linkedin/post-details` | `url` (string) | 1 |
| `linkedin_post_transcript` | `/v1/linkedin/post-transcript` | `url` (string) | 7 |
| `linkedin_company_posts` | `/v1/linkedin/company-posts` | `url` (string), `limit`? (number) | 16 |
| `linkedin_search_posts` | `/v1/linkedin/search-posts` | `q` (string), `sort`? (string), `limit`? (number) | 16 |

### Rumble

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `rumble_video_details` | `/v1/rumble/video-details` | `url` (string) | 1 |
| `rumble_channel_videos` | `/v1/rumble/channel-videos` | `url` (string), `limit`? (number) | 12 |
| `rumble_search` | `/v1/rumble/search` | `q` (string), `limit`? (number) | 12 |
| `rumble_comments` | `/v1/rumble/comments` | `url` (string), `limit`? (number) | 30 |

### TikTok Shop

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `tiktok_shop_search` | `/v1/tiktok-shop/shop-search` | `q` (string), `region`? (string), `limit`? (number) | 56 |
| `tiktok_shop_products` | `/v1/tiktok-shop/shop-products` | `url` (string), `limit`? (number) | 56 |
| `tiktok_shop_product_details` | `/v1/tiktok-shop/product-details` | `url` (string) | 14 |
| `tiktok_shop_product_reviews` | `/v1/tiktok-shop/product-reviews` | `url` (string), `limit`? (number) | 45 |
| `tiktok_shop_user_showcase` | `/v1/tiktok-shop/user-showcase` | `username` (string), `limit`? (number) | 45 |

### GitHub

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `github_user` | `/v1/github/user` | `username` (string) | 3 |
| `github_repositories` | `/v1/github/repositories` | `username` (string), `limit`? (number) | 12 |
| `github_repository` | `/v1/github/repository` | `repo` (string) | 3 |
| `github_pull_requests` | `/v1/github/pull-requests` | `repo` (string), `state`? (string), `limit`? (number) | 12 |
| `github_activity` | `/v1/github/activity` | `username` (string), `limit`? (number) | 12 |
| `github_followers` | `/v1/github/followers` | `username` (string), `limit`? (number) | 12 |
| `github_following` | `/v1/github/following` | `username` (string), `limit`? (number) | 12 |
| `github_contributions` | `/v1/github/contributions` | `username` (string) | 3 |
| `github_trending_repositories` | `/v1/github/trending-repositories` | `q` (string), `limit`? (number) | 12 |
| `github_trending_developers` | `/v1/github/trending-developers` | `q` (string), `limit`? (number) | 12 |

### Google Search

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `google_search` | `/v1/google/search` | `q` (string), `country`? (string), `language`? (string), `limit`? (number) | 42 |

### Twitch

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `twitch_profile` | `/v1/twitch/profile` | `url` (string) | 9 |
| `twitch_user_videos` | `/v1/twitch/user-videos` | `url` (string), `limit`? (number) | 34 |
| `twitch_user_schedule` | `/v1/twitch/user-schedule` | `url` (string) | 34 |
| `twitch_clip` | `/v1/twitch/clip` | `url` (string) | 9 |

### Spotify

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `spotify_artist` | `/v1/spotify/artist` | `url` (string) | 6 |
| `spotify_track` | `/v1/spotify/track` | `url` (string) | 6 |
| `spotify_album` | `/v1/spotify/album` | `url` (string) | 6 |
| `spotify_search` | `/v1/spotify/search` | `q` (string), `type`? (string), `limit`? (number) | 23 |
| `spotify_podcast` | `/v1/spotify/podcast` | `url` (string), `limit`? (number) | 6 |
| `spotify_podcast_episodes` | `/v1/spotify/podcast-episodes` | `url` (string), `limit`? (number) | 23 |

### SoundCloud

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `soundcloud_artist` | `/v1/soundcloud/artist` | `url` (string) | 7 |
| `soundcloud_artist_tracks` | `/v1/soundcloud/artist-tracks` | `url` (string), `limit`? (number) | 28 |
| `soundcloud_track` | `/v1/soundcloud/track` | `url` (string) | 7 |

### Linktree

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `linktree_page` | `/v1/linktree/page` | `url` (string) | 4 |

### Snapchat

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `snapchat_user_profile` | `/v1/snapchat/user-profile` | `url` (string) | 11 |

### Truth Social

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `truth_social_profile` | `/v1/truth-social/profile` | `url` (string) | 5 |
| `truth_social_user_posts` | `/v1/truth-social/user-posts` | `url` (string), `limit`? (number) | 17 |
| `truth_social_post` | `/v1/truth-social/post` | `url` (string) | 5 |

### Kick

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `kick_clip` | `/v1/kick/clip` | `url` (string), `limit`? (number) | 34 |

### Amazon Shop

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `amazon_shop_page` | `/v1/amazon-shop/page` | `url` (string), `marketplace`? (string), `limit`? (number) | 89 |

### Age and Gender

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `age_gender_get` | `/v1/age-gender` | `name` (string), `names`? (string) | 4 |

### Kwai

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `kwai_profile` | `/v1/kwai/profile` | `url` (string) | 17 |
| `kwai_user_posts` | `/v1/kwai/user-posts` | `url` (string), `limit`? (number) | 45 |
| `kwai_post` | `/v1/kwai/post` | `url` (string) | 17 |

### Komi

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `komi_page` | `/v1/komi/page` | `url` (string) | 4 |

### Pillar

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `pillar_page` | `/v1/pillar/page` | `url` (string) | 4 |

### Linkbio

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `linkbio_page` | `/v1/linkbio/page` | `url` (string) | 4 |

### Linkme

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `linkme_profile` | `/v1/linkme/profile` | `url` (string) | 4 |

### Account

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `account_balance` | `/v1/account/balance` | none | 0 |
| `account_request_history` | `/v1/account/request-history` | `limit`? (number) | 0 |
| `account_daily_usage` | `/v1/account/daily-usage` | `days`? (number) | 0 |
| `account_most_used_routes` | `/v1/account/most-used-routes` | `days`? (number), `limit`? (number) | 0 |

### Public Ad Libraries

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
| `facebook_ad_library_search` | `/v1/ad-library/facebook/search` | `q` (string), `country`? (string), `limit`? (number) | 70 |
| `facebook_ad_library_company_ads` | `/v1/ad-library/facebook/company-ads` | `url` (string), `country`? (string), `limit`? (number) | 70 |
| `facebook_ad_library_search_companies` | `/v1/ad-library/facebook/search-companies` | `q` (string), `country`? (string), `limit`? (number) | 70 |
| `facebook_ad_library_ad_details` | `/v1/ad-library/facebook/ad-details` | `url` (string) | 17 |
| `facebook_ad_library_ad_transcript` | `/v1/ad-library/facebook/ad-transcript` | `url` (string) | 17 |
| `tiktok_ad_library_search` | `/v1/ad-library/tiktok/search` | `q` (string), `country`? (string), `limit`? (number) | 70 |
| `tiktok_ad_library_ad_details` | `/v1/ad-library/tiktok/ad-details` | `url` (string), `country`? (string) | 17 |
| `google_ad_library_company_ads` | `/v1/ad-library/google/company-ads` | `advertiser` (string), `country`? (string), `limit`? (number) | 67 |
| `google_ad_library_ad_details` | `/v1/ad-library/google/ad-details` | `creative_id` (string), `country`? (string) | 17 |
| `google_ad_library_advertiser_search` | `/v1/ad-library/google/advertiser-search` | `q` (string), `country`? (string), `limit`? (number) | 45 |
| `linkedin_ad_library_search_ads` | `/v1/ad-library/linkedin/search-ads` | `q` (string), `country`? (string), `limit`? (number) | 70 |
| `linkedin_ad_library_ad_details` | `/v1/ad-library/linkedin/ad-details` | `url` (string) | 17 |

---
Generated from the Captapi catalog. Do not edit by hand — run `node generate.mjs`.
