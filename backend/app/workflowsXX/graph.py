"""
LangGraph workflow definition for agent orchestration
"""

from typing import Dict, Any, Literal, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver
from datetime import datetime
import uuid

from app.workflowsXX.state import WorkflowState, WorkflowStep, StepStatus, WorkflowStatus
from app.workflows.agent_registry import AgentRegistry
from app.core.logging import get_logger
from app.observability.tracer import tracer
from app.observability.metrics import metrics

logger = get_logger("workflow_graph")


class WorkflowGraphBuilder:
    """
    Builds and manages LangGraph workflow for agent orchestration
    """

    def __init__(self):
        self.registry = AgentRegistry()
        self.logger = logger
        self.graph = None
        self.app = None

    def build_graph(self) -> StateGraph:
        """
        Construct the workflow graph with all nodes and edges
        """
        # Create graph with WorkflowState schema
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("planner", self._planning_node)
        workflow.add_node("executor", self._execution_node)
        workflow.add_node("validator", self._validation_node)
        workflow.add_node("finalizer", self._finalization_node)

        # Add conditional edges
        workflow.set_entry_point("planner")

        # Planner -> conditional branch
        workflow.add_conditional_edges(
            "planner",
            self._after_planning,
            {
                "execute": "executor",
                "fail": END
            }
        )

        # Executor -> conditional branch
        workflow.add_conditional_edges(
            "executor",
            self._after_execution,
            {
                "continue": "executor",  # Loop back for next step
                "validate": "validator",
                "fail": END
            }
        )

        # Validator -> finalizer
        workflow.add_edge("validator", "finalizer")
        workflow.add_edge("finalizer", END)

        return workflow

    async def _planning_node(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Node: Generate workflow plan using PlannerAgent
        """
        self.logger.info(f"Planning workflow for task: {state.original_task}")

        # Start trace span
        span_id = tracer.start_span(
            operation="workflow_planning",
            metadata={"task": state.original_task[:100]}
        )

        try:
            # Update state
            state.status = WorkflowStatus.PLANNING
            state.started_at = datetime.now()

            # Get planner agent
            planner = self.registry.get_agent("planner_agent")

            # Execute planning
            result = await planner.run({"task": state.original_task})

            if result["status"] != "success":
                raise Exception(
                    f"Planning failed: {result.get('error', 'Unknown error')}")

            # Convert plan to WorkflowStep objects
            plan_data = result["output"].get("plan", [])

            steps = []
            for idx, step_data in enumerate(plan_data):
                step = WorkflowStep(
                    step_id=str(uuid.uuid4()),
                    step_number=idx + 1,
                    agent_name=step_data.get("agent", "unknown"),
                    task=step_data.get("task", ""),
                    max_retries=3
                )
                steps.append(step)

            state.plan = steps
            state.status = WorkflowStatus.EXECUTING

            self.logger.info(f"Created plan with {len(steps)} steps")

            tracer.end_span(span_id, status="success")

            return {
                "plan": steps,
                "status": WorkflowStatus.EXECUTING,
                "updated_at": datetime.now()
            }

        except Exception as e:
            self.logger.error(f"Planning failed: {str(e)}")
            state.error = str(e)
            state.status = WorkflowStatus.FAILED

            tracer.end_span(span_id, status="error")
            metrics.record_agent_execution("planner", 0, success=False)

            return {
                "error": str(e),
                "status": WorkflowStatus.FAILED,
                "updated_at": datetime.now()
            }

    async def _execution_node(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Node: Execute current workflow step
        """
        current_step = state.get_current_step()

        if not current_step:
            self.logger.warning("No current step to execute")
            return {"status": WorkflowStatus.COMPLETED}

        self.logger.info(
            f"Executing step {current_step.step_number}/{len(state.plan)}: "
            f"{current_step.agent_name} - {current_step.task[:50]}..."
        )

        # Start trace span
        span_id = tracer.start_span(
            operation=f"step_{current_step.step_number}_{current_step.agent_name}",
            metadata={
                "step_id": current_step.step_id,
                "agent": current_step.agent_name,
                "task": current_step.task[:100]
            }
        )

        try:
            # Mark step as started
            current_step.start()

            # Prepare input with context
            input_data = {
                "task": current_step.task,
                **state.context  # Pass accumulated context
            }

            # Get agent
            agent = self.registry.get_agent(current_step.agent_name)

            # Execute agent
            result = await agent.run(input_data)

            if result["status"] == "success":
                # Step completed successfully
                current_step.complete(result.get("output", {}))

                # Update context with this step's output
                output_data = result.get("output", {})
                state.context[current_step.agent_name] = output_data

                # Store result
                state.results.append({
                    "step": current_step.step_number,
                    "agent": current_step.agent_name,
                    "status": "success",
                    "output": output_data
                })

                self.logger.info(
                    f"Step {current_step.step_number} completed successfully")

                tracer.end_span(span_id, status="success")

                # Move to next step
                has_more = state.advance_to_next_step()

                return {
                    "context": state.context,
                    "results": state.results,
                    "current_step_index": state.current_step_index,
                    "updated_at": datetime.now()
                }
            else:
                # Step failed
                error_msg = result.get("error", "Unknown error")
                current_step.fail(error_msg)

                self.logger.error(
                    f"Step {current_step.step_number} failed: {error_msg}")

                tracer.end_span(span_id, status="error")

                return {
                    "error": error_msg,
                    "status": WorkflowStatus.FAILED,
                    "updated_at": datetime.now()
                }

        except Exception as e:
            error_msg = str(e)
            current_step.fail(error_msg)

            self.logger.error(
                f"Step {current_step.step_number} exception: {error_msg}")

            tracer.end_span(span_id, status="error")

            return {
                "error": error_msg,
                "status": WorkflowStatus.FAILED,
                "updated_at": datetime.now()
            }

    async def _validation_node(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Node: Validate final output
        """
        self.logger.info("Validating workflow output")

        # Simple validation - can be extended
        if state.results:
            final_step = state.results[-1]
            if final_step.get("status") == "success":
                # Extract final output from writer agent
                writer_output = state.context.get("writer_agent", {})
                final_output = writer_output.get("report", str(writer_output))

                state.final_output = final_output
                state.status = WorkflowStatus.COMPLETED
                state.completed_at = datetime.now()

                # Calculate total duration
                if state.started_at:
                    total_duration = (state.completed_at -
                                      state.started_at).total_seconds() * 1000
                    metrics.record_workflow_execution(total_duration)

                self.logger.info("Workflow validation passed")

                return {
                    "final_output": final_output,
                    "status": WorkflowStatus.COMPLETED,
                    "completed_at": state.completed_at
                }

        state.status = WorkflowStatus.FAILED
        state.error = "Validation failed: No valid output generated"

        return {
            "status": WorkflowStatus.FAILED,
            "error": state.error,
            "updated_at": datetime.now()
        }

    async def _finalization_node(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Node: Cleanup and final logging
        """
        self.logger.info(f"Workflow finalized with status: {state.status}")

        # Log metrics summary
        steps_completed = sum(
            1 for step in state.plan if step.status == StepStatus.COMPLETED)
        steps_failed = sum(
            1 for step in state.plan if step.status == StepStatus.FAILED)

        self.logger.info(
            f"Workflow stats - Completed: {steps_completed}, Failed: {steps_failed}, "
            f"Total steps: {len(state.plan)}"
        )

        return {
            "updated_at": datetime.now()
        }

    def _after_planning(self, state: WorkflowState) -> Literal["execute", "fail"]:
        """
        Conditional edge: Decide next step after planning
        """
        if state.status == WorkflowStatus.FAILED or state.error:
            return "fail"
        return "execute"

    def _after_execution(self, state: WorkflowState) -> Literal["continue", "validate", "fail"]:
        """
        Conditional edge: Decide next step after execution
        """
        if state.status == WorkflowStatus.FAILED:
            return "fail"

        if state.is_complete():
            return "validate"

        # More steps to execute
        return "continue"

    def compile(self, checkpoint: bool = True):
        """
        Compile the workflow graph
        """
        graph = self.build_graph()

        if checkpoint:
            # Add memory for state persistence
            memory = MemorySaver()
            self.app = graph.compile(checkpointer=memory)
        else:
            self.app = graph.compile()

        return self.app


def create_workflow_engine(with_checkpoint: bool = True):
    """
    Factory function to create workflow engine
    """
    builder = WorkflowGraphBuilder()
    return builder.compile(checkpoint=with_checkpoint)
