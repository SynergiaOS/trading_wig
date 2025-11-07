#!/bin/bash
# QuestDB-Pocketbase Monitoring System Startup Script
# ===================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE_DIR="/workspace"
LOGS_DIR="/workspace/logs"
BACKUPS_DIR="/workspace/backups"
MONITORING_DIR="/workspace/monitoring"
MONITORING_PORT=8080
LOG_LEVEL="INFO"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}  QuestDB-Pocketbase Monitoring System${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
}

# Function to check if required directories exist
check_directories() {
    print_status "Checking required directories..."
    
    # Create directories if they don't exist
    mkdir -p "$LOGS_DIR" "$BACKUPS_DIR" "$MONITORING_DIR"
    
    # Set proper permissions
    chmod 755 "$LOGS_DIR" "$BACKUPS_DIR" "$MONITORING_DIR"
    
    print_status "Directories ready"
}

# Function to check Python dependencies
check_dependencies() {
    print_status "Checking Python dependencies..."
    
    # Check if Python 3.8+ is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check required packages
    python3 -c "import aiohttp, psutil" 2>/dev/null || {
        print_warning "Required packages not found. Installing..."
        pip3 install aiohttp psutil
    }
    
    print_status "Dependencies verified"
}

# Function to check database accessibility
check_databases() {
    print_status "Checking database accessibility..."
    
    # Check QuestDB test database
    if [ -f "/workspace/code/questdb_wig80_test.db" ]; then
        print_status "QuestDB test database found"
        
        # Test database access
        if sqlite3 /workspace/code/questdb_wig80_test.db "SELECT COUNT(*) FROM wig80_historical;" >/dev/null 2>&1; then
            print_status "QuestDB database accessible"
        else
            print_warning "QuestDB database found but not accessible"
        fi
    else
        print_warning "QuestDB test database not found at /workspace/code/questdb_wig80_test.db"
    fi
    
    # Check Pocketbase service
    if curl -s --connect-timeout 5 http://localhost:8090/api/health >/dev/null 2>&1; then
        print_status "Pocketbase service is accessible"
    else
        print_warning "Pocketbase service not accessible at http://localhost:8090"
        print_warning "Monitoring system will run but may show health issues"
    fi
}

# Function to start monitoring system
start_monitoring_system() {
    print_status "Starting monitoring system service..."
    
    cd "$WORKSPACE_DIR/code"
    
    # Start monitoring system in background
    nohup python3 monitoring_system.py > "$LOGS_DIR/monitoring_system.out" 2>&1 &
    MONITORING_PID=$!
    
    # Save PID for later
    echo $MONITORING_PID > /tmp/monitoring_system.pid
    
    print_status "Monitoring system started (PID: $MONITORING_PID)"
    
    # Wait a moment for startup
    sleep 3
    
    # Check if process is still running
    if kill -0 $MONITORING_PID 2>/dev/null; then
        print_status "Monitoring system is running"
    else
        print_error "Monitoring system failed to start"
        print_error "Check logs at: $LOGS_DIR/monitoring_system.out"
        exit 1
    fi
}

# Function to start dashboard
start_dashboard() {
    print_status "Starting monitoring dashboard..."
    
    cd "$WORKSPACE_DIR/code"
    
    # Start dashboard in background
    nohup python3 monitoring_dashboard.py --port $MONITORING_PORT > "$LOGS_DIR/monitoring_dashboard.out" 2>&1 &
    DASHBOARD_PID=$!
    
    # Save PID for later
    echo $DASHBOARD_PID > /tmp/monitoring_dashboard.pid
    
    print_status "Dashboard started (PID: $DASHBOARD_PID)"
    
    # Wait a moment for startup
    sleep 3
    
    # Check if process is still running
    if kill -0 $DASHBOARD_PID 2>/dev/null; then
        print_status "Dashboard is running"
    else
        print_error "Dashboard failed to start"
        print_error "Check logs at: $LOGS_DIR/monitoring_dashboard.out"
        exit 1
    fi
}

# Function to show service status
show_status() {
    print_header
    print_status "QuestDB-Pocketbase Monitoring System Status"
    echo ""
    
    # Check monitoring system
    if [ -f /tmp/monitoring_system.pid ]; then
        PID=$(cat /tmp/monitoring_system.pid)
        if kill -0 $PID 2>/dev/null; then
            print_status "✓ Monitoring System: Running (PID: $PID)"
        else
            print_error "✗ Monitoring System: Not running"
        fi
    else
        print_error "✗ Monitoring System: Not started"
    fi
    
    # Check dashboard
    if [ -f /tmp/monitoring_dashboard.pid ]; then
        PID=$(cat /tmp/monitoring_dashboard.pid)
        if kill -0 $PID 2>/dev/null; then
            print_status "✓ Dashboard: Running (PID: $PID)"
        else
            print_error "✗ Dashboard: Not running"
        fi
    else
        print_error "✗ Dashboard: Not started"
    fi
    
    echo ""
    print_status "Access the monitoring dashboard at:"
    print_status "  http://localhost:$MONITORING_PORT/"
    echo ""
}

# Function to stop services
stop_services() {
    print_status "Stopping monitoring services..."
    
    # Stop monitoring system
    if [ -f /tmp/monitoring_system.pid ]; then
        PID=$(cat /tmp/monitoring_system.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            print_status "Monitoring system stopped (PID: $PID)"
        fi
        rm -f /tmp/monitoring_system.pid
    fi
    
    # Stop dashboard
    if [ -f /tmp/monitoring_dashboard.pid ]; then
        PID=$(cat /tmp/monitoring_dashboard.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            print_status "Dashboard stopped (PID: $PID)"
        fi
        rm -f /tmp/monitoring_dashboard.pid
    fi
}

# Function to show logs
show_logs() {
    local service=$1
    
    case $service in
        "monitoring")
            print_status "Monitoring System Logs (last 20 lines):"
            tail -20 "$LOGS_DIR/monitoring_system.out"
            ;;
        "dashboard")
            print_status "Dashboard Logs (last 20 lines):"
            tail -20 "$LOGS_DIR/monitoring_dashboard.out"
            ;;
        "all")
            print_status "All Monitoring Logs:"
            echo "=== Monitoring System ==="
            tail -20 "$LOGS_DIR/monitoring_system.out"
            echo ""
            echo "=== Dashboard ==="
            tail -20 "$LOGS_DIR/monitoring_dashboard.out"
            ;;
        *)
            print_error "Unknown service: $service"
            echo "Available services: monitoring, dashboard, all"
            ;;
    esac
}

# Function to show help
show_help() {
    echo "QuestDB-Pocketbase Monitoring System Startup Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start          Start both monitoring system and dashboard"
    echo "  stop           Stop all monitoring services"
    echo "  restart        Restart all monitoring services"
    echo "  status         Show status of all services"
    echo "  logs [service] Show logs (service: monitoring|dashboard|all)"
    echo "  check          Run system checks without starting services"
    echo "  help           Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  MONITORING_PORT    Dashboard port (default: 8080)"
    echo "  LOG_LEVEL         Logging level (default: INFO)"
    echo ""
    echo "Examples:"
    echo "  $0 start                # Start all services"
    echo "  $0 logs monitoring     # Show monitoring system logs"
    echo "  $0 status              # Show service status"
    echo ""
}

# Main function
main() {
    # Apply environment variables
    if [ ! -z "$MONITORING_PORT" ]; then
        MONITORING_PORT=$MONITORING_PORT
    fi
    
    if [ ! -z "$LOG_LEVEL" ]; then
        LOG_LEVEL=$LOG_LEVEL
    fi
    
    case "${1:-start}" in
        "start")
            print_header
            check_directories
            check_dependencies
            check_databases
            start_monitoring_system
            start_dashboard
            echo ""
            show_status
            print_status "Monitoring system is ready!"
            print_status "Access the dashboard at: http://localhost:$MONITORING_PORT/"
            ;;
        "stop")
            print_header
            stop_services
            print_status "All services stopped"
            ;;
        "restart")
            print_header
            stop_services
            sleep 2
            check_directories
            check_dependencies
            check_databases
            start_monitoring_system
            start_dashboard
            echo ""
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "${2:-all}"
            ;;
        "check")
            print_header
            check_directories
            check_dependencies
            check_databases
            print_status "System check completed"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Trap to ensure clean shutdown
trap 'print_status "Received interrupt signal, shutting down..."; stop_services; exit 0' INT TERM

# Run main function with all arguments
main "$@"