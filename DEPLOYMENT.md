# Deployment Guide

## 🚀 Wdrożenie Produkcyjne

### Wymagania Systemowe

- **OS**: Linux (Ubuntu 20.04+ / Debian 11+)
- **Python**: 3.12+
- **Node.js**: 18+
- **RAM**: Minimum 2GB (4GB+ recommended)
- **Disk**: Minimum 5GB wolnego miejsca

### Krok 1: Przygotowanie Środowiska

```bash
# Aktualizacja systemu
sudo apt update && sudo apt upgrade -y

# Instalacja Python i pip
sudo apt install python3 python3-pip python3-venv -y

# Instalacja Node.js i pnpm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
npm install -g pnpm

# Instalacja Docker (opcjonalnie, dla QuestDB)
sudo apt install docker.io docker-compose -y
```

### Krok 2: Klonowanie Repozytorium

```bash
git clone https://github.com/twoj-username/polish-finance-platform.git
cd polish-finance-platform
```

### Krok 3: Konfiguracja Backend

```bash
cd code

# Utworzenie virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalacja zależności
pip install -r requirements.txt

# Konfiguracja zmiennych środowiskowych
cp .env.example .env
nano .env  # Edytuj zgodnie z potrzebami
```

### Krok 4: Konfiguracja Frontend

```bash
cd ../polish-finance-platform/polish-finance-app

# Instalacja zależności
pnpm install

# Build produkcyjny
pnpm run build:prod
```

### Krok 5: Uruchomienie z systemd (Linux)

Utwórz pliki service dla każdego serwisu:

#### `/etc/systemd/system/polish-finance-backend.service`

```ini
[Unit]
Description=Polish Finance Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/package/code
Environment="PATH=/path/to/package/code/venv/bin"
ExecStart=/path/to/package/code/venv/bin/python3 realtime_api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### `/etc/systemd/system/polish-finance-analysis.service`

```ini
[Unit]
Description=Polish Finance Analysis API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/package/code
Environment="PATH=/path/to/package/code/venv/bin"
ExecStart=/path/to/package/code/venv/bin/python3 analysis_api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### `/etc/systemd/system/polish-finance-frontend.service`

```ini
[Unit]
Description=Polish Finance Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/package/polish-finance-platform/polish-finance-app
ExecStart=/usr/bin/pnpm run start
Restart=always

[Install]
WantedBy=multi-user.target
```

Uruchomienie:

```bash
sudo systemctl daemon-reload
sudo systemctl enable polish-finance-backend
sudo systemctl enable polish-finance-analysis
sudo systemctl enable polish-finance-frontend
sudo systemctl start polish-finance-backend
sudo systemctl start polish-finance-analysis
sudo systemctl start polish-finance-frontend
```

### Krok 6: Konfiguracja Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name twoja-domena.pl;

    # Frontend
    location / {
        proxy_pass http://localhost:4173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/data {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Analysis API
    location /api/analysis {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Krok 7: SSL/HTTPS (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d twoja-domena.pl
```

## 🔒 Bezpieczeństwo

1. **Firewall**: Skonfiguruj ufw lub firewalld
2. **Secrets**: Używaj zmiennych środowiskowych, nie commituj tokenów
3. **HTTPS**: Zawsze używaj HTTPS w produkcji
4. **Rate Limiting**: Skonfiguruj rate limiting w Nginx

## 📊 Monitoring

- Użyj systemd logs: `journalctl -u polish-finance-backend`
- Skonfiguruj monitoring (Prometheus, Grafana)
- Ustaw alerty dla błędów

## 🔄 Aktualizacje

```bash
git pull origin main
cd code && source venv/bin/activate && pip install -r requirements.txt
cd ../polish-finance-platform/polish-finance-app && pnpm install && pnpm run build:prod
sudo systemctl restart polish-finance-*
```

