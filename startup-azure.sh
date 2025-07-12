#!/bin/bash
# Azure App Service startup for GitRot
# Builds frontend during deployment with timeout protection

echo "🔵 Azure App Service: GitRot Startup with Frontend Build"

# Set production environment
export NODE_ENV=production
export NEXT_TELEMETRY_DISABLED=1

# Azure port configuration
PORT=${PORT:-8000}
export PORT

echo "🌐 Using port: $PORT"

# Install system dependencies quickly
echo "📦 Installing system dependencies..."
apt-get update -q >/dev/null 2>&1 || echo "⚠️ Package update skipped"
apt-get install -y git curl nodejs npm >/dev/null 2>&1 || echo "⚠️ Some packages may already be installed"

# Verify Node.js version
echo "🔍 Environment check..."
echo "   Python: $(python3 --version 2>/dev/null || echo 'Not available')"
echo "   Node: $(node --version 2>/dev/null || echo 'Not available')"
echo "   NPM: $(npm --version 2>/dev/null || echo 'Not available')"

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt || {
    echo "❌ Failed to install Python dependencies"
    exit 1
}

# Build frontend with timeout protection
echo "🎨 Building frontend with timeout protection..."
if [[ -d "gitrot-frontend" ]]; then
    cd gitrot-frontend
    
    # Quick dependency install
    echo "📦 Installing frontend dependencies..."
    timeout 90 npm ci --prefer-offline --no-audit --no-fund >/dev/null 2>&1 || {
        echo "⚠️ Fast install failed, trying npm install..."
        timeout 120 npm install >/dev/null 2>&1 || {
            echo "❌ Frontend dependency install failed"
            cd ..
            echo "⚠️ Continuing with backend only"
            frontend_available=false
        }
    }
    
    if [[ "$frontend_available" != "false" ]]; then
        # Build with strict timeout
        echo "🏗️ Building Next.js application..."
        timeout 150 npm run build >/dev/null 2>&1 || {
            echo "❌ Frontend build timed out or failed"
            cd ..
            echo "⚠️ Continuing with backend only"
            frontend_available=false
        }
    fi
    
    cd ..
    
    if [[ "$frontend_available" != "false" ]]; then
        echo "✅ Frontend build completed"
    fi
else
    echo "⚠️ Frontend directory not found"
fi

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

# Start the backend immediately
echo "🚀 Starting FastAPI application..."

# Azure App Service expects the main process to run in foreground
exec uvicorn fastapi_app:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level info \
    --access-log \
    --no-use-colors
