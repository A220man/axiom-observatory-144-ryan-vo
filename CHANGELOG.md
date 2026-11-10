# Changelog

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
- Provider configurable via `LLM_PROVIDER` env (defaults to `simulated`)
- API keys and base URLs only on server side via `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`

## 1.2.0 — work-in-progress checkpoint

Implemented auth-oidc feature: OIDC Keycloak authentication with SPA PKCE flow.

### Backend
- Added OIDC authentication endpoints (`/api/v1/auth/login`, `/callback`, `/logout`, `/me`)
- PKCE (RFC 7636) support for secure SPA authentication
- JWT validation using Keycloak JWKS endpoint
- Protected benchmark endpoint requires valid Bearer token
- In-memory state store for PKCE parameters (production should use Redis)
- 11 new backend tests for auth functionality

### Frontend
- React Router integration with protected/public routes
- `useAuth` hook managing authentication state in sessionStorage
- PKCE code verifier/challenge generation and storage
- Login button with Keycloak redirect
- OAuth callback handler component
- API client automatically includes Bearer token
- Login/logout UI in header

### Configuration
- Keycloak settings via environment variables (KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET)
- Updated docker-compose.yml already includes Keycloak service

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.
