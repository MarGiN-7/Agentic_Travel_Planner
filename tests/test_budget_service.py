
from decimal import Decimal

import pytest
from pydantic import ValidationError

from services.budget_service import (
    BudgetAssessment,
    TripExpenses,
)


def sample_expenses():
    return TripExpenses(
        flights=14400,
        accommodation=9600,
        food=5000,
        local_transport=2000,
        activities=1000,
    )


def test_total_expenses():
    assert sample_expenses().total == Decimal("32000")


def test_over_budget():
    assessment = BudgetAssessment(
        budget=25000,
        expenses=sample_expenses(),
    )

    assert assessment.within_budget is False
    assert assessment.remaining == Decimal("-7000")
    assert assessment.utilization_percent == Decimal("128.00")


def test_within_budget():
    assessment = BudgetAssessment(
        budget=40000,
        expenses=sample_expenses(),
    )

    assert assessment.within_budget is True
    assert assessment.remaining == Decimal("8000")


def test_exact_budget():
    assessment = BudgetAssessment(
        budget=32000,
        expenses=sample_expenses(),
    )

    assert assessment.within_budget is True
    assert assessment.remaining == Decimal("0")


def test_negative_expense_rejected():
    with pytest.raises(ValidationError):
        TripExpenses(
            flights=-100,
            accommodation=1000,
            food=500,
            local_transport=200,
            activities=100,
        )


def test_zero_budget_rejected():
    with pytest.raises(ValidationError):
        BudgetAssessment(
            budget=0,
            expenses=sample_expenses(),
        )


def test_summary_mentions_over_budget():
    assessment = BudgetAssessment(
        budget=25000,
        expenses=sample_expenses(),
    )

    assert "Over budget" in assessment.summary()
    assert "7,000" in assessment.summary()
