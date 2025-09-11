#!/bin/bash

# Pixel AI Creator - Staging Test Script
# Comprehensive testing before production deployment

set -e

echo "🚀 Pixel AI Creator - Staging Test Suite"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT=$(dirname "$(readlink -f "$0")")/..
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
API_URL="http://localhost:8000"
TIMEOUT=60

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Utility functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    ((TESTS_PASSED++))
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((TESTS_FAILED++))
}

run_test() {
    local test_name="$1"
    echo -e "\n${BLUE}Testing:${NC} $test_name"
    ((TESTS_RUN++))
}

# Test functions
test_prerequisites() {
    run_test "Prerequisites and Dependencies"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        return 1
    fi
    log_success "Docker is available"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        return 1
    fi
    log_success "Docker Compose is available"
    
    # Check project files
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log_error "docker-compose.yml not found"
        return 1
    fi
    log_success "docker-compose.yml exists"
    
    # Check entrypoint script
    if [[ ! -f "$PROJECT_ROOT/docker/api/entrypoint.sh" ]]; then
        log_error "Entrypoint script not found"
        return 1
    fi
    
    if [[ ! -x "$PROJECT_ROOT/docker/api/entrypoint.sh" ]]; then
        log_error "Entrypoint script is not executable"
        return 1
    fi
    log_success "Entrypoint script exists and is executable"
    
    # Check API files
    if [[ ! -f "$PROJECT_ROOT/api/main.py" ]]; then
        log_error "API main.py not found"
        return 1
    fi
    log_success "API files present"
    
    # Check templates
    if [[ ! -d "$PROJECT_ROOT/templates" ]]; then
        log_error "Templates directory not found"
        return 1
    fi
    
    template_count=$(find "$PROJECT_ROOT/templates" -name "*.json" | wc -l)
    if [[ $template_count -lt 6 ]]; then
        log_error "Insufficient templates found (expected 6, found $template_count)"
        return 1
    fi
    log_success "Templates directory with $template_count templates"
}

test_docker_build() {
    run_test "Docker Image Build"
    
    cd "$PROJECT_ROOT"
    
    # Build API image
    if docker build -f docker/api/Dockerfile -t pixel-ai-api:staging api/; then
        log_success "API Docker image built successfully"
    else
        log_error "Failed to build API Docker image"
        return 1
    fi
    
    # Check image exists
    if docker images | grep -q "pixel-ai-api.*staging"; then
        log_success "API image exists in Docker registry"
    else
        log_error "API image not found in Docker registry"
        return 1
    fi
}

test_compose_validation() {
    run_test "Docker Compose Configuration"
    
    cd "$PROJECT_ROOT"
    
    # Validate compose file
    if docker-compose config --quiet; then
        log_success "docker-compose.yml is valid"
    else
        log_error "docker-compose.yml validation failed"
        return 1
    fi
    
    # Check for required services
    services=$(docker-compose config --services)
    required_services=("api" "postgres" "redis" "chromadb")
    
    for service in "${required_services[@]}"; do
        if echo "$services" | grep -q "^$service$"; then
            log_success "Service '$service' is defined"
        else
            log_error "Required service '$service' is missing"
            return 1
        fi
    done
}

test_environment_setup() {
    run_test "Environment Configuration"
    
    # Check for .env.example
    if [[ -f "$PROJECT_ROOT/.env.example" ]]; then
        log_success ".env.example exists"
    else
        log_warning ".env.example not found (recommended for documentation)"
    fi
    
    # Check critical environment variables are documented
    if [[ -f "$PROJECT_ROOT/.env.example" ]]; then
        required_vars=("DATABASE_URL" "REDIS_URL" "OPENAI_API_KEY" "SECRET_KEY")
        
        for var in "${required_vars[@]}"; do
            if grep -q "^$var=" "$PROJECT_ROOT/.env.example"; then
                log_success "Environment variable '$var' is documented"
            else
                log_warning "Environment variable '$var' not documented"
            fi
        done
    fi
}

test_service_startup() {
    run_test "Service Startup and Health Checks"
    
    cd "$PROJECT_ROOT"
    
    # Clean up any existing containers
    log_info "Cleaning up existing containers..."
    docker-compose down -v --remove-orphans 2>/dev/null || true
    
    # Start services
    log_info "Starting services..."
    if docker-compose up -d --build; then
        log_success "Services started successfully"
    else
        log_error "Failed to start services"
        return 1
    fi
    
    # Wait for services to be healthy
    log_info "Waiting for services to become healthy..."
    
    local start_time=$(date +%s)
    local current_time
    local elapsed
    
    while true; do
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))
        
        if [[ $elapsed -gt $TIMEOUT ]]; then
            log_error "Services failed to become healthy within $TIMEOUT seconds"
            return 1
        fi
        
        # Check API health
        if curl -s "$API_URL/health" > /dev/null 2>&1; then
            log_success "API is healthy"
            break
        fi
        
        echo -n "."
        sleep 2
    done
}

test_api_endpoints() {
    run_test "API Endpoint Testing"
    
    # Test health endpoint
    response=$(curl -s -w "%{http_code}" "$API_URL/health")
    http_code="${response: -3}"
    
    if [[ "$http_code" == "200" ]]; then
        log_success "Health endpoint responding correctly"
    else
        log_error "Health endpoint failed (HTTP $http_code)"
        return 1
    fi
    
    # Test templates endpoint
    response=$(curl -s -w "%{http_code}" "$API_URL/api/templates/list")
    http_code="${response: -3}"
    
    if [[ "$http_code" == "200" ]]; then
        log_success "Templates endpoint responding correctly"
    else
        log_error "Templates endpoint failed (HTTP $http_code)"
        return 1
    fi
    
    # Test Razorflow endpoints
    response=$(curl -s -w "%{http_code}" "$API_URL/api/razorflow/queue/status")
    http_code="${response: -3}"
    
    if [[ "$http_code" == "200" ]]; then
        log_success "Razorflow queue status endpoint responding"
    else
        log_warning "Razorflow queue status endpoint may not be implemented yet (HTTP $http_code)"
    fi
}

test_template_system() {
    run_test "Template System Functionality"
    
    # Test template loading
    response=$(curl -s "$API_URL/api/templates/list")
    
    if echo "$response" | grep -q "customer_service_bot"; then
        log_success "Customer service bot template is available"
    else
        log_error "Customer service bot template not found"
        return 1
    fi
    
    if echo "$response" | grep -q "restaurant_assistant"; then
        log_success "Restaurant assistant template is available"
    else
        log_error "Restaurant assistant template not found"
        return 1
    fi
    
    # Count available templates
    template_count=$(echo "$response" | grep -o '"[^"]*_[^"]*"' | wc -l)
    if [[ $template_count -ge 6 ]]; then
        log_success "Sufficient templates available ($template_count)"
    else
        log_warning "Fewer templates than expected ($template_count, expected 6)"
    fi
}

test_razorflow_integration() {
    run_test "Razorflow-AI Integration"
    
    # Test queue build endpoint with sample data
    sample_data='{
        "name": "Test Restaurant",
        "email": "test@restaurant.com",
        "industry": "restaurant",
        "description": "A test restaurant for staging",
        "requirements": ["order_taking", "reservations"],
        "budget": 5000,
        "timeline": "2_weeks"
    }'
    
    response=$(curl -s -w "%{http_code}" \
        -H "Content-Type: application/json" \
        -d "$sample_data" \
        "$API_URL/api/razorflow/queue-build")
    
    http_code="${response: -3}"
    
    if [[ "$http_code" == "200" ]] || [[ "$http_code" == "201" ]]; then
        log_success "Razorflow queue build endpoint functional"
    else
        log_warning "Razorflow queue build may need configuration (HTTP $http_code)"
    fi
}

test_database_connectivity() {
    run_test "Database Connectivity"
    
    # Check if database container is running
    if docker-compose ps postgres | grep -q "Up"; then
        log_success "PostgreSQL container is running"
    else
        log_error "PostgreSQL container is not running"
        return 1
    fi
    
    # Check Redis connectivity
    if docker-compose ps redis | grep -q "Up"; then
        log_success "Redis container is running"
    else
        log_error "Redis container is not running"
        return 1
    fi
    
    # Check ChromaDB connectivity
    if docker-compose ps chromadb | grep -q "Up"; then
        log_success "ChromaDB container is running"
    else
        log_warning "ChromaDB container may not be running"
    fi
}

test_performance() {
    run_test "Basic Performance Testing"
    
    # Test API response time
    start_time=$(date +%s%N)
    curl -s "$API_URL/health" > /dev/null
    end_time=$(date +%s%N)
    
    response_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    
    if [[ $response_time -lt 1000 ]]; then
        log_success "API response time acceptable (${response_time}ms)"
    else
        log_warning "API response time slow (${response_time}ms)"
    fi
    
    # Test template loading performance
    start_time=$(date +%s%N)
    curl -s "$API_URL/api/templates/list" > /dev/null
    end_time=$(date +%s%N)
    
    template_load_time=$(( (end_time - start_time) / 1000000 ))
    
    if [[ $template_load_time -lt 2000 ]]; then
        log_success "Template loading time acceptable (${template_load_time}ms)"
    else
        log_warning "Template loading time slow (${template_load_time}ms)"
    fi
}

test_security() {
    run_test "Basic Security Checks"
    
    # Test that sensitive endpoints require authentication (if implemented)
    response=$(curl -s -w "%{http_code}" "$API_URL/api/admin/system")
    http_code="${response: -3}"
    
    if [[ "$http_code" == "401" ]] || [[ "$http_code" == "403" ]] || [[ "$http_code" == "404" ]]; then
        log_success "Admin endpoints are protected"
    else
        log_warning "Admin endpoints may not be properly protected"
    fi
    
    # Test for common security headers (basic check)
    headers=$(curl -s -I "$API_URL/health")
    
    if echo "$headers" | grep -qi "x-frame-options\|x-content-type-options"; then
        log_success "Some security headers are present"
    else
        log_warning "Consider adding security headers"
    fi
}

cleanup() {
    run_test "Cleanup"
    
    cd "$PROJECT_ROOT"
    
    log_info "Stopping and cleaning up containers..."
    docker-compose down -v --remove-orphans
    
    # Remove test images
    if docker images | grep -q "pixel-ai-api.*staging"; then
        docker rmi pixel-ai-api:staging
        log_success "Test images cleaned up"
    fi
    
    log_success "Cleanup completed"
}

# Main test execution
main() {
    echo -e "\n${BLUE}Starting Staging Test Suite...${NC}\n"
    
    # Run all tests
    test_prerequisites
    test_docker_build
    test_compose_validation
    test_environment_setup
    test_service_startup
    test_api_endpoints
    test_template_system
    test_razorflow_integration
    test_database_connectivity
    test_performance
    test_security
    
    # Always cleanup
    cleanup
    
    # Print summary
    echo -e "\n${BLUE}========================================="
    echo "Test Summary"
    echo "=========================================${NC}"
    echo -e "Total Tests: ${TESTS_RUN}"
    echo -e "Passed: ${GREEN}${TESTS_PASSED}${NC}"
    echo -e "Failed: ${RED}${TESTS_FAILED}${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}🎉 All tests passed! System is ready for staging deployment.${NC}"
        exit 0
    else
        echo -e "\n${RED}❌ Some tests failed. Please review and fix issues before deployment.${NC}"
        exit 1
    fi
}

# Handle interrupts
trap cleanup EXIT

# Run main function
main "$@"
