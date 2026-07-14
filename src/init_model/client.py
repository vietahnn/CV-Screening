from langchain.chat_models import init_chat_model
class LLM_Client():
    def __init__(self, model_name, provider, temperature = 0):
        self.model_name = model_name
        self.provider = provider
        self.temperature = temperature

    def get_model(self):
        model = init_chat_model(
            model= f"{self.provider}:{self.model_name}",
            temperature = self.temperature
        )

        return model