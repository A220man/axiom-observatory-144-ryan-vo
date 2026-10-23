from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class ProviderType(str, Enum):
    OPENAI_COMPATIBLE = "openai_compatible"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    SIMULATED = "simulated"


class BenchmarkRequest(BaseModel):
    model: str = Field(..., description="Model identifier")
    provider: ProviderType = Field(default=ProviderType.SIMULATED, description="LLM provider type")
    prompt: str = Field(..., min_length=1, max_length=10000, description="Input prompt")
    max_tokens: int = Field(default=100, ge=1, le=4096, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    num_runs: int = Field(default=1, ge=1, le=10, description="Number of benchmark runs")


class TokenMetrics(BaseModel):
    ttft_ms: float = Field(..., description="Time to first token in milliseconds")
    tpot_ms: float = Field(..., description="Time per output token in milliseconds")
    throughput_tokens_per_sec: float = Field(..., description="Tokens per second")
    total_tokens: int = Field(..., description="Total tokens generated")
    prompt_tokens: int = Field(..., description="Prompt tokens")
    completion_tokens: int = Field(..., description="Completion tokens")


class BenchmarkRun(BaseModel):
    id: str
    model: str
    provider: ProviderType
    prompt: str
    max_tokens: int
    temperature: float
    metrics: TokenMetrics
    created_at: datetime
    status: Literal["completed", "failed"]
    error: Optional[str] = None


class BenchmarkResponse(BaseModel):
    runs: list[BenchmarkRun]
    aggregate: Optional[TokenMetrics] = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    service: str = "axiom-observatory"