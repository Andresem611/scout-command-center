import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    APP_VERSION: '2.0.0',
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
