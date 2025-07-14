#!/bin/bash

# GitRot Docker Helper - Quick Setup
# This script sets up convenient aliases for the docker helper

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER_SCRIPT="$SCRIPT_DIR/docker-helper.sh"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}GitRot Docker Helper - Quick Setup${NC}"
echo ""

# Check if the helper script exists
if [ ! -f "$HELPER_SCRIPT" ]; then
    echo "Error: docker-helper.sh not found!"
    exit 1
fi

# Make sure it's executable
chmod +x "$HELPER_SCRIPT"

echo "You can use the helper script in the following ways:"
echo ""
echo -e "${GREEN}1. Direct execution:${NC}"
echo "   $HELPER_SCRIPT <command>"
echo ""
echo -e "${GREEN}2. Create an alias (recommended):${NC}"
echo "   Add this to your ~/.zshrc or ~/.bashrc:"
echo "   alias gitrot='$HELPER_SCRIPT'"
echo ""
echo -e "${GREEN}3. Quick commands available:${NC}"
echo "   • up      - Build and start all services"
echo "   • down    - Stop and remove all services"
echo "   • status  - Show service status"
echo "   • logs    - Show logs"
echo "   • health  - Check service health"
echo "   • clean   - Clean up everything"
echo ""

# Ask if user wants to add alias to their shell config
read -p "Would you like to add the 'gitrot' alias to your ~/.zshrc? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ALIAS_LINE="alias gitrot='$HELPER_SCRIPT'"
    
    # Check if alias already exists
    if grep -q "alias gitrot=" ~/.zshrc 2>/dev/null; then
        echo "Alias already exists in ~/.zshrc"
    else
        echo "" >> ~/.zshrc
        echo "# GitRot Docker Helper" >> ~/.zshrc
        echo "$ALIAS_LINE" >> ~/.zshrc
        echo -e "${GREEN}Alias added to ~/.zshrc${NC}"
        echo "Run 'source ~/.zshrc' or restart your terminal to use the 'gitrot' command"
    fi
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo "Run '$HELPER_SCRIPT help' to see all available commands"
