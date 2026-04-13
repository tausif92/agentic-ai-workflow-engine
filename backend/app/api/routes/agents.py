from fastapi import APIRouter

from app.agents.planner_agent import PlannerAgent
from app.models.workflow_state import WorkflowState

router = APIRouter()


@router.post("/planner")
async def run_planner(task: str):

    agent = PlannerAgent()

    state = WorkflowState(task=task)

    result = await agent(state)

    return result
