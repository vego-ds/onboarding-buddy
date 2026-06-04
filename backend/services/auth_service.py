from datetime import UTC, datetime, timedelta
import hmac
import os

from fastapi import HTTPException

from backend.security.auth import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    generate_opaque_token,
    hash_password,
    hash_token,
    verify_password,
)
from database.repositories.auth_repository import (
    create_auth_audit_log,
    create_password_reset_token,
    create_refresh_token,
    get_password_reset_token_by_hash,
    get_refresh_token_by_hash,
    mark_password_reset_token_used,
    revoke_refresh_token,
)
from database.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_email_and_tenant,
    get_user_by_id,
    sanitize_user,
    update_user_password_hash,
)

PASSWORD_RESET_EXPIRE_MINUTES = int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "30"))
SSO_SHARED_SECRET = os.getenv("SSO_SHARED_SECRET", "development-sso-secret")


def issue_token_pair(user):
    refresh_token = generate_opaque_token()
    expires_at = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    create_refresh_token(
        user_id=user["user_id"],
        token_hash=hash_token(refresh_token),
        expires_at=expires_at.isoformat(),
    )
    return {
        "access_token": create_access_token(user),
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": sanitize_user(user),
    }


def register_user(request):
    existing_user = get_user_by_email_and_tenant(request.email, request.tenant_id)
    if existing_user:
        raise HTTPException(status_code=409, detail="A user with this email already exists.")

    try:
        user = create_user(
            name=request.name.strip(),
            email=request.email,
            password_hash=hash_password(request.password),
            role=request.role,
            tenant_id=request.tenant_id,
            employee_id=request.employee_id,
            manager_id=request.manager_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    create_auth_audit_log(
        tenant_id=user.get("tenant_id"),
        user_id=user["user_id"],
        email=user["email"],
        event_type="register",
        event_status="success",
        event_message="User registered.",
    )
    return issue_token_pair(user)


def authenticate_user(email, password):
    user = get_user_by_email(email)
    if user is None or not verify_password(password, user["password_hash"]):
        create_auth_audit_log(
            email=str(email),
            event_type="login",
            event_status="failure",
            event_message="Invalid email or password.",
        )
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    create_auth_audit_log(
        tenant_id=user.get("tenant_id"),
        user_id=user["user_id"],
        email=user["email"],
        event_type="login",
        event_status="success",
        event_message="User logged in.",
    )
    return issue_token_pair(user)


def refresh_access_token(refresh_token):
    token_record = get_refresh_token_by_hash(hash_token(refresh_token))
    if token_record is None or token_record.get("revoked_at"):
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    expires_at = datetime.fromisoformat(token_record["expires_at"])
    if expires_at < datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Refresh token has expired.")

    user = get_user_by_id(token_record["user_id"])
    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    revoke_refresh_token(hash_token(refresh_token))
    create_auth_audit_log(
        tenant_id=user.get("tenant_id"),
        user_id=user["user_id"],
        email=user["email"],
        event_type="refresh",
        event_status="success",
        event_message="Refresh token exchanged.",
    )
    return issue_token_pair(user)


def logout_user(refresh_token):
    revoke_refresh_token(hash_token(refresh_token))
    return {"status": "logged_out"}


def request_password_reset(email):
    user = get_user_by_email(email)
    if user is None:
        create_auth_audit_log(
            email=str(email),
            event_type="password_reset_requested",
            event_status="ignored",
            event_message="Password reset requested for unknown email.",
        )
        return {"status": "reset_requested"}

    reset_token = generate_opaque_token()
    expires_at = datetime.now(UTC) + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)
    create_password_reset_token(
        user_id=user["user_id"],
        token_hash=hash_token(reset_token),
        expires_at=expires_at.isoformat(),
    )
    create_auth_audit_log(
        tenant_id=user.get("tenant_id"),
        user_id=user["user_id"],
        email=user["email"],
        event_type="password_reset_requested",
        event_status="success",
        event_message="Password reset token created.",
    )
    return {
        "status": "reset_requested",
        "reset_token": reset_token,
    }


def confirm_password_reset(reset_token, new_password):
    token_record = get_password_reset_token_by_hash(hash_token(reset_token))
    if token_record is None or token_record.get("used_at"):
        raise HTTPException(status_code=401, detail="Invalid reset token.")

    expires_at = datetime.fromisoformat(token_record["expires_at"])
    if expires_at < datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Reset token has expired.")

    password_hash = hash_password(new_password)
    update_user_password_hash(token_record["user_id"], password_hash)

    mark_password_reset_token_used(hash_token(reset_token))
    create_auth_audit_log(
        user_id=token_record["user_id"],
        event_type="password_reset_completed",
        event_status="success",
        event_message="Password reset completed.",
    )
    return {"status": "password_reset"}


def authenticate_sso_user(request):
    expected_assertion = hmac.new(
        SSO_SHARED_SECRET.encode("utf-8"),
        f"{request.provider}:{request.tenant_id}:{request.email}:{request.provider_subject}".encode("utf-8"),
        "sha256",
    ).hexdigest()
    if not hmac.compare_digest(expected_assertion, request.assertion):
        create_auth_audit_log(
            tenant_id=request.tenant_id,
            email=str(request.email),
            event_type="sso_login",
            event_status="failure",
            event_message="Invalid SSO assertion.",
        )
        raise HTTPException(status_code=401, detail="Invalid SSO assertion.")

    user = get_user_by_email_and_tenant(request.email, request.tenant_id)
    if user is None:
        user = create_user(
            name=request.name,
            email=request.email,
            password_hash=hash_password(generate_opaque_token()),
            role=request.role,
            tenant_id=request.tenant_id,
        )

    create_auth_audit_log(
        tenant_id=user.get("tenant_id"),
        user_id=user["user_id"],
        email=user["email"],
        event_type="sso_login",
        event_status="success",
        event_message=f"User logged in through {request.provider}.",
    )
    return issue_token_pair(user)
