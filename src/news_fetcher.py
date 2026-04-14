import feedparser
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
from config import RSS_FEEDS


def fetch_single_feed(url: str, hours: int = 24) -> List[dict]:
    """Fetch articles from a single RSS feed."""
    try:
        feed = feedparser.parse(url)
        articles = []
        cutoff = datetime.now() - timedelta(hours=hours)

        for entry in feed.entries[:10]:  # Max 10 per feed
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])

            # Skip old articles if we can determine the date
            if published and published < cutoff:
                continue

            articles.append({
                "title": entry.get("title", "Ohne Titel"),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", entry.get("description", "")),
                "published": published,
            })

        return articles
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []


def fetch_all_news(hours: int = 24) -> Dict[str, List[dict]]:
    """Fetch news from all RSS feeds, organized by category."""
    categorized_news = {}

    for category, urls in RSS_FEEDS.items():
        category_articles = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(fetch_single_feed, url, hours): url for url in urls}

            for future in as_completed(future_to_url):
                articles = future.result()
                category_articles.extend(articles)

        # Sort by date (newest first) and deduplicate by title
        seen_titles = set()
        unique_articles = []
        for article in sorted(category_articles, key=lambda x: x["published"] or datetime.min, reverse=True):
            title_lower = article["title"].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)

        # More articles for weekly digest and for KI & Technologie category
        if category == "KI & Technologie":
            max_articles = 14 if hours > 24 else 8  # Reduziert von 20/12
        else:
            max_articles = 10 if hours > 24 else 5
        categorized_news[category] = unique_articles[:max_articles]

    return categorized_news


def format_articles_for_summary(articles: List[dict]) -> str:
    """Format articles for the LLM summary prompt."""
    formatted = []
    for i, article in enumerate(articles, 1):
        text = f"{i}. {article['title']}\n"
        if article["summary"]:
            # Clean HTML tags from summary
            summary = article["summary"]
            import re
            summary = re.sub(r"<[^>]+>", "", summary)
            summary = summary[:500]  # Limit length
            text += f"   {summary}\n"
        if article["link"]:
            text += f"   Link: {article['link']}\n"
        formatted.append(text)
    return "\n".join(formatted)


if __name__ == "__main__":
    print("Fetching news...")
    news = fetch_all_news()
    for category, articles in news.items():
        print(f"\n=== {category} ({len(articles)} articles) ===")
        for article in articles:
            print(f"  - {article['title']}")
