import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS


def send_telegram_message(text: str, parse_mode: str = "Markdown") -> bool:
    """Send a message to all configured Telegram users."""
    if not TELEGRAM_BOT_TOKEN:
        print("  ERROR: TELEGRAM_BOT_TOKEN not configured!")
        return False

    if not TELEGRAM_CHAT_IDS:
        print("  ERROR: No TELEGRAM_CHAT_ID(S) configured!")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    max_length = 4096

    all_success = True
    for chat_id in TELEGRAM_CHAT_IDS:
        print(f"Sending to {chat_id}...")
        if len(text) <= max_length:
            success = _send_single_message(url, text, parse_mode, chat_id)
        else:
            chunks = _split_message(text, max_length)
            success = True
            for i, chunk in enumerate(chunks):
                if i > 0:
                    chunk = f"... (Fortsetzung)\n\n{chunk}"
                if not _send_single_message(url, chunk, parse_mode, chat_id):
                    success = False
        if not success:
            all_success = False

    return all_success


def _send_single_message(url: str, text: str, parse_mode: str, chat_id: str) -> bool:
    """Send a single message to a specific chat."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            print(f"  Message sent to {chat_id}!")
            return True
        else:
            print(f"  Telegram API error for {chat_id}: {response.status_code}")
            print(f"  Response: {response.text[:200]}")

            # Retry without markdown for any 400 error (often markdown parsing issues)
            if response.status_code == 400 and parse_mode:
                print("  Retrying without markdown...")
                del payload["parse_mode"]
                retry = requests.post(url, json=payload, timeout=30)
                if retry.status_code == 200:
                    print(f"  Message sent to {chat_id} (plain text)!")
                    return True
                else:
                    print(f"  Retry also failed: {retry.status_code} - {retry.text[:200]}")
            return False
    except Exception as e:
        print(f"  Error sending to {chat_id}: {e}")
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
