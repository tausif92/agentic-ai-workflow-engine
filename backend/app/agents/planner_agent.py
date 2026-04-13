from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService
from app.utils.llm_utils import parse_json_response
from app.models.workflow_state import WorkflowState
from app.core.logging import get_logger


class PlannerAgent(BaseAgent):
    """
    Generates execution plan for the workflow (LangGraph-compatible)
    """

    def __init__(self):
        super().__init__(name="planner_agent")
        self.llm = LLMService()
        self.logger = get_logger("planner_agent")

    async def _run(self, state: WorkflowState) -> dict:
        """
        LangGraph entry point

        Input:
            state: WorkflowState

        Output:
            dict → partial state update
        """

        task = state.task

        prompt = f"""
        You are an AI planning agent.

        Break down the task using ONLY these agents:
        1. research_agent
        2. analysis_agent
        3. writer_agent

        Flow:
        - research_agent → gather data
        - analysis_agent → analyze data
        - writer_agent → generate report

        IMPORTANT:
        - Return ONLY valid JSON
        - Do NOT include explanations
        - Do NOT include markdown (no ```)

        Format:
        [
            {{"step": 1, "agent": "research_agent", "task": "..."}},
            {{"step": 2, "agent": "analysis_agent", "task": "..."}},
            {{"step": 3, "agent": "writer_agent", "task": "..."}}
        ]

        Task:
        {task}
        """

        messages = [
            {"role": "system", "content": "You are a helpful AI planner."},
            {"role": "user", "content": prompt}
        ]

        response = await self.llm.generate(messages,
                                           source="user",   # 🔥 IMPORTANT
                                           metadata={
                                               "agent": "planner_agent",
                                               "step": "planning",
                                               "task": task
                                           },
                                           tags=["planner"])

        self.logger.info(f"Raw LLM response: {response}")

        try:
            plan = parse_json_response(response)
        except Exception:
            self.logger.error("Failed to parse LLM response as JSON")
            raise

        # ✅ LangGraph expects partial state update
        return {
            "plan": plan
        }
