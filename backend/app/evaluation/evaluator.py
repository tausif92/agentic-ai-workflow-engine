from app.evaluation.scorer import Scorer
from app.evaluation.feedback_store import FeedbackStore


class Evaluator:

    def __init__(self):
        self.scorer = Scorer()
        self.store = FeedbackStore()

    async def evaluate(self, task: str, output: str):

        scores = await self.scorer.score(task, output)

        record = {
            "task": task,
            "output": output,
            "scores": scores
        }

        self.store.add(record)

        return scores
