from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import math
from ..deps import get_db
from ..models import BrakePad

router = APIRouter()

def _list_pads_impl(db: Session, page:int, page_size:int, sort_by:str, sort_dir:str):

    # SORTING: validate & build the ORDER BY
    col = SORT_MAP.get(sort_by)
    if col is None:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by: {sort_by}")
    order = col.asc() if sort_dir.lower() == "asc" else col.desc()

    # total rows
    total = db.query(func.count(BrakePad.id)).scalar() or 0
    # normalize page if too large
    pages = max(1, math.ceil(total / page_size)) if total else 1
    page = min(page, pages)

    # SORTING applied here
    qset = (
        db.query(BrakePad)
        .order_by(order, BrakePad.id.asc())  # tie-breaker for stable pagination
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": [_pad_to_dict(p) for p in qset],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
        "sort_by": sort_by,
        "sort_dir": sort_dir.lower(),
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

# SORTING: allowlist of sortable columns (prevents SQL injection)
SORT_MAP = {
    "serial_number": BrakePad.serial_number,
    "pad_type":      BrakePad.pad_type,
    "status":        BrakePad.status,
    "line_id":       BrakePad.line_id,
    "belt_id":       BrakePad.belt_id,
    "stage_id":      BrakePad.stage_id,
    "batch_code":    getattr(BrakePad, "batch_code"),
    "created_at":    BrakePad.created_at,
}

# Canonical path → /pads  (no redirect)
@router.get("")
def list_pads_alias1(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),  # user-configurable in UI; backend caps at 100
    # SORTING: query params
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc", pattern="^(?i)(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """List brake pads (alias: '/pads')."""
    return _list_pads_impl(db, page, page_size, sort_by, sort_dir)

# Friendly alias → /pads/ (trailing slash)
@router.get("/")
def list_pads_alias2(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),  # user-configurable in UI; backend caps at 100
    # SORTING: query params
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc", pattern="^(?i)(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """List brake pads (alias: '/pads/')."""
    return _list_pads_impl(db, page, page_size, sort_by, sort_dir)