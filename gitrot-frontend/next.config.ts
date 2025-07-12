import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* config options here */
  experimental: {
    // Optimize build performance
    optimizePackageImports: ['lucide-react'],
  },
  
  // Ensure proper module resolution
  webpack: (config, { dev }) => {
    // Ensure proper module resolution for @/ aliases
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(process.cwd(), 'src'),
      '@/lib': path.resolve(process.cwd(), 'src/lib'),
      '@/components': path.resolve(process.cwd(), 'src/components'),
    };
    
    // Optimize for faster builds in production
    if (!dev) {
      // Reduce bundle analysis time
      config.optimization = {
        ...config.optimization,
        minimize: true,
        // Faster builds with smaller chunks
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: {
              minChunks: 1,
              priority: -20,
              reuseExistingChunk: true,
            },
            vendors: {
              test: /[\\/]node_modules[\\/]/,
              priority: -10,
              reuseExistingChunk: true,
            },
          },
        },
      };
    }
    
    // Additional resolve options for better compatibility
    config.resolve.extensions = ['.tsx', '.ts', '.jsx', '.js', '.json'];
    
    return config;
  },
  
  // Output configuration for better Azure compatibility
  output: 'standalone',
  
  // Disable source maps in production for faster builds
  productionBrowserSourceMaps: false,
};

export default nextConfig;
