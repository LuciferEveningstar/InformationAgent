import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(text: str, parse_mode: str = "Markdown") -> bool:
    """Send a message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    # Telegram has a 4096 character limit per message
    max_length = 4096

    if len(text) <= max_length:
        return _send_single_message(url, text, parse_mode)

    # Split into multiple messages if too long
    chunks = _split_message(text, max_length)
    success = True
    for i, chunk in enumerate(chunks):
        if i > 0:
            chunk = f"... (Fortsetzung)\n\n{chunk}"
        if not _send_single_message(url, chunk, parse_mode):
            success = False
    return success


def _send_single_message(url: str, text: str, parse_mode: str) -> bool:
    """Send a single message."""
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            print("Message sent successfully!")
            return True
        else:
            print(f"Telegram API error: {response.status_code}")
            print(response.text)
            # Retry without markdown if parsing failed
            if "parse" in response.text.lower() and parse_mode:
                print("Retrying without markdown...")
                payload["parse_mode"] = None
                retry = requests.post(url, json=payload, timeout=30)
                return retry.status_code == 200
            return False
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def _split_message(text: str, max_length: int) -> list:
    """Split a long message into chunks."""
    chunks = []
    current_chunk = ""

    for line in text.split("\n"):
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + "\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


if __name__ == "__main__":
    test_message = "*Test Nachricht*\n\nDies ist ein Test des Telegram Bots."
    send_telegram_message(test_message)
