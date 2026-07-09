import json
import os
import re
import time
from urllib import error, request


class GeminiModelAdapter:

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
        self.api_key_env = api_key_env or "GEMINI_API_KEY"
        self.base_url = (base_url or "https://generativelanguage.googleapis.com").rstrip("/")
        self.timeout = timeout
        self.max_retries = 3

    def generate(self, prompt):
        api_key = os.environ.get(self.api_key_env)

        if not api_key:
            raise ValueError(
                f"Environment variable '{self.api_key_env}' is required "
                "for the Gemini adapter."
            )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens,
                "thinkingConfig": {
                    "thinkingBudget": 0  # Forces the model to respond instantly with no reasoning tokens
                }
            }
        }

        endpoint = f"{self.base_url}/v1beta/models/{self.model}:generateContent?key={api_key}"

        retry_count = 0

        while True:
            body = json.dumps(payload).encode("utf-8")
            http_request = request.Request(
                endpoint,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            try:
                with request.urlopen(http_request, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
                break
            except error.HTTPError as exc:
                details = exc.read().decode("utf-8", errors="replace")
                details_lower = details.lower()

                should_retry_without_temperature = (
                    exc.code == 400
                    and "generationConfig" in payload
                    and "temperature" in payload["generationConfig"]
                    and "temperature" in details_lower
                    and "unsupported" in details_lower
                )

                if should_retry_without_temperature:
                    payload["generationConfig"].pop("temperature", None)
                    if not payload["generationConfig"]:
                        payload.pop("generationConfig", None)
                    continue

                should_retry_rate_limit = exc.code == 429 and retry_count < self.max_retries
                if should_retry_rate_limit:
                    retry_delay_seconds = self._extract_retry_delay_seconds(details)
                    retry_count += 1
                    time.sleep(retry_delay_seconds)
                    continue

                raise RuntimeError(
                    f"Gemini API request failed with status {exc.code}: {details}"
                ) from exc
            except error.URLError as exc:
                raise RuntimeError(
                    f"Gemini API request could not be completed: {exc.reason}"
                ) from exc

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected Gemini API response: {data}"
            ) from exc

    def _extract_retry_delay_seconds(self, details):
        default_delay_seconds = 60

        try:
            error_payload = json.loads(details)
        except json.JSONDecodeError:
            error_payload = None

        if isinstance(error_payload, dict):
            for item in error_payload.get("error", {}).get("details", []):
                retry_delay = item.get("retryDelay")
                if isinstance(retry_delay, str):
                    seconds = self._parse_duration_seconds(retry_delay)
                    if seconds is not None:
                        return seconds

            message = error_payload.get("error", {}).get("message", "")
            seconds = self._parse_retry_message_seconds(message)
            if seconds is not None:
                return seconds

        seconds = self._parse_retry_message_seconds(details)
        if seconds is not None:
            return seconds

        return default_delay_seconds

    def _parse_duration_seconds(self, value):
        match = re.fullmatch(r"(\d+)(?:\.\d+)?s", value.strip())
        if not match:
            return None

        return max(1, int(match.group(1)))

    def _parse_retry_message_seconds(self, text):
        match = re.search(r"Please retry in\s+(\d+(?:\.\d+)?)s", text, re.IGNORECASE)
        if not match:
            return None

        return max(1, int(float(match.group(1))) + 1)
