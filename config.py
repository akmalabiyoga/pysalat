"""Centralised configuration and constants for pysalat."""

import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "salat.db")

# ---------------------------------------------------------------------------
# External URLs
# ---------------------------------------------------------------------------
BASE_URL = "https://bimasislam.kemenag.go.id/jadwalshalat"
KABKOTA_URL = "https://bimasislam.kemenag.go.id/ajax/getKabkoshalat"
JADWAL_URL = "https://bimasislam.kemenag.go.id/ajax/getShalatbln"

# ---------------------------------------------------------------------------
# Default HTTP headers
# ---------------------------------------------------------------------------
DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    ),
}

# ---------------------------------------------------------------------------
# Database table schemas  (table_name -> column definitions)
# ---------------------------------------------------------------------------
DB_SCHEMAS: dict[str, str] = {
    "cookies": "name TEXT PRIMARY KEY, value TEXT",
    "provinces": "value TEXT PRIMARY KEY, name TEXT, name_slug TEXT",
    "kabupaten_kota": (
        "value TEXT PRIMARY KEY, name TEXT, name_slug TEXT, "
        "prov_val TEXT, prov_name TEXT"
    ),
}
