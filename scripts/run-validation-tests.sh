#!/bin/bash

# PIXEL AI CREATOR - VALIDATION TEST RUNNER
# Comprehensive test script for enhanced registration validation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 PIXEL AI CREATOR - VALIDATION TEST SUITE${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to check if service is running
check_service() {
    local service_name=$1
    local url=$2
    local timeout=30
    local count=0
    
    echo -e "${YELLOW}⏳ Checking $service_name at $url...${NC}"
    
    while [ $count -lt $timeout ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is running${NC}"
            return 0
        fi
        sleep 1
        ((count++))
    done
    
    echo -e "${RED}❌ $service_name is not responding after ${timeout}s${NC}"
    return 1
}

# Function to start services if needed
start_services() {
    echo -e "${BLUE}🚀 Starting services...${NC}"
    
    # Start frontend in development mode
    if ! check_service "Frontend" "http://localhost:3002"; then
        echo -e "${YELLOW}📦 Starting frontend in development mode...${NC}"
        cd frontend
        npm start &
        FRONTEND_PID=$!
        cd ..
        
        # Wait for frontend to be ready
        sleep 10
        check_service "Frontend" "http://localhost:3002"
    fi
    
    # Start backend API
    if ! check_service "API" "http://localhost:8002/health"; then
        echo -e "${YELLOW}🔧 Starting API server...${NC}"
        cd api
        source api_venv/bin/activate
        python main.py &
        API_PID=$!
        cd ..
        
        # Wait for API to be ready
        sleep 5
        check_service "API" "http://localhost:8002/health"
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "${BLUE}📦 Installing test dependencies...${NC}"
    
    # Install Playwright if not already installed
    if ! command -v npx playwright &> /dev/null; then
        echo -e "${YELLOW}⬇️ Installing Playwright...${NC}"
        npm install -D @playwright/test
        npx playwright install
    fi
    
    # Check if browsers are installed
    echo -e "${YELLOW}🌐 Checking browser installations...${NC}"
    npx playwright install chromium firefox webkit
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Function to run validation tests
run_validation_tests() {
    echo -e "${BLUE}🧪 Running validation tests...${NC}"
    
    # Create test results directory
    mkdir -p test-results test-reports/validation-tests
    
    # Run registration validation tests
    echo -e "${YELLOW}📝 Running registration validation tests...${NC}"
    npx playwright test test_registration_validation.spec.js \
        --config=playwright-validation.config.js \
        --reporter=html,json,list
    
    # Run toast notification tests
    echo -e "${YELLOW}🍞 Running toast notification tests...${NC}"
    npx playwright test test_toast_notifications.spec.js \
        --config=playwright-validation.config.js \
        --reporter=html,json,list
}

# Function to run specific test suites
run_specific_tests() {
    case $1 in
        "email")
            echo -e "${YELLOW}📧 Running email validation tests...${NC}"
            npx playwright test test_registration_validation.spec.js \
                --grep "Email Validation Tests" \
                --config=playwright-validation.config.js
            ;;
        "password")
            echo -e "${YELLOW}🔒 Running password validation tests...${NC}"
            npx playwright test test_registration_validation.spec.js \
                --grep "Password Validation Tests" \
                --config=playwright-validation.config.js
            ;;
        "toast")
            echo -e "${YELLOW}🍞 Running toast notification tests...${NC}"
            npx playwright test test_toast_notifications.spec.js \
                --config=playwright-validation.config.js
            ;;
        "mobile")
            echo -e "${YELLOW}📱 Running mobile responsiveness tests...${NC}"
            npx playwright test test_registration_validation.spec.js \
                --grep "Responsive Design Tests" \
                --config=playwright-validation.config.js
            ;;
        "accessibility")
            echo -e "${YELLOW}♿ Running accessibility tests...${NC}"
            npx playwright test test_registration_validation.spec.js \
                --grep "Accessibility Tests" \
                --config=playwright-validation.config.js
            ;;
        *)
            echo -e "${RED}❌ Unknown test suite: $1${NC}"
            echo -e "${YELLOW}Available test suites: email, password, toast, mobile, accessibility${NC}"
            exit 1
            ;;
    esac
}

# Function to generate test report
generate_report() {
    echo -e "${BLUE}📊 Generating test reports...${NC}"
    
    # Open HTML report if available
    if [ -f "test-reports/validation-tests/index.html" ]; then
        echo -e "${GREEN}📄 HTML report generated: test-reports/validation-tests/index.html${NC}"
        
        # Try to open in browser (works on most systems)
        if command -v xdg-open &> /dev/null; then
            xdg-open test-reports/validation-tests/index.html
        elif command -v open &> /dev/null; then
            open test-reports/validation-tests/index.html
        fi
    fi
    
    # Display JSON results summary
    if [ -f "test-results/validation-results.json" ]; then
        echo -e "${GREEN}📄 JSON results saved: test-results/validation-results.json${NC}"
    fi
}

# Function to cleanup
cleanup() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    
    # Kill background processes if we started them
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Set up trap for cleanup on exit
trap cleanup EXIT

# Main execution
main() {
    case ${1:-"all"} in
        "install")
            install_dependencies
            ;;
        "start")
            start_services
            ;;
        "test")
            if [ ! -z "$2" ]; then
                run_specific_tests $2
            else
                run_validation_tests
            fi
            ;;
        "report")
            generate_report
            ;;
        "all")
            install_dependencies
            start_services
            run_validation_tests
            generate_report
            ;;
        "help")
            echo -e "${BLUE}Usage: $0 [command] [options]${NC}"
            echo -e "${YELLOW}Commands:${NC}"
            echo -e "  install    Install test dependencies"
            echo -e "  start      Start services only"
            echo -e "  test       Run validation tests (or specific suite)"
            echo -e "  report     Generate and open test reports"
            echo -e "  all        Run complete test suite (default)"
            echo -e "  help       Show this help message"
            echo -e ""
            echo -e "${YELLOW}Test suites for 'test' command:${NC}"
            echo -e "  email      Email validation tests"
            echo -e "  password   Password validation tests"
            echo -e "  toast      Toast notification tests"
            echo -e "  mobile     Mobile responsiveness tests"
            echo -e "  accessibility  Accessibility tests"
            echo -e ""
            echo -e "${YELLOW}Examples:${NC}"
            echo -e "  $0 all                    # Run complete test suite"
            echo -e "  $0 test email            # Run only email validation tests"
            echo -e "  $0 test password         # Run only password tests"
            echo -e "  $0 start                 # Just start services"
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $1${NC}"
            echo -e "${YELLOW}Use '$0 help' for available commands${NC}"
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"

echo -e "${GREEN}🎉 Validation test script completed!${NC}"