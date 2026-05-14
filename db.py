"""SQLite database helpers for pysalat."""

import logging
import sqlite3

from config import DB_PATH

logger = logging.getLogger(__name__)


def _connect() -> sqlite3.Connection:
    """Return a connection to the application database."""
    return sqlite3.connect(DB_PATH)


def execute_query(query: str, params: tuple = ()) -> None:
    """Execute a write query (INSERT, UPDATE, DELETE, CREATE, DROP)."""
    with _connect() as conn:
        conn.cursor().execute(query, params)
        conn.commit()


def fetch_query(query: str, params: tuple = ()) -> list[tuple]:
    """Execute a read query and return all rows."""
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def fetch_one(query: str, params: tuple = ()) -> tuple | None:
    """Execute a read query and return the first row, or ``None``."""
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()


def drop_db(tables: list[str]) -> None:
    """Drop the listed tables if they exist."""
    for table in tables:
        execute_query(f"DROP TABLE IF EXISTS {table}")


def init_db(schemas: dict[str, str]) -> None:
    """Create (or recreate) tables according to the given schemas.

    Each key is a table name and each value is the column-definition SQL.
    Existing tables are dropped first so the schema is always up to date.
    """
    for table, schema in schemas.items():
        drop_db([table])
        execute_query(f"CREATE TABLE IF NOT EXISTS {table} ({schema})")
    logger.info("Initialised %d table(s): %s", len(schemas), ", ".join(schemas))