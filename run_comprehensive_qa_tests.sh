#!/bin/bash

# COMPREHENSIVE FRONTEND QA TEST RUNNER
# Pixel-AI-Creator - Complete UI/UX Testing Suite
# 
# This script runs comprehensive Playwright tests covering:
# ✅ All Forms & Input Fields
# ✅ All Buttons & Links  
# ✅ All Pages & Navigation
# ✅ Authentication Components
# ✅ Dashboard Features
# ✅ Advanced Authentication (MFA, Social Login, Password Strength)
# ✅ Database Management
# ✅ Chatbot Manager
# ✅ Analytics Dashboard
# ✅ Client Management
# ✅ Performance Monitoring
# ✅ Responsive Design
# ✅ Error Handling
# ✅ Accessibility

set -e

echo "🎯 PIXEL-AI-CREATOR COMPREHENSIVE QA TEST SUITE"
echo "================================================="
echo ""

# Check if frontend and backend are running
echo "🔍 Checking service availability..."

# Check frontend
if curl -s http://localhost:3002/health >/dev/null 2>&1; then
    echo "✅ Frontend service is running (localhost:3002)"
else
    echo "❌ Frontend service is not running on localhost:3002"
    echo "   Please start the frontend service first:"
    echo "   cd /home/jc/Documents/ChatBot-Project/Pixel-AI-Creator && docker-compose up frontend"
    exit 1
fi

# Check backend
if curl -s http://localhost:8002/health >/dev/null 2>&1; then
    echo "✅ Backend service is running (localhost:8002)"
else
    echo "⚠️  Backend service is not running on localhost:8002"
    echo "   Some tests may fail. Consider starting backend:"
    echo "   cd /home/jc/Documents/ChatBot-Project/Pixel-AI-Creator && docker-compose up api"
fi

echo ""

# Create test reports directory
mkdir -p test-reports
echo "📁 Test reports directory: $(pwd)/test-reports"

# Install Playwright browsers if needed
echo "🔧 Ensuring Playwright browsers are installed..."
cd tests
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Playwright dependencies..."
    npm install
fi

# Install browsers
npx playwright install chromium firefox webkit
echo ""

# Run comprehensive QA tests
echo "🚀 Starting Comprehensive Frontend QA Testing..."
echo "   Test Categories:"
echo "   🔐 Authentication System"
echo "   🛡️  Advanced Authentication Features" 
echo "   📊 Dashboard Components"
echo "   🤖 Chatbot Manager"
echo "   👥 Client Management"
echo "   🗄️  Database Management"
echo "   📱 Responsive Design"
echo "   🔄 Error Handling"
echo "   ⚡ Performance Testing"
echo "   ♿ Accessibility Testing"
echo ""

# Set test environment
export NODE_ENV=test
export PLAYWRIGHT_BROWSERS_PATH=0

# Run the comprehensive QA test suite
echo "🧪 Executing Complete QA Test Suite..."
npx playwright test test_frontend_complete_qa.spec.js --reporter=html,json,junit

# Check test results
TEST_EXIT_CODE=$?

echo ""
echo "📊 TEST EXECUTION SUMMARY"
echo "========================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ ALL QA TESTS PASSED SUCCESSFULLY!"
    echo ""
    echo "📋 Test Coverage Verified:"
    echo "   ✅ Login/Registration Forms"
    echo "   ✅ Input Field Validations"  
    echo "   ✅ Button Interactions"
    echo "   ✅ Navigation Links"
    echo "   ✅ Dashboard Components"
    echo "   ✅ Authentication Features"
    echo "   ✅ Responsive Design"
    echo "   ✅ Error Handling"
    echo "   ✅ Performance Benchmarks"
    echo "   ✅ Accessibility Standards"
else
    echo "⚠️  SOME QA TESTS FAILED OR HAD ISSUES"
    echo ""
    echo "📋 Check the detailed reports for specific failures:"
fi

echo ""
echo "📄 DETAILED TEST REPORTS:"
echo "   📊 HTML Report: test-reports/playwright-html/index.html"
echo "   📋 JSON Report: test-reports/playwright-results.json"
echo "   🔍 JUnit Report: test-reports/playwright-junit.xml"
echo ""

# Open HTML report if available
if [ -f "test-reports/playwright-html/index.html" ]; then
    echo "🌐 Opening HTML test report in browser..."
    # Try to open with various browsers
    if command -v google-chrome >/dev/null 2>&1; then
        google-chrome test-reports/playwright-html/index.html &
    elif command -v firefox >/dev/null 2>&1; then
        firefox test-reports/playwright-html/index.html &
    elif command -v chromium-browser >/dev/null 2>&1; then
        chromium-browser test-reports/playwright-html/index.html &
    else
        echo "   Manual access: file://$(pwd)/test-reports/playwright-html/index.html"
    fi
fi

echo ""
echo "📸 VISUAL VERIFICATION:"
echo "   Screenshots saved in: test-reports/"
echo "   - login-form-initial.png"
echo "   - dashboard-layout.png"
echo "   - responsive-*.png (multiple viewports)"
echo "   - performance-loaded.png"
echo "   - final-state-*.png"

echo ""
echo "🎯 QA TESTING COMPLETE!"
echo "   Frontend UI: $(curl -s http://localhost:3002/ | wc -l) lines of HTML served"
echo "   Test Duration: $(date)"
echo "   Exit Code: $TEST_EXIT_CODE"

# Return to original directory
cd ..

exit $TEST_EXIT_CODE
