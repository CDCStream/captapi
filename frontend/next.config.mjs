/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  typedRoutes: false,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  async rewrites() {
    return [
      // Agents commonly probe /.well-known/ for service manifests.
      { source: "/.well-known/mcp.json", destination: "/mcp.json" },
      { source: "/.well-known/llms.txt", destination: "/llms.txt" },
      { source: "/.well-known/llms-full.txt", destination: "/llms-full.txt" },
    ];
  },
  async redirects() {
    return [
      // Dashboard free-tools UI confused users about the API product;
      // send bookmarked links to the API Playground.
      {
        source: "/dashboard/tools",
        destination: "/dashboard/playground",
        permanent: true,
      },
      {
        source: "/dashboard/tools/:slug",
        destination: "/dashboard/playground",
        permanent: true,
      },
      // instagram-music-posts was removed (duplicate of reels-by-audio-id,
      // same scraper and data); keep old docs links alive.
      {
        source: "/apis/instagram-music-posts",
        destination: "/apis/instagram-reels-by-audio-id",
        permanent: true,
      },
      // Retired media-download how-tos / tools (ban-risk surfaces).
      {
        source: "/how-to/youtube-video-download",
        destination: "/how-to/youtube-video-details",
        permanent: true,
      },
      {
        source: "/how-to/tiktok-video-download",
        destination: "/how-to/tiktok-video-details",
        permanent: true,
      },
      {
        source: "/how-to/instagram-video-download",
        destination: "/how-to/instagram-details",
        permanent: true,
      },
      {
        source: "/tools/youtube-shorts-downloader",
        destination: "/tools/youtube-transcript",
        permanent: true,
      },
      {
        source: "/tools/youtube-to-mp4",
        destination: "/tools/youtube-transcript",
        permanent: true,
      },
      {
        source: "/tools/youtube-to-mp3",
        destination: "/tools/youtube-transcript",
        permanent: true,
      },
      {
        source: "/tools/youtube-thumbnail-downloader",
        destination: "/tools/youtube-transcript",
        permanent: true,
      },
      {
        source: "/tools/instagram-photo-downloader",
        destination: "/tools",
        permanent: true,
      },
      // Removed blog post still linked from other articles.
      {
        source: "/blog/mastering-rest-api-best-practices",
        destination: "/docs",
        permanent: true,
      },
      // Retired Google Search API page (never shipped / removed from catalog).
      {
        source: "/apis/google-search",
        destination: "/apis",
        permanent: true,
      },
      // Blog posts often link bare platform hubs (/apis/youtube) instead of the
      // real landing pages (/apis/youtube-api). Permanent redirects clear Ahrefs 404s.
      {
        source: "/apis/youtube",
        destination: "/apis/youtube-api",
        permanent: true,
      },
      {
        source: "/apis/tiktok",
        destination: "/apis/tiktok-api",
        permanent: true,
      },
      {
        source: "/apis/instagram",
        destination: "/apis/instagram-api",
        permanent: true,
      },
      {
        source: "/apis/reddit",
        destination: "/apis/reddit-api",
        permanent: true,
      },
      {
        source: "/apis/ad-library",
        destination: "/apis/facebook-ad-library-api",
        permanent: true,
      },
      {
        source: "/apis/ad-library-api",
        destination: "/apis/facebook-ad-library-api",
        permanent: true,
      },
      {
        source: "/apis/linkedin",
        destination: "/apis/linkedin-api",
        permanent: true,
      },
      {
        source: "/apis/facebook",
        destination: "/apis/facebook-api",
        permanent: true,
      },
      {
        source: "/apis/twitter",
        destination: "/apis/twitter-api",
        permanent: true,
      },
      // Renamed / shortened blog slugs still linked from older posts.
      {
        source: "/blog/top-10-data-collection-companies",
        destination: "/blog/data-collection-companies",
        permanent: true,
      },
      {
        source: "/blog/master-social-media-engagement-metrics",
        destination: "/blog/social-media-engagement-metrics",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
