# Railway Environment Variables - Ręczna Konfiguracja

Jeśli Railway CLI pokazuje "ENTER A VARIABLE", możesz ustawić zmienne środowiskowe ręcznie przez Railway Dashboard.

## 🎯 Szybki Start - Przez Railway Dashboard

### 1. Otwórz Railway Dashboard
```bash
railway open
```

### 2. Dla każdego serwisu ustaw zmienne środowiskowe

Przejdź do każdego serwisu → **Settings** → **Variables** → **Add Variable**

---

## 📋 Frontend Service

Dodaj następujące zmienne:

| Variable | Value |
|----------|-------|
| `NODE_ENV` | `production` |
| `PORT` | `4173` |
| `VITE_API_URL` | `https://backend-service.railway.app` (ustaw po deploy backend) |
| `VITE_ANALYSIS_API_URL` | `https://analysis-service.railway.app` (ustaw po deploy analysis) |

---

## 🔧 Backend Service

Dodaj następujące zmienne:

| Variable | Value |
|----------|-------|
| `PORT` | `8000` |
| `HOST` | `0.0.0.0` |
| `POCKETBASE_URL` | `http://pocketbase-service.railway.internal:8090` |
| `QUESTDB_HOST` | `questdb-service.railway.internal` |
| `QUESTDB_PORT` | `9009` |
| `QUESTDB_USER` | `admin` |
| `QUESTDB_PASSWORD` | `quest` |
| `REDIS_URL` | `redis://redis-service.railway.internal:6379` |

**Uwaga**: Zastąp nazwy serwisów (`pocketbase-service`, `questdb-service`, `redis-service`) rzeczywistymi nazwami Twoich serwisów w Railway.

---

## 🤖 Analysis Service

Dodaj następujące zmienne:

| Variable | Value |
|----------|-------|
| `ANALYSIS_PORT` | `8001` |
| `ANALYSIS_HOST` | `0.0.0.0` |
| `POCKETBASE_URL` | `http://pocketbase-service.railway.internal:8090` |
| `QUESTDB_HOST` | `questdb-service.railway.internal` |
| `QUESTDB_PORT` | `9009` |
| `QUESTDB_USER` | `admin` |
| `QUESTDB_PASSWORD` | `quest` |
| `REDIS_URL` | `redis://redis-service.railway.internal:6379` |

**Uwaga**: Zastąp nazwy serwisów (`pocketbase-service`, `questdb-service`, `redis-service`) rzeczywistymi nazwami Twoich serwisów w Railway.

---

## 🔄 Alternatywa - Użyj Railway CLI (jeśli działa)

Jeśli Railway CLI działa poprawnie, możesz użyć:

```bash
# Frontend
railway service frontend
railway variables NODE_ENV=production
railway variables PORT=4173

# Backend
railway service backend
railway variables PORT=8000
railway variables HOST=0.0.0.0
railway variables POCKETBASE_URL=http://pocketbase-service.railway.internal:8090
railway variables QUESTDB_HOST=questdb-service.railway.internal
railway variables QUESTDB_PORT=9009
railway variables QUESTDB_USER=admin
railway variables QUESTDB_PASSWORD=quest
railway variables REDIS_URL=redis://redis-service.railway.internal:6379

# Analysis
railway service analysis
railway variables ANALYSIS_PORT=8001
railway variables ANALYSIS_HOST=0.0.0.0
railway variables POCKETBASE_URL=http://pocketbase-service.railway.internal:8090
railway variables QUESTDB_HOST=questdb-service.railway.internal
railway variables QUESTDB_PORT=9009
railway variables QUESTDB_USER=admin
railway variables QUESTDB_PASSWORD=quest
railway variables REDIS_URL=redis://redis-service.railway.internal:6379
```

---

## 🔍 Railway Private Network

Railway automatycznie tworzy **private network** między serwisami w tym samym projekcie. Możesz używać nazw serwisów jako hostnames:

- `backend-service.railway.internal:8000`
- `analysis-service.railway.internal:8001`
- `pocketbase-service.railway.internal:8090`
- `questdb-service.railway.internal:9009`
- `redis-service.railway.internal:6379`

**Uwaga**: `.railway.internal` działa tylko między serwisami w tym samym projekcie Railway.

---

## ⚠️ Troubleshooting

### Problem: "ENTER A VARIABLE"
- **Rozwiązanie**: Użyj Railway Dashboard zamiast CLI
- Przejdź do serwisu → Settings → Variables → Add Variable

### Problem: Zmienne nie działają
- **Rozwiązanie**: Upewnij się, że:
  1. Nazwy serwisów są poprawne (sprawdź w Railway Dashboard)
  2. Serwisy są w tym samym projekcie Railway
  3. Używasz `.railway.internal` dla private network

### Problem: Nie można połączyć z bazami danych
- **Rozwiązanie**: 
  1. Sprawdź czy serwisy baz danych są uruchomione
  2. Sprawdź czy nazwy serwisów są poprawne
  3. Sprawdź logi serwisów: `railway logs --service backend`

---

## 📚 Więcej Informacji

- [Railway Multi-Service Setup](./RAILWAY_MULTI_SERVICE_SETUP.md)
- [Railway CLI Setup](./railway-cli-setup.md)
- [Railway Environment Variables](./RAILWAY_ENV_VARIABLES.md)
- [Railway Deploy Steps](./RAILWAY_DEPLOY_STEPS.md)

