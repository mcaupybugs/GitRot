#!/bin/bash
# Azure App Service startup for GitRot
# Updated: 2025-07-14 - Added Node.js/npm installation for frontend support

echo "🔵 Azure App Service: GitRot Startup (GitHub Actions Build)"

# Set production environment
export NODE_ENV=production
export NEXT_TELEMETRY_DISABLED=1

# Azure port configuration
PORT=${PORT:-8000}
export PORT

echo "🌐 Using port: $PORT"

# Environment check
echo "🔍 Environment check..."
echo "   Python: $(python3 --version 2>/dev/null || echo 'Not available')"
echo "   Node.js: $(node --version 2>/dev/null || echo 'Not available')"
echo "   npm: $(npm --version 2>/dev/null || echo 'Not available')"

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt || {
    echo "❌ Failed to install Python dependencies"
    exit 1
}

# Install Node.js and npm for frontend support
echo "📦 Installing Node.js and npm..."
if ! command -v node &> /dev/null; then
    echo "   Installing Node.js..."
    # Install Node.js 20.x (LTS) for Azure Linux
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - 2>/dev/null || {
        # Fallback: try without sudo for Azure App Service
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash - 2>/dev/null || {
            echo "⚠️ Node.js installation failed, trying alternative method..."
            # Alternative: Install using package manager if available
            if command -v apt-get &> /dev/null; then
                apt-get update -y && apt-get install -y nodejs npm 2>/dev/null || {
                    echo "⚠️ Could not install Node.js via apt-get"
                }
            elif command -v yum &> /dev/null; then
                yum install -y nodejs npm 2>/dev/null || {
                    echo "⚠️ Could not install Node.js via yum"
                }
            fi
        }
    }
    
    # Try installing nodejs separately if not available
    if ! command -v node &> /dev/null && command -v apt-get &> /dev/null; then
        apt-get install -y nodejs 2>/dev/null
    fi
    
    # Try installing npm separately if not available
    if ! command -v npm &> /dev/null && command -v apt-get &> /dev/null; then
        apt-get install -y npm 2>/dev/null
    fi
fi

# Verify Node.js and npm installation
if command -v node &> /dev/null && command -v npm &> /dev/null; then
    echo "✅ Node.js installed: $(node --version)"
    echo "✅ npm installed: $(npm --version)"
else
    echo "⚠️ Node.js/npm installation incomplete - frontend features may be limited"
    echo "   Node.js available: $(command -v node &> /dev/null && echo "Yes" || echo "No")"
    echo "   npm available: $(command -v npm &> /dev/null && echo "Yes" || echo "No")"
fi

# Set Git environment variables (if git operations are needed)
export GIT_PYTHON_REFRESH=quiet
if command -v git &> /dev/null; then
    export GIT_PYTHON_GIT_EXECUTABLE=$(which git)
fi

# Check if frontend build exists (should be built by GitHub Actions)
if [[ -d "gitrot-frontend/.next" ]]; then
    echo "✅ Frontend build found - ready to serve"
else
    echo "⚠️ Frontend build not found"
    
    # Try to build frontend if Node.js/npm are available
    if command -v npm &> /dev/null && [[ -d "gitrot-frontend" ]]; then
        echo "🏗️ Attempting to build frontend..."
        cd gitrot-frontend || {
            echo "❌ Could not enter frontend directory"
            cd "$(dirname "$0")" # Return to script directory
        }
        
        if [[ -f "package.json" ]]; then
            echo "📦 Installing frontend dependencies..."
            npm install --production --silent 2>/dev/null || {
                echo "⚠️ Frontend dependency installation failed"
            }
            
            echo "🔨 Building frontend..."
            NEXT_TELEMETRY_DISABLED=1 NODE_ENV=production npm run build 2>/dev/null || {
                echo "⚠️ Frontend build failed"
            }
            
            if [[ -d ".next" ]]; then
                echo "✅ Frontend build completed successfully"
            else
                echo "⚠️ Frontend build did not produce expected output"
            fi
        else
            echo "⚠️ package.json not found in frontend directory"
        fi
        
        cd .. # Return to root directory
    else
        echo "⚠️ Cannot build frontend - npm not available or frontend directory missing"
        echo "💡 Running in backend-only mode"
    fi
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
# Force Azure refresh - Mon Jul 14 02:11:20 IST 2025
