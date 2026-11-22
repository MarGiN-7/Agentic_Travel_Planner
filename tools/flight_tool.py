import json
from langchain.tools import tool

@tool
def flight_search(source: str, destination: str):
    """
    Search for flights between a source and a destination city.
    Returns a list of available flights with their price, airline, and departure time.
    """
    try:
        with open(r'C:\Users\Kushagra Singhal\AgenticTravelPlanner\data\flights.json', 'r') as f:
            flights = json.load(f)
        
        results = [f for f in flights if f['source'].lower() == source.lower() and f['destination'].lower() == destination.lower()]
        
        if not results:
            return f"No flights found from {source} to {destination}."
        
        # Sort by price (cheapest first)
        results.sort(key=lambda x: x['price'])
        return results
    except Exception as e:
        return f"Error searching flights: {str(e)}"
