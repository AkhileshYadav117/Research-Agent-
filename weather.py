import requests

def get_weather(place: str) -> str:
    """
    Fetches real current weather data for a place using Open-Meteo's
    free geocoding + forecast API (no key required).
    Returns a plain-text summary, or empty string if it fails.
    """
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": place, "count": 1},
            timeout=8,
        ).json()

        if not geo.get("results"):
            return ""

        loc = geo["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        resolved_name = f"{loc['name']}, {loc.get('admin1', '')}, {loc.get('country', '')}"

        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            },
            timeout=8,
        ).json()

        current = weather.get("current", {})
        if not current:
            return ""

        return (
            f"Live weather data for {resolved_name}: "
            f"Temperature: {current.get('temperature_2m')}°C, "
            f"Humidity: {current.get('relative_humidity_2m')}%, "
            f"Wind speed: {current.get('wind_speed_10m')} km/h."
        )
    except Exception:
        return ""