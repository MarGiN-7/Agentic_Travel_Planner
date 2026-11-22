import requests
from langchain.tools import tool

# Simple city to lat/long mapping for demo purposes
CITY_COORDINATES = {
    "goa": {"lat": 15.2993, "lon": 74.1240},
    "mumbai": {"lat": 19.0760, "lon": 72.8777},
    "delhi": {"lat": 28.6139, "lon": 77.2090},
    "bangalore": {"lat": 12.9716, "lon": 77.5946},
    "manali": {"lat": 32.2432, "lon": 77.1892}
}

@tool
def weather_lookup(city: str):
    """
    Look up the current weather forecast for a given city using Open-Meteo API.
    Returns a brief summary of the weather.
    """
    city_lower = city.lower()
    if city_lower not in CITY_COORDINATES:
        return f"Weather data not available for {city}. Please check the city name."
    
    coords = CITY_COORDINATES[city_lower]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "daily" in data:
            # Simplified weather code mapping
            weather_codes = {
                0: "Clear sky",
                1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Fog", 48: "Depositing rime fog",
                51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
                95: "Thunderstorm"
            }
            
            days = data['daily']['time']
            max_temps = data['daily']['temperature_2m_max']
            min_temps = data['daily']['temperature_2m_min']
            codes = data['daily']['weathercode']
            
            forecast = []
            for i in range(min(3, len(days))): # Return 3 days forecast
                condition = weather_codes.get(codes[i], "Unknown")
                forecast.append(f"{days[i]}: {condition}, Max: {max_temps[i]}°C, Min: {min_temps[i]}°C")
            
            return "\n".join(forecast)
        else:
            return "Could not retrieve weather forecast."
            
    except Exception as e:
        return f"Error fetching weather: {str(e)}"
