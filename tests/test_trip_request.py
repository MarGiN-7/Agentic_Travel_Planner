
from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from models.trip_request import TripRequest


def valid_trip(**overrides):
    data = {
        "source": "Delhi",
        "destination": "Goa",
        "departure_date": date.today() + timedelta(days=7),
        "num_days": 4,
        "travelers": 2,
        "budget": 25000,
        "travel_style": "balanced",
        "interests": ["Beaches", "Nature"],
    }

    data.update(overrides)
    return TripRequest(**data)


def test_valid_trip():
    trip = valid_trip()

    assert trip.source == "Delhi"
    assert trip.destination == "Goa"
    assert trip.num_days == 4
    assert trip.budget == 25000


def test_prompt_contains_preferences():
    trip = valid_trip()

    prompt = trip.to_agent_prompt()

    assert "Delhi to Goa" in prompt
    assert "Travelers: 2" in prompt
    assert "INR 25,000" in prompt
    assert "Beaches, Nature" in prompt


def test_same_source_and_destination_rejected():
    with pytest.raises(ValidationError):
        valid_trip(
            source="Delhi",
            destination="delhi"
        )


def test_past_departure_date_rejected():
    with pytest.raises(ValidationError):
        valid_trip(
            departure_date=date.today() - timedelta(days=1)
        )


@pytest.mark.parametrize("days", [0, 15, -1])
def test_invalid_duration_rejected(days):
    with pytest.raises(ValidationError):
        valid_trip(num_days=days)


@pytest.mark.parametrize("budget", [0, -500])
def test_invalid_budget_rejected(budget):
    with pytest.raises(ValidationError):
        valid_trip(budget=budget)


def test_city_whitespace_normalized():
    trip = valid_trip(source="  New   Delhi  ")

    assert trip.source == "New Delhi"


def test_duplicate_interests_removed():
    trip = valid_trip(
        interests=["Beaches", "Nature", "Beaches"]
    )

    assert trip.interests == ["Beaches", "Nature"]
