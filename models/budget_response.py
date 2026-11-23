
from typing import Literal

from pydantic import BaseModel, Field

from services.budget_service import TripExpenses


class BudgetResponse(BaseModel):
    expenses: TripExpenses

    price_source: Literal[
        "live_api",
        "local_dataset",
        "ai_estimate",
    ] = "ai_estimate"

    assumptions: list[str] = Field(
        default_factory=list
    )
