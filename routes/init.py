"""GET /init — initialise cookies and province data."""

import json
import logging
import os

from fastapi import APIRouter, HTTPException
import requests

from config import DATA_DIR
from db import execute_query
from scraper import fetch_cookies_and_provinces
from utils import slugify

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/init")
def init():
    """Fetch cookies and provinces from the Bimas Islam website, persist to DB and JSON."""
    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        cookies_dict, provinces = fetch_cookies_and_provinces()

        # Persist cookies
        if cookies_dict:
            with open(os.path.join(DATA_DIR, "cookies.json"), "w") as f:
                json.dump(cookies_dict, f, indent=4)
            for name, value in cookies_dict.items():
                execute_query(
                    "INSERT OR REPLACE INTO cookies (name, value) VALUES (?, ?)",
                    (name, value),
                )
            logger.info("Saved %d cookie(s)", len(cookies_dict))

        # Persist provinces
        if provinces:
            with open(os.path.join(DATA_DIR, "provinces.json"), "w") as f:
                json.dump(provinces, f, indent=4)
            for prov in provinces:
                execute_query(
                    "INSERT OR REPLACE INTO provinces (value, name, name_slug) VALUES (?, ?, ?)",
                    (prov["value"], prov["text"], slugify(prov["text"])),
                )
            logger.info("Saved %d province(s)", len(provinces))

        return {
            "message": "Initialization successful",
            "cookies": cookies_dict,
            "provinces": provinces,
        }

    except requests.exceptions.RequestException as e:
        logger.exception("Error during initialization")
        raise HTTPException(
            status_code=500, detail=f"Error accessing the website: {e!s}"
        )
