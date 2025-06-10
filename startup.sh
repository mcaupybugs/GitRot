#!/bin/bash
# Azure App Service startup script for GitRot with Git installation

echo "🔵 Azure App Service: GitRot Startup Configuration"

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

pip install -r requirements.txt

# Azure best practice: Start Streamlit application
echo "🚀 Starting GitRot Streamlit application..."
python -m streamlit run entry_page.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.fileWatcherType none