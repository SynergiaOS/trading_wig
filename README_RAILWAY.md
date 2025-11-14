# Railway Deployment - README

> **Start tutaj** 👇

---

## 🎯 Wszystko czego potrzebujesz

### 📘 Główny Przewodnik
**[RAILWAY_COMPLETE_GUIDE.md](./RAILWAY_COMPLETE_GUIDE.md)** - Kompletny przewodnik krok po kroku

### 🚀 Szybki Setup
**[railway-dashboard-setup.sh](./railway-dashboard-setup.sh)** - Interaktywny helper do konfiguracji przez Dashboard

### 📋 Environment Variables
- `env.railway.frontend.example` - Zmienne dla Frontend
- `env.railway.backend.example` - Zmienne dla Backend
- `env.railway.analysis.example` - Zmienne dla Analysis

---

## ⚡ Quick Start (2 minuty)

### Opcja 1: Railway Dashboard ⭐ (Zalecane)

```bash
# Uruchom helper
./railway-dashboard-setup.sh
```

Helper przeprowadzi Cię przez wszystkie kroki w Railway Dashboard.

### Opcja 2: Ręcznie

1. Otwórz: https://railway.app
2. Utwórz projekt "WIG"
3. Dodaj 3 serwisy (frontend, backend, analysis)
4. Dla każdego serwisu:
   - Ustaw Dockerfile Path
   - Dodaj zmienne środowiskowe (zobacz pliki `env.railway.*.example`)
   - Deploy

---

## 📂 Pliki Railway

### Używane Pliki

| Plik | Opis |
|------|------|
| `RAILWAY_COMPLETE_GUIDE.md` | Główny przewodnik (czytaj to!) |
| `railway-dashboard-setup.sh` | Interaktywny setup helper |
| `env.railway.*.example` | Templates zmiennych środowiskowych |
| `Dockerfile.frontend` | Frontend Docker image |
| `Dockerfile.backend` | Backend Docker image |
| `Dockerfile.analysis` | Analysis Docker image |
| `railway-*.json` | Railway service configs |

### Archiwalne Pliki (dla referencji)

<details>
<summary>Kliknij aby rozwinąć</summary>

- `RAILWAY_ENV_VARIABLES.md` - Zmienne środowiskowe (consolidated → RAILWAY_COMPLETE_GUIDE.md)
- `RAILWAY_DEPLOYMENT.md` - Deployment guide (consolidated → RAILWAY_COMPLETE_GUIDE.md)
- `RAILWAY_MULTI_SERVICE_SETUP.md` - Multi-service setup (consolidated → RAILWAY_COMPLETE_GUIDE.md)
- `RAILWAY_DEPLOY_STEPS.md` - Deploy steps (consolidated → railway-dashboard-setup.sh)
- `RAILWAY_ENV_SETUP.md` - Env setup (consolidated → env.railway.*.example)
- `RAILWAY_QUICK_START.md` - Quick start (consolidated → README_RAILWAY.md)
- `railway-cli-setup.md` - CLI setup (CLI jest interaktywny, Dashboard jest lepszy)
- `RAILWAY_TOKEN_SETUP.md` - Token setup (token nie działa z CLI)
- `RAILWAY_AUTH_SUMMARY.md` - Auth summary (nieaktualne)
- `RAILWAY_CLI_USAGE.md` - CLI usage (nieaktualne)
- `RAILWAY_FIX_AUTH.md` - Auth fix (nieaktualne)
- `create-railway-project.sh` - Project creation (użyj Dashboard)
- `setup-railway-services.sh` - Services setup (użyj Dashboard)
- `fix-railway-auth.sh` - Auth fix (niepotrzebne)

</details>

---

## 🎓 Architektura

### Multi-Service Setup

```
Frontend (4173) → Backend (8000) ⇄ Analysis (8001)
                       ↓               ↓
                  [Shared Services]
                  • Pocketbase (8090)
                  • QuestDB (9009)
                  • Redis (6379)
```

### Railway Private Network

Wszystkie serwisy w projekcie mogą się łączyć przez private network:
- `backend.railway.internal:8000`
- `analysis.railway.internal:8001`
- `pocketbase.railway.internal:8090`

---

## ✅ Checklist

- [ ] Przeczytaj `RAILWAY_COMPLETE_GUIDE.md`
- [ ] Uruchom `./railway-dashboard-setup.sh`
- [ ] Skonfiguruj 3 serwisy w Railway Dashboard
- [ ] Deploy wszystkich serwisów
- [ ] Zaktualizuj Frontend variables (po deploy backend/analysis)
- [ ] Zweryfikuj działanie wszystkich serwisów

---

## 📞 Pomoc

- 📘 **Główny przewodnik**: [RAILWAY_COMPLETE_GUIDE.md](./RAILWAY_COMPLETE_GUIDE.md)
- 🔧 **Setup helper**: `./railway-dashboard-setup.sh`
- 🌐 **Railway Docs**: https://docs.railway.com
- 💬 **Railway Discord**: https://discord.gg/railway

---

**Gotowy na deploy? → Uruchom: `./railway-dashboard-setup.sh`** 🚀

