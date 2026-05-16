"""Seed PostgreSQL database from JSON files."""

import json
import logging
import os
import sys
from datetime import datetime

# Add parent directory to path so we can import config and pg_db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATA_DIR
from pg_db import init_pg_db, get_pg_connection
from utils import slugify

# Set up logging for the script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# Prayer ID mapping
PRAYER_MAPPING = {
    "imsak": 1,
    "subuh": 2,
    "terbit": 3,
    "dhuha": 4,
    "dzuhur": 5,
    "ashar": 6,
    "maghrib": 7,
    "isya": 8,
}

def seed_database():
    """Parse JSON files and seed PostgreSQL database."""
    logger.info("Initializing PostgreSQL schema...")
    init_pg_db()

    jadwal_dir = os.path.join(DATA_DIR, "jadwal-sholat")
    if not os.path.exists(jadwal_dir):
        logger.error(f"Jadwal directory not found: {jadwal_dir}")
        return

    json_files = [f for f in os.listdir(jadwal_dir) if f.endswith(".json")]
    logger.info(f"Found {len(json_files)} JSON files to process.")

    with get_pg_connection() as conn:
        with conn.cursor() as cursor:
            for filename in json_files:
                file_path = os.path.join(jadwal_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                    prov_name = data.get("prov")
                    kabko_name = data.get("kabko")
                    
                    if not prov_name or not kabko_name:
                        logger.warning(f"Skipping {filename}: Missing 'prov' or 'kabko'")
                        continue

                    prov_slug = slugify(prov_name)
                    kabko_slug = slugify(kabko_name)

                    # 1. Insert Province
                    cursor.execute(
                        """
                        INSERT INTO provinsi (slug, name) 
                        VALUES (%s, %s) 
                        ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name
                        """,
                        (prov_slug, prov_name)
                    )

                    # 2. Insert Kabupaten/Kota
                    cursor.execute(
                        """
                        INSERT INTO kabupaten_kota (slug, name, provinsi_slug) 
                        VALUES (%s, %s, %s) 
                        ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name, provinsi_slug = EXCLUDED.provinsi_slug
                        """,
                        (kabko_slug, kabko_name, prov_slug)
                    )

                    # 3. Prepare Jadwal entries
                    jadwal_entries = []
                    jadwal_data = data.get("data", {})
                    
                    for date_str, times_dict in jadwal_data.items():
                        # Parse the date
                        try:
                            prayer_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                        except ValueError:
                            logger.warning(f"Invalid date format in {filename}: {date_str}")
                            continue

                        for prayer_key, time_str in times_dict.items():
                            if prayer_key == "tanggal" or not time_str:
                                continue

                            prayer_id = PRAYER_MAPPING.get(prayer_key.lower())
                            if not prayer_id:
                                continue

                            # Combine date and time
                            try:
                                dt_str = f"{date_str} {time_str}"
                                prayer_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                            except ValueError:
                                logger.warning(f"Invalid time format in {filename}: {dt_str}")
                                continue

                            jadwal_entries.append((
                                kabko_slug,
                                prayer_id,
                                prayer_date,
                                prayer_time
                            ))

                    # 4. Bulk Insert Jadwal
                    if jadwal_entries:
                        from psycopg2.extras import execute_values
                        execute_values(
                            cursor,
                            """
                            INSERT INTO jadwal (kabupaten_kota_slug, prayer_id, prayer_date, prayer_time)
                            VALUES %s
                            ON CONFLICT (kabupaten_kota_slug, prayer_date, prayer_id) 
                            DO UPDATE SET prayer_time = EXCLUDED.prayer_time
                            """,
                            jadwal_entries
                        )
                        logger.info(f"Seeded {len(jadwal_entries)} records for {kabko_name} ({prov_name})")

                except Exception as e:
                    logger.error(f"Failed to process {filename}: {e}")

        # Commit all changes at the end of the loop
        conn.commit()
    logger.info("Database seeding completed.")

if __name__ == "__main__":
    seed_database()
