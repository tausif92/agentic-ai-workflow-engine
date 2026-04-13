from typing import Dict, Any, List
from app.core.logging import get_logger
from app.workflows.agent_registry import AgentRegistry
from app.agents.planner_agent import PlannerAgent


class WorkflowOrchestrator:
    """
    Executes multi-step workflows using agents
    """

    def __init__(self):
        self.logger = get_logger("orchestrator")
        self.registry = AgentRegistry()
        self.planner = PlannerAgent()

    async def execute_workflow(self, task: str) -> Dict[str, Any]:
        """
        Main workflow execution entry
        """

        self.logger.info(f"Starting workflow for task: {task}")

        # Step 1: Generate plan
        planner_result = await self.planner.run({"task": task})

        if planner_result["status"] != "success":
            return planner_result

        plan = planner_result["output"]["plan"]

        results: List[Dict[str, Any]] = []

        # Step 2: Execute each step
        context = {}
        for step in plan:
            step_num = step.get("step")
            agent_name = step.get("agent")
            step_task = step.get("task")

            self.logger.info(
                f"Executing Step {step_num}: {agent_name} → {step_task}")

            try:
                agent = self.registry.get_agent(agent_name)

                # 🔥 Build input dynamically
                input_data = {
                    "task": step_task,
                    **context  # pass previous outputs
                }

                result = await agent.run(input_data)

                if result["status"] != "success":
                    self.logger.error(f"Step {step_num} failed")
                    break

                output = result["output"]

                # 🔥 Update context for next agents
                if agent_name == "research_agent":
                    context["research_data"] = output.get("insights")

                elif agent_name == "analysis_agent":
                    context["analysis_data"] = output.get("analysis")

                elif agent_name == "writer_agent":
                    context["final_report"] = output.get("report")

                results.append({
                    "step": step_num,
                    "agent": agent_name,
                    "result": result
                })

            except Exception as e:
                self.logger.error(f"Error in step {step_num}: {str(e)}")
                break

        self.logger.info("Workflow execution completed")

        return {
            "task": task,
            "steps_executed": len(results),
            "results": results
        }
