#!/bin/bash
# Fix Railway Authentication Script
# Usuwa RAILWAY_TOKEN ze środowiska i umożliwia ponowne logowanie

echo "🔧 Naprawianie autentykacji Railway..."
echo ""

# 1. Usuń zmienne środowiskowe RAILWAY_TOKEN
echo "1. Usuwanie RAILWAY_TOKEN ze środowiska..."
unset RAILWAY_TOKEN
unset RAILWAY_API_TOKEN

# Sprawdź czy są jeszcze ustawione
if env | grep -q "RAILWAY_TOKEN"; then
    echo "   ⚠️  RAILWAY_TOKEN nadal jest ustawiona!"
    echo "   Usuń ją ręcznie z ~/.bashrc, ~/.zshrc lub ~/.profile"
else
    echo "   ✅ RAILWAY_TOKEN usunięta ze środowiska"
fi

# 2. Sprawdź pliki konfiguracyjne Railway
echo ""
echo "2. Sprawdzanie konfiguracji Railway..."
if [ -f ~/.railway/config.json ]; then
    echo "   📁 Znaleziono: ~/.railway/config.json"
    if grep -q "token" ~/.railway/config.json 2>/dev/null; then
        echo "   ⚠️  Plik zawiera token - sprawdź zawartość:"
        echo "   cat ~/.railway/config.json"
    else
        echo "   ✅ Plik nie zawiera tokenu"
    fi
else
    echo "   ✅ Brak pliku konfiguracyjnego Railway"
fi

# 3. Usuń token z .railway.env jeśli istnieje (nie powinien być używany przez CLI)
echo ""
echo "3. Sprawdzanie .railway.env..."
if [ -f .railway.env ]; then
    echo "   📁 Znaleziono: .railway.env"
    echo "   ⚠️  Plik zawiera token API (dla CI/CD, nie dla CLI)"
    echo "   ✅ Token w .railway.env nie jest ładowany przez skrypty"
fi

# 4. Instrukcje
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Następne kroki:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Upewnij się, że RAILWAY_TOKEN nie jest ustawiona:"
echo "   env | grep RAILWAY"
echo ""
echo "2. Jeśli widzisz RAILWAY_TOKEN, usuń ją z:"
echo "   - ~/.bashrc"
echo "   - ~/.zshrc"
echo "   - ~/.profile"
echo "   - Lub zaktualnej sesji: unset RAILWAY_TOKEN"
echo ""
echo "3. Zaloguj się ponownie:"
echo "   railway login"
echo ""
echo "4. Sprawdź autentykację:"
echo "   railway whoami"
echo ""
echo "5. Sprawdź status projektu:"
echo "   railway status"
echo ""

