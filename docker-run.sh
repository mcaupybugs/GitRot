#!/bin/bash

# GitRot Docker Run Script
# Easy Docker management for GitRot application

set -e

echo "🚀 GitRot Docker Run Script"
echo "============================"

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  up         Start the application"
    echo "  down       Stop the application"
    echo "  logs       View application logs"
    echo "  restart    Restart the application"
    echo "  build      Build Docker images"
    echo "  status     Show container status"
    echo "  clean      Remove containers and images"
    echo ""
    echo "Options:"
    echo "  -d, --dev      Use development configuration"
    echo "  -p, --prod     Use production configuration (default)"
    echo "  -f, --follow   Follow logs (use with logs command)"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 up              # Start production environment"
    echo "  $0 --dev up        # Start development environment"
    echo "  $0 logs --follow   # Follow application logs"
    echo "  $0 restart         # Restart the application"
}

# Default values
MODE="prod"
FOLLOW_LOGS=false
COMMAND=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dev)
            MODE="dev"
            shift
            ;;
        -p|--prod)
            MODE="prod"
            shift
            ;;
        -f|--follow)
            FOLLOW_LOGS=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        up|down|logs|restart|build|status|clean)
            COMMAND="$1"
            shift
            ;;
        *)
            echo "Unknown option or command: $1"
            show_usage
            exit 1
            ;;
    esac
done

# If no command provided, show usage
if [[ -z "$COMMAND" ]]; then
    echo "Error: No command specified."
    show_usage
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set Docker Compose profile based on mode
if [[ "$MODE" == "dev" ]]; then
    COMPOSE_ARGS="--profile dev"
    SERVICE_NAME="gitrot-dev"
else
    COMPOSE_ARGS=""
    SERVICE_NAME="gitrot"
fi

# Execute commands
case $COMMAND in
    up)
        echo "🚀 Starting GitRot in $MODE mode..."
        if [[ "$MODE" == "dev" ]]; then
            echo "📝 Development mode: Hot reload enabled"
            docker-compose $COMPOSE_ARGS up $SERVICE_NAME
        else
            echo "🏭 Production mode: Optimized build"
            docker-compose up -d $SERVICE_NAME
            echo "✅ GitRot started successfully!"
            echo "🌐 Frontend: http://localhost:3000"
            echo "🔗 Backend API: http://localhost:8000"
            echo "📊 Health Check: http://localhost:8000/health"
        fi
        ;;
    down)
        echo "🛑 Stopping GitRot..."
        docker-compose down
        echo "✅ GitRot stopped successfully!"
        ;;
    logs)
        echo "📋 Viewing GitRot logs..."
        if [[ "$FOLLOW_LOGS" == true ]]; then
            docker-compose logs -f $SERVICE_NAME
        else
            docker-compose logs $SERVICE_NAME
        fi
        ;;
    restart)
        echo "🔄 Restarting GitRot..."
        docker-compose restart $SERVICE_NAME
        echo "✅ GitRot restarted successfully!"
        ;;
    build)
        echo "🏗️  Building GitRot Docker images..."
        if [[ "$MODE" == "dev" ]]; then
            docker-compose build $SERVICE_NAME
        else
            docker-compose build $SERVICE_NAME
        fi
        echo "✅ Build completed successfully!"
        ;;
    status)
        echo "📊 GitRot Container Status:"
        docker-compose ps
        echo ""
        echo "🐳 Docker Images:"
        docker images | grep -E "(gitrot|REPOSITORY)"
        ;;
    clean)
        echo "🧹 Cleaning up GitRot containers and images..."
        read -p "Are you sure you want to remove all GitRot containers and images? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down --rmi all --volumes --remove-orphans
            docker system prune -f
            echo "✅ Cleanup completed!"
        else
            echo "❌ Cleanup cancelled."
        fi
        ;;
    *)
        echo "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac
