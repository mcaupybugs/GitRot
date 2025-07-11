#!/bin/bash
# Azure App Service startup script for GitRot with Git installation
# Uses UV for faster Python dependency management with pip fallback

echo "🔵 Azure App Service: GitRot Startup Configuration (with UV)"

# Azure best practice: Update package lists
apt-get update -q

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

# Install UV if not available
if ! command -v uv &> /dev/null; then
    echo "⚡ Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "🐍 Installing Python dependencies with UV..."
uv sync --frozen || {
    echo "❌ Failed to install Python dependencies with UV, falling back to pip..."
    pip install -r requirements.txt || {
        echo "❌ Failed to install Python dependencies"
        exit 1
    }
}

# Azure best practice: Start the FastAPI application with proper configuration
echo "🌐 Starting FastAPI server with UV..."

# Use the PORT environment variable set by Azure, default to 8000
PORT=${PORT:-8000}

# Try to use UV first, fallback to direct uvicorn if UV not available
if command -v uv &> /dev/null; then
    # Start Uvicorn with UV and production settings
    uv run uvicorn fastapi_app:app \
        --host 0.0.0.0 \
        --port $PORT \
        --workers 1 \
        --log-level info \
        --access-log \
        --no-use-colors
else
    # Fallback to direct uvicorn
    uvicorn fastapi_app:app \
        --host 0.0.0.0 \
        --port $PORT \
        --workers 1 \
        --log-level info \
        --access-log \
        --no-use-colors
fi

echo "🎯 GitRot FastAPI application started on port $PORT"
