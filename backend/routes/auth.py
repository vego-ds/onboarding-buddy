from fastapi import APIRouter, Depends

from backend.security.auth import get_current_user, sanitize_current_user
from backend.services.auth_service import (
    authenticate_sso_user,
    authenticate_user,
    confirm_password_reset,
    logout_user,
    refresh_access_token,
    register_user,
    request_password_reset,
)
from schemas.auth import (
    LoginRequest,
    LogoutRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    SSOLoginRequest,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(request: RegisterRequest):
    return register_user(request)


@router.post("/login")
def login(request: LoginRequest):
    return authenticate_user(request.email, request.password)


@router.post("/refresh")
def refresh(request: RefreshTokenRequest):
    return refresh_access_token(request.refresh_token)


@router.post("/logout")
def logout(request: LogoutRequest):
    return logout_user(request.refresh_token)


@router.post("/password-reset/request")
def password_reset_request(request: PasswordResetRequest):
    return request_password_reset(request.email)


@router.post("/password-reset/confirm")
def password_reset_confirm(request: PasswordResetConfirmRequest):
    return confirm_password_reset(request.reset_token, request.new_password)


@router.post("/sso/login")
def sso_login(request: SSOLoginRequest):
    return authenticate_sso_user(request)


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {"user": sanitize_current_user(current_user)}
