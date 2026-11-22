
import os
import sys
import streamlit as st
from dotenv import load_dotenv

# -----------------------------
# Project setup
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "lib")

if os.path.exists(LIB_DIR):
    sys.path.insert(0, LIB_DIR)

sys.path.append(BASE_DIR)

load_dotenv()

from agents.travel_agent import create_travel_agent

st.set_page_config(
    page_title="WanderAI | Smart Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background: #f5f8fc;
        color: #172b4d;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1150px;
    }

    .hero {
        background: linear-gradient(
            120deg, #102a43, #176b87, #159895
        );
        border-radius: 22px;
        padding: 45px 38px;
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 12px 28px rgba(16, 42, 67, .14);
    }

    .hero h1 {
        color: white !important;
        font-size: clamp(2rem, 4vw, 3.2rem);
        font-weight: 800;
        margin: 0 0 12px;
    }

    .hero p {
        color: #e0f2fe !important;
        font-size: 1.08rem;
        line-height: 1.7;
        max-width: 650px;
    }

    .eyebrow {
        color: #a5f3fc;
        font-size: .82rem;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }

    .section-title {
        font-size: 1.55rem;
        font-weight: 750;
        color: #102a43;
        margin-bottom: 5px;
    }

    .section-subtitle {
        color: #64748b;
        margin-bottom: 20px;
    }

    .feature-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 23px 18px;
        min-height: 155px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,.03);
    }

    .feature-card h3 {
        color: #123451;
        font-size: 1.05rem;
        margin: 8px 0;
    }

    .feature-card p {
        color: #64748b;
        font-size: .9rem;
        line-height: 1.5;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button {
        background: linear-gradient(90deg, #087e8b, #0d9488);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        padding: .75rem 1.5rem;
        min-height: 48px;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button:hover {
        background: #096b75;
        color: white;
        border: none;
    }

    div[data-testid="stForm"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 5px 20px rgba(0,0,0,.035);
    }

    .result-header {
        background: #e6f7f4;
        border-left: 5px solid #0d9488;
        border-radius: 10px;
        padding: 18px;
        margin: 18px 0;
        color: #134e4a;
    }

    .result-header h3 {
        color: #134e4a;
        margin: 0 0 6px;
    }

    .footer {
        text-align: center;
        color: #64748b;
        padding: 24px 0;
        font-size: .88rem;
    }

    @media (max-width: 640px) {
        .hero {
            padding: 28px 20px;
        }
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Gemini response formatter
# -----------------------------
def extract_text(output):
    if isinstance(output, str):
        return output

    if isinstance(output, list):
        parts = []
        for block in output:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
            elif isinstance(block, str):
                parts.append(block)
        return "\n\n".join(parts)

    return str(output) if output is not None else ""


# -----------------------------
# Session state
# -----------------------------
if "itinerary" not in st.session_state:
    st.session_state.itinerary = ""

if "trip_info" not in st.session_state:
    st.session_state.trip_info = {}


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("## 🌍 WanderAI")
    st.caption("Your intelligent travel companion")

    st.divider()

    st.markdown("### 🔐 AI Configuration")

    gemini_api_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Leave blank to use the GOOGLE_API_KEY from your .env file."
    )

    if gemini_api_key:
        os.environ["GOOGLE_API_KEY"] = gemini_api_key

    if os.getenv("GOOGLE_API_KEY"):
        st.success("Gemini API key configured")
    else:
        st.warning("Gemini API key required")

    st.divider()

    st.markdown("### ⚡ Powered By")
    st.markdown("""
    - Google Gemini
    - LangChain AI Agents
    - Streamlit
    - Python
    - Open-Meteo Weather
    """)

    st.divider()

    st.info(
        "Travel prices and recommendations are estimates. "
        "Confirm availability before booking."
    )


# -----------------------------
# Hero section
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="eyebrow">✦ YOUR AI TRAVEL COMPANION</div>
    <h1>Explore More.<br>Plan Smarter.</h1>
    <p>
        From flights and hotels to hidden gems and weather,
        let intelligent AI plan your next unforgettable journey.
    </p>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# Planning form
# -----------------------------
st.markdown(
    '<div class="section-title">✈️ Plan Your Next Adventure</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Tell us where you want to go. AI will handle the planning.'
    '</div>',
    unsafe_allow_html=True
)

with st.form("travel_form"):
    col1, col2 = st.columns(2, gap="large")

    with col1:
        source = st.text_input(
            "📍 Departure City",
            placeholder="e.g. Delhi"
        )

    with col2:
        destination = st.text_input(
            "🏝️ Destination City",
            placeholder="e.g. Goa"
        )

    st.write("")

    num_days = st.slider(
        "🗓️ Trip Duration (Days)",
        min_value=1,
        max_value=7,
        value=3
    )

    st.caption(
        f"Your personalized itinerary will cover {num_days} day(s)."
    )

    submit_button = st.form_submit_button(
        "✨ Generate My Trip",
        use_container_width=True,
        type="primary"
    )


# -----------------------------
# Generate trip
# -----------------------------
if submit_button:
    source = source.strip()
    destination = destination.strip()

    if not os.getenv("GOOGLE_API_KEY"):
        st.error(
            "Please configure your Gemini API key in the sidebar "
            "or .env file."
        )

    elif not source or not destination:
        st.error(
            "Please enter both departure and destination cities."
        )

    else:
        # Clear previous results before generating a new trip
        st.session_state.itinerary = ""
        st.session_state.trip_info = {}

        with st.spinner(
            f"🌍 Planning your {num_days}-day adventure to {destination}..."
        ):
            try:
                agent = create_travel_agent()

                user_input = (
                    f"Plan a {num_days}-day trip from "
                    f"{source} to {destination}. "
                    "Include flight options, hotel recommendations, "
                    "weather, tourist attractions, a day-wise "
                    "itinerary, and an estimated budget. "
                    "Format the final answer in readable Markdown."
                )

                response = agent.invoke({
                    "input": user_input
                })

                itinerary_text = extract_text(
                    response.get("output", "")
                )

                if itinerary_text.strip():
                    st.session_state.itinerary = itinerary_text
                    st.session_state.trip_info = {
                        "source": source,
                        "destination": destination,
                        "days": num_days
                    }
                else:
                    st.warning(
                        "The AI returned no itinerary text. "
                        "Please try again."
                    )

            except Exception as e:
                st.error(f"Trip generation failed: {e}")


# -----------------------------
# Display generated itinerary
# -----------------------------
if st.session_state.itinerary:
    info = st.session_state.trip_info

    st.markdown("---")

    st.markdown(
        f"""
        <div class="result-header">
            <h3>🎉 Your Adventure Is Ready!</h3>
            <div>
                {info['source']} → {info['destination']}
                &nbsp; | &nbsp; {info['days']} Days
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## 🧭 Your Personalized Itinerary")

    with st.container(border=True):
        st.markdown(st.session_state.itinerary)

    st.download_button(
        label="📥 Download Itinerary",
        data=st.session_state.itinerary,
        file_name="WanderAI_Travel_Itinerary.md",
        mime="text/markdown",
        use_container_width=True
    )


# -----------------------------
# Feature cards
# -----------------------------
st.markdown("---")

st.markdown(
    '<div class="section-title">Why Travel With WanderAI?</div>',
    unsafe_allow_html=True
)

st.write("")

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 28px;">✈️</div>
        <h3>Smart Flight Search</h3>
        <p>Explore relevant flight options and estimated fares.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 28px;">🏨</div>
        <h3>Hotel Recommendations</h3>
        <p>Discover accommodation options for your destination.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 28px;">🗺️</div>
        <h3>AI-Powered Itineraries</h3>
        <p>Get day-wise travel plans with activities and budgets.</p>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# Footer
# -----------------------------
st.markdown("""
<div class="footer">
    🌍 WanderAI — Explore the world, intelligently.<br>
    Built with Python · Streamlit · LangChain · Google Gemini
</div>
""", unsafe_allow_html=True)
