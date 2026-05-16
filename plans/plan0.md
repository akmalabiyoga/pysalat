# PySalat: Current Project Baseline

This document outlines the current state, architecture, and achievements of the `pysalat` project. It serves as a baseline for future planning and development.

## 1. Project Overview
`pysalat` is a FastAPI-based application designed to scrape and serve Indonesian prayer schedule (Jadwal Sholat) data from the official Bimas Islam (Kemenag) website.

## 2. Architecture & Tech Stack
- **Framework**: FastAPI (served via Uvicorn).
- **Database**: SQLite (`db.py`) used for lightweight, persistent storage of session cookies and geographical metadata (provinces, kabupaten/kota).
- **Scraping**: `requests` and `BeautifulSoup4` (`scraper.py`) are used to interact with the Bimas Islam web portal, handle session states, and parse HTML forms.
- **Project Structure**: Modularised routing under the `routes/` directory, separating concerns for initialization, province/city fetching, and schedule fetching.

## 3. Current Capabilities & Achievements

### A. Session and Cookie Management (`/init`)
- **Capability**: Can perform a two-step HTTP handshake with the Bimas Islam portal to generate and capture necessary session cookies.
- **Achievement**: Successfully bypasses initial session requirements and stores valid cookies both in the SQLite database and as a local JSON file (`data/cookies.json`), ensuring subsequent API requests to Bimas Islam are authenticated.

### B. Geographical Data Extraction
- **Provinces (`/init`)**: Automatically extracts the list of available provinces from the HTML `<select>` elements and persists them to the database and `data/provinces.json`.
- **Kabupaten/Kota (`/kabupaten-kota`)**: Can fetch the list of cities/districts for any given province using the Bimas Islam AJAX endpoint.
- **Achievement**: Implemented a `slugify` utility that allows for robust, case-insensitive, and space-agnostic querying of regions (e.g., matching "dki jakarta" seamlessly), making the API user-friendly. Stores fetched city data in the DB and as JSON files (e.g., `data/kabupaten-kota/DKI JAKARTA.json`).

### C. Prayer Schedule Retrieval (`/jadwal-sholat`)
- **Capability**: Can fetch the monthly prayer schedule for a specific province, kabupaten/kota, month, and year.
- **Achievement**: Integrates database lookups (using slugified names) to resolve the exact internal IDs required by the Bimas Islam API. The resulting schedule is returned via the FastAPI endpoint and persisted to the file system as JSON (e.g., `data/jadwal-sholat/DKI JAKARTA_KOTA JAKARTA PUSAT_2026_05.json`).

## 4. Code Quality & Modularity
- The codebase was recently refactored to remove redundant code.
- Database schemas and global constants are centralized in `config.py`.
- Routing logic is cleanly split into `routes/init.py`, `routes/kabupaten.py`, and `routes/jadwal.py`.
- Database operations are abstracted in `db.py` to prevent logic duplication.
- Comprehensive logging is implemented across all modules to track scraping and API activities.

---
*End of Baseline (plan0.md)*
