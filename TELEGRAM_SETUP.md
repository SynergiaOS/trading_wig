# Telegram Alerts - Setup Guide

## 🔔 Konfiguracja Alertów Telegram

### Krok 1: Utwórz Bota Telegram

1. Otwórz Telegram i znajdź **@BotFather**
2. Wyślij komendę: `/newbot`
3. Podaj nazwę bota (np. "WIG30/WIG80 Alerts")
4. Podaj username bota: **@wig30_bot** (lub inny dostępny)
5. **Zapisz token** który otrzymasz (wygląda jak: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Uwaga**: Jeśli username @wig30_bot jest już zajęty, użyj innego (np. @wig30_alerts_bot)

### Krok 2: Uzyskaj Chat ID

**Opcja A - Przez bota:**
1. Wyślij wiadomość do swojego bota
2. Odwiedź: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Znajdź `"chat":{"id":123456789}` - to jest Twój Chat ID

**Opcja B - Przez @userinfobot:**
1. Wyślij `/start` do @userinfobot
2. Bot wyśle Ci Twój Chat ID

### Krok 3: Skonfiguruj Zmienne Środowiskowe

```bash
export TELEGRAM_BOT_TOKEN='twój_token_tutaj'
export TELEGRAM_CHAT_ID='twój_chat_id_tutaj'
```

Lub dodaj do `~/.bashrc`:
```bash
echo 'export TELEGRAM_BOT_TOKEN="twój_token"' >> ~/.bashrc
echo 'export TELEGRAM_CHAT_ID="twój_chat_id"' >> ~/.bashrc
source ~/.bashrc
```

### Krok 4: Uruchom Serwer Alertów

**Tryb API (dla integracji):**
```bash
cd code
python3 telegram_alerts.py
```

**Tryb Monitorowania (automatyczne alerty):**
```bash
cd code
python3 telegram_alerts.py --monitor
```

## 📡 API Endpoints

### 1. Wysyłanie wiadomości
```bash
curl -X POST http://localhost:8002/api/telegram/send \
  -H "Content-Type: application/json" \
  -d '{
    "bot_token": "twój_token",
    "chat_id": "twój_chat_id",
    "message": "Test wiadomości"
  }'
```

### 2. Wysyłanie alertu dla spółki
```bash
curl -X POST http://localhost:8002/api/telegram/alert \
  -H "Content-Type: application/json" \
  -d '{
    "bot_token": "twój_token",
    "chat_id": "twój_chat_id",
    "symbol": "PKN"
  }'
```

### 3. Wysyłanie top okazji
```bash
curl -X POST http://localhost:8002/api/telegram/top \
  -H "Content-Type: application/json" \
  -d '{
    "bot_token": "twój_token",
    "chat_id": "twój_chat_id",
    "limit": 5
  }'
```

## 🔄 Automatyczne Monitorowanie

Uruchom monitorowanie, które sprawdza zmiany cen co 60 sekund:

```bash
export TELEGRAM_BOT_TOKEN='twój_token'
export TELEGRAM_CHAT_ID='twój_chat_id'
cd code
python3 telegram_alerts.py --monitor
```

Alerty będą wysyłane gdy:
- Zmiana ceny >= 3% (można zmienić w kodzie: `alert_threshold`)
- Rekomendacja się zmienia
- Wykryto znaczące ruchy cenowe

## 📋 Przykładowe Wiadomości

### Alert o zmianie ceny:
```
📈 ALERT WIG80 🔴

PKN - PKNORLEN
💰 Cena: 388.50 PLN
📊 Zmiana: +13.76%

📈 Rekomendacja: BUY
⭐ Score: 75.5/100

⏰ 2025-11-07 05:30:00
```

### Top okazje:
```
🎯 TOP 5 OKAZJI WIG80

1. 🟢 PKN - PKNORLEN
   💰 388.50 PLN (+13.76%) | BUY | ⭐75.5

2. 🟢 ERB - Erbud SA
   💰 616.37 PLN (+14.94%) | STRONG_BUY | ⭐82.3
...
```

## 🛠️ Troubleshooting

**Problem: Bot nie odpowiada**
- Sprawdź czy token jest poprawny
- Upewnij się że wysłałeś `/start` do bota

**Problem: Nie otrzymuję wiadomości**
- Sprawdź Chat ID
- Sprawdź czy bot nie jest zablokowany
- Sprawdź logi: `tail -f /tmp/telegram_alerts.log`

**Problem: Rate limiting**
- Telegram ma limit: 30 wiadomości/sekundę
- Monitor sprawdza co 60 sekund (można zmienić)

## 📝 Notatki

- Bot token jest wrażliwy - nie udostępniaj publicznie
- Chat ID może być numerem lub username (z @)
- Dla grup, użyj Chat ID grupy (ujemna liczba)

