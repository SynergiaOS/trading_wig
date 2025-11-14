#!/bin/bash
# Skrypt do dodania serwisu frontend w Railway

set -euo pipefail

# Logging functions
log() {
    echo -e "[\033[36m$(date '+%Y-%m-%d %H:%M:%S')\033[0m] $*"
}

success() {
    log "\033[32m✅ SUCCESS:\033[0m $*"
}

warning() {
    log "\033[33m⚠️  WARNING:\033[0m $*"
}

error_exit() {
    log "\033[31m❌ ERROR:\033[0m $*" >&2
    exit 1
}

info() {
    log "\033[34mℹ️  INFO:\033[0m $*"
}

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🚀 DODAWANIE SERWISU FRONTEND DO RAILWAY                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Sprawdź Railway CLI
if ! command -v railway &> /dev/null; then
    error_exit "Railway CLI nie jest zainstalowany. Zainstaluj: npm install -g @railway/cli"
fi

# Sprawdź autentykację
if ! railway whoami &>/dev/null 2>&1; then
    error_exit "Nie jesteś zalogowany. Zaloguj się: railway login"
fi

USER_INFO=$(railway whoami 2>&1 | head -1)
success "Zalogowany: $USER_INFO"
echo ""

# Sprawdź czy serwis już istnieje
if railway service frontend &>/dev/null 2>&1; then
    warning "Serwis 'frontend' już istnieje!"
    info "Przełączam na serwis frontend..."
    railway service frontend
else
    info "Dodawanie serwisu frontend..."
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 INSTRUKCJE:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Railway CLI wymaga interakcji. Wykonaj następujące kroki:"
    echo ""
    echo "1. Wybierz: 'GitHub Repo'"
    echo "2. Wpisz: SynergiaOS/trading_wig"
    echo "3. Dla zmiennych środowiskowych - naciśnij Enter (pomin)"
    echo ""
    echo "Następnie skrypt automatycznie ustawi zmienne środowiskowe."
    echo ""
    read -p "Naciśnij Enter, aby rozpocząć dodawanie serwisu..."
    echo ""
    
    # Dodaj serwis (wymaga interakcji)
    railway add --service frontend --repo SynergiaOS/trading_wig || {
        error_exit "Nie udało się dodać serwisu. Sprawdź czy projekt jest połączony: railway link"
    }
fi

echo ""
info "Przełączam na serwis frontend..."
railway service frontend

echo ""
log "📋 KROK 2: Ustawianie zmiennych środowiskowych"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Zmienne środowiskowe dla frontendu
FRONTEND_VARS=(
    "NODE_ENV=production"
    "PORT=4173"
    "VITE_REFRESH_INTERVAL=30000"
)

for var in "${FRONTEND_VARS[@]}"; do
    KEY=$(echo "$var" | cut -d'=' -f1)
    VALUE=$(echo "$var" | cut -d'=' -f2-)
    echo -n "   Ustawiam $KEY... "
    
    if railway variables --set "$var" --service frontend &>/dev/null 2>&1; then
        echo "✅"
    else
        # Sprawdź czy zmienna już istnieje
        if railway variables --json 2>/dev/null | grep -q "\"$KEY\":"; then
            echo "⚠️  (już istnieje)"
        else
            echo "❌ (błąd - sprawdź ręcznie)"
        fi
    fi
done

echo ""
success "Zmienne środowiskowe ustawione!"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     ✅ SERWIS FRONTEND DODANY!                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 NASTĘPNE KROKI (w Railway Dashboard):"
echo ""
echo "1. Otwórz Railway Dashboard:"
echo "   https://railway.app"
echo ""
echo "2. Wybierz projekt WIG → Serwis 'frontend'"
echo ""
echo "3. W Settings → Build → Dockerfile Path:"
echo "   Ustaw: Dockerfile.frontend"
echo ""
echo "4. W Settings → Deploy → Health Check:"
echo "   Path: /"
echo "   Timeout: 100"
echo ""
echo "5. W Settings → Networking:"
echo "   Kliknij 'Generate Domain'"
echo ""
echo "6. Po deploy Backend i Analysis, dodaj zmienne:"
echo "   VITE_API_URL=https://backend-production-XXXX.up.railway.app"
echo "   VITE_ANALYSIS_API_URL=https://analysis-production-XXXX.up.railway.app"
echo ""
echo "🎯 Gotowe! Teraz możesz zdeployować serwis frontend 🚀"
echo ""

