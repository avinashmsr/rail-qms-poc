from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import BrakePad, AssemblyLine, PadStatus

router = APIRouter()

def _line_stats_impl(db: Session):
    lines = db.query(AssemblyLine).all()
    out = []
    for ln in lines:
        q = db.query(BrakePad).filter(BrakePad.line_id == ln.id)
        total = q.count()
        passed = q.filter(BrakePad.status == PadStatus.PASSED).count()
        failed = q.filter(BrakePad.status == PadStatus.FAILED).count()
        inprog = q.filter(BrakePad.status == PadStatus.IN_PROGRESS).count()
        out.append(
            {"line": ln.name, "total": total, "passed": passed, "failed": failed, "in_progress": inprog}
        )
    return out

# Canonical path used by frontend: /stats/lines
@router.get("/lines")
def line_stats(db: Session = Depends(get_db)):
    """Pass/Fail/In-progress counts per line — canonical: '/stats/lines'."""
    return _line_stats_impl(db)

# Optional convenience alias: /stats  (same payload)
@router.get("")
@router.get("/")
def line_stats_root(db: Session = Depends(get_db)):
    """Alias for '/stats': returns the same line stats."""
    return _line_stats_impl(db)