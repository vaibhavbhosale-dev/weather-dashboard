
import streamlit as st
import httpx
import pandas as pd
import base64
from datetime import datetime


# =====================================
# BACKEND URL
# =====================================

BACKEND_URL = "https://weather-dashboard-production-7db3.up.railway.app"

# =====================================
# WEATHER ICONS
# =====================================

weather_icons = {
    0: ("☀️", "Clear Sky"),
    1: ("🌤️", "Mainly Clear"),
    2: ("⛅", "Partly Cloudy"),
    3: ("☁️", "Overcast"),
    45: ("🌫️", "Fog"),
    48: ("🌫️", "Fog"),
    51: ("🌦️", "Light Drizzle"),
    53: ("🌦️", "Moderate Drizzle"),
    55: ("🌧️", "Heavy Drizzle"),
    61: ("🌧️", "Light Rain"),
    63: ("🌧️", "Moderate Rain"),
    65: ("🌧️", "Heavy Rain"),
    71: ("❄️", "Snow"),
    73: ("❄️", "Moderate Snow"),
    75: ("❄️", "Heavy Snow"),
    80: ("🌦️", "Rain Showers"),
    81: ("🌦️", "Moderate Rain Showers"),
    82: ("🌧️", "Heavy Rain Showers"),
    95: ("⛈️", "Thunderstorm"),
    96: ("⛈️", "Thunderstorm with Hail"),
    99: ("⛈️", "Heavy Thunderstorm with Hail"),
}


# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
)


# =====================================
# LOAD BACKGROUND IMAGE
# =====================================

try:
    with open("assets/weather_bg.jpg", "rb") as image_file:
        encoded_image = base64.b64encode(
            image_file.read()
        ).decode()
except FileNotFoundError:
    encoded_image = ""


# =====================================
# CUSTOM CSS
# =====================================

if encoded_image:
    st.markdown(
        f"""
        <style>

        .stApp {{
            background-image:
                linear-gradient(
                    rgba(0, 0, 0, 0.55),
                    rgba(0, 0, 0, 0.55)
                ),
                url("data:image/jpeg;base64,{encoded_image}");

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        .forecast-card {{
            padding: 16px 6px;
            border-radius: 16px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.12);
            min-height: 190px;
            background: rgba(255,255,255,0.03);
            box-sizing: border-box;
        }}

        .forecast-day {{
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .forecast-icon {{
            font-size: 36px;
            margin: 8px 0;
        }}

        .forecast-temp {{
            font-size: 19px;
            font-weight: 700;
            margin-top: 8px;
        }}

        .forecast-min {{
            font-size: 13px;
            opacity: 0.6;
            margin-top: 3px;
        }}

        .forecast-condition {{
            font-size: 11px;
            opacity: 0.7;
            margin-top: 10px;
            line-height: 1.3;
        }}

        .forecast-rain {{
            font-size: 11px;
            opacity: 0.7;
            margin-top: 8px;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# =====================================
# PAGE HEADING
# =====================================

st.title("🌤️ Weather Dashboard")

st.caption("Built using FastAPI + Streamlit")


# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("About")

st.sidebar.write(
    """
    This app fetches weather data
    using the Open-Meteo API.
    """
)


# =====================================
# CITY INPUT
# =====================================

city = st.text_input(
    "🏙️ Enter City",
    placeholder="Example: Pune",
)


# =====================================
# SEARCH BUTTON
# =====================================

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    search = st.button(
        "🔍 Get Weather",
        use_container_width=True,
    )


# =====================================
# WEATHER REQUEST
# =====================================

if search:

    if not city.strip():

        st.warning("⚠️ Please enter a city name.")

    else:

        with st.spinner("Fetching weather..."):

            try:

                url = (
                    f"{BACKEND_URL}/weather/"
                    f"{city.strip()}"
                )

                response = httpx.get(
                    url,
                    timeout=60,
                )

            except httpx.RequestError:

                st.error(
                    "❌ Could not connect to the "
                    "weather server."
                )

                st.stop()

        # =================================
        # API RESPONSE
        # =================================

        if response.status_code == 200:

            data = response.json()

            # =================================
            # CURRENT WEATHER
            # =================================

            icon, condition = weather_icons.get(
                data.get("weather_code"),
                ("❓", "Unknown"),
            )

            st.subheader(
                f"📍 {data['city']}"
            )

            st.write(
                f"{icon} {condition}"
            )

            st.metric(
                "🌡 Temperature",
                f"{data['temperature']}°C",
            )


            # =================================
            # HUMIDITY + WIND + FEELS LIKE
            # =================================

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "💧 Humidity",
                    f"{data['humidity']}%",
                )

            with col2:

                st.metric(
                    "💨 Wind Speed",
                    f"{data['wind_speed']} km/h",
                )

            with col3:

                st.metric(
                    "🥵 Feels Like",
                    f"{data['feels_like']}°C",
                )


            # =================================
            # SUNRISE + SUNSET
            # =================================

            st.divider()

            st.subheader("🌅 Sun Information")

            sunrise = data["sunrise"][0]
            sunset = data["sunset"][0]

            sunrise_time = datetime.fromisoformat(
                sunrise
            ).strftime("%I:%M %p")

            sunset_time = datetime.fromisoformat(
                sunset
            ).strftime("%I:%M %p")

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "🌅 Sunrise",
                    sunrise_time,
                )

            with col2:

                st.metric(
                    "🌇 Sunset",
                    sunset_time,
                )


            # =================================
            # 7-DAY FORECAST
            # =================================

            st.divider()

            st.subheader("📅 7-Day Forecast")

            forecast = data["forecast"]

            rain_probability = data[
                "rain_probability"
            ]


            # =================================
            # FORECAST CARDS
            # =================================

            forecast_columns = st.columns(
                len(forecast)
            )

            for i, day in enumerate(forecast):

                with forecast_columns[i]:

                    date_string = day["date"]
                    weather_code = day["weather_code"]
                    max_temp = day["max_temp"]
                    min_temp = day["min_temp"]

                    rain = rain_probability[i]


                    # -----------------------------
                    # WEATHER ICON
                    # -----------------------------

                    icon, condition = weather_icons.get(
                        weather_code,
                        ("❓", "Unknown"),
                    )


                    # -----------------------------
                    # DATE
                    # -----------------------------

                    date = datetime.strptime(
                        date_string,
                        "%Y-%m-%d",
                    )


                    # -----------------------------
                    # DAY NAME
                    # -----------------------------

                    if i == 0:

                        day_name = "TODAY"

                    else:

                        day_name = date.strftime(
                            "%a"
                        ).upper()


                    # -----------------------------
                    # FORECAST CARD
                    # -----------------------------

                    st.html(
                        f"""
                        <div class="forecast-card">

                            <div class="forecast-day">
                                {day_name}
                            </div>

                            <div class="forecast-icon">
                                {icon}
                            </div>

                            <div class="forecast-temp">
                                {max_temp}°C
                            </div>

                            <div class="forecast-min">
                                {min_temp}°C
                            </div>

                            <div class="forecast-condition">
                                {condition}
                            </div>

                            <div class="forecast-rain">
                                🌧️ Rain: {rain}%
                            </div>

                        </div>
                        """
                    )


            # =================================
            # TEMPERATURE TREND
            # =================================

            st.divider()

            st.subheader("📈 Temperature Trend")


            # =================================
            # CREATE DATAFRAME
            # =================================

            forecast_df = pd.DataFrame({

                "Date": [
                    day["date"]
                    for day in forecast
                ],

                "Maximum Temperature": [
                    day["max_temp"]
                    for day in forecast
                ],

                "Minimum Temperature": [
                    day["min_temp"]
                    for day in forecast
                ],
            })


            # =================================
            # CONVERT DATE
            # =================================

            forecast_df["Date"] = pd.to_datetime(
                forecast_df["Date"]
            )


            # =================================
            # SET INDEX
            # =================================

            chart_df = forecast_df.set_index(
                "Date"
            )


            # =================================
            # DISPLAY CHART
            # =================================

            st.line_chart(chart_df)


        # =================================
        # API ERROR
        # =================================

        else:

            try:

                error_data = response.json()

                error_message = error_data.get(
                    "detail",
                    "Unable to fetch weather.",
                )

            except Exception:

                error_message = (
                    "Unable to fetch weather."
                )

            st.error(
                f"❌ {error_message}"
            )

