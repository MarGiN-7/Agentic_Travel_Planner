import os
import sys

# Add the local lib folder to sys.path
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')
if os.path.exists(lib_path):
    sys.path.insert(0, lib_path)

from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.travel_agent import create_travel_agent

load_dotenv()

def test_planner():
    if not os.getenv("OPENAI_API_KEY"):
        print("Skipping test: No OpenAI API Key found.")
        return

    print("Initializing Travel Agent...")
    agent = create_travel_agent()
    
    print("Sending query: 'Plan a 2-day trip from Mumbai to Goa'...")
    try:
        response = agent.invoke({"input": "Plan a 2-day trip from Mumbai to Goa."})
        print("\n--- AGENT RESPONSE ---")
        print(response["output"])
        print("----------------------\n")
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_planner()
