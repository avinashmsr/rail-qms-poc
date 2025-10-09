from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..utils.seed import seed_factory
from ..utils.synthetic import generate_synthetic_pads  # for pad generation
from ..utils.images import generate_image_set, get_image_dir

router = APIRouter()

@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    return seed_factory(db)

@router.post("/generate")
def generate(count: int = 100, db: Session = Depends(get_db)):
    pad_infos = []
    try:
        # DB pads
        created = generate_synthetic_pads(db, count=count)  # returns list of ORM objects or dicts
        pad_infos = [
            {"id": p.id, "serial_number": getattr(p, "serial_number", None), "pad_type": getattr(p, "pad_type", "TRANSIT")}
            for p in created
        ]
    except Exception:
        # Fallback to images-only if synthetic pad creation isn't present
        pad_infos = []

    images = generate_image_set(count=count, pad_infos=pad_infos or None)
    return {
        "status": "ok",
        "image_dir": str(get_image_dir()),
        "generated": images,
    }