import json
import os
from urllib import error, request


class AnthropicModelAdapter:

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
        self.api_key_env = api_key_env or "ANTHROPIC_API_KEY"
        self.base_url = (base_url or "https://api.anthropic.com").rstrip("/")
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
            "max_tokens": self.max_tokens or 1024,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        if self.temperature is not None:
            payload["temperature"] = self.temperature

        endpoint = f"{self.base_url}/v1/messages"
        body = json.dumps(payload).encode("utf-8")

        http_request = request.Request(
            endpoint,
            data=body,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
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
                f"Anthropic API request failed with status {exc.code}: {details}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(
                f"Anthropic API request could not be completed: {exc.reason}"
            ) from exc

        try:
            return data["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected Anthropic API response: {data}"
            ) from exc