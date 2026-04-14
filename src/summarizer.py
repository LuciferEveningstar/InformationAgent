import time
import requests
from datetime import datetime
from typing import Dict, List
from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    SUMMARY_PROMPT,
    CURATE_PROMPT,
    WEEKLY_PROMPT,
    CALENDAR_ENABLED,
)
from news_fetcher import format_articles_for_summary

# OpenRouter API Endpoint
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _get_timestamp(weekly: bool = False) -> str:
    """Generate timestamp string for the digest."""
    now = datetime.now()
    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    weekday = weekdays[now.weekday()]
    date_str = now.strftime("%d.%m.%Y")

    if weekly:
        return f"Wochenrückblick - {weekday}, {date_str}"
    return f"{weekday}, {date_str} - {now.strftime('%H:%M')} Uhr"


def _get_weather() -> str:
    """Get weather forecast for Walldorf."""
    try:
        from weather_fetcher import get_weather_walldorf, get_pollen_forecast
        weather = get_weather_walldorf()
        pollen = get_pollen_forecast()
        return f"{weather}\n{pollen}"
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return "Wetter: Keine Daten verfügbar"


def _get_calendar(weekly: bool = False) -> str:
    """Get calendar events for today or the week."""
    if not CALENDAR_ENABLED:
        print("  Calendar disabled (no credentials found)")
        return ""
    try:
        from calendar_fetcher import get_calendar_digest
        result = get_calendar_digest(weekly=weekly)
        print(f"  Calendar result: {result[:50] if result else 'empty'}...")
        return result
    except Exception as e:
        print(f"Error fetching calendar: {e}")
        return ""


def _generate_with_openrouter(prompt: str, max_retries: int = 3) -> str:
    """Generate content using OpenRouter API with retry logic."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY nicht konfiguriert!")

    for attempt in range(max_retries):
        try:
            response = requests.post(
                url=OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://github.com/InformationAgent",
                    "X-OpenRouter-Title": "InformationAgent News Bot",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 8000,  # Reasoning-Modelle brauchen mehr Tokens
                },
                timeout=120,
            )

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]

                if content:
                    # Log token usage
                    usage = data.get("usage", {})
                    print(f"  [{OPENROUTER_MODEL}] Tokens: {usage.get('total_tokens', 'N/A')}")
                    return content
                else:
                    raise ValueError("Leere Antwort von API")

            elif response.status_code == 429:
                # Rate limit - warten und retry
                wait_time = 10 * (attempt + 1)
                print(f"  Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            else:
                error_msg = response.text[:200]
                raise Exception(f"API Error {response.status_code}: {error_msg}")

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"  Timeout, retry {attempt + 2}/{max_retries}...")
                continue
            raise Exception("Request Timeout nach allen Versuchen")

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Error: {e}, retry {attempt + 2}/{max_retries}...")
                time.sleep(5)
                continue
            raise

    raise Exception("Alle Versuche fehlgeschlagen")


def summarize_category(category: str, articles: List[dict]) -> str:
    """Summarize articles in a category using OpenRouter."""
    if not articles:
        return f"**{category}**\nKeine aktuellen Nachrichten in dieser Kategorie.\n"

    articles_text = format_articles_for_summary(articles)
    prompt = SUMMARY_PROMPT.format(articles=articles_text)

    try:
        response = _generate_with_openrouter(prompt)
        return f"**{category}**\n{response}\n"
    except Exception as e:
        print(f"Error summarizing {category}: {e}")
        titles = "\n".join([f"- {a['title']}" for a in articles])
        return f"**{category}**\n{titles}\n"


def summarize_all_categories(categorized_news: Dict[str, List[dict]]) -> str:
    """Summarize all categories."""
    summaries = []
    for category, articles in categorized_news.items():
        print(f"Summarizing {category}...")
        summary = summarize_category(category, articles)
        summaries.append(summary)
        time.sleep(2)  # Rate limit buffer
    return "\n".join(summaries)


def curate_digest(summaries: str, weekly: bool = False) -> str:
    """Create the final curated digest using OpenRouter."""
    prompt_template = WEEKLY_PROMPT if weekly else CURATE_PROMPT
    timestamp = _get_timestamp(weekly)

    # Add weather forecast for daily digest
    if not weekly:
        weather = _get_weather()
        timestamp = f"{timestamp}\n{weather}"

    # Add calendar events
    calendar = _get_calendar(weekly=weekly)
    if calendar:
        timestamp = f"{timestamp}\n\n{calendar}"

    prompt = prompt_template.format(summaries=summaries, timestamp=timestamp)

    try:
        response = _generate_with_openrouter(prompt)
        return response
    except Exception as e:
        print(f"Error curating digest: {e}")
        header = f"*{timestamp}*\n\n*Wochenrückblick*" if weekly else f"*{timestamp}*\n\n*Dein Morgen-Briefing*"
        return f"{header}\n\n{summaries}"


if __name__ == "__main__":
    from news_fetcher import fetch_all_news

    print("Fetching news...")
    news = fetch_all_news()

    print("\nSummarizing...")
    summaries = summarize_all_categories(news)
    print(summaries)

    print("\nCurating digest...")
    digest = curate_digest(summaries)
    print(digest)
