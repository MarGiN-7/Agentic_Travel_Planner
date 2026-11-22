
import streamlit as st
import os
import sys

# Add the local lib folder to sys.path
lib_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "lib"
)
if os.path.exists(lib_path):
    sys.path.insert(0, lib_path)

from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.travel_agent import create_travel_agent

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Agentic AI Travel Planning Assistant")

st.markdown("""
Plan your next adventure with the help of an intelligent AI Agent.
It searches for flights, hotels, attractions, and even checks the weather for you!
""")

# Sidebar for configuration
with st.sidebar:
    st.header("Settings")

    gemini_api_key = st.text_input(
        "Gemini API Key",
        type="password"
    )

    if gemini_api_key:
        os.environ["GOOGLE_API_KEY"] = gemini_api_key

    st.info(
        "This agent uses LangChain and Google Gemini to plan your trip."
    )

# Main input form
with st.form("travel_form"):
    col1, col2 = st.columns(2)

    with col1:
        source = st.text_input(
            "Source City",
            placeholder="e.g. Delhi"
        )

    with col2:
        destination = st.text_input(
            "Destination City",
            placeholder="e.g. Goa"
        )

    num_days = st.slider(
        "Number of Days",
        1,
        7,
        3
    )

    submit_button = st.form_submit_button(
        "Generate Itinerary"
    )

# Generate itinerary
if submit_button:

    if not os.getenv("GOOGLE_API_KEY"):
        st.error(
            "Please provide a Gemini API Key in the sidebar or .env file."
        )

    elif not source or not destination:
        st.error(
            "Please enter both source and destination cities."
        )

    else:
        with st.spinner(
            f"Agent is planning your {num_days}-day trip to {destination}..."
        ):
            try:
                agent = create_travel_agent()

                user_input = (
                    f"Plan a {num_days}-day trip "
                    f"from {source} to {destination}."
                )

                response = agent.invoke({
                    "input": user_input
                })

                # Extract text from Gemini response
                output = response["output"]

                if isinstance(output, list):
                    itinerary_text = "\n\n".join(
                        block.get("text", "")
                        for block in output
                        if isinstance(block, dict)
                        and block.get("type") == "text"
                    )
                else:
                    itinerary_text = str(output)

                if itinerary_text.strip():
                    st.success("Trip Plan Generated!")

                    st.markdown(
                        "### Your Custom Itinerary"
                    )

                    st.markdown(itinerary_text)
                else:
                    st.warning(
                        "The agent returned no itinerary text."
                    )

            except Exception as e:
                st.error(
                    f"An error occurred: {str(e)}"
                )

st.divider()

st.caption(
    "Built with LangChain, Google Gemini, and Streamlit. "
    "Data sourced from local JSON and Open-Meteo API."
)
