#!/bin/bash

echo "🔍 Pre-Test Environment Verification"
echo "====================================="

# Check if backend is running
echo "📡 Checking backend status..."
if curl -f http://localhost:8002 &>/dev/null; then
    echo "✅ Backend is running on port 8002"
else
    echo "❌ Backend is not responding on port 8002"
    echo "💡 Try starting with: docker-compose up -d"
fi

# Check if frontend is running
echo "🌐 Checking frontend status..."
if curl -f http://localhost:3002 &>/dev/null; then
    echo "✅ Frontend is running on port 3002"
else
    echo "❌ Frontend is not responding on port 3002"
    echo "💡 Try starting the frontend with: cd frontend && npm start"
fi

# Check database connection (if we can reach the API)
echo "🗄️ Checking database and test user..."
if curl -f http://localhost:8002 &>/dev/null; then
    echo "📋 Test Account Details:"
    echo "   Email: jc@razorflow-ai.com"
    echo "   Password: Password123!"
    echo "   Admin Email: admin@razorflow-ai.com" 
    echo "   Admin Password: AdminPass123!"
    echo "   Client Email: client@razorflow-ai.com"
    echo "   Client Password: ClientPass123!"
else
    echo "⚠️ Cannot verify database - backend not responding"
fi

# Check if Playwright is available
echo "🎭 Checking Playwright availability..."
if command -v npx >/dev/null 2>&1; then
    echo "✅ npx is available"
    if npx playwright --version &>/dev/null; then
        echo "✅ Playwright is installed and ready"
    else
        echo "❌ Playwright not found"
        echo "💡 Install with: npx playwright install"
    fi
else
    echo "❌ npx not found"
    echo "💡 Install Node.js and npm first"
fi

echo ""
echo "🚀 Ready to run comprehensive test:"
echo "   npx playwright test tests/comprehensive-assistant-creation-build-test.spec.js --headed"
echo ""