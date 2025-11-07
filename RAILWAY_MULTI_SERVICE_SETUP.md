# Railway Multi-Service Setup Guide

Ten przewodnik pokazuje jak podzielić projekt na 3 osobne serwisy w Railway.

## 🏗️ Architektura

Projekt składa się z 3 serwisów:

1. **Frontend** - React aplikacja (port 80/4173)
2. **Backend API** - Realtime Data API (port 8000)
3. **Analysis API** - Analysis API (port 8001)

## 📁 Struktura Plików

```
.
├── Dockerfile.frontend      # Frontend service
├── Dockerfile.backend       # Backend API service
├── Dockerfile.analysis      # Analysis API service
├── railway-frontend.json    # Frontend config
├── railway-backend.json     # Backend config
├── railway-analysis.json    # Analysis config
└── code/
    ├── realtime_api_server.py
    └── analysis_api_server.py
```

## 🚀 Konfiguracja w Railway

### Metoda 1: Railway Dashboard (Rekomendowana)

1. **Utwórz nowy projekt w Railway**
   - Przejdź do https://railway.app
   - Kliknij "New Project"
   - Wybierz "Deploy from GitHub repo"
   - Wybierz repozytorium `SynergiaOS/trading_wig`

2. **Dodaj pierwszy serwis - Frontend**
   - Kliknij "+ New" → "GitHub Repo"
   - Wybierz ten sam repozytorium
   - W Settings → Build → Dockerfile Path: `Dockerfile.frontend`
   - W Settings → Deploy → Start Command: (puste, używa CMD z Dockerfile)
   - W Settings → Network → Port: `80`
   - W Settings → Variables:
     - `NODE_ENV=production`
     - `VITE_API_URL=https://your-backend-url.railway.app` (ustawisz po deploy backendu)

3. **Dodaj drugi serwis - Backend API**
   - Kliknij "+ New" → "GitHub Repo"
   - Wybierz ten sam repozytorium
   - W Settings → Build → Dockerfile Path: `Dockerfile.backend`
   - W Settings → Deploy → Start Command: (puste, używa CMD z Dockerfile)
   - W Settings → Network → Port: `8000`
   - W Settings → Variables:
     - `PORT=8000`
     - `HOST=0.0.0.0`

4. **Dodaj trzeci serwis - Analysis API**
   - Kliknij "+ New" → "GitHub Repo"
   - Wybierz ten sam repozytorium
   - W Settings → Build → Dockerfile Path: `Dockerfile.analysis`
   - W Settings → Deploy → Start Command: (puste, używa CMD z Dockerfile)
   - W Settings → Network → Port: `8001`
   - W Settings → Variables:
     - `ANALYSIS_PORT=8001`
     - `ANALYSIS_HOST=0.0.0.0`

5. **Skonfiguruj zmienne środowiskowe**
   - W każdym serwisie dodaj:
     - **Frontend**: `VITE_API_URL=https://backend-service.railway.app`
     - **Frontend**: `VITE_ANALYSIS_API_URL=https://analysis-service.railway.app`
     - **Backend**: Używa danych z `data/wig80_current_data.json`
     - **Analysis**: Używa danych z `data/wig80_current_data.json`

6. **Utwórz Private Network (opcjonalnie)**
   - Railway automatycznie tworzy private network między serwisami
   - Możesz używać nazw serwisów jako hostnames:
     - `backend-service.railway.internal:8000`
     - `analysis-service.railway.internal:8001`

### Metoda 2: Railway CLI

```bash
# Zainstaluj Railway CLI
npm i -g @railway/cli

# Zaloguj się
railway login

# Utwórz nowy projekt
railway init

# Dodaj frontend service
railway add --dockerfile Dockerfile.frontend
railway variables set NODE_ENV=production
railway variables set VITE_API_URL=https://backend.railway.app

# Dodaj backend service (w nowym terminalu)
railway add --dockerfile Dockerfile.backend
railway variables set PORT=8000
railway variables set HOST=0.0.0.0

# Dodaj analysis service (w nowym terminalu)
railway add --dockerfile Dockerfile.analysis
railway variables set ANALYSIS_PORT=8001
railway variables set ANALYSIS_HOST=0.0.0.0
```

## 🔗 Konfiguracja URL-i

Po deploy, każdy serwis otrzyma swój własny URL:

- **Frontend**: `https://frontend-service.railway.app`
- **Backend API**: `https://backend-service.railway.app`
- **Analysis API**: `https://analysis-service.railway.app`

### Aktualizacja Frontend

Po uzyskaniu URL-i backendu i analysis API, zaktualizuj zmienne środowiskowe frontendu:

```bash
# W Railway Dashboard → Frontend Service → Variables
VITE_API_URL=https://backend-service.railway.app
VITE_ANALYSIS_API_URL=https://analysis-service.railway.app
```

Lub użyj Railway Private Network (wewnętrzne URL-e):

```bash
VITE_API_URL=http://backend-service.railway.internal:8000
VITE_ANALYSIS_API_URL=http://analysis-service.railway.internal:8001
```

## 📝 Zmienne Środowiskowe

### Frontend
```env
NODE_ENV=production
VITE_API_URL=https://backend-service.railway.app
VITE_ANALYSIS_API_URL=https://analysis-service.railway.app
VITE_REFRESH_INTERVAL=30000
```

### Backend API
```env
PORT=8000
HOST=0.0.0.0
```

### Analysis API
```env
ANALYSIS_PORT=8001
ANALYSIS_HOST=0.0.0.0
```

## 🔍 Weryfikacja

Po deploy sprawdź czy wszystkie serwisy działają:

```bash
# Frontend
curl https://frontend-service.railway.app

# Backend API
curl https://backend-service.railway.app/data

# Analysis API
curl https://analysis-service.railway.app/api/analysis
```

## 🐛 Troubleshooting

### Problem: Frontend nie może połączyć się z API
- **Rozwiązanie**: Sprawdź zmienne środowiskowe `VITE_API_URL` i `VITE_ANALYSIS_API_URL`
- Upewnij się, że URL-e są publiczne (nie używasz `.railway.internal`)

### Problem: CORS errors
- **Rozwiązanie**: Backend i Analysis API mają już skonfigurowane CORS headers
- Jeśli problemy, sprawdź `Access-Control-Allow-Origin` w kodzie

### Problem: Port conflicts
- **Rozwiązanie**: Railway automatycznie zarządza portami przez zmienną `PORT`
- Upewnij się, że kod używa `os.environ.get('PORT')`

## 📊 Monitoring

Railway automatycznie monitoruje:
- Health checks (jeśli skonfigurowane)
- Logs dla każdego serwisu
- Metrics (CPU, Memory, Network)

## 🔄 Aktualizacja

Aby zaktualizować serwis:
1. Zrób zmiany w kodzie
2. Commit i push do GitHub
3. Railway automatycznie wykryje zmiany i zbuduje nowy deploy
4. Każdy serwis deployuje się niezależnie

## 📚 Dodatkowe Zasoby

- [Railway Documentation](https://docs.railway.app)
- [Railway Multi-Service Guide](https://docs.railway.app/develop/services)
- [Railway Private Networks](https://docs.railway.app/networking/private-networks)

