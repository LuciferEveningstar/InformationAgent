#!/usr/bin/env python3
"""Fetch market data (DAX, S&P 500, EUR/USD) for morning briefing."""

import yfinance as yf


# Symbole für Yahoo Finance
MARKETS = {
    "DAX": "^GDAXI",
    "S&P 500": "^GSPC",
    "EUR/USD": "EURUSD=X",
}


def get_market_data() -> str:
    """
    Fetch current market data with daily change.

    Returns formatted string with colored indicators:
    🟢 for positive, 🔴 for negative change.
    """
    results = []

    for name, symbol in MARKETS.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info

            price = info.last_price
            prev_close = info.previous_close

            if price and prev_close:
                change = price - prev_close
                change_pct = (change / prev_close) * 100

                # Farbe basierend auf Änderung
                if change >= 0:
                    color = "🟢"
                    sign = "+"
                else:
                    color = "🔴"
                    sign = ""

                # Formatierung je nach Asset
                if name == "EUR/USD":
                    # Währung: 4 Dezimalstellen
                    results.append(f"{name} {price:.4f} {color} {sign}{change_pct:.2f}%")
                else:
                    # Indizes: Punkte ohne Dezimalstellen
                    results.append(f"{name} {price:,.0f} {color} {sign}{change_pct:.2f}%")
            else:
                results.append(f"{name} --")

        except Exception as e:
            print(f"Error fetching {name}: {e}")
            results.append(f"{name} --")

    return "📈 " + " · ".join(results)


if __name__ == "__main__":
    print(get_market_data())
