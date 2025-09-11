#!/bin/bash

# Celery Worker Startup Script for Pixel AI Creator
# This script starts Celery workers and beat scheduler for background task processing

set -e

echo "🚀 Starting Pixel AI Creator Background Services..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:/app"
export C_FORCE_ROOT=1

# Function to start Celery worker
start_worker() {
    local queue_name=$1
    local concurrency=${2:-4}
    
    echo "📋 Starting Celery worker for queue: $queue_name"
    celery -A core.celery_app worker \
        --loglevel=info \
        --queues="$queue_name" \
        --concurrency="$concurrency" \
        --hostname="worker-$queue_name@%h" \
        --pidfile="/tmp/celery-$queue_name.pid" \
        --logfile="/var/log/celery/worker-$queue_name.log" \
        --detach
}

# Function to start Celery beat scheduler
start_beat() {
    echo "⏰ Starting Celery beat scheduler"
    celery -A core.celery_app beat \
        --loglevel=info \
        --pidfile="/tmp/celery-beat.pid" \
        --logfile="/var/log/celery/beat.log" \
        --detach
}

# Function to stop all Celery processes
stop_celery() {
    echo "🛑 Stopping Celery processes..."
    pkill -f "celery.*worker" || true
    pkill -f "celery.*beat" || true
    rm -f /tmp/celery-*.pid
    echo "✅ Celery processes stopped"
}

# Function to check worker status
check_status() {
    echo "📊 Checking Celery worker status..."
    celery -A core.celery_app inspect active
    celery -A core.celery_app inspect stats
}

# Function to monitor workers
monitor_workers() {
    echo "👁️  Starting Celery worker monitor..."
    celery -A core.celery_app events
}

# Create log directory
mkdir -p /var/log/celery

# Handle script arguments
case "$1" in
    start)
        echo "🎯 Starting all Celery services..."
        
        # Start workers for different queues
        start_worker "default" 4
        start_worker "conversations" 6
        start_worker "analytics" 2
        start_worker "notifications" 2
        start_worker "maintenance" 1
        
        # Start beat scheduler
        start_beat
        
        echo "✅ All Celery services started successfully!"
        echo "📝 Check logs at: /var/log/celery/"
        ;;
        
    stop)
        stop_celery
        ;;
        
    restart)
        stop_celery
        sleep 2
        $0 start
        ;;
        
    status)
        check_status
        ;;
        
    monitor)
        monitor_workers
        ;;
        
    worker)
        if [ -z "$2" ]; then
            echo "❌ Usage: $0 worker <queue_name> [concurrency]"
            exit 1
        fi
        queue_name=$2
        concurrency=${3:-4}
        start_worker "$queue_name" "$concurrency"
        ;;
        
    beat)
        start_beat
        ;;
        
    dev)
        echo "🔧 Starting Celery in development mode..."
        celery -A core.celery_app worker --loglevel=debug --queues=default,conversations,analytics,notifications,maintenance
        ;;
        
    flower)
        echo "🌸 Starting Flower monitoring interface..."
        celery -A core.celery_app flower --port=5555
        ;;
        
    purge)
        echo "🧹 Purging all queues..."
        celery -A core.celery_app purge -f
        echo "✅ All queues purged"
        ;;
        
    test)
        echo "🧪 Testing Celery setup..."
        python -c "
from core.celery_app import celery_app, debug_task, health_check
import time

print('Testing Celery connection...')
result = debug_task.delay()
print(f'Debug task ID: {result.id}')

print('Testing health check...')
health_result = health_check.delay()
print(f'Health check task ID: {health_result.id}')

print('Waiting for results...')
time.sleep(5)

try:
    debug_result = result.get(timeout=10)
    print(f'Debug task result: {debug_result}')
    
    health_data = health_result.get(timeout=10)
    print(f'Health check result: {health_data}')
    
    print('✅ Celery is working correctly!')
except Exception as e:
    print(f'❌ Celery test failed: {e}')
"
        ;;
        
    logs)
        queue=${2:-"default"}
        echo "📄 Showing logs for queue: $queue"
        tail -f "/var/log/celery/worker-$queue.log"
        ;;
        
    *)
        echo "🤖 Pixel AI Creator - Celery Management Script"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|monitor|worker|beat|dev|flower|purge|test|logs}"
        echo ""
        echo "Commands:"
        echo "  start                    - Start all Celery workers and beat scheduler"
        echo "  stop                     - Stop all Celery processes"
        echo "  restart                  - Restart all Celery services"
        echo "  status                   - Check worker status and stats"
        echo "  monitor                  - Start real-time event monitoring"
        echo "  worker <queue> [conc]    - Start single worker for specific queue"
        echo "  beat                     - Start only beat scheduler"
        echo "  dev                      - Start in development mode (single worker)"
        echo "  flower                   - Start Flower monitoring web interface"
        echo "  purge                    - Purge all queues (removes all pending tasks)"
        echo "  test                     - Test Celery setup with debug tasks"
        echo "  logs [queue]             - Show logs for specific queue (default: default)"
        echo ""
        echo "Examples:"
        echo "  $0 start                 # Start all services"
        echo "  $0 worker conversations 8  # Start conversation worker with 8 processes"
        echo "  $0 logs analytics        # Show analytics worker logs"
        echo ""
        exit 1
        ;;
esac

exit 0
