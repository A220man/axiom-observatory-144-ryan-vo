# Changelog

## 1.7.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.6.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.5.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

### Backend
- Added `SimulatedAdapter` implementing `LLMAdapter` interface for benchmarking without external API keys
- Updated adapter factory to support `SIMULATED` provider type via `ProviderType.SIMULATED`
- Added deterministic token timing metrics (TTFT, TPOT, throughput) suitable for token-speed benchmarking
- All adapter outputs are deterministic given request parameters (seed derived from model+prompt+temperature)
- 4 new adapter factory tests for simulated provider

## 1.4.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.3.0 — work-in-progress checkpoint

Implemented llm-adapters feature: LLM provider adapters for real inference benchmarking.

### Backend
- Added base `LLMAdapter` interface with common metrics (TTFT, TPOT, throughput) and key redaction
- Implemented OpenAI-compatible adapter (OpenAI, vLLM, LM Studio, etc.) with streaming support
- Implemented Anthropic adapter (Claude models) with streaming support
- Implemented Google Gemini adapter with streaming support
- Implemented Ollama adapter (local models) with streaming support
- Added adapter factory for provider selection via `ProviderType` enum
- Updated `InferenceService` to route requests to real adapters for non-simulated providers
- Maintained simulated provider for testing without API keys
- 9 new adapter factory tests, all 30 backend tests pass

### Frontend
- No frontend changes required (existing provider selector works with new adapters)
- All 7 frontend tests pass, typecheck and build succeed

### Configuration
