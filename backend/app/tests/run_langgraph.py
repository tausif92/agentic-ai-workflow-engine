import asyncio
from app.workflows.langgraph_workflow import build_graph
from app.models.workflow_state import WorkflowState


async def main():
    # 🔹 Build graph
    graph = build_graph()

    # 🔹 Initial state
    initial_state = WorkflowState(
        task="Analyze application performance and generate report"
    )

    # 🔹 Execute workflow
    result = await graph.ainvoke(initial_state)

    print("\n✅ FINAL OUTPUT:\n")
    print(result.get("final_output"))

    print("\n📊 FULL STATE:\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
