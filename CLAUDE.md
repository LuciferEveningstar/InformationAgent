# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Daily news agent that fetches articles from RSS feeds, summarizes them with OpenRouter API (MiniMax M2.7), and sends curated digests via Telegram. Includes optional Google Calendar integration for daily agenda. Runs automatically via GitHub Actions at 6:00 UTC daily.

## Architecture

Five-stage pipeline orchestrated by `src/main.py`:

1. **News Fetching** (`news_fetcher.py`) - Parallel RSS feed fetching with ThreadPoolExecutor, deduplication, date filtering
2. **Weather & Pollen** (`weather_fetcher.py`) - wttr.in for weather, DWD OpenData for pollen forecast (Walldorf region)
3. **Calendar** (`calendar_fetcher.py`) - Google Calendar API via Service Account, shows today's events
4. **Summarization** (`summarizer.py`) - OpenRouter API (MiniMax M2.7) with retry logic
5. **Delivery** (`telegram_sender.py`) - Telegram Bot API with automatic HTML fallback on 400 errors

Configuration in `config.py`: API keys, RSS feed categories, OpenRouter model, prompts (summary/curation/weekly), calendar settings.

## Running Locally

```bash
# Setup
cp .env.example .env
# Edit .env with actual keys: OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS

# Install dependencies
pip install -r requirements.txt

# Run daily digest
cd src && python main.py

# Run weekly digest
cd src && python main.py --weekly

# Test individual components
cd src && python news_fetcher.py      # Fetch only
cd src && python summarizer.py        # Fetch + summarize
cd src && python telegram_sender.py   # Send test message
cd src && python calendar_fetcher.py  # Test calendar (requires service_account.json)
cd src && python test_calendar.py     # Send calendar via Telegram
cd src && python test_openrouter.py   # Test OpenRouter API (m2.7, m1, kimi, or all)
```

## GitHub Actions

- `.github/workflows/daily_news.yml` - Daily digest at 6:00 UTC (cron + manual trigger)
- `.github/workflows/weekly_news.yml` - Weekly digest (manual trigger only)

### Required Secrets

| Secret | Beschreibung |
|--------|--------------|
| `OPENROUTER_API_KEY` | OpenRouter API Key (sk-or-v1-...) |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID(s) |
| `GOOGLE_CALENDAR_CREDENTIALS` | Service Account JSON (optional, für Kalender) |

Note: Use singular `TELEGRAM_CHAT_ID` in GitHub secrets, but code supports `TELEGRAM_CHAT_IDS` (comma-separated) for multiple recipients in local `.env`.

## Critical Implementation Details

### OpenRouter API

Uses MiniMax M2.7 as default model (`OPENROUTER_MODEL` in config). Key considerations:
- MiniMax M2.7 is a reasoning model - uses internal "thinking" tokens before responding
- `max_tokens=8000` ensures enough room for reasoning + response
- Pricing: $0.30/M input, $1.20/M output (~$0.005 per full digest)
- Retry logic with exponential backoff on 429 errors

Available models in `test_openrouter.py`:
- `minimax/minimax-m2.7` (default) - Best price/performance for news summaries
- `minimax/minimax-m1` - 1M context window, more expensive
- `moonshotai/kimi-k2.5` - Multimodal, good for image analysis

### Telegram Error Recovery

`telegram_sender.py` handles 400 errors (often malformed markdown from LLM) with automatic retry using `parse_mode=None`. Splits messages >4096 chars with continuation markers. Validates `TELEGRAM_CHAT_IDS` non-empty at start of `send_telegram_message()`.

### News Fetching Strategy

- Fetches max 10 articles per feed, filters by publication date (24h daily, 168h weekly)
- Deduplicates by lowercase title, sorts by date descending
- Takes top 5 articles/category (daily) or 10 (weekly)
- RSS feed categories: KI & Technologie, SAP, Deutsche Politik, Internationale Politik, Wirtschaft

## Common Issues

**Empty chat ID list**: Code now fails fast with explicit error. Check `TELEGRAM_CHAT_IDS` in `.env` or `TELEGRAM_CHAT_ID` in GitHub secrets.

**OpenRouter rate limit**: Automatic retry with exponential backoff (10s, 20s, 30s). If persistent, check API quota at openrouter.ai.

**None response from model**: Usually means `max_tokens` too low for reasoning models. Current setting (8000) should be sufficient.

**Markdown parsing errors**: Automatic fallback to plain text. If persistent, check prompt templates in `config.py` for invalid Telegram HTML syntax.

**Calendar shows no events**: Service Account muss explizit zum Kalender eingeladen werden UND `CALENDAR_ID` muss die richtige Email-Adresse sein (nicht "primary").

## Code Conventions

- German text in prompts, output messages, and comments
- Type hints on function signatures
- Error handling: catch exceptions, send user-friendly Telegram error message, exit with status 1
- Use `print()` for progress logging (GitHub Actions captures stdout)

## Google Calendar Integration (Optional)

Zeigt heutige Termine im Morgen-Digest an. Automatisch aktiviert wenn Credentials vorhanden sind.

### Setup

1. **Google Cloud Console**: Neues Projekt erstellen, "Google Calendar API" aktivieren
2. **Service Account**: APIs & Services > Credentials > Create Credentials > Service Account > JSON Key erstellen
3. **Kalender freigeben**: In Google Calendar die Service Account Email (`NAME@PROJECT-ID.iam.gserviceaccount.com`) hinzufügen mit "Alle Termindetails anzeigen"
4. **Lokal**: JSON als `service_account.json` im Projekt-Root speichern
5. **GitHub Actions**: Gesamten JSON-Inhalt als Secret `GOOGLE_CALENDAR_CREDENTIALS` anlegen

### Wichtig

- `CALENDAR_ID` in `calendar_fetcher.py` muss die Email-Adresse des freigegebenen Kalenders sein (nicht "primary")
- Service Accounts haben einen eigenen leeren Kalender — sie sehen nur explizit freigegebene Kalender
- `service_account.json` ist in `.gitignore` und darf NIEMALS committed werden
