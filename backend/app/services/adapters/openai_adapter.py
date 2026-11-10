import json
import time
from typing import AsyncIterator, Optional
import httpx

from app.services.adapters.base import LLMAdapter, InferenceResult, TokenMetrics


class OpenAICompatibleAdapter(LLMAdapter):
    """Adapter for OpenAI-compatible APIs (OpenAI, vLLM, LM Studio, etc.)."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: float = 30.0,
    ):
        super().__init__(api_key, base_url, model, timeout_seconds)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout_seconds,
        )

    async def generate(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> InferenceResult:
        """Generate completion with metrics."""
        start_time = time.perf_counter()
        ttft_ms = 0
        completion_tokens = 0
        completion_text = ""

        try:
            async for token in self.stream_generate(prompt, max_tokens, temperature):
                if ttft_ms == 0:
                    ttft_ms = (time.perf_counter() - start_time) * 1000
                completion_tokens += 1
                completion_text += token

            total_time_ms = (time.perf_counter() - start_time) * 1000
            prompt_tokens = len(prompt) // 4  # Rough estimate

            metrics = self._calculate_metrics(
                ttft_ms=ttft_ms,
                completion_tokens=completion_tokens,
                total_time_ms=total_time_ms,
                prompt_tokens=prompt_tokens,
            )

            return InferenceResult(
                metrics=metrics,
                completion_text=completion_text,
                status="completed",
            )

        except httpx.HTTPStatusError as e:
            error_msg = self._redact_key(f"HTTP {e.response.status_code}: {e.response.text}")
            return InferenceResult(
                metrics=TokenMetrics(0, 0, 0, 0, 0, 0),
                completion_text="",
                status="failed",
                error=error_msg,
            )
        except Exception as e:
            return InferenceResult(
                metrics=TokenMetrics(0, 0, 0, 0, 0, 0),
                completion_text="",
                status="failed",
                error=self._redact_key(str(e)),
            )

    async def stream_generate(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> AsyncIterator[str]:
        """Stream tokens from OpenAI-compatible API."""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }

        async with self.client.stream("POST", "/v1/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                if line.strip() == "":
                    break

                try:
                    chunk = json.loads(line[6:])
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    token = delta.get("content")
                    if token:
                        yield token
                except json.JSONDecodeError:
                    continue

    async def close(self):
        await self.client.aclose()
