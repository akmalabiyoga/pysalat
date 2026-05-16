"""PostgreSQL database helpers for pysalat."""

import logging
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor

from config import PG_DATABASE_URL

logger = logging.getLogger(__name__)

@contextmanager
def get_pg_connection():
    """Context manager for PostgreSQL connection."""
    conn = None
    try:
        conn = psycopg2.connect(PG_DATABASE_URL)
        yield conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise
    finally:
        if conn:
            conn.close()

def execute_pg_query(query: str, params: tuple = ()) -> None:
    """Execute a write query on PostgreSQL."""
    with get_pg_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
        conn.commit()

def fetch_pg_query(query: str, params: tuple = ()) -> list[dict]:
    """Execute a read query on PostgreSQL and return all rows as dicts."""
    with get_pg_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

def init_pg_db() -> None:
    """Initialize PostgreSQL database schema."""
    schema = """
    CREATE TABLE IF NOT EXISTS provinsi (
        slug VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS kabupaten_kota (
        slug VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        provinsi_slug VARCHAR(255) NOT NULL REFERENCES provinsi(slug) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS prayer (
        id SMALLINT PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS jadwal (
        id SERIAL PRIMARY KEY,
        kabupaten_kota_slug VARCHAR(255) NOT NULL REFERENCES kabupaten_kota(slug) ON DELETE CASCADE,
        prayer_id SMALLINT NOT NULL REFERENCES prayer(id) ON DELETE CASCADE,
        prayer_date DATE NOT NULL,
        prayer_time TIMESTAMP NOT NULL,
        UNIQUE (kabupaten_kota_slug, prayer_date, prayer_id)
    );

    CREATE INDEX IF NOT EXISTS idx_jadwal_prayer_date ON jadwal(prayer_date);
    CREATE INDEX IF NOT EXISTS idx_jadwal_location_date ON jadwal(kabupaten_kota_slug, prayer_date);
    """
    
    try:
        execute_pg_query(schema)
        
        # Seed the prayer table
        prayers = [
            (1, "Imsak"),
            (2, "Subuh"),
            (3, "Terbit"),
            (4, "Dhuha"),
            (5, "Dzuhur"),
            (6, "Ashar"),
            (7, "Maghrib"),
            (8, "Isya"),
        ]
        
        with get_pg_connection() as conn:
            with conn.cursor() as cursor:
                for p_id, p_name in prayers:
                    cursor.execute(
                        "INSERT INTO prayer (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
                        (p_id, p_name)
                    )
            conn.commit()
            
        logger.info("PostgreSQL tables and prayer references initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL schema: {e}")
        raise
