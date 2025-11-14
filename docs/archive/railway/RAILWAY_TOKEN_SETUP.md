# Railway Token Setup

Ten dokument opisuje jak skonfigurować i używać tokenu Railway API.

## 🔑 Token Railway

**⚠️ WAŻNE**: Railway CLI wymaga interaktywnego logowania przez `railway login`. Token API nie może być użyty bezpośrednio do autentykacji CLI w lokalnym środowisku.

Token Railway API może być używany w:
- **CI/CD pipelines** (GitHub Actions, GitLab CI, etc.) przez Railway API
- **Automation scripts** używające Railway REST API
- **Programmatic access** do Railway resources

Dla lokalnego użycia CLI, musisz użyć `railway login`.

## 📝 Konfiguracja Tokenu

### 1. Plik .railway.env

Token został zapisany w pliku `.railway.env`:

```bash
RAILWAY_API_TOKEN=db768a10-39af-4211-b81e-b0730df1ae4f
```

**⚠️ WAŻNE**: Plik `.railway.env` jest w `.gitignore` i nie zostanie commitowany do repozytorium.

### 2. Użycie Tokenu

#### Opcja A: Automatyczne (przez skrypty)

Skrypty `create-railway-project.sh` i `setup-railway-services.sh` automatycznie ładują token z `.railway.env`:

```bash
./create-railway-project.sh
./setup-railway-services.sh
```

#### Opcja B: Ręczne (przez zmienną środowiskową)

```bash
# Załaduj token
export RAILWAY_API_TOKEN=db768a10-39af-4211-b81e-b0730df1ae4f

# Lub z pliku
export $(grep -v '^#' .railway.env | xargs)

# Teraz możesz używać Railway CLI
railway variables --set "KEY=VALUE" --service <service-name>
```

#### Opcja C: W CI/CD (GitHub Actions, GitLab CI, etc.)

```yaml
# Przykład dla GitHub Actions
env:
  RAILWAY_API_TOKEN: ${{ secrets.RAILWAY_API_TOKEN }}

steps:
  - name: Set Railway variables
    run: |
      railway variables --set "KEY=VALUE" --service <service-name>
```

## 🔐 Bezpieczeństwo

1. **Nigdy nie commituj tokenu** - plik `.railway.env` jest w `.gitignore`
2. **Używaj secrets w CI/CD** - przechowuj token w secrets (GitHub Secrets, GitLab CI Variables, etc.)
3. **Rotuj tokeny regularnie** - zmieniaj tokeny co jakiś czas
4. **Ogranicz uprawnienia** - używaj tokenów z minimalnymi wymaganymi uprawnieniami

## 📋 Jak uzyskać nowy token

1. Przejdź do Railway Dashboard: https://railway.app
2. Kliknij na swój profil (prawy górny róg)
3. Przejdź do **Settings** → **Tokens**
4. Kliknij **New Token**
5. Nadaj nazwę tokenowi i skopiuj go
6. Zaktualizuj `.railway.env` z nowym tokenem

## 🚀 Przykłady użycia

### Ustawienie zmiennych środowiskowych

```bash
# Z tokenem w .railway.env
./setup-railway-services.sh

# Lub ręcznie
export $(grep -v '^#' .railway.env | xargs)
railway variables --set "PORT=8000" --service backend
```

### Deploy z tokenem

```bash
export $(grep -v '^#' .railway.env | xargs)
railway up --service frontend
```

### Sprawdzenie autentykacji

```bash
export $(grep -v '^#' .railway.env | xargs)
railway whoami
```

## ⚠️ Troubleshooting

### Problem: "Not authenticated"

```bash
# Sprawdź czy token jest załadowany
echo $RAILWAY_API_TOKEN

# Załaduj token
export $(grep -v '^#' .railway.env | xargs)

# Sprawdź autentykację
railway whoami
```

### Problem: "Invalid token"

- Sprawdź czy token jest poprawny
- Upewnij się, że token nie wygasł
- Wygeneruj nowy token w Railway Dashboard

### Problem: "Permission denied"

- Sprawdź czy token ma odpowiednie uprawnienia
- Upewnij się, że masz dostęp do projektu

## 📚 Więcej Informacji

- [Railway CLI Documentation](https://docs.railway.com/guides/cli)
- [Railway API Tokens](https://docs.railway.com/reference/api#authentication)
- [Railway Environment Variables](https://docs.railway.com/guides/variables)

