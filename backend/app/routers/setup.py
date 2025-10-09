from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..utils.seed import seed_factory
from ..utils.synthetic import create_pads
from ..utils.images import generate_image_set
from ..models import AssemblyLine
from ..schemas import GenerateSyntheticRequest

router = APIRouter()

@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    return seed_factory(db)

@router.post("/generate")
def generate(req: GenerateSyntheticRequest, db: Session = Depends(get_db)):
    lines = db.query(AssemblyLine).all()
    line_ids = [l.id for l in lines]
    belts_map = {l.id:[b.id for b in l.belts] for l in lines}
    stages_map = {l.id:[s.id for s in l.stages] for l in lines}
    pads = create_pads(db, req.count, line_ids, belts_map, stages_map)
    out = generate_image_set("/app/app_data/images", min(200, req.count))
    return {"pads": len(pads), "images": len(out), "dir": "/app/app_data/images"}