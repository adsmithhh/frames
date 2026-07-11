import json
import os
from urllib import error, request


class OpenAiModelAdapter:

    def __init__(
        self,
        model,
        temperature=None,
        max_tokens=None,
        api_key_env=None,
        base_url=None,
        timeout=60,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key_env = api_key_env or "OPENAI_API_KEY"
        self.base_url = (base_url or "https://api.openai.com").rstrip("/")
        self.timeout = timeout

    def generate(self, prompt):
        api_key = os.environ.get(self.api_key_env)

        if not api_key:
            raise ValueError(
                f"Environment variable '{self.api_key_env}' is required "
                "for the Anthropic adapter."
            )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        if self.temperature is not None:
            payload["temperature"] = self.temperature

        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens

        endpoint = f"{self.base_url}/chat/completions"
        body = json.dumps(payload).encode("utf-8")

        http_request = request.Request(
            endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Openai API request failed with status {exc.code}: {details}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(
                f"Openai API request could not be completed: {exc.reason}"
            ) from exc

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected Openai API response: {data}"
            ) from exc
