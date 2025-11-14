# Railway Quick Start Guide

Szybki przewodnik po tworzeniu i konfiguracji projektu Railway.

## 🚀 Szybki Start

### 1. Utwórz Nowy Projekt

#### Opcja A: Automatyczne (Zalecane)

```bash
./create-railway-project.sh
```

Skrypt zapyta Cię o:
- Nazwę projektu
- Czy dodać serwisy (frontend, backend, analysis)

#### Opcja B: Ręczne

```bash
# Zaloguj się do Railway
railway login

# Utwórz nowy projekt
railway init trading-wig

# Lub bez nazwy (interaktywne)
railway init
```

### 2. Dodaj Serwisy

#### Opcja A: Automatyczne (Jeśli nie dodałeś podczas tworzenia projektu)

```bash
./setup-railway-services.sh
```

#### Opcja B: Ręczne

```bash
# Frontend
railway add --service frontend --repo SynergiaOS/trading_wig \
    --variables "NODE_ENV=production" \
    --variables "PORT=4173"

# Backend
railway add --service backend --repo SynergiaOS/trading_wig \
    --variables "PORT=8000" \
    --variables "HOST=0.0.0.0"

# Analysis
railway add --service analysis --repo SynergiaOS/trading_wig \
    --variables "ANALYSIS_PORT=8001" \
    --variables "ANALYSIS_HOST=0.0.0.0"
```

### 3. Konfiguruj Dockerfile Path

W Railway Dashboard:

1. Otwórz Dashboard: `railway open`
2. Dla każdego serwisu:
   - Settings → Build → Dockerfile Path
   - Ustaw odpowiedni Dockerfile:
     - `frontend` → `Dockerfile.frontend`
     - `backend` → `Dockerfile.backend`
     - `analysis` → `Dockerfile.analysis`

### 4. Ustaw Zmienne Środowiskowe

#### Przez Railway Dashboard (Zalecane)

1. Otwórz Dashboard: `railway open`
2. Dla każdego serwisu:
   - Settings → Variables → Add Variable
   - Dodaj zmienne zgodnie z `RAILWAY_ENV_SETUP.md`

#### Przez Railway CLI

```bash
# Frontend
railway service frontend
railway variables --set "NODE_ENV=production"
railway variables --set "PORT=4173"

# Backend
railway service backend
railway variables --set "PORT=8000"
railway variables --set "HOST=0.0.0.0"
railway variables --set "POCKETBASE_URL=http://pocketbase-service.railway.internal:8090"
# ... więcej zmiennych (zobacz RAILWAY_ENV_SETUP.md)

# Analysis
railway service analysis
railway variables --set "ANALYSIS_PORT=8001"
railway variables --set "ANALYSIS_HOST=0.0.0.0"
# ... więcej zmiennych (zobacz RAILWAY_ENV_SETUP.md)
```

### 5. Deploy Serwisów

```bash
# Deploy wszystkich serwisów
railway up --service frontend
railway up --service backend
railway up --service analysis

# Lub deploy z aktualnego katalogu
railway up
```

### 6. Zaktualizuj Frontend Variables (Po Deploy)

Po deploy Backend i Analysis, pobierz ich URL-e i zaktualizuj Frontend:

```bash
# Sprawdź URL-e
railway domain --service backend
railway domain --service analysis

# Zaktualizuj Frontend
railway service frontend
railway variables --set "VITE_API_URL=https://backend-url.railway.app"
railway variables --set "VITE_ANALYSIS_API_URL=https://analysis-url.railway.app"
```

## 📋 Checklist

- [ ] Zalogowany do Railway (`railway login`)
- [ ] Projekt utworzony (`railway init`)
- [ ] Serwisy dodane (frontend, backend, analysis)
- [ ] Dockerfile Path ustawiony dla każdego serwisu
- [ ] Zmienne środowiskowe ustawione
- [ ] Serwisy zdeployowane
- [ ] Frontend variables zaktualizowane (po deploy backend/analysis)

## 🔍 Przydatne Komendy

### Status i Informacje

```bash
# Status projektu
railway status

# Lista projektów
railway list

# Aktualny użytkownik
railway whoami

# Otwórz Dashboard
railway open
```

### Serwisy

```bash
# Lista serwisów
railway service

# Linkuj do serwisu
railway service frontend

# Zmienne środowiskowe
railway variables --service frontend

# Logi
railway logs --service frontend
```

### Deploy

```bash
# Deploy do aktualnego serwisu
railway up

# Deploy do konkretnego serwisu
railway up --service frontend

# Deploy bez logów
railway up --detach
```

## 🐛 Troubleshooting

### Problem: "Not logged in"
```bash
railway login
```

### Problem: "No project linked"
```bash
railway link
# Lub
railway init
```

### Problem: "ENTER A VARIABLE"
- Użyj Railway Dashboard zamiast CLI
- Zobacz `RAILWAY_ENV_SETUP.md` dla instrukcji

### Problem: Build fails
- Sprawdź czy Dockerfile Path jest ustawiony
- Sprawdź logi: `railway logs --service <service-name>`

## 📚 Więcej Dokumentacji

- [RAILWAY_ENV_SETUP.md](./RAILWAY_ENV_SETUP.md) - Ręczna konfiguracja zmiennych
- [RAILWAY_ENV_VARIABLES.md](./RAILWAY_ENV_VARIABLES.md) - Kompletna lista zmiennych
- [RAILWAY_MULTI_SERVICE_SETUP.md](./RAILWAY_MULTI_SERVICE_SETUP.md) - Multi-service setup
- [RAILWAY_DEPLOY_STEPS.md](./RAILWAY_DEPLOY_STEPS.md) - Szczegółowy deployment
- [railway-cli-setup.md](./railway-cli-setup.md) - CLI setup guide

## 🔗 Przydatne Linki

- [Railway Documentation](https://docs.railway.app)
- [Railway CLI Reference](https://docs.railway.com/reference/cli-api)
- [Railway Dashboard](https://railway.app)

