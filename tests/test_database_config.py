from database.db import BASE_DIR, convert_placeholders, get_sqlite_path, is_postgres_url


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


def test_resolves_sqlite_database_path():
    assert get_sqlite_path("sqlite:///onboarding_buddy.db") == (
        BASE_DIR / "onboarding_buddy.db"
    )
