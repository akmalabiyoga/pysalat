"""GET /jadwal-sholat — fetch monthly prayer schedule."""

import json
import logging
import os

from fastapi import APIRouter, HTTPException

from config import DATA_DIR
from db import fetch_one
from scraper import fetch_jadwal_sholat
from utils import get_cookies_dict, slugify
from pg_db import fetch_pg_query

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

@router.get("/api/v1/jadwal")
def get_jadwal_from_db(kabkota: str, date: str | None = None, start_date: str | None = None, end_date: str | None = None):
    """Fetch schedule from PostgreSQL database for a specific city.
    Can filter by exact 'date' or range ('start_date' and 'end_date'). Dates must be in YYYY-MM-DD format.
    """
    kab_slug = slugify(kabkota)
    
    query = """
        SELECT 
            j.prayer_date,
            j.prayer_time,
            p.name AS prayer_name,
            k.name AS kabupaten_kota_name,
            pr.name AS provinsi_name
        FROM jadwal j
        JOIN prayer p ON j.prayer_id = p.id
        JOIN kabupaten_kota k ON j.kabupaten_kota_slug = k.slug
        JOIN provinsi pr ON k.provinsi_slug = pr.slug
        WHERE j.kabupaten_kota_slug = %s
    """
    params = [kab_slug]

    if date:
        query += " AND j.prayer_date = %s"
        params.append(date)
    elif start_date and end_date:
        query += " AND j.prayer_date >= %s AND j.prayer_date <= %s"
        params.extend([start_date, end_date])
        
    query += " ORDER BY j.prayer_date ASC, p.id ASC"

    try:
        results = fetch_pg_query(query, tuple(params))
        if not results:
            return {"message": "No data found for the given criteria", "data": []}
        
        # Serialize datetime and date objects to strings
        for row in results:
            row["prayer_date"] = row["prayer_date"].isoformat()
            row["prayer_time"] = row["prayer_time"].isoformat()
            
        return {"status": 1, "message": "Success", "data": results}
    except Exception as exc:
        logger.exception("Error querying PostgreSQL database")
        raise HTTPException(status_code=500, detail=f"Database query failed: {exc!s}")
