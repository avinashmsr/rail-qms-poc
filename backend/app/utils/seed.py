from sqlalchemy.orm import Session
from ..models import AssemblyLine, ConveyorBelt, Stage


def seed_factory(db: Session):
    # idempotent seed
    if db.query(AssemblyLine).count() > 0:
        return
    stages_order = [
        ("Mixing", 1), ("Molding", 2), ("Curing", 3), ("Grinding", 4), ("Painting", 5), ("Final QC", 6)
        ]
    for i, line_name in enumerate(["Transit Line A", "Freight Line B"], start=1):
        line = AssemblyLine(name=line_name)
        db.add(line); db.flush()
        for b in range(1, 4):
            db.add(ConveyorBelt(name=f"Belt {b}", line_id=line.id))
        for name, seq in stages_order:
            db.add(Stage(name=name, sequence=seq, line_id=line.id))
    db.commit()