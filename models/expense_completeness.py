
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


ExpenseCategory = Literal[
    "flights",
    "accommodation",
    "food",
    "local_transport",
    "activities",
    "other",
]


class ExpenseCompleteness(BaseModel):
    missing_categories: list[ExpenseCategory] = Field(
        default_factory=list
    )

    notes: list[str] = Field(default_factory=list)

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value):
        if isinstance(value, str):
            return [value] if value.strip() else []

        return value

    @model_validator(mode="after")
    def remove_duplicates(self):
        self.missing_categories = list(
            dict.fromkeys(self.missing_categories)
        )
        return self

    @property
    def is_complete(self) -> bool:
        return len(self.missing_categories) == 0

    def warning_message(self) -> str:
        if self.is_complete:
            return "All expense categories are accounted for."

        categories = ", ".join(
            category.replace("_", " ").title()
            for category in self.missing_categories
        )

        return (
            f"Incomplete budget estimate. "
            f"Missing costs: {categories}. "
            "The final trip cost may be higher."
        )
