from fastapi import APIRouter, Depends, HTTPException
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
def generate(count: int = 150, lines: int = 2, belts_per_line: int = 3, db: Session = Depends(get_db)):
    """
    1) Create synthetic BrakePad rows in DB
    2) Generate synthetic images for those pads
    3) Return a compact summary
    """
    # 1) Create pads in DB
    try:
        pads = generate_synthetic_pads(db, count=count, lines=lines, belts_per_line=belts_per_line, create_mixes=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"generate_synthetic_pads failed: {e!s}")

    # 2) Build image metadata from pads (be tolerant of Enum vs str)
    def to_pad_type(pt):
        try:
            return pt.value if hasattr(pt, "value") else str(pt)
        except Exception:
            return "TRANSIT"

    pad_infos = []
    for p in pads:
        pad_infos.append({
            "id": getattr(p, "id", None),
            "serial_number": getattr(p, "serial_number", None),
            "pad_type": to_pad_type(getattr(p, "pad_type", "TRANSIT")),
            "stage_name": getattr(getattr(p, "stage", None), "name", None),
        })

    # 3) Generate images
    try:
        images = generate_image_set(count=len(pad_infos) or count, pad_infos=pad_infos or None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"generate_image_set failed: {e!s}")

    return {
        "status": "ok",
        "pads_created": len(pads),
        "images_created": len(images),
        "image_dir": str(get_image_dir()),
    }