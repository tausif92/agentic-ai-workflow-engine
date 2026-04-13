from abc import ABC, abstractmethod
from typing import Dict, Any
from app.core.logging import get_logger
from app.models.workflow_state import WorkflowState


class BaseAgent(ABC):
    """
    Base class for all LangGraph-compatible agents.

    Enforces:
    - __call__(state) entry point
    - centralized logging
    - error handling
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(name)

    @abstractmethod
    async def _run(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Core logic of the agent.
        Must return partial state update (dict).
        """
        pass

    async def __call__(self, state: WorkflowState) -> Dict[str, Any]:
        """
        LangGraph entry point.
        Handles logging + error management.
        """

        self.logger.info(f"Agent '{self.name}' started execution")

        try:
            result = await self._run(state)

            if not isinstance(result, dict):
                raise ValueError(
                    f"{self.name} must return dict, got {type(result)}"
                )

            self.logger.info(f"Agent '{self.name}' completed execution")

            return result

        except Exception as e:
            self.logger.error(f"Agent '{self.name}' failed: {str(e)}")

            # 🔥 Important: raise error so LangGraph captures it in trace
            raise
