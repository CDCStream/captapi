# SC parity backlog (Captapi)

Last updated: 2026-08-04 (Twitter community-tweets pricing + meta + cURL URL).

Audit habit: check footer stamp `N/M · docs YYYY-MM-DD` before judging a page. Field lists come from **examples** (`api_snapshots.json` → `api-examples.generated.ts`) — ship code + refresh snapshot **with `ok: true`** or `gen_examples.py` skips the slug and the page looks broken.

## Done recently (do not re-queue without re-verify)

- [x] `/apis` build stamp + short ISR (`CONTENT_UPDATED`, footer `PLATFORM/ENDPOINT · docs DATE`)
- [x] Docs intro: public social media (not "social media video")
- [x] `hasCreatorHeart`: inactive tip ≠ true (cache bump comments / comment-replies)
- [x] `playlist` + `playlist-videos`: enrich (ISO publishedAt, exact views, video id, channel{})
- [x] `playlist-videos` example: `totalVideos` + `channel{}`
- [x] `channel-playlists`: `id` field
- [x] `channel-videos` / `channel-streams` / `channel-shorts`: player enrich path in code
- [x] `popular-hashtags`: Creative Center population videoCount vs sampleVideoCount (verify on current docs stamp)
- [x] Community post details: likeCount int + likeCountText (example may lag — re-check stamp)
- [x] TikTok `user-followers` / `user-followings`: id + secUid + createTime/region/language + total + nextCursor; native flat 1 credit
- [x] TikTok `search-users` docs example: live profiles (no `exampleSecUid` / filler ids)
- [x] Price transparency on followers (Apify ~0.4/user) — same honesty as search-users; Ad Library 17/70 already documented as capped
- [x] TikTok `channel-details` docs: id + secUid + createTime + ttSeller + bioLink.risk (API already had them; snapshot `ok` was missing)
- [x] TikTok `/live` ≡ `/live-info` (shared runner); streamQualities keep hls/cmaf/dash/lls; offline omits viewerCount
- [x] TikTok user-followers/followings: keep `region` key (null when omitted); fix filler nextCursor; docs key order
- [x] TikTok aweme lists (`channel-posts` / top-search / hashtag / music via mapper): `videoUrl` + `downloadUrl` (+ no-wm when present), `mediaUrlsExpireAt`; author id/secUid; drop `description`=`caption`; keep isAd/isPaidPartnership/shopProductUrl
- [x] TikTok `profile-region`: promote `id` / `secUid` / `createTime` / `createTimeUnix` / `ttSeller` / `isOrganization` from `raw.user` (same upstream as channel-details)
- [x] Field-doc slug overrides: profile-region `videos`/`likes`/`verified`/`region`; search-suggestions `region`/`language` (market, not creator)
- [x] search-suggestions billing copy → flat 2 credits (aligned with param table + FAQ)
- [x] TikTok `comment-replies`: authorId / authorSecUid / commentLanguage (same contract as comments; docs example was stale Apify shape)
- [x] Twitter `user-tweets`: docs say most popular ~100 (not recent/latest); ISO `publishedAt`; hashtags/media arrays; conversationId/source/isQuote/author.id; views/bookmarks when exposed
- [x] Twitter `profile`: `displayName` (+ `name` BC); `verified` always present; docs delivers no longer generic "when exposed"
- [x] Twitter `tweet-details`: hydrate retweets/quotes/author.followers from user-tweets timeline (or profile fallback); `isRetweet` in example
- [x] Twitter shared tweet contract: `engagement` always 6 keys; ISO `publishedAt` on search + user-tweets + tweet-details; `hashtags[]` on search; TweetResultByRestId path for details
- [x] Twitter `community-tweets`: flat 2 native / ~0.7 Apify; `url`+`communityName`+`memberCount`; cURL uses community URL; ISO+6-key tweets

## Next turn — priority order (Twitter block continued)

| # | Work | Effort | Notes |
|---|------|--------|-------|
| 1 | Deploy stamp re-verify community-tweets cURL + pricing copy + meta fields | Low | Footer stamp first |
| 2 | Price-transparency pass: other 18/70/20/17 credit families (same search-users sentence) | Low | Ad Library, shorts-comments, LinkedIn ad-details |
| 3 | Twitter search + community-tweets: cursor + sort + since/until | Med | Brand listening / monitoring |
| 4 | User-tweets GraphQL path so views/bookmarks fill (not just null keys) | Med | Syndication omits |
| 5 | `professional.category` + `parody_commentary_fan_label` | Low | Brand safety |
| 6 | Vaat/teslim lint (request≠response + longDescription ⊆ example keys) | Low | Automate |
| 7 | Remaining platforms | Medium | |

## YouTube — open quality notes

- playlist vs playlist-videos: same mapper in code; stale SSG made them look different — re-check both on same docs stamp.
- replyCount on replies: values like 5/2/0 — confirm InnerTube meaning / whether to omit.
- comment-replies gaps vs /comments: no nextCursor/hasMore/totalComments; separate endpoint + 2 credits vs SC token-on-same-endpoint.
- author.channelId still often missing on comments (recurring).
- order (top/newest) missing on comments.
- publishedTime ISO on replies: confirm live.

## Process

1. Auditor checks footer stamp first.
2. After API shape changes: update `backend/api_snapshots.json` + `python backend/gen_examples.py`.
3. Bump `frontend/lib/seo.ts` → `CONTENT_UPDATED` when marketing/docs must invalidate.
4. Prefer SC-first diffs; do not re-prioritize fixed items without live re-probe.
