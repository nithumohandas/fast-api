from fastapi import APIRouter, Depends
from schemas.users import UserResponse
from dependencies import get_current_user_remote

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user_remote)):
    return current_user

@router.get("/profile", response_model=UserResponse)
async def read_user_profile(current_user: dict = Depends(get_current_user_remote)):
    # This endpoint also requires authentication
    return current_user

@router.put("/me")
async def update_user_me(current_user: dict = Depends(get_current_user_remote)):
    # Example protected endpoint
    return {"message": f"Update profile for {current_user['username']}"}