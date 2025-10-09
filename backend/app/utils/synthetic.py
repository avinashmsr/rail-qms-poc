from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models import AssemblyLine, ConveyorBelt, Stage, BrakePad
# enums may be present in your models; tolerate both enum and str usage
try:
    from ..models import PadStatus, PadType  # type: ignore
except Exception:
    PadStatus = None  # type: ignore
    PadType = None    # type: ignore


def _to_enum_or_str(enum_cls, name: str):
    """Return enum value if enum_cls exists, else the raw string."""
    if enum_cls is None:
        return name
    try:
        return getattr(enum_cls, name)
    except Exception:
        try:
            return enum_cls(name)
        except Exception:
            return name


def create_pads(
    db: Session,
    count: int,
    lines: int = 2,
    belts_per_line: int = 3,
) -> List[BrakePad]:
    """
    Create 'count' synthetic BrakePad rows distributed across existing lines/belts/stages.
    - If belts/stages are missing for a line, minimal ones are created.
    - Requires that /setup/seed has already created at least one AssemblyLine.
    """
    line_rows = db.execute(select(AssemblyLine)).scalars().all()
    if not line_rows:
        raise RuntimeError("No assembly lines found. Run /setup/seed first.")

    # Ensure each line has belts/stages (idempotent-ish)
    belts_by_line = {}
    stages_by_line = {}
    for ln in line_rows:
        belts = db.execute(
            select(ConveyorBelt).where(ConveyorBelt.line_id == ln.id)
        ).scalars().all()
        if not belts:
            for b in range(1, belts_per_line + 1):
                db.add(ConveyorBelt(name=f"Belt {b}", line_id=ln.id))
            db.flush()
            belts = db.execute(
                select(ConveyorBelt).where(ConveyorBelt.line_id == ln.id)
            ).scalars().all()

        stages = db.execute(
            select(Stage).where(Stage.line_id == ln.id).order_by(Stage.sequence)
        ).scalars().all()
        if not stages:
            defaults = [
                ("Mixing", 1), ("Molding", 2), ("Curing", 3),
                ("Grinding", 4), ("Painting", 5), ("Final QC", 6),
            ]
            for n, s in defaults:
                db.add(Stage(name=n, sequence=s, line_id=ln.id))
            db.flush()
            stages = db.execute(
                select(Stage).where(Stage.line_id == ln.id).order_by(Stage.sequence)
            ).scalars().all()

        belts_by_line[ln.id] = belts
        stages_by_line[ln.id] = stages

    rng = random.Random()
    pads_created: List[BrakePad] = []

    for i in range(count):
        ln = rng.choice(line_rows)
        belt = rng.choice(belts_by_line[ln.id])
        # bias toward early stages but allow any
        stages = stages_by_line[ln.id]
        stage = stages[min(rng.randint(0, len(stages) - 1), rng.randint(0, len(stages) - 1))]

        ptype_str = "TRANSIT" if rng.random() < 0.5 else "FREIGHT"
        status_roll = rng.random()
        if status_roll < 0.65:
            status_str = "PASSED"
        elif status_roll < 0.85:
            status_str = "IN_PROGRESS"
        else:
            status_str = "FAILED"

        serial_prefix = "TR" if ptype_str == "TRANSIT" else "FR"
        serial_number = f"{serial_prefix}-{ln.id:02d}-{belt.id:02d}-{i+1:05d}"

        pad = BrakePad(
            serial_number=serial_number,
            pad_type=_to_enum_or_str(PadType, ptype_str),
            status=_to_enum_or_str(PadStatus, status_str),
            line_id=ln.id,
            belt_id=belt.id,
            stage_id=stage.id,
            created_at=datetime.now(timezone.utc),
        )
        db.add(pad)
        pads_created.append(pad)

    db.flush()   # assign IDs
    db.commit()
    return pads_created


# Wrapper with the name you used elsewhere; keeps API compatibility
def generate_synthetic_pads(
    db: Session,
    count: int,
    lines: int = 2,
    belts_per_line: int = 3
):
    return create_pads(db, count=count, lines=lines, belts_per_line=belts_per_line)