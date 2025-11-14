#!/bin/bash
# Railway Set Variables Script
# Ustawia wszystkie zmienne środowiskowe dla serwisów

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🔧 RAILWAY SET VARIABLES                                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Sprawdź czy Railway CLI działa
if ! railway whoami &>/dev/null; then
    echo "❌ Railway CLI nie jest zalogowany"
    echo "   Uruchom: railway login"
    exit 1
fi

echo "✅ Railway CLI działa"
echo ""

# Funkcja do ustawiania zmiennych dla serwisu
set_service_vars() {
    local SERVICE=$1
    shift
    local VARS=("$@")
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Ustawiam zmienne dla: $SERVICE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    railway service "$SERVICE"
    
    for var in "${VARS[@]}"; do
        if [[ $var == *"="* ]]; then
            KEY=$(echo "$var" | cut -d'=' -f1)
            VALUE=$(echo "$var" | cut -d'=' -f2-)
            echo "   Ustawiam: $KEY=***"
            railway variables --set "$var" --service "$SERVICE" || echo "   ⚠️  Nie udało się ustawić: $KEY"
        fi
    done
    echo ""
}

# Frontend Service
echo "🔹 Frontend Service"
read -p "Podaj Backend URL (lub Enter aby pominąć): " BACKEND_URL
read -p "Podaj Analysis URL (lub Enter aby pominąć): " ANALYSIS_URL

FRONTEND_VARS=(
    "NODE_ENV=production"
    "PORT=4173"
    "VITE_REFRESH_INTERVAL=30000"
)

if [ ! -z "$BACKEND_URL" ]; then
    FRONTEND_VARS+=("VITE_API_URL=$BACKEND_URL")
fi

if [ ! -z "$ANALYSIS_URL" ]; then
    FRONTEND_VARS+=("VITE_ANALYSIS_API_URL=$ANALYSIS_URL")
fi

set_service_vars "frontend" "${FRONTEND_VARS[@]}"

# Backend Service
echo "🔹 Backend Service"
BACKEND_VARS=(
    "PORT=8000"
    "HOST=0.0.0.0"
)
set_service_vars "backend" "${BACKEND_VARS[@]}"

# Analysis Service
echo "🔹 Analysis Service"
ANALYSIS_VARS=(
    "ANALYSIS_PORT=8001"
    "ANALYSIS_HOST=0.0.0.0"
)
set_service_vars "analysis" "${ANALYSIS_VARS[@]}"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     ✅ ZMIENNE USTAWIONE!                                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
