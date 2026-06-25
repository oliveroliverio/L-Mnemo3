import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow the user's remote IP for Hot Module Reloading
  allowedDevOrigins: ['10.53.4.247'],
  async rewrites() {
    return [
      {
        source: '/api/memory-peg/:path*',
        destination: `${process.env.NEXT_PUBLIC_MEMORY_PEG_API}/:path*`,
      },
      {
        source: '/api/sqlite/:path*',
        destination: `${process.env.NEXT_PUBLIC_SQLITE_API}/:path*`,
      }
    ];
  },
};

export default nextConfig;
