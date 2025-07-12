#!/bin/bash
# Optimized Azure App Service startup for GitRot (FastAPI + Next.js)
# Simplified version that handles Azure constraints better

echo "🔵 Azure App Service: GitRot Optimized Startup"

# Install system dependencies with error handling
echo "📦 Installing system dependencies..."
apt-get update -q 2>/dev/null || echo "⚠️ Package update skipped"
apt-get install -y git curl 2>/dev/null || echo "⚠️ System packages may already be installed"

# Install Node.js 20 (LTS) with version verification
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - 2>/dev/null
    apt-get install -y nodejs 2>/dev/null
fi

# Verify Node.js version - Next.js 15 requires Node.js 18.18+
echo "🔍 Verifying Node.js version..."
node_version=$(node -v)
echo "📦 Node.js version: $node_version"

# Check if Node.js version is compatible (18.18+)
node_major=$(echo $node_version | cut -d'.' -f1 | sed 's/v//')
node_minor=$(echo $node_version | cut -d'.' -f2)

if [ "$node_major" -lt 18 ] || ([ "$node_major" -eq 18 ] && [ "$node_minor" -lt 18 ]); then
    echo "❌ Node.js version $node_version is too old. Next.js 15 requires Node.js 18.18+"
    echo "📦 Installing latest Node.js LTS..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - 2>/dev/null
    apt-get install -y nodejs 2>/dev/null
    echo "📦 Updated Node.js version: $(node -v)"
fi

# Verify critical dependencies
if ! command -v git &> /dev/null; then
    echo "❌ Git is required but not available"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not available"
    exit 1
fi

echo "✅ Dependencies verified:"
echo "   Git: $(git --version 2>/dev/null || echo 'Not available')"
echo "   Node: $(node --version 2>/dev/null || echo 'Not available')"
echo "   npm: $(npm --version 2>/dev/null || echo 'Not available')"

# Set Git environment variables
export GIT_PYTHON_REFRESH=quiet
export GIT_PYTHON_GIT_EXECUTABLE=$(which git)

# Set production environment early
export NODE_ENV=production
export NEXT_TELEMETRY_DISABLED=1

# Azure port configuration
PORT=${PORT:-8000}
export PORT

echo "🌐 Using port: $PORT"

# Install Python dependencies
echo "🐍 Installing Python backend dependencies..."
pip install -r requirements.txt || {
    echo "❌ Failed to install Python dependencies"
    exit 1
}

# Handle Next.js frontend
if [[ -d "gitrot-frontend" ]]; then
    echo "🎨 Setting up Next.js frontend..."
    cd gitrot-frontend
    
    # Check if package.json exists
    if [[ ! -f "package.json" ]]; then
        echo "❌ package.json not found in gitrot-frontend directory"
        cd ..
        echo "⚠️ Skipping frontend build, running backend only"
    else
        # Check if build already exists (pre-built)
        if [[ -d ".next" ]]; then
            echo "✅ Frontend build already exists, skipping build process"
        else
            # For Azure App Service, we need to optimize the build process
            echo "🏗️ Starting optimized frontend build for Azure..."
            echo "🔍 Environment info - Node.js: $(node -v), NPM: $(npm -v)"
            
            # Use npm ci for faster, reproducible builds
            echo "📦 Installing frontend dependencies (fast mode)..."
            timeout 60 npm ci --prefer-offline --no-audit --no-fund --silent || {
                echo "⚠️ Fast install failed, trying regular install..."
                timeout 90 npm install --silent || {
                    echo "❌ Could not install frontend dependencies"
                    cd ..
                    echo "⚠️ Running backend only due to frontend setup failure"
                    return 0
                }
            }
            
            # Build with optimizations for Azure
            echo "🏗️ Building Next.js application (optimized)..."
            # Set build timeout and use faster build options
            NEXT_TELEMETRY_DISABLED=1 NODE_ENV=production NODE_OPTIONS="--max-old-space-size=1024" timeout 120 npm run build:fast || {
                echo "❌ Frontend build failed or timed out"
                cd ..
                echo "⚠️ Running backend only due to build failure"
                return 0
            }
        fi
        
        cd ..
        echo "✅ Frontend setup completed!"
    fi
else
    echo "⚠️ Frontend directory not found, running backend only"
fi

# Set production environment
export NODE_ENV=production
export NEXT_TELEMETRY_DISABLED=1

# Update FastAPI CORS for Azure
echo "🔧 Configuring CORS for Azure environment..."

# Create a dynamic CORS configuration
cat > update_cors.py << 'EOF'
import os
import re

# Read the current fastapi_app.py
with open('fastapi_app.py', 'r') as f:
    content = f.read()

# Get Azure hostname
azure_hostname = os.getenv('WEBSITE_HOSTNAME', 'localhost')

# Define new CORS origins
new_origins = f'''[
    "http://localhost:3000",
    "http://127.0.0.1:3000", 
    "https://{azure_hostname}",
    f"https://{{azure_hostname}}",
]'''

# Update CORS origins in the file
cors_pattern = r'allow_origins=\[[^\]]*\]'
updated_content = re.sub(cors_pattern, f'allow_origins={new_origins}', content)

# Write back the updated content
with open('fastapi_app.py', 'w') as f:
    f.write(updated_content)

print(f"✅ CORS updated for Azure hostname: {azure_hostname}")
EOF

python update_cors.py 2>/dev/null || echo "⚠️ CORS update skipped"

# Start the backend immediately to avoid Azure timeout
echo "🚀 Starting FastAPI application (quick start mode)..."

# Azure App Service expects the main process to run in foreground
exec uvicorn fastapi_app:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level info \
    --access-log \
    --no-use-colors
