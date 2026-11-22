import json
from langchain.tools import tool

@tool
def place_discovery(city: str, place_type: str = None):
    """
    Discover points of interest (POIs) in a specific city.
    Optionally filter by type (e.g., 'Beach', 'Heritage', 'Nature').
    Returns a list of places with their description and rating.
    """
    try:
        with open(r'C:\Users\Kushagra Singhal\AgenticTravelPlanner\data\places.json', 'r') as f:
            places = json.load(f)
        
        results = [p for p in places if p['city'].lower() == city.lower()]
        
        if place_type:
            results = [p for p in results if p['type'].lower() == place_type.lower()]
            
        if not results:
            return f"No places found in {city}" + (f" of type {place_type}." if place_type else ".")
        
        # Sort by rating (highest first)
        results.sort(key=lambda x: x['rating'], reverse=True)
        return results
    except Exception as e:
        return f"Error searching places: {str(e)}"
