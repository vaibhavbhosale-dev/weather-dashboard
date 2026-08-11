import httpx
from fastapi import HTTPException
from time import time


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
        f"https://geocoding-api.open-meteo.com/v1/search"
        f"?name={city}&count=1&language=en&format=json"
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
                detail=f"Geocoding service error: {e.response.status_code}"
            )

        except httpx.RequestError:

            raise HTTPException(
                status_code=503,
                detail="Could not connect to the geocoding service."
            )

        data = response.json()

    if "results" not in data or not data["results"]:

        raise HTTPException(
            status_code=404,
            detail="City not found"
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
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&"
        f"longitude={longitude}&"
        f"current="
        f"temperature_2m,"
        f"relative_humidity_2m,"
        f"wind_speed_10m,"
        f"weather_code,"
        f"apparent_temperature&"
        f"daily="
        f"weather_code,"
        f"temperature_2m_max,"
        f"temperature_2m_min,"
        f"precipitation_probability_max,"
        f"sunrise,"
        f"sunset&"
        f"forecast_days=7&"
        f"timezone=auto"
    )


    # =================================
    # REQUEST WEATHER
    # =================================

    async with httpx.AsyncClient() as client:

        try:

            weather_response = await client.get(
                weather_url,
                timeout=30
            )

        except httpx.RequestError:

            raise HTTPException(
                status_code=503,
                detail="Could not connect to the weather service."
            )


    # =================================
    # RATE LIMIT
    # =================================

    if weather_response.status_code == 429:

        raise HTTPException(
            status_code=429,
            detail=(
                "Weather service is temporarily rate-limited. "
                "Please try again later."
            )
        )


    # =================================
    # OTHER HTTP ERRORS
    # =================================

    try:

        weather_response.raise_for_status()

    except httpx.HTTPStatusError as e:

        raise HTTPException(
            status_code=502,
            detail=(
                f"Weather service returned "
                f"status {e.response.status_code}."
            )
        )


    # =================================
    # PARSE RESPONSE
    # =================================

    weather_data = weather_response.json()


    # =================================
    # VALIDATE RESPONSE
    # =================================

    if "current" not in weather_data:

        raise HTTPException(
            status_code=502,
            detail="Weather service returned an invalid response."
        )

    if "daily" not in weather_data:

        raise HTTPException(
            status_code=502,
            detail="Weather service returned incomplete forecast data."
        )


    # =================================
    # CREATE RESPONSE
    # =================================

    result = {

        "temperature":
            weather_data["current"]["temperature_2m"],

        "humidity":
            weather_data["current"]["relative_humidity_2m"],

        "wind_speed":
            weather_data["current"]["wind_speed_10m"],

        "weather_code":
            weather_data["current"]["weather_code"],

        "feels_like":
            weather_data["current"]["apparent_temperature"],

        "sunrise":
            weather_data["daily"]["sunrise"],

        "sunset":
            weather_data["daily"]["sunset"],

        "rain_probability":
            weather_data["daily"]["precipitation_probability_max"],

        "forecast": [

            {
                "date": date,
                "weather_code": code,
                "max_temp": max_temp,
                "min_temp": min_temp
            }

            for date, code, max_temp, min_temp in zip(

                weather_data["daily"]["time"],

                weather_data["daily"]["weather_code"],

                weather_data["daily"]["temperature_2m_max"],

                weather_data["daily"]["temperature_2m_min"]

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