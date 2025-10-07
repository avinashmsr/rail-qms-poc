from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..utils.seed import seed_factory

router = APIRouter()

@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    return seed_factory(db)
