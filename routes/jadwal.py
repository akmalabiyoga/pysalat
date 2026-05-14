"""GET /jadwal-sholat — fetch monthly prayer schedule."""

import json
import logging
import os

from fastapi import APIRouter, HTTPException

from config import DATA_DIR
from db import fetch_one
from scraper import fetch_jadwal_sholat
from utils import get_cookies_dict, slugify

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/jadwal-sholat")
def get_jadwal_sholat(province: str, kabkota: str, bulan: str, tahun: str):
    """Return the monthly prayer schedule for a kabupaten/kota."""
    # Resolve province
    prov_slug = slugify(province)
    prov_data = fetch_one(
        "SELECT value, name FROM provinces WHERE name_slug LIKE ?",
        (f"%{prov_slug}%",),
    )
    if not prov_data:
        raise HTTPException(status_code=404, detail=f"Province {province} not found")
    prov_val, prov_name = prov_data

    # Resolve kabupaten/kota
    kab_slug = slugify(kabkota)
    kab_data = fetch_one(
        "SELECT value, name FROM kabupaten_kota WHERE name_slug LIKE ? AND prov_val = ?",
        (f"%{kab_slug}%", prov_val),
    )
    if not kab_data:
        raise HTTPException(
            status_code=404,
            detail=f"Kabupaten/Kota {kabkota} not found in province {prov_name}",
        )
    kab_val, kab_name = kab_data

    logger.info(
        "Jadwal Sholat → Province: %s (%s), Kab/Kota: %s (%s)",
        prov_name, prov_val, kab_name, kab_val,
    )

    cookies = get_cookies_dict()

    try:
        jadwal_data = fetch_jadwal_sholat(prov_val, kab_val, bulan, tahun, cookies)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching schedule: {exc!s}")

    # Persist to JSON
    out_dir = os.path.join(DATA_DIR, "jadwal-sholat")
    os.makedirs(out_dir, exist_ok=True)
    file_path = os.path.join(out_dir, f"{prov_name}_{kab_name}_{tahun}_{bulan}.json")
    with open(file_path, "w") as f:
        json.dump(jadwal_data, f, indent=4)
    logger.info("Saved jadwal sholat to %s", file_path)

    return jadwal_data
