import pytest

from database.db import convert_placeholders, get_connection, is_postgres_url


def test_detects_postgres_database_urls():
    assert is_postgres_url("postgresql://user:pass@localhost:5432/app")
    assert is_postgres_url("postgres://user:pass@localhost:5432/app")
    assert not is_postgres_url("sqlite:///onboarding_buddy.db")


def test_converts_sqlite_placeholders_for_postgres_driver():
    query = "SELECT * FROM employees WHERE employee_id = ? AND role = ?"

    assert (
        convert_placeholders(query)
        == "SELECT * FROM employees WHERE employee_id = %s AND role = %s"
    )


def test_rejects_non_postgres_runtime_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///onboarding_buddy.db")

    with pytest.raises(RuntimeError, match="PostgreSQL URL"):
        get_connection()
