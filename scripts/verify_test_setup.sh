#!/bin/bash

# Test Framework Verification Script
echo "🔍 Verifying Test Framework Setup..."
echo "=================================="

# Check Python virtual environment
echo "📋 Checking Python test environment..."
if [ -d "api/test_env" ]; then
    echo "✅ Test virtual environment exists"
    cd api
    source test_env/bin/activate
    
    # Check key dependencies
    echo "🔍 Verifying key dependencies..."
    python -c "import pytest; print('✅ pytest installed')" 2>/dev/null || echo "❌ pytest missing"
    python -c "import httpx; print('✅ httpx installed')" 2>/dev/null || echo "❌ httpx missing"
    python -c "import fastapi; print('✅ fastapi installed')" 2>/dev/null || echo "❌ fastapi missing"
    python -c "import sqlalchemy; print('✅ sqlalchemy installed')" 2>/dev/null || echo "❌ sqlalchemy missing"
    python -c "import openai; print('✅ openai installed')" 2>/dev/null || echo "❌ openai missing"
    
    cd ..
else
    echo "❌ Test virtual environment not found"
fi

# Check Node.js dependencies
echo ""
echo "📦 Checking Node.js dependencies..."
if [ -d "frontend/node_modules" ]; then
    echo "✅ Frontend node_modules exists"
else
    echo "❌ Frontend dependencies missing"
fi

# Check Newman
echo ""
echo "📮 Checking Newman (Postman CLI)..."
if command -v newman &> /dev/null; then
    echo "✅ Newman is installed: $(newman --version)"
else
    echo "❌ Newman not found"
fi

# Check Playwright
echo ""
echo "🎭 Checking Playwright..."
cd frontend
if npx playwright --version &> /dev/null; then
    echo "✅ Playwright is available: $(npx playwright --version)"
else
    echo "❌ Playwright not found"
fi
cd ..

# Check test files
echo ""
echo "📁 Checking test files..."
if [ -f "tests/test_ui_components_playwright.spec.js" ]; then
    echo "✅ Playwright UI tests found"
else
    echo "❌ Playwright tests missing"
fi

if [ -f "tests/AI_RazorFlow_API_Tests.postman_collection.json" ]; then
    echo "✅ Postman API tests found"
else
    echo "❌ Postman tests missing"
fi

if [ -f "tests/test_backend_comprehensive.py" ]; then
    echo "✅ Pytest backend tests found"
else
    echo "❌ Pytest tests missing"
fi

# Check configuration files
echo ""
echo "⚙️  Checking configuration files..."
if [ -f "frontend/playwright.config.js" ]; then
    echo "✅ Playwright config found"
else
    echo "❌ Playwright config missing"
fi

if [ -f "scripts/run_comprehensive_tests.sh" ]; then
    echo "✅ Test runner script found"
else
    echo "❌ Test runner script missing"
fi

echo ""
echo "🎯 Setup Verification Complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Start your frontend: cd frontend && npm run dev"
echo "  2. Start your backend: cd api && python main.py"
echo "  3. Run tests: ./scripts/run_comprehensive_tests.sh"
