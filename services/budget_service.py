
from decimal import Decimal
from pydantic import BaseModel, Field, computed_field


class TripExpenses(BaseModel):
    flights: Decimal = Field(ge=0)
    accommodation: Decimal = Field(ge=0)
    food: Decimal = Field(ge=0)
    local_transport: Decimal = Field(ge=0)
    activities: Decimal = Field(ge=0)
    other: Decimal = Field(default=Decimal("0"), ge=0)

    @computed_field
    @property
    def total(self) -> Decimal:
        return sum(
            (
                self.flights,
                self.accommodation,
                self.food,
                self.local_transport,
                self.activities,
                self.other,
            ),
            Decimal("0"),
        )


class BudgetAssessment(BaseModel):
    budget: Decimal = Field(gt=0)
    expenses: TripExpenses

    @computed_field
    @property
    def total_cost(self) -> Decimal:
        return self.expenses.total

    @computed_field
    @property
    def remaining(self) -> Decimal:
        return self.budget - self.total_cost

    @computed_field
    @property
    def within_budget(self) -> bool:
        return self.total_cost <= self.budget

    @computed_field
    @property
    def utilization_percent(self) -> Decimal:
        return (
            self.total_cost / self.budget * Decimal("100")
        ).quantize(Decimal("0.01"))

    def summary(self) -> str:
        if self.within_budget:
            return (
                f"Within budget. "
                f"Remaining: INR {self.remaining:,.2f}"
            )

        return (
            f"Over budget by INR {-self.remaining:,.2f}. "
            "Consider cheaper flights, accommodation, "
            "or activities."
        )
