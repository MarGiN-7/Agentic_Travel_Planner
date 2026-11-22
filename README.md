# Agentic AI-Based Travel Planning Assistant💫

An intelligent travel planning system built using LangChain, OpenAI, and Streamlit. This assistant autonomously creates optimized trip itineraries by searching for flights, hotels, attractions, and real-time weather data.

## Features
- **Flight Search**: Finds available flights from local JSON data and suggests options.
- **Hotel Recommendation**: Suggests top-rated hotels based on user destination.
- **Places Discovery**: Recommends popular attractions and POIs.
- **Weather Integration**: Fetches real-time weather forecasts using the Open-Meteo API.
- **Budget Estimation**: Provides a total cost breakdown including flights, accommodation, and daily expenses.
- **Agentic Reasoning**: Uses a LangChain ToolCalling agent to make decisions and justify choices.

## Project Structure
```
AgenticTravelPlanner/
├── data/
│   ├── flights.json       # Mock flight data
│   ├── hotels.json        # Mock hotel data
│   └── places.json        # Mock places/attractions data
├── tools/
│   ├── flight_tool.py     # LangChain tool for flight search
│   ├── hotel_tool.py      # LangChain tool for hotel recommendations
│   ├── place_tool.py      # LangChain tool for places discovery
│   ├── weather_tool.py    # LangChain tool for weather (Open-Meteo API)
│   └── budget_tool.py     # LangChain tool for budget calculation
├── agents/
│   └── travel_agent.py    # Core LangChain agent logic
├── app.py                 # Streamlit UI application
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Setup Instructions

1. **Clone the repository** (or navigate to the folder).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables**:
   Create a `.env` file and add your OpenAI API Key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Technologies Used
- **Python**: Core programming language.
- **LangChain**: Framework for building the Agentic AI.
- **OpenAI GPT-3.5/4**: LLM for reasoning and planning.
- **Streamlit**: Web interface for user interaction.
- **Open-Meteo API**: Free weather forecast data.
