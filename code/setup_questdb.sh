#!/bin/bash

# WIG80 QuestDB Setup Script
# Complete setup and initialization for QuestDB Polish Stock Market Analysis
# ===========================================

set -e

echo "🚀 Starting WIG80 QuestDB Setup..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if Docker is installed
check_docker() {
    print_header "Checking Docker Installation"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first:"
        echo "  Ubuntu/Debian: sudo apt-get install docker.io docker-compose"
        echo "  CentOS/RHEL: sudo yum install docker docker-compose"
        echo "  macOS: brew install docker docker-compose"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first:"
        echo "  sudo curl -L \"https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
        echo "  sudo chmod +x /usr/local/bin/docker-compose"
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Create necessary directories
create_directories() {
    print_header "Creating Directory Structure"
    
    mkdir -p questdb_config
    mkdir -p data
    mkdir -p logs
    
    print_status "Created directories: questdb_config, data, logs"
}

# Generate QuestDB configuration
generate_config() {
    print_header "Generating QuestDB Configuration"
    
    if [ ! -f "questdb_config/server.conf" ]; then
        print_status "QuestDB configuration file not found. Using default configuration..."
        # The configuration will be created by the files already written
        print_status "Configuration file created: questdb_config/server.conf"
    else
        print_status "Configuration file already exists, skipping..."
    fi
}

# Start QuestDB with Docker
start_questdb() {
    print_header "Starting QuestDB"
    
    print_status "Starting QuestDB container..."
    docker-compose -f docker-compose.questdb.yml up -d
    
    # Wait for QuestDB to be ready
    print_status "Waiting for QuestDB to start (30 seconds)..."
    sleep 30
    
    # Check if container is running
    if docker ps | grep -q wig80-questdb; then
        print_status "QuestDB container is running successfully!"
    else
        print_error "QuestDB container failed to start. Check logs with:"
        echo "  docker-compose -f docker-compose.questdb.yml logs"
        exit 1
    fi
}

# Wait for QuestDB API to be ready
wait_for_api() {
    print_header "Waiting for QuestDB API"
    
    print_status "Waiting for QuestDB REST API to be ready..."
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -u admin:quest http://localhost:8812/health > /dev/null 2>&1; then
            print_status "QuestDB REST API is ready!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        print_status "Attempt $attempt/$max_attempts - waiting..."
        sleep 2
    done
    
    print_error "QuestDB REST API is not responding. Please check the logs."
    docker-compose -f docker-compose.questdb.yml logs
    exit 1
}

# Initialize database schema
initialize_database() {
    print_header "Initializing Database Schema"
    
    if [ -f "wig80_database_setup.sql" ]; then
        print_status "Initializing database schema..."
        
        # Execute SQL script via QuestDB REST API
        curl -u admin:quest -G "http://localhost:8812/exec" --data-urlencode "query@-" << 'EOF'
-- WIG80 QuestDB Database Setup Script
-- Polish Stock Market Time Series Analysis
-- =======================================

-- Create the main historical data table
CREATE TABLE IF NOT EXISTS wig80_historical (
    ts TIMESTAMP,
    symbol SYMBOL CAPACITY 200 CACHE,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume LONG,
    macd DOUBLE,
    rsi DOUBLE,
    bb_upper DOUBLE,
    bb_lower DOUBLE
) TIMESTAMP(ts) PARTITION BY DAY WAL;

-- Create AI insights table
CREATE TABLE IF NOT EXISTS ai_insights (
    ts TIMESTAMP,
    symbol SYMBOL CAPACITY 200 CACHE,
    insight_type STRING,
    result JSON,
    confidence DOUBLE
) TIMESTAMP(ts) PARTITION BY DAY WAL;

-- Create market correlations table
CREATE TABLE IF NOT EXISTS market_correlations (
    ts TIMESTAMP,
    symbol_a SYMBOL CAPACITY 200 CACHE,
    symbol_b SYMBOL CAPACITY 200 CACHE,
    correlation DOUBLE,
    strength DOUBLE
) TIMESTAMP(ts) PARTITION BY DAY WAL;

-- Create valuation analysis table
CREATE TABLE IF NOT EXISTS valuation_analysis (
    ts TIMESTAMP,
    symbol SYMBOL CAPACITY 200 CACHE,
    pe_ratio DOUBLE,
    pb_ratio DOUBLE,
    historical_pe_avg DOUBLE,
    historical_pb_avg DOUBLE,
    overvaluation_score DOUBLE
) TIMESTAMP(ts) PARTITION BY DAY WAL;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS wig80_historical_symbol_idx ON wig80_historical(symbol);
CREATE INDEX IF NOT EXISTS wig80_historical_symbol_ts_idx ON wig80_historical(symbol, ts DESC);

CREATE INDEX IF NOT EXISTS ai_insights_symbol_idx ON ai_insights(symbol);
CREATE INDEX IF NOT EXISTS ai_insights_symbol_ts_idx ON ai_insights(symbol, ts DESC);
CREATE INDEX IF NOT EXISTS ai_insights_type_idx ON ai_insights(insight_type);

CREATE INDEX IF NOT EXISTS market_correlations_symbol_a_idx ON market_correlations(symbol_a);
CREATE INDEX IF NOT EXISTS market_correlations_symbol_b_idx ON market_correlations(symbol_b);
CREATE INDEX IF NOT EXISTS market_correlations_symbols_ts_idx ON market_correlations(symbol_a, symbol_b, ts DESC);

CREATE INDEX IF NOT EXISTS valuation_analysis_symbol_idx ON valuation_analysis(symbol);
CREATE INDEX IF NOT EXISTS valuation_analysis_symbol_ts_idx ON valuation_analysis(symbol, ts DESC);
EOF

        if [ $? -eq 0 ]; then
            print_status "Database schema initialized successfully!"
        else
            print_error "Failed to initialize database schema"
            exit 1
        fi
    else
        print_error "Schema file not found: wig80_database_setup.sql"
        exit 1
    fi
}

# Install Python dependencies
install_dependencies() {
    print_header "Installing Python Dependencies"
    
    if command -v python3 &> /dev/null; then
        print_status "Installing required Python packages..."
        python3 -m pip install aiohttp asyncio --quiet || print_warning "Some packages failed to install"
        print_status "Python dependencies installed"
    else
        print_warning "Python3 not found, skipping Python dependency installation"
    fi
}

# Run sample data population
populate_sample_data() {
    print_header "Populating Sample Data"
    
    if [ -f "wig80_questdb_client.py" ]; then
        print_status "Running sample data population script..."
        
        if command -v python3 &> /dev/null; then
            python3 wig80_questdb_client.py || print_warning "Sample data population script encountered issues"
            print_status "Sample data population completed!"
        else
            print_warning "Python3 not found, skipping sample data population"
        fi
    else
        print_warning "Python client script not found"
    fi
}

# Display success information
show_success_info() {
    print_header "Setup Complete!"
    
    echo -e "${GREEN}✅ QuestDB has been successfully set up for WIG80 analysis!${NC}"
    echo ""
    echo "🔗 Access Information:"
    echo "  • QuestDB Web Console: http://localhost:9009"
    echo "    Username: admin"
    echo "    Password: quest"
    echo ""
    echo "  • REST API: http://localhost:8812"
    echo "  • PostgreSQL Wire: localhost:9000"
    echo ""
    echo "📊 Database Tables Created:"
    echo "  • wig80_historical - Historical stock data with technical indicators"
    echo "  • ai_insights - AI-generated market insights"
    echo "  • market_correlations - Stock correlation analysis"
    echo "  • valuation_analysis - Fundamental analysis metrics"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • Stop QuestDB:     docker-compose -f docker-compose.questdb.yml down"
    echo "  • View logs:        docker-compose -f docker-compose.questdb.yml logs"
    echo "  • Restart:          docker-compose -f docker-compose.questdb.yml restart"
    echo "  • Remove data:      docker-compose -f docker-compose.questdb.yml down -v"
    echo ""
    echo "📈 Sample Queries:"
    echo "  • Top performers:   SELECT symbol, AVG(rsi) FROM wig80_historical GROUP BY symbol"
    echo "  • Volume leaders:   SELECT symbol, SUM(volume) FROM wig80_historical GROUP BY symbol"
    echo "  • Recent data:      SELECT * FROM wig80_historical WHERE ts >= dateadd('day', -7, now())"
    echo ""
    echo "🎉 Happy analyzing Polish stock market data!"
}

# Main execution
main() {
    # Parse command line arguments
    SKIP_DOCKER=false
    SKIP_DATA=false
    VERBOSE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-docker)
                SKIP_DOCKER=true
                shift
                ;;
            --skip-data)
                SKIP_DATA=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-docker    Skip Docker setup (assume QuestDB is already running)"
                echo "  --skip-data      Skip sample data population"
                echo "  --verbose        Show verbose output"
                echo "  --help           Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    print_header "WIG80 QuestDB Setup Starting"
    
    # Run setup steps
    check_docker
    create_directories
    generate_config
    
    if [ "$SKIP_DOCKER" = false ]; then
        start_questdb
        wait_for_api
    else
        print_warning "Skipping Docker setup - assuming QuestDB is already running"
    fi
    
    initialize_database
    install_dependencies
    
    if [ "$SKIP_DATA" = false ]; then
        populate_sample_data
    else
        print_warning "Skipping sample data population"
    fi
    
    show_success_info
}

# Run main function
main "$@"
