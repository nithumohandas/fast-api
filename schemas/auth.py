from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    message: Optional[str] = None

class PublicKeyResponse(BaseModel):
    """Info for remote servers to validate tokens"""
    algorithm: str
    issuer: str
    audience: str
    # Note: For production, use RSA and expose public key
    # For demo with HS256, share secret_key securely