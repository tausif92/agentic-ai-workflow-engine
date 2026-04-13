import asyncio
from app.workflows.orchestrator import WorkflowOrchestrator


async def test():
    orchestrator = WorkflowOrchestrator()

    result = await orchestrator.execute_workflow(
        "Generate weekly report for applications"
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(test())
