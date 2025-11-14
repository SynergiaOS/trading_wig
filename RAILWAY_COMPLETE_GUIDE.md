# Railway Deployment - Kompletny Przewodnik

> **Ostatnia aktualizacja**: 2025-11-07  
> **Projekt**: WIG - Polish Finance Trading Platform  
> **Architektura**: Multi-service (Frontend, Backend, Analysis)

---

## 📋 Spis Treści

1. [Szybki Start](#szybki-start)
2. [Architektura](#architektura)
3. [Konfiguracja przez Dashboard](#konfiguracja-przez-dashboard)
4. [Zmienne Środowiskowe](#zmienne-środowiskowe)
5. [Deployment](#deployment)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Szybki Start

### Opcja 1: Railway Dashboard (Zalecane) ⭐

1. **Otwórz Railway Dashboard**: https://railway.app
2. **Utwórz nowy projekt** lub wybierz istniejący "WIG"
3. **Dodaj serwisy** (3 serwisy: frontend, backend, analysis)
4. **Skonfiguruj każdy serwis** zgodnie z sekcją [Konfiguracja](#konfiguracja-przez-dashboard)
5. **Deploy** każdego serwisu

### Opcja 2: Railway CLI

**⚠️ UWAGA**: Railway CLI wymaga interaktywnego logowania przez przeglądarkę.

```bash
# Zaloguj się (otwiera przeglądarkę)
railway login

# Sprawdź status
railway status

# Dodaj serwisy (zobacz railway-cli-setup.md)
```

---

## 🏗️ Architektura

### Serwisy

Projekt składa się z 3 głównych serwisów:

```
┌─────────────────────────────────────────────────────────────┐
│                    RAILWAY PROJECT: WIG                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐ │
│  │  FRONTEND   │      │   BACKEND   │      │  ANALYSIS   │ │
│  │  (React)    │─────▶│  (Python)   │◀────▶│  (Python)   │ │
│  │  Port: 4173 │      │  Port: 8000 │      │  Port: 8001 │ │
│  └─────────────┘      └─────────────┘      └─────────────┘ │
│         │                    │                     │         │
│         │                    ▼                     ▼         │
│         │             ┌──────────────────────────────┐       │
│         │             │   Shared Services (opt.)     │       │
│         │             │  • Pocketbase (8090)         │       │
│         └────────────▶│  • QuestDB (9009)            │       │
│                       │  • Redis (6379)              │       │
│                       └──────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Dockerfile Mapping

| Serwis | Dockerfile | Port | Health Check |
|--------|-----------|------|--------------|
| Frontend | `Dockerfile.frontend` | 4173 | `/` |
| Backend | `Dockerfile.backend` | 8000 | `/data` |
| Analysis | `Dockerfile.analysis` | 8001 | `/api/analysis` |

---

## 🎯 Konfiguracja przez Dashboard

### Krok 1: Utwórz Projekt

1. Przejdź do: https://railway.app
2. Kliknij **"New Project"**
3. Nazwa: **WIG**
4. Environment: **production** (domyślne)

### Krok 2: Dodaj Frontend Service

1. W projekcie kliknij **"+ New Service"**
2. Wybierz **"GitHub Repo"**
3. Wybierz repo: **SynergiaOS/trading_wig**
4. Nazwa serwisu: **frontend**

**Konfiguracja Frontend:**

- **Settings → Build**:
  - Dockerfile Path: `Dockerfile.frontend`
  - Build Command: (pozostaw puste, używamy Dockerfile)

- **Settings → Deploy**:
  - Health Check Path: `/`
  - Health Check Timeout: 100s
  - Restart Policy: ON_FAILURE
  - Max Retries: 10

- **Settings → Networking**:
  - Generate Domain (kliknij **"Generate Domain"**)
  - Port: 4173 (automatycznie wykryte z EXPOSE)

- **Settings → Variables**:
  ```
  NODE_ENV=production
  PORT=4173
  VITE_REFRESH_INTERVAL=30000
  ```
  
  **⚠️ Po deploy backend i analysis dodaj:**
  ```
  VITE_API_URL=https://backend-XXXX.up.railway.app
  VITE_ANALYSIS_API_URL=https://analysis-XXXX.up.railway.app
  ```

### Krok 3: Dodaj Backend Service

1. Kliknij **"+ New Service"**
2. Wybierz **"GitHub Repo"**
3. Wybierz repo: **SynergiaOS/trading_wig**
4. Nazwa serwisu: **backend**

**Konfiguracja Backend:**

- **Settings → Build**:
  - Dockerfile Path: `Dockerfile.backend`

- **Settings → Deploy**:
  - Health Check Path: `/data`
  - Health Check Timeout: 100s
  - Restart Policy: ON_FAILURE
  - Max Retries: 10

- **Settings → Networking**:
  - Generate Domain
  - Port: 8000

- **Settings → Variables**:
  ```
  PORT=8000
  HOST=0.0.0.0
  ```
  
  **Jeśli używasz osobnych serwisów dla baz danych, dodaj:**
  ```
  POCKETBASE_URL=http://pocketbase.railway.internal:8090
  QUESTDB_HOST=questdb.railway.internal
  QUESTDB_PORT=9009
  QUESTDB_USER=admin
  QUESTDB_PASSWORD=quest
  REDIS_URL=redis://redis.railway.internal:6379
  ```

### Krok 4: Dodaj Analysis Service

1. Kliknij **"+ New Service"**
2. Wybierz **"GitHub Repo"**
3. Wybierz repo: **SynergiaOS/trading_wig**
4. Nazwa serwisu: **analysis**

**Konfiguracja Analysis:**

- **Settings → Build**:
  - Dockerfile Path: `Dockerfile.analysis`

- **Settings → Deploy**:
  - Health Check Path: `/api/analysis`
  - Health Check Timeout: 100s
  - Restart Policy: ON_FAILURE
  - Max Retries: 10

- **Settings → Networking**:
  - Generate Domain
  - Port: 8001

- **Settings → Variables**:
  ```
  ANALYSIS_PORT=8001
  ANALYSIS_HOST=0.0.0.0
  ```
  
  **Jeśli używasz osobnych serwisów dla baz danych (te same co Backend):**
  ```
  POCKETBASE_URL=http://pocketbase.railway.internal:8090
  QUESTDB_HOST=questdb.railway.internal
  QUESTDB_PORT=9009
  QUESTDB_USER=admin
  QUESTDB_PASSWORD=quest
  REDIS_URL=redis://redis.railway.internal:6379
  ```

### Krok 5: Zaktualizuj Frontend Variables

Po deploy Backend i Analysis:

1. Skopiuj URL-e z **Settings → Networking → Domains**:
   - Backend: `https://backend-production-XXXX.up.railway.app`
   - Analysis: `https://analysis-production-XXXX.up.railway.app`

2. W **Frontend Service → Settings → Variables** dodaj:
   ```
   VITE_API_URL=https://backend-production-XXXX.up.railway.app
   VITE_ANALYSIS_API_URL=https://analysis-production-XXXX.up.railway.app
   ```

3. Redeploy Frontend (Railway automatycznie zrobi to po zmianie zmiennych)

---

## 🔧 Zmienne Środowiskowe

### Frontend Service

| Zmienna | Wartość | Opis |
|---------|---------|------|
| `NODE_ENV` | `production` | Node environment |
| `PORT` | `4173` | Port aplikacji |
| `VITE_API_URL` | `https://backend-XXXX.railway.app` | URL do Backend API |
| `VITE_ANALYSIS_API_URL` | `https://analysis-XXXX.railway.app` | URL do Analysis API |
| `VITE_REFRESH_INTERVAL` | `30000` | Refresh interval (ms) |

### Backend Service

| Zmienna | Wartość | Opis |
|---------|---------|------|
| `PORT` | `8000` | Port aplikacji |
| `HOST` | `0.0.0.0` | Host binding |
| `POCKETBASE_URL` ⚙️ | `http://pocketbase.railway.internal:8090` | Pocketbase URL (opcjonalne) |
| `QUESTDB_HOST` ⚙️ | `questdb.railway.internal` | QuestDB host (opcjonalne) |
| `QUESTDB_PORT` ⚙️ | `9009` | QuestDB port (opcjonalne) |
| `QUESTDB_USER` ⚙️ | `admin` | QuestDB user (opcjonalne) |
| `QUESTDB_PASSWORD` ⚙️ | `quest` | QuestDB password (opcjonalne) |
| `REDIS_URL` ⚙️ | `redis://redis.railway.internal:6379` | Redis URL (opcjonalne) |

⚙️ = Tylko jeśli używasz osobnych serwisów dla baz danych

### Analysis Service

Te same zmienne co Backend (z wyjątkiem PORT i HOST):

| Zmienna | Wartość | Opis |
|---------|---------|------|
| `ANALYSIS_PORT` | `8001` | Port aplikacji |
| `ANALYSIS_HOST` | `0.0.0.0` | Host binding |
| + wszystkie zmienne z Backend Service | ... | (POCKETBASE_URL, QUESTDB_*, REDIS_URL) |

---

## 🚀 Deployment

### Automatyczny Deploy

Railway automatycznie deployuje gdy:
- Pushjesz zmiany do GitHub
- Zmieniasz zmienne środowiskowe
- Klikasz **"Deploy"** w Dashboard

### Ręczny Deploy

1. W Railway Dashboard przejdź do serwisu
2. Kliknij **"Deployments"**
3. Kliknij **"Deploy"** lub **"Redeploy"**

### Kolejność Deploy

```
1️⃣ Backend   → Deploy i zaczekaj na URL
2️⃣ Analysis  → Deploy i zaczekaj na URL
3️⃣ Frontend  → Zaktualizuj zmienne (VITE_API_URL, VITE_ANALYSIS_API_URL) i deploy
```

---

## 🔗 Railway Private Network

Railway automatycznie tworzy **private network** między serwisami w tym samym projekcie.

### Używanie Private Network

Zamiast publicznych URL-i, możesz używać internal hostnames:

```bash
# Format
http://<service-name>.railway.internal:<port>

# Przykłady
http://backend.railway.internal:8000
http://analysis.railway.internal:8001
http://pocketbase.railway.internal:8090
http://questdb.railway.internal:9009
http://redis.railway.internal:6379
```

### Kiedy używać Private Network

- ✅ Dla komunikacji backend ↔ backend
- ✅ Dla połączeń backend ↔ database
- ✅ Dla komunikacji między serwisami w tym samym projekcie
- ❌ Dla frontend ↔ backend (frontend działa w przeglądarce klienta, potrzebuje publicznego URL)

---

## 🐛 Troubleshooting

### Problem: Build fails

**Objawy**: Build kończy się błędem  
**Rozwiązanie**:
1. Sprawdź czy Dockerfile Path jest ustawiony poprawnie
2. Sprawdź logi: **Deployments → View Logs**
3. Sprawdź czy wszystkie pliki są w repo

### Problem: "Cannot connect to backend"

**Objawy**: Frontend nie łączy się z Backend  
**Rozwiązanie**:
1. Sprawdź `VITE_API_URL` i `VITE_ANALYSIS_API_URL` w Frontend Variables
2. Upewnij się, że używasz publicznych URL-i (nie `.railway.internal`)
3. Sprawdź czy Backend i Analysis są uruchomione

### Problem: "Health check failed"

**Objawy**: Serwis nie startuje, health check timeout  
**Rozwiązanie**:
1. Sprawdź czy Health Check Path jest poprawny
2. Zwiększ Health Check Timeout (100s → 300s)
3. Sprawdź logi czy aplikacja startuje poprawnie

### Problem: "RAILWAY_TOKEN invalid"

**Objawy**: CLI pokazuje błąd "invalid RAILWAY_TOKEN"  
**Rozwiązanie**:
```bash
# Usuń token ze środowiska
unset RAILWAY_TOKEN RAILWAY_API_TOKEN

# Usuń konfigurację
rm ~/.railway/config.json

# Zaloguj się ponownie
railway login
```

### Problem: Port conflicts

**Objawy**: Aplikacja nie startuje, błąd "port already in use"  
**Rozwiązanie**:
- Railway automatycznie zarządza portami przez zmienną `PORT`
- Upewnij się, że kod używa `os.getenv('PORT')` lub `process.env.PORT`

---

## 📊 Monitoring

### W Railway Dashboard

1. **Deployments** → Zobacz historię deploymentów
2. **Metrics** → CPU, Memory, Network usage
3. **Logs** → Real-time logs dla każdego serwisu

### Health Checks

Railway automatycznie monitoruje health checks:

- **Frontend**: `GET /` → powinien zwrócić 200
- **Backend**: `GET /data` → powinien zwrócić JSON
- **Analysis**: `GET /api/analysis` → powinien zwrócić JSON

---

## 🔐 Bezpieczeństwo

### Zmienne Środowiskowe

- ✅ Używaj Railway Variables dla secrets (hasła, tokeny)
- ✅ Nie commituj secrets do repo
- ✅ Używaj Railway Secrets dla wrażliwych danych

### Private Network

- ✅ Używaj `.railway.internal` dla komunikacji między serwisami
- ✅ Publiczne URL-e tylko dla frontend i API endpoints

### CORS

- Backend i Analysis mają skonfigurowane CORS headers
- Domyślnie: `Access-Control-Allow-Origin: *`
- W produkcji: ogranicz do konkretnych domen

---

## 📚 Dodatkowe Zasoby

### Dokumentacja Railway

- [Railway Documentation](https://docs.railway.com)
- [Railway CLI Reference](https://docs.railway.com/reference/cli-api)
- [Railway Variables Guide](https://docs.railway.com/guides/variables)

### Lokalne Pliki

- `Dockerfile.frontend` - Frontend Docker image
- `Dockerfile.backend` - Backend Docker image
- `Dockerfile.analysis` - Analysis Docker image
- `railway-frontend.json` - Frontend config
- `railway-backend.json` - Backend config
- `railway-analysis.json` - Analysis config

---

## 🎯 Checklist Deployment

### Przed Deploymentem

- [ ] Kod jest w GitHub repo (SynergiaOS/trading_wig)
- [ ] Dockerfiles są poprawne
- [ ] Zmienne środowiskowe są zdefiniowane
- [ ] Health checks są skonfigurowane

### Podczas Deploymentu

- [ ] Backend zdeployowany i działa
- [ ] Analysis zdeployowany i działa
- [ ] Frontend zmienne zaktualizowane (VITE_API_URL, VITE_ANALYSIS_API_URL)
- [ ] Frontend zdeployowany i działa

### Po Deploymencie

- [ ] Frontend otwiera się w przeglądarce
- [ ] Frontend łączy się z Backend (sprawdź Network w DevTools)
- [ ] Frontend łączy się z Analysis
- [ ] Health checks są zielone dla wszystkich serwisów
- [ ] Logi nie pokazują błędów

---

## 💡 Pro Tips

### 1. Railway Private Network

Dla komunikacji backend → backend używaj private network (szybciej i bezpieczniej):

```bash
# Zamiast publicznego URL
POCKETBASE_URL=https://pocketbase.railway.app

# Użyj private network
POCKETBASE_URL=http://pocketbase.railway.internal:8090
```

### 2. Auto-deploy z GitHub

Railway automatycznie deployuje przy każdym pushu do GitHub. Możesz to wyłączyć:
- Settings → Deploy → Deploy Triggers → On Push (włącz/wyłącz)

### 3. Custom Domains

Railway pozwala na custom domains:
- Settings → Networking → Custom Domain → Add Domain

### 4. Environment Variables z innych serwisów

Railway automatycznie udostępnia zmienne:
- `RAILWAY_ENVIRONMENT` - nazwa środowiska
- `RAILWAY_SERVICE_NAME` - nazwa serwisu
- `RAILWAY_PUBLIC_DOMAIN` - publiczny URL serwisu

Możesz ich użyć do service discovery:

```bash
# W Frontend variables
VITE_API_URL=${{RAILWAY_STATIC_URL}}
# Railway automatycznie podstawi URL
```

---

## 🔄 Workflow Development → Production

### Development (lokalnie)

```bash
# Frontend
cd polish-finance-platform/polish-finance-app
pnpm install
pnpm run dev

# Backend
cd code
python realtime_api_server.py

# Analysis
python analysis_api_server.py
```

### Production (Railway)

1. Push do GitHub
2. Railway automatycznie deployuje
3. Sprawdź w Dashboard czy wszystko działa
4. Monitoruj logi i metryki

---

## 📞 Support

### Potrzebujesz pomocy?

1. Sprawdź [Troubleshooting](#troubleshooting)
2. Zobacz logi w Railway Dashboard
3. Sprawdź Railway Status Page: https://status.railway.app
4. Railway Community: https://discord.gg/railway

---

## 📝 Notatki

### Railway CLI Authentication

- Railway CLI wymaga interaktywnego logowania przez `railway login`
- Token API (`RAILWAY_API_TOKEN`) jest tylko dla REST API w CI/CD
- Nie używaj `RAILWAY_TOKEN` w CLI - to spowoduje błąd "invalid RAILWAY_TOKEN"

### Service Discovery

- Railway automatycznie tworzy DNS dla wszystkich serwisów
- Format internal: `<service-name>.railway.internal:<port>`
- Format public: `https://<service-name>-production-XXXX.up.railway.app`

### Costs

Railway oferuje:
- **Developer Plan**: $5/miesiąc + usage
- **Team Plan**: $20/miesiąc + usage
- Free trial: $5 credit

