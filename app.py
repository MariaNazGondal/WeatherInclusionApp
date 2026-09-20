import os
from flask import Flask, render_template, request
import requests

# Explicitly bind template folder to current script directory
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Weather Code interpreter according to WMO standard
def interpret_weather(w_code, temp_c, is_day):
    # Base condition mapping
    rain_codes = [51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99]
    snow_codes = [71, 73, 75, 77, 85, 86]
    cloudy_codes = [1, 2, 3, 45, 48]
    
    if w_code in rain_codes:
        condition = "Rainy"
        weather_icon = "🌧️"
        status_text = "It is raining outside."
    elif w_code in snow_codes:
        condition = "Snowy"
        weather_icon = "❄️"
        status_text = "It is snowing outside."
    elif w_code in cloudy_codes:
        condition = "Cloudy"
        weather_icon = "☁️"
        status_text = "It is cloudy outside."
    else:
        condition = "Sunny"
        weather_icon = "☀️" if is_day else "🌙"
        status_text = "The sky is clear."

    # Dress Code rules (Plain language + Visuals)
    clothes = []
    if temp_c < 5:
        clothes.append({"item": "Heavy Winter Coat", "icon": "🧥", "desc": "Keep very warm"})
        clothes.append({"item": "Warm Hat & Gloves", "icon": "🧤", "desc": "Protect head and hands"})
        clothes.append({"item": "Warm Boots", "icon": "🥾", "desc": "Warm feet"})
    elif 5 <= temp_c < 16:
        clothes.append({"item": "Warm Jacket / Sweater", "icon": "🧥", "desc": "Cozy layer"})
        clothes.append({"item": "Long Pants", "icon": "👖", "desc": "Cover legs"})
        clothes.append({"item": "Closed Shoes", "icon": "👟", "desc": "Comfortable sneakers"})
    elif 16 <= temp_c < 24:
        clothes.append({"item": "T-shirt & Light Cardigan", "icon": "👕", "desc": "Nice and comfortable"})
        clothes.append({"item": "Pants or Skirt", "icon": "👖", "desc": "Light clothing"})
        clothes.append({"item": "Walking Shoes", "icon": "👟", "desc": "Ready to move"})
    else:
        clothes.append({"item": "Light T-Shirt / Shorts", "icon": "🩳", "desc": "Stay cool"})
        clothes.append({"item": "Sun Hat / Sunglasses", "icon": "🕶️", "desc": "Protect from sun"})
        clothes.append({"item": "Drink Water", "icon": "💧", "desc": "Stay hydrated"})

    if w_code in rain_codes:
        clothes.append({"item": "Rain Jacket or Umbrella", "icon": "☂️", "desc": "Stay dry"})
    elif w_code in snow_codes:
        clothes.append({"item": "Waterproof Boots", "icon": "🥾", "desc": "Walk safely"})

    # Activity recommendations (Simple visual cues)
    activities = []
    if w_code in rain_codes or w_code in snow_codes or temp_c < 0:
        activities.append({"name": "Drawing or Puzzles", "icon": "🎨", "where": "Inside"})
        activities.append({"name": "Listen to Music", "icon": "🎵", "where": "Inside"})
        activities.append({"name": "Board Games", "icon": "🎲", "where": "Inside"})
    else:
        activities.append({"name": "Go for a Walk", "icon": "🚶", "where": "Outside"})
        activities.append({"name": "Visit a Park", "icon": "🌳", "where": "Outside"})
        activities.append({"name": "Play Ball", "icon": "⚽", "where": "Outside"})

    return {
        "condition": condition,
        "weather_icon": weather_icon,
        "status_text": status_text,
        "clothes": clothes,
        "activities": activities
    }

@app.route("/", methods=["GET", "POST"])
def index():
    city = request.form.get("city", "Copenhagen")
    weather_data = None
    error_msg = None

    try:
        # Step 1: Geocoding API
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()

        if geo_res.get("results"):
            lat = geo_res["results"][0]["latitude"]
            lon = geo_res["results"][0]["longitude"]
            city_name = geo_res["results"][0]["name"]
            country = geo_res["results"][0].get("country", "")

            # Step 2: Forecast API
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            w_res = requests.get(weather_url).json()
            current = w_res["current_weather"]

            temp_c = round(current["temperature"])
            w_code = current["weathercode"]
            is_day = current.get("is_day", 1)

            insights = interpret_weather(w_code, temp_c, is_day)

            weather_data = {
                "city": f"{city_name}, {country}",
                "temp": temp_c,
                **insights
            }
        else:
            error_msg = "City not found. Try typing a major city name."
    except Exception:
        error_msg = "Could not fetch weather right now. Check internet connection."

    return render_template("index.html", weather=weather_data, error=error_msg, city=city)

if __name__ == "__main__":
    app.run(debug=True, port=5000)