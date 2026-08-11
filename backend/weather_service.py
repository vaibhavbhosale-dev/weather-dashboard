import httpx
from fastapi import HTTPException


async def get_coordinates(city: str):

    url = (
        f"https://geocoding-api.open-meteo.com/v1/search"
        f"?name={city}&count=1&language=en&format=json"
    )

    async with httpx.AsyncClient() as client:

        response = await client.get(url)

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


async def get_weather_data(
    latitude: float,
    longitude: float
):

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

    async with httpx.AsyncClient() as client:

        weather_response = await client.get(
            weather_url
        )

    weather_data = weather_response.json()

    return {

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