import requests


def get_weather_walldorf() -> str:
    """Fetch daily weather forecast for Walldorf using wttr.in JSON API."""
    try:
        # JSON format gives structured data with daily min/max temps
        url = "https://wttr.in/Walldorf,Germany?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        today = data["weather"][0]
        current = data["current_condition"][0]

        max_temp = today["maxtempC"]
        min_temp = today["mintempC"]
        condition = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        wind_kmph = current["windspeedKmph"]

        # Wetter-Emoji basierend auf Condition
        condition_lower = condition.lower()
        if "sun" in condition_lower or "clear" in condition_lower:
            emoji = "☀️"
        elif "cloud" in condition_lower or "overcast" in condition_lower:
            emoji = "☁️"
        elif "rain" in condition_lower or "drizzle" in condition_lower:
            emoji = "🌧️"
        elif "snow" in condition_lower:
            emoji = "❄️"
        elif "thunder" in condition_lower:
            emoji = "⛈️"
        elif "fog" in condition_lower or "mist" in condition_lower:
            emoji = "🌫️"
        else:
            emoji = "🌤️"

        return f"Walldorf: {emoji} bis {max_temp}°C (min {min_temp}°C), {wind_kmph}km/h, {humidity}%"
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return "Wetter: Keine Daten verfügbar"


def get_pollen_forecast() -> str:
    """Fetch pollen forecast for Walldorf (Baden-Württemberg, Region 111) from DWD.

    Returns a simple 0-10 score instead of detailed list.
    """
    try:
        # DWD OpenData - kostenlose Pollenflug-Daten
        url = "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Walldorf (69190) liegt in Region 111: "Oberrhein und unteres Neckartal"
        region_id = 111
        region_data = None

        for region in data.get("content", []):
            if region.get("partregion_id") == region_id:
                region_data = region
                break

        if not region_data:
            return "🌼 Pollen: ?"

        pollen_data = region_data.get("Pollen", {})

        # Belastungsstufen zu numerischen Werten (0-3 Skala der DWD)
        level_to_num = {
            "0": 0,
            "0-1": 0.5,
            "1": 1,
            "1-2": 1.5,
            "2": 2,
            "2-3": 2.5,
            "3": 3
        }

        # Sammle alle Belastungswerte
        levels = []
        for values in pollen_data.values():
            today_level = values.get("today", "0")
            num_level = level_to_num.get(today_level, 0)
            levels.append(num_level)

        if not levels:
            return "🌼 Pollen: 0/10"

        # Gesamtbelastung: Höchstwert + Durchschnitt kombiniert, auf 0-10 skaliert
        max_level = max(levels)
        avg_level = sum(levels) / len(levels)

        # Formel: 60% Höchstwert + 40% Durchschnitt, dann auf 0-10 skalieren (DWD max ist 3)
        combined = (max_level * 0.6 + avg_level * 0.4)
        score = round(combined * 10 / 3)  # Skaliere von 0-3 auf 0-10
        score = min(10, max(0, score))  # Clamp auf 0-10

        # Emoji basierend auf Belastung
        if score <= 2:
            emoji = "🌼"
        elif score <= 5:
            emoji = "🤧"
        else:
            emoji = "😷"

        return f"{emoji} Pollen: {score}/10"

    except Exception as e:
        print(f"Error fetching pollen data: {e}")
        return "🌼 Pollen: ?"

