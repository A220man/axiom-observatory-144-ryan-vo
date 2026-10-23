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