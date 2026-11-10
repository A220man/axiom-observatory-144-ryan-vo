import random
import time
import uuid
from typing import Optional
from app.models.schemas import (
    BenchmarkRequest,
    BenchmarkRun,
    BenchmarkResponse,
    TokenMetrics,
    ProviderType,
)
from app.services.adapters import create_adapter, LLMAdapter, InferenceResult


class InferenceService:
    """Inference service supporting both simulated and real LLM providers."""

    def __init__(self):
        self._base_latency_ms = 50  # Base latency per token for simulated
        self._adapter_cache: dict[str, LLMAdapter] = {}

    def _get_rng(self, request: BenchmarkRequest, run_idx: int) -> random.Random:
        """Create a deterministic RNG seeded from request parameters."""
        seed_data = f"{request.model}:{request.prompt}:{request.max_tokens}:{run_idx}"
        seed = hash(seed_data) & 0xFFFFFFFF
        rng = random.Random(seed)
        return rng

    def _get_adapter_key(self, request: BenchmarkRequest) -> str:
        """Generate cache key for adapter."""
        return f"{request.provider}:{request.model}"

    async def _get_adapter(self, request: BenchmarkRequest) -> LLMAdapter:
        """Get or create adapter for the request."""
        key = self._get_adapter_key(request)
        if key not in self._adapter_cache:
            self._adapter_cache[key] = create_adapter(
                provider=request.provider,
                api_key=None,  # Will use settings defaults
                base_url=None,
                model=request.model,
            )
        return self._adapter_cache[key]

    async def _run_simulated(self, request: BenchmarkRequest, run_idx: int) -> BenchmarkRun:
        """Run a simulated benchmark."""
        run_id = str(uuid.uuid4())[:8]
        rng = self._get_rng(request, run_idx)

        # Temperature controls variance: 0 = deterministic, higher = more variance
        temp_variance = min(request.temperature * 0.25, 0.5)

        # Simulate TTFT (time to first token)
        base_ttft = self._base_latency_ms * 0.8
        ttft_variance = self._base_latency_ms * 0.4 * temp_variance
        ttft_ms = base_ttft + rng.uniform(0, ttft_variance) + rng.uniform(0, self._base_latency_ms * 0.4 * (1 - temp_variance))

        # Simulate token generation
        base_completion = 50 + (hash(request.model) % 100)
        completion_variance = int(50 * temp_variance)
        completion_tokens = min(request.max_tokens, base_completion + rng.randint(-completion_variance, completion_variance))
        completion_tokens = max(1, completion_tokens)

        base_tpot = self._base_latency_ms * 0.5
        tpot_variance = self._base_latency_ms * 0.5 * temp_variance
        tpot_ms = base_tpot + rng.uniform(0, tpot_variance) + rng.uniform(0, self._base_latency_ms * 0.5 * (1 - temp_variance))

        generation_time_ms = ttft_ms + (completion_tokens * tpot_ms)
        total_time_sec = generation_time_ms / 1000

        # Simulate prompt tokens (rough estimate)
        prompt_tokens = len(request.prompt) // 4

        metrics = TokenMetrics(
            ttft_ms=ttft_ms,
            tpot_ms=tpot_ms,
            throughput_tokens_per_sec=completion_tokens / total_time_sec if total_time_sec > 0 else 0,
            total_tokens=prompt_tokens + completion_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        run = BenchmarkRun(
            id=run_id,
            model=request.model,
            provider=request.provider,
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            metrics=metrics,
            created_at=time.time(),
            status="completed",
            error=None,
        )
        return run

    async def _run_real(self, request: BenchmarkRequest, run_idx: int) -> BenchmarkRun:
        """Run a real LLM benchmark using the adapter."""
        run_id = str(uuid.uuid4())[:8]
        adapter = await self._get_adapter(request)

        result = await adapter.generate(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        # Convert InferenceResult to BenchmarkRun
        run = BenchmarkRun(
            id=run_id,
            model=request.model,
            provider=request.provider,
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            metrics=result.metrics,
            created_at=time.time(),
            status=result.status,
            error=result.error,
        )
        return run

    async def run_benchmark(self, request: BenchmarkRequest) -> BenchmarkResponse:
        """Run benchmark using either simulated or real provider."""
        runs = []

        for run_idx in range(request.num_runs):
            if request.provider == ProviderType.SIMULATED:
                run = await self._run_simulated(request, run_idx)
            else:
                run = await self._run_real(request, run_idx)
            runs.append(run)

        # Calculate aggregate metrics
        if runs:
            agg_ttft = sum(r.metrics.ttft_ms for r in runs) / len(runs)
            agg_tpot = sum(r.metrics.tpot_ms for r in runs) / len(runs)
            agg_throughput = sum(r.metrics.throughput_tokens_per_sec for r in runs) / len(runs)
            agg_total = sum(r.metrics.total_tokens for r in runs) / len(runs)
            agg_prompt = sum(r.metrics.prompt_tokens for r in runs) / len(runs)
            agg_completion = sum(r.metrics.completion_tokens for r in runs) / len(runs)

            aggregate = TokenMetrics(
                ttft_ms=agg_ttft,
                tpot_ms=agg_tpot,
                throughput_tokens_per_sec=agg_throughput,
                total_tokens=int(agg_total),
                prompt_tokens=int(agg_prompt),
                completion_tokens=int(agg_completion),
            )
        else:
            aggregate = None

        return BenchmarkResponse(runs=runs, aggregate=aggregate)

    async def close(self):
        """Close all adapter connections."""
        for adapter in self._adapter_cache.values():
            await adapter.close()
        self._adapter_cache.clear()


inference_service = InferenceService()
