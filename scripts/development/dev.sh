#!/bin/bash

# Development Helper Commands

case "$1" in
    "start")
        echo "🚀 Starting development environment..."
        docker-compose -f docker-compose.dev.yml up -d
        ;;
    "stop")
        echo "🛑 Stopping development environment..."
        docker-compose -f docker-compose.dev.yml down
        ;;
    "restart")
        echo "🔄 Restarting development environment..."
        docker-compose -f docker-compose.dev.yml restart
        ;;
    "logs")
        if [ -z "$2" ]; then
            echo "📋 Showing all logs..."
            docker-compose -f docker-compose.dev.yml logs -f
        else
            echo "📋 Showing logs for $2..."
            docker-compose -f docker-compose.dev.yml logs -f "$2"
        fi
        ;;
    "build")
        echo "🔨 Rebuilding development containers..."
        docker-compose -f docker-compose.dev.yml build --no-cache
        ;;
    "ps"|"status")
        echo "📊 Development container status..."
        docker-compose -f docker-compose.dev.yml ps
        ;;
    "shell")
        service=${2:-api}
        echo "🐚 Opening shell in $service container..."
        docker-compose -f docker-compose.dev.yml exec "$service" /bin/bash
        ;;
    "test-auth")
        echo "🧪 Testing authentication endpoint..."
        curl -X POST http://localhost:8002/api/auth/register \
          -H "Content-Type: application/json" \
          -d '{"email":"test@dev.com","password":"TestPass123!","first_name":"Dev","last_name":"User"}'
        echo ""
        ;;
    "test-api")
        echo "🧪 Testing API health..."
        curl http://localhost:8002/health
        echo ""
        ;;
    "test-frontend")
        echo "🧪 Testing frontend..."
        curl -I http://localhost:3002
        ;;
    "clean")
        echo "🧹 Cleaning up development environment..."
        docker-compose -f docker-compose.dev.yml down -v
        docker system prune -f
        ;;
    *)
        echo "🛠️  Pixel AI Creator - Development Commands"
        echo "=========================================="
        echo ""
        echo "Usage: ./dev.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  start          Start development environment"
        echo "  stop           Stop development environment"
        echo "  restart        Restart all services"
        echo "  build          Rebuild containers"
        echo "  ps|status      Show container status"
        echo "  logs [service] Show logs (optionally for specific service)"
        echo "  shell [service] Open shell in container (default: api)"
        echo "  test-auth      Test authentication endpoint"
        echo "  test-api       Test API health"
        echo "  test-frontend  Test frontend"
        echo "  clean          Stop and clean up everything"
        echo ""
        echo "Examples:"
        echo "  ./dev.sh start"
        echo "  ./dev.sh logs api"
        echo "  ./dev.sh shell frontend"
        echo "  ./dev.sh test-auth"
        ;;
esac
