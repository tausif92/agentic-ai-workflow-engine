from typing import List, Dict


class ShortTermMemory:
    """
    Stores conversation history for a session
    """

    def __init__(self):
        self.messages: List[Dict] = []

    def add(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content
        })

    def get(self) -> List[Dict]:
        return self.messages

    def clear(self):
        self.messages = []
