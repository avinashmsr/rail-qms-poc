from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import BrakePad

router = APIRouter()

def _list_pads_impl(db: Session, line_id: int | None, status: str | None):
    q = db.query(BrakePad)
    if line_id is not None:
        q = q.filter(BrakePad.line_id == line_id)
    if status is not None:
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
            "created_at": p.created_at.isoformat(),
        }
        for p in q.order_by(BrakePad.created_at.desc()).limit(500)
    ]

# Canonical path → /pads  (no redirect)
@router.get("")
def list_pads_no_slash(line_id: int | None = None, status: str | None = None, db: Session = Depends(get_db)):
    """List brake pads (alias: '/pads')."""
    return _list_pads_impl(db, line_id, status)

# Friendly alias → /pads/ (trailing slash)
@router.get("/")
def list_pads_with_slash(line_id: int | None = None, status: str | None = None, db: Session = Depends(get_db)):
    """List brake pads (alias: '/pads/')."""
    return _list_pads_impl(db, line_id, status)