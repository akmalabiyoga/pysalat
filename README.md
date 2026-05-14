# pysalat

Indonesian prayer schedule API — scrapes and serves data from the [Bimas Islam](https://bimasislam.kemenag.go.id/jadwalshalat) website.

## Requirements

- Python ≥ 3.14
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Quick Start

```bash
# Install dependencies
uv sync

# Run the dev server
uv run uvicorn main:app --reload
```

The API will be available at **http://localhost:8000**.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/init` | Fetch session cookies & province list from Bimas Islam, persist to DB |
| `GET` | `/kabupaten-kota?province=JAWA BARAT` | Get kabupaten/kota for a province |
| `GET` | `/kabupaten-kota/{province}` | Same as above, using a path parameter |
| `GET` | `/jadwal-sholat?province=...&kabkota=...&bulan=...&tahun=...` | Get monthly prayer schedule |

> **Note:** You must call `/init` first to populate cookies and province data before using the other endpoints.

## Project Structure

```
pysalat/
├── main.py          # FastAPI app entry point & startup
├── config.py        # Constants (URLs, headers, DB path, schemas)
├── db.py            # SQLite helpers
├── scraper.py       # HTTP requests & HTML parsing
├── utils.py         # Shared helpers (slugify, cookie loading)
├── routes/
│   ├── __init__.py  # Router aggregation
│   ├── init.py      # GET /init
│   ├── kabupaten.py # GET /kabupaten-kota
│   └── jadwal.py    # GET /jadwal-sholat
├── api.http         # Sample requests (VS Code REST Client)
└── pyproject.toml
```

## License

Unlicensed — personal project.
