#!/bin/bash

# GitRot Docker Helper Script
# Simplifies Docker Compose operations for GitRot project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project name
PROJECT_NAME="gitrot"

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker and Docker Compose are installed
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

# Build services
build() {
    log_info "Building GitRot services..."
    docker-compose build "$@"
    log_success "Build completed"
}

# Start services
start() {
    log_info "Starting GitRot services..."
    docker-compose up -d "$@"
    log_success "Services started"
    show_status
}

# Start services with build
up() {
    log_info "Building and starting GitRot services..."
    docker-compose up -d --build "$@"
    log_success "Services are up and running"
    show_status
}

# Stop services
stop() {
    log_info "Stopping GitRot services..."
    docker-compose stop "$@"
    log_success "Services stopped"
}

# Restart services
restart() {
    log_info "Restarting GitRot services..."
    docker-compose restart "$@"
    log_success "Services restarted"
    show_status
}

# Stop and remove services
down() {
    log_info "Stopping and removing GitRot services..."
    docker-compose down "$@"
    log_success "Services removed"
}

# Show service status
status() {
    show_status
}

show_status() {
    log_info "Service status:"
    docker-compose ps
    echo ""
    log_info "Service URLs:"
    echo -e "  ${GREEN}Frontend:${NC} http://localhost:3000"
    echo -e "  ${GREEN}Backend API:${NC} http://localhost:8000"
    echo -e "  ${GREEN}Backend Health:${NC} http://localhost:8000/health"
}

# Show logs
logs() {
    if [ $# -eq 0 ]; then
        log_info "Showing logs for all services..."
        docker-compose logs -f
    else
        log_info "Showing logs for service: $1"
        docker-compose logs -f "$1"
    fi
}

# Show recent logs
logs_tail() {
    local lines=${1:-100}
    if [ $# -le 1 ]; then
        log_info "Showing last $lines lines for all services..."
        docker-compose logs --tail="$lines"
    else
        local service=$2
        log_info "Showing last $lines lines for service: $service"
        docker-compose logs --tail="$lines" "$service"
    fi
}

# Execute command in service container
exec_service() {
    if [ $# -lt 2 ]; then
        log_error "Usage: exec <service> <command>"
        exit 1
    fi
    
    local service=$1
    shift
    log_info "Executing command in $service: $*"
    docker-compose exec "$service" "$@"
}

# Open shell in service container
shell() {
    local service=${1:-backend}
    log_info "Opening shell in $service container..."
    docker-compose exec "$service" /bin/bash 2>/dev/null || docker-compose exec "$service" /bin/sh
}

# Clean up everything (containers, images, volumes)
clean() {
    log_warning "This will remove all GitRot containers, images, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up GitRot resources..."
        docker-compose down -v --rmi all --remove-orphans
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Health check
health() {
    log_info "Checking service health..."
    
    # Check backend health
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend is healthy"
    else
        log_error "Backend is not responding"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        log_success "Frontend is healthy"
    else
        log_error "Frontend is not responding"
    fi
}

# Show help
help() {
    cat << EOF
GitRot Docker Helper Script

USAGE:
    $0 <command> [options]

COMMANDS:
    build           Build all services
    start           Start services (without building)
    up              Build and start services
    stop            Stop services
    restart         Restart services
    down            Stop and remove services
    status          Show service status and URLs
    logs [service]  Show logs (all services or specific service)
    tail [lines] [service]  Show recent logs (default: 100 lines)
    exec <service> <cmd>    Execute command in service container
    shell [service] Open shell in service container (default: backend)
    health          Check service health
    clean           Remove all containers, images, and volumes
    help            Show this help message

EXAMPLES:
    $0 up                   # Build and start all services
    $0 logs backend         # Show backend logs
    $0 tail 50 frontend     # Show last 50 lines of frontend logs
    $0 exec backend ls -la  # List files in backend container
    $0 shell frontend       # Open shell in frontend container
    $0 clean                # Clean up everything

SERVICE URLs:
    Frontend:      http://localhost:3000
    Backend API:   http://localhost:8000
    Backend Health: http://localhost:8000/health
EOF
}

# Main command handling
main() {
    # Check dependencies first
    check_dependencies
    
    case "${1:-help}" in
        build)
            shift
            build "$@"
            ;;
        start)
            shift
            start "$@"
            ;;
        up)
            shift
            up "$@"
            ;;
        stop)
            shift
            stop "$@"
            ;;
        restart)
            shift
            restart "$@"
            ;;
        down)
            shift
            down "$@"
            ;;
        status)
            status
            ;;
        logs)
            shift
            logs "$@"
            ;;
        tail)
            shift
            logs_tail "$@"
            ;;
        exec)
            shift
            exec_service "$@"
            ;;
        shell)
            shift
            shell "$@"
            ;;
        health)
            health
            ;;
        clean)
            clean
            ;;
        help|--help|-h)
            help
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
