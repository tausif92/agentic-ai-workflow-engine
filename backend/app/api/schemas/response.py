from pydantic import BaseModel
from typing import Any, Dict, List


class WorkflowResponse(BaseModel):
    task: str
    final_output: str | None
    results: List[Dict[str, Any]]
    trace_id: str | None = None
