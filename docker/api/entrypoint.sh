#!/bin/bash
# Docker Entrypoint Script for Pixel AI Creator API
# Handles initialization, health checks, and service startup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Environment validation
validate_environment() {
    log "🔍 Validating environment variables..."
    
    # Required environment variables
    REQUIRED_VARS=(
        "DATABASE_URL"
        "REDIS_URL" 
        "OPENAI_API_KEY"
    )
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    success "Environment variables validated"
}

# Wait for dependencies
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1
    
    log "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            success "$service_name is ready"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts: $service_name not ready, waiting..."
        sleep 2
        ((attempt++))
    done
    
    error "$service_name failed to become ready after $max_attempts attempts"
    return 1
}

# Database health check
check_database() {
    log "🗄️ Checking database connection..."
    
    python3 -c "
import asyncio
import sys
from core.database import test_connection

async def test():
    try:
        result = await test_connection()
        if result:
            print('Database connection successful')
            sys.exit(0)
        else:
            print('Database connection failed')
            sys.exit(1)
    except Exception as e:
        print(f'Database connection error: {e}')
        sys.exit(1)

asyncio.run(test())
" || return 1
    
    success "Database connection verified"
}

# Redis health check
check_redis() {
    log "🔴 Checking Redis connection..."
    
    python3 -c "
import redis
import sys
import os

try:
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    r = redis.from_url(redis_url)
    r.ping()
    print('Redis connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Redis connection error: {e}')
    sys.exit(1)
" || return 1
    
    success "Redis connection verified"
}

# Initialize database schema
initialize_database() {
    log "📋 Initializing database schema..."
    
    python3 -c "
import asyncio
from core.database import init_db

async def init():
    try:
        await init_db()
        print('Database initialized successfully')
    except Exception as e:
        print(f'Database initialization error: {e}')
        raise

asyncio.run(init())
" || {
        error "Database initialization failed"
        return 1
    }
    
    success "Database schema initialized"
}

# Validate Razorflow-AI templates
validate_templates() {
    log "🤖 Validating Razorflow-AI templates..."
    
    python3 -c "
import asyncio
import sys
import os
sys.path.append('/app')

from services.template_manager import TemplateManager

async def validate():
    try:
        template_manager = TemplateManager()
        templates = await template_manager.list_available_templates()
        
        if len(templates) == 0:
            print('No templates found')
            sys.exit(1)
        
        valid_count = 0
        for template in templates:
            try:
                template_data = await template_manager.load_template(template['template_id'])
                validation = await template_manager.validate_template(template_data)
                if validation['valid']:
                    valid_count += 1
                else:
                    print(f'Template {template[\"template_id\"]} validation failed: {validation[\"errors\"]}')
            except Exception as e:
                print(f'Template {template.get(\"template_id\", \"unknown\")} error: {e}')
        
        print(f'Templates validated: {valid_count}/{len(templates)}')
        if valid_count == len(templates):
            print('All templates valid')
            sys.exit(0)
        else:
            print('Some templates failed validation')
            sys.exit(1)
            
    except Exception as e:
        print(f'Template validation error: {e}')
        sys.exit(1)

asyncio.run(validate())
" || {
        warning "Template validation issues detected"
        return 1
    }
    
    success "Templates validated successfully"
}

# Create required directories
setup_directories() {
    log "📁 Setting up required directories..."
    
    directories=(
        "/app/generated-bots"
        "/app/templates"
        "/app/logs"
        "/app/tmp"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log "Created directory: $dir"
        fi
    done
    
    success "Directories setup complete"
}

# Install additional Python packages if needed
install_dependencies() {
    log "📦 Checking Python dependencies..."
    
    # Check if all required packages are installed
    python3 -c "
import pkg_resources
import sys

required_packages = [
    'fastapi',
    'uvicorn',
    'sqlalchemy',
    'asyncpg',
    'redis',
    'openai',
    'playwright',
    'beautifulsoup4',
    'structlog'
]

missing_packages = []
for package in required_packages:
    try:
        pkg_resources.get_distribution(package)
    except pkg_resources.DistributionNotFound:
        missing_packages.append(package)

if missing_packages:
    print(f'Missing packages: {missing_packages}')
    sys.exit(1)
else:
    print('All required packages are installed')
    sys.exit(0)
" || {
        error "Missing Python dependencies"
        return 1
    }
    
    success "Python dependencies verified"
}

# Run pre-startup tests
run_startup_tests() {
    log "🧪 Running pre-startup tests..."
    
    # Test basic API functionality
    python3 -c "
import asyncio
import sys
sys.path.append('/app')

from services.web_analyzer import WebAnalyzer
from services.template_manager import TemplateManager
from services.razorflow_integration import RazorflowIntegration

async def test_services():
    try:
        # Test WebAnalyzer
        analyzer = WebAnalyzer()
        if not hasattr(analyzer, 'openai_client'):
            raise Exception('WebAnalyzer not properly initialized')
        
        # Test TemplateManager
        template_manager = TemplateManager()
        templates = await template_manager.list_available_templates()
        if not isinstance(templates, list):
            raise Exception('TemplateManager not returning proper data')
        
        # Test RazorflowIntegration
        razorflow = RazorflowIntegration()
        if not hasattr(razorflow, 'build_queue'):
            raise Exception('RazorflowIntegration not properly initialized')
        
        print('All services initialized successfully')
        sys.exit(0)
        
    except Exception as e:
        print(f'Service initialization error: {e}')
        sys.exit(1)

asyncio.run(test_services())
" || {
        error "Service initialization tests failed"
        return 1
    }
    
    success "Pre-startup tests passed"
}

# Health check endpoint test
test_health_endpoint() {
    log "🏥 Testing health endpoint..."
    
    # Start the server in background for testing
    uvicorn main:app --host 0.0.0.0 --port 8000 &
    SERVER_PID=$!
    
    # Wait a moment for server to start
    sleep 5
    
    # Test health endpoint
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        success "Health endpoint responding"
        kill $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
        return 0
    else
        error "Health endpoint not responding"
        kill $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
        return 1
    fi
}

# Main startup sequence
main() {
    log "🚀 Starting Pixel AI Creator API initialization..."
    
    # Parse command line arguments
    case "${1:-start}" in
        "start")
            log "Starting full initialization sequence..."
            ;;
        "test")
            log "Running test mode..."
            ;;
        "debug")
            log "Starting debug mode..."
            set -x
            ;;
        *)
            log "Usage: $0 [start|test|debug]"
            exit 1
            ;;
    esac
    
    # Run initialization steps
    validate_environment || exit 1
    setup_directories || exit 1
    install_dependencies || exit 1
    
    # Wait for dependencies
    if [ "${ENVIRONMENT:-}" = "production" ]; then
        # Parse database URL to get host and port
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        REDIS_HOST=$(echo $REDIS_URL | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')
        
        wait_for_service "$DB_HOST" 5432 "PostgreSQL" || exit 1
        wait_for_service "$REDIS_HOST" 6379 "Redis" || exit 1
    fi
    
    # Initialize services
    check_database || exit 1
    check_redis || exit 1
    initialize_database || exit 1
    validate_templates || warning "Template validation failed, continuing..."
    run_startup_tests || exit 1
    
    success "🎉 Initialization complete!"
    
    # Start the application based on mode
    case "${1:-start}" in
        "test")
            log "Test mode complete, exiting..."
            exit 0
            ;;
        "debug")
            log "Starting application in debug mode..."
            exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
            ;;
        *)
            log "Starting application in production mode..."
            exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
            ;;
    esac
}

# Install netcat if not present (for service checking)
if ! command -v nc &> /dev/null; then
    apt-get update && apt-get install -y netcat-openbsd
fi

# Run main function
main "$@"
