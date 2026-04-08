#!/usr/bin/env python3
"""Google Calendar integration for daily agenda."""

import json
import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

# Nur Lesezugriff auf Kalender
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Kalender-ID des Benutzers (Email-Adresse des freigegebenen Kalenders)
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "lucifereveningstaryoutub@gmail.com")


def get_calendar_service():
    """Authentifiziert mit Service Account und gibt den Calendar Service zurück."""
    creds = None

    # Option 1: Credentials aus Environment Variable (für GitHub Actions)
    creds_json = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
    if creds_json:
        try:
            creds_data = json.loads(creds_json)
            creds = service_account.Credentials.from_service_account_info(
                creds_data, scopes=SCOPES
            )
        except Exception as e:
            print(f"Error parsing GOOGLE_CALENDAR_CREDENTIALS: {e}")
            return None
    else:
        # Option 2: Credentials aus Datei (für lokale Entwicklung)
        creds_path = os.path.join(os.path.dirname(__file__), "..", "service_account.json")
        if os.path.exists(creds_path):
            creds = service_account.Credentials.from_service_account_file(
                creds_path, scopes=SCOPES
            )
        else:
            print("ERROR: Keine Calendar Credentials gefunden!")
            print("Setze GOOGLE_CALENDAR_CREDENTIALS als Environment Variable")
            print(f"oder speichere die Service Account JSON als {creds_path}")
            return None

    return build("calendar", "v3", credentials=creds)


def get_todays_events() -> list[dict]:
    """Holt alle Events für heute."""
    service = get_calendar_service()
    if not service:
        return []

    # Zeitbereich: Heute 00:00 bis 23:59
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_of_day.isoformat() + "Z",
            timeMax=end_of_day.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        return events_result.get("items", [])
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return []


def get_weeks_events() -> list[dict]:
    """Holt alle Events für die kommende Woche."""
    service = get_calendar_service()
    if not service:
        return []

    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_day + timedelta(days=7)

    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_of_day.isoformat() + "Z",
            timeMax=end_of_week.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        return events_result.get("items", [])
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return []


def format_event_time(event: dict) -> str:
    """Formatiert die Event-Zeit für Anzeige."""
    start = event.get("start", {})

    # Ganztägige Events haben "date" statt "dateTime"
    if "date" in start:
        return "Ganztägig"

    if "dateTime" in start:
        dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
        return dt.strftime("%H:%M")

    return ""


def format_event_for_digest(event: dict) -> str:
    """Formatiert ein einzelnes Event für den Digest."""
    time = format_event_time(event)
    summary = event.get("summary", "Ohne Titel")
    location = event.get("location", "")

    result = f"• {time}: {summary}"
    if location:
        result += f" ({location})"

    return result


def get_calendar_digest(weekly: bool = False) -> Optional[str]:
    """
    Erstellt einen formatierten Kalender-Digest.

    Args:
        weekly: True für Wochenübersicht, False für Tagesübersicht

    Returns:
        Formatierter String mit Terminen oder None wenn keine Termine/Fehler
    """
    events = get_weeks_events() if weekly else get_todays_events()

    if not events:
        if weekly:
            return "📅 Keine Termine in den nächsten 7 Tagen"
        return "📅 Keine Termine heute"

    if weekly:
        # Gruppiere nach Tagen
        days: dict[str, list[str]] = {}
        for event in events:
            start = event.get("start", {})
            date_str = start.get("date") or start.get("dateTime", "")[:10]

            try:
                event_date = datetime.fromisoformat(date_str)
                day_name = event_date.strftime("%A, %d.%m.")  # z.B. "Montag, 08.04."
            except:
                day_name = date_str

            if day_name not in days:
                days[day_name] = []
            days[day_name].append(format_event_for_digest(event))

        lines = ["📅 Termine diese Woche:"]
        for day, day_events in days.items():
            lines.append(f"\n<b>{day}</b>")
            lines.extend(day_events)

        return "\n".join(lines)
    else:
        lines = [f"📅 Heute {len(events)} Termin(e):"]
        for event in events:
            lines.append(format_event_for_digest(event))

        return "\n".join(lines)


if __name__ == "__main__":
    # Test: Zeige heutige Termine
    print("=== Calendar Fetcher Test ===\n")

    print("Tagesübersicht:")
    print(get_calendar_digest(weekly=False))

    print("\n" + "="*40 + "\n")

    print("Wochenübersicht:")
    print(get_calendar_digest(weekly=True))
