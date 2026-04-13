from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService
from app.models.workflow_state import WorkflowState
from app.core.logging import get_logger


class WriterAgent(BaseAgent):
    """
    Generates final human-readable output (LangGraph-compatible)
    """

    def __init__(self):
        super().__init__(name="writer_agent")
        self.llm = LLMService()
        self.logger = get_logger("writer_agent")

    async def _run(self, state: WorkflowState) -> dict:
        """
        LangGraph entry point

        Input:
            state: WorkflowState

        Output:
            dict → partial state update
        """

        task = state.task
        analysis_data = state.analysis_data

        # 🔒 Guard: ensure upstream data exists
        if not analysis_data:
            self.logger.error("Missing analysis_data in state")
            raise ValueError(
                "No analysis_data available for report generation")

        self.logger.info("Generating final report")

        prompt = f"""
        You are a report generation assistant.

        Generate a professional report based on the following analysis.

        Task:
        {task}

        Analysis:
        {analysis_data}

        The report should include:
        - Summary
        - Key Findings
        - Recommendations
        - Conclusion

        Ensure the report is clear, concise, and well-structured.
        """

        messages = [
            {"role": "system", "content": "You are a professional report writer."},
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

        self.logger.info("Report generation completed")

        # ✅ LangGraph state update
        return {
            "final_output": response
        }
