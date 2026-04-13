import re


SUSPICIOUS_PATTERNS = [
    r"ignore previous instructions",
    r"disregard above",
    r"system prompt",
    r"act as",
    r"you are now",
    r"override instructions",
    r"bypass",
]


def detect_prompt_injection(text: str) -> bool:
    """
    Detects common prompt injection patterns
    """

    if not text:
        return False

    text = text.lower()

    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text):
            return True

    return False
