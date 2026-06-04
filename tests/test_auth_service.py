from datetime import timedelta
import hmac

import pytest
from fastapi import HTTPException

from backend.security import auth
from backend.services import auth_service
from schemas.auth import LoginRequest, RegisterRequest


def test_password_hash_verification_round_trip():
    password_hash = auth.hash_password("correct horse battery staple")

    assert auth.verify_password("correct horse battery staple", password_hash) is True
    assert auth.verify_password("wrong password", password_hash) is False


def test_access_token_round_trip():
    user = {
        "user_id": "USER_123",
        "email": "user@example.com",
        "role": "employee",
    }

    token = auth.create_access_token(user)
    payload = auth.decode_access_token(token)

    assert payload["sub"] == "USER_123"
    assert payload["role"] == "employee"


def test_expired_token_is_rejected():
    user = {
        "user_id": "USER_123",
        "email": "user@example.com",
        "role": "employee",
    }

    token = auth.create_access_token(user, expires_delta=timedelta(seconds=-1))

    with pytest.raises(HTTPException) as error:
        auth.decode_access_token(token)

    assert error.value.status_code == 401
    assert error.value.detail == "Token has expired."


def test_invalid_token_is_rejected():
    token = auth.create_access_token(
        {
            "user_id": "USER_123",
            "email": "user@example.com",
            "role": "employee",
        }
    )
    invalid_token = f"{token[:-2]}xx"

    with pytest.raises(HTTPException) as error:
        auth.decode_access_token(invalid_token)

    assert error.value.status_code == 401
    assert error.value.detail == "Invalid token."


def test_register_user_hashes_password_and_returns_token(monkeypatch):
    captured = {}

    def fake_create_user(**kwargs):
        captured.update(kwargs)
        return {
            "user_id": "USER_123",
            "name": kwargs["name"],
            "email": kwargs["email"],
            "password_hash": kwargs["password_hash"],
            "role": kwargs["role"],
            "tenant_id": kwargs["tenant_id"],
            "employee_id": kwargs["employee_id"],
            "manager_id": kwargs["manager_id"],
        }

    monkeypatch.setattr(auth_service, "get_user_by_email_and_tenant", lambda *_args: None)
    monkeypatch.setattr(auth_service, "create_user", fake_create_user)
    monkeypatch.setattr(
        auth_service,
        "create_refresh_token",
        lambda user_id, token_hash, expires_at: {},
    )
    monkeypatch.setattr(auth_service, "create_auth_audit_log", lambda **_kwargs: {})

    response = auth_service.register_user(
        RegisterRequest(
            name="Avery Lee",
            email="avery@example.com",
            password="password123",
            role="employee",
            tenant_id="TENANT_DEFAULT",
            employee_id="EMP_1",
        )
    )

    assert response["access_token"]
    assert response["user"]["email"] == "avery@example.com"
    assert "password_hash" not in response["user"]
    assert captured["password_hash"].startswith("pbkdf2_sha256$")


def test_login_rejects_bad_password(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "get_user_by_email",
        lambda _email: {
            "user_id": "USER_123",
            "email": "avery@example.com",
            "password_hash": auth.hash_password("correct-password"),
            "role": "employee",
        },
    )
    monkeypatch.setattr(auth_service, "create_auth_audit_log", lambda **_kwargs: {})

    with pytest.raises(HTTPException) as error:
        auth_service.authenticate_user("avery@example.com", "wrong-password")

    assert error.value.status_code == 401


def test_employee_can_only_access_own_employee_record(monkeypatch):
    def fake_employee(employee_id):
        return {"employee_id": employee_id, "tenant_id": "TENANT_DEFAULT"}

    monkeypatch.setattr(auth, "get_employee_by_id", fake_employee)
    employee_user = {
        "user_id": "USER_EMP",
        "role": "employee",
        "employee_id": "EMP_1",
        "tenant_id": "TENANT_DEFAULT",
    }

    assert auth.can_access_employee(employee_user, "EMP_1") is True
    assert auth.can_access_employee(employee_user, "EMP_2") is False


def test_manager_can_access_direct_reports(monkeypatch):
    manager_user = {"user_id": "USER_MANAGER", "role": "manager", "tenant_id": "TENANT_DEFAULT"}
    monkeypatch.setattr(
        auth,
        "get_employee_by_id",
        lambda employee_id: {"employee_id": employee_id, "tenant_id": "TENANT_DEFAULT"},
    )
    monkeypatch.setattr(
        auth,
        "list_users_by_manager_id",
        lambda _manager_id: [
            {
                "user_id": "USER_EMP",
                "role": "employee",
                "employee_id": "EMP_2",
                "manager_id": "USER_MANAGER",
            }
        ],
    )

    assert auth.can_access_employee(manager_user, "EMP_2") is True
    assert auth.can_access_employee(manager_user, "EMP_3") is False


def test_hr_can_access_all_employee_records(monkeypatch):
    monkeypatch.setattr(
        auth,
        "get_employee_by_id",
        lambda employee_id: {
            "employee_id": employee_id,
            "tenant_id": "TENANT_DEFAULT",
        },
    )
    assert auth.can_access_employee({"role": "hr_admin", "tenant_id": "TENANT_DEFAULT"}, "EMP_99") is True
    assert auth.can_access_employee({"role": "admin", "tenant_id": "TENANT_DEFAULT"}, "EMP_99") is True


def test_cross_tenant_employee_access_is_rejected(monkeypatch):
    monkeypatch.setattr(
        auth,
        "get_employee_by_id",
        lambda employee_id: {"employee_id": employee_id, "tenant_id": "TENANT_OTHER"},
    )

    assert auth.can_access_employee(
        {"role": "admin", "tenant_id": "TENANT_DEFAULT"},
        "EMP_99",
    ) is False


def test_role_dependency_allows_hr_and_rejects_employee():
    dependency = auth.require_roles("hr_admin", "admin")

    assert dependency({"role": "hr_admin"}) == {"role": "hr_admin"}
    with pytest.raises(HTTPException) as error:
        dependency({"role": "employee"})

    assert error.value.status_code == 403


def test_refresh_token_rotation(monkeypatch):
    stored_hashes = []

    monkeypatch.setattr(
        auth_service,
        "create_refresh_token",
        lambda user_id, token_hash, expires_at: stored_hashes.append(token_hash),
    )
    monkeypatch.setattr(
        auth_service,
        "get_refresh_token_by_hash",
        lambda token_hash: {
            "user_id": "USER_123",
            "token_hash": token_hash,
            "expires_at": "2999-01-01T00:00:00+00:00",
            "revoked_at": None,
        },
    )
    monkeypatch.setattr(
        auth_service,
        "get_user_by_id",
        lambda _user_id: {
            "user_id": "USER_123",
            "email": "avery@example.com",
            "role": "employee",
            "tenant_id": "TENANT_DEFAULT",
        },
    )
    monkeypatch.setattr(auth_service, "revoke_refresh_token", lambda _hash: 1)
    monkeypatch.setattr(auth_service, "create_auth_audit_log", lambda **_kwargs: {})

    response = auth_service.refresh_access_token("refresh-token")

    assert response["access_token"]
    assert response["refresh_token"]
    assert stored_hashes


def test_password_reset_request_returns_token_for_known_user(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "get_user_by_email",
        lambda _email: {
            "user_id": "USER_123",
            "email": "avery@example.com",
            "tenant_id": "TENANT_DEFAULT",
        },
    )
    monkeypatch.setattr(
        auth_service,
        "create_password_reset_token",
        lambda **_kwargs: {"reset_token_id": "RESET_1"},
    )
    monkeypatch.setattr(auth_service, "create_auth_audit_log", lambda **_kwargs: {})

    response = auth_service.request_password_reset("avery@example.com")

    assert response["status"] == "reset_requested"
    assert response["reset_token"]


def test_sso_login_verifies_assertion_and_creates_user(monkeypatch):
    captured = {}
    assertion = hmac.new(
        auth_service.SSO_SHARED_SECRET.encode("utf-8"),
        b"oidc:TENANT_DEFAULT:sso@example.com:provider-subject",
        "sha256",
    ).hexdigest()

    def fake_create_user(**kwargs):
        captured.update(kwargs)
        return {
            "user_id": "USER_SSO",
            "name": kwargs["name"],
            "email": kwargs["email"],
            "role": kwargs["role"],
            "tenant_id": kwargs["tenant_id"],
            "password_hash": kwargs["password_hash"],
        }

    monkeypatch.setattr(auth_service, "get_user_by_email_and_tenant", lambda *_args: None)
    monkeypatch.setattr(auth_service, "create_user", fake_create_user)
    monkeypatch.setattr(
        auth_service,
        "create_refresh_token",
        lambda user_id, token_hash, expires_at: {},
    )
    monkeypatch.setattr(auth_service, "create_auth_audit_log", lambda **_kwargs: {})

    from schemas.auth import SSOLoginRequest

    response = auth_service.authenticate_sso_user(
        SSOLoginRequest(
            email="sso@example.com",
            name="SSO User",
            tenant_id="TENANT_DEFAULT",
            role="employee",
            provider_subject="provider-subject",
            assertion=assertion,
        )
    )

    assert response["access_token"]
    assert response["user"]["email"] == "sso@example.com"
    assert captured["tenant_id"] == "TENANT_DEFAULT"


def test_sso_login_rejects_bad_assertion(monkeypatch):
    monkeypatch.setattr(auth_service, "create_auth_audit_log", lambda **_kwargs: {})

    from schemas.auth import SSOLoginRequest

    with pytest.raises(HTTPException) as error:
        auth_service.authenticate_sso_user(
            SSOLoginRequest(
                email="sso@example.com",
                name="SSO User",
                tenant_id="TENANT_DEFAULT",
                provider_subject="provider-subject",
                assertion="bad",
            )
        )

    assert error.value.status_code == 401
