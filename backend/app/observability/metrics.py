from collections import defaultdict


class Metrics:

    def __init__(self):
        self.data = defaultdict(int)
        self.latencies = []

    def record_success(self):
        self.data["success"] += 1

    def record_failure(self):
        self.data["failure"] += 1

    def record_latency(self, duration: float):
        self.latencies.append(duration)

    def summary(self):
        avg_latency = (
            sum(self.latencies) / len(self.latencies)
            if self.latencies else 0
        )

        return {
            "success": self.data["success"],
            "failure": self.data["failure"],
            "avg_latency": avg_latency
        }
