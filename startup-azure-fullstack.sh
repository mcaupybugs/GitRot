#!/bin/bash
# Azure App Service startup script for GitRot Full-Stack (FastAPI + Next.js)
# This script handles both backend and frontend deployment on Azure

echo "🔵 Azure App Service: GitRot Full-Stack Startup Configuration"
echo "📦 Backend: FastAPI + 🎨 Frontend: Next.js"

# Azure best practice: Update package lists
echo "📦 Updating package lists..."
apt-get update -q

# Azure deployment: Install required system packages
echo "📦 Installing system dependencies..."
apt-get install -y git curl

# Install Node.js (required for Next.js)
echo "📦 Installing Node.js and npm..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

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
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
    apt-get install -y nodejs
    echo "📦 Updated Node.js version: $(node -v)"
fi

# Verify installations
echo "🔍 Verifying installations..."
if command -v git &> /dev/null; then
    echo "✅ Git installed: $(git --version)"
    export GIT_PYTHON_REFRESH=quiet
    export GIT_PYTHON_GIT_EXECUTABLE=$(which git)
else
    echo "❌ Git installation failed"
    exit 1
fi

if command -v node &> /dev/null; then
    echo "✅ Node.js installed: $(node --version)"
    echo "✅ npm installed: $(npm --version)"
else
    echo "❌ Node.js installation failed"
    exit 1
fi

# Install Python dependencies (Backend)
echo "🐍 Installing Python dependencies for FastAPI backend..."
pip install -r requirements.txt

# Install and build Next.js frontend
echo "🎨 Setting up Next.js frontend..."
cd gitrot-frontend

# Check if package.json exists
if [[ ! -f "package.json" ]]; then
    echo "❌ package.json not found in gitrot-frontend directory"
    exit 1
fi

# Clean install to ensure consistency
echo "🧹 Cleaning previous installs..."
rm -rf node_modules
rm -f package-lock.json

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Build the Next.js application
echo "🏗️ Building Next.js application..."
echo "🔍 Environment info - Node.js: $(node -v), NPM: $(npm -v)"

NEXT_TELEMETRY_DISABLED=1 NODE_ENV=production npm run build

if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed"
    exit 1
fi

echo "✅ Frontend build completed successfully!"

# Return to root directory
cd ..

# Azure best practice: Set environment variables
echo "🔧 Setting up environment variables..."
export NODE_ENV=production
export NEXT_TELEMETRY_DISABLED=1

# Get the port from Azure environment variable
PORT=${PORT:-8000}
FRONTEND_PORT=$((PORT + 1))

echo "🌐 Backend will run on port: $PORT"
echo "🎨 Frontend will run on port: $FRONTEND_PORT"

# Create a process manager script to handle both services
cat > run_services.sh << 'EOF'
#!/bin/bash

# Function to handle cleanup
cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Start FastAPI backend
echo "🚀 Starting FastAPI backend..."
uvicorn fastapi_app:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level info \
    --access-log \
    --no-use-colors &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start Next.js frontend
echo "🚀 Starting Next.js frontend..."
cd gitrot-frontend
npm start -- -p $FRONTEND_PORT -H 0.0.0.0 &
FRONTEND_PID=$!
cd ..

echo "✅ Both services started successfully!"
echo "📡 Backend API: http://localhost:$PORT"
echo "🎨 Frontend: http://localhost:$FRONTEND_PORT"
echo "📚 API Docs: http://localhost:$PORT/api/docs"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
EOF

# Make the service runner executable
chmod +x run_services.sh

# Azure App Service: Update CORS to allow frontend domain
echo "🔧 Configuring CORS for Azure deployment..."

# Create environment-specific configuration
cat > azure_config.py << EOF
import os

# Azure App Service configuration
AZURE_WEBSITE_HOSTNAME = os.getenv('WEBSITE_HOSTNAME', 'localhost')
FRONTEND_URL = f"https://{AZURE_WEBSITE_HOSTNAME}" if AZURE_WEBSITE_HOSTNAME != 'localhost' else f"http://localhost:$FRONTEND_PORT"

# CORS origins for Azure
CORS_ORIGINS = [
    FRONTEND_URL,
    f"http://localhost:$FRONTEND_PORT",
    "http://localhost:3000",  # Local development
    f"https://{AZURE_WEBSITE_HOSTNAME}",
]

print(f"🔧 CORS configured for: {CORS_ORIGINS}")
EOF

# Update frontend environment for production
echo "🔧 Configuring frontend for Azure..."
cd gitrot-frontend

# Create production environment file
cat > .env.production << EOF
NEXT_PUBLIC_API_URL=http://localhost:$PORT
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
EOF

cd ..

# Azure best practice: Health check endpoint
echo "🏥 Setting up health checks..."
cat > health_check.py << 'EOF'
#!/usr/bin/env python3
import requests
import sys
import time

def check_health():
    try:
        # Check backend
        backend_response = requests.get(f"http://localhost:{PORT}/health", timeout=10)
        if backend_response.status_code != 200:
            print("❌ Backend health check failed")
            return False
        
        # Check frontend (optional, as it might take longer to start)
        try:
            frontend_response = requests.get(f"http://localhost:{PORT + 1}", timeout=5)
            print("✅ Frontend is responding")
        except:
            print("⚠️ Frontend not ready yet (this is normal)")
        
        print("✅ Backend health check passed")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    PORT = int(os.getenv('PORT', 8000))
    
    # Wait for services to start
    time.sleep(10)
    
    # Perform health check
    if check_health():
        print("🎯 GitRot Full-Stack application is healthy!")
        sys.exit(0)
    else:
        print("💥 Health check failed!")
        sys.exit(1)
EOF

chmod +x health_check.py

# Start the services
echo "🚀 Starting GitRot Full-Stack Application..."
echo "📊 Process Management: Background services with monitoring"

# Run the services
./run_services.sh

echo "🎯 GitRot Full-Stack application startup complete!"
