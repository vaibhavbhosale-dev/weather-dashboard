from fastapi import FastAPI
import httpx
from weather_service import get_coordinates,get_weather_data

app = FastAPI()


@app.get("/")
async def home():
    return {
        "message": "Welcome to Weather API"
    }


@app.get("/coordinates/{city}")
async def coordinates(city: str):
    return await get_coordinates(city)


@app.get("/weather/{city}")
async def weather(city: str):

    coordinate_data = await get_coordinates(city)

    weather_data = await get_weather_data(
    coordinate_data["latitude"],
    coordinate_data["longitude"]
    )

    return {
    "city": coordinate_data["city"],
    **weather_data
    }