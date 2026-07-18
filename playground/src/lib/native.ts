// Heuristic for whether an endpoint is served by our self-scraper (direct) or
// an Apify actor. Mirrors the migration state in the backend routers. Used only
// to ESTIMATE upstream cost in the console; the authoritative source is the
// requests.source column. Update as more endpoints migrate to native.
import type { Endpoint } from "../catalog.generated";
import type { SourceGuess } from "./cost";

// Whole platforms served natively (no Apify) today.
const NATIVE_PLATFORMS = new Set<string>([
  "twitch",
  "github",
  "bluesky",
  "linktree",
  // SoundCloud: all endpoints try the public api-v2 first (Apify fallback).
  "soundcloud",
]);

// Specific native-first paths on otherwise-Apify platforms.
const NATIVE_PATHS = new Set<string>([
  // TikTok native-first endpoints
  "/v1/tiktok/video-details",
  "/v1/tiktok/channel-details",
  "/v1/tiktok/channel-posts",
  "/v1/tiktok/comments",
  "/v1/tiktok/profile-region",
  "/v1/tiktok/audience-demographics",
  // Twitter transcript uses the free syndication API (Apify fallback).
  "/v1/twitter/transcript",
  // YouTube is native-first for everything except these Apify-only paths
  // (handled by the exclusion set below).
]);

// YouTube is native-first across the board except a few actor-only endpoints.
const YT_APIFY_ONLY = new Set<string>([
  "/v1/youtube/trending-shorts",
  "/v1/youtube/community-posts",
]);

// Instagram endpoints served by Decodo's instagram_graphql_profile target.
// hashtag/post targets are currently disabled on Decodo's side, so
// hashtag-search falls back to Apify.
const IG_DECODO_PATHS = new Set<string>([
  "/v1/instagram/channel-details",
  "/v1/instagram/basic-profile",
  "/v1/instagram/channel-posts",
  "/v1/instagram/channel-reels",
  "/v1/instagram/reels-search",
]);

export function guessSource(e: Endpoint): SourceGuess {
  if (e.platform === "youtube") {
    return YT_APIFY_ONLY.has(e.path) ? "apify" : "direct";
  }
  if (e.platform === "instagram") {
    if (e.path === "/v1/instagram/embed") return "direct";
    return IG_DECODO_PATHS.has(e.path) ? "direct" : "apify";
  }
  if (NATIVE_PLATFORMS.has(e.platform)) return "direct";
  if (NATIVE_PATHS.has(e.path)) return "direct";
  return "apify";
}
