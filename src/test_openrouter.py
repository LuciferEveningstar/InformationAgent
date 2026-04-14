#!/usr/bin/env python3
"""Test script for OpenRouter API connection."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API Key aus .env laden
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Verfügbare Modelle zum Testen
MODELS = {
    "m1": "minimax/minimax-m1",
    "m2.7": "minimax/minimax-m2.7",
    "kimi": "moonshotai/kimi-k2.5",
}


def test_openrouter(model_key: str = "m2.7", prompt: str = "Sag 'Hallo' auf Deutsch und erkläre in einem Satz, wer du bist."):
    """
    Testet die OpenRouter API mit einem einfachen Prompt.

    Args:
        model_key: Kurzname des Modells (m1, m2.7, kimi)
        prompt: Test-Prompt
    """
    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY nicht in .env gefunden!")
        print("Bitte füge OPENROUTER_API_KEY=sk-or-... zu deiner .env Datei hinzu.")
        return None

    model = MODELS.get(model_key, model_key)
    print(f"=== OpenRouter API Test ===")
    print(f"Modell: {model}")
    print(f"Prompt: {prompt}\n")

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://github.com/InformationAgent",
                "X-OpenRouter-Title": "InformationAgent News Bot",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,  # Reasoning-Modelle brauchen mehr Tokens
            },
            timeout=60,
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Antwort extrahieren
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            print(f"\n--- Antwort ---")
            print(content)
            print(f"\n--- Token Usage ---")
            print(f"  Input:  {usage.get('prompt_tokens', 'N/A')}")
            print(f"  Output: {usage.get('completion_tokens', 'N/A')}")
            print(f"  Total:  {usage.get('total_tokens', 'N/A')}")

            # Kosten berechnen (ungefähr)
            model_pricing = {
                "minimax/minimax-m1": (0.40, 2.20),
                "minimax/minimax-m2.7": (0.30, 1.20),
                "moonshotai/kimi-k2.5": (0.38, 1.72),
            }
            if model in model_pricing:
                input_price, output_price = model_pricing[model]
                input_tokens = usage.get('prompt_tokens', 0)
                output_tokens = usage.get('completion_tokens', 0)
                cost = (input_tokens * input_price + output_tokens * output_price) / 1_000_000
                print(f"  Kosten: ~${cost:.6f}")

            return content
        else:
            print(f"\nERROR: {response.status_code}")
            print(response.text)
            return None

    except requests.exceptions.Timeout:
        print("ERROR: Request Timeout (>60s)")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


if __name__ == "__main__":
    import sys

    # Optionales Argument: Modell-Key
    model = sys.argv[1] if len(sys.argv) > 1 else "m2.7"

    if model == "all":
        # Teste alle Modelle
        for key in MODELS:
            print("\n" + "="*50 + "\n")
            test_openrouter(key)
    else:
        test_openrouter(model)
