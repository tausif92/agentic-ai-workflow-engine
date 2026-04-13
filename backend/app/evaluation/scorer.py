from app.services.llm_service import LLMService


class Scorer:

    def __init__(self):
        self.llm = LLMService()

    async def score(self, task: str, output: str) -> dict:

        prompt = f"""
        You are an evaluation system.

        Evaluate the quality of the following response.

        Task:
        {task}

        Response:
        {output}

        Score on:
        - relevance (0-10)
        - completeness (0-10)
        - clarity (0-10)
        - correctness (0-10)

        Return ONLY JSON:
        {{
            "relevance": int,
            "completeness": int,
            "clarity": int,
            "correctness": int,
            "overall": int
        }}
        """

        messages = [
            {"role": "system", "content": "You are a strict evaluator."},
            {"role": "user", "content": prompt}
        ]

        response = await self.llm.generate(messages)

        from app.utils.llm_utils import parse_json_response
        return parse_json_response(response)
