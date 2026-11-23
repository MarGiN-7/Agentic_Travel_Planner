
import pytest
from pydantic import ValidationError

from models.expense_completeness import ExpenseCompleteness


def test_complete_budget():
    result = ExpenseCompleteness()

    assert result.is_complete is True
    assert result.missing_categories == []


def test_incomplete_budget():
    result = ExpenseCompleteness(
        missing_categories=["activities"]
    )

    assert result.is_complete is False
    assert "Activities" in result.warning_message()


def test_multiple_missing_categories():
    result = ExpenseCompleteness(
        missing_categories=["activities", "local_transport"]
    )

    assert result.is_complete is False
    assert "Activities" in result.warning_message()
    assert "Local Transport" in result.warning_message()


def test_duplicate_categories_removed():
    result = ExpenseCompleteness(
        missing_categories=[
            "activities",
            "activities",
            "food",
        ]
    )

    assert result.missing_categories == [
        "activities",
        "food",
    ]


def test_invalid_category_rejected():
    with pytest.raises(ValidationError):
        ExpenseCompleteness(
            missing_categories=["shopping"]
        )


def test_notes_preserved():
    result = ExpenseCompleteness(
        missing_categories=["activities"],
        notes=["Waterfall entry fees are not included."],
    )

    assert result.notes == [
        "Waterfall entry fees are not included."
    ]

def test_string_notes_normalized():
    result = ExpenseCompleteness(
        missing_categories=["activities"],
        notes="Waterfall entry fees are not included.",
    )

    assert result.notes == [
        "Waterfall entry fees are not included."
    ]
    assert result.is_complete is False
