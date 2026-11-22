import json
from langchain.tools import tool

@tool
def hotel_recommendation(city: str, min_rating: float = 4.0):
    """
    Recommend hotels in a specific city with a minimum rating.
    Returns a list of hotels with their price per night, rating, and amenities.
    """
    try:
        with open(r'C:\Users\Kushagra Singhal\AgenticTravelPlanner\data\hotels.json', 'r') as f:
            hotels = json.load(f)
        
        results = [h for h in hotels if h['city'].lower() == city.lower() and h['rating'] >= min_rating]
        
        if not results:
            return f"No hotels found in {city} with rating >= {min_rating}."
        
        # Sort by rating (highest first)
        results.sort(key=lambda x: x['rating'], reverse=True)
        return results
    except Exception as e:
        return f"Error searching hotels: {str(e)}"
