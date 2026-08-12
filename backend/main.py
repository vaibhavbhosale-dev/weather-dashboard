
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.weather_service import get_coordinates, get_weather_data

from backend.weather_service import (
    get_coordinates,
    get_weather_data
)


# =====================================
# CREATE FASTAPI APP
# =====================================

app = FastAPI(
    title="Weather Dashboard API",
    description="Weather API using Open-Meteo",
    version="1.0.0"
)


# =====================================
# CORS
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================
# ROOT
# =====================================

@app.get("/")
async def root():

    return {
        "message": "Weather Dashboard API is running!"
    }


# =====================================
# WEATHER ENDPOINT
# =====================================

@app.get("/weather/{city}")
async def get_weather(city: str):

    # =================================
    # VALIDATE CITY
    # =================================

    city = city.strip()

    if not city:

        raise HTTPException(
            status_code=400,
            detail="City name cannot be empty."
        )

    # =================================
    # GET COORDINATES
    # =================================

    location = await get_coordinates(city)

    # =================================
    # GET WEATHER
    # =================================

    weather = await get_weather_data(
        location["latitude"],
        location["longitude"]
    )

    # =================================
    # COMBINE RESPONSE
    # =================================

    return {

        "city": location["city"],

        "latitude": location["latitude"],

        "longitude": location["longitude"],

        "temperature": weather["temperature"],

        "humidity": weather["humidity"],

        "wind_speed": weather["wind_speed"],

        "weather_code": weather["weather_code"],

        "feels_like": weather["feels_like"],

        "sunrise": weather["sunrise"],

        "sunset": weather["sunset"],

        "rain_probability":
            weather["rain_probability"],

        "forecast":
            weather["forecast"]
    }

