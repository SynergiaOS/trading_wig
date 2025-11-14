#!/bin/bash
# DO IT ALL - Automatycznie wykonuje wszystkie możliwe kroki
# Ten skrypt robi wszystko co może być zrobione automatycznie

set -euo pipefail

# Configuration
PROJECT_NAME="${PROJECT_NAME:-WIG}"
REPO="${REPO:-SynergiaOS/trading_wig}"
SERVICES=("frontend" "backend" "analysis")

# Logging function with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

error_exit() {
    log "❌ ERROR: $*" >&2
    exit 1
}

warning() {
    log "⚠️  WARNING: $*"
}

success() {
    log "✅ SUCCESS: $*"
}

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🚀 RAILWAY - DO IT ALL                                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Ten skrypt automatycznie wykonuje wszystkie możliwe kroki"
echo "konfiguracji Railway. Reszta musisz zrobić przez Dashboard."
echo ""

# ============================================================================
# KROK 1: Sprawdź Railway CLI
# ============================================================================
log "📋 KROK 1: Sprawdzanie Railway CLI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if ! command -v railway &> /dev/null; then
    error_exit "Railway CLI nie jest zainstalowany. Zainstaluj: npm install -g @railway/cli"
fi

RAILWAY_VERSION=$(railway --version 2>&1 | head -1)
success "Railway CLI zainstalowany: $RAILWAY_VERSION"
echo ""

# ============================================================================
# KROK 2: Sprawdź autentykację
# ============================================================================
log "📋 KROK 2: Sprawdzanie autentykacji"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Usuń RAILWAY_TOKEN jeśli jest ustawiona (blokuje CLI)
unset RAILWAY_TOKEN

if railway whoami &>/dev/null 2>&1; then
    USER_INFO=$(railway whoami 2>&1 | head -1)
    success "Zalogowany: $USER_INFO"
else
    error_exit "Nie jesteś zalogowany. Zaloguj się: railway login"
fi

echo ""

# ============================================================================
# KROK 3: Połącz projekt
# ============================================================================
log "📋 KROK 3: Łączenie projektu"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if railway status &>/dev/null 2>&1; then
    success "Projekt połączony:"
    railway status 2>&1 | head -5
    PROJECT_LINKED=true
else
    warning "Projekt nie jest połączony"
    echo ""
    log "Próbuję połączyć..."
    echo "Wybierz projekt '$PROJECT_NAME' z listy (jeśli widzisz prompt)"
    echo ""
    
    # Próbuj połączyć (może wymagać interakcji)
    if railway link 2>&1 | head -5; then
        PROJECT_LINKED=true
        success "Projekt połączony"
    else
        PROJECT_LINKED=false
        warning "Nie udało się połączyć automatycznie"
        echo "   Uruchom ręcznie: railway link"
        echo "   Wybierz projekt: $PROJECT_NAME"
    fi
fi

echo ""

# ============================================================================
# KROK 4: Sprawdź serwisy
# ============================================================================
log "📋 KROK 4: Sprawdzanie serwisów"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

EXISTING_SERVICES=()
MISSING_SERVICES=()

for service in "${SERVICES[@]}"; do
    if railway service "$service" &>/dev/null 2>&1; then
        success "$service - istnieje"
        EXISTING_SERVICES+=("$service")
    else
        warning "$service - nie istnieje"
        MISSING_SERVICES+=("$service")
    fi
done

echo ""

# ============================================================================
# KROK 5: Ustaw zmienne dla istniejących serwisów
# ============================================================================
if [ "$PROJECT_LINKED" = true ] && [ ${#EXISTING_SERVICES[@]} -gt 0 ]; then
    echo "📋 KROK 5: Ustawianie zmiennych środowiskowych"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Funkcja do ustawiania zmiennych
    set_vars() {
        local SERVICE=$1
        shift
        local VARS=("$@")
        
        echo "🔧 Serwis: $SERVICE"
        
        # Przełącz na serwis
        railway service "$SERVICE" &>/dev/null 2>&1 || return 1
        
        for var in "${VARS[@]}"; do
            if [[ $var == *"="* ]] && [[ ! $var == \#* ]]; then
                KEY=$(echo "$var" | cut -d'=' -f1)
                echo -n "   $KEY... "
                if railway variables --set "$var" --service "$SERVICE" &>/dev/null 2>&1; then
                    echo "✅"
                else
                    echo "⚠️  (może już istnieje)"
                fi
            fi
        done
        echo ""
    }
    
    # Frontend
    if [[ " ${EXISTING_SERVICES[@]} " =~ " frontend " ]]; then
        FRONTEND_VARS=(
            "NODE_ENV=production"
            "PORT=4173"
            "VITE_REFRESH_INTERVAL=30000"
        )
        set_vars "frontend" "${FRONTEND_VARS[@]}"
    fi
    
    # Backend
    if [[ " ${EXISTING_SERVICES[@]} " =~ " backend " ]]; then
        BACKEND_VARS=(
            "PORT=8000"
            "HOST=0.0.0.0"
        )
        set_vars "backend" "${BACKEND_VARS[@]}"
    fi
    
    # Analysis
    if [[ " ${EXISTING_SERVICES[@]} " =~ " analysis " ]]; then
        ANALYSIS_VARS=(
            "ANALYSIS_PORT=8001"
            "ANALYSIS_HOST=0.0.0.0"
        )
        set_vars "analysis" "${ANALYSIS_VARS[@]}"
    fi
fi

# ============================================================================
# KROK 6: Podsumowanie i instrukcje
# ============================================================================
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     ✅ AUTOMATYCZNA KONFIGURACJA ZAKOŃCZONA!                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

log "📊 PODSUMOWANIE:"
echo ""
success "Railway CLI: Zainstalowany i zalogowany"
if [ "$PROJECT_LINKED" = true ]; then
    success "Projekt: Połączony"
    railway status 2>&1 | head -3 | sed 's/^/   /'
else
    warning "Projekt: Nie połączony (uruchom: railway link)"
fi
echo ""

if [ ${#EXISTING_SERVICES[@]} -gt 0 ]; then
    success "Istniejące serwisy (zmienne ustawione):"
    for service in "${EXISTING_SERVICES[@]}"; do
        echo "   - $service"
    done
    echo ""
fi

if [ ${#MISSING_SERVICES[@]} -gt 0 ]; then
    warning "Brakujące serwisy (dodaj przez Dashboard):"
    for service in "${MISSING_SERVICES[@]}"; do
        echo "   - $service"
    done
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 CO DALEJ (przez Railway Dashboard):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Otwórz Railway Dashboard:"
echo "   https://railway.app"
echo ""
echo "2. Dodaj brakujące serwisy:"
if [ ${#MISSING_SERVICES[@]} -gt 0 ]; then
    for service in "${MISSING_SERVICES[@]}"; do
        echo "   - $service"
    done
else
    echo "   (wszystkie serwisy już istnieją ✅)"
fi
echo ""

echo "3. Dla każdego serwisu ustaw:"
echo "   - Dockerfile Path (Dockerfile.frontend/backend/analysis)"
echo "   - Health Check Path (/ dla frontend, /data dla backend, /api/analysis dla analysis)"
echo "   - Generate Domain"
echo ""

echo "4. Deploy serwisów:"
echo "   - Railway Dashboard → Serwis → Deploy"
echo ""

echo "5. Po deploy Backend i Analysis:"
echo "   - Skopiuj ich URL-e"
echo "   - Dodaj do Frontend: VITE_API_URL i VITE_ANALYSIS_API_URL"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 DOKUMENTACJA:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📘 railway-setup-commands.txt - Wszystkie instrukcje"
echo "  📋 railway-setup-checklist.md - Checklist"
echo "  📗 RAILWAY_COMPLETE_GUIDE.md - Kompletny przewodnik"
echo ""

echo "🎯 Gotowe! Resztę zrobisz przez Railway Dashboard 🚀"
echo ""

