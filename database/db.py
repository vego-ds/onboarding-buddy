import os
from pathlib import Path

from dotenv import load_dotenv

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - exercised only when PostgreSQL is used
    psycopg = None
    dict_row = None

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
DEFAULT_DATABASE_URL = (
    "postgresql://onboarding_buddy:onboarding_buddy@localhost:5432/onboarding_buddy"
)

load_dotenv(BASE_DIR / ".env")


def get_database_url():
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def is_postgres_url(database_url):
    return database_url.startswith(("postgresql://", "postgres://"))


def get_integrity_error_classes():
    if psycopg is None:
        return ()

    return (psycopg.IntegrityError,)


def is_duplicate_email_error(error):
    message = str(error).lower()
    return (
        "employee_email" in message
        or "employees.employee_email" in message
        or "employees_employee_email_key" in message
    )


class PostgresConnection:
    def __init__(self, database_url):
        if psycopg is None:
            raise RuntimeError(
                "PostgreSQL support requires psycopg. Install dependencies with "
                "`pip install -r requirements.txt`."
            )

        self.connection = psycopg.connect(database_url, row_factory=dict_row)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.connection.rollback()
        self.connection.close()

    def execute(self, query, values=None):
        return self.connection.execute(convert_placeholders(query), values)

    def executescript(self, script):
        for statement in split_sql_statements(script):
            self.execute(statement)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()


def convert_placeholders(query):
    return query.replace("?", "%s")


def split_sql_statements(script):
    return [statement.strip() for statement in script.split(";") if statement.strip()]


def get_connection():
    database_url = get_database_url()

    if is_postgres_url(database_url):
        return PostgresConnection(database_url)

    raise RuntimeError(
        "DATABASE_URL must be a PostgreSQL URL, for example "
        "postgresql://onboarding_buddy:onboarding_buddy@localhost:5432/onboarding_buddy"
    )


def init_db():
    with get_connection() as connection:
        with open(SCHEMA_PATH, "r") as schema_file:
            connection.executescript(schema_file.read())
        connection.commit()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized for: {get_database_url()}")
