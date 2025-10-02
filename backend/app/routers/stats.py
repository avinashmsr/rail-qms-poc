from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import BrakePad, AssemblyLine, PadStatus


router = APIRouter()


@router.get("/lines")
def line_stats(db: Session = Depends(get_db)):
lines = db.query(AssemblyLine).all()
out = []
for ln in lines:
q = db.query(BrakePad).filter(BrakePad.line_id == ln.id)
total = q.count()
passed = q.filter(BrakePad.status == PadStatus.PASSED).count()
failed = q.filter(BrakePad.status == PadStatus.FAILED).count()
inprog = q.filter(BrakePad.status == PadStatus.IN_PROGRESS).count()
out.append({"line": ln.name, "total": total, "passed": passed, "failed": failed, "in_progress": inprog})
return out