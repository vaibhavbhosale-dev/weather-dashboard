# 🌤️ Weather Dashboard

A simple weather dashboard built using **Python, FastAPI, and Streamlit**.

This project allows users to enter a city and view its current weather information along with a 7-day forecast.

## ✨ Features

- 🌡️ Current temperature
- 🥵 Feels-like temperature
- 💧 Humidity
- 💨 Wind speed
- 🌦️ Current weather condition
- 🌧️ Rain probability
- 🌅 Sunrise time
- 🌇 Sunset time
- 📅 7-day weather forecast
- 📈 Temperature trend chart
- 🌤️ Weather-based icons
- 🖼️ Custom weather background

## 🛠️ Technologies Used

- **Python**
- **FastAPI** – Backend
- **Streamlit** – Frontend
- **HTTPX** – Making API requests
- **Pandas** – Processing forecast data
- **Open-Meteo API** – Weather and geocoding data

## 🔄 How It Works

The basic flow of the project is:

```text
User enters a city
        ↓
Streamlit frontend
        ↓
FastAPI backend
        ↓
Geocoding API
        ↓
Latitude + Longitude
        ↓
Open-Meteo Weather API
        ↓
FastAPI processes the data
        ↓
Streamlit displays the weather