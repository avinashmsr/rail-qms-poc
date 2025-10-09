import os, random, string
from sqlalchemy.orm import Session
from ..models import BrakePad, PadType, PadStatus, MaterialMix

def rand_sn():
    return "SN-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

def create_pads(db: Session, count: int, line_ids: list[int], belt_ids_map: dict[int, list[int]], stage_ids_map: dict[int, list[int]]):
    pads = []
    for i in range(count):
        ln = random.choice(line_ids)
        belt = random.choice(belt_ids_map[ln])
        stage = random.choice(stage_ids_map[ln])
        pad = BrakePad(
            serial_number=rand_sn(),
            pad_type=random.choice([PadType.TRANSIT, PadType.FREIGHT]),
            batch_code=f"BATCH-{random.randint(100,999)}",
            line_id=ln, belt_id=belt, stage_id=stage,
            status=random.choice([PadStatus.IN_PROGRESS, PadStatus.PASSED, PadStatus.FAILED])
            )
        db.add(pad); db.flush()
        mix = MaterialMix(
            brakepad_id=pad.id,
            resin_pct=random.uniform(10, 20),
            fiber_pct=random.uniform(7, 16),
            metal_powder_pct=random.uniform(18, 35),
            filler_pct=random.uniform(8, 22),
            abrasives_pct=random.uniform(4, 14),
            binder_pct=random.uniform(2, 10),
            temp_c=random.uniform(130, 200),
            pressure_mpa=random.uniform(25, 55),
            cure_time_s=random.uniform(800, 1600),
            moisture_pct=random.uniform(0.1, 1.2),
            )
        db.add(mix)
        pads.append(pad)
    db.commit()
    return pads

def generate_synthetic_pads(db, count: int, lines: int = 2, belts_per_line: int = 3):
    return create_pads(db, count=count, lines=lines, belts_per_line=belts_per_line)