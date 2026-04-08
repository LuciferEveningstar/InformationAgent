import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Telegram Chat IDs - kommagetrennt für mehrere Empfänger
_chat_ids_raw = os.getenv("TELEGRAM_CHAT_IDS", os.getenv("TELEGRAM_CHAT_ID", ""))
TELEGRAM_CHAT_IDS = [cid.strip() for cid in _chat_ids_raw.split(",") if cid.strip()]

# Gemini Models (kostenlose Modelle) - Fallback-Reihenfolge bei Rate Limits
GEMINI_MODELS = [
    "models/gemini-2.5-flash",
    "models/gemini-2.5-flash-lite",
    "models/gemini-3-flash",
    "models/gemini-3.1-flash-lite",
]

# RSS Feeds nach Kategorie
RSS_FEEDS = {
    "KI & Technologie": [
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.technologyreview.com/feed/",
        "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "https://blog.google/technology/ai/rss/",
        "https://openai.com/blog/rss.xml",
        "https://www.anthropic.com/news/rss.xml",
        "https://venturebeat.com/category/ai/feed/",
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
    "Wirtschaft": [
        "https://www.handelsblatt.com/contentexport/feed/top-themen",
        "https://www.manager-magazin.de/wirtschaft/index.rss",
        "https://www.wiwo.de/rss/schlagzeilen.rss",
        "https://www.faz.net/rss/aktuell/wirtschaft/",
    ],
}

# Prompts
SUMMARY_PROMPT = """Fasse die folgenden Nachrichtenartikel kurz und prägnant auf Deutsch zusammen.
Für jeden Artikel: 1-2 Sätze, die das Wichtigste erfassen.
WICHTIG: Behalte den Original-Link für jeden Artikel bei!

Artikel:
{articles}

Format pro Artikel:
**[Titel]**
[Zusammenfassung in 1-2 Sätzen]
[Link](URL)
"""

CURATE_PROMPT = """Du bist ein persönlicher News-Kurator. Erstelle aus den folgenden zusammengefassten News einen
Morgen-Digest mit etwa 5 Minuten Lesezeit.

Regeln:
1. Wähle die wichtigsten und interessantesten Stories aus jeder Kategorie
2. Schreibe auf Deutsch, klar und informativ
3. Strukturiere nach Kategorien mit Emoji-Überschriften
4. WICHTIG: Füge nach jeder Story den Link zum Original-Artikel als Markdown-Link ein: [Link](URL)
5. Füge am Ende einen kurzen "Ausblick" mit 1-2 Sätzen hinzu, was heute wichtig werden könnte
6. Halte es kompakt aber informativ
7. GANZ AM ENDE: Füge ein TL;DR mit max 1 Minute Lesezeit hinzu - nur die absolut wichtigsten 3-4 Punkte über alle Kategorien
8. Verwende **fett** für Kategorieüberschriften (z.B. **🤖 KI & Technologie**)

Zusammengefasste News:
{summaries}

Erstelle den Digest im folgenden Format:

*{timestamp}*

*Guten Morgen! Hier dein News-Briefing:*

**🤖 KI & Technologie**
[News-Titel]: [Zusammenfassung] [Link](URL)

**🏢 SAP**
[News-Titel]: [Zusammenfassung] [Link](URL)

**🇩🇪 Deutsche Politik**
[News-Titel]: [Zusammenfassung] [Link](URL)

**🌍 Internationale Politik**
[News-Titel]: [Zusammenfassung] [Link](URL)

**💼 Wirtschaft**
[News-Titel]: [Zusammenfassung] [Link](URL)

**🔮 Ausblick**
[Was heute wichtig wird]

**📌 TL;DR (1 Min)**
[Die 3-4 wichtigsten Punkte des Tages in Stichpunkten]
"""

WEEKLY_PROMPT = """Du bist ein persönlicher News-Kurator. Erstelle einen Wochenrückblick aus den folgenden News der letzten 7 Tage.

Regeln:
1. Fasse die wichtigsten Entwicklungen der Woche zusammen
2. Schreibe auf Deutsch, klar und informativ
3. Strukturiere nach Kategorien mit Emoji-Überschriften
4. WICHTIG: Füge Links zu den wichtigsten Artikeln als Markdown-Links ein: [Link](URL)
5. Identifiziere Trends und wiederkehrende Themen
6. Etwa 7-10 Minuten Lesezeit
7. GANZ AM ENDE: Füge ein TL;DR mit max 1 Minute Lesezeit hinzu - nur die absolut wichtigsten 4-5 Punkte der Woche
8. Verwende **fett** für Kategorieüberschriften (z.B. **🤖 KI & Technologie**)

News der Woche:
{summaries}

Erstelle den Wochenrückblick im folgenden Format:

*{timestamp}*

*Wochenrückblick*

**🤖 KI & Technologie**
[Die wichtigsten Entwicklungen der Woche] [Link](URL)

**🏢 SAP**
[Die wichtigsten Entwicklungen der Woche] [Link](URL)

**🇩🇪 Deutsche Politik**
[Die wichtigsten Entwicklungen der Woche] [Link](URL)

**🌍 Internationale Politik**
[Die wichtigsten Entwicklungen der Woche] [Link](URL)

**💼 Wirtschaft**
[Die wichtigsten Entwicklungen der Woche] [Link](URL)

**📊 Trends der Woche**
[Wiederkehrende Themen und Muster]

**🔮 Ausblick**
[Was nächste Woche wichtig werden könnte]

**📌 TL;DR (1 Min)**
[Die 4-5 wichtigsten Punkte der Woche in Stichpunkten]
"""
