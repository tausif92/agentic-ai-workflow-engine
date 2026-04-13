import asyncio
from app.models.workflow_state import WorkflowState
from app.workflows.langgraph_workflow import build_graph


async def test():

    graph = build_graph()

    state = WorkflowState(
        task="Generate weekly performance report"
    )

    result = await graph.ainvoke(state)

    print(result)


if __name__ == "__main__":
    asyncio.run(test())
