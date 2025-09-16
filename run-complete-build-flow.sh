#!/bin/bash

# Complete Build Flow Test Runner - Single Sequential Test
# This script runs the complete build flow as a single test case

echo "🚀 Complete Build Flow Test - Sequential Version"
echo "================================================"

# Set environment variables
export NODE_ENV=test
export TEST_ENV=true

# Ensure test results directory exists
mkdir -p test-results

# Run the complete build flow test (single sequential test)
echo "🎯 Running Complete Build Flow Test..."
npx playwright test tests/complete-build-flow-single.spec.js \
  --config=playwright-build-flow.config.js \
  --reporter=json \
  --output=test-results/ \
  --timeout=180000 \
  --retries=0 \
  --workers=1

# Capture exit code
EXIT_CODE=$?

echo ""
echo "📊 Test Results Summary"
echo "======================"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Complete build flow test passed successfully!"
else
    echo "❌ Complete build flow test failed (exit code: $EXIT_CODE)"
fi

echo ""
echo "🔍 Recent test results:"
ls -la test-results/ | tail -5

echo ""
echo "🎯 Test Run Complete"
echo "==================="
echo "Exit Code: $EXIT_CODE"
echo "Timestamp: $(date)"

exit $EXIT_CODE