# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Daily news agent that fetches articles from RSS feeds, summarizes them with Google Gemini AI, and sends curated digests via Telegram. Runs automatically via GitHub Actions at 7:00 UTC daily.

## Architecture

Four-stage pipeline orchestrated by `src/main.py`:

1. **News Fetching** (`news_fetcher.py`) - Parallel RSS feed fetching with ThreadPoolExecutor, deduplication, date filtering
2. **Summarization** (`summarizer.py`) - Gemini API calls with automatic model fallback on rate limits
3. **Curation** (`summarizer.py`) - Final digest assembly with timestamp and formatting
4. **Delivery** (`telegram_sender.py`) - Telegram Bot API with automatic markdown fallback on 400 errors

Configuration in `config.py`: API keys, RSS feed categories, Gemini models, prompts (summary/curation/weekly).

## Running Locally

```bash
# Setup
cp .env.example .env
# Edit .env with actual keys: GOOGLE_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS

# Install dependencies
pip install -r requirements.txt

# Run daily digest
cd src && python main.py

# Run weekly digest
cd src && python main.py --weekly

# Test individual components
cd src && python news_fetcher.py  # Fetch only
cd src && python summarizer.py    # Fetch + summarize
cd src && python telegram_sender.py  # Send test message
```

## GitHub Actions

- `.github/workflows/daily_news.yml` - Daily digest at 7:00 UTC (cron + manual trigger)
- `.github/workflows/weekly_news.yml` - Weekly digest (manual trigger only)
- Required secrets: `GOOGLE_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

Note: Use singular `TELEGRAM_CHAT_ID` in GitHub secrets, but code supports `TELEGRAM_CHAT_IDS` (comma-separated) for multiple recipients in local `.env`.

## Critical Implementation Details

### Gemini Rate Limit Handling

Free tier has 20 requests/day per model. `summarizer.py` implements automatic fallback chain:
1. `gemini-2.5-flash` → 2. `gemini-2.5-flash-lite` → 3. `gemini-3-flash` → 4. `gemini-3.1-flash-lite`

Global `_current_model_index` persists across API calls within same run. On 429/RESOURCE_EXHAUSTED: retries 3x with exponential backoff (10s, 20s, 30s), then switches to next model.

### Telegram Error Recovery

`telegram_sender.py` handles 400 errors (often malformed markdown from LLM) with automatic retry using `parse_mode=None`. Splits messages >4096 chars with continuation markers. Validates `TELEGRAM_CHAT_IDS` non-empty at start of `send_telegram_message()`.

### News Fetching Strategy

- Fetches max 10 articles per feed, filters by publication date (24h daily, 168h weekly)
- Deduplicates by lowercase title, sorts by date descending
- Takes top 5 articles/category (daily) or 10 (weekly)
- RSS feed categories: KI & Technologie, SAP, Deutsche Politik, Internationale Politik, Wirtschaft

## Common Issues

**Empty chat ID list**: Code now fails fast with explicit error. Check `TELEGRAM_CHAT_IDS` in `.env` or `TELEGRAM_CHAT_ID` in GitHub secrets.

**Rate limit exhaustion**: All 4 Gemini models depleted = exception thrown. Occurs if >20 requests/model used that day. Wait 24h or use paid API.

**Markdown parsing errors**: Automatic fallback to plain text. If persistent, check prompt templates in `config.py` for invalid Telegram markdown syntax.

## Code Conventions

- German text in prompts, output messages, and comments
- Type hints on function signatures
- Error handling: catch exceptions, send user-friendly Telegram error message, exit with status 1
- Use `print()` for progress logging (GitHub Actions captures stdout)

## Google Calendar Integration (Optional)

Die Calendar-Integration zeigt deine Termine im Morgen-Digest an. Sie ist standardmäßig deaktiviert und nutzt einen Google Service Account.

### Setup

1. **Google Cloud Project**
   - Gehe zu https://console.cloud.google.com/
   - Erstelle ein neues Projekt oder wähle ein bestehendes
   - Aktiviere die "Google Calendar API" unter APIs & Services > Library

2. **Service Account erstellen**
   - Gehe zu APIs & Services > Credentials
   - Klicke "Create Credentials" > "Service Account"
   - Name vergeben, Rolle "Viewer" reicht
   - Unter "Keys" einen neuen JSON Key erstellen und herunterladen

3. **Kalender für Service Account freigeben**
   - Öffne Google Calendar (calendar.google.com)
   - Einstellungen des gewünschten Kalenders öffnen
   - Unter "Für bestimmte Personen freigeben" die Service Account Email hinzufügen
   - Email-Format: `NAME@PROJECT-ID.iam.gserviceaccount.com`

4. **Lokale Nutzung**
   - Service Account JSON als `service_account.json` im Projekt-Root speichern
   - In `.env`: `CALENDAR_ENABLED=true`

5. **GitHub Actions**
   - Neues Secret `GOOGLE_CALENDAR_CREDENTIALS` erstellen
   - Den **gesamten Inhalt** der Service Account JSON als Wert einfügen
   - In Workflow: `GOOGLE_CALENDAR_CREDENTIALS: ${{ secrets.GOOGLE_CALENDAR_CREDENTIALS }}`

### GitHub Actions Secrets (Zusammenfassung)

| Secret | Beschreibung |
|--------|--------------|
| `GOOGLE_API_KEY` | Gemini API Key |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID(s) |
| `GOOGLE_CALENDAR_CREDENTIALS` | **Neu**: Gesamte Service Account JSON |
| `CALENDAR_ENABLED` | **Neu**: `true` zum Aktivieren |

### Sicherheit

**WICHTIG**: `service_account.json` ist in `.gitignore` und darf NIEMALS committed werden!
