# Naprawa autentykacji Railway - Instrukcje

## 🔧 Problem

Jeśli widzisz błąd:
```
Found invalid RAILWAY_TOKEN
Unauthorized
```

To oznacza, że Railway CLI próbuje użyć nieprawidłowego tokenu z konfiguracji.

## ✅ Rozwiązanie

### Krok 1: Usuń nieprawidłowy token z konfiguracji

```bash
# Usuń plik konfiguracyjny Railway (zostanie utworzony ponownie przy logowaniu)
rm ~/.railway/config.json
```

### Krok 2: Usuń RAILWAY_TOKEN ze środowiska

```bash
# Usuń z aktualnej sesji
unset RAILWAY_TOKEN
unset RAILWAY_API_TOKEN

# Sprawdź czy są jeszcze ustawione
env | grep RAILWAY
```

### Krok 3: Sprawdź pliki shell (opcjonalnie)

Jeśli RAILWAY_TOKEN jest ustawiona w plikach shell:

```bash
# Sprawdź pliki
grep -r "RAILWAY_TOKEN" ~/.bashrc ~/.zshrc ~/.profile 2>/dev/null

# Jeśli znajdziesz, usuń te linie z plików
```

### Krok 4: Zaloguj się ponownie

```bash
# Zaloguj się interaktywnie
railway login
```

### Krok 5: Sprawdź autentykację

```bash
# Sprawdź czy jesteś zalogowany
railway whoami

# Sprawdź status projektu
railway status
```

## 🚀 Szybkie naprawienie

Uruchom skrypt:

```bash
./fix-railway-auth.sh
```

Następnie:

```bash
railway login
```

## ⚠️ Ważne

- **NIE ustawiaj** `RAILWAY_TOKEN` dla Railway CLI
- Railway CLI używa sesji z `railway login`, nie tokenu API
- Token API (`RAILWAY_API_TOKEN`) jest tylko dla CI/CD i REST API

## 📋 Po naprawieniu

Po pomyślnym logowaniu, możesz używać Railway CLI normalnie:

```bash
railway status
railway variables --set "KEY=VALUE" --service <service>
railway up --service <service>
```

