
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from weather_service import (
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

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =====================================
# ROOT ENDPOINT
# =====================================

@app.get("/")
async def root():

    return {
        "message": "Weather Dashboard API is running!",
        "status": "online"
    }


# =====================================
# HEALTH CHECK
# =====================================

@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


# =====================================
# WEATHER ENDPOINT
# =====================================

@app.get("/weather/{city}")
async def weather(city: str):

    # -----------------------------
    # GET COORDINATES
    # -----------------------------

    location = await get_coordinates(city)

    # -----------------------------
    # GET WEATHER
    # -----------------------------

    weather_data = await get_weather_data(
        location["latitude"],
        location["longitude"]
    )

    # -----------------------------
    # COMBINE RESPONSE
    # -----------------------------

    return {

        "city": location["city"],

        "latitude": location["latitude"],

        "longitude": location["longitude"],

        "temperature":
            weather_data["temperature"],

        "humidity":
            weather_data["humidity"],

        "wind_speed":
            weather_data["wind_speed"],

        "weather_code":
            weather_data["weather_code"],

        "feels_like":
            weather_data["feels_like"],

        "sunrise":
            weather_data["sunrise"],

        "sunset":
            weather_data["sunset"],

        "rain_probability":
            weather_data["rain_probability"],

        "forecast":
            weather_data["forecast"]
    }
