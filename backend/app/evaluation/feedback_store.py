from typing import List, Dict


class FeedbackStore:
    """
    Stores evaluation results (in-memory for now)
    """

    def __init__(self):
        self.data: List[Dict] = []

    def add(self, record: Dict):
        self.data.append(record)

    def get_all(self):
        return self.data

    def get_low_scores(self, threshold: int = 5):
        return [
            r for r in self.data
            if r.get("scores", {}).get("overall", 10) < threshold
        ]
