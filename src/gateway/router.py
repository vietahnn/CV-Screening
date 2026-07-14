from gateway.config import model_list, fallbacks
from gateway.cost_tracker import log_call
from litellm import Router

class LLMGateway:
    def __init__(self):
        self.router = Router(model_list= model_list, fallbacks=fallbacks)

    def call_llm(self, role: str ,messages: list[dict], format):
        response = self.router.completion(
            model = role,
            messages =  messages,
            response_format=format,
            temperature = 0
        )
        log_call(role, response)
        return response


gateway = LLMGateway()

