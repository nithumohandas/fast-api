from core.auth_config import get_settings
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError

from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token
)
from schemas.auth import TokenResponse, TokenValidationResponse, PublicKeyResponse
from schemas.users import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()

# Mock database
fake_users_db = {
    "testuser": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "$2b$12$O8p1FmLGdlnth6U/zvxzOebKoMJft6ozXwuFg1BaD.rgHJL1Cnp8a",
        "is_active": True
    }
}


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint - generates JWT tokens"""
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens with user info
    token_data = {
        "sub": user["username"],
        "user_id": user["id"],
        "email": user["email"]
    }

    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data={"sub": user["username"]})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register new user"""
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    hashed_password = get_password_hash(user.password)
    user_dict = {
        "id": len(fake_users_db) + 1,
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "is_active": True
    }

    fake_users_db[user.username] = user_dict
    return user_dict


@router.post("/validate", response_model=TokenValidationResponse, include_in_schema=False)
async def validate_token(authorization: str = Header(...)):
    """
    Endpoint for remote servers to validate JWT tokens
    Remote server sends: Authorization: Bearer <token>
    """
    try:
        # Extract token from header
        if not authorization.startswith("Bearer "):
            return TokenValidationResponse(
                valid=False,
                message="Invalid authorization header format"
            )

        token = authorization.replace("Bearer ", "")

        # Decode and validate token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.AUDIENCE,
            issuer=settings.ISSUER
        )

        username = payload.get("sub")
        user_id = payload.get("user_id")

        if username is None:
            return TokenValidationResponse(
                valid=False,
                message="Token missing required claims"
            )

        # Verify user still exists and is active
        user = fake_users_db.get(username)
        if not user or not user.get("is_active"):
            return TokenValidationResponse(
                valid=False,
                message="User not found or inactive"
            )

        return TokenValidationResponse(
            valid=True,
            user_id=user_id,
            username=username,
            message="Token is valid"
        )

    except JWTError as e:
        return TokenValidationResponse(
            valid=False,
            message=f"Invalid token: {str(e)}"
        )


@router.get("/public-key", response_model=PublicKeyResponse)
async def get_public_key_info():
    """
    Endpoint for remote servers to get token validation info
    For production, use RSA and return actual public key
    """
    return PublicKeyResponse(
        algorithm=settings.ALGORITHM,
        issuer=settings.ISSUER,
        audience=settings.AUDIENCE
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        username = payload.get("sub")
        user = fake_users_db.get(username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Create new access token
        token_data = {
            "sub": user["username"],
            "user_id": user["id"],
            "email": user["email"]
        }

        new_access_token = create_access_token(data=token_data)

        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,  # Keep same refresh token
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )