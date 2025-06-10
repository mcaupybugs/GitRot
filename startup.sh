#!/bin/bash
# Azure App Service startup script for GitRot

echo "🔵 Azure App Service: GitRot Startup Configuration"

# Azure best practice: Install Git if not present
if ! command -v git &> /dev/null; then
    echo "📦 Installing Git on Azure App Service..."
    apt-get update -y
    apt-get install -y git
    echo "✅ Git installation completed"
else
    echo "✅ Git already available"
fi

# Azure deployment: Set Git environment variable
export GIT_PYTHON_REFRESH=quiet
export GIT_PYTHON_GIT_EXECUTABLE=$(which git)

echo "🔍 Git version: $(git --version)"
echo "📍 Git path: $(which git)"

# Azure best practice: Start Streamlit application
echo "🚀 Starting GitRot Streamlit application..."
python -m streamlit run entry_page.py --server.port $PORT --server.address 0.0.0.0 --server.headless true