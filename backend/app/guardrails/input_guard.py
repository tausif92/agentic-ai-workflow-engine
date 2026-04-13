from typing import Dict, Any
from app.guardrails.injection_detector import detect_prompt_injection


def validate_input(input_data: Dict[str, Any]) -> None:
    """
    Validates incoming input before sending to LLM
    """

    if not input_data:
        raise ValueError("Input data is empty")

    task = input_data.get("task")

    if not task or not isinstance(task, str):
        raise ValueError("Invalid or missing 'task' in input")

    if len(task.strip()) < 3:
        raise ValueError("Task is too short")

    # 🔐 Prompt Injection Detection
    if detect_prompt_injection(task):
        raise ValueError("Potential prompt injection detected in input")
