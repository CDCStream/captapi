# SC parity backlog (Captapi)

Last updated: 2026-08-06 (instagram trending-reels: warm cron removed; cache-first 4h + single-flight; 502 on scrape fail). Next: Cursor pattern copy from truth-social-user-posts · TikTok Shop relatedVideos.

Audit habit: check footer stamp `N/M · docs YYYY-MM-DD` before judging a page. Field lists come from **examples** (`api_snapshots.json` · `api-examples.generated.ts`) · ship code + refresh snapshot **with `ok: true`** or `gen_examples.py` skips the slug and the page looks broken.

## Done recently (do not re-queue without re-verify)

- [x] `/apis` build stamp + short ISR (`CONTENT_UPDATED`, footer `PLATFORM/ENDPOINT · docs DATE`)
- [x] Docs intro: public social media (not "social media video")
- [x] `hasCreatorHeart`: inactive tip ? true (cache bump comments / comment-replies)
- [x] `playlist` + `playlist-videos`: enrich (ISO publishedAt, exact views, video id, channel{})
- [x] `playlist-videos` example: `totalVideos` + `channel{}`
- [x] `playlist` metadata-only (1 credit) vs `playlist-videos` paginated contents (cursor, 2/page)
- [x] playlist envelope: `channel{}` (not `owner` / `channelName`); `commentCount*` only on short rows
- [x] `community-posts`: drop author/image/video twins; publishedTimeApprox; …IsApproximate
- [x] `channel-playlists`: cursor + `totalVideos` (aligned with `/playlist`)
- [x] `channel-playlists`: `id` field
- [x] `channel-videos` / `channel-streams` / `channel-shorts`: player enrich path in code
- [x] `popular-hashtags`: Creative Center population videoCount vs sampleVideoCount (verify on current docs stamp)
- [x] Community post details: likeCount int + likeCountText (example may lag · re-check stamp)
- [x] TikTok `user-followers` / `user-followings`: id + secUid + createTime/region/language + total + nextCursor; native flat 1 credit
- [x] TikTok `search-users` docs example: live profiles (no `exampleSecUid` / filler ids)
- [x] Price transparency on followers (Apify ~0.4/user) · same honesty as search-users; Ad Library 17/70 already documented as capped
- [x] TikTok `channel-details` docs: id + secUid + createTime + ttSeller + bioLink.risk (API already had them; snapshot `ok` was missing)
- [x] TikTok `/live` ? `/live-info` (shared runner); streamQualities keep hls/cmaf/dash/lls; offline omits viewerCount
- [x] TikTok user-followers/followings: keep `region` key (null when omitted); fix filler nextCursor; docs key order
- [x] TikTok aweme lists (`channel-posts` / top-search / hashtag / music via mapper): `videoUrl` + `downloadUrl` (+ no-wm when present), `mediaUrlsExpireAt`; author id/secUid; drop `description`=`caption`; keep isAd/isPaidPartnership/shopProductUrl
- [x] TikTok `profile-region`: promote `id` / `secUid` / `createTime` / `createTimeUnix` / `ttSeller` / `isOrganization` from `raw.user` (same upstream as channel-details)
- [x] Field-doc slug overrides: profile-region `videos`/`likes`/`verified`/`region`; search-suggestions `region`/`language` (market, not creator)
- [x] search-suggestions billing copy · flat 2 credits (aligned with param table + FAQ)
- [x] TikTok `comment-replies`: authorId / authorSecUid / commentLanguage (same contract as comments; docs example was stale Apify shape)
- [x] Twitter `user-tweets`: docs say most popular ~100 (not recent/latest); ISO `publishedAt`; hashtags/media arrays; conversationId/source/isQuote/author.id; views/bookmarks when exposed
- [x] Twitter `profile`: `displayName` (+ `name` BC); `verified` always present; docs delivers no longer generic "when exposed"
- [x] Twitter `tweet-details`: hydrate retweets/quotes/author.followers from user-tweets timeline (or profile fallback); `isRetweet` in example
- [x] Twitter shared tweet contract: `engagement` always 6 keys; ISO `publishedAt` on search + user-tweets + tweet-details; `hashtags[]` on search; TweetResultByRestId path for details
- [x] Twitter `community-tweets`: flat 2 native / ~0.7 Apify; `url`+`communityName`+`memberCount`; cURL uses community URL; ISO+6-key tweets
- [x] Field-doc platform bleed: slug overrides + `lint:field-descs` (sticky keys); community `createdAt` · `.000Z`
- [x] Threads profile: `displayName` (+ `name`), `private`/`isPrivate`, `bioLinks`/`bioFragments`, `isThreadsOnlyUser`, `transparencyLabel`, HD versions (keys always present)
- [x] `platformLimits` docs field + UI block (Threads posts, Twitter user-tweets, FB profile-posts, YT comments, Ad Library search, TT/IG transcript, hashtag region)
- [x] Threads `user-posts`: flat 2 native / ~0.7 Apify; `engagement.views`; `threadId`/`replyToId`/`isReply`/`isQuote`; top-level `author{}`; limit note (~20·30 Meta cap)
- [x] Threads `post-details`: always `comments[]` + `relatedPosts[]` + `engagement.views` key; not a user-posts alias; FAQ honesty when reply tree omitted on logged-out hydrate; Threads likes/verified field-doc overrides (no YT/Bluesky bleed)
- [x] Threads `search` / `search-users`: flat native 2 / 1 (was ~18 / ~14 Apify-priced); search-users `id` + `profileImage` + `followers` key; honest Top-SERP / non-semantic people-search docs; verified false?null fix
- [x] Reddit `subreddit-details`: ISO `createdAt` (was float-string epoch); `id`/`rules[]`/`activeUsers`/`submitText`; category field-doc + sticky lint; case-insensitive param docs
- [x] Reddit search/list score honesty: authoritative `score` (not ups-downs doc lie); `scoreHidden` from `hide_score`; posts-only vs SC comments[]/media[] documented
- [x] Pinterest `board`: cURL board URL (not pin); `saves` + `imageOriginal` + `images{}`; top-level `author{}`; destinationUrl field-doc overrides
- [x] Pinterest `user-boards`: stop account-scoped `followers` twin; stable row shape; Redux map + 474x cover + ISO `createdAt`; docs two-way (undocumented fields)
- [x] LinkedIn `company`: About specialties/size/founded/organizationType + similarPages[]; employeeCount vs employees[]; Apify `identifier:[slug]` fix; slogan/cover enrich; funding/employees[] people documented gaps
- [x] LinkedIn `company-posts`: always-key `engagement{likes,comments,reposts}`; permalink hydrate when homepage LD omits counts (A-type headline fix)
- [x] Facebook Events: local-offset `startDate`/`endDate` + `timezone`; derive `duration`/`isPast`/`eventType`; `organizers[].id`; drop `organizer` string + facepile `usersResponded`; field-doc overrides (no LinkedIn/Bluesky/song bleed)
- [x] Facebook Events canonical: profile-events yearless·startDate; search location/from/to + relevance; no "Happening now"; shared Event shape; comedy Chicago example; flat-2 billing docs
- [x] Rumble: real embedId only (no permalink fabricate); durationSeconds+durationText; type video|short|live; FIELD_DESCS platform bleed sealed into SLUG_FIELD_DESCS
- [x] Truth Social (3 endpoints): prominent-only auth warning + honest use cases; `locked`/`bot`/`group`/`location`/`acct`/`emojis`/`fields[].verifiedAt`; ISO `lastStatusAt`; profile/post flat 1 credit; user-posts 2 native (~0.85 Apify); slug field docs
- [x] Truth Social posts: HTML→text no longer breaks span-soft-wrapped URLs; `links[]` from `<a href>`; top-level `author{}` + slim per-post author; `externalVideoId`→Rumble; upvotes/downvotes; `card`; `media.meta`/`durationSeconds`; `missing.png`→null; limit-80 docs; use cases not video-library boilerplate
- [x] Truth Social post + user-posts: shared mapper gains `reblog`/`quote`/`inReplyTo*` chain, platform `mentions[]`/`tags[]`, `poll`, `visibility`, `spoilerText`, `sponsored`, `pinned`, post-level `group` (session flags still omitted)
- [x] Text transcripts (`linkedin/post-transcript`, `reddit/post-transcript`, `twitter/transcript`): `timingSource=none`, omit `start`/`duration`/`timestamp` (returned only when `captions`), segment `index`/`wordCount`/`charStart`/`charEnd`, top-level `estimatedReadSeconds` @ 200 wpm; LinkedIn strips `| N comments on LinkedIn`, ugcPost `publishedAt` via VideoObject
- [ ] **Cursor pattern rollout** — reference ready on `truth-social-user-posts` (`nextCursor` + `hasMore` + `cursor` param + honest null docs). Effort dropped to Low: copy this shape to ~35 list endpoints that still invent offsets or omit hasMore.

## Promise-gap taxonomy (do not conflate)

| Type | Meaning | Fix |
|------|---------|-----|
| **A** | Hand-written promise on one endpoint (tagline / longDescription / delivers names a field that response lacks) | Add field or rewrite copy |
| **B** | Generic category template (`delivers()` channel/search/·) mismatches a specific endpoint | Override `delivers` on that slug |
| **C** | Response ships fields the docs never name (inverse of A) | Document or strip · two-way promise lint |

Known A-type leftovers still open; B-type for `threads-profile` closed this turn. C-type caught on `pinterest-user-boards` (privacy/sectionCount/coverImage/createdAt were live but undocumented).

## Cross-cutting (auditor meta-finding)

| # | Work | Effort | Notes |
|---|------|--------|-------|
| ? | **Canonical mapper per platform** · wire every sibling endpoint to the platform's richest normalize (engagement / author / dates). Validated on 8 platforms: X, YT, TT, Reddit, IG, Threads, LI, · | Med / highest ROI | Most backlog items are "connect existing code", not greenfield |
| | LinkedIn: `search-posts` engagement · `company-posts` (shipped hydrate+always-key; confirm deploy) | | |
| | Same pattern: TT followers·followings; YT videos·streams; IG hashtag·reels-search; · | | |

## Next turn

| # | Work | Effort | Notes |
|---|------|--------|-------|
| 1 | TikTok Shop: relatedVideos[] + commissionRate on showcase; cursor/page; shop_slogan | Med | reviews docs + showcase PDP hydrate shipped; masked reviewer handles still a platform limit |
| 2 | LinkedIn company `funding` + featured `employees[]` people (SC-rich) | Med | guest HTML empty; Apify funding blob empty for Shopify |
| 3 | LinkedIn company-posts: reaction breakdown + postType/media carousels | Med | totals ship; SC-style reactions{} still open |
| 3 | LinkedIn company similarPages `image` fill rate | Low | guest cards often omit media.licdn logos |
| 5 | Pinterest board-scoped followers (SC path) | Med | still null after account-twin fix |
| 6 | Pinterest board + user-boards cursor | Med | saves already on board/user-pins mapper |
| 7 | Reddit search `comments[]` (+ optional `media[]`) | Med | |
| 8 | Catalog-wide `to_iso()` + price-anomaly pass (Pinterest 13 vs SC 1) | Low | |
| 8b | Cursor (`nextCursor`/`hasMore`/`cursor`) → ~35 lists; ref = truth-social-user-posts | Low | was Med |
| 9 | Two-way promise lint (A missing + C undocumented) | Low | |
| 10 | Propagate Reddit sort+timeframe+cursor to TT/X/Threads/IG search | Med | |
| 11 | Threads comments GraphQL + search sort/since-until | Med | |
| 12 | Entity-search quality (Threads/FB/Google) | Med | |

## YouTube · open quality notes

- playlist vs playlist-videos: same mapper in code; stale SSG made them look different · re-check both on same docs stamp.
- replyCount on replies: values like 5/2/0 · confirm InnerTube meaning / whether to omit.
- comment-replies gaps vs /comments: no nextCursor/hasMore/totalComments; separate endpoint + 2 credits vs SC token-on-same-endpoint.
- author.channelId still often missing on comments (recurring).
- order (top/newest) missing on comments.
- publishedTime ISO on replies: confirm live.

## Process

1. Auditor checks footer stamp first.
2. After API shape changes: update `backend/api_snapshots.json` + `python backend/gen_examples.py`.
3. Bump `frontend/lib/seo.ts` · `CONTENT_UPDATED` when marketing/docs must invalidate.
4. Prefer SC-first diffs; do not re-prioritize fixed items without live re-probe.
