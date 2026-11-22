import pytest
import asyncio
from app.services.adapters.factory import create_adapter
from app.services.adapters.simulated_adapter import SimulatedAdapter
from app.models.schemas import ProviderType


class TestAdapterFactory:
    def test_create_openai_adapter(self):
        adapter = create_adapter(
            ProviderType.OPENAI_COMPATIBLE,
            api_key="test-key",
            base_url="https://api.openai.com/v1",
            model="gpt-4",
        )
        assert adapter is not None
        assert adapter.model == "gpt-4"
        assert adapter.api_key == "test-key"

    def test_create_anthropic_adapter(self):
        adapter = create_adapter(
            ProviderType.ANTHROPIC,
            api_key="test-key",
            base_url="https://api.anthropic.com",
            model="claude-3-opus",
        )
        assert adapter is not None
        assert adapter.model == "claude-3-opus"

    def test_create_gemini_adapter(self):
        adapter = create_adapter(
            ProviderType.GEMINI,
            api_key="test-key",
            base_url="https://generativelanguage.googleapis.com",
            model="gemini-pro",
        )
        assert adapter is not None
        assert adapter.model == "gemini-pro"

    def test_create_ollama_adapter(self):
        adapter = create_adapter(
            ProviderType.OLLAMA,
            api_key="",
            base_url="http://localhost:11434",
            model="llama3",
        )
        assert adapter is not None
        assert adapter.model == "llama3"

    def test_invalid_provider_raises(self):
        with pytest.raises(ValueError):
            create_adapter("invalid_provider")

    def test_openai_defaults_to_openai_url(self):
        adapter = create_adapter(
            ProviderType.OPENAI_COMPATIBLE,
            api_key="test-key",
            base_url="",
            model="gpt-4",
        )
        assert "openai.com" in adapter.base_url

    def test_anthropic_defaults_to_anthropic_url(self):
        adapter = create_adapter(
            ProviderType.ANTHROPIC,
            api_key="test-key",
            base_url="",
            model="claude-3",
        )
        assert "anthropic.com" in adapter.base_url

    def test_gemini_defaults_to_google_url(self):
        adapter = create_adapter(
            ProviderType.GEMINI,
            api_key="test-key",
            base_url="",
            model="gemini-pro",
        )
        assert "generativelanguage.googleapis.com" in adapter.base_url

    def test_ollama_defaults_to_localhost(self):
        adapter = create_adapter(
            ProviderType.OLLAMA,
            api_key="",
            base_url="",
            model="llama3",
        )
        assert "localhost:11434" in adapter.base_url


class TestSimulatedAdapter:
    def test_create_simulated_adapter(self):
        adapter = create_adapter(
            ProviderType.SIMULATED,
            api_key="simulated-key",
            base_url="simulated://url",
            model="simulated-model",
        )
        assert adapter is not None
        assert adapter.model == "simulated-model"
        assert adapter.api_key == "simulated-key"

    def test_simulated_adapter_generate(self):
        adapter = SimulatedAdapter(
            api_key="test-key",
            base_url="simulated://url",
            model="test-model",
        )

        result = asyncio.get_event_loop().run_until_complete(
            adapter.generate(
                prompt="Hello, world!",
                max_tokens=10,
                temperature=0.7,
            )
        )
        assert result is not None
        assert result.status == "completed"
        assert len(result.completion_text) > 0
        metrics = result.metrics
        assert metrics.ttft_ms > 0
        assert metrics.tpot_ms > 0
        assert metrics.throughput_tokens_per_sec > 0
        assert metrics.total_tokens > 0
        assert metrics.prompt_tokens >= 0
        assert metrics.completion_tokens > 0

    def test_simulated_adapter_deterministic(self):
        """Same seed should produce same results."""
        adapter = SimulatedAdapter(
            api_key="test-key",
            base_url="simulated://url",
            model="deterministic-model",
        )

        result1 = asyncio.get_event_loop().run_until_complete(
            adapter.generate(
                prompt="Deterministic prompt",
                max_tokens=20,
                temperature=0.5,
            )
        )
        result2 = asyncio.get_event_loop().run_until_complete(
            adapter.generate(
                prompt="Deterministic prompt",
                max_tokens=20,
                temperature=0.5,
            )
        )
        # Same seed + same inputs → same completion text
        assert result1.completion_text == result2.completion_text
        assert result1.metrics.completion_tokens == result2.metrics.completion_tokens

    def test_simulated_adapter_stream_generate(self):
        """Stream generate yields the right number of tokens."""
        adapter = SimulatedAdapter(
            api_key="test-key",
            base_url="simulated://url",
            model="stream-model",
        )

        tokens = []
        async def collect():
            async for token in adapter.stream_generate(
                prompt="Stream me",
                max_tokens=5,
                temperature=0.7,
            ):
                tokens.append(token)
        asyncio.get_event_loop().run_until_complete(collect())
        assert len(tokens) == 5
        # Each token should have the expected format
        for token in tokens:
            assert token.startswith("<token_")
            assert token.endswith(">")
