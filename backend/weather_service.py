
import asyncio
from time import time

import httpx
from fastapi import HTTPException


# =====================================
# SIMPLE WEATHER CACHE
# =====================================

weather_cache = {}

CACHE_DURATION = 600  # 10 minutes


# =====================================
# GET CITY COORDINATES
# =====================================

async def get_coordinates(city: str):

    url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={city}"
        "&count=1"
        "&language=en"
        "&format=json"
    )

    async with httpx.AsyncClient() as client:

        try:

            response = await client.get(
                url,
                timeout=30
            )

            response.raise_for_status()

        except httpx.HTTPStatusError as e:

            raise HTTPException(
                status_code=502,
                detail=(
                    f"Geocoding service returned "
                    f"status {e.response.status_code}."
                )
            )

        except httpx.RequestError:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Could not connect to "
                    "the geocoding service."
                )
            )

    try:
        data = response.json()

    except Exception:

        raise HTTPException(
            status_code=502,
            detail="Geocoding service returned invalid JSON."
        )

    if "results" not in data or not data["results"]:

        raise HTTPException(
            status_code=404,
            detail="City not found."
        )

    location = data["results"][0]

    return {
        "city": location["name"],
        "latitude": location["latitude"],
        "longitude": location["longitude"]
    }


# =====================================
# GET WEATHER DATA
# =====================================

async def get_weather_data(
    latitude: float,
    longitude: float
):

    # =================================
    # CACHE KEY
    # =================================

    cache_key = (
        round(latitude, 4),
        round(longitude, 4)
    )

    # =================================
    # CHECK CACHE
    # =================================

    if cache_key in weather_cache:

        cached_data, timestamp = weather_cache[cache_key]

        if time() - timestamp < CACHE_DURATION:

            return cached_data

        else:

            del weather_cache[cache_key]

    # =================================
    # OPEN-METEO URL
    # =================================

    weather_url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&"
        f"longitude={longitude}&"
        "current="
        "temperature_2m,"
        "relative_humidity_2m,"
        "wind_speed_10m,"
        "weather_code,"
        "apparent_temperature&"
        "daily="
        "weather_code,"
        "temperature_2m_max,"
        "temperature_2m_min,"
        "precipitation_probability_max,"
        "sunrise,"
        "sunset&"
        "forecast_days=7&"
        "timezone=auto"
    )

    # =================================
    # REQUEST WEATHER
    # =================================

    weather_response = None

    async with httpx.AsyncClient() as client:

        for attempt in range(3):

            try:

                weather_response = await client.get(
                    weather_url,
                    timeout=30
                )

                # =================================
                # RATE LIMIT
                # =================================

                if weather_response.status_code == 429:

                    # Get Retry-After header if available
                    retry_after = weather_response.headers.get(
                        "Retry-After"
                    )

                    if retry_after:

                        try:
                            wait_time = int(retry_after)
                        except ValueError:
                            wait_time = 10

                    else:

                        wait_time = 10 * (attempt + 1)

                    # Retry only twice
                    if attempt < 2:

                        await asyncio.sleep(
                            min(wait_time, 30)
                        )

                        continue

                    raise HTTPException(
                        status_code=429,
                        detail=(
                            "Open-Meteo is currently "
                            "rate-limiting requests. "
                            "Please try again later."
                        )
                    )

                # =================================
                # OTHER HTTP ERRORS
                # =================================

                weather_response.raise_for_status()

                break

            except httpx.RequestError:

                if attempt < 2:

                    await asyncio.sleep(
                        3 * (attempt + 1)
                    )

                    continue

                raise HTTPException(
                    status_code=503,
                    detail=(
                        "Could not connect to "
                        "the weather service."
                    )
                )

            except httpx.HTTPStatusError as e:

                raise HTTPException(
                    status_code=502,
                    detail=(
                        "Weather service returned "
                        f"status {e.response.status_code}."
                    )
                )

    # =================================
    # SAFETY CHECK
    # =================================

    if weather_response is None:

        raise HTTPException(
            status_code=502,
            detail="No response from weather service."
        )

    # =================================
    # PARSE JSON
    # =================================

    try:

        weather_data = weather_response.json()

    except Exception:

        raise HTTPException(
            status_code=502,
            detail=(
                "Weather service returned "
                "invalid JSON."
            )
        )

    # =================================
    # VALIDATE RESPONSE
    # =================================

    if "current" not in weather_data:

        raise HTTPException(
            status_code=502,
            detail=(
                "Weather service returned "
                "no current weather data."
            )
        )

    if "daily" not in weather_data:

        raise HTTPException(
            status_code=502,
            detail=(
                "Weather service returned "
                "no forecast data."
            )
        )

    current = weather_data["current"]
    daily = weather_data["daily"]

    # =================================
    # CREATE RESULT
    # =================================

    result = {

        "temperature":
            current["temperature_2m"],

        "humidity":
            current["relative_humidity_2m"],

        "wind_speed":
            current["wind_speed_10m"],

        "weather_code":
            current["weather_code"],

        "feels_like":
            current["apparent_temperature"],

        "sunrise":
            daily["sunrise"],

        "sunset":
            daily["sunset"],

        "rain_probability":
            daily["precipitation_probability_max"],

        "forecast": [

            {
                "date": date,

                "weather_code": code,

                "max_temp": max_temp,

                "min_temp": min_temp
            }

            for date, code, max_temp, min_temp in zip(

                daily["time"],

                daily["weather_code"],

                daily["temperature_2m_max"],

                daily["temperature_2m_min"]
            )
        ]
    }

    # =================================
    # SAVE TO CACHE
    # =================================

    weather_cache[cache_key] = (
        result,
        time()
    )

    return result

