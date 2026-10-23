import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.schemas import TokenMetrics, BenchmarkRequest


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def get_client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_check(self):
        async with await get_client() as client:
            response = await client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "axiom-observatory"
            assert "version" in data


class TestBenchmarkEndpoint:
    @pytest.mark.asyncio
    async def test_benchmark_basic(self):
        async with await get_client() as client:
            payload = {
                "model": "test-model",
                "provider": "simulated",
                "prompt": "Hello, world!",
                "max_tokens": 50,
                "temperature": 0.7,
                "num_runs": 1,
            }
            response = await client.post("/api/v1/benchmark", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "runs" in data
            assert len(data["runs"]) == 1
            run = data["runs"][0]
            assert run["model"] == "test-model"
            assert run["provider"] == "simulated"
            assert run["status"] == "completed"
            assert "metrics" in run
            metrics = run["metrics"]
            assert "ttft_ms" in metrics
            assert "tpot_ms" in metrics
            assert "throughput_tokens_per_sec" in metrics
            assert "total_tokens" in metrics
            assert metrics["throughput_tokens_per_sec"] > 0

    @pytest.mark.asyncio
    async def test_benchmark_multiple_runs(self):
        async with await get_client() as client:
            payload = {
                "model": "test-model",
                "provider": "simulated",
                "prompt": "Test prompt for multiple runs",
                "max_tokens": 100,
                "temperature": 0.5,
                "num_runs": 3,
            }
            response = await client.post("/api/v1/benchmark", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert len(data["runs"]) == 3
            assert data["aggregate"] is not None
            agg = data["aggregate"]
            assert agg["ttft_ms"] > 0
            assert agg["throughput_tokens_per_sec"] > 0

    @pytest.mark.asyncio
    async def test_benchmark_validation_max_tokens(self):
        async with await get_client() as client:
            payload = {
                "model": "test-model",
                "provider": "simulated",
                "prompt": "Test",
                "max_tokens": 5000,
                "temperature": 0.7,
                "num_runs": 1,
            }
            response = await client.post("/api/v1/benchmark", json=payload)
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_benchmark_validation_empty_prompt(self):
        async with await get_client() as client:
            payload = {
                "model": "test-model",
                "provider": "simulated",
                "prompt": "",
                "max_tokens": 50,
                "temperature": 0.7,
                "num_runs": 1,
            }
            response = await client.post("/api/v1/benchmark", json=payload)
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_benchmark_validation_temperature(self):
        async with await get_client() as client:
            payload = {
                "model": "test-model",
                "provider": "simulated",
                "prompt": "Test",
                "max_tokens": 50,
                "temperature": 3.0,
                "num_runs": 1,
            }
            response = await client.post("/api/v1/benchmark", json=payload)
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_benchmark_different_providers(self):
        async with await get_client() as client:
            for provider in ["openai_compatible", "anthropic", "gemini", "ollama", "simulated"]:
                payload = {
                    "model": "test-model",
                    "provider": provider,
                    "prompt": "Test",
                    "max_tokens": 50,
                    "temperature": 0.7,
                    "num_runs": 1,
                }
                response = await client.post("/api/v1/benchmark", json=payload)
                assert response.status_code == 200, f"Failed for provider {provider}"
                data = response.json()
                assert data["runs"][0]["provider"] == provider

    @pytest.mark.asyncio
    async def test_benchmark_consistent_results(self):
        async with await get_client() as client:
            payload = {
                "model": "deterministic-model",
                "provider": "simulated",
                "prompt": "Deterministic prompt",
                "max_tokens": 50,
                "temperature": 0.0,
                "num_runs": 2,
            }
            response = await client.post("/api/v1/benchmark", json=payload)
            assert response.status_code == 200
            data = response.json()
            run1_tokens = data["runs"][0]["metrics"]["completion_tokens"]
            run2_tokens = data["runs"][1]["metrics"]["completion_tokens"]
            assert abs(run1_tokens - run2_tokens) <= 5


class TestBenchmarkSchemas:
    def test_token_metrics_schema(self):
        metrics = TokenMetrics(
            ttft_ms=100.0,
            tpot_ms=10.0,
            throughput_tokens_per_sec=100.0,
            total_tokens=150,
            prompt_tokens=50,
            completion_tokens=100,
        )
        assert metrics.ttft_ms == 100.0
        assert metrics.throughput_tokens_per_sec == 100.0

    def test_benchmark_request_defaults(self):
        req = BenchmarkRequest(model="test", prompt="hello")
        assert req.provider.value == "simulated"
        assert req.max_tokens == 100
        assert req.temperature == 0.7
        assert req.num_runs == 1