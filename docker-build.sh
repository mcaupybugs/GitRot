#!/bin/bash

# GitRot Docker Build Script
# Builds Docker images for both production and development

set -e

echo "🐳 GitRot Docker Build Script"
echo "=============================="

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -p, --prod     Build production image"
    echo "  -d, --dev      Build development image"
    echo "  -a, --all      Build both production and development images"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --prod      # Build production image"
    echo "  $0 --dev       # Build development image"
    echo "  $0 --all       # Build both images"
}

# Parse command line arguments
BUILD_PROD=false
BUILD_DEV=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--prod)
            BUILD_PROD=true
            shift
            ;;
        -d|--dev)
            BUILD_DEV=true
            shift
            ;;
        -a|--all)
            BUILD_PROD=true
            BUILD_DEV=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# If no options provided, show usage
if [[ "$BUILD_PROD" == false && "$BUILD_DEV" == false ]]; then
    echo "Error: No build target specified."
    show_usage
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Build production image
if [[ "$BUILD_PROD" == true ]]; then
    echo "🏗️  Building production image..."
    docker build -t gitrot:latest -t gitrot:prod .
    echo "✅ Production image built successfully: gitrot:latest, gitrot:prod"
fi

# Build development image
if [[ "$BUILD_DEV" == true ]]; then
    echo "🏗️  Building development image..."
    docker build -f Dockerfile.dev -t gitrot:dev .
    echo "✅ Development image built successfully: gitrot:dev"
fi

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "Available images:"
docker images | grep gitrot

echo ""
echo "Next steps:"
if [[ "$BUILD_PROD" == true ]]; then
    echo "  Run production:  docker-compose up"
    echo "  Or directly:     docker run -p 3000:3000 -p 8000:8000 gitrot:latest"
fi
if [[ "$BUILD_DEV" == true ]]; then
    echo "  Run development: docker-compose --profile dev up gitrot-dev"
    echo "  Or directly:     docker run -p 3000:3000 -p 8000:8000 -v \$(pwd):/app gitrot:dev"
fi
