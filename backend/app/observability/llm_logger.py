import time


class LLMLogger:

    def log_request(self, messages):
        return {
            "messages": messages,
            "start_time": time.time()
        }

    def log_response(self, log_data, response):
        log_data["end_time"] = time.time()
        log_data["duration"] = log_data["end_time"] - log_data["start_time"]
        log_data["response"] = response

        return log_data
