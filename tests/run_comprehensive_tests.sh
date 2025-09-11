#!/bin/bash

# Comprehensive Test Runner for Pixel-AI-Creator
# Runs both Frontend (Playwright) and Backend (Postman) tests
# Author: AI Assistant
# Version: 1.0

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/jc/Documents/ChatBot-Project/Pixel-AI-Creator"
TEST_DIR="$PROJECT_DIR/tests"
REPORTS_DIR="$PROJECT_DIR/test-reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# URLs
FRONTEND_URL="http://localhost:3002"
API_URL="http://localhost:8002"

# Test files
PLAYWRIGHT_TEST="test_frontend_comprehensive_playwright.spec.js"
POSTMAN_COLLECTION="Pixel-AI-Creator-Complete-API-Tests.postman_collection.json"

echo -e "${BLUE}🚀 Pixel-AI-Creator Comprehensive Test Suite${NC}"
echo -e "${BLUE}===============================================${NC}"
echo "Timestamp: $(date)"
echo "Project Directory: $PROJECT_DIR"
echo ""

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Function to check if service is running
check_service() {
    local url=$1
    local service_name=$2
    
    echo -e "${YELLOW}Checking $service_name at $url...${NC}"
    
    if curl -f -s "$url" > /dev/null 2>&1 || curl -f -s "$url/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name is not responding${NC}"
        return 1
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if check_service "$url" "$service_name"; then
            return 0
        fi
        
        echo "Attempt $attempt/$max_attempts - waiting 5 seconds..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name failed to start after $max_attempts attempts${NC}"
    return 1
}

# Function to start services
start_services() {
    echo -e "${BLUE}🔧 Starting Services...${NC}"
    cd "$PROJECT_DIR"
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ docker-compose not found${NC}"
        exit 1
    fi
    
    # Start services
    echo "Starting Docker services..."
    docker-compose up -d api frontend postgres redis
    
    # Wait for services to be ready
    wait_for_service "$API_URL/health" "API"
    wait_for_service "$FRONTEND_URL" "Frontend"
    
    echo -e "${GREEN}✅ All services are running${NC}"
}

# Function to install test dependencies
install_dependencies() {
    echo -e "${BLUE}📦 Installing Test Dependencies...${NC}"
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm not found - please install Node.js${NC}"
        exit 1
    fi
    
    # Install Playwright if not already installed
    if ! command -v npx playwright &> /dev/null; then
        echo "Installing Playwright..."
        npm install -g @playwright/test
        npx playwright install
    fi
    
    # Check if newman (Postman CLI) is available
    if ! command -v newman &> /dev/null; then
        echo "Installing Newman (Postman CLI)..."
        npm install -g newman newman-reporter-htmlextra
    fi
    
    echo -e "${GREEN}✅ Dependencies are installed${NC}"
}

# Function to run Playwright tests
run_playwright_tests() {
    echo -e "${BLUE}🎭 Running Frontend Tests (Playwright)...${NC}"
    cd "$TEST_DIR"
    
    local report_file="$REPORTS_DIR/playwright-report-$TIMESTAMP.html"
    
    if [ -f "$PLAYWRIGHT_TEST" ]; then
        echo "Running: $PLAYWRIGHT_TEST"
        
        # Run Playwright tests with HTML reporter
        if npx playwright test "$PLAYWRIGHT_TEST" --reporter=html --output="$REPORTS_DIR/playwright-$TIMESTAMP"; then
            echo -e "${GREEN}✅ Playwright tests completed successfully${NC}"
            echo -e "📊 Report: $REPORTS_DIR/playwright-$TIMESTAMP/index.html"
            return 0
        else
            echo -e "${RED}❌ Playwright tests failed${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Playwright test file not found: $PLAYWRIGHT_TEST${NC}"
        return 1
    fi
}

# Function to run Postman tests
run_postman_tests() {
    echo -e "${BLUE}📮 Running API Tests (Postman)...${NC}"
    cd "$TEST_DIR"
    
    local report_file="$REPORTS_DIR/postman-report-$TIMESTAMP.html"
    local json_report="$REPORTS_DIR/postman-results-$TIMESTAMP.json"
    
    if [ -f "$POSTMAN_COLLECTION" ]; then
        echo "Running: $POSTMAN_COLLECTION"
        
        # Run Newman with HTML reporter
        if npx newman run "$POSTMAN_COLLECTION" \
            --reporters htmlextra,json \
            --reporter-htmlextra-export "$report_file" \
            --reporter-json-export "$json_report" \
            --timeout-request 10000 \
            --delay-request 500; then
            echo -e "${GREEN}✅ Postman tests completed successfully${NC}"
            echo -e "📊 HTML Report: $report_file"
            echo -e "📊 JSON Report: $json_report"
            return 0
        else
            echo -e "${RED}❌ Postman tests failed${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Postman collection not found: $POSTMAN_COLLECTION${NC}"
        return 1
    fi
}

# Function to generate summary report
generate_summary() {
    echo -e "${BLUE}📊 Generating Test Summary...${NC}"
    
    local summary_file="$REPORTS_DIR/test-summary-$TIMESTAMP.txt"
    
    cat > "$summary_file" << EOF
Pixel-AI-Creator Test Suite Summary
====================================
Timestamp: $(date)
Test Run ID: $TIMESTAMP

Services Tested:
- Frontend: $FRONTEND_URL
- API: $API_URL

Test Results:
- Playwright (Frontend): ${PLAYWRIGHT_RESULT:-"Not Run"}
- Postman (API): ${POSTMAN_RESULT:-"Not Run"}

Reports Generated:
- Summary: $summary_file
- Playwright: $REPORTS_DIR/playwright-$TIMESTAMP/index.html
- Postman HTML: $REPORTS_DIR/postman-report-$TIMESTAMP.html
- Postman JSON: $REPORTS_DIR/postman-results-$TIMESTAMP.json

Docker Services:
$(docker-compose ps)

System Information:
- OS: $(uname -a)
- Node.js: $(node --version 2>/dev/null || echo "Not installed")
- npm: $(npm --version 2>/dev/null || echo "Not installed")
- Docker: $(docker --version 2>/dev/null || echo "Not installed")
- Docker Compose: $(docker-compose --version 2>/dev/null || echo "Not installed")
EOF

    echo -e "${GREEN}✅ Summary report generated: $summary_file${NC}"
}

# Function to open reports in browser
open_reports() {
    echo -e "${BLUE}🌐 Opening Test Reports...${NC}"
    
    local playwright_report="$REPORTS_DIR/playwright-$TIMESTAMP/index.html"
    local postman_report="$REPORTS_DIR/postman-report-$TIMESTAMP.html"
    
    if command -v xdg-open &> /dev/null; then
        [ -f "$playwright_report" ] && xdg-open "$playwright_report" 2>/dev/null &
        [ -f "$postman_report" ] && xdg-open "$postman_report" 2>/dev/null &
    elif command -v open &> /dev/null; then
        [ -f "$playwright_report" ] && open "$playwright_report" 2>/dev/null &
        [ -f "$postman_report" ] && open "$postman_report" 2>/dev/null &
    else
        echo "Please manually open the report files:"
        [ -f "$playwright_report" ] && echo "- Playwright: $playwright_report"
        [ -f "$postman_report" ] && echo "- Postman: $postman_report"
    fi
}

# Function to cleanup
cleanup() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    # Add any cleanup tasks here if needed
}

# Main execution
main() {
    local run_frontend=true
    local run_api=true
    local start_services_flag=true
    local open_reports_flag=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --frontend-only)
                run_api=false
                shift
                ;;
            --api-only)
                run_frontend=false
                shift
                ;;
            --no-start-services)
                start_services_flag=false
                shift
                ;;
            --open-reports)
                open_reports_flag=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --frontend-only      Run only frontend tests"
                echo "  --api-only          Run only API tests"
                echo "  --no-start-services Don't start Docker services"
                echo "  --open-reports      Open reports in browser"
                echo "  --help              Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Install dependencies
    install_dependencies
    
    # Start services if requested
    if [ "$start_services_flag" = true ]; then
        start_services
    else
        echo -e "${YELLOW}⚠️  Skipping service startup - make sure services are running${NC}"
        check_service "$API_URL/health" "API" || echo -e "${YELLOW}⚠️  API might not be ready${NC}"
        check_service "$FRONTEND_URL" "Frontend" || echo -e "${YELLOW}⚠️  Frontend might not be ready${NC}"
    fi
    
    # Run tests
    local overall_result=0
    
    if [ "$run_frontend" = true ]; then
        if run_playwright_tests; then
            PLAYWRIGHT_RESULT="✅ PASSED"
        else
            PLAYWRIGHT_RESULT="❌ FAILED"
            overall_result=1
        fi
    fi
    
    if [ "$run_api" = true ]; then
        if run_postman_tests; then
            POSTMAN_RESULT="✅ PASSED"
        else
            POSTMAN_RESULT="❌ FAILED"
            overall_result=1
        fi
    fi
    
    # Generate summary
    generate_summary
    
    # Open reports if requested
    if [ "$open_reports_flag" = true ]; then
        open_reports
    fi
    
    # Final summary
    echo ""
    echo -e "${BLUE}📋 Test Run Complete${NC}"
    echo -e "${BLUE}=====================${NC}"
    echo -e "Playwright Tests: ${PLAYWRIGHT_RESULT:-"Skipped"}"
    echo -e "Postman Tests: ${POSTMAN_RESULT:-"Skipped"}"
    echo ""
    
    if [ $overall_result -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed successfully!${NC}"
    else
        echo -e "${RED}💥 Some tests failed. Check the reports for details.${NC}"
    fi
    
    echo -e "📊 Reports available in: $REPORTS_DIR"
    
    # Cleanup
    cleanup
    
    exit $overall_result
}

# Handle interrupts
trap cleanup EXIT

# Run main function with all arguments
main "$@"
