# 🚀 RAILWAY SETUP - ZACZYNAMY TUTAJ!

## KROK 1: Zaloguj się do Railway CLI

```bash
railway login
```

To otworzy przeglądarkę. Zaloguj się i autoryzuj CLI.

## KROK 2: Uruchom automatyczną konfigurację

```bash
./DO_IT_ALL.sh
```

Ten skrypt automatycznie:
- ✅ Sprawdzi czy Railway CLI działa
- ✅ Połączy projekt (jeśli istnieje)
- ✅ Sprawdzi które serwisy istnieją
- ✅ Ustawi wszystkie zmienne środowiskowe dla istniejących serwisów

## KROK 3: Dodaj brakujące serwisy przez Dashboard

Jeśli jakieś serwisy nie istnieją, dodaj je przez Railway Dashboard:

1. Otwórz: https://railway.app
2. Kliknij "+ New Service"
3. Wybierz "GitHub Repo" → SynergiaOS/trading_wig
4. Dodaj serwisy: `frontend`, `backend`, `analysis`

## KROK 4: Skonfiguruj serwisy w Dashboard

Dla każdego serwisu ustaw:

### Frontend:
- **Dockerfile Path**: `Dockerfile.frontend`
- **Health Check Path**: `/`
- **Variables**: (już ustawione przez skrypt)

### Backend:
- **Dockerfile Path**: `Dockerfile.backend`
- **Health Check Path**: `/data`
- **Variables**: (już ustawione przez skrypt)

### Analysis:
- **Dockerfile Path**: `Dockerfile.analysis`
- **Health Check Path**: `/api/analysis`
- **Variables**: (już ustawione przez skrypt)

## KROK 5: Deploy

1. W Railway Dashboard kliknij "Deploy" dla każdego serwisu
2. Zaczekaj na zakończenie builda
3. Sprawdź czy serwisy działają (zielony status)

## KROK 6: Zaktualizuj Frontend variables

Po deploy Backend i Analysis:

1. Skopiuj URL-e z Railway Dashboard:
   - Backend: `https://backend-production-XXXX.up.railway.app`
   - Analysis: `https://analysis-production-XXXX.up.railway.app`

2. W Frontend Service → Settings → Variables → Add:
   ```
   VITE_API_URL=https://backend-production-XXXX.up.railway.app
   VITE_ANALYSIS_API_URL=https://analysis-production-XXXX.up.railway.app
   ```

3. Railway automatycznie redeploy Frontend

## ✅ Gotowe!

Wszystko powinno działać. Sprawdź:
- Frontend: Otwórz URL w przeglądarce
- Backend: `curl https://backend-XXXX.railway.app/data`
- Analysis: `curl https://analysis-XXXX.railway.app/api/analysis`

---

## 📚 Więcej informacji:

- `railway-setup-commands.txt` - Wszystkie komendy i instrukcje
- `railway-setup-checklist.md` - Checklist do odhaczenia
- `RAILWAY_COMPLETE_GUIDE.md` - Kompletny przewodnik
