#!/usr/bin/env python3
"""Test script for calendar integration."""

from calendar_fetcher import get_calendar_digest
from telegram_sender import send_telegram_message

print("Fetching calendar...")
daily = get_calendar_digest(weekly=False)
print(daily)

print("\nSending to Telegram...")
send_telegram_message(daily)
print("Done!")
