from fastapi import APIRouter, HTTPException
from app.api.schemas.request import WorkflowRequest
from app.api.schemas.response import WorkflowResponse

from app.workflows.langgraph_workflow import build_graph
from app.models.workflow_state import WorkflowState

import asyncio

router = APIRouter()

# 🔥 Build graph once (singleton pattern)
graph = build_graph()


@router.post("/run", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest):

    try:
        initial_state = WorkflowState(task=request.task)

        result = await asyncio.wait_for(
            graph.ainvoke(
                initial_state,
                config={
                    "tags": ["api", "workflow"],
                    "metadata": {
                        "source": "api",
                        "task": request.task
                    }
                }
            ),
            timeout=60
        )

        return WorkflowResponse(
            task=request.task,
            final_output=result.get("final_output"),
            results=[],
            trace_id=None
        )

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Workflow timeout")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
