#!/bin/bash

# Pixel AI Creator - Root Directory Cleanup Script
# Organizes files and removes temporary artifacts

echo "🧹 Cleaning up Pixel AI Creator root directory..."
echo "=================================================="

# Navigate to project root
cd /home/jc/Documents/ChatBot-Project/Pixel-AI-Creator

# Create backup of current state
echo "📦 Creating backup..."
mkdir -p .cleanup-backup/$(date +%Y%m%d_%H%M%S)
cp -r . .cleanup-backup/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true

# Remove temporary test files from root
echo "🗑️ Removing temporary test files..."
rm -f comprehensive_ai_test.py
rm -f quick-test.py
rm -f minimal_ai_test.py
rm -f simple_ai_test.py
rm -f test-frontend-integration.py
rm -f test-env.py
rm -f test_chromadb_integration.py
rm -f test_chromadb_basic.py
rm -f frontend-backend-integration-success.py
rm -f quick_ai_validation.py
rm -f razorflow_validation.py
rm -f run_integration_tests.py
rm -f test_ai_integration.py
rm -f test_auth.py
rm -f ui_validation.py
rm -f validate_integration.py
rm -f debug-startup.py
rm -f database_schema_validation.py

# Remove temporary configuration files from root
echo "🗑️ Removing temporary config files..."
rm -f requirements-test.txt
rm -f pytest.ini

# Remove temporary directories
echo "🗑️ Removing temporary directories..."
rm -rf ai_test_env/
rm -rf test-env/
rm -rf test_env/
rm -rf venv/
rm -rf .pytest_cache/

# Remove temporary result files
echo "🗑️ Removing temporary result files..."
rm -f frontend_backend_integration_test_results.json
rm -f test-results-postman.json
rm -f test_results_postman.json

# Clean up any Python cache files
echo "🗑️ Removing Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Organize documentation files
echo "📚 Organizing documentation..."
mkdir -p docs/status-reports
mv AUTHENTICATION_SYSTEM_COMPLETE.md docs/status-reports/ 2>/dev/null || true
mv FRONTEND_BACKEND_INTEGRATION_SUCCESS.md docs/status-reports/ 2>/dev/null || true
mv FRONTEND_BACKEND_TESTING_SUCCESS.md docs/status-reports/ 2>/dev/null || true
mv HIGH_PRIORITY_COMPLETION_SUMMARY.md docs/status-reports/ 2>/dev/null || true
mv TEST_REPORT_COMPREHENSIVE.md docs/status-reports/ 2>/dev/null || true
mv TEST_STATUS_REPORT.md docs/status-reports/ 2>/dev/null || true
mv TODO_CRITICAL_DEVELOPMENT.md docs/status-reports/ 2>/dev/null || true

# Keep important documentation in root
echo "📋 Keeping important docs in root..."
# README.md, PROJECT_STATUS.md, DEPLOYMENT_* files stay in root

# Clean up test-results directory
echo "🧪 Cleaning test results..."
if [ -d "test-results" ]; then
    find test-results -type f -mtime +7 -delete 2>/dev/null || true
    find test-results -type d -empty -delete 2>/dev/null || true
fi

echo ""
echo "✅ Root directory cleanup complete!"
echo ""
echo "📁 Current structure:"
ls -la | grep -E "(^d|README|PROJECT|DEPLOYMENT|docker-compose)"
echo ""
echo "📚 Documentation moved to: docs/status-reports/"
echo "🧪 Tests organized in: tests/"
echo "🐳 Docker configs: docker-compose.yml, docker/"
echo "🚀 Scripts organized in: scripts/"
