# Railway Environment Variables - Kompletna Lista

Ten dokument zawiera kompletną listę wszystkich zmiennych środowiskowych potrzebnych do konfiguracji serwisów w Railway.

## 📋 Frontend Service

### Podstawowe zmienne
```bash
NODE_ENV=production
PORT=4173
```

### Zmienne dla połączenia z backendami (ustaw po deploy backend i analysis)
```bash
VITE_API_URL=https://backend-service.railway.app
VITE_ANALYSIS_API_URL=https://analysis-service.railway.app
VITE_REFRESH_INTERVAL=30000
```

### Ustawienie przez Railway CLI
```bash
railway service frontend
railway variables --set "NODE_ENV=production" --service frontend
railway variables --set "PORT=4173" --service frontend
# Po deploy backend i analysis:
railway variables --set "VITE_API_URL=https://backend-service.railway.app" --service frontend
railway variables --set "VITE_ANALYSIS_API_URL=https://analysis-service.railway.app" --service frontend
```

---

## 🔧 Backend Service

### Podstawowe zmienne
```bash
PORT=8000
HOST=0.0.0.0
ALLOWED_ORIGIN=*  # Optional: restrict CORS origins (default: *)
```

### Railway Service Discovery (dla połączenia z innymi serwisami)
```bash
# Jeśli masz osobne serwisy dla baz danych:
POCKETBASE_URL=http://pocketbase-service.railway.internal:8090
QUESTDB_HOST=questdb-service.railway.internal
QUESTDB_PORT=9009
QUESTDB_USER=admin
QUESTDB_PASSWORD=quest
REDIS_URL=redis://redis-service.railway.internal:6379

# Lub użyj publicznych URL-i (jeśli serwisy są publiczne):
# POCKETBASE_URL=https://pocketbase-service.railway.app
# QUESTDB_HOST=questdb-service.railway.app
# REDIS_URL=redis://redis-service.railway.app:6379
```

### Ustawienie przez Railway CLI
```bash
railway service backend
railway variables --set "PORT=8000" --service backend
railway variables --set "HOST=0.0.0.0" --service backend
railway variables --set "POCKETBASE_URL=http://pocketbase-service.railway.internal:8090" --service backend
railway variables --set "QUESTDB_HOST=questdb-service.railway.internal" --service backend
railway variables --set "QUESTDB_PORT=9009" --service backend
railway variables --set "QUESTDB_USER=admin" --service backend
railway variables --set "QUESTDB_PASSWORD=quest" --service backend
railway variables --set "REDIS_URL=redis://redis-service.railway.internal:6379" --service backend
```

---

## 🤖 Analysis Service

### Podstawowe zmienne
```bash
PORT=8001
HOST=0.0.0.0
ALLOWED_ORIGIN=*  # Optional: restrict CORS origins (default: *)
```

### Railway Service Discovery (dla połączenia z innymi serwisami)
```bash
# Te same zmienne jak dla Backend Service
POCKETBASE_URL=http://pocketbase-service.railway.internal:8090
QUESTDB_HOST=questdb-service.railway.internal
QUESTDB_PORT=9009
QUESTDB_USER=admin
QUESTDB_PASSWORD=quest
REDIS_URL=redis://redis-service.railway.internal:6379
```

### Ustawienie przez Railway CLI
```bash
railway service analysis
railway variables --set "PORT=8001" --service analysis
railway variables --set "HOST=0.0.0.0" --service analysis
railway variables --set "POCKETBASE_URL=http://pocketbase-service.railway.internal:8090" --service analysis
railway variables --set "QUESTDB_HOST=questdb-service.railway.internal" --service analysis
railway variables --set "QUESTDB_PORT=9009" --service analysis
railway variables --set "QUESTDB_USER=admin" --service analysis
railway variables --set "QUESTDB_PASSWORD=quest" --service analysis
railway variables --set "REDIS_URL=redis://redis-service.railway.internal:6379" --service analysis
```

---

## 🗄️ Opcjonalne Serwisy (jeśli używasz osobnych serwisów dla baz danych)

### Pocketbase Service
```bash
POCKETBASE_URL=http://pocketbase-service.railway.internal:8090
# Lub publiczny URL:
# POCKETBASE_URL=https://pocketbase-service.railway.app
```

### QuestDB Service
```bash
QUESTDB_HOST=questdb-service.railway.internal
QUESTDB_PORT=9009
QUESTDB_USER=admin
QUESTDB_PASSWORD=quest
# Lub publiczny URL:
# QUESTDB_HOST=questdb-service.railway.app
```

### Redis Service
```bash
REDIS_URL=redis://redis-service.railway.internal:6379
# Lub publiczny URL:
# REDIS_URL=redis://redis-service.railway.app:6379
```

---

## 🔗 Railway Private Network

Railway automatycznie tworzy **private network** między serwisami w tym samym projekcie. Możesz używać nazw serwisów jako hostnames:

- `backend-service.railway.internal:8000`
- `analysis-service.railway.internal:8001`
- `pocketbase-service.railway.internal:8090`
- `questdb-service.railway.internal:9009`
- `redis-service.railway.internal:6379`

**Uwaga**: `.railway.internal` działa tylko między serwisami w tym samym projekcie Railway.

---

## 📝 Uwagi

1. **Zmiany wymagają redeploy**: Po zmianie zmiennych środowiskowych, Railway automatycznie zrestartuje serwis.

2. **Kolejność deploy**: 
   - Najpierw deploy Backend i Analysis
   - Następnie pobierz ich URL-e
   - Na końcu zaktualizuj Frontend z URL-ami backendów

3. **Bezpieczeństwo**: 
   - Nie commituj haseł do repozytorium
   - Używaj Railway Secrets dla wrażliwych danych
   - W produkcji używaj silnych haseł

4. **Development vs Production**:
   - Lokalnie kod używa domyślnych wartości `localhost`
   - W Railway ustaw odpowiednie zmienne środowiskowe

---

## 🚀 Szybki Start

Użyj skryptu automatycznego:
```bash
./setup-railway-services.sh
```

Lub ręcznie przez Railway CLI (zobacz `railway-cli-setup.md`).

---

## 📚 Więcej Informacji

- [Railway Multi-Service Setup](./RAILWAY_MULTI_SERVICE_SETUP.md)
- [Railway CLI Setup](./railway-cli-setup.md)
- [Railway Deploy Steps](./RAILWAY_DEPLOY_STEPS.md)

