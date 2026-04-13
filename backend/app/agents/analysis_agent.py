from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService
from app.models.workflow_state import WorkflowState
from app.core.logging import get_logger


class AnalysisAgent(BaseAgent):
    """
    Analyzes research data to extract insights and patterns (LangGraph-compatible)
    """

    def __init__(self):
        super().__init__(name="analysis_agent")
        self.llm = LLMService()
        self.logger = get_logger("analysis_agent")

    async def _run(self, state: WorkflowState) -> dict:
        """
        LangGraph entry point

        Input:
            state: WorkflowState

        Output:
            dict → partial state update
        """

        task = state.task
        research_data = state.research_data

        # 🔒 Guard: ensure upstream data exists
        if not research_data:
            self.logger.error("Missing research_data in state")
            raise ValueError("No research_data available for analysis")

        self.logger.info("Starting analysis on research data")

        prompt = f"""
        You are a data analyst.

        Analyze the following data and extract:

        - Key insights
        - Trends
        - Anomalies
        - Recommendations

        Task:
        {task}

        Data:
        {research_data}

        Return structured analysis.
        """

        messages = [
            {"role": "system", "content": "You are an expert data analyst."},
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

        self.logger.info("Analysis completed")

        # ✅ Return partial state update (LangGraph style)
        return {
            "analysis_data": response
        }
