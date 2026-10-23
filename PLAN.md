# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-skeleton

## Roadmap

### core-skeleton — FastAPI/React skeleton with basic inference benchmark endpoint

Status: done

Acceptance:
- FastAPI app runs with /health endpoint
- React + Vite frontend builds and serves
- POST /api/v1/benchmark accepts model config and returns token/s metrics
- Dockerfiles for backend and frontend build
- docker-compose.yml with backend, frontend, Keycloak
- Backend tests pass (pytest)
- Frontend typecheck/build/test pass

Implementation: `backend/app/main.py`, `backend/app/api/benchmark.py`, `backend/app/services/inference.py`, `backend/app/models/schemas.py`, `backend/app/core/config.py`, `backend/requirements.txt`, `backend/tests/test_benchmark.py`, `frontend/package.json`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/api/client.ts`, `frontend/src/components/BenchmarkForm.tsx`, `frontend/src/hooks/useBenchmark.ts`, `frontend/src/types/api.ts`, `Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml`, `.env.example`

Tests: `backend/tests/test_benchmark.py`, `frontend/src/__tests__/BenchmarkForm.test.tsx`

### auth-oidc — OIDC Keycloak authentication with SPA PKCE flow

Status: planned

Acceptance:
- Login redirects to Keycloak
- Callback exchanges code for tokens with PKCE
- Access token stored in memory, used for API calls
- Logout clears session
- Protected endpoints reject unauthenticated requests

### llm-adapters — LLM provider adapters (OpenAI-compatible, Anthropic, Gemini, Ollama)

Status: planned

Acceptance:
- Configurable provider via LLM_PROVIDER env
- Adapters implement common interface
- Bounded timeouts and redacted errors
- Keys only server-side

### real-inference — Real LLM inference benchmarking with token streaming

Status: planned

Acceptance:
- Streams tokens from configured provider
- Measures TTFT, TPOT, throughput
- Returns structured metrics
- Handles provider errors gracefully

### results-persistence — SQLite persistence for benchmark runs and results

Status: planned

Acceptance:
- Stores benchmark config and results
- Pagination and filtering on history endpoint
- UTC timestamps, audit log

### export-workflow — Export benchmark results (JSON, CSV)

Status: planned

Acceptance:
- Export single run or filtered history
- Download from frontend

