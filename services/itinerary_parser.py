
import json

from pydantic import ValidationError

from models.itinerary_response import ItineraryResponse


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


def parse_itinerary(output):
    text = extract_text(output).strip()

    if not text:
        raise ValueError("The agent returned an empty response.")

    # Accept JSON enclosed in a Markdown code fence.
    if text.startswith("```"):
        lines = text.splitlines()

        if len(lines) >= 3 and lines[-1].strip() == "```":
            text = "\n".join(lines[1:-1]).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "The agent did not return valid structured JSON."
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "Expected a JSON object containing itinerary data."
        )

    try:
        return ItineraryResponse.model_validate(data)
    except ValidationError as exc:
        raise ValueError(
            "The agent returned invalid itinerary fields."
        ) from exc
