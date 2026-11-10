from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, Optional
import time


@dataclass
class TokenMetrics:
    ttft_ms: float
    tpot_ms: float
    throughput_tokens_per_sec: float
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int


@dataclass
class InferenceResult:
    metrics: TokenMetrics
    completion_text: str
    status: str = "completed"
    error: Optional[str] = None


class LLMAdapter(ABC):
    """Base interface for LLM provider adapters."""

    def __init__(self, api_key: str, base_url: str, model: str, timeout_seconds: float = 30.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> InferenceResult:
        """Generate completion and return metrics."""
        pass

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> AsyncIterator[str]:
        """Stream tokens from the model."""
        pass

    def _calculate_metrics(
        self,
        ttft_ms: float,
        completion_tokens: int,
        total_time_ms: float,
        prompt_tokens: int,
    ) -> TokenMetrics:
        """Calculate token metrics from timing data."""
        tpot_ms = (total_time_ms - ttft_ms) / max(completion_tokens, 1) if completion_tokens > 0 else 0
        throughput = (completion_tokens / (total_time_ms / 1000)) if total_time_ms > 0 else 0

        return TokenMetrics(
            ttft_ms=ttft_ms,
            tpot_ms=tpot_ms,
            throughput_tokens_per_sec=throughput,
            total_tokens=prompt_tokens + completion_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    def _redact_key(self, text: str) -> str:
        """Redact API key from error messages."""
        if self.api_key:
            return text.replace(self.api_key, "***REDACTED***")
        return text
