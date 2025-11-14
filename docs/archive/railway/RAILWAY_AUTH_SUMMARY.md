# Railway Authentication - Podsumowanie

## ✅ Co zostało skonfigurowane

1. **Token zapisany** w pliku `.railway.env`
2. **Plik `.railway.env` dodany do `.gitignore`** (bezpieczeństwo)
3. **Skrypty zaktualizowane** do automatycznego ładowania tokenu

## ⚠️ Ważne informacje

### Railway CLI vs Railway API Token

- **Railway CLI** wymaga interaktywnego logowania przez `railway login`
- **Token API** nie może być użyty bezpośrednio do autentykacji CLI
- Token jest przydatny dla:
  - CI/CD pipelines (przez Railway REST API)
  - Automation scripts
  - Programmatic access

### Aktualny status

Twój projekt **WIG** jest już połączony z Railway CLI (poprzez interaktywne logowanie).

## 🚀 Jak używać

### Lokalnie (CLI)

```bash
# Zaloguj się interaktywnie (jeśli potrzebne)
railway login

# Sprawdź status
railway status

# Używaj CLI normalnie
railway variables --set "KEY=VALUE" --service <service-name>
```

### W CI/CD (przez API)

```bash
# Użyj tokenu z .railway.env
export RAILWAY_API_TOKEN=db768a10-39af-4211-b81e-b0730df1ae4f

# Użyj Railway REST API
curl -H "Authorization: Bearer $RAILWAY_API_TOKEN" \
  https://api.railway.app/v1/projects
```

## 📋 Token jest zapisany w

- Plik: `.railway.env`
- Zmienne: `RAILWAY_TOKEN` i `RAILWAY_API_TOKEN`
- Status: ✅ Zapisany i zabezpieczony (w `.gitignore`)

## 🔗 Przydatne linki

- [Railway CLI Documentation](https://docs.railway.com/guides/cli)
- [Railway REST API](https://docs.railway.com/reference/api)
- [Railway Authentication](https://docs.railway.com/reference/api#authentication)

