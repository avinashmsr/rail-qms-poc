from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import math
from ..deps import get_db
from ..models import BrakePad, PadStatus, PadType, Stage  # PadStatus, PadType enums in models

router = APIRouter()

def _list_pads_impl(
        db: Session, 
        page:int, 
        page_size:int, 
        sort_by:str, 
        sort_dir:str,
        status: list[str] | None = Query(None),
        pad_type: list[str] | None = Query(None),
        line_id: int | None = Query(None),
        belt_id: int | None = Query(None),
        stage_id: int | None = Query(None),
        q: str | None = Query(None, description="Search serial_number or batch_code"),
        ):

    # Build filters
    filters = []
    st_enums = _coerce_enum_list(status, PadStatus)
    if st_enums:
        filters.append(BrakePad.status.in_(st_enums))

    pt_enums = _coerce_enum_list(pad_type, PadType)
    if pt_enums:
        filters.append(BrakePad.pad_type.in_(pt_enums))

    if line_id:
        filters.append(BrakePad.line_id == line_id)
    if belt_id:
        filters.append(BrakePad.belt_id == belt_id)
    if stage_id:
        filters.append(BrakePad.stage_id == stage_id)

    if q:
        ql = f"%{q.strip()}%"
        # serial or batch_code (batch_code may be missing in some schemas; getattr guards)
        col_batch = getattr(BrakePad, "batch_code")
        filters.append(
            (BrakePad.serial_number.ilike(ql)) | (col_batch.ilike(ql))
        )

    # Validate & build sorting
    col = SORT_MAP.get(sort_by)
    if col is None:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by: {sort_by}")
    order = col.asc() if sort_dir.lower() == "asc" else col.desc()

    # Total (filtered)
    total = db.query(func.count(BrakePad.id)).filter(*filters).scalar() or 0
    pages = max(1, math.ceil(total / page_size)) if total else 1
    page = min(page, pages)

    # Page slice
    qset = (
        db.query(BrakePad)
        .options(joinedload(BrakePad.stage))      # avoid N+1
        .filter(*filters)
        .order_by(order, BrakePad.id.asc())  # tie-breaker for stable paging
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
         "filters": {
            "status": status, "pad_type": pad_type,
            "line_id": line_id, "belt_id": belt_id, "stage_id": stage_id, "q": q,
        },
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
        "stage_id": p.stage_id, # this is raw Foreign Key
        "stage_name": getattr(p.stage, "name", None),   # ← user-friendly attribute
        "stage_seq": getattr(p.stage, "sequence", None),
        "batch_code": getattr(p, "batch_code", None),
        "created_at": p.created_at,
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

# FILTERING: helper to coerce query strings -> Enum members
def _coerce_enum_list(values, enum_cls):
    if not values: return None
    out = []
    for v in values:
        try:
            out.append(getattr(enum_cls, v.strip()))
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid {enum_cls.__name__} value: {v}")
    return out

# Canonical path → /pads  (no redirect)
@router.get("")
def list_pads_alias1(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),  # user-configurable in UI; backend caps at 100
    # SORTING: query params
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc", pattern="^(?i)(asc|desc)$"),
    # FILTERING: accept repeated params (?status=FAILED&status=PASSED) or comma form
    status: list[str] | None = Query(None),
    pad_type: list[str] | None = Query(None),
    line_id: int | None = Query(None),
    belt_id: int | None = Query(None),
    stage_id: int | None = Query(None),
    q: str | None = Query(None, description="Search serial_number or batch_code"),
    db: Session = Depends(get_db)
):
    """List brake pads (alias: '/pads')."""
    return _list_pads_impl(db, page, page_size, sort_by, sort_dir, status, pad_type, line_id, belt_id, stage_id, q)

# Friendly alias → /pads/ (trailing slash)
@router.get("/")
def list_pads_alias2(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),  # user-configurable in UI; backend caps at 100
    # SORTING: query params
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc", pattern="^(?i)(asc|desc)$"),
    # FILTERING: accept repeated params (?status=FAILED&status=PASSED) or comma form
    status: list[str] | None = Query(None),
    pad_type: list[str] | None = Query(None),
    line_id: int | None = Query(None),
    belt_id: int | None = Query(None),
    stage_id: int | None = Query(None),
    q: str | None = Query(None, description="Search serial_number or batch_code"),
    db: Session = Depends(get_db)
):
    """List brake pads (alias: '/pads/')."""
    return _list_pads_impl(db, page, page_size, sort_by, sort_dir, status, pad_type, line_id, belt_id, stage_id, q)