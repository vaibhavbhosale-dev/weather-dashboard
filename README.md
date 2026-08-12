# 🌤️ Weather Dashboard

# 🌤️ Weather Dashboard

A full-stack weather dashboard built using Streamlit and FastAPI.

## 🚀 Live Demo

👉 [Open Weather Dashboard](https://weather-dashboard-k9girn8hkbvnkp4n2qtkp9.streamlit.app/)

## 🔗 Backend API

👉 [View FastAPI API Documentation](https://weather-dashboard-production-7db3.up.railway.app/docs)

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