#!/bin/bash

# Comprehensive Test Runner for Pixel AI Creator
# Pre-deployment validation for Linode deployment

set -e  # Exit on any error

echo "🚀 Pixel AI Creator - Comprehensive Test Suite"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to log test results
log_test_result() {
    local test_name="$1"
    local result="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✅ $test_name${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ $test_name${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Function to run command and capture result
run_test() {
    local test_name="$1"
    local command="$2"
    
    echo -e "${BLUE}🔍 Running: $test_name${NC}"
    
    if eval "$command" > /dev/null 2>&1; then
        log_test_result "$test_name" "PASS"
        return 0
    else
        log_test_result "$test_name" "FAIL"
        return 1
    fi
}

# Check prerequisites
echo -e "${YELLOW}📋 Checking Prerequisites...${NC}"

# Check if Python is installed
if command -v python3 &> /dev/null; then
    log_test_result "Python 3 Installation" "PASS"
else
    log_test_result "Python 3 Installation" "FAIL"
    echo "Error: Python 3 is required"
    exit 1
fi

# Check if Docker is installed and running
if command -v docker &> /dev/null && docker info &> /dev/null; then
    log_test_result "Docker Installation & Service" "PASS"
else
    log_test_result "Docker Installation & Service" "FAIL"
    echo "Error: Docker is required and must be running"
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    log_test_result "Docker Compose Installation" "PASS"
else
    log_test_result "Docker Compose Installation" "FAIL"
    echo "Error: Docker Compose is required"
    exit 1
fi

# Set up test environment
echo -e "\n${YELLOW}🔧 Setting Up Test Environment...${NC}"

# Navigate to project directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Install test dependencies
echo "Installing test dependencies..."
if pip install -r api/requirements-test.txt > /dev/null 2>&1; then
    log_test_result "Test Dependencies Installation" "PASS"
else
    log_test_result "Test Dependencies Installation" "FAIL"
fi

# Check environment variables
echo -e "\n${YELLOW}🌍 Environment Validation...${NC}"

# Required environment variables
required_vars=("OPENAI_API_KEY" "SECRET_KEY" "DATABASE_URL" "REDIS_URL")

for var in "${required_vars[@]}"; do
    if [ -n "${!var}" ]; then
        log_test_result "Environment Variable: $var" "PASS"
    else
        log_test_result "Environment Variable: $var" "FAIL"
        echo -e "${YELLOW}⚠️  Warning: $var is not set${NC}"
    fi
done

# Configuration validation
echo -e "\n${YELLOW}📁 Configuration Validation...${NC}"

# Check if key files exist
key_files=(
    "docker-compose.yml"
    "api/main.py"
    "api/core/config.py"
    "api/core/database.py"
    "api/requirements.txt"
)

for file in "${key_files[@]}"; do
    if [ -f "$file" ]; then
        log_test_result "Key File: $file" "PASS"
    else
        log_test_result "Key File: $file" "FAIL"
    fi
done

# Docker configuration tests
echo -e "\n${YELLOW}🐳 Docker Configuration Tests...${NC}"

# Validate docker-compose.yml
run_test "Docker Compose Configuration Syntax" "docker-compose config"

# Test Docker builds (without running)
run_test "API Dockerfile Syntax" "docker build -f docker/api/Dockerfile api --dry-run 2>/dev/null || docker build -f docker/api/Dockerfile api -t pixel-test-api --no-cache > /dev/null"

# Code quality tests
echo -e "\n${YELLOW}🔍 Code Quality Tests...${NC}"

# Python syntax check
run_test "Python Syntax Check" "python3 -m py_compile api/main.py"

# Import validation
run_test "Python Import Validation" "cd api && python3 -c 'import main; print(\"Imports successful\")'"

# Linting (if available)
if command -v flake8 &> /dev/null; then
    run_test "Code Linting (flake8)" "flake8 api/ --max-line-length=88 --ignore=E501,W503"
fi

# Security checks
echo -e "\n${YELLOW}🔒 Security Validation...${NC}"

# Check for hardcoded secrets (basic)
if ! grep -r "sk-[a-zA-Z0-9]" api/ > /dev/null 2>&1; then
    log_test_result "No Hardcoded API Keys" "PASS"
else
    log_test_result "No Hardcoded API Keys" "FAIL"
    echo -e "${YELLOW}⚠️  Potential hardcoded API keys found${NC}"
fi

# Check for SQL injection patterns (basic)
if ! grep -r "execute.*%" api/ > /dev/null 2>&1; then
    log_test_result "SQL Injection Prevention" "PASS"
else
    log_test_result "SQL Injection Prevention" "FAIL"
    echo -e "${YELLOW}⚠️  Potential SQL injection patterns found${NC}"
fi

# Unit tests
echo -e "\n${YELLOW}🧪 Unit Tests...${NC}"

if [ -d "api/tests" ] && [ -n "$(ls -A api/tests)" ]; then
    # Run unit tests
    cd api
    
    # Basic API tests
    if python3 -m pytest tests/test_api.py -v --tb=short > /dev/null 2>&1; then
        log_test_result "API Unit Tests" "PASS"
    else
        log_test_result "API Unit Tests" "FAIL"
    fi
    
    # Service tests
    if python3 -m pytest tests/test_services.py -v --tb=short > /dev/null 2>&1; then
        log_test_result "Service Unit Tests" "PASS"
    else
        log_test_result "Service Unit Tests" "FAIL"
    fi
    
    # Production readiness tests
    if python3 -m pytest tests/test_production.py -v --tb=short > /dev/null 2>&1; then
        log_test_result "Production Readiness Tests" "PASS"
    else
        log_test_result "Production Readiness Tests" "FAIL"
    fi
    
    cd ..
else
    log_test_result "Unit Tests Directory" "FAIL"
    echo -e "${YELLOW}⚠️  No tests found in api/tests directory${NC}"
fi

# Integration tests (with Docker)
echo -e "\n${YELLOW}🔗 Integration Tests...${NC}"

# Start services for integration testing
echo "Starting Docker services for integration tests..."
if docker-compose up -d > /dev/null 2>&1; then
    log_test_result "Docker Services Startup" "PASS"
    
    # Wait for services to be ready
    sleep 30
    
    # Test API health endpoint
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_test_result "API Health Endpoint" "PASS"
    else
        log_test_result "API Health Endpoint" "FAIL"
    fi
    
    # Test database connectivity
    if docker exec pixel-postgres pg_isready -U pixel_user > /dev/null 2>&1; then
        log_test_result "Database Connectivity" "PASS"
    else
        log_test_result "Database Connectivity" "FAIL"
    fi
    
    # Test Redis connectivity
    if docker exec pixel-redis redis-cli ping > /dev/null 2>&1; then
        log_test_result "Redis Connectivity" "PASS"
    else
        log_test_result "Redis Connectivity" "FAIL"
    fi
    
    # Clean up
    echo "Stopping Docker services..."
    docker-compose down > /dev/null 2>&1
    
else
    log_test_result "Docker Services Startup" "FAIL"
fi

# Performance validation
echo -e "\n${YELLOW}⚡ Performance Validation...${NC}"

# Check system resources
total_memory=$(free -m | awk 'NR==2{printf "%.1f", $2/1024}')
available_disk=$(df -h . | awk 'NR==2{print $4}')

echo "System Resources:"
echo "  Memory: ${total_memory}GB"
echo "  Disk: ${available_disk} available"

if (( $(echo "$total_memory >= 2.0" | bc -l) )); then
    log_test_result "Minimum Memory Requirements" "PASS"
else
    log_test_result "Minimum Memory Requirements" "FAIL"
    echo -e "${YELLOW}⚠️  Recommended: 2GB+ RAM for production${NC}"
fi

# Deployment readiness
echo -e "\n${YELLOW}🚀 Deployment Readiness...${NC}"

# Check for production configurations
if [ -f ".env.example" ]; then
    log_test_result "Environment Template" "PASS"
else
    log_test_result "Environment Template" "FAIL"
fi

# Check for documentation
if [ -f "README.md" ] && [ -f "PROJECT_STATUS.md" ]; then
    log_test_result "Documentation" "PASS"
else
    log_test_result "Documentation" "FAIL"
fi

# Linode-specific checks
echo -e "\n${YELLOW}☁️  Linode Deployment Checks...${NC}"

# Check if configurations are suitable for Linode
if grep -q "restart: unless-stopped" docker-compose.yml; then
    log_test_result "Container Restart Policy" "PASS"
else
    log_test_result "Container Restart Policy" "FAIL"
    echo -e "${YELLOW}⚠️  Consider adding restart policies for production${NC}"
fi

# Check for volume persistence
if grep -q "volumes:" docker-compose.yml; then
    log_test_result "Data Persistence Configuration" "PASS"
else
    log_test_result "Data Persistence Configuration" "FAIL"
fi

# Final summary
echo -e "\n${BLUE}📊 Test Summary${NC}"
echo "================================"
echo -e "Total Tests: ${TOTAL_TESTS}"
echo -e "${GREEN}Passed: ${PASSED_TESTS}${NC}"
echo -e "${RED}Failed: ${FAILED_TESTS}${NC}"

success_rate=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
echo -e "Success Rate: ${success_rate}%"

echo -e "\n${BLUE}🎯 Production Readiness Assessment${NC}"
echo "======================================"

if [ $success_rate -ge 90 ]; then
    echo -e "${GREEN}🎉 EXCELLENT! System is ready for production deployment${NC}"
    echo -e "${GREEN}✅ Ready for Linode deployment${NC}"
    exit 0
elif [ $success_rate -ge 75 ]; then
    echo -e "${YELLOW}⚠️  GOOD: System is mostly ready with minor issues${NC}"
    echo -e "${YELLOW}🔧 Address failed tests before deployment${NC}"
    exit 1
elif [ $success_rate -ge 50 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Significant issues found${NC}"
    echo -e "${RED}❌ Not recommended for production deployment${NC}"
    exit 1
else
    echo -e "${RED}❌ CRITICAL: Major issues found${NC}"
    echo -e "${RED}🚨 Do not deploy to production${NC}"
    exit 1
fi
