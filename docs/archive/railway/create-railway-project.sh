#!/bin/bash
# Railway Project Creation Script
# Tworzy nowy projekt Railway i konfiguruje podstawowe serwisy

set -e

# ⚠️ NIE ładuj RAILWAY_TOKEN - Railway CLI nie używa tokenu API
# Token jest tylko dla REST API w CI/CD
# Dla CLI użyj: railway login (interaktywne logowanie)

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🚀 RAILWAY PROJECT CREATION                                ║"
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

# Zapytaj o nazwę projektu
read -p "📝 Podaj nazwę projektu (lub naciśnij Enter dla nazwy domyślnej 'trading-wig'): " PROJECT_NAME
PROJECT_NAME=${PROJECT_NAME:-trading-wig}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Tworzę nowy projekt: $PROJECT_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Utwórz nowy projekt (railway init jest interaktywny)
echo "🔨 Tworzenie projektu..."
echo "⚠️  Railway CLI poprosi Cię o nazwę projektu."
echo "    Wprowadź nazwę: $PROJECT_NAME"
echo ""

# Railway init jest interaktywny - uruchom bez argumentów
# Użytkownik będzie musiał wprowadzić nazwę interaktywnie
railway init

echo ""
echo "✅ Projekt utworzony!"
echo ""

# Sprawdź status projektu
echo "📋 Status projektu:"
railway status
echo ""

# Zapytaj czy chce dodać serwisy
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "❓ Dodawanie serwisów"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Czy chcesz teraz dodać serwisy do projektu?"
echo "  • frontend - React aplikacja (port 4173)"
echo "  • backend - Backend API (port 8000)"
echo "  • analysis - Analysis API (port 8001)"
echo ""
echo "Możesz też dodać je później używając: ./setup-railway-services.sh"
echo ""
read -p "Dodaj serwisy teraz? [y/N]: " ADD_SERVICES
ADD_SERVICES=${ADD_SERVICES:-n}

if [[ $ADD_SERVICES =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Dodawanie serwisów..."
    echo ""
    
    # Frontend Service
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Dodaję serwis: frontend"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if railway add --service frontend --repo SynergiaOS/trading_wig \
        --variables "NODE_ENV=production" \
        --variables "PORT=4173" 2>/dev/null; then
        railway service frontend
        echo "✅ Serwis frontend dodany"
    else
        echo "⚠️  Nie udało się dodać serwisu frontend automatycznie"
        echo "   Dodaj go ręcznie: railway add --service frontend --repo SynergiaOS/trading_wig"
    fi
    echo ""
    
    # Backend Service
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Dodaję serwis: backend"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if railway add --service backend --repo SynergiaOS/trading_wig \
        --variables "PORT=8000" \
        --variables "HOST=0.0.0.0" 2>/dev/null; then
        railway service backend
        echo "✅ Serwis backend dodany"
    else
        echo "⚠️  Nie udało się dodać serwisu backend automatycznie"
        echo "   Dodaj go ręcznie: railway add --service backend --repo SynergiaOS/trading_wig"
    fi
    echo ""
    
    # Analysis Service
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Dodaję serwis: analysis"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if railway add --service analysis --repo SynergiaOS/trading_wig \
        --variables "ANALYSIS_PORT=8001" \
        --variables "ANALYSIS_HOST=0.0.0.0" 2>/dev/null; then
        railway service analysis
        echo "✅ Serwis analysis dodany"
    else
        echo "⚠️  Nie udało się dodać serwisu analysis automatycznie"
        echo "   Dodaj go ręcznie: railway add --service analysis --repo SynergiaOS/trading_wig"
    fi
    echo ""
    
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║     ✅ SERWISY DODANE!                                        ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
else
    echo ""
    echo "⏭️  Pomijam dodawanie serwisów."
    echo "   Możesz dodać je później używając: ./setup-railway-services.sh"
    echo ""
fi

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     ✅ PROJEKT UTWORZONY!                                      ║"
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
echo "3. Ustaw dodatkowe zmienne środowiskowe (jeśli potrzebne):"
echo "   railway variables --set 'KEY=VALUE' --service <service-name>"
echo "   Zobacz RAILWAY_ENV_SETUP.md dla pełnej listy zmiennych"
echo ""
echo "4. Deploy serwisów:"
echo "   railway up --service frontend"
echo "   railway up --service backend"
echo "   railway up --service analysis"
echo ""
echo "📚 Dokumentacja:"
echo "   - RAILWAY_ENV_SETUP.md - Konfiguracja zmiennych środowiskowych"
echo "   - RAILWAY_ENV_VARIABLES.md - Kompletna lista zmiennych"
echo "   - setup-railway-services.sh - Dodawanie serwisów do istniejącego projektu"
echo ""

