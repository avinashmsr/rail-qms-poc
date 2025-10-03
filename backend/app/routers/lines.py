from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..deps import get_db
from ..models import (
    AssemblyLine,
    ConveyorBelt,
    Stage,
    BrakePad,
    PadStatus,
)

router = APIRouter()


def _line_payload(db: Session, ln: AssemblyLine, with_counts: bool = True):
    belts = db.query(ConveyorBelt).filter(ConveyorBelt.line_id == ln.id).all()
    stages = (
        db.query(Stage)
        .filter(Stage.line_id == ln.id)
        .order_by(Stage.sequence.asc())
        .all()
    )

    payload = {
        "id": ln.id,
        "name": ln.name,
        "belts": [{"id": b.id, "name": b.name} for b in belts],
        "stages": [{"id": s.id, "name": s.name, "sequence": s.sequence} for s in stages],
    }

    if with_counts:
        total = db.query(func.count(BrakePad.id)).filter(BrakePad.line_id == ln.id).scalar() or 0
        passed = (
            db.query(func.count(BrakePad.id))
            .filter(BrakePad.line_id == ln.id, BrakePad.status == PadStatus.PASSED)
            .scalar()
            or 0
        )
        failed = (
            db.query(func.count(BrakePad.id))
            .filter(BrakePad.line_id == ln.id, BrakePad.status == PadStatus.FAILED)
            .scalar()
            or 0
        )
        inprog = (
            db.query(func.count(BrakePad.id))
            .filter(BrakePad.line_id == ln.id, BrakePad.status == PadStatus.IN_PROGRESS)
            .scalar()
            or 0
        )
        payload["pad_counts"] = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "in_progress": inprog,
        }

    return payload


@router.get("")
def list_lines(db: Session = Depends(get_db), with_counts: bool = True):
    """List all assembly lines with belts, stages, and optional pad counts."""
    lines = db.query(AssemblyLine).all()
    return [_line_payload(db, ln, with_counts=with_counts) for ln in lines]


@router.get("/{line_id}")
def get_line(line_id: int, db: Session = Depends(get_db), with_counts: bool = True):
    """Get a single line by ID with belts, stages, and optional pad counts."""
    ln = db.get(AssemblyLine, line_id)
    if not ln:
        raise HTTPException(status_code=404, detail="Line not found")
    return _line_payload(db, ln, with_counts=with_counts)


@router.get("/{line_id}/belts")
def list_line_belts(line_id: int, db: Session = Depends(get_db)):
    """List belts for a specific line."""
    ln = db.get(AssemblyLine, line_id)
    if not ln:
        raise HTTPException(status_code=404, detail="Line not found")
    belts = db.query(ConveyorBelt).filter(ConveyorBelt.line_id == ln.id).all()
    return [{"id": b.id, "name": b.name} for b in belts]


@router.get("/{line_id}/stages")
def list_line_stages(line_id: int, db: Session = Depends(get_db)):
    """List stages for a specific line (ordered by sequence)."""
    ln = db.get(AssemblyLine, line_id)
    if not ln:
        raise HTTPException(status_code=404, detail="Line not found")
    stages = (
        db.query(Stage)
        .filter(Stage.line_id == ln.id)
        .order_by(Stage.sequence.asc())
        .all()
    )
    return [{"id": s.id, "name": s.name, "sequence": s.sequence} for s in stages]