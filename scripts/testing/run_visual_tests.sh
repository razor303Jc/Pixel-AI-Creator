#!/bin/bash

# Visual Playwright Test Runner
# Run tests in headed mode so you can watch them execute

echo "🎭 Starting Visual Playwright Tests for Main App Features"
echo "========================================================"

# Ensure frontend is running
echo "🔍 Checking if frontend is accessible..."
if curl -s http://localhost:3002 > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3002"
else
    echo "❌ Frontend not accessible on http://localhost:3002"
    echo "💡 Make sure Docker containers are running with: docker-compose up -d"
    exit 1
fi

# Create test reports directory
mkdir -p test-reports/screenshots

echo ""
echo "🚀 Starting Playwright tests in HEADED mode (you can watch them!)..."
echo "📺 Browser windows will open showing the tests in action"
echo ""

# Run main app features test with headed browser
echo "🎯 Running Main App Features Tests..."
npx playwright test test_main_app_features.spec.js --headed --workers=1 --timeout=60000

echo ""
echo "🎯 Running Dashboard Specific Tests..."
npx playwright test test_dashboard_features.spec.js --headed --workers=1 --timeout=60000

echo ""
echo "📊 Generating HTML Report..."
npx playwright show-report

echo ""
echo "✅ Visual testing completed!"
echo "📁 Screenshots saved to: test-reports/screenshots/"
echo "📋 Full HTML report available at: test-reports/playwright-html/index.html"
echo ""
echo "🎭 Thanks for watching the tests in action!"
