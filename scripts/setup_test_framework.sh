#!/bin/bash

# Quick Test Setup and Runner for Pixel AI Creator
# Installs dependencies and runs comprehensive test suite

set -e

echo "🚀 Pixel AI Creator - Test Framework Setup"
echo "=========================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Node.js dependencies for frontend and Playwright
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

# Install Playwright browsers
echo "🎭 Setting up Playwright..."
if ! command_exists playwright; then
    npx playwright install
fi
cd ..

# Install Python dependencies for backend testing
echo "🐍 Installing Python test dependencies..."
cd api

# Create virtual environment if it doesn't exist
if [ ! -d "test_env" ]; then
    echo "Creating test virtual environment..."
    python -m venv test_env
fi

# Activate virtual environment
source test_env/bin/activate

# Upgrade pip to avoid dependency resolution issues
pip install --upgrade pip setuptools wheel

# Install dependencies with dependency resolution
echo "Installing test dependencies (this may take a moment)..."
pip install -r requirements-test.txt --upgrade-strategy=eager

echo "✅ Python test dependencies installed successfully"
cd ..

# Install Newman (Postman CLI) globally
echo "📮 Installing Newman for Postman tests..."
if ! command_exists newman; then
    npm install -g newman newman-reporter-html
fi

echo ""
echo "✅ Test framework setup complete!"
echo ""
echo "� Verify installation:"
echo "  ./scripts/verify_test_setup.sh        - Verify all components"
echo ""
echo "�📋 Available Commands:"
echo "  ./scripts/run_comprehensive_tests.sh  - Run all tests"
echo "  cd frontend && npx playwright test     - Run UI tests only"
echo "  newman run tests/AI_RazorFlow_API_Tests.postman_collection.json - Run API tests only"
echo "  cd api && source test_env/bin/activate && python -m pytest ../tests/test_backend_comprehensive.py - Run backend tests only"
echo ""
echo "🎯 To run all tests now:"
echo "  ./scripts/run_comprehensive_tests.sh"
