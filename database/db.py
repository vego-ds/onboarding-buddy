import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "onboarding_buddy.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        with open(SCHEMA_PATH, "r") as schema_file:
            connection.executescript(schema_file.read())
        connection.commit()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at: {DB_PATH}")
