from pydantic import BaseModel


class WorkflowRequest(BaseModel):
    task: str
