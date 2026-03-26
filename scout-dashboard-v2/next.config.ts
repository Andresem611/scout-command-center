import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable static export for Vercel
  output: 'standalone',
  
  // Environment variables available at build time
  env: {
    APP_VERSION: '2.0.0',
  },
};

export default nextConfig;
