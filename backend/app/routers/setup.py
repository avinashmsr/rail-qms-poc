from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import AssemblyLine, ConveyorBelt, Stage
from ..utils.seed import seed_factory


router = APIRouter()


@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    seed_factory(db)
    return {"status": "ok"}