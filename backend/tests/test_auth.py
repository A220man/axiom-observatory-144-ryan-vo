import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.models.auth import UserInfo
from app.api.auth import require_auth, get_current_user, _auth_states

# Override auth dependency for testing
test_user = UserInfo(
    sub="test-user",
    preferred_username="testuser",
    email="test@example.com",
    name="Test User",
    roles=["user"],
)

app.dependency_overrides[require_auth] = lambda: test_user
app.dependency_overrides[get_current_user] = lambda: test_user


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def get_client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestAuthEndpoints:
    @pytest.mark.asyncio
    async def test_login_endpoint(self):
        async with await get_client() as client:
            response = await client.get("/api/v1/auth/login")
            assert response.status_code == 200
            data = response.json()
            assert "login_url" in data
            assert "state" in data
            assert "code_challenge" in data
            assert data["code_challenge_method"] == "S256"
            # Verify state is stored
            assert data["state"] in _auth_states

    @pytest.mark.asyncio
    async def test_callback_invalid_state(self):
        async with await get_client() as client:
            response = await client.post("/api/v1/auth/callback", json={
                "code": "test-code",
                "state": "invalid-state",
                "code_verifier": "test-verifier",
            })
            assert response.status_code == 400
            assert "Invalid or expired state" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_callback_invalid_code_verifier(self):
        async with await get_client() as client:
            # First get a valid state
            login_response = await client.get("/api/v1/auth/login")
            state = login_response.json()["state"]
            
            response = await client.post("/api/v1/auth/callback", json={
                "code": "test-code",
                "state": state,
                "code_verifier": "wrong-verifier",
            })
            assert response.status_code == 400
            assert "Invalid code verifier" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_logout_endpoint(self):
        async with await get_client() as client:
            response = await client.post("/api/v1/auth/logout")
            assert response.status_code == 200
            assert response.json()["message"] == "Logged out successfully"

    @pytest.mark.asyncio
    async def test_me_endpoint_requires_auth(self):
        # Remove auth override temporarily
        app.dependency_overrides.pop(require_auth, None)
        app.dependency_overrides.pop(get_current_user, None)
        try:
            async with await get_client() as client:
                response = await client.get("/api/v1/auth/me")
                assert response.status_code == 401
        finally:
            app.dependency_overrides[require_auth] = lambda: test_user
            app.dependency_overrides[get_current_user] = lambda: test_user

    @pytest.mark.asyncio
    async def test_me_endpoint_with_auth(self):
        async with await get_client() as client:
            response = await client.get("/api/v1/auth/me")
            assert response.status_code == 200
            data = response.json()
            assert data["sub"] == "test-user"
            assert data["preferred_username"] == "testuser"


class TestPKCEGeneration:
    def test_generate_code_verifier(self):
        from app.api.auth import generate_code_verifier
        verifier = generate_code_verifier()
        assert len(verifier) >= 43
        assert len(verifier) <= 128

    def test_generate_code_challenge(self):
        from app.api.auth import generate_code_challenge, generate_code_verifier
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)
        assert len(challenge) > 0
        # Verify it's valid base64url
        import base64
        # Add padding if needed
        padded = challenge + '=' * (-len(challenge) % 4)
        decoded = base64.urlsafe_b64decode(padded)
        assert len(decoded) == 32  # SHA256 = 32 bytes

    def test_generate_state(self):
        from app.api.auth import generate_state
        state = generate_state()
        assert len(state) > 0


class TestJWTValidation:
    @pytest.mark.asyncio
    async def test_get_current_user_missing_token(self):
        from app.api.auth import get_current_user
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc:
            await get_current_user(None)
        assert exc.value.status_code == 401
        assert "Missing authorization header" in exc.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        from app.api.auth import get_current_user, security
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")
        
        with patch('app.api.auth.httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"keys": []}
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(HTTPException) as exc:
                await get_current_user(credentials)
            assert exc.value.status_code == 401
