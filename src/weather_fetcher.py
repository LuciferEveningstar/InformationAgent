import requests


def get_weather_walldorf() -> str:
    """Fetch weather forecast for Walldorf (69190) using wttr.in."""
    try:
        # wttr.in provides free weather data without API key
        # format=3 gives compact output like "Walldorf: ⛅️ +15°C"
        url = "https://wttr.in/Walldorf,Germany?format=%l:+%c+%t+(gefühlt:+%f),+%w,+%h"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        weather_info = response.text.strip()
        return weather_info
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return "Wetter: Keine Daten verfügbar"


def get_pollen_forecast() -> str:
    """Fetch pollen forecast for Walldorf (Baden-Württemberg, Region 111) from DWD."""
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
            return "Pollenflug: Keine Daten verfügbar"

        pollen_data = region_data.get("Pollen", {})

        # Mapping von Belastungsstufen
        level_map = {
            "0": "keine",
            "0-1": "keine-gering",
            "1": "gering",
            "1-2": "gering-mittel",
            "2": "mittel",
            "2-3": "mittel-hoch",
            "3": "hoch"
        }

        # Sammle nur relevante Pollen (Belastung > 0)
        active_pollen = []
        for pollen_type, values in pollen_data.items():
            today_level = values.get("today", "0")
            if today_level != "0":
                level_text = level_map.get(today_level, today_level)
                active_pollen.append(f"{pollen_type}: {level_text}")

        if active_pollen:
            return "🌼 Pollenflug heute: " + ", ".join(active_pollen)
        else:
            return "🌼 Pollenflug: Keine Belastung"

    except Exception as e:
        print(f"Error fetching pollen data: {e}")
        return "Pollenflug: Keine Daten verfügbar"

