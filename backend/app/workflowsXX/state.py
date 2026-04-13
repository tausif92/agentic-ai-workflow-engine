"""
Pydantic models for workflow state management
Enables type safety, validation, and serialization
"""

from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class StepStatus(str, Enum):
    """Status of individual workflow step"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class WorkflowStatus(str, Enum):
    """Overall workflow status"""
    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class WorkflowStep(BaseModel):
    """
    Represents a single step in the workflow
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    step_id: str = Field(description="Unique step identifier")
    step_number: int = Field(description="Order in workflow")
    agent_name: str = Field(description="Agent to execute")
    task: str = Field(description="Task description for agent")
    status: StepStatus = Field(default=StepStatus.PENDING)

    # Execution results
    input_data: Optional[Dict[str, Any]] = Field(default=None)
    output: Optional[Dict[str, Any]] = Field(default=None)
    error: Optional[str] = Field(default=None)

    # Timing
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    duration_ms: Optional[float] = Field(default=None)

    # Retry information
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)

    def start(self) -> None:
        """Mark step as started"""
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now()

    def complete(self, output: Dict[str, Any]) -> None:
        """Mark step as completed with output"""
        self.status = StepStatus.COMPLETED
        self.completed_at = datetime.now()
        self.output = output
        if self.started_at:
            self.duration_ms = (self.completed_at -
                                self.started_at).total_seconds() * 1000

    def fail(self, error: str) -> None:
        """Mark step as failed"""
        self.status = StepStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
        if self.started_at:
            self.duration_ms = (self.completed_at -
                                self.started_at).total_seconds() * 1000


class WorkflowResult(BaseModel):
    """
    Final result of workflow execution
    """
    success: bool
    final_output: Optional[str] = None
    error: Optional[str] = None
    total_duration_ms: Optional[float] = None
    steps_completed: int = 0
    steps_failed: int = 0


class WorkflowState(BaseModel):
    """
    Complete workflow state for LangGraph
    This is the single source of truth for workflow execution
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Metadata
    workflow_id: str = Field(description="Unique workflow identifier")
    status: WorkflowStatus = Field(default=WorkflowStatus.CREATED)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Task and planning
    original_task: str = Field(description="User's original request")
    plan: List[WorkflowStep] = Field(default_factory=list)
    current_step_index: int = Field(default=0)

    # Context and data sharing between steps
    context: Dict[str, Any] = Field(default_factory=dict)

    # Execution results
    results: List[Dict[str, Any]] = Field(default_factory=list)
    final_output: Optional[str] = None

    # Error handling
    error: Optional[str] = Field(default=None)
    retry_count: int = Field(default=0)

    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def get_current_step(self) -> Optional[WorkflowStep]:
        """Get the current step being executed"""
        if 0 <= self.current_step_index < len(self.plan):
            return self.plan[self.current_step_index]
        return None

    def advance_to_next_step(self) -> bool:
        """Move to next step, returns True if more steps remain"""
        self.current_step_index += 1
        self.updated_at = datetime.now()
        return self.current_step_index < len(self.plan)

    def is_complete(self) -> bool:
        """Check if all steps are complete"""
        return all(
            step.status in [StepStatus.COMPLETED,
                            StepStatus.SKIPPED, StepStatus.FAILED]
            for step in self.plan
        )

    def get_step_by_id(self, step_id: str) -> Optional[WorkflowStep]:
        """Find a step by its ID"""
        for step in self.plan:
            if step.step_id == step_id:
                return step
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """Create from dictionary"""
        return cls(**data)
