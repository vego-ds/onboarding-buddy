from fastapi import APIRouter, Depends

from backend.security.auth import get_current_user, sanitize_current_user
from backend.services.auth_service import authenticate_user, register_user
from schemas.auth import LoginRequest, RegisterRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(request: RegisterRequest):
    return register_user(request)


@router.post("/login")
def login(request: LoginRequest):
    return authenticate_user(request.email, request.password)


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {"user": sanitize_current_user(current_user)}
