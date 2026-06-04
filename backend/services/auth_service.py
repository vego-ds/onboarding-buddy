from fastapi import HTTPException

from backend.security.auth import (
    create_access_token,
    hash_password,
    verify_password,
)
from database.repositories.user_repository import (
    create_user,
    get_user_by_email,
    sanitize_user,
)


def register_user(request):
    existing_user = get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="A user with this email already exists.")

    try:
        user = create_user(
            name=request.name.strip(),
            email=request.email,
            password_hash=hash_password(request.password),
            role=request.role,
            employee_id=request.employee_id,
            manager_id=request.manager_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    token = create_access_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": sanitize_user(user),
    }


def authenticate_user(email, password):
    user = get_user_by_email(email)
    if user is None or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": sanitize_user(user),
    }
