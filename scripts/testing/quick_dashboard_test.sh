#!/bin/bash

# Quick Dashboard Feature Test Runner
# Focus on just the dashboard tests for faster execution

echo "🏠 Quick Dashboard Feature Tests"
echo "================================"

# Check frontend
if curl -s http://localhost:3002 > /dev/null; then
    echo "✅ Frontend ready on http://localhost:3002"
else
    echo "❌ Frontend not accessible"
    exit 1
fi

echo ""
echo "🎯 Running Dashboard Tests (you can watch!)..."

# Run just the dashboard tests
npx playwright test test_dashboard_features.spec.js --headed --workers=1 --timeout=30000 --reporter=list

echo ""
echo "✅ Dashboard tests completed!"
