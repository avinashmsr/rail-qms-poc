from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models import (
    AssemblyLine, ConveyorBelt, Stage, BrakePad, MaterialMix, PadStatus, PadType
)

def _random_mix() -> dict:
    """
    Make a plausible material composition that sums to 100 (%),
    plus a few process parameters.
    """
    # Random weights -> normalize to 100, then round & fix remainder
    parts = [random.uniform(0.5, 1.5) for _ in range(5)]
    total = sum(parts)
    pct = [p / total * 100 for p in parts]
    # Assign names and round
    names = ["resin_pct", "metal_fiber_pct", "friction_modifier_pct", "binder_pct", "filler_pct"]
    rounded = [int(round(x)) for x in pct]
    # Fix rounding drift to sum exactly 100
    drift = 100 - sum(rounded)
    rounded[-1] += drift
    mix = dict(zip(names, rounded))
    # Add process params
    mix.update({
        "mix_temp_c": int(random.uniform(80, 140)), # mix temperature
        "press_ton": round(random.uniform(20, 60), 1), # press force (tons)
        "cure_minutes": int(random.uniform(30, 120)), # cure time
    })
    return mix

def _coerce_enum(value_str: str, enum_cls) -> object:
    """Coerce a string to the Enum member; raise if invalid -> fail fast."""
    return getattr(enum_cls, value_str)

def _make_batch_code(line_id: int, belt_id: int, when: datetime, rng: random.Random) -> str:
    """Deterministic-ish but unique enough for demo data."""
    return f"BC-{line_id:02d}{belt_id:02d}-{when:%Y%m%d}-{rng.randint(1000,9999)}"

def create_pads(
    db: Session,
    count: int,
    lines: int = 2,  # for API compatibility; we use existing seeded lines
    belts_per_line: int = 3,
    create_mixes: bool = True, # <-- default ON
) -> List[BrakePad]:
    """
    Create 'count' synthetic BrakePad rows distributed across existing lines/belts/stages.
    If a line has no belts/stages yet, minimal ones are created. Optionally creates a
    MaterialMix per pad for ML features.

    Requires that /setup/seed has already created at least one AssemblyLine.
    """
    line_rows = db.execute(select(AssemblyLine)).scalars().all()
    if not line_rows:
        raise RuntimeError("No assembly lines found. Run /setup/seed first.")

    # Ensure belts/stages per line (idempotent-ish)
    belts_by_line, stages_by_line = {}, {}
    for ln in line_rows:
        belts = db.execute(select(ConveyorBelt).where(ConveyorBelt.line_id == ln.id)).scalars().all()
        if not belts:
            for b in range(1, belts_per_line + 1):
                db.add(ConveyorBelt(name=f"Belt {b}", line_id=ln.id))
            db.flush()
            belts = db.execute(select(ConveyorBelt).where(ConveyorBelt.line_id == ln.id)).scalars().all()

        stages = db.execute(select(Stage).where(Stage.line_id == ln.id).order_by(Stage.sequence)).scalars().all()
        if not stages:
            for n, s in [("Mixing",1),("Molding",2),("Curing",3),("Grinding",4),("Painting",5),("Final QC",6)]:
                db.add(Stage(name=n, sequence=s, line_id=ln.id))
            db.flush()
            stages = db.execute(select(Stage).where(Stage.line_id == ln.id).order_by(Stage.sequence)).scalars().all()

        belts_by_line[ln.id] = belts
        stages_by_line[ln.id] = stages

    rng = random.Random()
    pads_created: List[BrakePad] = []

    for i in range(count):
        ln = rng.choice(line_rows)
        belt = rng.choice(belts_by_line[ln.id])
        stage = rng.choice(stages_by_line[ln.id])

        ptype_str = "TRANSIT" if rng.random() < 0.5 else "FREIGHT"
        status_roll = rng.random()
        status_str = "PASSED" if status_roll < 0.65 else ("IN_PROGRESS" if status_roll < 0.85 else "FAILED")

        now = datetime.now(timezone.utc)
        batch_code = _make_batch_code(ln.id, belt.id, now, rng)

        serial_prefix = "TR" if ptype_str == "TRANSIT" else "FR"
        serial_number = f"{serial_prefix}-{ln.id:02d}-{belt.id:02d}-{i+1:05d}"

        pad = BrakePad(
            serial_number=serial_number,
            pad_type=_coerce_enum(ptype_str, PadType),
            status=_coerce_enum(status_str, PadStatus),
            line_id=ln.id,
            belt_id=belt.id,
            stage_id=stage.id,
            created_at=now,
            batch_code=batch_code
        )
        db.add(pad)
        db.flush() # need pad.id for MaterialMix FK

        if create_mixes:
            mix = _random_mix()
            db.add(MaterialMix(
                pad_id=pad.id,
                resin_pct=mix["resin_pct"],
                metal_fiber_pct=mix["metal_fiber_pct"],
                friction_modifier_pct=mix["friction_modifier_pct"],
                binder_pct=mix["binder_pct"],
                filler_pct=mix["filler_pct"],
                mix_temp_c=mix["mix_temp_c"],
                press_ton=mix["press_ton"],
                cure_minutes=mix["cure_minutes"],
                created_at=now,
            ))

        pads_created.append(pad)

    db.commit()
    return pads_created

# Wrapper function - Convenience alias - other parts of the app expect this name
def generate_synthetic_pads(db: Session, count: int, lines: int = 2, belts_per_line: int = 3, create_mixes: bool = True):
    return create_pads(db, count=count, lines=lines, belts_per_line=belts_per_line, create_mixes=create_mixes)