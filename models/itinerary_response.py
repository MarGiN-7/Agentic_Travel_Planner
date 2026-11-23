
from typing import Literal

from pydantic import BaseModel, Field

from models.expense_completeness import ExpenseCompleteness
from services.budget_service import TripExpenses


class ItineraryResponse(BaseModel):
    itinerary_markdown: str = Field(min_length=1)

    expenses: TripExpenses | None = None

    price_source: Literal[
        "live_api",
        "local_dataset",
        "ai_estimate",
        "unknown",
    ] = "unknown"

    assumptions: list[str] = Field(default_factory=list)

    completeness: ExpenseCompleteness | None = None
