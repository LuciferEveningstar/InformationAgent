import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Gemini Models (kostenlose Modelle)
GEMINI_FLASH_MODEL = "models/gemini-2.5-flash"
GEMINI_PRO_MODEL = "models/gemini-2.5-flash"  # Flash für alles, Pro hat kein Free-Tier Quota

# RSS Feeds nach Kategorie
RSS_FEEDS = {
    "KI & Technologie": [
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.technologyreview.com/feed/",
        "https://feeds.arstechnica.com/arstechnica/technology-lab",
    ],
    "SAP": [
        "https://news.sap.com/feed/",
        "https://blogs.sap.com/feed/",
    ],
    "Deutsche Politik": [
        "https://www.tagesschau.de/index~rss2.xml",
        "https://www.zeit.de/politik/index-rss",
        "https://www.spiegel.de/politik/index.rss",
    ],
    "Internationale Politik": [
        "https://feeds.reuters.com/Reuters/worldNews",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.theguardian.com/world/rss",
    ],
}

# Prompts
SUMMARY_PROMPT = """Fasse die folgenden Nachrichtenartikel kurz und prägnant auf Deutsch zusammen.
Für jeden Artikel: 1-2 Sätze, die das Wichtigste erfassen.
Behalte den Titel und füge die Zusammenfassung hinzu.

Artikel:
{articles}

Format pro Artikel:
**[Titel]**
[Zusammenfassung in 1-2 Sätzen]
"""

CURATE_PROMPT = """Du bist ein persönlicher News-Kurator. Erstelle aus den folgenden zusammengefassten News einen
Morgen-Digest mit etwa 5 Minuten Lesezeit.

Regeln:
1. Wähle die wichtigsten und interessantesten Stories aus jeder Kategorie
2. Schreibe auf Deutsch, klar und informativ
3. Strukturiere nach Kategorien mit Emoji-Überschriften
4. Füge am Ende einen kurzen "Ausblick" mit 1-2 Sätzen hinzu, was heute wichtig werden könnte
5. Halte es kompakt aber informativ

Zusammengefasste News:
{summaries}

Erstelle den Digest im folgenden Format:

*Guten Morgen! Hier dein News-Briefing:*

*KI & Technologie*
[News]

*SAP*
[News]

*Deutsche Politik*
[News]

*Internationale Politik*
[News]

*Ausblick*
[Was heute wichtig wird]
"""
