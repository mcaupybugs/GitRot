#!/bin/bash
# Optimized Azure App Service startup for GitRot (FastAPI + Next.js)
# Uses UV for faster Python dependency management with pip fallback

echo "🔵 Azure App Service: GitRot Optimized Startup (with UV)"

# Install system dependencies with error handling
echo "📦 Installing system dependencies..."
apt-get update -q 2>/dev/null || echo "⚠️ Package update skipped"
apt-get install -y git curl 2>/dev/null || echo "⚠️ System packages may already be installed"

# Install Node.js 20 (LTS)
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - 2>/dev/null
    apt-get install -y nodejs 2>/dev/null
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
echo "   UV: $(uv --version 2>/dev/null || echo 'Not available')"

# Set Git environment variables
export GIT_PYTHON_REFRESH=quiet
export GIT_PYTHON_GIT_EXECUTABLE=$(which git)

# Azure port configuration
PORT=${PORT:-8000}
export PORT

echo "🌐 Using port: $PORT"

# Install UV if not available
if ! command -v uv &> /dev/null; then
    echo "⚡ Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install Python dependencies using UV
echo "🐍 Installing Python backend dependencies with UV..."
uv sync --frozen || {
    echo "❌ Failed to install Python dependencies with UV, falling back to pip..."
    pip install -r requirements.txt || {
        echo "❌ Failed to install Python dependencies"
        exit 1
    }
}

# Handle Next.js frontend
if [[ -d "gitrot-frontend" ]]; then
    echo "🎨 Setting up Next.js frontend..."
    cd gitrot-frontend
    
    # Install dependencies
    echo "📦 Installing frontend dependencies..."
    npm ci --only=production 2>/dev/null || npm install
    
    # Build the application
    echo "🏗️ Building Next.js application..."
    npm run build || {
        echo "❌ Frontend build failed"
        exit 1
    }
    
    cd ..
    echo "✅ Frontend build completed"
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

# Use UV if available, otherwise fall back to python
if command -v uv &> /dev/null; then
    uv run python update_cors.py 2>/dev/null || echo "⚠️ CORS update skipped"
else
    python update_cors.py 2>/dev/null || echo "⚠️ CORS update skipped"
fi

# For Azure App Service, we need to run only the backend
# Frontend will be served as static files or separate service
echo "🚀 Starting FastAPI application with UV..."

# Try to use UV first, fallback to direct uvicorn if UV not available
if command -v uv &> /dev/null; then
    # Azure App Service expects the main process to run in foreground
    exec uv run uvicorn fastapi_app:app \
        --host 0.0.0.0 \
        --port $PORT \
        --workers 1 \
        --log-level info \
        --access-log \
        --no-use-colors
else
    # Fallback to direct uvicorn
    exec uvicorn fastapi_app:app \
        --host 0.0.0.0 \
        --port $PORT \
        --workers 1 \
        --log-level info \
        --access-log \
        --no-use-colors
fi
