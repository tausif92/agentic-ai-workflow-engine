from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class WorkflowState(BaseModel):
    task: str

    plan: Optional[List[Dict[str, Any]]] = None

    research_data: Optional[str] = None
    analysis_data: Optional[str] = None
    final_output: Optional[str] = None

    # Optional (future extensions)
    conversation: Optional[List[Dict[str, Any]]] = None
    knowledge: Optional[List[str]] = None

    current_step: Optional[str] = None
    error: Optional[str] = None
