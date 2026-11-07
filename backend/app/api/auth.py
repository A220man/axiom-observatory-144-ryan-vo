import secrets
import hashlib
import base64
from datetime import datetime, timezone
from urllib.parse import urlencode
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

from app.core.config import settings
from app.models.auth import (
    TokenResponse,
    UserInfo,
    LoginUrlResponse,
    CallbackRequest,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

# In-memory state store (use Redis in production)
_auth_states: dict[str, dict] = {}


def generate_code_verifier() -> str:
    """Generate PKCE code verifier (43-128 chars)."""
    return secrets.token_urlsafe(32)[:128]


def generate_code_challenge(code_verifier: str) -> str:
    """Generate PKCE code challenge (S256)."""
    digest = hashlib.sha256(code_verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def generate_state() -> str:
    """Generate OAuth state parameter."""
    return secrets.token_urlsafe(32)


@router.get("/login", response_model=LoginUrlResponse)
async def login():
    """Initiate OIDC login with PKCE."""
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    state = generate_state()

    # Store state for callback validation
    _auth_states[state] = {
        "code_verifier": code_verifier,
        "created_at": datetime.now(timezone.utc),
    }

    # Build authorization URL
    auth_params = {
        "client_id": settings.keycloak_client_id,
        "response_type": "code",
        "scope": "openid profile email",
        "redirect_uri": f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/auth",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    
    login_url = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/auth?{urlencode(auth_params)}"

    return LoginUrlResponse(
        login_url=login_url,
        state=state,
        code_challenge=code_challenge,
    )


@router.post("/callback", response_model=TokenResponse)
async def callback(request: CallbackRequest):
    """Exchange authorization code for tokens with PKCE."""
    # Validate state
    auth_state = _auth_states.pop(request.state, None)
    if not auth_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state",
        )
    
    if auth_state["code_verifier"] != request.code_verifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid code verifier",
        )

    # Exchange code for tokens
    token_url = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": settings.keycloak_client_id,
        "code": request.code,
        "redirect_uri": f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/auth",
        "code_verifier": request.code_verifier,
    }
    
    if settings.keycloak_client_secret:
        token_data["client_secret"] = settings.keycloak_client_secret

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=token_data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token exchange failed: {response.text}",
            )
        token_response = response.json()

    return TokenResponse(**token_response)


# JWT validation
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> UserInfo:
    """Validate JWT and return user info."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    
    token = credentials.credentials
    
    # Fetch JWKS from Keycloak
    jwks_url = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/certs"
    async with httpx.AsyncClient() as client:
        jwks_response = await client.get(jwks_url)
        if jwks_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to fetch JWKS",
            )
        jwks = jwks_response.json()
    
    try:
        # Decode and validate token
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.keycloak_client_id,
            issuer=f"{settings.keycloak_url}/realms/{settings.keycloak_realm}",
        )
        return UserInfo(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token clearing)."""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserInfo)
async def get_me(user: UserInfo = Depends(get_current_user)):
    """Get current user info."""
    return user


# Dependency for protected routes
async def require_auth(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    """Require authentication for protected endpoints."""
    return user
