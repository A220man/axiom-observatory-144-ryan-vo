from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class TokenType(str, Enum):
    BEARER = "Bearer"


class TokenResponse(BaseModel):
    access_token: str
    token_type: TokenType = TokenType.BEARER
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class UserInfo(BaseModel):
    sub: str
    preferred_username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    roles: list[str] = []


class AuthState(BaseModel):
    code_verifier: str
    state: str
    created_at: datetime


class LoginUrlResponse(BaseModel):
    login_url: str
    state: str
    code_challenge: str
    code_challenge_method: str = "S256"


class CallbackRequest(BaseModel):
    code: str
    state: str
    code_verifier: str
