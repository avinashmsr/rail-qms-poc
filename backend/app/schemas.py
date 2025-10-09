from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict

class LineStats(BaseModel):
    line: str
    total: int
    passed: int
    failed: int
    in_progress: int

class GenerateSyntheticRequest(BaseModel):
    count: int = Field(gt=0, le=2000)
    lines: int = 2
    belts_per_line: int = 3