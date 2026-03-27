#!/usr/bin/env python3
"""Daily News Agent - Sends curated morning news via Telegram."""

import sys
import argparse
from datetime import datetime

from news_fetcher import fetch_all_news
from summarizer import summarize_all_categories, curate_digest
from telegram_sender import send_telegram_message


def main(weekly: bool = False):
    mode = "Weekly" if weekly else "Daily"
    print(f"=== {mode} News Agent - {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")

    # Step 1: Fetch news from RSS feeds
    hours = 168 if weekly else 24  # 7 days or 1 day
    print(f"1. Fetching news from RSS feeds (last {hours}h)...")
    try:
        categorized_news = fetch_all_news(hours=hours)
        total_articles = sum(len(articles) for articles in categorized_news.values())
        print(f"   Found {total_articles} articles across {len(categorized_news)} categories\n")
    except Exception as e:
        print(f"   ERROR fetching news: {e}")
        send_telegram_message(f"News Agent Fehler: Konnte Feeds nicht abrufen.\n{e}")
        sys.exit(1)

    if total_articles == 0:
        print("   No articles found. Exiting.")
        msg = "Diese Woche keine neuen Artikel gefunden." if weekly else "Heute keine neuen Artikel in den RSS-Feeds gefunden."
        send_telegram_message(msg)
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

    # Step 3: Curate final digest
    digest_type = "Wochenrückblick" if weekly else "Morgen-Digest"
    print(f"3. Curating {digest_type}...")
    try:
        digest = curate_digest(summaries, weekly=weekly)
        print("   Digest created\n")
    except Exception as e:
        print(f"   ERROR curating: {e}")
        header = "*Wochenrückblick*" if weekly else "*Dein Morgen-Briefing*"
        digest = f"{header}\n\n{summaries}"

    # Step 4: Send via Telegram
    print("4. Sending via Telegram...")
    success = send_telegram_message(digest)

    if success:
        print("\n=== Done! Message sent successfully ===")
    else:
        print("\n=== Warning: Message may not have been sent ===")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily News Agent")
    parser.add_argument("--weekly", action="store_true", help="Generate weekly digest instead of daily")
    args = parser.parse_args()
    main(weekly=args.weekly)
