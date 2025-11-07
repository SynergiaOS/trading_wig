# Polish Financial Analysis Platform

Profesjonalna platforma analizy finansowej dla polskiego rynku akcji (WIG80/WIG30) z integracją AI, wykrywaniem wzorców technicznych i alertami Telegram.

## 🚀 Funkcje

### 📊 Real-Time Market Dashboard
- **WIG80**: 88 spółek z indeksu WIG80
- **WIG30**: Top 30 największych spółek
- Dane w czasie rzeczywistym z Stooq.pl
- Przełącznik między indeksami WIG30/WIG80
- Wizualizacje i wykresy interaktywne
- Filtrowanie i sortowanie

### 🔍 Wykrywanie Wzorców Technicznych
- **Trend Wzrostowy/Spadkowy**: Automatyczne wykrywanie trendów
- **Flaga**: Konsolidacja po silnym ruchu
- **Trójkąty**: Wzrostowe i spadkowe
- **Breakout**: Wyłamania z wysokim wolumenem
- **Momentum**: Silny pęd cenowy
- **Kanały**: Poziome formacje

### 🤖 AI Multi-Agent Analysis System
Trzy wyspecjalizowane agenty AI:

1. **Fundamental Analyst**
   - Analiza wskaźników P/E i P/B
   - Ocena wartości spółki
   - Metryki rentowności

2. **Technical Analyst**
   - Średnie kroczące (SMA)
   - Analiza zmienności
   - Poziomy wsparcia i oporu
   - Analiza wolumenu

3. **Sentiment Analyst**
   - Ocena sentymentu rynku
   - Agregacja opinii
   - Ocena ryzyka

### 🔔 Telegram Alerts
- Alerty **TYLKO** dla spółek z wykrytymi wzorcami technicznymi
- Automatyczne monitorowanie
- Wysyłanie alertów o trendach, flagach, breakout
- Top okazje na Telegram

### 📈 Trading Capabilities
- Identyfikacja okazji do szybkiego zysku
- Rekomendacje pozycjonowania (1.5-4% na transakcję)
- Obliczenia stop-loss i take-profit
- Śledzenie portfela

## 🛠️ Technology Stack

### Backend
- **Python 3.12+**: Główny backend
- **QuestDB**: Baza danych time-series
- **PocketBase**: Backend-as-a-Service (BaaS)
- **FastAPI/HTTP Server**: API endpoints

### Frontend
- **React 18**: Nowoczesny framework UI
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Vite**: Szybki build tool
- **ECharts/Lightweight Charts**: Wizualizacje danych

### AI & Analysis
- **Pattern Detection**: Wykrywanie wzorców technicznych
- **RAG System**: System wiedzy o rynku
- **Multi-Agent Analysis**: Trzy agenty analityczne

## 📦 Instalacja

### Wymagania
- Python 3.12+
- Node.js 18+
- pnpm (package manager)
- Docker (opcjonalnie, dla QuestDB)

### Backend Setup

```bash
# Zainstaluj zależności Python
cd code
pip install -r requirements.txt

# Uruchom serwery API
python3 realtime_api_server.py      # Port 8000
python3 analysis_api_server.py      # Port 8001
python3 telegram_alerts.py          # Port 8002
```

### Frontend Setup

```bash
cd polish-finance-platform/polish-finance-app
pnpm install
pnpm run build:prod
pnpm run start
```

### PocketBase Setup

```bash
# Pobierz PocketBase (jeśli nie masz)
# Uruchom
./pocketbase serve
```

## 🚀 Uruchomienie Produkcyjne

Użyj skryptu startowego:

```bash
./start-production.sh
```

Lub ręcznie:

```bash
# Backend API
cd code && python3 realtime_api_server.py &

# Analysis API
cd code && python3 analysis_api_server.py &

# Telegram Alerts API
cd code && python3 telegram_alerts.py &

# Frontend
cd polish-finance-platform/polish-finance-app
pnpm run build:prod
pnpm run start
```

## 📡 API Endpoints

### Backend API (Port 8000)
- `GET /data` - WIG80 (88 spółek)
- `GET /wig80` - WIG80 (88 spółek)
- `GET /wig30` - WIG30 (30 spółek)

### Analysis API (Port 8001)
- `GET /api/analysis` - Wszystkie analizy
- `GET /api/analysis/top?limit=10` - Top okazje
- `GET /api/analysis/patterns` - Wszystkie wzorce techniczne
- `GET /api/analysis/{SYMBOL}` - Analiza konkretnej spółki

### Telegram Alerts API (Port 8002)
- `POST /api/telegram/send` - Wysyłanie wiadomości
- `POST /api/telegram/alert` - Alert dla spółki (tylko jeśli wzorzec)
- `POST /api/telegram/top` - Top wzorce techniczne

## 🔔 Konfiguracja Telegram Alerts

1. Utwórz bota przez @BotFather
2. Uzyskaj token i chat ID
3. Ustaw zmienne środowiskowe:

```bash
export TELEGRAM_BOT_TOKEN='twój_token'
export TELEGRAM_CHAT_ID='twój_chat_id'
```

4. Uruchom monitorowanie:

```bash
cd code
python3 telegram_alerts.py --monitor
```

Szczegółowa instrukcja: [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)

## 📊 Wykrywane Wzorce Techniczne

- 🚩 **Flaga**: Konsolidacja po silnym ruchu
- 🔺 **Trójkąt Wzrostowy/Spadkowy**: Formacje trójkątne
- 📐 **Kanał Poziomy**: Konsolidacja w zakresie
- ⚡ **Breakout**: Silny ruch z wysokim wolumenem
- 📈 **Trend Wzrostowy**: Trend wzrostowy (>5%)
- 📉 **Trend Spadkowy**: Trend spadkowy (<-5%)
- 📈 **Silny Momentum**: Pęd cenowy (>8%)

## 🏗️ Struktura Projektu

```
package/
├── code/                    # Backend Python
│   ├── realtime_api_server.py
│   ├── analysis_api_server.py
│   ├── telegram_alerts.py
│   └── ...
├── polish-finance-platform/
│   └── polish-finance-app/  # Frontend React
│       ├── src/
│       ├── public/
│       └── package.json
├── data/                     # Dane WIG80
├── docs/                     # Dokumentacja
└── README.md
```

## 🔧 Konfiguracja Środowiska

### Zmienne Środowiskowe

```bash
# API URLs
export VITE_API_URL="http://localhost:8000"
export VITE_ANALYSIS_API_URL="http://localhost:8001"

# Telegram
export TELEGRAM_BOT_TOKEN="twój_token"
export TELEGRAM_CHAT_ID="twój_chat_id"

# Ports
export PORT=8000
export ANALYSIS_PORT=8001
export TELEGRAM_API_PORT=8002
```

## 📝 Licencja

Zobacz [LICENSE.md](LICENSE.md)

## 🤝 Wsparcie

Dla pytań i wsparcia, zobacz dokumentację w folderze `docs/`.

## 🎯 Roadmap

- [x] Real-time data WIG80
- [x] WIG30 support
- [x] Wykrywanie wzorców technicznych
- [x] Telegram alerts
- [x] AI analysis system
- [ ] WebSocket real-time updates
- [ ] Portfolio tracking
- [ ] Advanced charting
- [ ] Mobile app

---

**Made with ❤️ for Polish Stock Market Analysis**

