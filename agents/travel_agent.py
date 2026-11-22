import os
import sys

# Add the local lib folder to sys.path
lib_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib')
if os.path.exists(lib_path):
    sys.path.insert(0, lib_path)

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Import tools
from tools.flight_tool import flight_search
from tools.hotel_tool import hotel_recommendation
from tools.place_tool import place_discovery
from tools.weather_tool import weather_lookup
from tools.budget_tool import budget_estimation

load_dotenv()

def create_travel_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0
    )    
    tools = [
        flight_search,
        hotel_recommendation,
        place_discovery,
        weather_lookup,
        budget_estimation
    ]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI Travel Assistant. Your goal is to help users plan their trips by providing structured itineraries.
        
        Follow these steps:
        1. Search for flights from the source to the destination.
        2. Recommend a highly-rated hotel in the destination city.
        3. Discover interesting places to visit in the destination.
        4. Check the weather forecast for the destination.
        5. Estimate the total budget based on the selected flight, hotel, and duration.
        
        Provide your final answer in a clear, structured format including:
        - Trip Summary
        - Flight Option Selected (with price and airline)
        - Hotel Recommendation (with price and rating)
        - Weather Forecast
        - Day-wise Itinerary (assign places to different days)
        - Budget Breakdown
        - Reasoning: Briefly explain why you chose these options.
        
        Use the tools provided to gather all necessary information. If a tool returns no results, inform the user and suggest alternatives if possible."""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor

if __name__ == "__main__":
    # Test the agent
    agent = create_travel_agent()
    response = agent.invoke({"input": "Plan a 3-day trip from Delhi to Goa."})
    print(response["output"])
