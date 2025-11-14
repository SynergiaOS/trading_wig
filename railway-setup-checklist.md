# Railway Setup Checklist

## ✅ Przed rozpoczęciem

- [ ] Railway CLI zainstalowany: `npm install -g @railway/cli`
- [ ] Zalogowany do Railway: `railway login`
- [ ] Projekt WIG utworzony w Railway Dashboard
- [ ] Repo GitHub połączone: SynergiaOS/trading_wig

## 🔧 Konfiguracja Serwisów

### Frontend Service

- [ ] Serwis "frontend" utworzony
- [ ] Dockerfile Path: `Dockerfile.frontend`
- [ ] Health Check Path: `/`
- [ ] Domain wygenerowany
- [ ] Zmienne środowiskowe ustawione:
  - [ ] `NODE_ENV=production`
  - [ ] `PORT=4173`
  - [ ] `VITE_REFRESH_INTERVAL=30000`
- [ ] Deploy zakończony
- [ ] Status: ✅ Działa

### Backend Service

- [ ] Serwis "backend" utworzony
- [ ] Dockerfile Path: `Dockerfile.backend`
- [ ] Health Check Path: `/data`
- [ ] Domain wygenerowany
- [ ] URL skopiowany: `https://backend-XXXX.railway.app`
- [ ] Zmienne środowiskowe ustawione:
  - [ ] `PORT=8000`
  - [ ] `HOST=0.0.0.0`
- [ ] Deploy zakończony
- [ ] Status: ✅ Działa
- [ ] Test: `curl https://backend-XXXX.railway.app/data`

### Analysis Service

- [ ] Serwis "analysis" utworzony
- [ ] Dockerfile Path: `Dockerfile.analysis`
- [ ] Health Check Path: `/api/analysis`
- [ ] Domain wygenerowany
- [ ] URL skopiowany: `https://analysis-XXXX.railway.app`
- [ ] Zmienne środowiskowe ustawione:
  - [ ] `ANALYSIS_PORT=8001`
  - [ ] `ANALYSIS_HOST=0.0.0.0`
- [ ] Deploy zakończony
- [ ] Status: ✅ Działa
- [ ] Test: `curl https://analysis-XXXX.railway.app/api/analysis`

## 🔗 Finalna Konfiguracja

- [ ] Frontend variables zaktualizowane:
  - [ ] `VITE_API_URL` ustawiony na Backend URL
  - [ ] `VITE_ANALYSIS_API_URL` ustawiony na Analysis URL
- [ ] Frontend redeployed
- [ ] Frontend działa i łączy się z Backend
- [ ] Frontend działa i łączy się z Analysis

## ✅ Weryfikacja

- [ ] Wszystkie serwisy mają status: ✅ Działa
- [ ] Frontend otwiera się w przeglądarce
- [ ] Frontend łączy się z Backend (sprawdź Network w DevTools)
- [ ] Frontend łączy się z Analysis
- [ ] Health checks są zielone dla wszystkich serwisów
- [ ] Logi nie pokazują błędów

## 🎉 Gotowe!

Wszystko skonfigurowane i działające!
