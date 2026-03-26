import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Vercel handles output automatically
  env: {
    APP_VERSION: '2.0.0',
  },
};

export default nextConfig;
