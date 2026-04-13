import json


def clean_json_response(response: str) -> str:
    if not response:
        raise ValueError("Empty response from LLM")

    cleaned = response.strip()

    # Remove markdown code blocks
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    return cleaned


def parse_json_response(response: str):
    cleaned = clean_json_response(response)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {cleaned}") from e
