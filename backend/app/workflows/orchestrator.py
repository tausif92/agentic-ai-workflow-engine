from typing import Dict, Any, List

from app.core.logging import get_logger
from app.workflows.agent_registry import AgentRegistry
from app.agents.planner_agent import PlannerAgent
from app.memory.session_manager import SessionManager
from app.observability.tracer import Tracer
from app.evaluation.evaluator import Evaluator


class WorkflowOrchestrator:

    def __init__(self):
        self.logger = get_logger("orchestrator")
        self.registry = AgentRegistry()
        self.planner = PlannerAgent()
        self.memory = SessionManager()
        self.evaluator = Evaluator()

    async def execute_workflow(self, task: str) -> Dict[str, Any]:

        self.logger.info(f"Starting workflow: {task}")

        tracer = Tracer()

        # 🔹 Reset session
        self.memory.reset()

        # 🔹 Store user input
        self.memory.add_interaction("user", task)

        # 🔹 Retrieve memory context
        memory_context = self.memory.get_context(task)

        # 🔹 Shared context
        context: Dict[str, Any] = {
            "task": task,
            "conversation": memory_context.get("conversation", []),
            "knowledge": memory_context.get("knowledge", [])
        }

        results: List[Dict[str, Any]] = []
        plan = []

        # =========================
        # 🔹 STEP 1: PLANNER
        # =========================
        planner_step = tracer.start_step("planner_agent")

        try:
            planner_result = await self.planner.run(context)

            if planner_result.get("status") != "success":
                self.logger.error("Planner failed")
                tracer.end_step(planner_step, "failure")

                return {
                    "task": task,
                    "error": "Planner failed",
                    "trace": tracer.get_trace()
                }

            plan = planner_result.get("output", {}).get("plan", [])
            context["plan"] = plan

            tracer.end_step(planner_step, "success")

        except Exception as e:
            self.logger.error(f"Planner exception: {str(e)}")
            tracer.end_step(planner_step, "failure")

            return {
                "task": task,
                "error": str(e),
                "trace": tracer.get_trace()
            }

        # =========================
        # 🔹 STEP 2: EXECUTION
        # =========================
        for step in plan:

            step_num = step.get("step")
            agent_name = step.get("agent")
            step_task = step.get("task")

            self.logger.info(
                f"Step {step_num}: {agent_name} → {step_task}"
            )

            step_trace = tracer.start_step(agent_name)

            try:
                agent = self.registry.get_agent(agent_name)

                input_data = {
                    "task": step_task,
                    "context": context
                }

                result = await agent.run(input_data)

                if result.get("status") != "success":
                    self.logger.error(f"Step {step_num} failed")
                    tracer.end_step(step_trace, "failure")
                    break

                output = result.get("output", {})

                # 🔥 Update shared context
                self._update_context(agent_name, output, context)

                # 🔥 Store in memory
                self.memory.add_interaction("agent", str(output))
                self.memory.store_knowledge(str(output))

                results.append({
                    "step": step_num,
                    "agent": agent_name,
                    "output": output
                })

                tracer.end_step(step_trace, "success")

            except Exception as e:
                self.logger.error(f"Error in step {step_num}: {str(e)}")
                tracer.end_step(step_trace, "failure")
                break

        # =========================
        # 🔹 EVALUATION
        # =========================
        evaluation = None

        final_output = context.get("final_output")

        if final_output:
            try:
                evaluation = await self.evaluator.evaluate(task, final_output)

                # 🔥 Auto-improvement hook
                if evaluation.get("overall", 10) < 6:
                    self.logger.warning("Low quality response detected")

                    self.memory.store_knowledge(
                        f"Poor response example: {final_output}"
                    )

            except Exception as e:
                self.logger.error(f"Evaluation failed: {str(e)}")

        # =========================
        # 🔹 FINAL RESPONSE
        # =========================
        return {
            "task": task,
            "results": results,
            "final_output": final_output,
            "evaluation": evaluation,
            "memory_used": {
                "conversation": context.get("conversation"),
                "knowledge": context.get("knowledge")
            },
            "trace": tracer.get_trace()
        }

    def _update_context(self, agent_name: str, output: Dict, context: Dict):

        if agent_name == "research_agent":
            context["research_data"] = output.get("insights")

        elif agent_name == "analysis_agent":
            context["analysis_data"] = output.get("analysis")

        elif agent_name == "writer_agent":
            context["final_output"] = output.get("report")
