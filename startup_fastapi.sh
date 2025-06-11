#!/bin/bash

# GitRot FastAPI Azure App Service Startup Script
# Azure best practice: Enhanced startup with proper error handling and logging

echo "🚀 Starting GitRot FastAPI Application..."

# Set working directory
cd /home/site/wwwroot

# Azure deployment: Install Git
echo "📦 Installing Git on Azure App Service..."
apt-get install -y git

# Azure best practice: Verify Git installation
if command -v git &> /dev/null; then
    echo "✅ Git installed successfully"
    echo "🔍 Git version: $(git --version)"
    echo "📍 Git path: $(which git)"
    
    # Azure deployment: Set Git environment variables
    export GIT_PYTHON_REFRESH=quiet
    export GIT_PYTHON_GIT_EXECUTABLE=$(which git)
    
    echo "✅ Git environment variables configured"
else
    echo "❌ Git installation failed"
    exit 1
fi

# Set Git executable path for Azure App Service
export PATH="/usr/bin:/opt/python/3.9.19/bin:$PATH"

# Azure best practice: Set environment variables for production
export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"
export PYTHONUNBUFFERED=1

# Azure best practice: Configure logging
export UVICORN_LOG_LEVEL=info

# Azure best practice: Install/upgrade pip and dependencies
echo "📦 Installing Python dependencies..."
python3 -m pip install --upgrade pip --no-cache-dir
python3 -m pip install -r requirements.txt --no-cache-dir

# Azure best practice: Create necessary directories if they don't exist
mkdir -p templates static

# Azure best practice: Check if required files exist
if [ ! -f "fastapi_app.py" ]; then
    echo "❌ Error: fastapi_app.py not found"
    exit 1
fi

if [ ! -f "templates/home_page.html" ]; then
    echo "❌ Error: templates/home_page.html not found"
    exit 1
fi

echo "✅ Git configured and files verified"

# Azure best practice: Start the FastAPI application with proper configuration
echo "🌐 Starting FastAPI server..."

# Use the PORT environment variable set by Azure, default to 8000
PORT=${PORT:-8000}

# Start Uvicorn with production settings
uvicorn fastapi_app:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level info \
    --access-log \
    --no-use-colors

echo "🎯 GitRot FastAPI application started on port $PORT"
