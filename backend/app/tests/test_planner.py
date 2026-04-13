import asyncio
from app.agents.planner_agent import PlannerAgent


async def test():
    agent = PlannerAgent()

    result = await agent.run({
        "task": "Generate weekly report for applications"
    })

    print(result)


if __name__ == "__main__":
    asyncio.run(test())
