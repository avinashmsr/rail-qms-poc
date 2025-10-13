from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import Stage

router = APIRouter()

@router.get("")  # GET /stages
def list_stages(line_id: int | None = Query(None), db: Session = Depends(get_db)):
    q = db.query(Stage)
    if line_id:
        q = q.filter(Stage.line_id == line_id)
    rows = q.order_by(Stage.sequence.asc(), Stage.id.asc()).all()
    return [{"id": s.id, "name": s.name, "sequence": s.sequence, "line_id": s.line_id} for s in rows]