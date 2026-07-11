import json
import os
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
        # Strip trailing slashes if present in the config string
        self.base_url = (base_url or "https://generativelanguage.googleapis.com").rstrip("/")
        self.timeout = timeout

    def generate(self, prompt):
        api_key = os.environ.get("api_key_env")

        if not api_key:
            raise ValueError(f"Environment variable '{self.api_key_env}' is required.")
        
        url = f"{self.base_url}/v1beta/models/{self.model}:generateContent?key={api_key}"

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
            "maxOutputTokens": self.max_tokens
        }
    }

        if self.temperature is not None:
            payload["temperature"] = self.temperature

        if self.max_tokens is not None:
            payload["max_completion_tokens"] = self.max_tokens

        api_base = self.base_url
        if not api_base.endswith("/v1"):
            api_base = f"{api_base}/v1"

        endpoint = f"{api_base}/chat/completions"

        # Some models accept only default temperature; retry once without it.
        while True:
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

            # Construct the dynamic endpoint
            url = f"{self.base_url}/v1beta/models/{self.model}:generateContent?key={api_key}"

            # Pass this dynamic 'url' variable into your urllib.request.Request() object
            http_request = request.Request(
                url=url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
                method="POST"
            )

            try:
                with request.urlopen(http_request, timeout=self.timeout) as response:
                    response_data = json.loads(response.read().decode("utf-8"))
                    
                    # Extract the response text based on Gemini's return schema
                    return response_data["candidates"][0]["content"]["parts"][0]["text"]  
                              
            except error.HTTPError as exc:
                details = exc.read().decode("utf-8", errors="replace")
                details_lower = details.lower()

                should_retry_without_temperature = (
                    exc.code == 400
                    and "temperature" in payload
                    and "temperature" in details_lower
                    and "unsupported" in details_lower
                )

                if should_retry_without_temperature:
                    payload.pop("temperature", None)
                    continue

                raise RuntimeError(
                    f"Gemini API request failed with status {exc.code}: {details}"
                ) from exc
            except error.URLError as exc:
                raise RuntimeError(
                    f"Gemini API request could not be completed: {exc.reason}"
                ) from exc

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected Gemini API response: {data}"
            ) from exc
