#!/bin/bash
# Railway Auto Setup Script
# Automatycznie przygotowuje wszystko do konfiguracji Railway

set -euo pipefail

# Configuration
PROJECT_NAME="${PROJECT_NAME:-WIG}"
REPO="${REPO:-SynergiaOS/trading_wig}"

# Logging functions
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
echo "║     🚀 RAILWAY AUTO SETUP                                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# KROK 1: Sprawdź aktualny stan
# ============================================================================
log "📋 Sprawdzanie aktualnego stanu..."
echo ""

# Sprawdź czy Railway CLI jest zainstalowany
if command -v railway &> /dev/null; then
    RAILWAY_VERSION=$(railway --version 2>&1 | head -1)
    success "Railway CLI zainstalowany: $RAILWAY_VERSION"
else
    warning "Railway CLI nie jest zainstalowany. Zainstaluj: npm install -g @railway/cli"
fi

# Sprawdź status projektu
if railway status &>/dev/null; then
    success "Projekt połączony:"
    railway status | head -3
else
    warning "Projekt nie jest połączony. Uruchom: railway link"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ============================================================================
# KROK 2: Przygotuj pliki konfiguracyjne
# ============================================================================
log "📁 Przygotowywanie plików konfiguracyjnych..."
echo ""

# Sprawdź czy Dockerfiles istnieją
for dockerfile in Dockerfile.frontend Dockerfile.backend Dockerfile.analysis; do
    if [ -f "$dockerfile" ]; then
        success "$dockerfile - OK"
    else
        error_exit "$dockerfile - NIE ZNALEZIONO!"
    fi
done

echo ""

# ============================================================================
# KROK 3: Generuj komendy do wykonania
# ============================================================================
log "📝 Generowanie komend do wykonania..."
echo ""

OUTPUT_FILE="railway-setup-commands.txt"

cat > "$OUTPUT_FILE" << 'EOF'
# ============================================================================
# RAILWAY SETUP - Wszystkie komendy do wykonania
# ============================================================================

# 1. OTWÓRZ RAILWAY DASHBOARD
# https://railway.app

# 2. UTWÓRZ PROJEKT (jeśli nie istnieje)
# - Kliknij "New Project"
# - Nazwa: WIG
# - Environment: production

# 3. DODAJ FRONTEND SERVICE
# ============================================================================
# W Railway Dashboard:
# - Kliknij "+ New Service"
# - Wybierz "GitHub Repo" → SynergiaOS/trading_wig
# - Nazwa: frontend
#
# Settings → Build:
#   Dockerfile Path: Dockerfile.frontend
#
# Settings → Deploy:
#   Health Check Path: /
#   Health Check Timeout: 100
#   Restart Policy: ON_FAILURE
#   Max Retries: 10
#
# Settings → Networking:
#   Generate Domain (kliknij)
#
# Settings → Variables (dodaj):
EOF

# Dodaj zmienne dla Frontend
cat >> "$OUTPUT_FILE" << EOF
NODE_ENV=production
PORT=4173
VITE_REFRESH_INTERVAL=30000
# UWAGA: VITE_API_URL i VITE_ANALYSIS_API_URL dodasz po deploy backend/analysis
EOF

cat >> "$OUTPUT_FILE" << 'EOF'

# 4. DODAJ BACKEND SERVICE
# ============================================================================
# W Railway Dashboard:
# - Kliknij "+ New Service"
# - Wybierz "GitHub Repo" → SynergiaOS/trading_wig
# - Nazwa: backend
#
# Settings → Build:
#   Dockerfile Path: Dockerfile.backend
#
# Settings → Deploy:
#   Health Check Path: /data
#   Health Check Timeout: 100
#   Restart Policy: ON_FAILURE
#   Max Retries: 10
#
# Settings → Networking:
#   Generate Domain (kliknij)
#   📝 SKOPIUJ URL (będzie potrzebny później)
#
# Settings → Variables (dodaj):
EOF

# Dodaj zmienne dla Backend
cat >> "$OUTPUT_FILE" << EOF
PORT=8000
HOST=0.0.0.0
# Opcjonalnie (jeśli masz osobne serwisy dla baz danych):
# POCKETBASE_URL=http://pocketbase.railway.internal:8090
# QUESTDB_HOST=questdb.railway.internal
# QUESTDB_PORT=9009
# QUESTDB_USER=admin
# QUESTDB_PASSWORD=quest
# REDIS_URL=redis://redis.railway.internal:6379
EOF

cat >> "$OUTPUT_FILE" << 'EOF'

# 5. DODAJ ANALYSIS SERVICE
# ============================================================================
# W Railway Dashboard:
# - Kliknij "+ New Service"
# - Wybierz "GitHub Repo" → SynergiaOS/trading_wig
# - Nazwa: analysis
#
# Settings → Build:
#   Dockerfile Path: Dockerfile.analysis
#
# Settings → Deploy:
#   Health Check Path: /api/analysis
#   Health Check Timeout: 100
#   Restart Policy: ON_FAILURE
#   Max Retries: 10
#
# Settings → Networking:
#   Generate Domain (kliknij)
#   📝 SKOPIUJ URL (będzie potrzebny później)
#
# Settings → Variables (dodaj):
EOF

# Dodaj zmienne dla Analysis
cat >> "$OUTPUT_FILE" << EOF
ANALYSIS_PORT=8001
ANALYSIS_HOST=0.0.0.0
# Opcjonalnie (te same co Backend):
# POCKETBASE_URL=http://pocketbase.railway.internal:8090
# QUESTDB_HOST=questdb.railway.internal
# QUESTDB_PORT=9009
# QUESTDB_USER=admin
# QUESTDB_PASSWORD=quest
# REDIS_URL=redis://redis.railway.internal:6379
EOF

cat >> "$OUTPUT_FILE" << 'EOF'

# 6. DEPLOY SERWISÓW
# ============================================================================
# W Railway Dashboard:
# - Dla każdego serwisu kliknij "Deploy"
# - Zaczekaj na zakończenie builda i deploy
# - Sprawdź czy serwis działa (zielony status)

# 7. ZAKTUALIZUJ FRONTEND VARIABLES
# ============================================================================
# Po deploy Backend i Analysis:
# 1. Skopiuj URL-e z Settings → Networking → Domains:
#    - Backend: https://backend-production-XXXX.up.railway.app
#    - Analysis: https://analysis-production-XXXX.up.railway.app
#
# 2. W Frontend Service → Settings → Variables → Add Variable:
#    VITE_API_URL=https://backend-production-XXXX.up.railway.app
#    VITE_ANALYSIS_API_URL=https://analysis-production-XXXX.up.railway.app
#
# 3. Railway automatycznie redeploy Frontend

# 8. WERYFIKACJA
# ============================================================================
# Sprawdź czy wszystkie serwisy działają:
# - Frontend: Otwórz URL w przeglądarce
# - Backend: curl https://backend-XXXX.railway.app/data
# - Analysis: curl https://analysis-XXXX.railway.app/api/analysis

# ============================================================================
# KONIEC
# ============================================================================
EOF

success "Utworzono plik: $OUTPUT_FILE"
echo ""

# ============================================================================
# KROK 4: Utwórz skrypt do automatycznego ustawiania zmiennych (jeśli CLI działa)
# ============================================================================
log "🔧 Przygotowywanie skryptu do ustawiania zmiennych..."
echo ""

VARS_SCRIPT="railway-set-variables.sh"

cat > "$VARS_SCRIPT" << 'EOF'
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
EOF

chmod +x "$VARS_SCRIPT"
success "Utworzono skrypt: $VARS_SCRIPT"
echo ""

# ============================================================================
# KROK 5: Generuj checklist
# ============================================================================
success "Generowanie checklist..."
echo ""

CHECKLIST_FILE="railway-setup-checklist.md"

cat > "$CHECKLIST_FILE" << 'EOF'
# Railway Setup Checklist

## ✅ Przed rozpoczęciem

- [ ] Railway CLI zainstalowany: `npm install -g @railway/cli`
- [ ] Zalogowany do Railway: `railway login`
- [ ] Projekt WIG utworzony w Railway Dashboard
- [ ] Repo GitHub połączone: SynergiaOS/trading_wig

## 🔧 Konfiguracja Serwisów

### Frontend Service

- [ ] Serwis "frontend" utworzony
- [ ] Dockerfile Path: `Dockerfile.frontend`
- [ ] Health Check Path: `/`
- [ ] Domain wygenerowany
- [ ] Zmienne środowiskowe ustawione:
  - [ ] `NODE_ENV=production`
  - [ ] `PORT=4173`
  - [ ] `VITE_REFRESH_INTERVAL=30000`
- [ ] Deploy zakończony
- [ ] Status: ✅ Działa

### Backend Service

- [ ] Serwis "backend" utworzony
- [ ] Dockerfile Path: `Dockerfile.backend`
- [ ] Health Check Path: `/data`
- [ ] Domain wygenerowany
- [ ] URL skopiowany: `https://backend-XXXX.railway.app`
- [ ] Zmienne środowiskowe ustawione:
  - [ ] `PORT=8000`
  - [ ] `HOST=0.0.0.0`
- [ ] Deploy zakończony
- [ ] Status: ✅ Działa
- [ ] Test: `curl https://backend-XXXX.railway.app/data`

### Analysis Service

- [ ] Serwis "analysis" utworzony
- [ ] Dockerfile Path: `Dockerfile.analysis`
- [ ] Health Check Path: `/api/analysis`
- [ ] Domain wygenerowany
- [ ] URL skopiowany: `https://analysis-XXXX.railway.app`
- [ ] Zmienne środowiskowe ustawione:
  - [ ] `ANALYSIS_PORT=8001`
  - [ ] `ANALYSIS_HOST=0.0.0.0`
- [ ] Deploy zakończony
- [ ] Status: ✅ Działa
- [ ] Test: `curl https://analysis-XXXX.railway.app/api/analysis`

## 🔗 Finalna Konfiguracja

- [ ] Frontend variables zaktualizowane:
  - [ ] `VITE_API_URL` ustawiony na Backend URL
  - [ ] `VITE_ANALYSIS_API_URL` ustawiony na Analysis URL
- [ ] Frontend redeployed
- [ ] Frontend działa i łączy się z Backend
- [ ] Frontend działa i łączy się z Analysis

## ✅ Weryfikacja

- [ ] Wszystkie serwisy mają status: ✅ Działa
- [ ] Frontend otwiera się w przeglądarce
- [ ] Frontend łączy się z Backend (sprawdź Network w DevTools)
- [ ] Frontend łączy się z Analysis
- [ ] Health checks są zielone dla wszystkich serwisów
- [ ] Logi nie pokazują błędów

## 🎉 Gotowe!

Wszystko skonfigurowane i działające!
EOF

success "Utworzono checklist: $CHECKLIST_FILE"
echo ""

# ============================================================================
# PODSUMOWANIE
# ============================================================================
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     ✅ AUTO SETUP ZAKOŃCZONY!                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Utworzone pliki:"
echo "   1. $OUTPUT_FILE - Wszystkie komendy i instrukcje"
echo "   2. $VARS_SCRIPT - Skrypt do ustawiania zmiennych (jeśli CLI działa)"
echo "   3. $CHECKLIST_FILE - Checklist do odhaczenia"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 NASTĘPNE KROKI:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Otwórz Railway Dashboard:"
echo "   https://railway.app"
echo ""
echo "2. Otwórz plik z komendami:"
echo "   cat $OUTPUT_FILE"
echo ""
echo "3. Follow instrukcje w pliku krok po kroku"
echo ""
echo "4. Użyj checklist do śledzenia postępu:"
echo "   cat $CHECKLIST_FILE"
echo ""
echo "5. (Opcjonalnie) Jeśli Railway CLI działa, użyj skryptu:"
echo "   ./$VARS_SCRIPT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Dokumentacja:"
echo "   - RAILWAY_COMPLETE_GUIDE.md - Kompletny przewodnik"
echo "   - README_RAILWAY.md - Railway overview"
echo ""
echo "🎯 Gotowe do deployment! 🚀"
echo ""

