#!/bin/bash
# DO IT ALL V2 - Ulepszona wersja automatycznej konfiguracji Railway
# Ta wersja naprawia problemy z oryginalnym skryptem i dodaje lepsze logowanie

set -euo pipefail

# Configuration
PROJECT_NAME="${PROJECT_NAME:-WIG}"
REPO="${REPO:-SynergiaOS/trading_wig}"
SERVICES=("frontend" "backend" "analysis")

# Logging function with timestamp and colors
log() {
    echo -e "[\033[36m$(date '+%Y-%m-%d %H:%M:%S')\033[0m] $*"
}

error_exit() {
    log "\033[31m❌ ERROR:\033[0m $*" >&2
    exit 1
}

warning() {
    log "\033[33m⚠️  WARNING:\033[0m $*"
}

success() {
    log "\033[32m✅ SUCCESS:\033[0m $*"
}

info() {
    log "\033[34mℹ️  INFO:\033[0m $*"
}

# Header
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🚀 RAILWAY - DO IT ALL V2                                ║"
echo "║     Ulepszona wersja z lepszym logowaniem i obsługą błędów   ║"
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

# Sprawdź czy jesteśmy zalogowani
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

# Spróbuj pobrać status projektu
PROJECT_STATUS=$(railway status 2>&1 || echo "NOT_CONNECTED")
PROJECT_LINKED=false

if [[ "$PROJECT_STATUS" != *"NOT_CONNECTED"* ]] && [[ "$PROJECT_STATUS" != *"No project linked"* ]]; then
    success "Projekt połączony:"
    echo "$PROJECT_STATUS" | head -5 | sed 's/^/   /'
    PROJECT_LINKED=true
else
    warning "Projekt nie jest połączony"
    echo ""
    info "Próbuję połączyć automatycznie..."
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
    # Spróbuj przełączyć na serwis
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
    log "📋 KROK 5: Ustawianie zmiennych środowiskowych"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Funkcja do ustawiania zmiennych z lepszą obsługą błędów
    set_vars() {
        local SERVICE=$1
        shift
        local VARS=("$@")
        
        echo "🔧 Serwis: $SERVICE"
        
        # Przełącz na serwis
        if ! railway service "$SERVICE" &>/dev/null 2>&1; then
            warning "Nie można przełączyć na serwis $SERVICE"
            return 1
        fi
        
        for var in "${VARS[@]}"; do
            if [[ $var == *"="* ]] && [[ ! $var == \#* ]]; then
                KEY=$(echo "$var" | cut -d'=' -f1)
                VALUE=$(echo "$var" | cut -d'=' -f2-)
                echo -n "   $KEY... "
                
                # Spróbuj ustawić zmienną
                if railway variables --set "$KEY=$VALUE" --service "$SERVICE" &>/dev/null 2>&1; then
                    echo "✅"
                else
                    # Sprawdź czy zmienna już istnieje
                    if railway variables --json 2>/dev/null | grep -q "\"$KEY\":"; then
                        echo "⚠️  (już istnieje)"
                    else
                        echo "❌ (błąd)"
                    fi
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
            "USE_REALTIME_API=true"
        )
        set_vars "backend" "${BACKEND_VARS[@]}"
    fi
    
    # Analysis
    if [[ " ${EXISTING_SERVICES[@]} " =~ " analysis " ]]; then
        # Pobierz Backend URL jeśli backend istnieje
        BACKEND_URL=""
        if [[ " ${EXISTING_SERVICES[@]} " =~ " backend " ]]; then
            info "Pobieranie Backend URL..."
            BACKEND_URL=$(railway variables --json --service backend 2>/dev/null | grep -o '"RAILWAY_PUBLIC_DOMAIN":"[^"]*"' | cut -d'"' -f4 || echo "")
            if [ -z "$BACKEND_URL" ]; then
                # Spróbuj pobrać z Railway status
                BACKEND_URL=$(railway status --service backend 2>/dev/null | grep -i "url\|domain" | head -1 | grep -o 'https://[^ ]*' || echo "")
            fi
            if [ -n "$BACKEND_URL" ] && [[ ! "$BACKEND_URL" =~ ^https:// ]]; then
                BACKEND_URL="https://$BACKEND_URL"
            fi
        fi
        
        ANALYSIS_VARS=(
            "PORT=8001"
            "HOST=0.0.0.0"
            "USE_BACKEND_API=true"
        )
        
        # Dodaj BACKEND_API_URL jeśli mamy URL
        if [ -n "$BACKEND_URL" ]; then
            ANALYSIS_VARS+=("BACKEND_API_URL=$BACKEND_URL")
            info "Używam Backend URL: $BACKEND_URL"
        else
            warning "Nie można automatycznie pobrać Backend URL"
            warning "Ustaw BACKEND_API_URL ręcznie w Railway Dashboard"
        fi
        
        set_vars "analysis" "${ANALYSIS_VARS[@]}"
    fi
else
    warning "Pomijanie ustawiania zmiennych (projekt niepołączony lub brak serwisów)"
fi
echo ""

# ============================================================================
# KROK 6: Dodatkowe informacje
# ============================================================================
log "📋 KROK 6: Dodatkowe informacje"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Sprawdź czy mamy jakieś zmienne już ustawione
if [ "$PROJECT_LINKED" = true ]; then
    info "Aktualne zmienne w projekcie:"
    railway variables --json 2>/dev/null | head -20 || warning "Nie można pobrać zmiennych"
    echo ""
fi

# ============================================================================
# KROK 7: Podsumowanie i instrukcje
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
echo "6. Opcjonalnie: Uruchom skrypt weryfikacji:"
echo "   ./railway-post-deploy-verify.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 DOKUMENTACJA:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📘 railway-setup-commands.txt - Wszystkie instrukcje"
echo "  📋 railway-setup-checklist.md - Checklist"
echo "  📗 RAILWAY_COMPLETE_GUIDE.md - Kompletny przewodnik"
echo "  🔧 DO_IT_ALL_V2.sh - Ta ulepszona wersja"
echo ""
echo "🎯 Gotowe! Resztę zrobisz przez Railway Dashboard 🚀"
echo ""