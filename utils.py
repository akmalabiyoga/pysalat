"""Shared utility helpers for pysalat."""

from db import fetch_query


def slugify(name: str) -> str:
    """Normalise a name into a lowercase slug for DB lookups.

    Removes spaces, dots, and commas then lowercases the result.
    """
    return name.replace(" ", "").replace(".", "").replace(",", "").lower()


def get_cookies_dict() -> dict[str, str]:
    """Load cookies from the database and return as a plain dict."""
    rows = fetch_query("SELECT name, value FROM cookies")
    return {row[0]: row[1] for row in rows}
