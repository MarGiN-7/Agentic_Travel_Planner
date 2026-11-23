
import json

import pytest

from services.itinerary_parser import parse_itinerary


def sample_response():
    return {
        "itinerary_markdown": "# Goa Trip\n\nDay 1: Beach",
        "expenses": {
            "flights": 15000,
            "accommodation": 6000,
            "food": 3000,
            "local_transport": 1000,
            "activities": 0,
            "other": 0,
        },
        "price_source": "ai_estimate",
        "assumptions": ["Prices are estimates"],
    }


def test_parses_plain_json():
    plan = parse_itinerary(json.dumps(sample_response()))

    assert plan.itinerary_markdown.startswith("# Goa Trip")
    assert plan.expenses.total == 25000
    assert plan.price_source == "ai_estimate"


def test_parses_gemini_text_blocks():
    output = [
        {
            "type": "text",
            "text": json.dumps(sample_response()),
            "index": 0,
        }
    ]

    plan = parse_itinerary(output)

    assert plan.expenses.total == 25000


def test_parses_json_code_fence():
    output = "```json\n" + json.dumps(sample_response()) + "\n```"

    plan = parse_itinerary(output)

    assert plan.expenses.total == 25000


def test_allows_missing_expenses():
    data = sample_response()
    data["expenses"] = None

    plan = parse_itinerary(json.dumps(data))

    assert plan.expenses is None


def test_rejects_negative_expenses():
    data = sample_response()
    data["expenses"]["flights"] = -100

    with pytest.raises(ValueError):
        parse_itinerary(json.dumps(data))


def test_rejects_invalid_json():
    with pytest.raises(ValueError):
        parse_itinerary("This is a regular Markdown itinerary.")


def test_rejects_empty_response():
    with pytest.raises(ValueError):
        parse_itinerary("")
