# Railway Deployment Guide

## 🚂 Wdrożenie na Railway (Pro)

### Wymagania

- Konto Railway Pro
- GitHub repository: https://github.com/SynergiaOS/trading_wig
- Railway CLI (opcjonalnie)

### Struktura Wdrożenia

Projekt składa się z 3 serwisów:

1. **Frontend** (React/Vite) - Port 4173
2. **Backend API** (Python) - Port 8000
3. **Analysis API** (Python) - Port 8001

### Krok 1: Przygotowanie Repozytorium

Projekt jest już gotowy z plikami konfiguracyjnymi:
- `railway.json` - konfiguracja frontendu
- `railway-backend.json` - konfiguracja backend API
- `railway-analysis.json` - konfiguracja analysis API
- `Procfile` - start command dla frontendu

### Krok 2: Utworzenie Projektów na Railway

#### 2.1 Frontend Service

1. Zaloguj się na [Railway](https://railway.app)
2. Kliknij "New Project"
3. Wybierz "Deploy from GitHub repo"
4. Wybierz repozytorium: `SynergiaOS/trading_wig`
5. Railway automatycznie wykryje `railway.json`

**Konfiguracja Build:**
- Root Directory: `/` (root projektu)
- Build Command: `cd polish-finance-platform/polish-finance-app && pnpm install && pnpm run build:prod`
- Start Command: `cd polish-finance-platform/polish-finance-app && pnpm run start`

**Zmienne Środowiskowe:**
```bash
NODE_ENV=production
PORT=4173
VITE_API_URL=https://your-backend-service.railway.app
VITE_ANALYSIS_API_URL=https://your-analysis-service.railway.app
VITE_REFRESH_INTERVAL=30000
```

#### 2.2 Backend API Service

1. W tym samym projekcie Railway, kliknij "New Service"
2. Wybierz "GitHub Repo" → `SynergiaOS/trading_wig`
3. W ustawieniach, zmień:
   - Root Directory: `/code`
   - Start Command: `python3 realtime_api_server.py`

**Zmienne Środowiskowe:**
```bash
PORT=8000
HOST=0.0.0.0
PYTHON_VERSION=3.12
```

**Build Settings:**
- Builder: NIXPACKS
- Build Command: `pip install -r requirements.txt`

#### 2.3 Analysis API Service

1. W tym samym projekcie Railway, kliknij "New Service"
2. Wybierz "GitHub Repo" → `SynergiaOS/trading_wig`
3. W ustawieniach, zmień:
   - Root Directory: `/code`
   - Start Command: `python3 analysis_api_server.py`

**Zmienne Środowiskowe:**
```bash
PORT=8001
HOST=0.0.0.0
PYTHON_VERSION=3.12
ALLOWED_ORIGIN=*  # Optional: restrict CORS origins in production
```

**Build Settings:**
- Builder: NIXPACKS
- Build Command: `pip install -r requirements.txt`

### Krok 3: Konfiguracja Zmiennych Środowiskowych

#### Frontend Service Variables:
```bash
NODE_ENV=production
PORT=4173
VITE_API_URL=${{Backend_API.RAILWAY_PUBLIC_DOMAIN}}
VITE_ANALYSIS_API_URL=${{Analysis_API.RAILWAY_PUBLIC_DOMAIN}}
VITE_REFRESH_INTERVAL=30000
```

#### Backend API Variables:
```bash
PORT=8000
HOST=0.0.0.0
PYTHON_VERSION=3.12
```

#### Analysis API Variables:
```bash
PORT=8001
HOST=0.0.0.0
PYTHON_VERSION=3.12
ALLOWED_ORIGIN=*  # Optional: restrict CORS origins in production
```

### Krok 4: Konfiguracja Portów i Domen

1. **Frontend Service:**
   - Railway automatycznie przypisze port
   - Włącz "Generate Domain" dla publicznego URL
   - Domena będzie dostępna jako: `your-project.railway.app`

2. **Backend API:**
   - Włącz "Generate Domain"
   - Użyj domeny w zmiennych środowiskowych frontendu

3. **Analysis API:**
   - Włącz "Generate Domain"
   - Użyj domeny w zmiennych środowiskowych frontendu

### Krok 5: Konfiguracja CORS

Upewnij się, że backend API ma skonfigurowane CORS dla domeny Railway:

W `code/realtime_api_server.py` i `code/analysis_api_server.py`:
```python
self.send_header('Access-Control-Allow-Origin', '*')  # Dla produkcji użyj konkretnej domeny
```

### Krok 6: Konfiguracja Danych

#### Opcja A: Użyj Railway Volume dla danych

1. W Backend API service, dodaj Volume:
   - Path: `/data`
   - Mount: `/app/data`

2. Skopiuj plik `wig80_current_data.json` do volume:
   ```bash
   railway run cp data/wig80_current_data.json /app/data/
   ```

#### Opcja B: Użyj Railway Secrets dla danych

1. Dodaj dane jako secret w Railway
2. Przy starcie, pobierz dane z secret

### Krok 7: Deploy

1. Railway automatycznie wykryje zmiany w GitHub
2. Po pushu do `main`, Railway zbuduje i wdroży wszystkie serwisy
3. Sprawdź logi w Railway dashboard

### Krok 8: Monitoring

1. **Logs**: Sprawdzaj logi w Railway dashboard
2. **Metrics**: Railway pokazuje użycie CPU, RAM, Network
3. **Alerts**: Skonfiguruj alerty dla błędów

### Troubleshooting

#### Problem: Build fails
- Sprawdź logi build w Railway
- Upewnij się, że wszystkie zależności są w `requirements.txt` i `package.json`

#### Problem: Service nie startuje
- Sprawdź logi runtime
- Upewnij się, że port jest poprawnie skonfigurowany
- Sprawdź zmienne środowiskowe

#### Problem: CORS errors
- Upewnij się, że backend ma skonfigurowane CORS
- Sprawdź czy domeny są poprawne w zmiennych środowiskowych

#### Problem: Brak danych
- Upewnij się, że plik `wig80_current_data.json` jest dostępny
- Sprawdź ścieżki w kodzie

### Railway CLI (Opcjonalnie)

```bash
# Instalacja
npm i -g @railway/cli

# Login
railway login

# Link do projektu
railway link

# Deploy
railway up

# Sprawdź logi
railway logs

# Zmienne środowiskowe
railway variables
```

### Koszty Railway Pro

- Railway Pro: $20/miesiąc
- Zawiera:
  - Nieograniczone deploys
  - Więcej zasobów
  - Priority support
  - Custom domains

### Przykładowa Struktura Projektu na Railway

```
Railway Project: trading-wig
├── Frontend Service (React)
│   ├── Domain: trading-wig-frontend.railway.app
│   ├── Port: 4173
│   └── Build: pnpm build:prod
├── Backend API Service (Python)
│   ├── Domain: trading-wig-backend.railway.app
│   ├── Port: 8000
│   └── Start: python3 realtime_api_server.py
└── Analysis API Service (Python)
    ├── Domain: trading-wig-analysis.railway.app
    ├── Port: 8001
    └── Start: python3 analysis_api_server.py
```

### Następne Kroki

1. ✅ Push projektu na GitHub
2. ✅ Utwórz projekt na Railway
3. ✅ Skonfiguruj 3 serwisy
4. ✅ Ustaw zmienne środowiskowe
5. ✅ Deploy i test

---

**Gotowe!** Projekt będzie dostępny na Railway z automatycznym deployem z GitHub.

