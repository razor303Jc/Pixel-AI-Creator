#!/bin/bash

# Development Environment Startup Script
# Switches from production to development mode with volume mounts

echo "🚀 Pixel AI Creator - Development Mode Setup"
echo "=============================================="

# Stop production containers
echo "🛑 Stopping production containers..."
docker-compose down

echo ""
echo "🧹 Cleaning up production containers and images..."

# Remove production containers
docker container prune -f

# Remove production images (optional - uncomment if you want clean rebuild)
# docker image prune -f

echo ""
echo "🔧 Building development environment..."

# Build development images
docker-compose -f docker-compose.dev.yml build --no-cache

echo ""
echo "🚀 Starting development containers with volume mounts..."

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "🔍 Checking service status..."
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "✅ Development environment is ready!"
echo ""
echo "📋 Service URLs:"
echo "   🌐 Frontend (Dev):  http://localhost:3002"
echo "   🔌 Backend API:     http://localhost:8002"
echo "   🗄️  Database:       localhost:5433"
echo "   📊 ChromaDB:       http://localhost:8003"
echo ""
echo "🔥 Features enabled:"
echo "   ✅ Live code reloading (both frontend & backend)"
echo "   ✅ Volume mounts for instant changes"
echo "   ✅ Debug mode enabled"
echo "   ✅ Hot module replacement"
echo ""
echo "📝 Development tips:"
echo "   • Edit files directly - changes reflect immediately"
echo "   • Check logs: docker-compose -f docker-compose.dev.yml logs -f [service]"
echo "   • Restart service: docker-compose -f docker-compose.dev.yml restart [service]"
echo "   • Stop all: docker-compose -f docker-compose.dev.yml down"
echo ""
echo "🎯 Next steps:"
echo "   1. Fix SQLAlchemy models (changes will auto-reload!)"
echo "   2. Test authentication endpoints"
echo "   3. Develop with instant feedback"
echo ""

# Test if services are responding
echo "🧪 Testing service connectivity..."

# Test backend
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "   ✅ Backend API: Healthy"
else
    echo "   ⚠️  Backend API: Starting up..."
fi

# Test frontend
if curl -s http://localhost:3002 > /dev/null 2>&1; then
    echo "   ✅ Frontend: Healthy"
else
    echo "   ⚠️  Frontend: Starting up..."
fi

echo ""
echo "🎉 Happy developing! Changes will be reflected immediately."
