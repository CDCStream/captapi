# SC parity backlog (Captapi)

Last updated: 2026-08-04 (Threads profile + platformLimits). Next: remaining Threads endpoints / A-type promise lint.

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
- [x] Field-doc platform bleed: slug overrides + `lint:field-descs` (sticky keys); community `createdAt` → `.000Z`
- [x] Threads profile: `displayName` (+ `name`), `private`/`isPrivate`, `bioLinks`/`bioFragments`, `isThreadsOnlyUser`, `transparencyLabel`, HD versions (keys always present)
- [x] `platformLimits` docs field + UI block (Threads posts, Twitter user-tweets, FB profile-posts, YT comments, Ad Library search, TT/IG transcript, hashtag region)

## Promise-gap taxonomy (do not conflate)

| Type | Meaning | Fix |
|------|---------|-----|
| **A** | Hand-written promise on one endpoint (tagline / longDescription / delivers names a field that response lacks) | Add field or rewrite copy |
| **B** | Generic category template (`delivers()` channel/search/…) mismatches a specific endpoint | Override `delivers` on that slug |

Known A-type leftovers still open; B-type for `threads-profile` closed this turn.

## Next turn

| # | Work | Effort | Notes |
|---|------|--------|-------|
| 1 | Live re-probe Threads profile (bioLinks + isThreadsOnlyUser on a non-zuck account) | Low | zuck often has empty links / null threads-only |
| 2 | Remaining Threads endpoints vs SC (user-posts engagement shape, post-details) | Med | |
| 3 | A-type vaat lint (5 known cases) | Low | song-details, comment-replies, … |
| 4 | Price-transparency pass: other 18/70/20/17 credit families | Low | |
| 5 | Twitter search + community-tweets: cursor + sort + since/until | Med | |
| 6 | User-tweets GraphQL path for real views/bookmarks | Med | |
| 7 | Catalog-wide `to_iso()` helper (7 date formats) | Low | |
| 8 | Broaden field-desc lint beyond sticky keys (optional) | Low | |

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
