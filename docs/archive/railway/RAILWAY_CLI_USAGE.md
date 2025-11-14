# Railway CLI - Prawidłowe Użycie

## ✅ Aktualna sytuacja

Twój projekt **WIG** jest już poprawnie połączony z Railway CLI poprzez interaktywne logowanie (`railway login`).

## ⚠️ Ważne: Token API vs CLI Authentication

### Railway CLI NIE używa tokenu API

- **Railway CLI** używa sesji z interaktywnego logowania (`railway login`)
- **Token API** (`RAILWAY_API_TOKEN`) jest tylko dla Railway REST API (CI/CD)
- **NIE ustawiaj** `RAILWAY_TOKEN` - to spowoduje błąd "invalid RAILWAY_TOKEN"

## 🚀 Jak używać Railway CLI

### 1. Sprawdź status (bez tokenu!)

```bash
# NIE ustawiaj RAILWAY_TOKEN
unset RAILWAY_TOKEN RAILWAY_API_TOKEN

# Sprawdź status
railway status
```

### 2. Ustaw zmienne środowiskowe

```bash
# Upewnij się, że nie masz RAILWAY_TOKEN ustawionego
unset RAILWAY_TOKEN

# Ustaw zmienne
railway variables --set "PORT=8000" --service backend
railway variables --set "HOST=0.0.0.0" --service backend
```

### 3. Zobacz zmienne

```bash
railway variables --service backend
```

### 4. Deploy

```bash
railway up --service backend
```

## 🔧 Jeśli widzisz błąd "invalid RAILWAY_TOKEN"

```bash
# Usuń zmienną RAILWAY_TOKEN
unset RAILWAY_TOKEN

# Sprawdź czy nie jest ustawiona
env | grep RAILWAY

# Jeśli jest, usuń ją
unset RAILWAY_TOKEN RAILWAY_API_TOKEN

# Teraz Railway CLI powinien działać
railway status
```

## 📋 Token API - tylko dla CI/CD

Token `RAILWAY_API_TOKEN` jest **tylko** dla:
- CI/CD pipelines (GitHub Actions, GitLab CI)
- Railway REST API
- Automation scripts używające API

**NIE** dla lokalnego Railway CLI.

## ✅ Prawidłowy workflow

```bash
# 1. Zaloguj się interaktywnie (tylko raz)
railway login

# 2. Połącz projekt (tylko raz)
railway link
# Wybierz projekt: WIG

# 3. Użyj CLI normalnie (bez tokenu)
railway status
railway variables --set "KEY=VALUE" --service <service>
railway up --service <service>
```

## 🐛 Troubleshooting

### Problem: "Found invalid RAILWAY_TOKEN"

```bash
# Rozwiązanie: Usuń RAILWAY_TOKEN
unset RAILWAY_TOKEN
railway status
```

### Problem: "Unauthorized"

```bash
# Rozwiązanie: Zaloguj się
railway login
```

### Problem: "Project Token not found"

```bash
# Rozwiązanie: Połącz projekt
railway link
# Wybierz projekt WIG
```

## 📚 Więcej informacji

- [Railway CLI Documentation](https://docs.railway.com/guides/cli)
- [Railway Authentication](https://docs.railway.com/reference/api#authentication)

