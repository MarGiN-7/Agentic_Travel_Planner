
import os
import sys
from datetime import date, timedelta
from decimal import Decimal
from html import escape

import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError

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
from models.trip_request import TripRequest
from services.itinerary_parser import parse_itinerary
from services.budget_service import BudgetAssessment

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

if "budget_data" not in st.session_state:
    st.session_state.budget_data = None

if "price_source" not in st.session_state:
    st.session_state.price_source = "unknown"

if "price_assumptions" not in st.session_state:
    st.session_state.price_assumptions = []


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
        source = st.text_input("📍 Departure City", placeholder="e.g. Delhi")
    with col2:
        destination = st.text_input("🏝️ Destination City", placeholder="e.g. Goa")

    col3, col4 = st.columns(2, gap="large")
    with col3:
        departure_date = st.date_input(
            "📅 Departure Date",
            value=date.today() + timedelta(days=7),
            min_value=date.today(),
        )
    with col4:
        travelers = st.number_input(
            "👥 Number of Travelers", min_value=1, max_value=20, value=2, step=1
        )

    num_days = st.slider("🗓️ Trip Duration (Days)", 1, 14, 4)

    col5, col6 = st.columns(2, gap="large")
    with col5:
        budget = st.number_input(
            "💰 Total Trip Budget (INR)",
            min_value=1,
            value=25000,
            step=1000,
            help="Total budget for all travelers, not per person.",
        )
    with col6:
        travel_style = st.selectbox(
            "✨ Travel Style", ["budget", "balanced", "luxury"], index=1,
            format_func=str.title,
        )

    interests = st.multiselect(
        "🎯 Your Interests",
        ["Beaches", "Nature", "Adventure", "Food", "Culture",
         "Shopping", "History", "Nightlife", "Relaxation", "Wildlife"],
        default=["Nature", "Food"],
        max_selections=10,
    )

    st.caption("Prices are estimates. Confirm live prices and availability before booking.")
    submit_button = st.form_submit_button(
        "✨ Generate My Trip", use_container_width=True, type="primary"
    )


# -----------------------------
# Generate trip
# -----------------------------
if submit_button:
    try:
        trip = TripRequest(
            source=source,
            destination=destination,
            departure_date=departure_date,
            num_days=num_days,
            travelers=travelers,
            budget=budget,
            travel_style=travel_style,
            interests=interests,
        )
    except ValidationError as exc:
        for error in exc.errors():
            field = ".".join(str(part) for part in error["loc"]) or "Trip"
            st.error(f"{field}: {error['msg']}")
    else:
        if not os.getenv("GOOGLE_API_KEY"):
            st.error("Please configure your Gemini API key in the sidebar or .env file.")
        else:
            # Avoid showing a stale result if the new request fails.
            st.session_state.itinerary = ""
            st.session_state.trip_info = {}
            st.session_state.budget_data = None
            st.session_state.price_source = "unknown"
            st.session_state.price_assumptions = []

            with st.spinner(
                f"🌍 Planning your {trip.num_days}-day adventure to {trip.destination}..."
            ):
                try:
                    agent = create_travel_agent()
                    response = agent.invoke({"input": trip.to_agent_prompt()})
                    raw_output = response.get("output", "")
                    try:
                        plan = parse_itinerary(raw_output)
                    except ValueError:
                        # Keep a readable fallback if Gemini fails to return valid JSON.
                        # Do not attempt to infer costs from arbitrary text.
                        st.warning(
                            "Gemini returned an unstructured response. "
                            "The itinerary is shown below, but budget analysis is unavailable."
                        )
                        itinerary_text = extract_text(raw_output)
                        plan = None
                    else:
                        itinerary_text = plan.itinerary_markdown

                    if itinerary_text.strip():
                        st.session_state.itinerary = itinerary_text
                        st.session_state.trip_info = {
                            "source": trip.source,
                            "destination": trip.destination,
                            "days": trip.num_days,
                            "departure_date": trip.departure_date.isoformat(),
                            "travelers": trip.travelers,
                            "budget": trip.budget,
                            "travel_style": trip.travel_style,
                            "interests": trip.interests,
                        }
                        if plan is not None:
                            st.session_state.price_source = plan.price_source
                            st.session_state.price_assumptions = plan.assumptions
                            if plan.expenses is not None:
                                st.session_state.budget_data = BudgetAssessment(
                                    budget=Decimal(str(trip.budget)),
                                    expenses=plan.expenses,
                                ).model_dump(mode="json")
                        st.success("Your personalized trip plan is ready!")
                    else:
                        st.warning("The AI returned no itinerary text. Please try again.")
                except Exception:
                    st.error(
                        "Trip generation failed. Check your API key, connection, "
                        "and Gemini quota, then try again."
                    )


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
                {escape(info['source'])} → {escape(info['destination'])}
                &nbsp; | &nbsp; {info['days']} Days
                &nbsp; | &nbsp; {escape(info['departure_date'])}
                &nbsp; | &nbsp; {info['travelers']} Traveler(s)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## 🧭 Your Personalized Itinerary")

    with st.container(border=True):
        st.markdown(st.session_state.itinerary)

    st.markdown("## 💰 Trip Budget Analysis")
    budget_data = st.session_state.budget_data
    if budget_data is None:
        st.info("Budget analysis unavailable: a complete expense breakdown was not provided.")
    else:
        # Revalidate persisted data; all arithmetic comes from BudgetAssessment.
        assessment = BudgetAssessment.model_validate(budget_data)
        cost = assessment.total_cost
        remaining = assessment.remaining
        utilization = float(assessment.utilization_percent)

        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Your budget", f"₹{assessment.budget:,.0f}")
        metric2.metric("Estimated trip cost", f"₹{cost:,.0f}")
        metric3.metric(
            "Remaining budget" if remaining >= 0 else "Over budget by",
            f"₹{abs(remaining):,.0f}",
        )
        st.progress(min(max(utilization / 100, 0.0), 1.0))
        st.caption(f"Estimated budget utilization: {utilization:.1f}%")

        if not assessment.within_budget:
            st.error(
                f"Estimated costs exceed your budget by ₹{-remaining:,.0f}. "
                "Consider cheaper flights, accommodation, or activities."
            )
        elif utilization >= 90:
            st.warning(
                "This plan uses almost all of your budget. "
                "Allow extra room for unexpected costs."
            )
        else:
            st.success("Estimated expenses fit within your stated budget.")

        categories = {
            "Flights": assessment.expenses.flights,
            "Accommodation": assessment.expenses.accommodation,
            "Food": assessment.expenses.food,
            "Local transport": assessment.expenses.local_transport,
            "Activities": assessment.expenses.activities,
            "Other": assessment.expenses.other,
        }
        st.markdown("### Expense breakdown")
        st.bar_chart({name: float(value) for name, value in categories.items()})
        with st.expander("See itemized estimated expenses"):
            for name, amount in categories.items():
                st.write(f"{name}: ₹{amount:,.0f}")

        if assessment.expenses.activities == 0:
            st.warning(
                "Activities are listed as ₹0. Check whether sightseeing, "
                "entry fees, or tours have been omitted from the estimate."
            )

    source_labels = {
        "ai_estimate": "AI-generated estimate",
        "local_dataset": "Local dataset / sample prices",
        "live_api": "Live API (as reported by the agent; not independently verified)",
        "unknown": "Unknown or mixed sources",
    }
    st.caption(
        "Price source: " + source_labels.get(st.session_state.price_source, "Unknown")
        + ". Prices and availability must be confirmed before booking."
    )
    if st.session_state.price_assumptions:
        with st.expander("Pricing assumptions"):
            for assumption in st.session_state.price_assumptions:
                st.write("• " + str(assumption))

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
