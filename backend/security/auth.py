from datetime import UTC, datetime, timedelta
import base64
import hashlib
import hmac
import json
import os
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database.repositories.user_repository import (
    get_user_by_id,
    list_users_by_manager_id,
    sanitize_user,
)

AUTH_TOKEN_EXPIRE_MINUTES = int(os.getenv("AUTH_TOKEN_EXPIRE_MINUTES", "60"))
JWT_ALGORITHM = "HS256"
JWT_SECRET = os.getenv("JWT_SECRET", "development-only-change-me")
PASSWORD_ITERATIONS = 210_000
VALID_ROLES = {"employee", "manager", "hr_admin", "admin"}

bearer_scheme = HTTPBearer(auto_error=False)


def b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(data):
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(f"{data}{padding}".encode("ascii"))


def hash_password(password):
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        str(password).encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    )
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt}${derived.hex()}"


def verify_password(password, password_hash):
    try:
        algorithm, iterations, salt, expected_hash = password_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    derived = hashlib.pbkdf2_hmac(
        "sha256",
        str(password).encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return hmac.compare_digest(derived, expected_hash)


def create_access_token(user, expires_delta=None):
    expires = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=AUTH_TOKEN_EXPIRE_MINUTES)
    )
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": user["user_id"],
        "email": user["email"],
        "role": user["role"],
        "exp": int(expires.timestamp()),
    }
    signing_input = (
        f"{b64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))}."
        f"{b64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))}"
    )
    signature = hmac.new(
        JWT_SECRET.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{b64url_encode(signature)}"


def decode_access_token(token):
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as error:
        raise HTTPException(status_code=401, detail="Invalid token.") from error

    signing_input = f"{header_b64}.{payload_b64}"
    expected_signature = hmac.new(
        JWT_SECRET.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    actual_signature = b64url_decode(signature_b64)

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise HTTPException(status_code=401, detail="Invalid token.")

    payload = json.loads(b64url_decode(payload_b64))
    if payload.get("exp", 0) < int(datetime.now(UTC).timestamp()):
        raise HTTPException(status_code=401, detail="Token has expired.")

    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required.")

    payload = decode_access_token(credentials.credentials)
    user = get_user_by_id(payload.get("sub"))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    return user


def require_roles(*allowed_roles):
    def dependency(current_user=Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions.")
        return current_user

    return dependency


def is_hr_or_admin(user):
    return user.get("role") in {"hr_admin", "admin"}


def can_access_employee(user, employee_id):
    employee_id = str(employee_id or "").strip().upper()
    if is_hr_or_admin(user):
        return True
    if user.get("role") == "employee":
        return str(user.get("employee_id") or "").upper() == employee_id
    if user.get("role") == "manager":
        direct_reports = list_users_by_manager_id(user["user_id"])
        return any(
            str(report.get("employee_id") or "").upper() == employee_id
            for report in direct_reports
        )
    return False


def assert_employee_access(user, employee_id):
    if not can_access_employee(user, employee_id):
        raise HTTPException(status_code=403, detail="Insufficient employee access.")


def sanitize_current_user(user):
    return sanitize_user(user)
