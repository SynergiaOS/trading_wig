#!/bin/bash
# Production startup script for Polish Finance Platform

set -e

echo "🚀 Starting Polish Finance Platform - Production Mode"
echo "===================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if services are running
check_service() {
    if curl -s "$1" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $2 is running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $2 is not running${NC}"
        return 1
    fi
}

# Start Backend Python API
echo ""
echo "📡 Starting Backend Python API..."
cd "$(dirname "$0")/code"
if ! pgrep -f "python3 realtime_api_server.py" > /dev/null; then
    python3 realtime_api_server.py > /tmp/realtime_api_prod.log 2>&1 &
    sleep 2
    echo -e "${GREEN}✅ Backend API started${NC}"
else
    echo -e "${GREEN}✅ Backend API already running${NC}"
fi

# Start PocketBase
echo ""
echo "🗄️  Starting PocketBase..."
cd "$(dirname "$0")"
if ! pgrep -f "pocketbase serve" > /dev/null; then
    ./pocketbase serve --http=0.0.0.0:8090 > /tmp/pocketbase_prod.log 2>&1 &
    sleep 2
    echo -e "${GREEN}✅ PocketBase started${NC}"
else
    echo -e "${GREEN}✅ PocketBase already running${NC}"
fi

# Build and start Frontend
echo ""
echo "🎨 Building Frontend for production..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/polish-finance-platform/polish-finance-app"

# Build production
NODE_ENV=production pnpm run build:prod

echo ""
echo "🌐 Starting Frontend production server..."
pnpm run start > /tmp/frontend_prod.log 2>&1 &
sleep 3

# Check all services
echo ""
echo "🔍 Checking services..."
echo "======================"

check_service "http://localhost:8000/data" "Backend API"
check_service "http://localhost:8090/api/health" "PocketBase"
check_service "http://localhost:4173" "Frontend"

echo ""
echo "===================================================="
echo "🎉 Production environment is ready!"
echo ""
echo "📍 Services:"
echo "   Frontend:  http://localhost:4173"
echo "   Backend:   http://localhost:8000/data"
echo "   PocketBase: http://localhost:8090"
echo ""
echo "📋 Logs:"
echo "   Frontend:  tail -f /tmp/frontend_prod.log"
echo "   Backend:   tail -f /tmp/realtime_api_prod.log"
echo "   PocketBase: tail -f /tmp/pocketbase_prod.log"
echo "===================================================="

