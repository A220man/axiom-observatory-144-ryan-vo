# Changelog

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

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
