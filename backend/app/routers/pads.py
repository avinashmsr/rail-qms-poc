from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import math
from ..deps import get_db
from ..models import BrakePad

router = APIRouter()

def _list_pads_impl(db: Session, page:int, page_size:int):

    # total rows
    total = db.query(func.count(BrakePad.id)).scalar() or 0

    # normalize page if too large (e.g., after deletes)
    pages = max(1, math.ceil(total / page_size)) if total else 1
    page = min(page, pages)

    # page slice
    q = db.query(BrakePad).order_by(BrakePad.created_at.desc())
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [_pad_to_dict(p) for p in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }

def _enum_name_or_value(x):
    return getattr(x, "name", x)

def _pad_to_dict(p: BrakePad) -> dict:
    return {
        "id": p.id,
        "serial_number": p.serial_number,
        "pad_type": _enum_name_or_value(p.pad_type),
        "status": _enum_name_or_value(p.status),
        "line_id": p.line_id,
        "belt_id": p.belt_id,
        "stage_id": p.stage_id,
        "created_at": p.created_at,
        "batch_code": getattr(p, "batch_code", None),
    }

# Canonical path → /pads  (no redirect)
@router.get("")
def list_pads_alias1(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),  # user-configurable in UI; backend caps at 100
    db: Session = Depends(get_db)
):
    """List brake pads (alias: '/pads')."""
    return _list_pads_impl(db, page, page_size)

# Friendly alias → /pads/ (trailing slash)
@router.get("/")
def list_pads_alias2(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),  # user-configurable in UI; backend caps at 100
    db: Session = Depends(get_db)
):
    """List brake pads (alias: '/pads/')."""
    return _list_pads_impl(db, page, page_size)