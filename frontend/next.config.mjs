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
    ];
  },
};

export default nextConfig;
