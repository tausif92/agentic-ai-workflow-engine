from typing import List, Dict, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.core.config import settings
from app.core.logging import get_logger
from app.core.retry import retry_async

from app.guardrails.input_guard import validate_input
from app.guardrails.output_guard import validate_output

from app.observability.llm_logger import LLMLogger
from app.observability.metrics import Metrics


class LLMService:
    """
    Handles all LLM interactions with:
    - LangSmith tracing
    - Guardrails
    - Retry logic
    - Metrics
    - Custom logging
    """

    def __init__(self):
        self.model = settings.MODEL_NAME
        self.logger = get_logger("llm_service")

        # ✅ LangChain LLM (enables LangSmith tracing automatically)
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=0.3
        )

        # 🔥 Observability (your custom layer)
        self.llm_logger = LLMLogger()
        self.metrics = Metrics()

    async def generate(
        self,
        messages: List[Dict],
        temperature: float = 0.3,
        max_tokens: int = 1000,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        source: str = "internal"   # 🔥 NEW
    ) -> str:

        # =========================
        # 🔐 INPUT GUARD
        # =========================
        user_message = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            ""
        )

        # 🔐 Apply guard ONLY for user input
        if source == "user":
            validate_input({"task": user_message})

        # =========================
        # 🔍 CUSTOM LOGGING (REQUEST)
        # =========================
        log_data = self.llm_logger.log_request(messages)

        # =========================
        # 🔄 CONVERT TO LANGCHAIN FORMAT
        # =========================
        lc_messages = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))

        # =========================
        # 🔁 LLM CALL WITH RETRY
        # =========================
        async def _call_llm():
            self.logger.info("Calling LLM...")

            response = await self.llm.ainvoke(
                lc_messages,
                config={
                    "tags": tags or ["llm_call"],
                    "metadata": metadata or {}
                }
            )

            return response.content

        try:
            content = await retry_async(_call_llm, retries=3)

            # =========================
            # 🛡️ OUTPUT GUARD
            # =========================
            validate_output(content)

            # =========================
            # 🔍 CUSTOM LOGGING (RESPONSE)
            # =========================
            log_data = self.llm_logger.log_response(log_data, content)
            duration = log_data.get("duration", 0)

            # =========================
            # 📊 METRICS
            # =========================
            self.metrics.record_success()
            self.metrics.record_latency(duration)

            self.logger.info(
                f"LLM success | duration={duration:.2f}s"
            )

            return content

        except Exception as e:
            self.metrics.record_failure()
            self.logger.error(f"LLM call failed: {str(e)}")
            raise
