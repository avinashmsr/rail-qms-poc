from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..utils.seed import seed_factory
from ..utils.synthetic import generate_synthetic_pads  # DB-side generator
from ..utils.images import generate_image_set, get_image_dir

router = APIRouter()

@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    return seed_factory(db)

@router.post("/generate")
def generate(count: int = 150, lines: int = 2, belts_per_line: int = 3,
             db: Session = Depends(get_db)):
    """
    1) Create synthetic BrakePad rows in DB
    2) Generate synthetic images for those pads
    3) Return a compact summary
    """
    # 1) DB rows
    pads = generate_synthetic_pads(db, count=count, lines=lines, belts_per_line=belts_per_line)

    # 2) Images tied to those pads (serial/type/stage if available)
    pad_infos = []
    for p in pads:
        pad_type = getattr(p, "pad_type", "TRANSIT")
        if hasattr(pad_type, "value"):
            pad_type = pad_type.value
        pad_infos.append({
            "id": p.id,
            "serial_number": getattr(p, "serial_number", None),
            "pad_type": pad_type,
            "stage_name": getattr(getattr(p, "stage", None), "name", None),
        })

    images = generate_image_set(count=len(pad_infos), pad_infos=pad_infos)
    return {
        "status": "ok",
        "pads_created": len(pads),
        "images_created": len(images),
        "image_dir": str(get_image_dir()),
    }