from fastapi import APIRouter, Depends
from dependencies import get_current_user_local, get_current_user_remote

router = APIRouter(prefix="/api", tags=["API"])

@router.get("/protected-local")
async def protected_endpoint_local(current_user: dict = Depends(get_current_user_local)):
    """
    Protected endpoint using LOCAL token validation
    Faster but requires shared secret
    """
    return {
        "message": "This is a protected endpoint (local validation)",
        "user": current_user
    }

@router.get("/protected-remote")
async def protected_endpoint_remote(current_user: dict = Depends(get_current_user_remote)):
    """
    Protected endpoint using REMOTE token validation
    More secure, doesn't require sharing secret
    """
    return {
        "message": "This is a protected endpoint (remote validation)",
        "user": current_user
    }

@router.get("/data")
async def get_data(current_user: dict = Depends(get_current_user_local)):
    """Example data endpoint"""
    return {
        "data": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ],
        "requested_by": current_user["username"]
    }

@router.post("/actions")
async def perform_action(current_user: dict = Depends(get_current_user_local)):
    """Example action endpoint"""
    return {
        "status": "success",
        "action": "performed",
        "user_id": current_user["user_id"]
    }