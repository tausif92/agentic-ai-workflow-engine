import uuid
import time
from typing import Dict, Any


class Tracer:

    def __init__(self):
        self.trace_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.steps = []

    def start_step(self, name: str):
        return {
            "name": name,
            "start_time": time.time()
        }

    def end_step(self, step: Dict[str, Any], status: str = "success"):
        step["end_time"] = time.time()
        step["duration"] = step["end_time"] - step["start_time"]
        step["status"] = status

        self.steps.append(step)

    def get_trace(self):
        return {
            "trace_id": self.trace_id,
            "total_duration": time.time() - self.start_time,
            "steps": self.steps
        }
