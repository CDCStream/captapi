// Changelog data layer: reads changelog_entries from Supabase with a static
// fallback so the page renders even before the migration is applied.
import { getServiceClient } from "@/lib/supabase/admin";

export type ChangelogCategory =
  | "feature"
  | "improvement"
  | "fix"
  | "integration"
  | "platform";

export interface ChangelogEntry {
  id: string;
  publishedAt: string; // ISO date (YYYY-MM-DD)
  category: ChangelogCategory;
  title: string;
  description: string;
  items: string[];
}

export const CATEGORY_LABELS: Record<ChangelogCategory, string> = {
  feature: "New",
  improvement: "Improved",
  fix: "Fixed",
  integration: "Integrations",
  platform: "Platforms",
};

interface ChangelogRow {
  id: string;
  published_at: string;
  category: string;
  title: string;
  description: string | null;
  items: unknown;
}

function parseRow(row: ChangelogRow): ChangelogEntry {
  return {
    id: row.id,
    publishedAt: row.published_at,
    category: (row.category as ChangelogCategory) ?? "improvement",
    title: row.title,
    description: row.description ?? "",
    items: Array.isArray(row.items) ? row.items.filter((i): i is string => typeof i === "string") : [],
  };
}

/** Static mirror of the migration seed — used only when the table is unavailable. */
const FALLBACK_ENTRIES: Omit<ChangelogEntry, "id">[] = [
  {
    publishedAt: "2026-08-04",
    category: "fix",
    title: "Reddit subreddit-details: ISO createdAt, rules[], t5_ id",
    description:
      "Docs example showed createdAt as a float-string Unix epoch (\"1201327674.0\") while FIELD_DESCS promised ISO 8601 — the worst date-format variant in the catalog. Mapper now never echoes raw epochs; live about.json + about/rules fill id (t5_…), activeUsers (currently online — not mislabeled weekly actives), rules[], and submitText. category field-doc no longer leaks YouTube SponsorBlock enums onto Reddit; sticky lint covers category. Param copy documents case-insensitive names (Captapi advantage vs ScrapeCreators' case-sensitive warning).",
    items: [
      "createdAt → ISO-8601 UTC (never \"1201327674.0\")",
      "id (t5_…) + activeUsers + rules[] + submitText",
      "category field-doc override + sticky lint",
      "Case-insensitive subreddit names documented",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "improvement",
    title: "Threads search + search-users: flat native pricing + richer users",
    description:
      "threads/search was ~18 credits and search-users ~14 for the same native Decodo hydrate TikTok/Twitter already bill flat. Native search is now flat 2 (twitter/search parity); search-users flat 1 (TikTok/SC parity). Apify fallback stays ~0.7/result. search-users adds id + profileImage + followers (keyed, usually null). Docs drop the false “topic-related profiles” promise — users are authors of keyword SERP hits — and spell out Meta Top ranking, stale posts, and engagement-farm spam. verified no longer collapses false→null via or.",
    items: [
      "search: flat 2 native / ~0.7 Apify (was ~18)",
      "search-users: flat 1 native / ~0.7 Apify (was ~14)",
      "search-users: id + profileImage + followers key",
      "Honest platformLimits + FAQ (Top SERP, no sort/date, not semantic people-search)",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "improvement",
    title: "Threads post-details: comments[], relatedPosts[], views key",
    description:
      "threads/post-details was a same-shape alias of a single user-posts card — no fields that justified a details endpoint, and Threads had no comments surface at all. The permalink hydrate now always returns comments[] (inline same-thread replies when Meta embeds them; [] on viral logged-out pages) and relatedPosts[] from BarcelonaLoggedOutRelatedPosts (no second call). engagement.views is always keyed (often null on web hydrate). Field-doc overrides stop YouTube/Bluesky copy leaking onto Threads pages; FAQ documents the honest empty-comments case vs ScrapeCreators' deeper GraphQL path.",
    items: [
      "comments[] + relatedPosts[] always present on post-details",
      "engagement.views keyed; bare Meta GK view_counts ints ignored",
      "Threads field-doc overrides for likes/verified/views/publishedAt",
      "FAQ: not an alias; empty comments = hydrate limit, not a missing key",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "improvement",
    title: "Threads user-posts: flat 2 native, views, thread chain",
    description:
      "threads/user-posts was still Apify-priced at ~0.7/post (~14 at default) even on the free native profile hydrate — same soft-cap surface as ScrapeCreators and Twitter user-tweets (flat 2). Native path is now flat 2; Apify fallback stays ~0.7/post (min 2), with a FAQ matching the user-followers pricing-honesty template. Posts gain engagement.views (when Meta exposes view_counts), threadId/replyToId/isReply/isQuote for multi-part Threads, and a top-level author{} so profileImage is not repeated on every row. limit param documents Meta's ~20–30 public-post ceiling.",
    items: [
      "Flat 2 credits native; ~0.7/post Apify fallback (min 2)",
      "engagement.views + threadId/replyToId/isReply/isQuote",
      "Top-level author{}; slim per-post author (no repeated avatar URL)",
      "limit note: Meta only exposes ~20–30 public posts",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "improvement",
    title: "Threads profile cross-platform fields + platformLimits docs",
    description:
      "Threads profile now ships displayName (+ name BC), private/isPrivate (TikTok + Instagram keys), bioFragments from text_app_biography, and keeps isThreadsOnlyUser / bioLinks.verified / transparencyLabel always keyed. Docs add an optional platformLimits block (SC-style honest ceilings) on Threads user-posts, Twitter user-tweets, Facebook profile-posts, YouTube comments, Ad Library search, and TikTok/Instagram transcripts. threads-profile What you get is endpoint-specific (no more generic channel template promising vague external links).",
    items: [
      "threads/profile: displayName, private/isPrivate, bioFragments[]",
      "platformLimits section on 8 high-traffic endpoints",
      "threads-profile delivers override (B-type template gap closed)",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "fix",
    title: "Field-doc platform bleed + twitter/community ISO createdAt",
    description:
      "Shared FIELD_DESCS was leaking wrong-platform copy into sibling pages (worst case: creator on twitter/community said \"Kick clip\"). Sticky keys now have slug overrides; describeField prefers slug overrides for all value shapes; npm run lint:field-descs fails the build when a sticky field description names another platform. twitter/community createdAt normalized to catalog ISO (.000Z) instead of Python isoformat with microseconds/+00:00.",
    items: [
      "twitter/community creator field note is X founder handle (not Kick)",
      "Slug overrides for the 8 audited sticky fields + lint:field-descs",
      "community createdAt → YYYY-MM-DDTHH:MM:SS.000Z",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "fix",
    title: "Twitter community-tweets: flat 2 native, community meta, fixed cURL URL",
    description:
      "community-tweets was billed ~0.7/tweet (18 credits at default limit) even on the free guest GraphQL path — same surface as search (flat 2). Native path is now flat 2; Apify fallback stays ~0.7/tweet (min 2), documented like search-users. Response adds url + communityName + memberCount. Docs/cURL no longer use a tweet/status URL (request≠response); Try-it uses x.com/i/communities/…. Tweets use the shared ISO + 6-key engagement contract. Cache v5.",
    items: [
      "Flat 2 credits native; ~0.7/tweet Apify fallback (min 2)",
      "communityName + memberCount + community url in response",
      "cURL/Try-it use community URL (not a status URL)",
      "ISO publishedAt + engagement 6-key shape on tweets[]",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "fix",
    title: "Twitter tweet contract: one engagement shape + ISO dates everywhere",
    description:
      "search / user-tweets / tweet-details now share one mapper contract: engagement always emits views,likes,replies,retweets,quotes,bookmarks (null when the upstream surface omits a metric), publishedAt is ISO-8601 UTC on all three, and hashtags[] is always present. Search docs example was still shipping raw Twitter dates — refreshed. tweet-details tries guest GraphQL TweetResultByRestId (same surface as search) before popular-timeline hydrate. Cache bumps: search v4, user-tweets v5, tweet-details v6.",
    items: [
      "Shared engagement{} 6-key shape across search / user-tweets / tweet-details",
      "ISO publishedAt on search (was raw RFC2822 in docs)",
      "hashtags[] always present on search results",
      "TweetResultByRestId path for views/bookmarks when guest GraphQL works",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "fix",
    title: "Twitter profile + tweet-details: sibling field parity",
    description:
      "twitter/profile already returned verified from GraphQL; docs example now also emits displayName (name kept for BC) so cross-platform clients use one key. tweet-details was thinner than user-tweets because syndication tweet-result omits retweet_count/quote_count/followers — we now hydrate those from the author's popular timeline (same surface as user-tweets) when the id matches, else profile for author.followers. Cache bumps: profile v8, tweet-details v5.",
    items: [
      "profile: displayName + verified always present",
      "tweet-details: retweets + quotes + isRetweet + author.followers",
      "Docs examples refreshed from live NASA / NASASpox",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "fix",
    title: "Twitter user-tweets: popular-not-latest warning + ISO publishedAt",
    description:
      "Docs said \"recent tweets\" while Twitter's public timeline embed returns ~100 most popular posts (not chronological) — same limit ScrapeCreators warns about. Copy, OpenAPI summary, use cases, and limit text now say so explicitly (not for new-tweet monitoring). publishedAt is ISO-8601 UTC (no raw \"Thu Apr 28…\"). hashtags[]/media[] always present; conversationId, source, isQuote, author.id, and engagement.views/bookmarks when the upstream row exposes them (timeline embed often omits views/source).",
    items: [
      "Docs: most popular ~100 — not chronological latest",
      "publishedAt ISO-8601 UTC",
      "hashtags[] + media[] always emitted",
      "conversationId / source / isQuote / author.id when exposed",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "fix",
    title: "TikTok comment-replies: authorId / authorSecUid / commentLanguage in docs + shape",
    description:
      "Docs promised the same identity fields as /comments, but the example was an old Apify-shaped payload without authorId/authorSecUid/commentLanguage. Native _map_reply already mapped them; we now keep those keys even when null, Apify fallback keeps them too, cache bumped to v4, and the example was refreshed from a live reply page (distinct authorIds + commentLanguage).",
    items: [
      "authorId + authorSecUid + commentLanguage always present on replies",
      "Docs example refreshed (totalReplies + live identity fields)",
      "comment-replies cache v4",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "improvement",
    title: "TikTok profile-region: id/secUid/createTime/ttSeller promoted from raw",
    description:
      "profile-region already fetched webapp.user-detail (same blob as channel-details) but left id, secUid, createTime, ttSeller, and isOrganization buried under raw.user. Those fields are now top-level — same names as channel-details — with no extra scrape. Docs also fix field-description leakage (videos is an integer count here, not Ad Library media objects; search-suggestions region is the request market) and correct search-suggestions billing copy to flat 2 credits.",
    items: [
      "profile-region: id, secUid, createTime, createTimeUnix, ttSeller, isOrganization",
      "Slug field-doc overrides for videos / likes / verified / region",
      "search-suggestions: flat 2 credits (not per suggestion)",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "feature",
    title: "TikTok list posts: videoUrl + download URLs (channel-posts / search / music)",
    description:
      "Instagram list endpoints already returned videoUrl; TikTok channel-posts (and other aweme-backed lists) only had thumbnails — so the Archiving use case could not pull media. Native aweme mapping now surfaces videoUrl, downloadUrl, downloadUrlNoWatermark when TikTok exposes them, plus mediaUrlsExpireAt for CDN expiry. author.id/secUid, isAd/isPaidPartnership, and shopProductUrl stay on the row; the caption/description twin is dropped. Docs example refreshed from a live @paw.dreams0 probe.",
    items: [
      "videoUrl / downloadUrl / downloadUrlNoWatermark + mediaUrlsExpireAt on aweme lists",
      "author.id + secUid; isAd / isPaidPartnership kept after finalize",
      "description=caption duplicate removed",
      "channel-posts cache bump (v11) + docs stamp",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "fix",
    title: "TikTok user-followers docs stamp: same shape as followings (1 credit)",
    description:
      "user-followers already shared the native signer mapper with user-followings (id/secUid/createTime/language/total/nextCursor, flat 1 credit) — some /apis pages were stuck on an older SSG build showing 20 credits. Docs examples reordered (total/hasMore/nextCursor first), region kept as null when TikTok omits it, and the round filler nextCursor replaced. Deploy refreshes the followers stamp to match followings.",
    items: [
      "user-followers example: total + hasMore + nextCursor + region key",
      "region/language keys retained as null when upstream omits them",
      "SSG/docs stamp alignment with user-followings (1 credit)",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "improvement",
    title: "TikTok Live: true /live ↔ /live-info alias + hls/cmaf in streamQualities",
    description:
      "GET /v1/tiktok/live and /live-info now share one runner (identical JSON). streamQualities keeps flv/hls/cmaf/dash/lls when TikTok exposes them (dash falls back to cmaf MPD); streamUrls prefers playable HLS/CMAF before FLV. Offline rooms omit stale viewerCount; totalEnterCount stays as last-known. paidEvent + gameTagId/hashTagId retained; duplicate followingCount dropped. Docs example uses a room with real HLS; status field copy is live-specific (2 = live).",
    items: [
      "/live and /live-info: same payload (prefer /live at 1 credit)",
      "streamQualities: hls + cmaf/dash + lls (not FLV-only)",
      "viewerCount omitted when isLive is false",
      "Slug-specific status docs for TikTok Live",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "fix",
    title: "TikTok channel-details docs: id + secUid + ttSeller example restored",
    description:
      "GET /v1/tiktok/channel-details already returned id, secUid, createTime, ttSeller, bioLink.risk, and commerce flags — but the docs example had dropped ok:true so gen_examples skipped the slug, leaving a thin pre-enrichment sample (no identity). Snapshot refreshed from live @natgeo; catalog/FAQ lead with handle→id/secUid resolve and the Shop bridge (ttSeller).",
    items: [
      "Docs example: id + secUid + createTime + ttSeller + bioLink.risk",
      "region key added when TikTok exposes it",
      "FAQ: resolve contract + ttSeller → Shop chain",
      "Cache bump v=5",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "improvement",
    title: "TikTok user-followers/followings: secUid, cursor, total — search-users parity",
    description:
      "GET /v1/tiktok/user-followers and /user-followings now return the same identity fields as search-users (id + secUid), plus createTime/createTimeUnix, region, and language when TikTok exposes them. Responses include total (profile followerCount/followingCount), hasMore, and nextCursor (TikTok minCursor). Native path is flat 1 credit (was ~20 Apify); Apify fallback stays ~0.4/user (min 5). Docs examples: search-users fake exampleSecUid rows replaced with live profiles; followers/followings snapshots show id/secUid + total.",
    items: [
      "user-followers/followings: id + secUid + createTime/region/language",
      "total + nextCursor/hasMore (minCursor) — page mega audiences",
      "Native flat 1 credit (SC parity); Apify ~0.4/user documented",
      "search-users docs example: real secUid (no exampleSecUid filler)",
    ],
  },
  {
    publishedAt: "2026-08-04",
    category: "fix",
    title: "hasCreatorHeart false positives; refresh playlist examples + totalVideos",
    description:
      "YouTube comment toolbars include heartActiveTooltip (❤ by @Channel) on every unhearted comment — older builds treated any non-empty tooltip as hasCreatorHeart=true (10/10 on rickroll replies). Detection stays strict; comments/comment-replies caches bumped. Docs examples regenerated: playlist-videos now shows totalVideos + channel{}, comment-replies hearts are false, footer docs stamp → 2026-08-04.",
    items: [
      "hasCreatorHeart: never true from inactive ❤ by @Channel tooltip",
      "playlist-videos example: totalVideos + channel{} (was missing from snapshot)",
      "comment-replies example: hasCreatorHeart false; cache v bump",
      "docs stamp CONTENT_UPDATED → 2026-08-04",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Align /apis SSG builds; playlist enrich + channel-playlists id",
    description:
      "Marketing pages were sticky across deploys — /apis index could show an older ENDPOINT_COUNT (e.g. 173) while newer slug pages showed 177, hiding already-shipped fixes like popular-hashtags videoCount docs. Footer now stamps PLATFORM_COUNT/ENDPOINT_COUNT · docs DATE, CONTENT_UPDATED bumped, and ISR is 60s on marketing/apis. youtube/playlist player-enriches videos for exact viewCount + ISO publishedAt (owner/totalVideos already native). channel-playlists rows expose id for chaining into /playlist.",
    items: [
      "/apis ISR 60s + footer build stamp (N/M · docs DATE)",
      "CONTENT_UPDATED → 2026-08-03 (force catalog/sitemap freshness)",
      "youtube/playlist(+videos): enrich_video_cards (exact views, ISO)",
      "channel-playlists: id field on each playlist row",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "channel-streams Live-tab gate + video enrich; video-sponsors overlaps/minVotes",
    description:
      "channel-streams was returning Videos for channels without a Live tab (InnerTube still accepts streams params — MrBeast looked like live VODs). We now require a Live tab (hasLiveTab:false ⇒ empty), player-enrich streams/videos for exact viewCount + ISO publishedAt, and bill streams flat 2 credits. video-sponsors sorts by startSeconds, drops votes<0 by default (minVotes), flags overlapsWith, and exposes coverageSeconds for density without double-counting.",
    items: [
      "channel-streams: Live tab gate + hasLiveTab; flat 2 credits",
      "channel-videos/streams: player enrich (exact views, ISO dates)",
      "video-sponsors: sort, minVotes, overlapsWith, coverageSeconds",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Linkbio (lnk.bio): bypass Cloudflare 403 that marked the platform Degraded",
    description:
      "lnk.bio started returning Cloudflare challenge pages to plain httpx, so /v1/linkbio/page failed with HTTP 502 and /status showed Linkbio as Degraded. Fetches now prefer Chrome TLS impersonation (curl_cffi) before residential/direct httpx, restore profile + links for handles like @charlidamelio, and bump the page cache key.",
    items: [
      "browser_fetch: Chrome impersonation for CF-protected HTML",
      "creator-pages / linkbio: use browser_fetch; cache v9",
      "curl_cffi dependency for production Docker image",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Community posts: numeric likes + pollOptions; /apis ISR; cache docs no longer overclaim cacheMaxAge",
    description:
      "community-post-details now shares the list schema: likeCount (int) + likeCountText (was string likes like \"727K\"), channel{}, ISO publishedAt/publishedTime, and pollOptions[{text,voteCount,percentage}] + totalVotes for polls (per-choice votes often null publicly — YouTube gates them). Marketing /apis pages use revalidate=3600 so PLATFORM_COUNT/ENDPOINT_COUNT cannot stick across mixed SSG deploys; OG image reads live catalog counts (was hardcoded 173). Generic cache= param copy no longer tells every endpoint to prefer cacheMaxAge — only profile endpoints that actually accept it.",
    items: [
      "community-post-details: likeCount int + likeCountText; drop string likes",
      "polls: postType=poll + pollOptions[] + totalVotes",
      "/apis ISR 1h; OG uses ENDPOINT_COUNT/PLATFORM_COUNT",
      "cache param docs: cacheMaxAge only where supported",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "YouTube comments: ISO publishedTime + comment field docs; stale marketing copy audit",
    description:
      "Comment rows now approximate publishedTime (ISO) from publishedTimeText (including \"… (edited)\" labels) so they are sortable like SC. Generic comments responseStructure fallback no longer documents wrong names (total/likes/replies → totalReturned/likeCount/replyCount). shorts-comments params are flat 2 credits + cache (same engine as /comments). Production /apis scan: 210 pages, 0 with stale \"29 platforms / 179 endpoints\" footer — remaining \"29 platforms\" hits are blog body copy in Supabase and a historical changelog title. hasCreatorHeart rejects inactive chrome tooltips like \"❤ by @Channel\".",
    items: [
      "comments: publishedTime ISO from relative labels; keep publishedTimeText",
      "docs: comments structure uses likeCount/replyCount/totalReturned",
      "shorts-comments: lpFlat 2 + cache; SKILL credits 2",
      "hasCreatorHeart: ignore ❤ by @Channel inactive tooltips",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "YouTube Shorts: real trending feed + channel-shorts field fill (SC-first)",
    description:
      "channel-shorts was returning shelf stubs (thumbnailUrl/publishedAt/durationSeconds null, rounded viewCount) at 20 credits — ScrapeCreators' /v1/youtube/channel/shorts returns player-enriched rows for 1 credit. We now derive thumbnailUrl from the video id, enrich each Short via InnerTube player (exact views, publish date, duration, description, genre, engagement when exposed), and bill flat 2 credits. trending-shorts no longer searches the keyword \"trending\" (which surfaced 11-view videos with #Trending in the title); it uses YouTube's reel_watch_sequence feed — the same surface SC documents for /v1/youtube/shorts/trending. Optional q only seeds that sequence.",
    items: [
      "channel-shorts: thumbnail from id + player enrich; flat 2 credits (was 20)",
      "trending-shorts: reel_watch_sequence feed, not q=trending keyword search",
      "SC-style viewCountText/Int, durationMs/Formatted, like/comment when exposed",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "improvement",
    title: "Ad Library SC-parity audit: ctaType, trim, LinkedIn aliases — most fields already shipped",
    description:
      "Code audit vs ScrapeCreators: Facebook search already had status/media_type/sort_by/search_type/ad_type/start_date/end_date/cursor plus isActive, publisherPlatforms, cards, typed images/videos, pageLikeCount, politicalCountries, searchResultsCount — the docs example just hid them. Now ctaType is returned, trim is accepted (SC DX; payloads already lean), and the FB search example surfaces those fields. LinkedIn search already returned targeting{}, totalImpressions, impressionsByCountry[], totalAds, paginationToken — adds company + paginationToken input aliases, advertiserLinkedinPage, ISO dates, and stops treating creative headlines as company names on thin SERP rows. Remaining real gap vs SC: Facebook cursor is in-batch (HTML page), not Meta's multi-thousand POST cursor.",
    items: [
      "FB: ctaType + trim + SC-parity docs example (isActive/platforms/cards/…)",
      "LI: company/paginationToken aliases + advertiserLinkedinPage + ISO dates",
      "LI: never echo headline as advertiser.name",
      "Honest gap: FB nextCursor pages the HTML batch, not SC's deep cursor",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Facebook search-companies: brand match + pageId vs profileId",
    description:
      "search-companies no longer lists whoever appeared first in a keyword ad scrape (Sukeban / widget apps above Nike). Page names must contain the query tokens; exact and vanity matches rank first; empty beats off-brand spam. Each company now exposes pageId / advertiserId (pass to company-ads — Meta view_all_page_id) separately from profileId when facebook.com/{digits}/ uses a different numeric identity, plus libraryUrl. Docs spell the chain: search-companies → pageId → company-ads.",
    items: [
      "Name filter + rank (Nike first; Sukeban/IControl dropped for q=nike)",
      "pageId / advertiserId vs profileId disambiguation",
      "libraryUrl for view_all_page_id; company-ads docs say which id to pass",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Google/LinkedIn ad-details: AR+CR identity, countries[], DKI flag, 2 credits",
    description:
      "google/ad-details is not an alias of company-ads — it adds text/headline/landingUrl/impressions — but the docs example had mixed Nike legal entities (Inc. request → Retail BV response). Response id + advertiser.id now must match the request AR/CR; 404 explains Inc/BV/SRL are different entities. countries[] is ISO-3166 (no 27-name comma string); country is a single ISO when unambiguous. textIsTemplate marks {KeyWord:…} DKI macros. LinkedIn ad-details extracts advertiser.id from /company/{id}, keeps null keys for country/logo (no silent field loss), and both detail endpoints list at 2 credits native with Apify capped at 5 (was silent 17).",
    items: [
      "Google: strict AR+CR identity + chain-synced Nike, Inc. example",
      "Google: countries[] ISO + textIsTemplate for DKI",
      "LinkedIn: advertiser.id from company URL + stable null schema",
      "Google/LinkedIn ad-details: 2 credits native / Apify max 5",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Ad details: delivery fields + TikTok price/schema parity (no paid aliases)",
    description:
      "facebook/ad-details now surfaces Meta delivery extras when the library publishes them — platforms, demographicDistribution[], regionDistribution[], EU AAA / euTransparency, variantCount, isAaaEligible — and keeps those keys as null on commercial ads so the schema is honest. Creative fields still match a search hit for the same id (ID lookup is the primary DX). TikTok ad-details is no longer a 17-credit thinner twin of search: impressions (Unique users seen) parse is hardened, advertiser null keys match search, catalog bills 2 credits native with Apify capped at 5. Docs state alias honesty: detail endpoints that mirror search must either add fields or say so — never charge twice for the same payload silently.",
    items: [
      "FB ad-details: platforms + demography/region/EU AAA/variantCount (null when withheld)",
      "TT ad-details: impressions parity + 2 credits (Apify max 5, not 17)",
      "Docs: ID-lookup honesty — same creative as search unless Meta/TikTok add more",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Google advertiser-search → company-ads chain (Nike Inc., not SRL)",
    description:
      "advertiser-search no longer returns a single Italian NIKE SRL for q=nike&country=US. Brand queries are expanded (Nike, Inc. + siblings), ranked with country preference (US prefers Inc. over SRL/BV), and return multiple AR… entities so you can pick. company-ads adds resolvedAdvertiser{id,name,url}, sort=last_shown|first_shown, and stable null keys for text/headline/cta/landingUrl/spend. Chain: search → advertisers[0].id → company-ads?advertiser=AR…",
    items: [
      "advertiser-search: expand + rank multi-result (Nike, Inc. first for US)",
      "company-ads: resolvedAdvertiser + sort + stable null schema",
      "Docs/examples use AR167… Nike, Inc. for the creatives chain",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "improvement",
    title: "Ad libraries: advertiser unify, FB cursor/platforms, TikTok relevance + 2 credits",
    description:
      "Facebook Ad Library search collapses the same page id to one advertiser name (no Facebook vs Facebook App split), adds platforms filter + nextCursor paging through the HTML batch, and documents status/date/media filters for live campaigns. TikTok Ad Library search relevance-filters so query tokens must appear in advertiser/copy (empty beats spam), keeps FB-parity null keys for headline/cta/landingUrl/spend/advertiser.id, ISO firstShown dates, and bills flat 2 credits native (Apify capped at 5 — never the old ~70 trap). DSA still withholds Meta-style spend; use Creative Center Top Ads for CTR/brand ranking.",
    items: [
      "FB: same advertiser id → one canonical name/url/logo per response",
      "FB: platforms + cursor/nextCursor; status/date/media already wired",
      "TT: relevance filter + stable null schema + ISO dates",
      "TT pricing: 2 native / 5 Apify cap (documented vs old ~70)",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Analytics showcase: full YouTube metrics, failed[], engagementRateBasis",
    description:
      "Post analytics no longer ships views-only YouTube rows when watch-page enrich is thin — incomplete native responses fall through to Apify so likes, comments, publishedAt, and @handle populate on the vitrin example. author.username never echoes the display name. metrics.engagementRateBasis is always interactions/views on post/compare (do not compare to popular-creators). Compare adds status, failedCount, and failed[] so partial batches are auditable; publishedAt normalizes to UTC Z; docs never fall back to example.com lorem.",
    items: [
      "YouTube thin native → Apify when likes/comments/handle/date missing",
      "username = @handle only; displayName stays separate",
      "engagementRateBasis=interactions/views on every post metrics object",
      "compare: status + failed[] + failedCount; real docs example fallback",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "improvement",
    title: "LinkedIn profile: experience/education/similarProfiles + restricted masking",
    description:
      "LinkedIn /profile no longer short-circuits on a thin native shell — when HTML omits experience/education it enriches from Apify (detail, then full-sections) so B2B core fields actually arrive. Additive sections: experience[], education[], similarProfiles[], projects, publications, articles, activity, recommendations, certifications, languages. Guest-masked asterisk copy (******* …) is returned as description:null with restricted:true instead of star spam. connections remaining null is documented as a LinkedIn logged-out platform limit.",
    items: [
      "Native→Apify enrich when experience/education missing",
      "similarProfiles[] + richer section pass-through",
      "Masked ******* → null + restricted:true",
      "connections null = LinkedIn guest limit (not a bug)",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "feature",
    title: "Creator trust layer: createTime, verification triad, tipjar contact{}, cacheMaxAge",
    description:
      "Account trust signals that make Creator Verification / Partnership Qualification real. TikTok channel-details and popular-creators now expose createTime / createTimeUnix (account age), bioLink{link,risk}, ttSeller, commerce/organization flags, and contact{}. Twitter/X profile keeps blue / legacy / identity verification as separate bits (isBlueVerified ≠ isLegacyVerified ≠ isIdentityVerified), plus fastFollowers/normalFollowers, tipjarSettings → contact{emails,paymentHandles,links}, and expanded bioUrls. New cacheMaxAge=1d|3d|7d|14d|30d on key profile endpoints; JSON envelope already includes cached + cachedAt on hits.",
    items: [
      "TikTok: createTime + bioLink.risk + ttSeller on channel-details / popular-creators",
      "Twitter: isLegacyVerified + tipjar contact{} + fastFollowers",
      "cacheMaxAge 1d–30d on TikTok/Twitter/Instagram profile endpoints",
      "Envelope cached + cachedAt (not header-only)",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "improvement",
    title: "trending-feed: Creative Center orderBy/period/countryCode + Instagram profile pass-throughs",
    description:
      "trending-feed stays the rich For You feed by default, and now accepts SC-style filters — orderBy (hot|like|comment|repost), period (7|30|120), countryCode, and page — to read TikTok Creative Center popular videos (same chart as videos/popular) with pagination.totalCount (~500) while still hydrating engagement/author when possible. Instagram basic-profile / channel-details / profile-search now surface categoryName, fbid, relatedProfiles[] (edge_related_profiles), businessAddress, and likeAndViewCountsDisabled from the existing web_profile_info payload — no new scrape, niche discovery + IG↔FB join without a creator-search endpoint.",
    items: [
      "trending-feed: orderBy / period / countryCode / page + pagination.totalCount",
      "Instagram profiles: relatedProfiles[] + likeAndViewCountsDisabled",
      "categoryName + fbid + businessAddress parity across profile endpoints",
      "Post mappers: likeAndViewCountsDisabled (0 ≠ hidden likes)",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "feature",
    title: "TikTok Creative Center: popular-hashtags, popular-creators, popular-songs",
    description:
      "popular-hashtags and popular-creators now read TikTok Creative Center charts (ads.tiktok.com/business/creativecenter) instead of sample co-occurrence / invented formulas — so videoCount is a real population total (not \"17 from a 20-video sample\") and engagementRate is TikTok's official interact rate when exposed. New GET /v1/tiktok/popular-songs adds popular|surging sounds with rankDiff, trend[] time series, and commercialMusic / ifCml for brand-safe audio. Flat 2 credits on the Creative Center path. Optional query= on popular-hashtags still runs the legacy related-tag co-occurrence enrich.",
    items: [
      "popular-hashtags: Creative Center chart + rankDiff + trend[] (flat 2 credits)",
      "popular-creators: Creative Center first, then FYP / Apify fallthrough",
      "New popular-songs: rankType, commercialMusic, trend[], rankDiff",
      "country / period (7|30|120) / page / newOnBoard filters",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "improvement",
    title: "Instagram Reels: views != plays, location{}, Highlights, commercial flags",
    description:
      "engagement.views is video_view_count (reach-style) when Instagram exposes it; engagement.plays is total play count including replays — the gap can be ~2x. viewsInstagram remains Instagram-only plays (excludes Facebook cross-post); viewsFacebook is the FB share. location{} now includes slug, hasPublicPage, addressJson / address{}. New GET /v1/instagram/highlights and /highlights-details for persistent Story Highlight albums (not live Stories). isAd / isAffiliate / isPaidPartnership and previewComments.authorId are filled on feed and search paths when Instagram exposes them.",
    items: [
      "views vs plays vs viewsInstagram / viewsFacebook documented and emitted",
      "location{id,name,slug,address} on post/reel mappers",
      "GET /highlights + /highlights-details (flat 1 credit each)",
      "isAd / isAffiliate / isPaidPartnership on enriched search/feed rows",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "improvement",
    title: "YouTube search: viewCountText/Int + lives/shelves arrays",
    description:
      "YouTube search already returned typed results and filters (type, sortBy, uploadDate, duration, region). Each hit now also exposes viewCountText (e.g. 750K) plus viewCountInt (750000) so compact UI labels stay honest. Response adds lives[] / shelves[], and continuationToken as an alias of nextCursor. Docs note: duration filters apply to long-form videos, not Shorts.",
    items: [
      "viewCountText + viewCountInt on search hits",
      "lives[] / shelves[] partitioned arrays",
      "continuationToken alias for nextCursor",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "TikTok popular-creators: real engagementRate (not likes÷followers)",
    description:
      "engagementRate was lifetime likes ÷ followers, which ranks high-volume posters above high-engagement ones and contradicted our own docs. It is now (likes/videos)/followers × 100 (percent), with engagementRateBasis: \"avgLikesPerVideo/followers\". sort=engagement uses the corrected rate. Per-creator country no longer echoes the query market (misleading for non-US creators); use top-level country for the feed market and creator.region when TikTok exposes a profile locale. Additive: avgViews, id/secUid when present, and contact{emails,links} parsed from bio. Superseded later the same day by Creative Center as the primary source — this entry records the formula fix on the FYP fallthrough path.",
    items: [
      "engagementRate = avg likes per video / followers × 100",
      "engagementRateBasis documents the formula",
      "Removed query-country echo on each creator (region when known)",
      "contact{} from bio emails / PayPal / Cash App when present",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "TikTok posts always include engagement shares + empty hashtags",
    description:
      "strip_empty was dropping null engagement.shares and empty hashtags, so some music-posts rows looked like a different schema. Every finalized post now always has engagement{views,likes,comments,shares,saves} (missing → 0), hashtags[] / mentions[] (missing → []), and isAd / isPaidPartnership (missing → false). music-posts also echoes musicId from the request URL when the row omits it.",
    items: [
      "engagement.shares always present (0 when TikTok omits it)",
      "hashtags / mentions always arrays",
      "isAd / isPaidPartnership always boolean",
      "music-posts musicId echoed from the sound URL",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "TikTok author{} is one shape across list endpoints",
    description:
      "music-posts omitted author.followers (and id/secUid) when MUSIC_AWEME left them blank, while top-search included followers — two schemas for the same author concept. All post lists now go through build_author(): username, displayName, url, profileImage, plus id / secUid / followers / verified always present (null when TikTok's surface omits them).",
    items: [
      "build_author() shared by music-posts / top-search / channel-posts / video-details",
      "followers / verified / id / secUid keys kept even when null",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "TikTok durationSeconds is always float",
    description:
      "top-search could return whole-second durations as JSON integers (47) while music-posts returned floats (29.534), breaking typed clients that expect one type. durationSeconds is now always a float rounded to 3 decimals (47.0) on video-details, channel-posts, music-posts, top-search, hashtag search, and trending feed.",
    items: [
      "durationSeconds always float (3 dp) across TikTok post endpoints",
      "Whole seconds serialize as 47.0, not integer 47",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "TikTok hashtags from text_extra + mentions[] (no emoji bleed)",
    description:
      "List endpoints were regex-slicing hashtags out of captions, so trailing emoji stuck to tags (okaralover💪💪❤️), case variants doubled (Latinus + latinus), and @mentions were missing. Hashtags now prefer TikTok's text_extra[].hashtag_name / cha_list (caption regex only when structured data is absent, with emoji-trail stripping). Mentions arrive as mentions[{userId,secUid,username,start,end}] — same shape as video-details. Instagram channel-posts also dedupes identical hashtag doubles.",
    items: [
      "Canonical hashtags from text_extra (emoji / case / dupe fixed)",
      "mentions[] with userId + secUid on music-posts / channel-posts / search",
      "Instagram hashtag list dedupe (NASAHubble ×2)",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "TikTok music-posts: author.verified is null when unknown",
    description:
      "TikTok's music feed (MUSIC_AWEME) often omits verification fields. We were defaulting missing badges to false, which falsely marked verified creators (e.g. Khaby Lame) as unverified. author.verified is now true/false only when TikTok exposes a badge signal; otherwise null. For definitive verification, use Channel Details.",
    items: [
      "author.verified null when MUSIC_AWEME omits the badge",
      "false only means confirmed unverified — never invented",
      "Docs note: use Channel Details for definitive verification",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "YouTube list publishedAt is ISO-8601 (not \"4 days ago\")",
    description:
      "channel-videos (and the shared channel-tab / search / hashtag / playlist card path) was putting YouTube's relative labels into publishedAt, which breaks typed SDKs, date sort/filter, and upload monitors. publishedAt is now always ISO-8601 (approximate from the relative label when YouTube does not expose an exact timestamp); the original string is kept as publishedTimeText — same pattern as ScrapeCreators' publishedTime + publishedTimeText.",
    items: [
      "publishedAt ISO on channel-videos / shorts / streams / search / hashtag / playlist",
      "publishedTimeText retains \"4 days ago\" style labels",
      "Comments + community posts get the same split",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Instagram channel-posts: IG/FB view split + per-item fields + user{}",
    description:
      "channel-posts now matches ScrapeCreators' documented play split and list shape more closely. engagement.views is total plays; viewsInstagram is Instagram-only (exclude Facebook cross-post); viewsFacebook is the FB share — accounts that cross-post can look ~20% inflated if you only read views. Each item maps from its own feed row (shortcode/pk — never zip play_counts across Image/Sidecar gaps). GraphQL video_view_count undercounts are dropped when likes > views. Feed overlay also backfills productType, durationSeconds, hasAudio, music{}, isPaidPartnership. Response includes top-level user{} (profile) and hasMore so one call covers posts + account.",
    items: [
      "viewsInstagram / viewsFacebook on videos (use viewsInstagram for IG-only)",
      "Per-item overlay; Image/Sidecar views: null",
      "productType, durationSeconds, hasAudio, music{}, isPaidPartnership",
      "Top-level user{} + hasMore (no second profile call)",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "improvement",
    title: "TikTok comments: authorId, authorSecUid, commentLanguage",
    description:
      "TikTok comments already beat SC on schema cleanliness, but were missing the three fields that make commenter identity and market listening work: authorId (uid), authorSecUid (sec_uid), and commentLanguage. Username alone is not a durable key. replyCount is included when TikTok exposes reply_comment_total. Lean schema kept — no 40-field user dumps.",
    items: [
      "authorId + authorSecUid on each comment",
      "commentLanguage (comment_language, else account language)",
      "replyCount when TikTok sends reply_comment_total",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Facebook comments: 10-type reactions + stable author.id",
    description:
      "Facebook comments were returning a single likeCount — useless for sentiment (anger vs love can share the same total). Each comment now includes reactionCount and reactions{like,love,care,haha,wow,sad,anger,thankful,pride,confused} from Facebook's top_reactions. author is an object with stable id (pfbid), name, shortName, gender when exposed; replyCount and hasMore are returned; optional feedbackId (from details) accepted as a faster alternative to url.",
    items: [
      "reactions{} 10-type breakdown + reactionCount",
      "author.id (pfbid) / gender / shortName",
      "Optional feedbackId param; hasMore on the response",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "improvement",
    title: "Instagram channel-reels: userId param + hasMore",
    description:
      "channel-reels now accepts optional userId (numeric Instagram ID) alongside url/@handle — skips the handle→ID resolve step when you already have the ID from basic-profile or another call. Response includes hasMore (boolean) with nextCursor so pagination loops don't have to infer end-of-list from a null cursor alone. No trim mode — Captapi responses stay lean by default.",
    items: [
      "Optional userId query param (faster path)",
      "hasMore boolean alongside nextCursor",
      "url remains optional when userId is set",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Instagram Trending Reels: flat 1 credit, /reels only",
    description:
      "Trending Reels was billed like a 28-credit Apify scrape and could surface Explore photos. It now scrapes instagram.com/reels (then /explore/reels) — never the Explore photo grid — returns videos only, and charges a flat 1 credit. Docs and response note that Instagram returns small overlapping batches; duplicates across calls are expected.",
    items: [
      "Flat 1 credit (was ~28 at limit=20)",
      "Source: /reels — Explore photos never returned",
      "Honesty note: duplicates across calls are expected",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Instagram reels-by-audio-id: trend signals + rich music",
    description:
      "reels-by-audio-id exists to answer “is this sound trending?” but returned only a reel list with a bare musicId. The response now includes top-level isTrendingInClips / trendRank / previousTrendRank and a music{} object (clusterId, assetId, canonicalId, title, artist, durationMs, audioType, isExplicit, hasLyrics, coverUrl). Each Reel can also carry hasAudio, coauthors[], and mashupInfo when Instagram exposes them.",
    items: [
      "Top-level isTrendingInClips + trendRank + music{}",
      "music.clusterId joins the /reels/audio/{id}/ URL",
      "Reel hasAudio, coauthors, mashupInfo (hasBeenMashedUp)",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Instagram Reels: split views into IG vs Facebook plays",
    description:
      "Instagram exposes three play metrics on Reels (play_count total, ig_play_count, fb_play_count) — Captapi was collapsing them into a single engagement.views, so Instagram-only analytics silently included Facebook cross-post plays (~20% on some Reels). Engagement now returns views (total), viewsInstagram, and viewsFacebook. Docs warn to use viewsInstagram for IG performance.",
    items: [
      "engagement.viewsInstagram + viewsFacebook on Reels when available",
      "views = total play_count (IG + Facebook)",
      "Docs note on channel-reels / channel-posts / details",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "TikTok Top Search: photo carousels, hashtag dedupe, cursor",
    description:
      "Top Search claimed mixed results but mapped only video-shaped rows with no contentType — photo carousels were indistinguishable. Mapper now sets mediaType/contentType (video|photo|multi_photo) and images[] for carousels. Hashtags no longer double-count Latinus+latinus (casefold dedupe, always hashtags:[]). Cursor pagination + within-page id dedupe; docs note TikTok can still repeat across pages.",
    items: [
      "contentType + images[] for photo carousels",
      "hashtags: lowercase-deduped, always an array",
      "cursor / nextCursor / hasMore on top-search",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "YouTube Shorts endpoints reject long-form videos",
    description:
      "Shorts Stats / Transcript / Summarizer / Comments were aliases of the main video endpoints with no Short check — the docs example was a 49-minute MrBeast watch URL. All four now verify Shorts (≤3 minutes / shorts-eligibility) and return HTTP 422 for long-form. Shorts Stats stamps isShort:true and a canonical youtube.com/shorts/{id} URL. Same schema as Video Details, honestly scoped.",
    items: [
      "shorts/*: 422 when duration > 180s (even under /shorts/{id})",
      "shorts/video-details: isShort:true + canonical Shorts URL",
      "Docs: no more watch?v= long-form example for Shorts Stats",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "improvement",
    title: "TikTok Trending Feed: publishedAt, rank, mediaType, saves, isAd",
    description:
      "Trending Feed now returns publishedAt + createTime (so you can tell fresh virals from weeks-old ones), keeps rank as a first-class For You position, renames title→caption to match other Captapi TikTok endpoints, and adds mediaType (video|photo), videoUrl, saves, isAd, authorId/secUid, and scrapedAt. Docs clarify flat 2 credits (not per-result) and that country is a region-availability hint — not “only creators from TR”.",
    items: [
      "publishedAt / createTime on every trending-feed item",
      "caption (not title); mediaType, videoUrl, saves, isAd",
      "authorId + secUid; country param honesty + lpFlat docs",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Facebook profile-posts: one author identity + honest shares",
    description:
      "Mixed post+Reel listings stamped a lowercased page slug onto Story authors (nasa) while Reels kept Facebook's URL casing (NASA). Listing feedback stubs also injected shares:0. Authors are now unified per response, engagement.views/shares stay present (null when unknown), unmatched zero share stubs are ignored, and scrapedAt is returned so profile-posts vs profile-reels counts can be compared by freshness.",
    items: [
      "Unify author.username casing across a profile-posts / profile-reels page",
      "Do not invent shares:0 from unmatched listing feedback",
      "engagement.views + shares always present; scrapedAt on the payload",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Instagram Trending Reels actually returns Reels",
    description:
      "Trending Reels was returning Explore photos/carousels (including 2018–2019 posts) because the native path padded with non-video cards and the Apify actor's mixed Explore dump was passed through unfiltered. Now both paths keep Video/clips only, drop posts older than ~180 days, prefer Explore Reels URLs, and expose numeric id + shortcode.",
    items: [
      "Filter Image/Sidecar out of trending-reels (channel-reels contract)",
      "Scrape explore/reels + reels before mixed explore/",
      "id = numeric media id when available; shortcode for URLs",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Instagram: never return likes > views on Reels",
    description:
      "GraphQL video_view_count undercounts many Reels and can sit below like_count (impossible). Channel Posts / Hashtag Search now prefer api/v1 play_count, drop untrustworthy views when likes > views, always expose engagement.views (null on Image/Sidecar), use null instead of empty productType, and dedupe caption @mentions. Facebook comments always include authorUrl (null when FB omits it).",
    items: [
      "IG channel-posts / hashtag-search: prefer play_count; sanitize likes>views",
      "engagement.views always present (null when N/A or untrusted)",
      "productType: null instead of \"\"; mentions[] deduped",
      "Facebook comments: authorUrl always on every comment object",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Stop inventing engagement zeros (IG/FB/YT/TikTok/Rumble)",
    description:
      "Missing like/comment/share/reply counts now stay null instead of becoming 0. Root cause: shared patterns like Instagram hidden_count(None)→0 and safe_int(...) or 0 across comments and post engagement. Also tightened YouTube hasCreatorHeart (emoji tooltips no longer force true) and stopped mapping Rumble engagementCount into likes. Kick likes:0 is Kick's own API returning zero — not invented. Prefer null over silent zeros so averages and engagement rates are not poisoned.",
    items: [
      "hidden_count: missing → null (not 0)",
      "IG/FB/YT/TikTok comments: drop or 0 on like/reply counts",
      "Facebook post engagement likes/comments: no invented zeros",
      "YouTube hasCreatorHeart: require real creator-heart signal",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Docs: profile use cases are enrichment, not influencer discovery",
    description:
      "API pages in the channel category (and Instagram Profile Search) no longer advertise \"Influencer Discovery — Find and vet creators by audience size.\" Those endpoints resolve or enrich a known handle/URL; they do not search niches. Use cases are now Profile Enrichment, Creator Verification, Competitive Analysis, and Partnership Qualification.",
    items: [
      "Replace Influencer Discovery template on channel endpoints",
      "Instagram Profile Search uses the same enrichment use cases",
      "Copy matches resolve/enrichment product scope",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Instagram profile search: id, bio, links — honest resolve mode",
    description:
      "GET /v1/instagram/profile-search now returns a CRM-ready resolved profile: numeric id, bio, bioLinks, externalUrl, categoryName, following/postCount, and business/professional flags — from the same web_profile_info path, still flat 1 credit. Docs clarify this is name→@handle resolve (mode=resolve), not niche discovery search like \"fitness coach\" creator lists.",
    items: [
      "Numeric id on users[] for stable CRM identity",
      "bio / bioLinks / externalUrl / categoryName / following / postCount",
      "isBusinessAccount / isProfessionalAccount",
      "mode=resolve — not multi-result niche search",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Facebook page details: distinct likes vs followers, talkingAbout",
    description:
      "GET /v1/facebook/page-details no longer copies likes into followers (they are different Facebook metrics). Parses exact likes from og:description, compact followers from page chrome (followersApproximate when K/M/B), and talkingAbout. Drops redundant name (kept displayName + fullName). Still returns category, website, and public email when exposed. Flat 2 credits.",
    items: [
      "likes and followers parsed separately (no copy)",
      "talkingAbout + followersApproximate for compact labels",
      "Drop duplicate name; keep displayName + fullName",
      "email / category / website unchanged",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Spotify search: full URIs, explicit/playable, scrapedAt",
    description:
      "GET /v1/spotify/search now returns canonical Spotify URIs (spotify:track:… etc.) so search hits chain into Track/Album/Artist/Podcast endpoints without prefixing bare IDs. Promotes explicit, playable, durationFormatted, and scrapedAt onto each result (no longer buried in raw). type=tracks|albums|artists|podcasts|episodes filter kept. Flat 2 credits native.",
    items: [
      "uri always spotify:{type}:{id} (Search ↔ Track parity)",
      "explicit / playable / durationFormatted on results",
      "scrapedAt per result (Apify sequential stamps preserved)",
      "raw dropped for track hits (same as Track details)",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Twitch user videos: filterBy, sortBy, cursor, broadcaster object",
    description:
      "GET /v1/twitch/user-videos now supports filterBy=ARCHIVE|HIGHLIGHT|UPLOAD, sortBy=TIME|VIEWS, limit up to 100, and cursor pagination (nextCursor/hasMore) over the first 100 matches. Response adds top-level broadcaster{id,username,displayName,followers,profileImage,isPartner}, plus per-video broadcastType, gameId/gameSlug, animatedPreviewUrl, and channel{}. Still a clean videos[] list (not a profile dump). Flat 2 credits native.",
    items: [
      "filterBy ARCHIVE / HIGHLIGHT / UPLOAD",
      "sortBy TIME | VIEWS; limit max 100",
      "cursor pagination (offset into first 100)",
      "broadcaster id + followers; broadcastType on each video",
    ],
  },
  {
    publishedAt: "2026-08-03",
    category: "fix",
    title: "Reddit search: sort + timeframe, scores, authorFullname",
    description:
      "GET /v1/reddit/search and /subreddit-search now accept sort=relevance|new|top|hot|comments (alias comment_count) and timeframe=hour|day|week|month|year|all (default all for top/comments). Results already expose authorFullname (t2_…), name (t3_…), score/downs/upvoteRatio, subscriberCount, totalAwardsReceived, and isVideo — docs/examples refreshed. publishedAt normalized to ISO …Z across Reddit. Still 2 credits.",
    items: [
      "sort + timeframe (e.g. top&timeframe=week, or new)",
      "authorFullname / score / upvoteRatio / subscriberCount in examples",
      "Same controls on subreddit-search",
      "ISO publishedAt …Z consistency",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "fix",
    title: "Facebook profile reels: drop archive padding after recency cliff",
    description:
      "GET /v1/facebook/profile-reels no longer pads \"latest\" with years-old videos pulled from a deep /videos scroll or the profile home feed. Listing prefers /reels (falls back to /videos) with a shallower scroll; after newest-first sort, the first gap larger than 1 year truncates the page. Engagement (views/likes/comments/shares) unchanged. Still 2 credits.",
    items: [
      "Prefer /reels tab before /videos",
      "Shallower listing scroll (less archive pollution)",
      "Recency cliff: stop at >1 year gap between items",
      "Home feed mined only when both tabs are empty",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "fix",
    title: "TikTok live: authoritative isLive/status + parsed stream qualities",
    description:
      "GET /v1/tiktok/live (and /live-info) no longer treat a leftover roomId or non-empty streamUrls as live. isLive is true only when liveRoom.status === 2; that numeric status is also returned at the top level and on room. Offline responses can still include the last room (title, counts, pull URLs) — trust isLive/status. Additive fields: creator.id / secUid / following, room.liveSubOnly / gameTagId / hashTagId / streamId, streamQualities[{quality,codec,resolution,bitrate,flv,hls,dash}], and streams{hd,sd,ld,origin,ao,…} (h264 preferred). streamUrls[] kept for compatibility. Still 1 credit on /live.",
    items: [
      "isLive only when status === 2 (room may still be last broadcast)",
      "creator.id + secUid + following",
      "streamQualities[] + streams{} with resolution/bitrate/codec",
      "liveSubOnly / gameTagId / hashTagId when present",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "fix",
    title: "Instagram basic profile: camelCase schema aligned with Channel Details",
    description:
      "GET /v1/instagram/basic-profile no longer returns raw Instagram snake_case (full_name, follower_count, is_private, hd_profile_pic_url_info). Response is Captapi camelCase matching Channel Details: displayName, bio, followers / following / postCount, verified, isPrivate, profileImage / profileImageHd, externalUrl, bioLinks[], categoryName, isBusinessAccount / isProfessionalAccount, businessAddress{cityName,streetAddress,zipCode,…}, fbid, highlightReelCount, hasClips, and transparency flags when present. Still 1 credit.",
    items: [
      "camelCase fields (displayName, followers, verified, …)",
      "externalUrl + bioLinks[] parity with Channel Details",
      "businessAddress includes streetAddress",
      "categoryName from category_name / category_enum",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "fix",
    title: "TikTok song details: usageCount, artists, commerce, chorus; 1 credit",
    description:
      "GET /v1/tiktok/song-details now returns the fields the docs already promised: usageCount (videos using the sound; null when TikTok omits a real total on music/aweme), artists[{id,uid,secUid,handle,displayName,verified,avatarUrl}] (owner lifted for original sounds), commerce rights (isCommerceMusic / hasCommerceRight / commercialRightType), createdAt, matchedSong.chorusInfo{startMs,durationMs}, musicReleaseInfo, and extra{loudnessLufs,amplitudePeak,beats,bpm} when present. Flat 1 credit on the native path (was 2); Apify fallback stays 2.",
    items: [
      "usageCount field (docs parity; null when TikTok sends 0/absent)",
      "artists[] with id/secUid/handle; commerce + chorus timing",
      "musicReleaseInfo + audio analysis extra{}",
      "1 credit native (was 2)",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "fix",
    title: "YouTube community posts: numeric likes, ISO dates, channel/video, cursor",
    description:
      "GET /v1/youtube/community-posts no longer returns likeCount as a display string (\"3M\") or publishedTime as a relative label only. likeCount is a number with likeCountText kept for display (likeCountApproximate when YouTube only shows K/M/B); publishedTime is ISO-8601 (approximate from relative labels) with publishedTimeText preserved. Each post adds channel{id,title,url,handle}, url/image, and when linked — video{id,title,thumbnail,url,viewCountText,viewCountInt,lengthText,lengthSeconds} plus enriched linkedVideos[]. Cursor pagination via nextCursor + hasMore. Flat 1 credit on the native /posts path; Apify fallback stays ~0.5/result.",
    items: [
      "likeCount number + likeCountText; ISO publishedTime + publishedTimeText",
      "channel{id,title,url,handle}; video{} / linkedVideos when attached",
      "nextCursor + hasMore pagination",
      "1 credit native (was ~10 at limit=20)",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "fix",
    title: "YouTube playlist: ISO publishedAt, video id, owner, totalVideos",
    description:
      "GET /v1/youtube/playlist and /playlist-videos no longer return relative labels like \"1 year ago\" in publishedAt. publishedAt is ISO-8601 (approximate when derived from YouTube's relative card text); the original label is kept as publishedTimeText. Each video now includes id. Playlist responses add owner{id,name,url,handle}, totalVideos (full playlist size vs totalReturned page length), and viewCountApproximate when viewCount comes from compact 2.5B-style UI text. Still flat 2 credits on the native path; fast=true RSS kept for exact dates / speed.",
    items: [
      "publishedAt ISO (approx from relative); publishedTimeText kept",
      "videos[].id on playlist + playlist-videos",
      "owner{id,name,url,handle} + totalVideos",
      "viewCountApproximate for compact K/M/B counts",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Instagram Reels Search: flat 2 credits, schema parity with hashtag",
    description:
      "GET /v1/instagram/reels-search drops from ~12 credits (0.6/result) to flat 2 — same native hashtag-grid path as /hashtag-search?mediaType=reels, including author-feed view backfill. Results now match hashtag-search shape: author.verified / profileImage / followers / postCount, engagement.views plus engagement.plays when Instagram exposes both (view_count ≠ play_count), music{}, location{}, isPaidPartnership / isAd / isAffiliate, and optional datePosted (last_24_hours|last_week|last_month|last_year). Note on the hashtag likes hypothesis: when both metrics exist, likes sit well below views (~12% on the sample viral reel) — likes are not mislabeled views; missing views was an enrich shortcode mismatch, now fixed.",
    items: [
      "Flat 2 credits (was ~0.6 × results)",
      "author.verified / profileImage / followers parity with hashtag-search",
      "engagement.views + plays when Instagram distinguishes them",
      "datePosted filter; enrich shortcode match fix for views backfill",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "fix",
    title: "Facebook group posts: real author IDs, sortBy, null shares",
    description:
      "GET /v1/facebook/group-posts no longer stamps the group slug into author.username (every post was \"dogspotting\"). Returns author.id when Facebook exposes it, permalink, optional topComments/videoDetails/videoViewCount, and sortBy (TOP_POSTS | RECENT_ACTIVITY | CHRONOLOGICAL | CHRONOLOGICAL_LISTINGS; default CHRONOLOGICAL via Facebook sorting_setting). engagement.shares stays null when unknown instead of inventing 0. Still flat 2 credits; limit up to 200.",
    items: [
      "Fix author.username = group slug bug",
      "author.id + permalink; shares null when unknown",
      "sortBy feed modes (default CHRONOLOGICAL)",
      "topComments / videoDetails when present in feed HTML",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Instagram tagged posts: cursor, author id, views; 1 credit native",
    description:
      "GET /v1/instagram/tagged-posts adds nextCursor + hasMore (channel-posts shape), author.id on each tagging creator, engagement.views/plays when Instagram exposes them on video tags, and newest-first sorting within a page. Native usertags path bills a flat 1 credit; Apify fallback stays ~0.9/result. Docs note that Instagram itself truncates the tagged feed for some mega brands (natgeo stuck in 2018) while accounts like nasa/cristiano return recent UGC — verified live.",
    items: [
      "nextCursor + hasMore pagination",
      "author.id + engagement.views when present",
      "Newest-first sort within each page",
      "1 credit native (was ~18 at limit=20)",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "TikTok search users: id, secUid, following; 1 credit native",
    description:
      "GET /v1/tiktok/search/users lifts uid/sec_uid out of the search payload as id + secUid (stable identity for CRM joins and chaining into follower/video lists), plus following, videos, likes, and slim items[] sample videos when TikTok includes them. Native signer path bills a flat 1 credit (ScrapeCreators parity); Apify fallback stays ~0.4/result.",
    items: [
      "id + secUid on each user",
      "following / videos / likes",
      "items[] sample videos when present",
      "1 credit native (was ~8 at limit=20)",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Spotify podcast: publisher, rating, topics; 1 credit",
    description:
      "GET /v1/spotify/podcast drops to 1 credit and lifts Pathfinder show fields into a stable top-level shape: publisher{name} (not artists[] — publisher ≠ hosts), rating{average, totalRatings}, topics[{title, uri}], contentRating/explicit, mediaType, htmlDescription, playable, consumptionOrder, plus totalEpisodes. Drops the bulky raw payload (including Spotify's visualIdentity color dump).",
    items: [
      "1 credit (was 2)",
      "rating.average + rating.totalRatings",
      "publisher{} instead of mislabeled artists[]",
      "topics + contentRating/explicit; no visualIdentity",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Spotify track: playCount, artist/album IDs; 1 credit",
    description:
      "GET /v1/spotify/track drops to 1 credit and switches to Spotify's getTrack Pathfinder query. Returns playCount (stream count), trackNumber, contentRating/explicit, artistItems[{id,uri,name,url}], albumInfo[{id,uri,name,url,releaseDate}], and previewUrl when present on the payload. Flat artists[] / album name strings kept for back-compat. Drops the bulky raw discography dump that buried those IDs.",
    items: [
      "1 credit (was 2)",
      "playCount, trackNumber, contentRating/explicit",
      "artistItems + albumInfo with chainable IDs",
      "Drop bulky raw track payload",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Twitch clip: curator vs channel, qualities, token expiry",
    description:
      "GET /v1/twitch/clip stays 1 credit and now returns a fully normalized clip — not Twitch's GraphQL array envelope. Adds curator (clipper) separate from channel (broadcaster id/followers/isPartner/lastBroadcast), language, isFeatured/isPublished, videoOffsetSeconds, gameId/slug/box art, videoQualities[{quality,frameRate,url}], and playbackAccessToken.expires/expiresAt. Flat broadcaster string kept for back-compat.",
    items: [
      "curator vs channel (clipper ≠ broadcaster)",
      "channel.followers / isPartner / lastBroadcast",
      "videoQualities + playbackAccessToken.expires",
      "language, isFeatured, isPublished, videoOffsetSeconds",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "SoundCloud artist: badges, creator subscription, lastModified",
    description:
      "GET /v1/soundcloud/artist now surfaces SoundCloud's paid-tier signals: badges {pro, creatorMidTier, proUnlimited, verified}, creatorSubscription.product.id (e.g. creator-pro-unlimited), and lastModified — so Pro Unlimited accounts are distinguishable from hobby profiles. Still 1 credit.",
    items: [
      "badges.pro / creatorMidTier / proUnlimited / verified",
      "creatorSubscription.product.id",
      "lastModified",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Kick clip: creator vs channel, VOD/maturity fields; 1 credit",
    description:
      "GET /v1/kick/clip drops to 1 credit on the native path and stops duplicating the same object as clip and clips[0]. Clip URLs hit Kick's single-clip API and return { channelUrl, clip } with creator (clipper) separate from channel (broadcaster), plus privacy, isMature, startedAt, vod.id, livestreamId, vodStartsAt, categorySlug/parentCategory/categoryBanner, and channel/creator ids + profile pictures. Channel URLs return { channelUrl, totalReturned, clips } only.",
    items: [
      "1 credit native (was 2)",
      "creator vs channel (clipper ≠ broadcaster)",
      "privacy, isMature, startedAt, vod, livestreamId",
      "No more clip + clips[0] duplicate payload",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Kwai profile: bio, verification, post counts; 1 credit",
    description:
      "GET /v1/kwai/profile drops from 17 → 1 credit and finally matches its own docs promise: bio, verified/verifiedDescription/verifiedNumber, gender, following, publicPostCount/privatePostCount, isPrivate, and eid — parsed from Kwai JSON-LD + Nuxt SSR state. Removes the duplicate raw block. When Kwai stubs follower/following to 1, followers prefer schema.org counts and following is omitted instead of a fake 1.",
    items: [
      "1 credit (was 17)",
      "bio, verified, verifiedDescription, verifiedNumber, gender, eid",
      "following, publicPostCount, privatePostCount, isPrivate",
      "Drop duplicate raw profile block",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Account APIs: camelCase field names",
    description:
      "GET /v1/account/balance (and sibling usage/history/daily-usage/most-used-routes/limits) now use camelCase keys — monthlyQuota, subscriptionCredits, topupCredits, totalCredits, subscriptionRenewsAt, creditsUsed, createdAt, etc. — matching the rest of the Captapi surface. Same data; naming only.",
    items: [
      "balance: monthlyQuota, subscriptionCredits, topupCredits, totalCredits, subscriptionRenewsAt",
      "usage/history/routes: creditsUsed, cacheHit, statusCode, createdAt, …",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Truth Social profile: bot/isPrivate flags, static media, 1 credit",
    description:
      "GET /v1/truth-social/profile drops from 5 → 1 credit and adds bot, isPrivate (locked), group, discoverable, location, avatarStatic/headerStatic, emojis[], plus acceptingMessages/chatsOnboarded/tvAccount when present. Bio stays HTML-stripped. Docs warn that as of late 2025 Truth Social typically only exposes public profiles for prominent accounts without login — auth-gated accounts return a clear 404. Native lookup retries via Decodo when datacenter IPs hit Cloudflare.",
    items: [
      "1 credit (was 5)",
      "bot, isPrivate, group, location, avatarStatic/headerStatic, emojis",
      "Docs + 404 copy for auth-gated / non-prominent accounts",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Amazon seller storefront: badges, scrapedAt, pagination; drop raw leak",
    description:
      "GET /v1/amazon-shop/page now returns seller name, scrapedAt, stable product shapes (price/currency/priceFormatted always present), isPrime/isBestSeller/isSponsored, canonical /dp/{ASIN} URLs, display priceFormatted ($1,234.56), and cursor pagination (nextCursor/hasMore). Removes rawFirstItem leakage. Docs clarify scope: seller storefronts (/sp?seller=), not influencer /shop/<handle> vitrines. Influencer shop URLs return 400 with a clear message. List price aligned to 1 credit per ~16-product page.",
    items: [
      "scrapedAt + isPrime/isBestSeller/isSponsored on products",
      "seller.name, canonical /dp URLs, stable price fields, cursor pagination",
      "Removed rawFirstItem; scope note vs influencer /shop/",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Linktree page: email, GROUP children, verticals, 1 credit",
    description:
      "GET /v1/linktree/page drops from 4 → 1 credit. Returns email when the creator publishes a mailto social, plus verticals and linkPlatforms. GROUP folders now nest child links under links[] (parentId on nested rows); typed links (SPOTIFY_*, SOUNDCLOUD_*, …) kept. socialAccounts includes soundcloud; socials remains the icon list. Browser-like fetch headers avoid Linktree 403s on datacenter UAs.",
    items: [
      "1 credit (was 4)",
      "email + verticals + linkPlatforms",
      "GROUP.links nesting + parentId; soundcloud in socialAccounts",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Snapchat profile: full snap lists, Spotlight, 1 credit",
    description:
      "GET /v1/snapchat/user-profile drops from 11 → 1 credit (native __NEXT_DATA__). Highlights now include snapList[] (mediaUrl + timestamp per snap), plus spotlightHighlights with engagement/views/shares/comments and video metadata. Adds createdAt/creationTimestampMs, businessProfileId, squareHeroImageUrl, badge, human-readable category (keeps categoryId), story snaps, and richer relatedAccounts. subscriberCount stays numeric.",
    items: [
      "1 credit (was 11); native HTML profile",
      "highlight snapList[] + Spotlight engagement/metadata",
      "createdAt, businessProfileId, hero image, readable category",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Reddit subreddit posts: sort, timeframe, score & author id",
    description:
      "GET /v1/reddit/subreddit-posts adds sort (best/hot/new/top/rising) and timeframe for top feeds, plus score/downs/upvoteRatio, authorFullname, subscriberCount, isVideo, totalAwardsReceived, and Reddit name (t3_…). Keeps flair/nsfw/thumbnail/text, ISO publishedAt, and nextCursor/hasMore. Flat 2 credits. Also normalizes subreddit-details createdAt to ISO.",
    items: [
      "sort + timeframe (top/controversial) query params",
      "score, downs, upvoteRatio, authorFullname, subscriberCount, isVideo",
      "ISO createdAt on subreddit-details",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Facebook Marketplace search: filters, priceAmount, status flags",
    description:
      "GET /v1/facebook/marketplace-search keeps city-name location (no lat/lng) and createdAt, and now accepts Marketplace filters (minPrice/maxPrice, sortBy, daysSinceListed, condition, deliveryMethod, availability, radiusMiles, category). Listings add priceAmount (minor units), strikethroughPrice*, categoryId, isPending/isHidden/isViewerSeller, plus hasMore/nextCursor within the fetched page. Docs clarified: details=false already includes the cover photo; details=true adds description/condition/coordinates/full gallery (2 + 2 credits per listing).",
    items: [
      "Price/sort/condition/delivery/availability/radius/category filters",
      "priceAmount + strikethrough + categoryId + pending/hidden flags",
      "hasMore/nextCursor; details=true docs fixed vs cover photos",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "improvement",
    title: "Instagram hashtag search: views, paid flags, creator size, audio",
    description:
      "GET /v1/instagram/hashtag-search stays on Instagram's native hashtag grid (not Google index) and now returns campaign-ready fields: engagement.views (backfilled from the creator feed when Polaris hides play counts), author.followers / author.postCount, isPaidPartnership / isAd / isAffiliate, music{id,title,artist} + musicId, location, accessibilityCaption, and previewComments. Optional mediaType=all|reels. Still flat 2 credits. Live check: engagement.likes matches Apify likesCount (not mislabeled views).",
    items: [
      "engagement.views + author.followers / postCount on hashtag hits",
      "isPaidPartnership / isAd / isAffiliate, music, location, previewComments",
      "mediaType=reels filter",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "fix",
    title: "TikTok Shop search: rating/reviews + HTML entity decode",
    description:
      "GET /v1/tiktok-shop/shop-search now returns rating and reviews when TikTok exposes them (native PDP hydrate / rate_info). Also fixes systematic HTML-entity leakage in API strings — titles and URLs no longer contain literal &amp; (safe_str now runs html.unescape). Keeps originalPrice/discount and seller.id.",
    items: [
      "rating + reviews on shop search hits",
      "Decode &amp; / &#x…; in titles, URLs, and other safe_str fields",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "feature",
    title: "Twitter/X profile: verification triad, listed/media/likes",
    description:
      "GET /v1/twitter/profile now uses guest GraphQL UserByScreenName for rich public fields: verified + isBlueVerified + isIdentityVerified, verification{verifiedType, reason, verifiedSince}, affiliate{} when present, listedCount/mediaCount/likesCount, pinnedTweetIds, bannerImage, profileImageShape, bioUrls[], highlightedTweets, and related signals. createdAt stays ISO-8601. Still 1 credit; HTML microdata remains the fallback.",
    items: [
      "Blue check / identity / affiliate verification fields",
      "listedCount, mediaCount, likesCount, pinnedTweetIds",
      "bannerImage, bioUrls, highlightedTweets",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "fix",
    title: "Rumble video details: real likes/comments, media, captions",
    description:
      "GET /v1/rumble/video-details no longer invents likes/dislikes/comments/views as 0 when Rumble does not expose them (null = unknown). Adds durationSeconds, numericId/embedId/shareUrl, channelHandle, width/height, captions{} (.vtt paths), and media{mp4|tar,timeline,audio,hls}. Keeps channelFollowers + channelVerified. Still 1 credit.",
    items: [
      "Null instead of fake zero engagement",
      "durationSeconds + captions{} + media qualities",
      "numericId, embedId, shareUrl, channelHandle",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "feature",
    title: "YouTube search: cursor pagination, ids, filters",
    description:
      "GET /v1/youtube/search is now cursor-paginated (nextCursor + hasMore), returns typed hits with stable id + canonical URL (no radio/mix query junk), channelId/channel{handle}, badges[], and additive videos/shorts/channels/playlists partitions. New filters: type, sortBy, uploadDate, duration, region. Flat 2 credits per page; cache=true supported.",
    items: [
      "nextCursor / hasMore pagination",
      "type + id + canonical url + channelId",
      "Filters: type, sortBy, uploadDate, duration, region",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "feature",
    title: "LinkedIn Ad Library search: targeting, dates, pagination",
    description:
      "GET /v1/ad-library/linkedin/search-ads now returns LinkedIn transparency fields — targeting{}, ISO startDate/endDate + adDuration, totalImpressions + impressionsByCountry[], cta/destinationUrl, headline/description, advertiser id/URL, and carouselImages[] — plus cursor pagination (paginationToken/nextCursor, totalAds, isLastPage) and filters (countries, startDate/endDate, companyId, keyword). Still flat 2 credits on the native path.",
    items: [
      "Additive targeting{}, dates, impressions, CTA/destination",
      "Cursor pagination + totalAds",
      "Filters: countries, date range, companyId, keyword",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "feature",
    title: "Bluesky profile: verification, labels, associated",
    description:
      "GET /v1/bluesky/profile now surfaces AT Protocol fields already on app.bsky.actor.getProfile: verified + verification{verifications[], verifiedStatus, trustedVerifierStatus}, moderation labels[], and associated{lists, feedgens, starterPacks, labeler} (plus chat/activitySubscription when present). Still 1 credit; existing keys unchanged.",
    items: [
      "Additive verified + verification{}",
      "Additive labels[] and associated{}",
      "Docs match What you get (verification status)",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "feature",
    title: "TikTok Creative Center Top Ads: 2 credits native",
    description:
      "GET /v1/ad-library/tiktok/top-ads now prefers a Decodo-native Creative Center path (XHR capture of creative_radar top_ads/v2/list) at a flat 2 credits. Apify remains the fallback at ~1 credit per returned ad (min 2). Response shape unchanged.",
    items: [
      "Native-first Decodo XHR path for Top Ads",
      "Price: flat 2 credits native (Apify ~1/ad min 2)",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "feature",
    title: "TikTok Creative Center Top Ads endpoint",
    description:
      "New GET /v1/ad-library/tiktok/top-ads returns Creative Center Top Ads as clean JSON — likes, ctr/ctrTier, costTier, industry/objective, isSparkAd, and video{url,urlHd,cover}. Filters: country (default US), period (7/30/180), orderBy (for_you|likes|ctr|impressions|cost), optional q/industry/objective/adFormat. Separate from EU Commercial Content Library search.",
    items: [
      "New /v1/ad-library/tiktok/top-ads",
      "Performance metrics: ctr, ctrTier, likes, costTier, Spark flag",
      "orderBy / period / industry / objective filters",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "feature",
    title: "TikTok Ad Library search: 2 credits native, ISO dates, GB default",
    description:
      "TikTok Ad Library search drops the ~70-credit Apify-first pricing to flat 2 credits on the Decodo-native Commercial Content Library path (Apify fallback capped at 5). firstShown/lastShown become ISO-8601, impressionsRange parses reach bands like 0-1K, and advertiser.location is added when present. Default country is GB (EU DSA library; US is often empty). Docs clarify this is not Creative Center — CTR/order_by metrics live on a different TikTok surface.",
    items: [
      "Price: ~70 → 2 credits native (Apify fallback ≤5)",
      "ISO dates + impressionsRange + advertiser.location",
      "Default country DE → GB; honesty note vs Creative Center",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "feature",
    title: "Twitch profile: game box art + animated video previews",
    description:
      "Twitch profile keeps game as the category name string and adds gameBoxArtUrl on stream, lastBroadcast, and recentVideos, plus animatedPreviewUrl (storyboard strip) on each VOD. Still 1 credit; no GraphQL leftover fields.",
    items: [
      "Additive gameBoxArtUrl on stream / lastBroadcast / recentVideos",
      "Additive animatedPreviewUrl on recentVideos",
      "game name string unchanged (non-breaking)",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "feature",
    title: "Threads profile: private, bioLinks, transparency, HD avatars",
    description:
      "Threads profile keeps id/username/name/bio/followers/verified/profileImage and adds isThreadsOnlyUser, isPrivate, bioLinks[], transparencyLabel, profileImageVersions[], and hasOnboarded. Still 1 credit. isThreadsOnlyUser is null when Meta's web hydrate omits it (common); following/post counts remain unavailable on this public surface.",
    items: [
      "Additive isThreadsOnlyUser, isPrivate, bioLinks, transparencyLabel",
      "Additive profileImageVersions[] and hasOnboarded",
      "Docs note: following/posts not on public Threads profile surface",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "feature",
    title: "Spotify artist: topCities, worldRank, topTracks, 1 credit",
    description:
      "Spotify artist lifts the valuable GraphQL fields out of raw into a stable top-level shape: worldRank, topCities[], externalLinks[], verified, topTracks[] (with playCount), concerts[], relatedArtists[], and albums/singles (+ counts). Price drops 2 → 1 credit (ScrapeCreators parity). Docs note that monthlyListeners / topCities / worldRank are not on Spotify's public Web API — this endpoint's GraphQL path is the real value. raw remains for advanced use.",
    items: [
      "Price: 2 → 1 credit",
      "Additive worldRank, topCities, externalLinks, verified, topTracks, concerts, relatedArtists, albums/singles",
      "Honesty note: GraphQL-only metrics vs Spotify Web API",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "feature",
    title: "GitHub user: email + parity fields, 1 credit, free-API note",
    description:
      "GitHub user drops from 3 credits to 1 (matching ScrapeCreators) and adds email (when public), nodeId, apiUrl, hireable, and siteAdmin. type is now user or organization. Docs note that this wraps GitHub's free public REST API — use Captapi for one-key workflows; call api.github.com directly for GitHub-only jobs.",
    items: [
      "Price: 3 → 1 credit",
      "Additive email, nodeId, apiUrl, hireable, siteAdmin",
      "Honesty note: free GitHub API alternative for GitHub-only workloads",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "fix",
    title: "Compare analytics: real unified metrics example + cache param",
    description:
      "Compare analytics docs no longer show placeholder example.com rows. The live example returns count/resolved/results[] with the same metrics object as post analytics (views, likes, comments, engagementRate, …). Adds cache=true (per-URL cache shared with /post; hits free) and honest billing copy — 1 credit per resolved URL, no bulk discount.",
    items: [
      "Live snapshot example with two real YouTube URLs and full metrics{}",
      "Additive cache param (shared with /v1/analytics/post)",
      "Docs/FAQ: same shape as post analytics; no bulk credit discount",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "feature",
    title: "Pinterest pin-details: title, link, createdAt, originAuthor, images",
    description:
      "Pinterest pin-details keeps board{}, author{}, image, and saves, and adds the fields needed for commerce and creator intel: title/description/seoAltText, link/destinationUrl, ISO createdAt, originAuthor vs author (pinner), repinCount/shareCount/reactionCount, and images{} including originals.",
    items: [
      "Additive title, description, seoAltText, link/destinationUrl, domain",
      "Additive createdAt/publishedAt (ISO-8601 from pin page)",
      "Additive originAuthor + images{236x,564x,originals} + repin/share/reaction counts",
    ],
  },
  {
    publishedAt: "2026-08-02",
    category: "fix",
    title: "Post analytics: YouTube likes, comments, publishedAt, engagementRate",
    description:
      "Cross-platform post analytics now uses the same enriched YouTube path as video-details, so likes, comments, publishedAt, and engagementRate populate instead of staying null when views alone were present. author.username prefers the channel handle; shares/saves remain null on YouTube (not publicly exposed).",
    items: [
      "YouTube analytics reuses enriched video-details (likes/comments/publishedAt)",
      "author.username ← channelHandle when available; displayName stays channel name",
      "Docs/FAQ: same metrics shape; platform-missing fields stay null",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "feature",
    title: "Google company-ads: cursor paging, date filters, adsCountEstimate",
    description:
      "Google Ads Transparency company-ads keeps the 2-credit media[] response, and adds cursor pagination (nextCursor/hasMore), adsCountEstimate, region alias, and start_date/end_date overlap filters. Docs note public commercial creatives only — login-gated and political ads are out of scope.",
    items: [
      "Additive hasMore / nextCursor / adsCountEstimate",
      "New params: cursor, region, start_date, end_date (topic=all only)",
      "Honesty note: public ATC creatives only; shapes can vary",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "feature",
    title: "Richer Facebook details: author id, SD/HD, captions, music (non-breaking)",
    description:
      "Facebook details keeps every existing field (videoUrl, author.username, engagement), and adds stable author.id, feedbackId, captionsUrl, videoSdUrl/videoHdUrl, video dimensions, nested video{}, and music when Facebook exposes them. Docs note that some Reel view counts on the post page can lag the public Reels grid badge.",
    items: [
      "Additive author.id + feedbackId",
      "Additive captionsUrl, videoSdUrl/videoHdUrl, videoWidth/videoHeight, video{}, music{}",
      "Docs warning for Reel view-count badge mismatch vs profile Reels grid",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "feature",
    title: "YouTube channel-details: email + SEO tags (non-breaking)",
    description:
      "YouTube channel-details keeps every existing numeric/stats field, and adds email (from About/description when publicly exposed) and tags[] from channel SEO keywords. CAPTCHA-gated business emails stay null.",
    items: [
      "Additive email when present in channel About/description or mailto links",
      "Additive tags[] from channelMetadataRenderer keywords (list, not a comma string)",
      "Existing subscriberCount/videoCount/viewCount numbers, handle, verified, links unchanged",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "fix",
    title: "LinkedIn profile: stop treating SEO meta as About",
    description:
      "LinkedIn profile no longer copies og:description into about, and no longer invents connections/currentCompany from that SEO trailer (the Bill Gates “8 connections” bug). about prefers JSON-LD Person description and is omitted when only SEO meta is available; connections matching the privacy/SEO placeholder are null.",
    items: [
      "about from JSON-LD only — SEO meta (and its leading mash) never returned as about",
      "connections matching “N connections on LinkedIn” SEO chrome → null",
      "Additive experience[] / education[] when the Apify fallback returns them",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "fix",
    title: "Reddit comments: real ISO publishedAt + post context",
    description:
      "Reddit post-comments publishedAt is now ISO 8601 (was a stringified unix float like \"1785330725.0\", which broke Date parsers). Existing flat comments + depth/parentId stay; response adds post, score/downs, authorFullname, and hasMore.",
    items: [
      "publishedAt is ISO 8601 UTC",
      "Additive score, downs, authorFullname, distinguished, controversiality",
      "post object + hasMore/nextCursor (cursor paging still deferred)",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "feature",
    title: "Richer TikTok Shop product-details (non-breaking)",
    description:
      "TikTok Shop product-details keeps price as a float + currency, and now returns seller id/url, originalPrice/discount, description, skus[], and optional region for the Apify path. Related affiliate videos remain best-effort when upstream provides them.",
    items: [
      "seller.id / seller.url restored (were stripped in details mode)",
      "originalPrice, discount, description, skus[], images[], region param",
      "Native path still bills 2 credits; Apify fallback remains 14",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "feature",
    title: "Facebook Ad Library search: filters + richer ads (non-breaking)",
    description:
      "Facebook Ad Library search keeps every existing ad field your integrations already parse (including media[] and string spend/impressions), and adds the filters and structured fields needed for competitor intel. Default status is ACTIVE so results match what advertisers are running now.",
    items: [
      "New filters: status, media_type, ad_type, search_type, sort_by, start_date, end_date (max limit 200 documented)",
      "Additive ad fields: isActive, publisherPlatforms, cards[], images[], videos[], spendRange/impressionsRange, pageLikeCount, disclaimer/byline, fetchedAt",
      "searchResultsCount / hasMore / nextCursor on the response (cursor paging deferred); docs note spend/impressions are usually political/issue-only",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "feature",
    title: "Richer TikTok channel-details (non-breaking)",
    description:
      "TikTok channel-details keeps every existing field your integrations already parse, and adds stable IDs, account age, commerce/seller flags, and bio-link risk for vetting and joins. category, private, and exact follower counts are unchanged.",
    items: [
      "New id and secUid for stable TikTok identity and chaining",
      "createTime, uniqueIdModifyTime, nickNameModifyTime for account-age and takeover signals",
      "isCommerceUser, isSeller, isOrganization, isAdVirtual, bioLinkRisk, friendCount/diggCount, avatar sizes, privacy settings, fetchedAt",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "improvement",
    title: "Transcript source in the JSON body (non-breaking)",
    description:
      "YouTube and TikTok transcript responses now include source in the body so RAG and analytics can weight caption quality vs Whisper. Existing transcript, transcriptSegments, wordCount, segments, and language fields are unchanged. YouTube also adds isAutoGenerated, isTranslated, and availableLanguages when captions are used.",
    items: [
      'source: "captions" | "whisper" (TikTok) | "fallback" (YouTube secondary path)',
      "YouTube: isAutoGenerated, isTranslated, availableLanguages[]",
      "No rename of segment fields; float seconds and ISO language codes unchanged",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "feature",
    title: "Richer Instagram channel-details (non-breaking)",
    description:
      "Instagram channel-details keeps every existing field your integrations already parse, and adds the IDs and account flags needed for joins, outreach, and private-account detection. externalUrl and profileImage are unchanged; bioLinks and profileImageHd are additive.",
    items: [
      "New id and fbid for stable Instagram user identity",
      "isPrivate, isBusinessAccount, isProfessionalAccount, categoryName",
      "bioLinks[], profileImageHd, businessAddress when present, plus fetchedAt",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "improvement",
    title: "YouTube comments: author channel ID, publishedTime, heart fix",
    description:
      "YouTube comments responses now include authorChannelId and publishedTime (ISO when InnerTube provides it) alongside the existing author string and publishedTimeText. hasCreatorHeart no longer false-positives on inactive heart tooltips. Billing stays a flat 2 credits per call.",
    items: [
      "authorChannelId for stable commenter joins",
      "publishedTime ISO when available; publishedTimeText unchanged",
      "hasCreatorHeart only true when the creator actually hearted the comment",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "feature",
    title: "Richer YouTube and TikTok video-details responses",
    description:
      "YouTube and TikTok video-details now return the fields teams need for joins, media pipelines, and filtering — without dumping a raw platform blob. Existing keys are unchanged; new fields are additive.",
    items: [
      "YouTube: channelHandle, contentType/isShort, liveStatus, availableCaptions[], thumbnails[], descriptionLinks[], language and access flags, fetchedAt",
      "TikTok: authorId/secUid, musicId/musicAuthor/isOriginalSound, mediaType, videoUrl/downloadUrl/downloadUrlNoWatermark, mentions[], status flags, isAd/isCommerce, region/width/height, mediaUrlsExpireAt, fetchedAt",
      "TikTok engagement.isApproximate marks rounded legacy counters vs exact statsV2 counts",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "improvement",
    title: "Billing metadata in every successful JSON response",
    description:
      "Successful API responses now include cached, creditsUsed, requestId, fetchedAt, and cachedAt in the JSON body (in addition to the existing x-captapi-* headers). Use fetchedAt for time-series snapshots and requestId when contacting support.",
    items: [
      "Body fields: cached, creditsUsed, requestId, fetchedAt, cachedAt",
      "New response header: x-captapi-request-id",
      "cachedAt is set when the response was served from cache; otherwise null",
    ],
  },
  {
    publishedAt: "2026-08-01",
    category: "platform",
    title: "Dashboard Tools page removed",
    description:
      "The in-dashboard free Tools section is gone so the product stays clearly API-first. Public free tools at /tools are unchanged. Bookmarked /dashboard/tools links redirect to the API Playground.",
    items: [
      "Removed Tools from the dashboard sidebar",
      "/dashboard/tools → /dashboard/playground",
      "Marketing free tools at /tools remain available",
    ],
  },
  {
    publishedAt: "2026-07-29",
    category: "improvement",
    title: "Cheaper pricing on list and search endpoints",
    description:
      "Many list and search endpoints now bill a flat 2 credits per call instead of scaling per result. This covers YouTube comments, comment replies, channel videos, search, and channel playlists; TikTok top search and trending feed; Instagram hashtag search; Twitter/X user tweets and search; and Reddit subreddit posts, comments, transcript, search, and subreddit search. Other endpoints keep their existing per-call or per-result pricing — see each docs page.",
    items: [
      "YouTube comments, replies, channel videos, search, and playlists → flat 2 credits",
      "TikTok top search and trending feed → flat 2 credits",
      "Instagram hashtag search → flat 2 credits",
      "Twitter/X user tweets and search → flat 2 credits",
      "Reddit list, comments, transcript, and search endpoints → flat 2 credits",
    ],
  },
  {
    publishedAt: "2026-07-17",
    category: "platform",
    title: "Retired media-download and privacy-workaround endpoints and tools",
    description:
      "To keep Captapi focused on public data and analytics, we've retired the media-download endpoints and a set of free tools that copied media files or worked around platform privacy features. Retired APIs: YouTube Video Download, TikTok Video Download, Instagram Video Download, Instagram Story Highlights, and Instagram Highlights Details. Retired free tools: YouTube to MP4/MP3, YouTube Shorts Downloader, YouTube Thumbnail Downloader, Instagram Photo Downloader, Instagram Highlights Viewer, Snapchat Story Viewer, Who Viewed My Profile, Am I Blocked, What Happens When You Block, Screenshot Notification Checker, and Snapchat+ Checker. All transcript, summary, profile, stats, comment, search, and trend endpoints are unchanged.",
    items: [
      "Retired 5 download/story endpoints across YouTube, TikTok, and Instagram",
      "Retired 12 media-download and privacy-workaround free tools",
      "No change to transcripts, summaries, profiles, stats, comments, search, or trends",
    ],
  },
  {
    publishedAt: "2026-07-17",
    category: "improvement",
    title: "TikTok Search Suggestions now returns a ready-to-open search link",
    description:
      "Every suggestion from the TikTok Search Suggestions API now includes a searchUrl — a direct TikTok search link that runs that exact query, so you can jump straight from a suggested keyword to its results. Alongside the existing suggestion text, rank, seed keyword, region, and language, it makes the endpoint a more complete keyword-research tool. No change to pricing.",
    items: [
      "New searchUrl field on each suggestion — opens that exact search on TikTok",
      "Rank now reflects TikTok's own suggestion order",
    ],
  },
  {
    publishedAt: "2026-07-17",
    category: "feature",
    title: "TikTok search, reworked: Search by Hashtag and Search Users",
    description:
      "TikTok search is now two focused endpoints. Search by Hashtag (/v1/tiktok/search/hashtag) returns the videos posted under a tag — each with its URL, caption, author, and full engagement counts — plus an optional region parameter that sets the proxy's exit country. Search Users (/v1/tiktok/search/users) returns the creators whose username, display name, or bio match a query, each with follower count, verified flag, and avatar. Both add cursor pagination: pass the returned nextCursor to page through results and check hasMore to know when you've reached the end. This replaces the older TikTok Search, TikTok Hashtag Search, and TikTok User Search endpoints, which have been retired. Billed per result.",
    items: [
      "TikTok Search by Hashtag API — videos under a hashtag with engagement counts and an optional proxy region",
      "TikTok Search Users API — creators matching a query with follower count, verified flag, and avatar",
      "Both support cursor pagination via nextCursor + hasMore",
      "Retired the old /v1/tiktok/search, /hashtag-search, and /user-search endpoints",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "TikTok Audience Demographics is now native — a real country breakdown",
    description:
      "The TikTok Audience Demographics API now returns a ranked breakdown of a creator's audience by country. TikTok never publishes follower geography, but every commenter's country is exposed on its own data, so we sample the people engaging across a creator's recent videos and tally their countries into audienceLocations — each with a country name, ISO countryCode, a raw count, and a percentage of the sample, plus videosSampled and sampleSize for transparency. It's computed from TikTok's own public engagement data and now costs a flat 3 credits.",
    items: [
      "New audienceLocations array: country, countryCode, count, and percentage",
      "Engagement-based country mix sampled from real commenters",
      "videosSampled and sampleSize included so you can judge the sample",
      "Native, no audience actor — flat 3 credits; cached results stay free",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "TikTok Profile Region now resolves a country even when TikTok hides it",
    description:
      "TikTok no longer exposes an account's country on any public surface, so the region field used to be almost always null. It's now filled with the best available signal: TikTok's authoritative value when present, otherwise an AI-inferred country (e.g. IT or US) guessed from public profile cues — bio, display name, and language. A regionSource field tells you which one you got (\"tiktok\" or \"inferred\") and regionConfidence (high/medium/low) grades an inferred guess. Flat 2 credits per call.",
    items: [
      "region is now populated: TikTok's own value, else an AI-inferred country",
      "regionSource labels the origin — \"tiktok\" or \"inferred\"",
      "regionConfidence grades inferred guesses (high/medium/low)",
      "Flat 2 credits per call; cached results stay free",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "Cheaper pricing on high-volume endpoints",
    description:
      "Several high-volume endpoints now cost far fewer credits. TikTok Comments drops to a flat 2 credits per call, and a range of single-fetch endpoints drop to just 1 credit. Cached results are still free and failed or empty calls are never charged.",
    items: [
      "TikTok Comments: flat 2 credits per call (was up to 10)",
      "YouTube Community Post Details: 1 credit",
      "Twitch Profile, Twitch Clip, and Twitch User Schedule: 1 credit",
      "SoundCloud Artist and SoundCloud Track: 1 credit",
      "Facebook Marketplace Item: 1 credit",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "TikTok Comments gets cursor pagination",
    description:
      "The TikTok Comments API now fetches straight from TikTok's own public data and supports true cursor pagination. Each response includes totalComments (the video's full comment count) and a nextCursor — pass it back in the cursor parameter to page through every comment, up to 500 per call. Comments still return text, author username and avatar, like count, and publish time. Now billed as a flat 2 credits per call (no matter how many comments you fetch), with automatic retries if a fetch path is unavailable.",
    items: [
      "Direct TikTok public data with automatic retries",
      "Cursor pagination: pass the returned nextCursor to fetch the next page",
      "New totalComments field with the video's full comment count",
      "Reply threads still available via the TikTok Comment Replies API",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "cache defaults to false — fresh data unless you opt in",
    description:
      "The optional cache query parameter on every data endpoint now defaults to false, so requests fetch fresh data unless you explicitly pass cache=true. Previously the default was true (serve from the 24h cache). Pass cache=true when you want the cached copy for free/instant repeat lookups.",
    items: [
      "Default is now cache=false on all data endpoints (always fresh)",
      "Pass cache=true to serve from the 24h response cache",
      "Updated across OpenAPI, docs, playground, MCP, SDKs, CLI, n8n, Make, Zapier, and Apify",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "Instagram Basic Profile by user ID — richer fields",
    description:
      "The Instagram Basic Profile API now takes an Instagram numeric user ID (e.g. 314216) and returns a much richer public profile — username, full name, biography, follower/following/media counts, verification and privacy flags, business/professional status, and standard + HD profile pictures — straight from Instagram's own public data. A profile URL, @handle, or username is still accepted and resolved automatically. Still costs 1 credit, and null/empty fields are stripped for a tidy response.",
    items: [
      "Accepts a numeric userId (URL/@handle/username also work)",
      "Returns bio, counts, verification, business flags, pk/fbid, and HD profile pic",
      "Faster profile resolution with automatic retries",
      "Null/empty fields are dropped, so you only see populated data",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "Instagram Embed API is now the Instagram Embed HTML API — full embed doc + profiles",
    description:
      "The Instagram Embed API is now called the Instagram Embed HTML API. It now returns Instagram's own self-contained embed page as full HTML (the document served at /embed/) instead of just the blockquote snippet, plus an embedUrl you can point an <iframe src> at. It also accepts profile URLs and @handles in addition to posts and reels — posts/reels come back as a media card, profiles as a profile card.",
    items: [
      "html is now Instagram's full self-contained embed document (iframe-ready)",
      "New embedUrl field to load the embed directly via <iframe src>",
      "Accepts profile URLs/@handles too; adds a type flag (post/reel/profile)",
      "Falls back to the classic blockquote + embed.js snippet if the page is unavailable",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "Instagram Highlights Details by highlight ID — 1 credit",
    description:
      "The Instagram Highlights Details API now takes a single Highlight ID (the id returned by the Story Highlights API) and returns just that album's stories from Instagram's public data. Pair it with Story Highlights: list a profile's albums, then pass an ID here to pull its contents. It's faster, richer, and the price dropped from 9 credits to 1.",
    items: [
      "Now accepts id (e.g. highlight:18201653992314974) instead of a profile URL + limit",
      "Returns one highlight's stories with media/video URL, thumbnail, size, duration, and post date",
      "Faster responses (~1s) and now costs 1 credit (was 9)",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "fix",
    title: "Instagram Story Highlights: dropped the always-empty itemCount",
    description:
      "The Instagram Story Highlights API listed every highlight album with an itemCount that was always null — the light listing endpoint never loads the stories inside, so it could never count them. We removed the misleading field. To get the real count (and the stories themselves), use the Instagram Highlights Details API, where itemCount is now always populated.",
    items: [
      "Each highlight now returns id, title, and coverUrl (no more null itemCount)",
      "Instagram Highlights Details now always fills itemCount from the expanded stories",
      "Response cache was refreshed so you see the new shape immediately",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "Instagram Profile Search — 1 credit",
    description:
      "The Instagram Profile Search API resolves a matching public profile directly from Instagram. Pass an account name, @handle, or profile URL. It's faster, more reliable, and the price dropped from 12 credits to 1.",
    items: [
      "Now costs 1 credit per lookup (was 12) and returns results in ~1s",
      "Accepts a name, @handle, or profile URL — e.g. nike, @nasa, instagram.com/natgeo",
      "The limit parameter was removed; the endpoint resolves the single matching profile",
    ],
  },
  {
    publishedAt: "2026-07-15",
    category: "improvement",
    title: "Instagram Music Posts API retired",
    description:
      "The Instagram Music Posts API has been removed — it was a duplicate of the Instagram Reels By Audio ID API (same scraper, same data) at a higher price. Use Reels By Audio ID instead; it accepts both audio IDs and full audio page URLs.",
    items: [
      "GET /v1/instagram/music-posts no longer exists (returns 404)",
      "Migrate to GET /v1/instagram/reels-by-audio-id — pass your audio page URL or the numeric audio ID as audio_id",
      "Old docs links redirect to the Reels By Audio ID page automatically",
    ],
  },
  {
    publishedAt: "2026-07-15",
    category: "improvement",
    title: "cache parameter on every endpoint (historical)",
    description:
      "Historical note: on this date every data endpoint gained an optional cache query parameter. Later (2026-07-16) the default flipped to cache=false (always fresh). Prefer the 2026-07-16 changelog entry for current behavior.",
    items: [
      "Superseded by: cache defaults to false — pass cache=true to use the 24h cache",
      "Documented across docs, playground, MCP, SDKs, CLI, and n8n",
      "Account endpoints (balance, usage) are always live and unaffected",
    ],
  },
  {
    publishedAt: "2026-07-14",
    category: "feature",
    title: "Report a bug from any API page",
    description:
      "A Report a bug button on every API docs page and in the dashboard lets you flag a wrong response, an error, or something slow in a couple of clicks.",
    items: [
      "Modal form with an endpoint picker (prefilled on API pages), a description field, and an optional email for logged-out users",
      "Reports are linked to your account automatically when you're signed in — no need to type your details",
      "Sits next to \"Try it\" on each API page and in the dashboard sidebar",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "feature",
    title: "Integrations hub at /integrations",
    description:
      "A dedicated page listing every official integration with setup guides, plus a hover dropdown in the navbar.",
    items: [
      "MCP Server (hosted + local), TypeScript & Python SDKs, CLI, n8n, Make.com, Apify Actor, and the REST API in one place",
      "Each card links to its setup guide and npm/PyPI package",
      "Machine-readable manifests highlighted for AI agents (/mcp.json, /llms.txt, OpenAPI 3)",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "feature",
    title: "Monitors + HMAC-signed webhooks",
    description:
      "Point a monitor at any list-returning endpoint and get only new items POSTed to your webhook — no polling loops on your side.",
    items: [
      "POST /v1/monitors: watch subreddit posts, channel videos, ad-library searches and more on your schedule (15 min to 24 h)",
      "Deliveries are HMAC-SHA256 signed (X-Captapi-Signature over timestamp.body) so you can verify authenticity",
      "POST /v1/monitors/{id}/test sends a signed test delivery",
      "Runs bill credits exactly like direct API calls; cached results stay free",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "feature",
    title: "Automatic metric history (GET /v1/history)",
    description:
      "Follower, view, and like counts now accumulate into a time series automatically whenever tracked profile or post endpoints are fetched fresh.",
    items: [
      "Chart growth without building your own snapshot pipeline",
      "Covers profile and details endpoints across YouTube, TikTok, Instagram, X, Reddit, Bluesky, Twitch and more",
      "Query by endpoint + URL with a configurable window (up to 365 days)",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "feature",
    title: "Batch endpoint (POST /v1/batch)",
    description: "Run up to 20 endpoint calls concurrently in a single HTTP request.",
    items: [
      "Per-item status and per-item billing — one failed item never fails the batch",
      "Cached items are free, exactly like single calls",
      "Ideal for enriching lists of profiles or videos in one round-trip",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "feature",
    title: "Public status page",
    description:
      "Live API health at /status, computed from real production traffic — not a manually flipped switch.",
    items: [
      "GET /v1/status (no auth) returns overall and per-platform success rates and response times over the last 24 h",
      "Human view at captapi.com/status refreshes every 2 minutes",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "feature",
    title: "Official TypeScript & Python SDKs",
    description:
      "Typed clients generated from the same catalog that powers the API, MCP server, and CLI.",
    items: [
      "npm install @captapi/sdk — zero dependencies, works on Node 18+, Deno, Bun, and edge runtimes",
      "pip install captapi — sync (Captapi) and async (AsyncCaptapi) clients on httpx",
      "A typed, namespaced method for every endpoint; errors always throw with status + code",
      "x-api-key header now accepted as an alias for Authorization: Bearer",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "integration",
    title: "MCP catalog synced to all endpoints",
    description:
      "The hosted MCP server and every published package now expose the full endpoint catalog.",
    items: [
      "@captapi/mcp 0.4.0, @captapi/cli 0.3.0, n8n-nodes-captapi 0.3.0, Apify Actor 0.3 published",
      "OpenAPI 3 spec linked from llms.txt manifests for AI agent discovery",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "improvement",
    title: "Richer response data across 11 platforms",
    description: "Closed field gaps against competitors with dedicated upstream sources.",
    items: [
      "Reddit: comment upvotes + threading (residential routing, optional OAuth app support)",
      "Twitch: clip/profile metadata and streamer schedules via a dedicated actor",
      "TikTok Shop: product reviews via a dedicated actor",
      "Also enriched: link-in-bio socials/email, Rumble embeds/streams/comments, Pinterest pin details, SoundCloud artist fields, Bluesky embeds, Truth Social website, GitHub repo/license/topics, X profile counts",
    ],
  },
  {
    publishedAt: "2026-07-03",
    category: "improvement",
    title: "Real response examples for all endpoints",
    description:
      "Every endpoint page now shows a real captured response, refreshed in batches across the whole catalog.",
    items: [
      "Batches covered Twitter/LinkedIn/Reddit, TikTok Shop/Threads/Snapchat/ad libraries, GitHub/Facebook Marketplace/Events/Pinterest/Spotify, and Rumble/Twitch/Bluesky/SoundCloud/Kwai",
      "Dozens of mapper fixes along the way: timestamped transcript segments, YouTube comment author metadata, duration parsing, Instagram actor replacement and more",
    ],
  },
  {
    publishedAt: "2026-07-03",
    category: "feature",
    title: "Platform landing pages + APIs dropdown",
    description:
      "Every platform got a dedicated landing page with endpoint lists, FAQ, and structured data; the navbar now opens the full API catalog.",
    items: [],
  },
  {
    publishedAt: "2026-06-28",
    category: "platform",
    title: "180 endpoints across 29 platforms",
    description: "Major catalog expansion with reliability fixes across the board.",
    items: [
      "New platforms and endpoints across the catalog, audited live end-to-end",
      "Endpoint reliability, agent URL validation, and integration discovery improvements",
      "Comprehensive live audit reports added to the repo",
    ],
  },
  {
    publishedAt: "2026-05-31",
    category: "platform",
    title: "EnsembleData & Scrape Creators parity push",
    description:
      "Expanded TikTok, Instagram, YouTube, and Facebook coverage to close competitor gaps.",
    items: [
      "19 new endpoints: TikTok hashtag/top/user search, song details, trending; IG hashtag/profile search, story highlights, embed; YT comment replies, channel playlists, community posts; FB profile posts/reels, group posts, comment replies",
      "Per-result pricing normalized to guarantee margins; dashboard analytics tab with daily usage charts",
    ],
  },
  {
    publishedAt: "2026-05-29",
    category: "feature",
    title: "Captapi launch",
    description:
      "One API for structured public social-media data: transcripts, AI summaries, comments, profiles, search, and downloads.",
    items: [
      "REST API with Bearer auth, credit-based billing, and cached-result discounts",
      "Dashboard with API keys, playground, usage analytics, and billing",
      "SEO/AEO foundation: llms.txt, structured data, programmatic docs",
    ],
  },
];

export async function getChangelog(): Promise<ChangelogEntry[]> {
  const sb = getServiceClient();
  if (sb) {
    const { data, error } = await sb
      .from("changelog_entries")
      .select("*")
      .order("published_at", { ascending: false })
      .order("created_at", { ascending: false });
    if (!error && data && data.length > 0) {
      return (data as ChangelogRow[]).map(parseRow);
    }
  }
  return FALLBACK_ENTRIES.map((e, i) => ({ ...e, id: `fallback-${i}` }));
}

/** Group entries by publish date (already sorted desc). */
export function groupByDate(entries: ChangelogEntry[]): { date: string; entries: ChangelogEntry[] }[] {
  const groups: { date: string; entries: ChangelogEntry[] }[] = [];
  for (const entry of entries) {
    const last = groups[groups.length - 1];
    if (last && last.date === entry.publishedAt) {
      last.entries.push(entry);
    } else {
      groups.push({ date: entry.publishedAt, entries: [entry] });
    }
  }
  return groups;
}
