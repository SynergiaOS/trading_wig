#!/bin/bash
# Railway Services Setup Script
# Automatycznie konfiguruje 3 serwisy w Railway

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🚀 RAILWAY SERVICES SETUP                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Sprawdź czy railway CLI jest zainstalowany
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI nie jest zainstalowany!"
    echo "Zainstaluj: npm install -g @railway/cli"
    exit 1
fi

# Sprawdź czy użytkownik jest zalogowany
if ! railway whoami &> /dev/null; then
    echo "⚠️  Nie jesteś zalogowany do Railway"
    echo "Uruchom: railway login"
    exit 1
fi

echo "✅ Railway CLI zainstalowany"
echo "✅ Zalogowany jako: $(railway whoami)"
echo ""

# Pobierz informacje o projekcie
PROJECT_INFO=$(railway status 2>&1)
echo "📋 Aktualny projekt:"
echo "$PROJECT_INFO"
echo ""

# Funkcja do dodawania serwisu
add_service() {
    local SERVICE_NAME=$1
    local DOCKERFILE=$2
    local VARIABLES=$3
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Dodaję serwis: $SERVICE_NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Dodaj serwis (interaktywnie)
    railway add --service "$SERVICE_NAME" --repo SynergiaOS/trading_wig
    
    # Linkuj do serwisu
    railway service "$SERVICE_NAME"
    
    # Ustaw zmienne środowiskowe
    if [ ! -z "$VARIABLES" ]; then
        echo "🔧 Ustawiam zmienne środowiskowe..."
        for var in $VARIABLES; do
            railway variables --set "$var" --service "$SERVICE_NAME"
        done
    fi
    
    echo "✅ Serwis $SERVICE_NAME skonfigurowany"
    echo ""
    echo "⚠️  WAŻNE: Ustaw Dockerfile Path w Railway Dashboard:"
    echo "   Settings → Build → Dockerfile Path: $DOCKERFILE"
    echo ""
}

# Dodaj serwisy
echo "🚀 Rozpoczynam konfigurację serwisów..."
echo ""

# Frontend Service
add_service "frontend" "Dockerfile.frontend" \
    "NODE_ENV=production PORT=4173"

# Backend Service  
add_service "backend" "Dockerfile.backend" \
    "PORT=8000 HOST=0.0.0.0"

# Analysis Service
add_service "analysis" "Dockerfile.analysis" \
    "ANALYSIS_PORT=8001 ANALYSIS_HOST=0.0.0.0"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     ✅ KONFIGURACJA ZAKOŃCZONA!                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 NASTĘPNE KROKI:"
echo ""
echo "1. Otwórz Railway Dashboard:"
echo "   railway open"
echo ""
echo "2. Dla każdego serwisu ustaw Dockerfile Path:"
echo "   - frontend → Dockerfile.frontend"
echo "   - backend → Dockerfile.backend"
echo "   - analysis → Dockerfile.analysis"
echo ""
echo "3. Po deploy Backend i Analysis, zaktualizuj Frontend variables:"
echo "   railway variables --set 'VITE_API_URL=https://backend-url.railway.app' --service frontend"
echo "   railway variables --set 'VITE_ANALYSIS_API_URL=https://analysis-url.railway.app' --service frontend"
echo ""
echo "4. Deploy serwisów:"
echo "   railway up --service frontend"
echo "   railway up --service backend"
echo "   railway up --service analysis"
echo ""

