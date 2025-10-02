from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict

class LineStats(BaseModel):
line: str
total: int
passed: int
failed: int
in_progress: int