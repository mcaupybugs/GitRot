#!/bin/bash
# Azure App Service startup for GitRot
# Frontend is pre-built by GitHub Actions

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

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt || {
    echo "❌ Failed to install Python dependencies"
    exit 1
}

# Set Git environment variables (if git operations are needed)
export GIT_PYTHON_REFRESH=quiet
if command -v git &> /dev/null; then
    export GIT_PYTHON_GIT_EXECUTABLE=$(which git)
fi

# Check if frontend build exists (should be built by GitHub Actions)
if [[ -d "gitrot-frontend/.next" ]]; then
    echo "✅ Frontend build found - ready to serve"
else
    echo "⚠️ Frontend build not found - running backend only"
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
