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


class InferenceService:
    """Simulated inference service for benchmarking."""

    def __init__(self):
        self._base_latency_ms = 50  # Base latency per token

    def _get_rng(self, request: BenchmarkRequest, run_idx: int) -> random.Random:
        """Create a deterministic RNG seeded from request parameters."""
        seed_data = f"{request.model}:{request.prompt}:{request.max_tokens}:{run_idx}"
        seed = hash(seed_data) & 0xFFFFFFFF
        rng = random.Random(seed)
        return rng

    async def run_benchmark(self, request: BenchmarkRequest) -> BenchmarkResponse:
        """Run benchmark simulation."""
        runs = []

        for run_idx in range(request.num_runs):
            run_id = str(uuid.uuid4())[:8]
            start_time = time.perf_counter()
            rng = self._get_rng(request, run_idx)

            # Temperature controls variance: 0 = deterministic, higher = more variance
            # Variance factor ranges from 0 (temp=0) to ~0.5 (temp=2.0)
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
                ttft_ms=round(ttft_ms, 2),
                tpot_ms=round(tpot_ms, 2),
                throughput_tokens_per_sec=round(completion_tokens / total_time_sec, 2) if total_time_sec > 0 else 0,
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
                created_at=__import__("datetime").datetime.utcnow(),
                status="completed",
            )
            runs.append(run)

        # Calculate aggregate metrics
        if runs:
            agg_ttft = sum(r.metrics.ttft_ms for r in runs) / len(runs)
            agg_tpot = sum(r.metrics.tpot_ms for r in runs) / len(runs)
            agg_throughput = sum(r.metrics.throughput_tokens_per_sec for r in runs) / len(runs)
            agg_total = sum(r.metrics.total_tokens for r in runs) // len(runs)
            agg_prompt = sum(r.metrics.prompt_tokens for r in runs) // len(runs)
            agg_completion = sum(r.metrics.completion_tokens for r in runs) // len(runs)

            aggregate = TokenMetrics(
                ttft_ms=round(agg_ttft, 2),
                tpot_ms=round(agg_tpot, 2),
                throughput_tokens_per_sec=round(agg_throughput, 2),
                total_tokens=agg_total,
                prompt_tokens=agg_prompt,
                completion_tokens=agg_completion,
            )
        else:
            aggregate = None

        return BenchmarkResponse(runs=runs, aggregate=aggregate)


inference_service = InferenceService()
import uuid
from typing import Optional
from app.models.schemas import (
    BenchmarkRequest,
    BenchmarkRun,
    BenchmarkResponse,
    TokenMetrics,
    ProviderType,
)


class InferenceService:
    """Simulated inference service for benchmarking."""

    def __init__(self):
        self._base_latency_ms = 50  # Base latency per token

    async def run_benchmark(self, request: BenchmarkRequest) -> BenchmarkResponse:
        """Run benchmark simulation."""
        runs = []

        for run_idx in range(request.num_runs):
            run_id = str(uuid.uuid4())[:8]
            start_time = time.perf_counter()

            # Simulate TTFT (time to first token)
            ttft_ms = self._base_latency_ms * (0.8 + 0.4 * (hash(request.prompt + str(run_idx)) % 100) / 100)

            # Simulate token generation
            completion_tokens = min(request.max_tokens, 50 + (hash(request.model) % 100))
            tpot_ms = self._base_latency_ms * (0.5 + 0.5 * (hash(request.model + str(run_idx)) % 100) / 100)

            generation_time_ms = ttft_ms + (completion_tokens * tpot_ms)
            total_time_sec = generation_time_ms / 1000

            # Simulate prompt tokens (rough estimate)
            prompt_tokens = len(request.prompt) // 4

            metrics = TokenMetrics(
                ttft_ms=round(ttft_ms, 2),
                tpot_ms=round(tpot_ms, 2),
                throughput_tokens_per_sec=round(completion_tokens / total_time_sec, 2) if total_time_sec > 0 else 0,
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
                created_at=__import__("datetime").datetime.utcnow(),
                status="completed",
            )
            runs.append(run)

        # Calculate aggregate metrics
        if runs:
            agg_ttft = sum(r.metrics.ttft_ms for r in runs) / len(runs)
            agg_tpot = sum(r.metrics.tpot_ms for r in runs) / len(runs)
            agg_throughput = sum(r.metrics.throughput_tokens_per_sec for r in runs) / len(runs)
            agg_total = sum(r.metrics.total_tokens for r in runs) // len(runs)
            agg_prompt = sum(r.metrics.prompt_tokens for r in runs) // len(runs)
            agg_completion = sum(r.metrics.completion_tokens for r in runs) // len(runs)

            aggregate = TokenMetrics(
                ttft_ms=round(agg_ttft, 2),
                tpot_ms=round(agg_tpot, 2),
                throughput_tokens_per_sec=round(agg_throughput, 2),
                total_tokens=agg_total,
                prompt_tokens=agg_prompt,
                completion_tokens=agg_completion,
            )
        else:
            aggregate = None

        return BenchmarkResponse(runs=runs, aggregate=aggregate)


inference_service = InferenceService()