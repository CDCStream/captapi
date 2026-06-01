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
    ];
  },
};

export default nextConfig;
