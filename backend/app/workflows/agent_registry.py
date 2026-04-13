from typing import Dict
from app.agents.planner_agent import PlannerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.writer_agent import WriterAgent


class AgentRegistry:
    """
    Maintains mapping of agent names → agent instances
    """

    def __init__(self):
        self.agents: Dict[str, object] = {
            "planner_agent": PlannerAgent(),
            "research_agent": ResearchAgent(),
            "analysis_agent": AnalysisAgent(),
            "writer_agent": WriterAgent(),
        }

    def get_agent(self, agent_name: str):
        agent = self.agents.get(agent_name)

        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")

        return agent
