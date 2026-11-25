import json
import time
from typing import AsyncIterator
import hashlib
import random

from app.services.adapters.base import LLMAdapter, InferenceResult, TokenMetrics


class SimulatedAdapter(LLMAdapter):
    """Simulated LLM adapter for benchmarking without external API keys.

    Generates realistic token timing metrics suitable for token-speed
    benchmarking. All output is deterministic given the seed derived from
    the request parameters.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: float = 30.0,
    ):
        super().__init__(api_key, base_url, model, timeout_seconds)

    def _calculate_metrics(
        self,
        ttft_ms: float,
        completion_tokens: int,
        total_time_ms: float,
        prompt_tokens: int,
    ) -> TokenMetrics:
        """Calculate token metrics from timing data (simulated override).

        TPOT is the time per output token, computed as:
          tpot = (total_time - ttft) / completion_tokens
        Throughput is tokens per second.
        """
        tpot_ms = (total_time_ms - ttft_ms) / max(completion_tokens, 1) if completion_tokens > 0 else 0.0
        throughput = (completion_tokens / (total_time_ms / 1000)) if total_time_ms > 0 else 0.0
        return TokenMetrics(
            ttft_ms=ttft_ms,
            tpot_ms=max(tpot_ms, 0.01),  # Ensure strictly positive
            throughput_tokens_per_sec=max(throughput, 0.01),
            total_tokens=prompt_tokens + completion_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    async def generate(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> InferenceResult:
        """Generate simulated completion with realistic metrics."""
        start_time = time.perf_counter()

        # Deterministic RNG seeded from prompt+model+temp for reproducible runs
        seed_data = f"{self.model}:{prompt}:{temperature}"
        seed = int(hashlib.sha256(seed_data.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)

        # TTFT: time to first token (varies with temperature, always positive)
        base_ttft = 50.0
        ttft_jitter = 20.0
        ttft_ms = base_ttft + rng.uniform(0, ttft_jitter) * (1 + abs(temperature) / 2.0)

        # Token generation: total tokens produced
        base_completion = 50 + hash(self.model) % 150
        completion_tokens = min(max_tokens, max(1, base_completion + rng.randint(-10, 10)))

        # TPOT: time per output token (always positive, varies with temperature)
        base_tpot = 50.0
        tpot_jitter = 10.0
        temp_factor = 1.0 + abs(temperature) * 0.3
        tpot_ms = abs(base_tpot * temp_factor + rng.uniform(0, tpot_jitter))

        # Total generation time = TTFT + (completion_tokens * TPOT)
        total_time_ms = ttft_ms + completion_tokens * tpot_ms
        total_time_ms = max(total_time_ms, 1.0)

        # Prompt tokens (rough estimate)
        prompt_tokens = len(prompt) // 4

        # Compute metrics via overridden method
        metrics = self._calculate_metrics(
            ttft_ms=ttft_ms,
            completion_tokens=completion_tokens,
            total_time_ms=total_time_ms,
            prompt_tokens=prompt_tokens,
        )

        # Generate simulated completion text deterministically
        tokens = []
        for i in range(completion_tokens):
            tok_text = f"<token_{i:03d}>"
            tokens.append(tok_text)
        completion_text = "".join(tokens)


        return InferenceResult(
            metrics=metrics,
            completion_text=completion_text,
            status="completed",
        )

    async def stream_generate(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> AsyncIterator[str]:
        """Stream simulated tokens.

        Yields one token at a time with realistic timing intervals.
        """
        seed_data = f"{self.model}:{prompt}:{temperature}"
        seed = int(hashlib.sha256(seed_data.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)

        base_tpot = 50.0
        tpot_jitter = 10.0
        temp_factor = 1.0 + abs(temperature) * 0.3

        for i in range(max_tokens):
            tpot = max(0.1, base_tpot * temp_factor + rng.uniform(0, tpot_jitter))
            # Yield token without actual sleep for test speed
            tok_text = f"<token_{i:03d}>"
            yield tok_text

    async def close(self):
        pass
