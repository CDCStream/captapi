# SC parity backlog (Captapi)

Last updated: 2026-08-04 (TikTok user-followers/followings + search-users examples).

Audit habit: check footer stamp `N/M · docs YYYY-MM-DD` before judging a page. Field lists come from **examples** (`api_snapshots.json` → `api-examples.generated.ts`) — ship code + refresh snapshot or the docs still look broken.

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

## Next turn — priority order

| # | Work | Effort | Notes |
|---|------|--------|-------|
| 1 | Re-verify TT followers live on prod (signer on) | Low | Confirm id/secUid/total/nextCursor + 1 credit billing |
| 2 | Remaining TikTok endpoints (trend trio, shop leftovers, …) | Medium | Continue SC-first |
| 3 | totalVideos / universe size on list endpoints | Low | SC pattern; exists on youtube/comments + playlist + TT followers |
| 4 | trending-shorts → real trend source (not keyword search) | Medium | Marked broken in YouTube block closeout |
| 5 | channel-shorts / shorts-comments pricing (20 vs flat 2) | Low | Confirm live billing + docs |
| 6 | channel-streams Live tab only (not Videos bleed) | Medium | Live-tab gate in code — confirm prod + docs |
| 7 | comment-replies: nextCursor + hasMore | Medium | Max 500 without cursor loses deep threads |
| 8 | Ad Library filters + LinkedIn targeting{} | Medium | |
| 9 | Remaining platforms (Twitter 5, Threads 5, …) | Medium | Continue SC-first audit |

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
