import requests
from datetime import date, timedelta
from langchain_core.tools import tool

@tool       # tool to get weather data on city
def weather_tool(city: str) -> dict:
    """Get current weather and tomorrow's forecast for a city."""
    return get_weather(city)


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Light snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}

def get_coordinates(city: str) -> dict:
    """Find a city's latitude, longitude, and timezone."""
    response = requests.get(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en"},
        timeout=10,
    )
    response.raise_for_status()

    results = response.json().get("results", [])
    if not results:
        raise ValueError(f"City not found: {city}")

    place = results[0]
    return {
        "name": place["name"],
        "country": place.get("country", "Unknown"),
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "timezone": place.get("timezone", "auto"),
    }

def get_weather(city: str) -> dict:
    """Get current weather and tomorrow's forecast."""
    place = get_coordinates(city)

    params = {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "timezone": place["timezone"],
        "forecast_days": 2,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,precipitation,"
            "weather_code,wind_speed_10m,wind_direction_10m"
        ),
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,precipitation_sum,"
            "wind_speed_10m_max,sunrise,sunset"
        ),
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
    }

    response = requests.get(
        WEATHER_URL, params=params, timeout=15
    )
    response.raise_for_status()
    data = response.json()

    current = data["current"]
    daily = data["daily"]

    today = date.today()
    # Use the API's local forecast date to handle timezones correctly.
    tomorrow_index = daily["time"].index(
        (today + timedelta(days=1)).isoformat()
    )

    code = current["weather_code"]
    tomorrow_code = daily["weather_code"][tomorrow_index]

    return {
        "location": f'{place["name"]}, {place["country"]}',
        "current": {
            "time": current["time"],
            "temperature_c": current["temperature_2m"],
            "feels_like_c": current["apparent_temperature"],
            "humidity_percent": current["relative_humidity_2m"],
            "condition": WEATHER_CODES.get(code, f"Weather code {code}"),
            "wind_speed_kmh": current["wind_speed_10m"],
            "wind_direction_degrees": current["wind_direction_10m"],
            "precipitation_mm": current["precipitation"],
        },
        "tomorrow": {
            "date": daily["time"][tomorrow_index],
            "condition": WEATHER_CODES.get(
                tomorrow_code, f"Weather code {tomorrow_code}"
            ),
            "min_temp_c": daily["temperature_2m_min"][tomorrow_index],
            "max_temp_c": daily["temperature_2m_max"][tomorrow_index],
            "rain_chance_percent": daily[
                "precipitation_probability_max"
            ][tomorrow_index],
            "rainfall_mm": daily["precipitation_sum"][tomorrow_index],
            "max_wind_kmh": daily["wind_speed_10m_max"][tomorrow_index],
            "sunrise": daily["sunrise"][tomorrow_index],
            "sunset": daily["sunset"][tomorrow_index],
        },
    }

"""testing weather 
>>>py weather.py
"""
def main():
    city = input("Enter city name: ").strip()
    if not city:
        print("Please enter a city name.")
        return

    try:
        weather = get_weather(city)
        current = weather["current"]
        tomorrow = weather["tomorrow"]

        print(f"\nWeather for {weather['location']}")
        print("\n--- CURRENT CONDITIONS ---")
        print(f"Time: {current['time']}")
        print(f"Condition: {current['condition']}")
        print(f"Temperature: {current['temperature_c']} °C")
        print(f"Feels like: {current['feels_like_c']} °C")
        print(f"Humidity: {current['humidity_percent']}%")
        print(f"Wind: {current['wind_speed_kmh']} km/h")
        print(f"Wind direction: {current['wind_direction_degrees']}°")
        print(f"Precipitation: {current['precipitation_mm']} mm")

        print(f"\n--- TOMORROW: {tomorrow['date']} ---")
        print(f"Condition: {tomorrow['condition']}")
        print(
            f"Temperature: {tomorrow['min_temp_c']}–"
            f"{tomorrow['max_temp_c']} °C"
        )
        print(f"Rain probability: {tomorrow['rain_chance_percent']}%")
        print(f"Expected rainfall: {tomorrow['rainfall_mm']} mm")
        print(f"Maximum wind: {tomorrow['max_wind_kmh']} km/h")
        print(f"Sunrise: {tomorrow['sunrise']}")
        print(f"Sunset: {tomorrow['sunset']}")

    except (requests.RequestException, ValueError, KeyError) as error:
        print(f"Could not retrieve weather: {error}")

# starting point
if __name__ == "__main__":
    main()
