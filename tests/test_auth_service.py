from datetime import timedelta

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
            "employee_id": kwargs["employee_id"],
            "manager_id": kwargs["manager_id"],
        }

    monkeypatch.setattr(auth_service, "get_user_by_email", lambda _email: None)
    monkeypatch.setattr(auth_service, "create_user", fake_create_user)

    response = auth_service.register_user(
        RegisterRequest(
            name="Avery Lee",
            email="avery@example.com",
            password="password123",
            role="employee",
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

    with pytest.raises(HTTPException) as error:
        auth_service.authenticate_user("avery@example.com", "wrong-password")

    assert error.value.status_code == 401


def test_employee_can_only_access_own_employee_record():
    employee_user = {
        "user_id": "USER_EMP",
        "role": "employee",
        "employee_id": "EMP_1",
    }

    assert auth.can_access_employee(employee_user, "EMP_1") is True
    assert auth.can_access_employee(employee_user, "EMP_2") is False


def test_manager_can_access_direct_reports(monkeypatch):
    manager_user = {"user_id": "USER_MANAGER", "role": "manager"}
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


def test_hr_can_access_all_employee_records():
    assert auth.can_access_employee({"role": "hr_admin"}, "EMP_99") is True
    assert auth.can_access_employee({"role": "admin"}, "EMP_99") is True


def test_role_dependency_allows_hr_and_rejects_employee():
    dependency = auth.require_roles("hr_admin", "admin")

    assert dependency({"role": "hr_admin"}) == {"role": "hr_admin"}
    with pytest.raises(HTTPException) as error:
        dependency({"role": "employee"})

    assert error.value.status_code == 403
