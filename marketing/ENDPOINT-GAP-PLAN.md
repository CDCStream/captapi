# Endpoint Competitive Gap Plan

Captapi vs ScrapeCreators. **Additive fields only** — never rename/remove keys customers already parse.

## Philosophy

- Keep envelope + camelCase + stable normalized shape
- Do not dump raw GraphQL / aweme by default
- Prefer exact counts when available; flag approximate otherwise
- Always expose stable platform IDs + real timestamps when raw has them

---

## #1-2 YouTube / TikTok video-details

See also VIDEO-DETAILS-GAP-PLAN.md. Phase 1 largely shipped (2026-08-01).

---

## #3 Instagram GET /v1/instagram/channel-details

**Constraint:** customers already use the 11-field shape — changes must be additive.

| Field | Priority | Status |
|---|---|---|
| id (numeric IG user id) | P0 | Ship additive |
| isPrivate | P0 | Ship additive |
| isBusinessAccount / isProfessionalAccount / categoryName | P0 | Ship additive |
| bioLinks[] (keep externalUrl as first/legacy) | P0 | Ship additive |
| profileImageHd (keep profileImage) | P1 | Ship additive |
| businessAddress | P1 | Ship additive when present |
| fetchedAt / count approximate flags | P1 | Ship additive |
| fbid | P2 | Ship additive |
| Recent posts embedded in profile | P2 | Deferred — keep separate /channel-posts |
| relatedProfiles[] | P2 | Deferred |
| Meta Verified vs classic (verificationType) | P2 | Deferred |

---

## #4 YouTube GET /v1/youtube/comments

| Field / param | Priority | Status |
|---|---|---|
| publishedTime ISO (keep publishedTimeText) | P0 | Ship when raw has unix/ISO; else null |
| authorChannelId (keep author string) | P0 | Ship additive |
| Fix hasCreatorHeart false positives | P0 | Ship |
| order=top\|newest | P1 | Deferred (InnerTube sort continuations) |
| replyLevel | P2 | Deferred |
| Document pagination ceiling | P2 | Docs only |
| Docs credit contradiction (flat 2 vs per-result) | P1 | Docs — billing is flat 2 |

---

## Cross-cutting

| Issue | Action |
|---|---|
| Stable IDs missing | Checklist for every entity normalizer |
| fetchedAt | Envelope middleware + per-payload where needed |
| Approximate counts | *IsApproximate / engagement.isApproximate |
| CDN expiry | mediaUrlsExpireAt / caption expiresAt |

---

## Next comparison candidates

1. TikTok Profile (channel-details)
2. Transcript (+ AI summary differentiator)
3. Facebook Ad Library
