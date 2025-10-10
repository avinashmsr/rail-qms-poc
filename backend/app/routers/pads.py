from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import BrakePad, AssemblyLine, ConveyorBelt, Stage

router = APIRouter()

@router.get("")
def list_pads(db: Session = Depends(get_db), line_id: int | None = None, status: str | None = None):
    q = db.query(BrakePad)
    if line_id:
        q = q.filter(BrakePad.line_id == line_id)
    if status:
        q = q.filter(BrakePad.status == status)
    return [
        {
            "id": p.id,
            "serial_number": p.serial_number,
            "pad_type": p.pad_type.value,
            "line_id": p.line_id,
            "belt_id": p.belt_id,
            "stage_id": p.stage_id,
            "status": p.status.value,
            "created_at": p.created_at.isoformat()
        } for p in q.order_by(BrakePad.created_at.desc()).limit(500)
    ]