
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class TripRequest(BaseModel):
    source: str = Field(min_length=2, max_length=100)
    destination: str = Field(min_length=2, max_length=100)

    departure_date: date

    num_days: int = Field(ge=1, le=14)
    travelers: int = Field(ge=1, le=20)
    budget: float = Field(gt=0)

    travel_style: Literal[
        "budget",
        "balanced",
        "luxury"
    ] = "balanced"

    interests: list[str] = Field(
        default_factory=list,
        max_length=10
    )

    @field_validator("source", "destination")
    @classmethod
    def clean_city(cls, value: str) -> str:
        value = " ".join(value.split())

        if len(value) < 2:
            raise ValueError(
                "City must contain at least 2 characters."
            )

        return value

    @field_validator("interests")
    @classmethod
    def clean_interests(cls, values: list[str]) -> list[str]:
        cleaned = [
            item.strip()
            for item in values
            if item.strip()
        ]

        return list(dict.fromkeys(cleaned))

    @model_validator(mode="after")
    def validate_trip(self):
        if self.source.casefold() == self.destination.casefold():
            raise ValueError(
                "Source and destination must be different."
            )

        if self.departure_date < date.today():
            raise ValueError(
                "Departure date cannot be in the past."
            )

        return self

    def to_agent_prompt(self) -> str:
        interests_text = (
            ", ".join(self.interests)
            if self.interests
            else "General sightseeing"
        )

        return (
            f"Plan a {self.num_days}-day trip from "
            f"{self.source} to {self.destination}.\n"
            f"Departure date: {self.departure_date.isoformat()}\n"
            f"Travelers: {self.travelers}\n"
            f"Total budget: INR {self.budget:,.0f}\n"
            f"Travel style: {self.travel_style}\n"
            f"Interests: {interests_text}\n\n"
            "Provide a day-wise itinerary, suitable flights, "
            "hotel recommendations, weather information, "
            "attractions, and a budget breakdown. "
            "Clearly distinguish verified information "
            "from estimates. Do not invent booking availability."
        )
