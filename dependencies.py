import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from core.app_config import get_settings

security = HTTPBearer()
settings = get_settings()


async def validate_token_locally(token: str) -> dict:
    """
    Validate JWT token locally using shared secret
    This is faster but requires sharing secret key
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.EXPECTED_AUDIENCE,
            issuer=settings.EXPECTED_ISSUER
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def validate_token_remotely(token: str) -> dict:
    """
    Validate token by calling auth server's validation endpoint
    This is more secure but slower due to network call
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVER_URL}/auth/validate",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token validation failed",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            data = response.json()
            if not data.get("valid"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=data.get("message", "Invalid token"),
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return data

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth service unavailable: {str(e)}"
        )


async def get_current_user_local(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Dependency for local token validation"""
    token = credentials.credentials
    payload = await validate_token_locally(token)
    return {
        "username": payload.get("sub"),
        "user_id": payload.get("user_id"),
        "email": payload.get("email")
    }


async def get_current_user_remote(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Dependency for remote token validation"""
    token = credentials.credentials
    validation_result = await validate_token_remotely(token)
    return {
        "username": validation_result.get("username"),
        "user_id": validation_result.get("user_id")
    }
