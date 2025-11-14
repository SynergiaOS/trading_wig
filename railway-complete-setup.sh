#!/bin/bash
# Railway Complete Setup - Automatycznie konfiguruje wszystko co się da
# Wykonuje wszystkie możliwe kroki automatycznie

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🚀 RAILWAY COMPLETE SETUP                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_NAME="WIG"
REPO="SynergiaOS/trading_wig"

# ============================================================================
# KROK 1: Przygotowanie
# ============================================================================
echo "📋 KROK 1: Przygotowanie"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Sprawdź Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI nie jest zainstalowany"
    echo "   Zainstaluj: npm install -g @railway/cli"
    exit 1
fi

echo "✅ Railway CLI zainstalowany"
echo ""

# Sprawdź czy zalogowany
if railway whoami &>/dev/null; then
    echo "✅ Zalogowany do Railway: $(railway whoami | head -1)"
else
    echo "⚠️  Nie jesteś zalogowany"
    echo "   Musisz uruchomić: railway login"
    echo "   To otworzy przeglądarkę do autoryzacji"
    exit 1
fi

echo ""

# Sprawdź czy projekt jest połączony
if railway status &>/dev/null; then
    echo "✅ Projekt połączony:"
    railway status | head -3
    echo ""
else
    echo "⚠️  Projekt nie jest połączony"
    echo "   Próbuję połączyć..."
    echo ""
    echo "   Musisz wybrać projekt 'WIG' z listy"
    railway link || {
        echo "   ❌ Nie udało się połączyć automatycznie"
        echo "   Uruchom ręcznie: railway link"
        exit 1
    }
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ============================================================================
# KROK 2: Sprawdź istniejące serwisy
# ============================================================================
echo "📦 KROK 2: Sprawdzanie istniejących serwisów"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Lista serwisów do sprawdzenia
SERVICES=("frontend" "backend" "analysis")
EXISTING_SERVICES=()
MISSING_SERVICES=()

for service in "${SERVICES[@]}"; do
    if railway service "$service" &>/dev/null 2>&1; then
        echo "✅ Serwis '$service' istnieje"
        EXISTING_SERVICES+=("$service")
    else
        echo "⚠️  Serwis '$service' nie istnieje"
        MISSING_SERVICES+=("$service")
    fi
done

echo ""

# ============================================================================
# KROK 3: Dodaj brakujące serwisy
# ============================================================================
if [ ${#MISSING_SERVICES[@]} -gt 0 ]; then
    echo "🔧 KROK 3: Dodawanie brakujących serwisów"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Musisz dodać następujące serwisy przez Railway Dashboard:"
    echo ""
    for service in "${MISSING_SERVICES[@]}"; do
        echo "   - $service"
    done
    echo ""
    echo "Otwórz Railway Dashboard: https://railway.app"
    echo "I dodaj serwisy zgodnie z instrukcjami w: railway-setup-commands.txt"
    echo ""
    read -p "Naciśnij Enter gdy wszystkie serwisy będą dodane..."
    echo ""
fi

# ============================================================================
# KROK 4: Ustaw zmienne środowiskowe
# ============================================================================
echo "🔧 KROK 4: Ustawianie zmiennych środowiskowych"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Funkcja do ustawiania zmiennych
set_service_variables() {
    local SERVICE=$1
    shift
    local VARS=("$@")
    
    echo "📦 Serwis: $SERVICE"
    
    # Przełącz na serwis
    if ! railway service "$SERVICE" &>/dev/null 2>&1; then
        echo "   ⚠️  Serwis '$SERVICE' nie istnieje - pomijam"
        echo ""
        return 1
    fi
    
    railway service "$SERVICE" &>/dev/null
    
    for var in "${VARS[@]}"; do
        if [[ $var == *"="* ]]; then
            KEY=$(echo "$var" | cut -d'=' -f1)
            VALUE=$(echo "$var" | cut -d'=' -f2-)
            echo "   🔧 Ustawiam: $KEY"
            if railway variables --set "$var" --service "$SERVICE" 2>/dev/null; then
                echo "      ✅ Ustawiono"
            else
                echo "      ⚠️  Nie udało się (możliwe że już istnieje)"
            fi
        fi
    done
    echo ""
}

# Frontend Service
echo "🔹 Frontend Service"
FRONTEND_VARS=(
    "NODE_ENV=production"
    "PORT=4173"
    "VITE_REFRESH_INTERVAL=30000"
)

# Zapytaj o URL-e (jeśli już są)
read -p "Podaj Backend URL (lub Enter aby pominąć teraz): " BACKEND_URL
read -p "Podaj Analysis URL (lub Enter aby pominąć teraz): " ANALYSIS_URL

if [ ! -z "$BACKEND_URL" ] && [[ "$BACKEND_URL" != "" ]]; then
    FRONTEND_VARS+=("VITE_API_URL=$BACKEND_URL")
fi

if [ ! -z "$ANALYSIS_URL" ] && [[ "$ANALYSIS_URL" != "" ]]; then
    FRONTEND_VARS+=("VITE_ANALYSIS_API_URL=$ANALYSIS_URL")
fi

set_service_variables "frontend" "${FRONTEND_VARS[@]}"

# Backend Service
echo "🔹 Backend Service"
BACKEND_VARS=(
    "PORT=8000"
    "HOST=0.0.0.0"
)
set_service_variables "backend" "${BACKEND_VARS[@]}"

# Analysis Service
echo "🔹 Analysis Service"
ANALYSIS_VARS=(
    "ANALYSIS_PORT=8001"
    "ANALYSIS_HOST=0.0.0.0"
)
set_service_variables "analysis" "${ANALYSIS_VARS[@]}"

# ============================================================================
# KROK 5: Podsumowanie
# ============================================================================
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     ✅ KONFIGURACJA ZAKOŃCZONA!                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "📋 Podsumowanie:"
echo ""
echo "✅ Projekt: $PROJECT_NAME"
echo "✅ Railway CLI: Zalogowany"
echo ""

if [ ${#EXISTING_SERVICES[@]} -gt 0 ]; then
    echo "✅ Istniejące serwisy:"
    for service in "${EXISTING_SERVICES[@]}"; do
        echo "   - $service"
    done
    echo ""
fi

if [ ${#MISSING_SERVICES[@]} -gt 0 ]; then
    echo "⚠️  Brakujące serwisy (dodaj przez Dashboard):"
    for service in "${MISSING_SERVICES[@]}"; do
        echo "   - $service"
    done
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 NASTĘPNE KROKI:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ${#MISSING_SERVICES[@]} -gt 0 ]; then
    echo "1. Dodaj brakujące serwisy przez Railway Dashboard:"
    echo "   https://railway.app"
    echo "   Zobacz instrukcje w: railway-setup-commands.txt"
    echo ""
fi

echo "2. Dla każdego serwisu ustaw Dockerfile Path:"
echo "   - frontend → Dockerfile.frontend"
echo "   - backend → Dockerfile.backend"
echo "   - analysis → Dockerfile.analysis"
echo ""

echo "3. Deploy serwisów:"
echo "   - Railway Dashboard → Serwis → Deploy"
echo ""

echo "4. Po deploy, zaktualizuj Frontend variables:"
if [ -z "$BACKEND_URL" ] || [ -z "$ANALYSIS_URL" ]; then
    echo "   - Pobierz URL-e z Railway Dashboard"
    echo "   - Dodaj VITE_API_URL i VITE_ANALYSIS_API_URL do Frontend"
fi
echo ""

echo "5. Sprawdź status:"
echo "   railway status"
echo "   railway variables --service frontend"
echo "   railway variables --service backend"
echo "   railway variables --service analysis"
echo ""

echo "📚 Dokumentacja:"
echo "   - railway-setup-commands.txt - Wszystkie instrukcje"
echo "   - railway-setup-checklist.md - Checklist"
echo "   - RAILWAY_COMPLETE_GUIDE.md - Kompletny przewodnik"
echo ""

