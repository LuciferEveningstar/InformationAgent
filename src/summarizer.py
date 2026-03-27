import time
from datetime import datetime
from google import genai
from google.genai import types
from typing import Dict, List
from config import (
    GOOGLE_API_KEY,
    GEMINI_MODELS,
    SUMMARY_PROMPT,
    CURATE_PROMPT,
    WEEKLY_PROMPT,
)
from news_fetcher import format_articles_for_summary

client = genai.Client(api_key=GOOGLE_API_KEY)

# Track which model to use (persists across calls within same run)
_current_model_index = 0


def _get_current_model() -> str:
    """Get the current model to use."""
    return GEMINI_MODELS[_current_model_index]


def _switch_to_next_model() -> bool:
    """Switch to next fallback model. Returns False if no more models available."""
    global _current_model_index
    if _current_model_index < len(GEMINI_MODELS) - 1:
        _current_model_index += 1
        print(f"  Switching to fallback model: {GEMINI_MODELS[_current_model_index]}")
        return True
    return False


def _get_timestamp(weekly: bool = False) -> str:
    """Generate timestamp string for the digest."""
    now = datetime.now()
    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    weekday = weekdays[now.weekday()]
    date_str = now.strftime("%d.%m.%Y")

    if weekly:
        return f"Wochenrückblick - {weekday}, {date_str}"
    return f"{weekday}, {date_str} - {now.strftime('%H:%M')} Uhr"


def _generate_with_retry(prompt: str, max_retries: int = 3) -> str:
    """Generate content with retry logic and model fallback for rate limits."""
    global _current_model_index

    while True:
        model = _get_current_model()

        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                if response.text:
                    return response.text
                raise ValueError("Empty response from API")
            except Exception as e:
                error_str = str(e)
                is_rate_limit = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str

                if is_rate_limit:
                    if attempt < max_retries - 1:
                        wait_time = 10 * (attempt + 1)
                        print(f"  Rate limited on {model}, waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        # All retries exhausted, try next model
                        if _switch_to_next_model():
                            break  # Break inner loop, continue outer while
                        else:
                            raise Exception(f"All models exhausted. Last error: {e}")
                else:
                    raise e
        else:
            # Inner for-loop completed without break = success or non-rate-limit error
            # This shouldn't be reached due to return/raise above, but just in case
            continue
        # Break from inner loop means we switched models, continue trying
        continue

    return ""


def summarize_category(category: str, articles: List[dict]) -> str:
    """Summarize articles in a category using Gemini Flash."""
    if not articles:
        return f"**{category}**\nKeine aktuellen Nachrichten in dieser Kategorie.\n"

    articles_text = format_articles_for_summary(articles)
    prompt = SUMMARY_PROMPT.format(articles=articles_text)

    try:
        response = _generate_with_retry(prompt)
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
        time.sleep(5)  # Longer rate limit buffer
    return "\n".join(summaries)


def curate_digest(summaries: str, weekly: bool = False) -> str:
    """Create the final curated digest using Gemini Pro."""
    prompt_template = WEEKLY_PROMPT if weekly else CURATE_PROMPT
    timestamp = _get_timestamp(weekly)
    prompt = prompt_template.format(summaries=summaries, timestamp=timestamp)

    try:
        response = _generate_with_retry(prompt)
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
