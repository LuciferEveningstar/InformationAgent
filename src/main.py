#!/usr/bin/env python3
"""Daily News Agent - Sends curated morning news via Telegram."""

import sys
from datetime import datetime

from news_fetcher import fetch_all_news
from summarizer import summarize_all_categories, curate_digest
from telegram_sender import send_telegram_message


def main():
    print(f"=== Daily News Agent - {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")

    # Step 1: Fetch news from RSS feeds
    print("1. Fetching news from RSS feeds...")
    try:
        categorized_news = fetch_all_news()
        total_articles = sum(len(articles) for articles in categorized_news.values())
        print(f"   Found {total_articles} articles across {len(categorized_news)} categories\n")
    except Exception as e:
        print(f"   ERROR fetching news: {e}")
        send_telegram_message(f"News Agent Fehler: Konnte Feeds nicht abrufen.\n{e}")
        sys.exit(1)

    if total_articles == 0:
        print("   No articles found. Exiting.")
        send_telegram_message("Heute keine neuen Artikel in den RSS-Feeds gefunden.")
        return

    # Step 2: Summarize each category with Gemini Flash
    print("2. Summarizing articles with Gemini Flash...")
    try:
        summaries = summarize_all_categories(categorized_news)
        print("   Summaries generated\n")
    except Exception as e:
        print(f"   ERROR summarizing: {e}")
        send_telegram_message(f"News Agent Fehler: Zusammenfassung fehlgeschlagen.\n{e}")
        sys.exit(1)

    # Step 3: Curate final digest with Gemini Pro
    print("3. Curating digest with Gemini Pro...")
    try:
        digest = curate_digest(summaries)
        print("   Digest created\n")
    except Exception as e:
        print(f"   ERROR curating: {e}")
        # Fallback: send raw summaries
        digest = f"*Dein Morgen-Briefing*\n\n{summaries}"

    # Step 4: Send via Telegram
    print("4. Sending via Telegram...")
    success = send_telegram_message(digest)

    if success:
        print("\n=== Done! Message sent successfully ===")
    else:
        print("\n=== Warning: Message may not have been sent ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
