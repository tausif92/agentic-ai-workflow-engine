import json


def validate_non_empty(output: str) -> None:
    if not output or not output.strip():
        raise ValueError("LLM output is empty")


def validate_length(output: str, min_length: int = 10) -> None:
    if len(output.strip()) < min_length:
        raise ValueError("LLM output is too short")


def validate_json(output: str) -> None:
    try:
        json.loads(output)
    except Exception:
        raise ValueError("Invalid JSON output from LLM")


def validate_output(output: str) -> None:
    """
    Combined output validation
    """

    validate_non_empty(output)
    validate_length(output)
