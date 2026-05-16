# Migration Plan to PostgreSQL (plan1.md)

This plan outlines the process of migrating the scraped prayer schedule (Jadwal Sholat) data from its current SQLite/JSON format into a normalized PostgreSQL database. This database will serve the client application.

## 1. Database Schema Design (PostgreSQL)

The primary goal is to store the prayer times in a format that is easy to query. To maintain data integrity and prevent anomalous data insertion, we will use a normalized schema. 

### Assessment of Date/Time Data Types
* **Date Querying**: Querying by date is incredibly common for prayer times. Storing a dedicated `DATE` column makes querying and indexing for a specific day much faster than extracting the date from a timestamp.
* **Local Time Representation**: Since the JSON data from Bimas Islam does not contain explicit timezone information and naturally represents the local time of the specific region, we will use the `TIMESTAMP` (without time zone) type. This avoids potential mismatches or errors from trying to map an external timezone reference. The time will be stored exactly as provided by Bimas Islam (local time).

### Table: `provinsi`
```sql
CREATE TABLE IF NOT EXISTS provinsi (
    slug VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
```

### Table: `kabupaten_kota`
```sql
CREATE TABLE IF NOT EXISTS kabupaten_kota (
    slug VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    provinsi_slug VARCHAR(255) NOT NULL REFERENCES provinsi(slug) ON DELETE CASCADE
);
```

### Table: `prayer`
Using a numeric ID is beneficial to maintain the natural chronological order of prayers within a day.
```sql
CREATE TABLE IF NOT EXISTS prayer (
    id SMALLINT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);
-- Pre-seeded data:
-- 1: Imsak, 2: Subuh, 3: Terbit, 4: Dhuha, 5: Dzuhur, 6: Ashar, 7: Maghrib, 8: Isya
```

### Table: `jadwal`
The `jadwal` table focuses purely on scheduling, tying together the location, the specific prayer, the date, and the exact local timestamp.
```sql
CREATE TABLE IF NOT EXISTS jadwal (
    id SERIAL PRIMARY KEY,
    kabupaten_kota_slug VARCHAR(255) NOT NULL REFERENCES kabupaten_kota(slug) ON DELETE CASCADE,
    prayer_id SMALLINT NOT NULL REFERENCES prayer(id) ON DELETE CASCADE,
    prayer_date DATE NOT NULL,
    prayer_time TIMESTAMP NOT NULL,
    UNIQUE (kabupaten_kota_slug, prayer_date, prayer_id)
);

-- Indexes to ensure fast querying by location and time
CREATE INDEX idx_jadwal_prayer_date ON jadwal(prayer_date);
CREATE INDEX idx_jadwal_location_date ON jadwal(kabupaten_kota_slug, prayer_date);
```

## 2. Data Transformation & Population Process

### Transformation Logic (JSON to Rows)
To populate the tables, our seeder process must respect the foreign key constraints:

**Step A: Seed Reference Data**
1. Seed the `prayer` table with IDs 1 through 8.
2. For each JSON file:
   - Extract `prov` (Province Name) and `kabko` (Kabupaten/Kota Name).
   - Generate their respective slugs using the `slugify` utility.
   - Insert or update the `provinsi` table with `(slug, name)`.
   - Insert or update the `kabupaten_kota` table with `(slug, name, provinsi_slug)`.

**Step B: Seed Jadwal (Prayer Times)**
1. Iterate over the `data` dictionary (key = `date_string`, value = `times_dict`).
2. Iterate over the specific prayer times within `times_dict` (e.g., `imsak`, `subuh`, etc., excluding the `tanggal` key).
3. Look up the `prayer_id` (e.g., `imsak` = 1).
4. Extract the `date_string` into a `DATE` object (`prayer_date`).
5. Combine `date_string` and the specific time string (e.g., `04:26`) to parse a full `TIMESTAMP` object (`prayer_time`), representing local time.
6. Insert the resulting row `(kabupaten_kota_slug, prayer_id, prayer_date, prayer_time)` into the `jadwal` table.

*(Example)*: A single day's data in the JSON will be expanded into 8 separate database rows linked to the city slug and the prayer ID.

## 3. Implementation Steps

### Phase 1: PostgreSQL Setup
1. Add a PostgreSQL driver (e.g., `psycopg2-binary` or `asyncpg`) to `pyproject.toml` / `uv.lock`.
2. Update `config.py` to handle a PostgreSQL connection string (e.g., `DATABASE_URL` via environment variables).
3. Create a database initialization script to execute the `CREATE TABLE` statements in the correct order (`prayer`/`provinsi` -> `kabupaten_kota` -> `jadwal`) to respect foreign keys.

### Phase 2: Data Seeder / Migration Script
1. Create a script (e.g., `scripts/seed_pg.py`) that reads all JSON files in the `data/jadwal-sholat/` directory.
2. Implement the transformation logic to parse the JSON files and populate the reference tables.
3. Use bulk inserts to efficiently load the flattened prayer time data into the PostgreSQL `jadwal` table.

### Phase 3: Update API Endpoints
1. Create new API endpoints (e.g., `/api/v1/jadwal`) that query the PostgreSQL database.
2. The endpoint should use `JOIN`s to stitch together the `prayer.name`, `kabupaten_kota.name`, and `jadwal.prayer_time`.
3. Filter efficiently using the `prayer_date` index.
