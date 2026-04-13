from typing import Dict, Any

from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory


class SessionManager:
    """
    Central memory manager:
    - Handles short-term (conversation)
    - Handles long-term (vector DB)
    - Provides unified interface to orchestrator
    """

    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()

    # =========================
    # 🔹 SHORT-TERM MEMORY
    # =========================

    def add_interaction(self, role: str, content: str):
        """
        Store conversation step
        """
        if not content:
            return

        self.short_term.add(role, content)

    def get_conversation(self):
        return self.short_term.get()

    # =========================
    # 🔹 LONG-TERM MEMORY
    # =========================

    def store_knowledge(self, text: str):
        """
        Store knowledge in vector DB
        """
        if not text:
            return

        self.long_term.store(text)

    def retrieve_knowledge(self, query: str):
        """
        Retrieve relevant knowledge
        """
        if not query:
            return []

        return self.long_term.retrieve(query)

    # =========================
    # 🔹 COMBINED CONTEXT
    # =========================

    def get_context(self, query: str) -> Dict[str, Any]:
        """
        Returns combined memory context for agents
        """

        return {
            "conversation": self.get_conversation(),
            "knowledge": self.retrieve_knowledge(query)
        }

    # =========================
    # 🔹 RESET SESSION
    # =========================

    def reset(self):
        """
        Clears short-term memory (new session)
        """
        self.short_term.clear()
