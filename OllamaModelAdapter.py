import ollama


class OllamaModelAdapter:

    def __init__(self, model, temperature=None, max_tokens=None):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt):
        options = {}

        if self.temperature is not None:
            options["temperature"] = self.temperature

        if self.max_tokens is not None:
            options["num_predict"] = self.max_tokens

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options=options or None,
        )

        return response["message"]["content"]
