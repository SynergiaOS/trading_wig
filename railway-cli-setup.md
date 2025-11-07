# Railway CLI Setup - Konfiguracja z Terminala

## 🚀 Automatyczna Konfiguracja

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
```

**⚠️ WAŻNE**: W Railway Dashboard ustaw:
- Settings → Build → Dockerfile Path: `Dockerfile.backend`

### 3. Dodaj Analysis Service

```bash
railway add --service analysis --repo SynergiaOS/trading_wig
railway service analysis
railway variables --set "ANALYSIS_PORT=8001" --service analysis
railway variables --set "ANALYSIS_HOST=0.0.0.0" --service analysis
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

