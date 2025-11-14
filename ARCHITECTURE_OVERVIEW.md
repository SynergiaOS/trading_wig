# 🏗️ Architecture Overview - Frontend, Backend, Analysis

## 📊 Kompletny Przegląd Systemu

### 🎯 Struktura Systemu

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                   │
│  Port: 4173 (Production) | 5173 (Development)               │
│  URL: https://frontend-production-XXXX.railway.app          │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────────┐          ┌──────────────────────┐
│   BACKEND API        │          │   ANALYSIS API       │
│   Port: 8000         │          │   Port: 8001         │
│   realtime_api_      │          │   analysis_api_      │
│   server.py          │          │   server.py          │
└──────────────────────┘          └──────────────────────┘
```

---

## 🎨 FRONTEND (React + TypeScript + Vite)

### 📁 Struktura
```
polish-finance-platform/polish-finance-app/
├── src/
│   ├── pages/
│   │   └── Dashboard.tsx          # Główny dashboard
│   ├── components/
│   │   ├── ChartModal.tsx         # Modal z wykresami
│   │   ├── CompanyAnalysisModal.tsx # Modal analizy spółki
│   │   └── ErrorBoundary.tsx       # Error handling
│   └── lib/
│       ├── dataService.ts          # API calls do backendu
│       ├── backendService.ts       # Health checks
│       ├── apiService.ts            # API client z retry
│       ├── watchlistService.ts     # Watchlist (localStorage)
│       ├── exportService.ts         # Export CSV/JSON
│       ├── formatters.ts            # Formatowanie danych
│       └── trendAnalysis.ts        # Analiza trendów
```

### 🔌 API Integracja

**Backend API (VITE_API_URL):**
- `GET /data` - WIG80 data (wszystkie 88 spółek)
- `GET /wig30` - WIG30 data (top 30 spółek)
- `GET /health` - Health check
- `GET /stats` - Statistics

**Analysis API (VITE_ANALYSIS_API_URL):**
- `GET /api/analysis/patterns` - Wzorce techniczne
- `GET /api/analysis/technical/{symbol}` - Analiza techniczna per spółka
- `GET /api/analysis` - Wszystkie analizy
- `GET /api/analysis/top?limit=10` - Top opportunities

### ✨ Funkcje Frontendu

1. **Dashboard**
   - Real-time WIG80/WIG30 data
   - Top gainers/losers
   - Volume leaders
   - Technical patterns
   - Market status & countdown

2. **Analiza Spółek**
   - Szczegółowa analiza techniczna (RSI, SMA, Bollinger Bands)
   - Analiza fundamentalna (P/E, P/B, scores)
   - Wzorce techniczne
   - Rekomendacje inwestycyjne

3. **Funkcje Użytkownika**
   - Watchlist/Favorites (localStorage)
   - Dark mode toggle
   - Export danych (CSV/JSON)
   - Filtrowanie i sortowanie
   - Notyfikacje (toasts)

4. **Wykresy**
   - Candlestick charts
   - Volume charts
   - Technical indicators overlay
   - Multiple timeframes (1D, 1W, 1M, 3M, 1Y)

### 🔧 Konfiguracja Produkcyjna

**Zmienne Środowiskowe (Railway):**
```bash
NODE_ENV=production
PORT=4173
VITE_API_URL=https://backend-production-XXXX.up.railway.app
VITE_ANALYSIS_API_URL=https://analysis-production-XXXX.up.railway.app
VITE_REFRESH_INTERVAL=30000
```

**Build:**
```bash
pnpm run build:prod
# Output: dist/ (gotowe do deploy)
```

---

## 🔧 BACKEND API (Python - Port 8000)

### 📁 Plik: `code/realtime_api_server.py`

### 🌐 Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/` | Root | API info |
| GET | `/data` | WIG80 data | JSON z 88 spółkami |
| GET | `/wig80` | WIG80 data (alias) | JSON z 88 spółkami |
| GET | `/wig30` | WIG30 data | JSON z top 30 spółkami |
| GET | `/health` | Health check | Status info |
| GET | `/stats` | Statistics | API stats |

### 📊 Response Format

```json
{
  "metadata": {
    "collection_date": "2025-11-13T10:00:00",
    "data_source": "stooq",
    "index": "WIG80",
    "currency": "PLN",
    "total_companies": 88
  },
  "companies": [
    {
      "symbol": "PKN",
      "company_name": "PKN Orlen SA",
      "current_price": 388.50,
      "change_percent": 13.76,
      "pe_ratio": 29.75,
      "pb_ratio": 2.15,
      "trading_volume": "1.5M"
    }
  ]
}
```

### 🚀 Uruchomienie

```bash
cd code
python realtime_api_server.py
# Lub z env vars:
PORT=8000 HOST=0.0.0.0 python realtime_api_server.py
```

### 🐳 Docker

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim
WORKDIR /app
COPY code/realtime_api_server.py .
COPY data/ ./data/
CMD ["python", "realtime_api_server.py"]
```

---

## 📈 ANALYSIS API (Python - Port 8001)

### 📁 Plik: `code/analysis_api_server.py`

### 🌐 Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/api/analysis` | Wszystkie analizy | Lista analiz wszystkich spółek |
| GET | `/api/analysis/top?limit=10` | Top opportunities | Top N spółek |
| GET | `/api/analysis/patterns` | Wzorce techniczne | Spółki z wykrytymi wzorcami |
| GET | `/api/analysis/technical/{symbol}` | Analiza techniczna | Analiza dla konkretnej spółki |
| GET | `/api/analysis/{symbol}` | Pełna analiza | Analiza + wzorce dla spółki |

### 📊 Response Format - Patterns

```json
{
  "timestamp": "2025-11-13T10:00:00",
  "total_with_patterns": 15,
  "companies": [
    {
      "symbol": "PKN",
      "company_name": "PKN Orlen SA",
      "current_price": 388.50,
      "change_percent": 13.76,
      "analysis": {
        "value_score": 60.0,
        "growth_score": 85.0,
        "momentum_score": 75.0,
        "overall_score": 73.3,
        "recommendation": "STRONG_BUY",
        "sentiment": "very_bullish",
        "risk_level": "medium",
        "confidence": 93.3
      },
      "patterns": [
        {
          "pattern_name": "Flaga Wzrostowa",
          "direction": "bullish",
          "strength": 0.85,
          "confidence": 0.92,
          "duration": "5-7 dni",
          "key_levels": {
            "support": 380.00,
            "resistance": 400.00
          },
          "probability": 0.78
        }
      ]
    }
  ]
}
```

### 📊 Response Format - Technical Analysis

```json
{
  "symbol": "PKN",
  "rsi": 65.4,
  "macd": 0.23,
  "bb_upper": 400.50,
  "bb_lower": 375.20,
  "sma_20": 385.00,
  "sma_50": 380.00,
  "support_level": 375.00,
  "resistance_level": 405.00
}
```

### 🚀 Uruchomienie

```bash
cd code
python analysis_api_server.py
# Lub z env vars:
ANALYSIS_PORT=8001 ANALYSIS_HOST=0.0.0.0 python analysis_api_server.py
```

### 🐳 Docker

```dockerfile
# Dockerfile.analysis
FROM python:3.11-slim
WORKDIR /app
COPY code/analysis_api_server.py .
COPY code/telegram_alerts.py .
COPY data/ ./data/
CMD ["python", "analysis_api_server.py"]
```

---

## 🔗 Integracja Frontend ↔ Backend ↔ Analysis

### 📡 Flow Danych

```
1. Frontend → Backend API
   GET /data → WIG80 companies data
   
2. Frontend → Analysis API
   GET /api/analysis/patterns → Technical patterns
   
3. Frontend → Analysis API (per company)
   GET /api/analysis/technical/{symbol} → Technical indicators
   
4. Frontend → Backend API (health)
   GET /health → Backend status
```

### ⚙️ Error Handling

**Frontend:**
- Retry logic: 3 próby z exponential backoff
- Timeout: 10s dla danych, 8s dla wzorców
- **Brak fallback** do statycznych danych w produkcji
- Graceful degradation dla non-critical features (patterns)

**Backend:**
- CORS enabled
- Error responses z proper status codes
- Logging wszystkich requestów

### 🔄 Auto-refresh

- **Dane główne:** Co 30 sekund (VITE_REFRESH_INTERVAL)
- **Wzorce:** Co 60 sekund
- **Health check:** Co 60 sekund

---

## 🚀 Deployment na Railway

### 📋 Checklist

#### Frontend Service
- [x] Dockerfile.frontend
- [x] railway-frontend.json
- [x] Build: `pnpm run build:prod`
- [ ] Variables:
  - `VITE_API_URL` (WYMAGANE)
  - `VITE_ANALYSIS_API_URL` (WYMAGANE)
  - `NODE_ENV=production`
  - `PORT=4173`

#### Backend Service
- [x] Dockerfile.backend
- [x] railway-backend.json
- [x] Port: 8000
- [ ] Variables:
  - `PORT=8000`
  - `HOST=0.0.0.0`
  - `ALLOWED_ORIGIN=*` (lub domena frontendu)

#### Analysis Service
- [x] Dockerfile.analysis
- [x] railway-analysis.json
- [x] Port: 8001
- [ ] Variables:
  - `ANALYSIS_PORT=8001`
  - `ANALYSIS_HOST=0.0.0.0`
  - `ALLOWED_ORIGIN=*` (lub domena frontendu)

### 🔗 Cross-Service Communication

**Po deploy wszystkich serwisów:**

1. **Skopiuj URL-e z Railway Dashboard:**
   - Backend: `https://backend-production-XXXX.up.railway.app`
   - Analysis: `https://analysis-production-XXXX.up.railway.app`

2. **Zaktualizuj Frontend Variables:**
   ```
   VITE_API_URL=https://backend-production-XXXX.up.railway.app
   VITE_ANALYSIS_API_URL=https://analysis-production-XXXX.up.railway.app
   ```

3. **Railway automatycznie redeploy Frontend**

---

## 🧪 Testowanie Lokalne

### 1. Uruchom Backend
```bash
cd code
python realtime_api_server.py
# Sprawdź: http://localhost:8000/data
```

### 2. Uruchom Analysis
```bash
cd code
python analysis_api_server.py
# Sprawdź: http://localhost:8001/api/analysis/patterns
```

### 3. Uruchom Frontend
```bash
cd polish-finance-platform/polish-finance-app
VITE_API_URL=http://localhost:8000 \
VITE_ANALYSIS_API_URL=http://localhost:8001 \
pnpm run dev
# Otwórz: http://localhost:5173
```

---

## 📊 Status Komponentów

| Komponent | Status | Port | Dockerfile | Railway Config |
|-----------|--------|------|------------|----------------|
| **Frontend** | ✅ Gotowy | 4173 | ✅ Dockerfile.frontend | ✅ railway-frontend.json |
| **Backend** | ✅ Gotowy | 8000 | ✅ Dockerfile.backend | ✅ railway-backend.json |
| **Analysis** | ✅ Gotowy | 8001 | ✅ Dockerfile.analysis | ✅ railway-analysis.json |

---

## ✅ Gotowe do Produkcji!

Wszystkie trzy komponenty są gotowe i zintegrowane:
- ✅ Frontend używa tylko API (bez statycznych wartości)
- ✅ Backend API działa i zwraca dane
- ✅ Analysis API działa i zwraca analizy
- ✅ Wszystko zintegrowane i przetestowane

**Następny krok:** Deploy na Railway! 🚀

