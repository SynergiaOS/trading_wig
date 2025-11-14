# Railway Deployment - Krok po kroku

## ✅ Projekt utworzony
- **Nazwa**: wig
- **URL**: https://railway.com/project/07624178-7237-4f81-89bf-96e0417bb20d

## 🚀 Dodaj 3 Serwisy

### KROK 1: Otwórz Railway Dashboard

```bash
# Przejdź do:
https://railway.com/project/07624178-7237-4f81-89bf-96e0417bb20d

# Lub użyj przeglądarki i zaloguj się na railway.app
```

### KROK 2: Dodaj Frontend Service

1. Kliknij **"+ New"** → **"GitHub Repo"**
2. Wybierz repozytorium: **SynergiaOS/trading_wig**
3. Po dodaniu, przejdź do **Settings**:
   - **Build** → **Dockerfile Path**: `Dockerfile.frontend`
   - **Variables** → Dodaj:
     - `NODE_ENV=production`
     - `PORT=4173`
4. Kliknij **"Deploy"** (lub Railway automatycznie zacznie build)

### KROK 3: Dodaj Backend Service

1. Kliknij **"+ New"** → **"GitHub Repo"**
2. Wybierz repozytorium: **SynergiaOS/trading_wig**
3. Po dodaniu, przejdź do **Settings**:
   - **Build** → **Dockerfile Path**: `Dockerfile.backend`
   - **Variables** → Dodaj:
     - `PORT=8000`
     - `HOST=0.0.0.0`
4. Kliknij **"Deploy"**

### KROK 4: Dodaj Analysis Service

1. Kliknij **"+ New"** → **"GitHub Repo"**
2. Wybierz repozytorium: **SynergiaOS/trading_wig**
3. Po dodaniu, przejdź do **Settings**:
   - **Build** → **Dockerfile Path**: `Dockerfile.analysis`
   - **Variables** → Dodaj:
     - `ANALYSIS_PORT=8001`
     - `ANALYSIS_HOST=0.0.0.0`
4. Kliknij **"Deploy"**

### KROK 5: Skonfiguruj Railway Service Discovery (opcjonalnie)

Jeśli używasz osobnych serwisów dla baz danych (Pocketbase, QuestDB, Redis), skonfiguruj zmienne środowiskowe:

**Dla Backend Service:**
1. Przejdź do **Backend Service** → **Settings** → **Variables**
2. Dodaj:
   - `POCKETBASE_URL=http://pocketbase-service.railway.internal:8090`
   - `QUESTDB_HOST=questdb-service.railway.internal`
   - `QUESTDB_PORT=9009`
   - `QUESTDB_USER=admin`
   - `QUESTDB_PASSWORD=quest`
   - `REDIS_URL=redis://redis-service.railway.internal:6379`

**Dla Analysis Service:**
1. Przejdź do **Analysis Service** → **Settings** → **Variables**
2. Dodaj te same zmienne co dla Backend Service

**Uwaga**: Zastąp nazwy serwisów (`pocketbase-service`, `questdb-service`, `redis-service`) rzeczywistymi nazwami Twoich serwisów w Railway.

### KROK 6: Skonfiguruj Frontend Variables

Po deploy Backend i Analysis, zaktualizuj Frontend variables:

1. Przejdź do **Frontend Service** → **Settings** → **Variables**
2. Dodaj:
   - `VITE_API_URL=https://backend-service.railway.app`
   - `VITE_ANALYSIS_API_URL=https://analysis-service.railway.app`
3. Zastąp `backend-service` i `analysis-service` rzeczywistymi URL-ami z Railway

## 🔍 Jak znaleźć URL-e serwisów

1. W Railway Dashboard, kliknij na każdy serwis
2. Przejdź do zakładki **"Settings"**
3. Znajdź sekcję **"Networking"** lub **"Domains"**
4. Railway automatycznie przypisze URL (np. `https://backend-production-xxxx.up.railway.app`)

## 📋 Podsumowanie Zmiennych Środowiskowych

### Frontend Service
```env
NODE_ENV=production
PORT=4173
VITE_API_URL=https://backend-url.railway.app
VITE_ANALYSIS_API_URL=https://analysis-url.railway.app
```

### Backend Service
```env
PORT=8000
HOST=0.0.0.0
# Railway Service Discovery (jeśli używasz osobnych serwisów dla baz danych)
POCKETBASE_URL=http://pocketbase-service.railway.internal:8090
QUESTDB_HOST=questdb-service.railway.internal
QUESTDB_PORT=9009
QUESTDB_USER=admin
QUESTDB_PASSWORD=quest
REDIS_URL=redis://redis-service.railway.internal:6379
```

### Analysis Service
```env
ANALYSIS_PORT=8001
ANALYSIS_HOST=0.0.0.0
# Railway Service Discovery (jeśli używasz osobnych serwisów dla baz danych)
POCKETBASE_URL=http://pocketbase-service.railway.internal:8090
QUESTDB_HOST=questdb-service.railway.internal
QUESTDB_PORT=9009
QUESTDB_USER=admin
QUESTDB_PASSWORD=quest
REDIS_URL=redis://redis-service.railway.internal:6379
```

## 🐛 Troubleshooting

### Problem: Build fails with "Cannot find module"
- **Rozwiązanie**: Upewnij się że używasz właściwego Dockerfile (Dockerfile.frontend/backend/analysis)

### Problem: Port conflicts
- **Rozwiązanie**: Railway automatycznie zarządza portami przez zmienną `PORT`, upewnij się że kod używa `process.env.PORT`

### Problem: CORS errors
- **Rozwiązanie**: Backend i Analysis API mają już skonfigurowane CORS headers

## ✅ Weryfikacja

Po deploy wszystkich serwisów, sprawdź:

```bash
# Frontend
curl https://frontend-service.railway.app

# Backend API
curl https://backend-service.railway.app/data

# Analysis API
curl https://analysis-service.railway.app/api/analysis
```

## 📚 Dokumentacja

- [Railway Multi-Service Setup](./RAILWAY_MULTI_SERVICE_SETUP.md)
- [Railway Documentation](https://docs.railway.app)

