import pytest
from app.services.adapters.factory import create_adapter
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
