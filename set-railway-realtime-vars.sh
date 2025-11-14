#!/bin/bash
# Skrypt do ustawienia zmiennych środowiskowych dla Real-Time API w Railway

set -euo pipefail

# Kolory
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🔧 Railway - Real-Time API Variables Setup              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Sprawdź Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI nie jest zainstalowany${NC}"
    echo "Zainstaluj: npm install -g @railway/cli"
    exit 1
fi

# Sprawdź autentykację
if ! railway whoami &>/dev/null 2>&1; then
    echo -e "${RED}❌ Nie jesteś zalogowany${NC}"
    echo "Zaloguj się: railway login"
    exit 1
fi

echo -e "${GREEN}✅ Railway CLI OK${NC}"
echo ""

# Funkcja do ustawiania zmiennych
set_var() {
    local SERVICE=$1
    local KEY=$2
    local VALUE=$3
    
    echo -n "   $KEY = $VALUE ... "
    
    if railway variables --set "$KEY=$VALUE" --service "$SERVICE" &>/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  (sprawdź czy już istnieje)${NC}"
        return 1
    fi
}

# ============================================================================
# BACKEND SERVICE
# ============================================================================
echo -e "${BLUE}📋 Backend Service${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if railway service backend &>/dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend service istnieje${NC}"
    echo ""
    
    set_var "backend" "PORT" "8000"
    set_var "backend" "HOST" "0.0.0.0"
    set_var "backend" "USE_REALTIME_API" "true"
    
    echo ""
else
    echo -e "${YELLOW}⚠️  Backend service nie istnieje${NC}"
    echo "   Utwórz go przez Railway Dashboard"
    echo ""
fi

# ============================================================================
# ANALYSIS SERVICE
# ============================================================================
echo -e "${BLUE}📋 Analysis Service${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if railway service analysis &>/dev/null 2>&1; then
    echo -e "${GREEN}✅ Analysis service istnieje${NC}"
    echo ""
    
    # Pobierz Backend URL
    echo -e "${YELLOW}⚠️  Potrzebuję URL Backend serwisu${NC}"
    echo "   Sprawdź w Railway Dashboard → Backend Service → Settings → Networking"
    echo "   Format: https://backend-production-XXXX.up.railway.app"
    echo ""
    read -p "   Wpisz Backend URL (lub naciśnij Enter aby pominąć): " BACKEND_URL
    
    set_var "analysis" "PORT" "8001"
    set_var "analysis" "HOST" "0.0.0.0"
    set_var "analysis" "USE_BACKEND_API" "true"
    
    if [ -n "$BACKEND_URL" ]; then
        set_var "analysis" "BACKEND_API_URL" "$BACKEND_URL"
    else
        echo -e "${YELLOW}   ⚠️  BACKEND_API_URL nie ustawione - ustaw ręcznie!${NC}"
    fi
    
    echo ""
else
    echo -e "${YELLOW}⚠️  Analysis service nie istnieje${NC}"
    echo "   Utwórz go przez Railway Dashboard"
    echo ""
fi

# ============================================================================
# FRONTEND SERVICE
# ============================================================================
echo -e "${BLUE}📋 Frontend Service${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if railway service frontend &>/dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend service istnieje${NC}"
    echo ""
    
    # Pobierz URL-e
    echo -e "${YELLOW}⚠️  Potrzebuję URL-e Backend i Analysis${NC}"
    echo "   Sprawdź w Railway Dashboard → Services → Settings → Networking"
    echo ""
    read -p "   Backend URL (lub Enter aby pominąć): " BACKEND_URL
    read -p "   Analysis URL (lub Enter aby pominąć): " ANALYSIS_URL
    
    set_var "frontend" "NODE_ENV" "production"
    set_var "frontend" "PORT" "4173"
    set_var "frontend" "VITE_REFRESH_INTERVAL" "30000"
    
    if [ -n "$BACKEND_URL" ]; then
        set_var "frontend" "VITE_API_URL" "$BACKEND_URL"
    else
        echo -e "${YELLOW}   ⚠️  VITE_API_URL nie ustawione - ustaw ręcznie!${NC}"
    fi
    
    if [ -n "$ANALYSIS_URL" ]; then
        set_var "frontend" "VITE_ANALYSIS_API_URL" "$ANALYSIS_URL"
    else
        echo -e "${YELLOW}   ⚠️  VITE_ANALYSIS_API_URL nie ustawione - ustaw ręcznie!${NC}"
    fi
    
    echo ""
else
    echo -e "${YELLOW}⚠️  Frontend service nie istnieje${NC}"
    echo "   Utwórz go przez Railway Dashboard"
    echo ""
fi

# ============================================================================
# PODSUMOWANIE
# ============================================================================
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✅ KONFIGURACJA ZAKOŃCZONA                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📝 Sprawdź zmienne w Railway Dashboard:${NC}"
echo "   railway open"
echo ""
echo -e "${YELLOW}⚠️  Jeśli nie ustawiłeś URL-i, zrób to ręcznie:${NC}"
echo "   1. Railway Dashboard → Services → Settings → Networking"
echo "   2. Skopiuj Public Domain URL-e"
echo "   3. Dodaj do Variables:"
echo "      - Analysis: BACKEND_API_URL"
echo "      - Frontend: VITE_API_URL, VITE_ANALYSIS_API_URL"
echo ""

