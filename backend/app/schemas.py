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

class MixIn(BaseModel):
    resin_pct: float
    fiber_pct: float
    metal_powder_pct: float
    filler_pct: float
    abrasives_pct: float
    binder_pct: float
    temp_c: float
    pressure_mpa: float
    cure_time_s: float
    moisture_pct: float

class PredictMixRequest(MixIn):
    brakepad_id: Optional[str] = None

class PredictMixResponse(BaseModel):
    label: Literal["PASS", "FAIL"]
    score: float
    explanation: Dict[str, float]
    model_version: str

class PredictImageRequest(BaseModel):
    brakepad_id: Optional[str] = None
    image_base64: Optional[str] = None

class PredictImageResponse(BaseModel):
    defects: List[str]
    stage_guess: Optional[str] = None
    score: float
    model_version: str