#!/bin/bash
# Railway Services Setup Script
# Automatycznie konfiguruje 3 serwisy w Railway

set -e

# ⚠️ NIE ładuj RAILWAY_TOKEN - Railway CLI nie używa tokenu API
# Token jest tylko dla REST API w CI/CD
# Dla CLI użyj: railway login (interaktywne logowanie)

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
    
    # Przygotuj zmienne dla railway add (opcjonalnie można ustawić podczas dodawania)
    local ADD_VARIABLES=""
    if [ ! -z "$VARIABLES" ]; then
        IFS=' ' read -ra VAR_ARRAY <<< "$VARIABLES"
        for var in "${VAR_ARRAY[@]}"; do
            if [[ $var == *"="* ]]; then
                ADD_VARIABLES="$ADD_VARIABLES --variables \"$var\""
            fi
        done
    fi
    
    # Dodaj serwis z zmiennymi (jeśli są)
    if [ ! -z "$ADD_VARIABLES" ]; then
        echo "🔧 Dodaję serwis ze zmiennymi środowiskowymi..."
        eval "railway add --service \"$SERVICE_NAME\" --repo SynergiaOS/trading_wig $ADD_VARIABLES"
    else
        railway add --service "$SERVICE_NAME" --repo SynergiaOS/trading_wig
    fi
    
    # Linkuj do serwisu
    railway service "$SERVICE_NAME"
    
    # Ustaw dodatkowe zmienne środowiskowe (używając --set zgodnie z dokumentacją)
    if [ ! -z "$VARIABLES" ]; then
        echo "🔧 Ustawiam zmienne środowiskowe..."
        IFS=' ' read -ra VAR_ARRAY <<< "$VARIABLES"
        for var in "${VAR_ARRAY[@]}"; do
            if [[ $var == *"="* ]]; then
                # Użyj właściwej składni Railway CLI: --set "KEY=VALUE"
                railway variables --set "$var" --service "$SERVICE_NAME" && echo "   ✅ $(echo $var | cut -d'=' -f1)" || echo "   ⚠️  $(echo $var | cut -d'=' -f1) - sprawdź czy zostało ustawione"
            fi
        done
        echo ""
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
    "PORT=8000 HOST=0.0.0.0 POCKETBASE_URL=http://pocketbase-service.railway.internal:8090 QUESTDB_HOST=questdb-service.railway.internal QUESTDB_PORT=9009 QUESTDB_USER=admin QUESTDB_PASSWORD=quest REDIS_URL=redis://redis-service.railway.internal:6379"

# Analysis Service
add_service "analysis" "Dockerfile.analysis" \
    "ANALYSIS_PORT=8001 ANALYSIS_HOST=0.0.0.0 POCKETBASE_URL=http://pocketbase-service.railway.internal:8090 QUESTDB_HOST=questdb-service.railway.internal QUESTDB_PORT=9009 QUESTDB_USER=admin QUESTDB_PASSWORD=quest REDIS_URL=redis://redis-service.railway.internal:6379"

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
echo "3. ⚠️  WAŻNE: Ustaw zmienne środowiskowe przez Railway Dashboard:"
echo "   - Przejdź do każdego serwisu → Settings → Variables"
echo "   - Zobacz RAILWAY_ENV_SETUP.md dla pełnej listy zmiennych"
echo "   - Lub użyj Railway Dashboard zamiast CLI jeśli widzisz 'ENTER A VARIABLE'"
echo ""
echo "4. Po deploy Backend i Analysis, zaktualizuj Frontend variables:"
echo "   - VITE_API_URL=https://backend-url.railway.app"
echo "   - VITE_ANALYSIS_API_URL=https://analysis-url.railway.app"
echo ""
echo "5. Deploy serwisów:"
echo "   railway up --service frontend"
echo "   railway up --service backend"
echo "   railway up --service analysis"
echo ""
echo "📚 Dokumentacja:"
echo "   - RAILWAY_ENV_SETUP.md - Ręczna konfiguracja zmiennych"
echo "   - RAILWAY_ENV_VARIABLES.md - Kompletna lista zmiennych"
echo ""

