import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import engine
from .models import Base
from .routers import lines, pads, stats, setup, stages

# -----------------------------------------------------------------------------
# Create tables (if not using Alembic for migrations)
# -----------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# -----------------------------------------------------------------------------
# App init
# -----------------------------------------------------------------------------
app = FastAPI(title="Rail QMS PoC", version="0.1.0")

# -----------------------------------------------------------------------------
# CORS (allow local dev UIs on 5173 React and 5174 Vue)
# -----------------------------------------------------------------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # make explicit; avoids wildcard+credentials quirks
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Ensure an images directory exists
#   - Default is ./app_data/images for local dev (Windows/macOS/Linux)
#   - If IMAGE_DIR is set (e.g., in Docker), that takes precedence
#   - here we handle both container & local seamlessly.
# -----------------------------------------------------------------------------
DEFAULT_IMG_DIR = Path(__file__).resolve().parent.parent / "app_data" / "images"
IMG_DIR = Path(os.getenv("IMAGE_DIR", str(DEFAULT_IMG_DIR)))
IMG_DIR.mkdir(parents=True, exist_ok=True)

# Optional: serve the images - can view them in the browser
# e.g., http://localhost:8000/images/some_synthetic_image.png
app.mount("/images", StaticFiles(directory=str(IMG_DIR)), name="images")

# -----------------------------------------------------------------------------
# Routers
# -----------------------------------------------------------------------------
app.include_router(lines.router, prefix="/lines", tags=["lines"])
app.include_router(pads.router, prefix="/pads", tags=["pads"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
app.include_router(setup.router, prefix="/setup", tags=["setup"])
app.include_router(stages.router, prefix="/stages", tags=["stages"])

# -----------------------------------------------------------------------------
# Basic health/root endpoints
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"ok": True, "service": "Rail QMS PoC"}

@app.get("/health")
def health():
    return {"status": "ok"}