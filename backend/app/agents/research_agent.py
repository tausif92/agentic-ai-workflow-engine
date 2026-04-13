from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService
from app.models.workflow_state import WorkflowState
from app.core.logging import get_logger


class ResearchAgent(BaseAgent):
    """
    Fetches and prepares data required for downstream agents (LangGraph-compatible)
    """

    def __init__(self):
        super().__init__(name="research_agent")
        self.llm = LLMService()
        self.logger = get_logger("research_agent")

    async def _run(self, state: WorkflowState) -> dict:
        """
        LangGraph entry point

        Input:
            state: WorkflowState

        Output:
            dict → partial state update
        """

        task = state.task

        # 🔹 Step 1: Fetch data (currently mock, can be replaced with APIs/DB)
        raw_data = self._fetch_mock_data(task)

        self.logger.info("Fetched raw data for research")

        # 🔹 Step 2: Use LLM to extract insights
        prompt = f"""
        You are a research assistant.

        Task:
        {task}

        Data:
        {raw_data}

        Extract:
        - key insights
        - important signals
        - anything relevant for downstream analysis

        Keep response structured and concise.
        """

        messages = [
            {"role": "system", "content": "You are a helpful research assistant."},
            {"role": "user", "content": prompt}
        ]

        response = await self.llm.generate(messages,
                                           source="internal",
                                           metadata={
                                               "agent": "planner_agent",
                                               "step": "planning",
                                               "task": task
                                           },
                                           tags=["planner"])

        self.logger.info("Research insights generated")

        # ✅ Return partial state update
        return {
            "research_data": response
        }

    def _fetch_mock_data(self, task: str) -> str:
        """
        Simulated data source (replace with real integrations later)
        """

        return f"""
        - Application A uptime: 99.5%
        - Application B uptime: 97.2%
        - Incident count: 12
        - Critical alerts: 3
        - Performance latency increased by 15%
        - Task context: {task}
        """
