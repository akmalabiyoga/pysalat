"""pysalat — Prayer schedule API backed by Bimas Islam data."""

import logging
import os

from fastapi import FastAPI

from config import DATA_DIR, DB_SCHEMAS
from db import init_db
from routes import router

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="pysalat",
    description="Indonesian prayer schedule API (data from Bimas Islam)",
    version="0.1.0",
)

app.include_router(router)


@app.on_event("startup")
def on_startup():
    """Ensure the data directory and database tables exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    init_db(DB_SCHEMAS)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
