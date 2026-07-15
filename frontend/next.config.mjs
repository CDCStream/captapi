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
    ];
  },
};

export default nextConfig;
