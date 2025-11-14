#!/bin/bash
# Skrypt do ustawienia WSZYSTKICH zmiennych środowiskowych w Railway jednorazowo

set -euo pipefail

# Kolory
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🚀 Railway - Ustaw WSZYSTKIE zmienne jednorazowo       ║${NC}"
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

# Pobierz URL-e serwisów
echo -e "${CYAN}📡 Pobieranie URL-i serwisów...${NC}"
echo ""

BACKEND_URL=""
ANALYSIS_URL=""

# Spróbuj pobrać URL-e z Railway
if railway service backend &>/dev/null 2>&1; then
    echo -e "${BLUE}   Szukam Backend URL...${NC}"
    # Spróbuj różne metody
    BACKEND_DOMAIN=$(railway status --service backend 2>/dev/null | grep -iE "domain|url|https://" | head -1 | grep -oE 'https://[^ ]+' || echo "")
    if [ -z "$BACKEND_DOMAIN" ]; then
        BACKEND_DOMAIN=$(railway variables --json --service backend 2>/dev/null | grep -oE '"RAILWAY_PUBLIC_DOMAIN":"[^"]*"' | cut -d'"' -f4 || echo "")
    fi
    if [ -n "$BACKEND_DOMAIN" ]; then
        if [[ ! "$BACKEND_DOMAIN" =~ ^https:// ]]; then
            BACKEND_URL="https://$BACKEND_DOMAIN"
        else
            BACKEND_URL="$BACKEND_DOMAIN"
        fi
        echo -e "${GREEN}   ✅ Backend URL: $BACKEND_URL${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Nie znaleziono Backend URL automatycznie${NC}"
    fi
fi

if railway service analysis &>/dev/null 2>&1; then
    echo -e "${BLUE}   Szukam Analysis URL...${NC}"
    ANALYSIS_DOMAIN=$(railway status --service analysis 2>/dev/null | grep -iE "domain|url|https://" | head -1 | grep -oE 'https://[^ ]+' || echo "")
    if [ -z "$ANALYSIS_DOMAIN" ]; then
        ANALYSIS_DOMAIN=$(railway variables --json --service analysis 2>/dev/null | grep -oE '"RAILWAY_PUBLIC_DOMAIN":"[^"]*"' | cut -d'"' -f4 || echo "")
    fi
    if [ -n "$ANALYSIS_DOMAIN" ]; then
        if [[ ! "$ANALYSIS_DOMAIN" =~ ^https:// ]]; then
            ANALYSIS_URL="https://$ANALYSIS_DOMAIN"
        else
            ANALYSIS_URL="$ANALYSIS_DOMAIN"
        fi
        echo -e "${GREEN}   ✅ Analysis URL: $ANALYSIS_URL${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Nie znaleziono Analysis URL automatycznie${NC}"
    fi
fi

echo ""

# Jeśli nie znaleziono URL-i, zapytaj użytkownika
if [ -z "$BACKEND_URL" ]; then
    echo -e "${YELLOW}⚠️  Nie znaleziono Backend URL${NC}"
    echo "   Sprawdź w Railway Dashboard → Backend Service → Settings → Networking"
    read -p "   Wpisz Backend URL (lub naciśnij Enter aby pominąć): " BACKEND_URL_INPUT
    if [ -n "$BACKEND_URL_INPUT" ]; then
        BACKEND_URL="$BACKEND_URL_INPUT"
        if [[ ! "$BACKEND_URL" =~ ^https:// ]]; then
            BACKEND_URL="https://$BACKEND_URL"
        fi
    fi
fi

if [ -z "$ANALYSIS_URL" ]; then
    echo -e "${YELLOW}⚠️  Nie znaleziono Analysis URL${NC}"
    echo "   Sprawdź w Railway Dashboard → Analysis Service → Settings → Networking"
    read -p "   Wpisz Analysis URL (lub naciśnij Enter aby pominąć): " ANALYSIS_URL_INPUT
    if [ -n "$ANALYSIS_URL_INPUT" ]; then
        ANALYSIS_URL="$ANALYSIS_URL_INPUT"
        if [[ ! "$ANALYSIS_URL" =~ ^https:// ]]; then
            ANALYSIS_URL="https://$ANALYSIS_URL"
        fi
    fi
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================================================
# FRONTEND SERVICE
# ============================================================================
echo -e "${BLUE}📋 Frontend Service${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if railway service frontend &>/dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend service istnieje${NC}"
    echo ""
    
    set_var "frontend" "NODE_ENV" "production"
    set_var "frontend" "PORT" "4173"
    set_var "frontend" "VITE_REFRESH_INTERVAL" "30000"
    
    if [ -n "$BACKEND_URL" ]; then
        set_var "frontend" "VITE_API_URL" "$BACKEND_URL"
    else
        echo -e "${YELLOW}   ⚠️  VITE_API_URL nie ustawione - brak Backend URL${NC}"
    fi
    
    if [ -n "$ANALYSIS_URL" ]; then
        set_var "frontend" "VITE_ANALYSIS_API_URL" "$ANALYSIS_URL"
    else
        echo -e "${YELLOW}   ⚠️  VITE_ANALYSIS_API_URL nie ustawione - brak Analysis URL${NC}"
    fi
    
    echo ""
else
    echo -e "${YELLOW}⚠️  Frontend service nie istnieje${NC}"
    echo ""
fi

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
    
    set_var "analysis" "PORT" "8001"
    set_var "analysis" "HOST" "0.0.0.0"
    set_var "analysis" "USE_BACKEND_API" "true"
    
    if [ -n "$BACKEND_URL" ]; then
        set_var "analysis" "BACKEND_API_URL" "$BACKEND_URL"
    else
        echo -e "${YELLOW}   ⚠️  BACKEND_API_URL nie ustawione - brak Backend URL${NC}"
    fi
    
    echo ""
else
    echo -e "${YELLOW}⚠️  Analysis service nie istnieje${NC}"
    echo ""
fi

# ============================================================================
# PODSUMOWANIE
# ============================================================================
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✅ WSZYSTKIE ZMIENNE USTAWIONE!                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📊 Podsumowanie:${NC}"
echo ""

if [ -n "$BACKEND_URL" ]; then
    echo -e "${GREEN}✅ Backend URL: $BACKEND_URL${NC}"
else
    echo -e "${YELLOW}⚠️  Backend URL: nie ustawione${NC}"
fi

if [ -n "$ANALYSIS_URL" ]; then
    echo -e "${GREEN}✅ Analysis URL: $ANALYSIS_URL${NC}"
else
    echo -e "${YELLOW}⚠️  Analysis URL: nie ustawione${NC}"
fi

echo ""
echo -e "${BLUE}📝 Sprawdź zmienne w Railway Dashboard:${NC}"
echo "   railway open"
echo ""
echo -e "${YELLOW}⚠️  Jeśli URL-e nie zostały ustawione automatycznie:${NC}"
echo "   1. Railway Dashboard → Services → Settings → Networking"
echo "   2. Skopiuj Public Domain URL-e"
echo "   3. Dodaj ręcznie do Variables:"
echo "      - Frontend: VITE_API_URL, VITE_ANALYSIS_API_URL"
echo "      - Analysis: BACKEND_API_URL"
echo ""

