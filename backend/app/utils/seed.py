# backend/app/utils/seed.py
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import AssemblyLine, ConveyorBelt, Stage

def seed_factory(db: Session) -> dict:
    """
    Idempotently seed:
      - 2 lines (Transit Line A, Freight Line B)
      - 3 belts per line
      - 6 ordered stages per line
    Returns a summary dict.
    """
    # already seeded?
    if db.execute(select(AssemblyLine.id).limit(1)).first():
        return {"status": "skipped", "reason": "already seeded"}

    stages_order = [
        ("Mixing", 1), ("Molding", 2), ("Curing", 3),
        ("Grinding", 4), ("Painting", 5), ("Final QC", 6),
    ]

    created = {"lines": [], "belts": 0, "stages": 0}

    for line_name in ("Transit Line A", "Freight Line B"):
        line = AssemblyLine(name=line_name)
        db.add(line); db.flush()  # get line.id

        belts = [ConveyorBelt(name=f"Belt {b}", line_id=line.id) for b in range(1, 4)]
        db.add_all(belts)

        stages = [Stage(name=n, sequence=s, line_id=line.id) for n, s in stages_order]
        db.add_all(stages)

        created["lines"].append(line_name)
        created["belts"] += len(belts)
        created["stages"] += len(stages)

    db.commit()
    return {"status": "ok", **created}