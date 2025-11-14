# 🚨 Railway Environment Variables - REAL-TIME API

## ⚠️ WAŻNE: Nowe zmienne środowiskowe dla Real-Time API

Po migracji na real-time API, **MUSISZ** dodać nowe zmienne środowiskowe w Railway!

---

## 📋 Backend Service

### Wymagane zmienne:
```bash
PORT=8000
HOST=0.0.0.0
USE_REALTIME_API=true  # ⚠️ NOWA ZMIENNA!
```

### Opcjonalne:
```bash
ALLOWED_ORIGIN=*
```

### Ustawienie przez Railway CLI:
```bash
railway service backend
railway variables --set "PORT=8000" --service backend
railway variables --set "HOST=0.0.0.0" --service backend
railway variables --set "USE_REALTIME_API=true" --service backend
```

---

## 📋 Analysis Service

### Wymagane zmienne:
```bash
PORT=8001
HOST=0.0.0.0
USE_BACKEND_API=true  # ⚠️ NOWA ZMIENNA!
BACKEND_API_URL=https://backend-production-XXXX.up.railway.app  # ⚠️ NOWA ZMIENNA!
```

**UWAGA**: `BACKEND_API_URL` musi być URL-em Twojego Backend serwisu w Railway!

### Ustawienie przez Railway CLI:
```bash
railway service analysis
railway variables --set "PORT=8001" --service analysis
railway variables --set "HOST=0.0.0.0" --service analysis
railway variables --set "USE_BACKEND_API=true" --service analysis
railway variables --set "BACKEND_API_URL=https://backend-production-XXXX.up.railway.app" --service analysis
```

**WAŻNE**: Zastąp `backend-production-XXXX.up.railway.app` rzeczywistym URL-em Twojego Backend serwisu!

---

## 📋 Frontend Service

### Wymagane zmienne (bez zmian):
```bash
NODE_ENV=production
PORT=4173
VITE_REFRESH_INTERVAL=30000
VITE_API_URL=https://backend-production-XXXX.up.railway.app
VITE_ANALYSIS_API_URL=https://analysis-production-XXXX.up.railway.app
```

---

## 🔧 Szybka konfiguracja przez Railway Dashboard

### 1. Backend Service
1. Otwórz Railway Dashboard
2. Przejdź do **Backend Service** → **Settings** → **Variables**
3. Dodaj:
   - `USE_REALTIME_API` = `true`

### 2. Analysis Service
1. Przejdź do **Analysis Service** → **Settings** → **Variables**
2. Dodaj:
   - `USE_BACKEND_API` = `true`
   - `BACKEND_API_URL` = `https://backend-production-XXXX.up.railway.app` (Twój URL!)

### 3. Sprawdź URL-e
1. W Railway Dashboard → **Backend Service** → **Settings** → **Networking**
2. Skopiuj **Public Domain** (np. `backend-production-XXXX.up.railway.app`)
3. Użyj tego URL-a w:
   - Analysis: `BACKEND_API_URL`
   - Frontend: `VITE_API_URL`

---

## ✅ Checklist

- [ ] Backend: `USE_REALTIME_API=true` ustawione
- [ ] Analysis: `USE_BACKEND_API=true` ustawione
- [ ] Analysis: `BACKEND_API_URL` ustawione na prawidłowy URL Backend
- [ ] Frontend: `VITE_API_URL` ustawione na prawidłowy URL Backend
- [ ] Frontend: `VITE_ANALYSIS_API_URL` ustawione na prawidłowy URL Analysis

---

## 🐛 Troubleshooting

### Problem: Backend nie pobiera danych
- **Sprawdź**: Czy `USE_REALTIME_API=true` jest ustawione
- **Sprawdź**: Logi Backend w Railway Dashboard

### Problem: Analysis nie działa
- **Sprawdź**: Czy `USE_BACKEND_API=true` jest ustawione
- **Sprawdź**: Czy `BACKEND_API_URL` wskazuje na prawidłowy URL Backend
- **Sprawdź**: Czy Backend jest dostępny (health check)

### Problem: Frontend nie łączy się z API
- **Sprawdź**: Czy `VITE_API_URL` i `VITE_ANALYSIS_API_URL` są ustawione
- **Sprawdź**: Czy URL-e są poprawne (z `https://`)
- **Sprawdź**: Czy serwisy są zdeployowane i działają

