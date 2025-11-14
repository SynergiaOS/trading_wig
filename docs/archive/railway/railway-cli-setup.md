# Railway CLI Setup - Konfiguracja z Terminala

## 🆕 Tworzenie Nowego Projektu

### Automatyczne Tworzenie Projektu

Uruchom skrypt do tworzenia nowego projektu:

```bash
./create-railway-project.sh
```

Skrypt:
- ✅ Utworzy nowy projekt Railway
- ✅ Opcjonalnie doda 3 serwisy (frontend, backend, analysis)
- ✅ Pokaże następne kroki

### Ręczne Tworzenie Projektu

```bash
# Utwórz nowy projekt
railway init

# Lub z nazwą projektu
railway init trading-wig
```

## 🚀 Dodawanie Serwisów do Istniejącego Projektu

### Automatyczna Konfiguracja

Uruchom skrypt setup:

```bash
./setup-railway-services.sh
```

Skrypt automatycznie:
- ✅ Doda 3 serwisy (frontend, backend, analysis)
- ✅ Ustawi zmienne środowiskowe
- ✅ Pokaże następne kroki

## 📋 Ręczna Konfiguracja (krok po kroku)

### 1. Dodaj Frontend Service

```bash
railway add --service frontend --repo SynergiaOS/trading_wig
railway service frontend
railway variables --set "NODE_ENV=production" --service frontend
railway variables --set "PORT=4173" --service frontend
```

**⚠️ WAŻNE**: W Railway Dashboard ustaw:
- Settings → Build → Dockerfile Path: `Dockerfile.frontend`

### 2. Dodaj Backend Service

```bash
railway add --service backend --repo SynergiaOS/trading_wig
railway service backend
railway variables --set "PORT=8000" --service backend
railway variables --set "HOST=0.0.0.0" --service backend
# Railway Service Discovery (jeśli używasz osobnych serwisów dla baz danych)
railway variables --set "POCKETBASE_URL=http://pocketbase-service.railway.internal:8090" --service backend
railway variables --set "QUESTDB_HOST=questdb-service.railway.internal" --service backend
railway variables --set "QUESTDB_PORT=9009" --service backend
railway variables --set "QUESTDB_USER=admin" --service backend
railway variables --set "QUESTDB_PASSWORD=quest" --service backend
railway variables --set "REDIS_URL=redis://redis-service.railway.internal:6379" --service backend
```

**⚠️ WAŻNE**: W Railway Dashboard ustaw:
- Settings → Build → Dockerfile Path: `Dockerfile.backend`

### 3. Dodaj Analysis Service

```bash
railway add --service analysis --repo SynergiaOS/trading_wig
railway service analysis
railway variables --set "ANALYSIS_PORT=8001" --service analysis
railway variables --set "ANALYSIS_HOST=0.0.0.0" --service analysis
# Railway Service Discovery (jeśli używasz osobnych serwisów dla baz danych)
railway variables --set "POCKETBASE_URL=http://pocketbase-service.railway.internal:8090" --service analysis
railway variables --set "QUESTDB_HOST=questdb-service.railway.internal" --service analysis
railway variables --set "QUESTDB_PORT=9009" --service analysis
railway variables --set "QUESTDB_USER=admin" --service analysis
railway variables --set "QUESTDB_PASSWORD=quest" --service analysis
railway variables --set "REDIS_URL=redis://redis-service.railway.internal:6379" --service analysis
```

**⚠️ WAŻNE**: W Railway Dashboard ustaw:
- Settings → Build → Dockerfile Path: `Dockerfile.analysis`

### 4. Deploy Serwisów

```bash
# Deploy Frontend
railway up --service frontend

# Deploy Backend
railway up --service backend

# Deploy Analysis
railway up --service analysis
```

### 5. Zaktualizuj Frontend Variables (po deploy)

Po deploy Backend i Analysis, pobierz ich URL-e i zaktualizuj Frontend:

```bash
# Sprawdź URL-e w Railway Dashboard lub użyj:
railway domain --service backend
railway domain --service analysis

# Zaktualizuj Frontend variables
railway variables --set "VITE_API_URL=https://backend-url.railway.app" --service frontend
railway variables --set "VITE_ANALYSIS_API_URL=https://analysis-url.railway.app" --service frontend
```

## 🔍 Przydatne Komendy

### Sprawdź status
```bash
railway status
railway service  # lista serwisów
```

### Wyświetl zmienne
```bash
railway variables --service frontend
railway variables --service backend
railway variables --service analysis
```

### Logi
```bash
railway logs --service frontend
railway logs --service backend
railway logs --service analysis
```

### Otwórz Dashboard
```bash
railway open
```

## ⚠️ Ograniczenia CLI

Railway CLI **NIE pozwala** na:
- ❌ Ustawienie Dockerfile Path (trzeba przez Dashboard)
- ❌ Konfigurację build settings (trzeba przez Dashboard)

Railway CLI **POZWALA** na:
- ✅ Dodawanie serwisów
- ✅ Ustawianie zmiennych środowiskowych
- ✅ Deploy serwisów
- ✅ Wyświetlanie logów
- ✅ Zarządzanie domenami

## 📚 Więcej Informacji

- [Railway CLI Documentation](https://docs.railway.app/develop/cli)
- [Railway Deploy Steps](./RAILWAY_DEPLOY_STEPS.md)

