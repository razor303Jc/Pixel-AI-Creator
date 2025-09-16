#!/bin/bash

# 🎭 COMPREHENSIVE BUILD FLOW TEST RUNNER
# Runs the complete assistant creation and build process tests

echo "🎯 Starting Comprehensive Build Flow Test Suite"
echo "=================================================="

# Check if required services are running
echo "🔍 Checking required services..."

# Check frontend
if ! curl -s http://localhost:3002 > /dev/null; then
    echo "❌ Frontend not running on localhost:3002"
    echo "   Please start with: cd frontend && npm start"
    exit 1
fi
echo "✅ Frontend is running"

# Check backend  
if ! curl -s http://localhost:8002/api/health > /dev/null 2>&1; then
    echo "❌ Backend not running on localhost:8002"
    echo "   Please start with: docker-compose up -d"
    exit 1
fi
echo "✅ Backend is running"

# Create test results directory
mkdir -p test-results
mkdir -p test-reports

# Set environment variables
export NODE_ENV=test
export PWDEBUG=0
export CI=false

echo ""
echo "🎭 Running Playwright Build Flow Tests..."
echo "==========================================="

# Run the comprehensive test suite
npx playwright test \
    --config=playwright-build-flow.config.js \
    --reporter=list,html,json \
    --output=test-results/ \
    --timeout=120000

TEST_EXIT_CODE=$?

echo ""
echo "📊 Test Results Summary"
echo "======================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed successfully!"
    
    # Show test artifacts
    echo ""
    echo "📁 Generated Test Artifacts:"
    if [ -d "test-results" ]; then
        find test-results -type f -name "*.json" -o -name "*.xml" | head -10
    fi
    
    if [ -d "test-reports" ]; then
        echo "📊 HTML Report: test-reports/build-flow-tests/index.html"
    fi
    
else
    echo "❌ Some tests failed (exit code: $TEST_EXIT_CODE)"
    
    # Show recent error logs
    echo ""
    echo "🔍 Recent test failures:"
    if [ -f "test-results/build-flow-results.json" ]; then
        cat test-results/build-flow-results.json | grep -A 5 -B 5 "failed\|error" | head -20
    fi
fi

echo ""
echo "🎯 Test Run Complete"
echo "==================="
echo "Exit Code: $TEST_EXIT_CODE"
echo "Timestamp: $(date)"

# Optional: Open test report
if [ "$1" == "--open-report" ] && [ -f "test-reports/build-flow-tests/index.html" ]; then
    echo "🌐 Opening test report in browser..."
    if command -v xdg-open > /dev/null; then
        xdg-open test-reports/build-flow-tests/index.html
    elif command -v open > /dev/null; then
        open test-reports/build-flow-tests/index.html
    fi
fi

exit $TEST_EXIT_CODE