from langgraph.graph import StateGraph, END

from app.models.workflow_state import WorkflowState
from app.agents.planner_agent import PlannerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.writer_agent import WriterAgent


def build_graph():
    """
    Builds LangGraph workflow for Agentic AI system
    """

    # 🔹 Initialize agents
    planner = PlannerAgent()
    research = ResearchAgent()
    analysis = AnalysisAgent()
    writer = WriterAgent()

    # 🔹 Create graph
    builder = StateGraph(WorkflowState)

    # 🔹 Add nodes (LangGraph will call __call__)
    builder.add_node("planner", planner)
    builder.add_node("research", research)
    builder.add_node("analysis", analysis)
    builder.add_node("writer", writer)

    # 🔹 Define flow
    builder.set_entry_point("planner")

    builder.add_edge("planner", "research")
    builder.add_edge("research", "analysis")
    builder.add_edge("analysis", "writer")
    builder.add_edge("writer", END)

    # 🔹 Compile graph
    graph = builder.compile()

    return graph
