
import os
import sys

# Add the local lib folder to sys.path
lib_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib",
)

if os.path.exists(lib_path):
    sys.path.insert(0, lib_path)

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    create_tool_calling_agent,
    AgentExecutor,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

# Import travel tools
from tools.flight_tool import flight_search
from tools.hotel_tool import hotel_recommendation
from tools.place_tool import place_discovery
from tools.weather_tool import weather_lookup
from tools.budget_tool import budget_estimation

load_dotenv()


def create_travel_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0,
    )

    tools = [
        flight_search,
        hotel_recommendation,
        place_discovery,
        weather_lookup,
        budget_estimation,
    ]

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are WanderAI, an intelligent AI travel assistant.

Your task is to create personalized travel itineraries using
the available flight, hotel, place, weather, and budget tools.

Follow these rules:

1. Research available flights and hotels using the tools.
2. Discover suitable attractions and activities.
3. Check weather information when available.
4. Respect the user's dates, travelers, budget, travel
   style, and interests.
5. Provide a day-wise itinerary.
6. Clearly distinguish estimates from verified prices.
7. Never invent booking availability or missing prices.
8. If the estimated cost exceeds the user's budget,
   explain this and suggest cheaper alternatives.

IMPORTANT: Your FINAL response must be one valid JSON
object with exactly these top-level fields:

{{
  "itinerary_markdown": "Full readable Markdown itinerary",
  "expenses": {{
    "flights": 0,
    "accommodation": 0,
    "food": 0,
    "local_transport": 0,
    "activities": 0,
    "other": 0
  }},
  "price_source": "unknown",
  "assumptions": [],
  "completeness": {{
    "missing_categories": [],
    "notes": []
  }}
}}

Expense completeness rules:
- Report costs excluded from the estimate in
  "completeness.missing_categories".
- Allowed categories: flights, accommodation, food,
  local_transport, activities, other.
- If a category has unknown costs, do not use zero
  as a placeholder.
- If the estimate cannot represent a complete breakdown,
  set "expenses" to null.
- If expenses is null because costs are missing,
  list the missing categories whenever identifiable.
- Explain exclusions in "completeness.notes".
- An empty missing_categories list means no omissions
  were identified, not that prices were independently verified.
- If you cannot assess completeness, set
  "completeness" to null.
- Never claim a trip is fully within budget when
  required expenses are missing.

Expense rules:
- All expense amounts must be totals in INR for the
  entire traveling group, not per-person prices.
- Use non-negative numeric values.
- Do not add a total field. Python will calculate it.
- Never use zero for an unknown expense.
- Use zero only when a category genuinely has no cost.
- If a complete breakdown is unavailable, use
  "expenses": null.
- Use "local_dataset" for local sample data.
- Use "live_api" only for prices verified by a live API.
- Use "ai_estimate" for AI-generated price estimates.
- Use "unknown" when sources are uncertain or mixed.
- Explain important price assumptions in "assumptions".
- Keep the itinerary and expense data consistent.
- Return JSON only, without code fences or extra text.
"""
        ),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(
        llm,
        tools,
        prompt,
    )

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
    )


if __name__ == "__main__":
    agent = create_travel_agent()

    response = agent.invoke({
        "input": (
            "Plan a 4-day trip from Delhi to Goa "
            "for 3 travelers with a total budget of INR 25000. "
            "Travel style: balanced. "
            "Interests: nature and food."
        )
    })

    print(response["output"])
