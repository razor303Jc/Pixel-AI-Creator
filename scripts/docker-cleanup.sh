#!/bin/bash

# Docker Cleanup and Reset Script for Pixel AI Creator Testing
set -e

echo "🧹 Pixel AI Creator - Docker Cleanup & Reset Script"
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to stop and remove containers
cleanup_containers() {
    log_info "Stopping and removing Pixel AI containers..."
    
    # Stop all pixel-related containers
    docker ps -a --filter "name=pixel-" --format "{{.Names}}" | xargs -r docker stop
    docker ps -a --filter "name=pixel-" --format "{{.Names}}" | xargs -r docker rm
    
    # Remove any orphaned containers from docker-compose
    docker-compose -f docker-compose.yml down --remove-orphans 2>/dev/null || true
    docker-compose -f docker-compose.test.yml down --remove-orphans 2>/dev/null || true
}

# Function to remove networks
cleanup_networks() {
    log_info "Cleaning up Docker networks..."
    
    # Remove pixel-related networks
    docker network ls --filter "name=pixel" --format "{{.Name}}" | xargs -r docker network rm 2>/dev/null || true
    
    # Prune unused networks
    docker network prune -f
}

# Function to remove volumes (optional)
cleanup_volumes() {
    if [[ "$1" == "--with-volumes" ]]; then
        log_warn "Removing Docker volumes (this will delete all data)..."
        docker volume ls --filter "name=pixel" --format "{{.Name}}" | xargs -r docker volume rm 2>/dev/null || true
    else
        log_info "Keeping Docker volumes (use --with-volumes to remove them)"
    fi
}

# Function to clean up images
cleanup_images() {
    if [[ "$1" == "--with-images" ]]; then
        log_info "Removing Pixel AI images..."
        docker images --filter "reference=pixel*" --format "{{.Repository}}:{{.Tag}}" | xargs -r docker rmi 2>/dev/null || true
        docker image prune -f
    else
        log_info "Keeping Docker images (use --with-images to remove them)"
    fi
}

# Function to verify cleanup
verify_cleanup() {
    log_info "Verifying cleanup..."
    
    echo "Remaining Pixel containers:"
    docker ps -a --filter "name=pixel-" --format "table {{.Names}}\t{{.Status}}" || echo "None"
    
    echo "Remaining Pixel networks:"
    docker network ls --filter "name=pixel" --format "table {{.Name}}\t{{.Driver}}" || echo "None"
    
    if [[ "$1" == "--with-volumes" ]]; then
        echo "Remaining Pixel volumes:"
        docker volume ls --filter "name=pixel" --format "table {{.Name}}\t{{.Driver}}" || echo "None"
    fi
}

# Function to recreate network
recreate_network() {
    log_info "Recreating test network..."
    
    # Create the test network with specific configuration
    docker network create \
        --driver bridge \
        --subnet=172.20.0.0/16 \
        --ip-range=172.20.240.0/20 \
        pixel-test-network 2>/dev/null || log_warn "Network already exists or couldn't be created"
}

# Main execution
main() {
    echo "Starting Docker cleanup process..."
    
    # Parse arguments
    WITH_VOLUMES=""
    WITH_IMAGES=""
    
    for arg in "$@"; do
        case $arg in
            --with-volumes)
                WITH_VOLUMES="--with-volumes"
                ;;
            --with-images)
                WITH_IMAGES="--with-images"
                ;;
            --help)
                echo "Usage: $0 [--with-volumes] [--with-images]"
                echo "  --with-volumes: Also remove Docker volumes (deletes data)"
                echo "  --with-images: Also remove Docker images"
                exit 0
                ;;
        esac
    done
    
    # Perform cleanup steps
    cleanup_containers
    cleanup_networks
    cleanup_volumes "$WITH_VOLUMES"
    cleanup_images "$WITH_IMAGES"
    
    # Recreate network for testing
    recreate_network
    
    # Verify cleanup
    verify_cleanup "$WITH_VOLUMES"
    
    log_info "Docker cleanup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Run: docker-compose -f docker-compose.test.yml up -d"
    echo "  2. Wait for services to start"
    echo "  3. Run tests: python -m pytest"
}

# Run main function with all arguments
main "$@"
