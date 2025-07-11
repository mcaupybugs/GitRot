import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* config options here */
  experimental: {
    // Ensure stable builds
    forceSwcTransforms: true,
  },
  
  // Ensure proper module resolution
  webpack: (config) => {
    // Ensure proper module resolution for @/ aliases
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(process.cwd(), 'src'),
      '@/lib': path.resolve(process.cwd(), 'src/lib'),
      '@/components': path.resolve(process.cwd(), 'src/components'),
    };
    
    // Ensure consistent builds
    config.cache = false;
    
    // Additional resolve options for better compatibility
    config.resolve.extensions = ['.tsx', '.ts', '.jsx', '.js', '.json'];
    
    return config;
  },
  
  // Output configuration for better Azure compatibility
  output: 'standalone',
};

export default nextConfig;
