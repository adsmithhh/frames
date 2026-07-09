class ModelAdapter:

    def __init__(
        self,
        backend,
        model,
        temperature=None,
        max_tokens=None,
        api_key_env=None,
        base_url=None,
        timeout=60,
    ):
        self.backend = (backend or "").strip().lower()
        if not self.backend:
            raise ValueError("Model backend cannot be empty.")

        self.adapter = self._build_adapter(
            backend=self.backend,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key_env=api_key_env,
            base_url=base_url,
            timeout=timeout,
        )

    def _build_adapter(
        self,
        backend,
        model,
        temperature,
        max_tokens,
        api_key_env,
        base_url,
        timeout,
    ):
        if backend == "ollama":
            from OllamaModelAdapter import OllamaModelAdapter

            return OllamaModelAdapter(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        if backend == "deepseek":
            from DeepSeekModelAdapter import DeepSeekModelAdapter

            return DeepSeekModelAdapter(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key_env=api_key_env,
                base_url=base_url,
                timeout=timeout,
            )
        
        if backend == "anthropic":
            from AnthropicModelAdapter import AnthropicModelAdapter

            return AnthropicModelAdapter(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key_env=api_key_env,
                base_url=base_url,
                timeout=timeout,
            )

        if backend == "openai":
            from OpenAiModelAdapter import OpenAiModelAdapter

            return OpenAiModelAdapter(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key_env=api_key_env,
                base_url=base_url,
                timeout=timeout,
            )
        
        if backend == "google":
            from GeminiModelAdapter import GeminiModelAdapter

            return GeminiModelAdapter(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key_env=api_key_env,
                base_url=base_url,
                timeout=timeout,
            )

        raise ValueError(f"Unsupported model adapter: {backend}")

    def generate(self, prompt):
        return self.adapter.generate(prompt)
