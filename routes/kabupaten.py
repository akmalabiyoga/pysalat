"""GET /kabupaten-kota — fetch kabupaten/kota for a province."""

import json
import logging
import os

from fastapi import APIRouter, HTTPException

from config import DATA_DIR
from db import execute_query, fetch_one
from scraper import fetch_kabupaten_kota
from utils import get_cookies_dict, slugify

logger = logging.getLogger(__name__)
router = APIRouter()


def _resolve_province(province: str) -> tuple[str, str]:
    """Resolve a province query string to its (value, name) from the DB."""
    prov_slug = slugify(province)
    row = fetch_one(
        "SELECT value, name FROM provinces WHERE name_slug LIKE ?",
        (f"%{prov_slug}%",),
    )
    if not row:
        raise HTTPException(status_code=404, detail=f"Province {province} not found")
    return row[0], row[1]


@router.get("/kabupaten-kota")
def get_kabupaten_kota(province: str):
    """Fetch and persist kabupaten/kota list for a province."""
    prov_val, prov_name = _resolve_province(province)
    logger.info("Province '%s' mapped to %s (%s)", province, prov_name, prov_val)

    cookies = get_cookies_dict()
    kabupaten_kota = fetch_kabupaten_kota(prov_val, cookies)

    # Persist to DB
    for city in kabupaten_kota:
        execute_query(
            "INSERT OR REPLACE INTO kabupaten_kota "
            "(value, name, name_slug, prov_val, prov_name) VALUES (?, ?, ?, ?, ?)",
            (city["value"], city["name"], slugify(city["name"]), prov_val, prov_name),
        )

    # Persist to JSON
    out_dir = os.path.join(DATA_DIR, "kabupaten-kota")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"{prov_name}.json"), "w") as f:
        json.dump(kabupaten_kota, f, indent=4)
    logger.info("Saved %d kabupaten/kota for %s", len(kabupaten_kota), prov_name)

    return kabupaten_kota


@router.get("/kabupaten-kota/{province}")
def get_kabupaten_kota_path(province: str):
    """Path-parameter variant of the kabupaten-kota endpoint."""
    return get_kabupaten_kota(province)
