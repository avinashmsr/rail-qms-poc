from pydantic import BaseModel, Field, AliasChoices, ConfigDict
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
    label: str | None = None
    score: float | None = None
    explanation: dict[str, float] | None = None
    
    ml_model_version: str = Field(
        ...,
        serialization_alias="model_version",
        validation_alias=AliasChoices("model_version", "ml_model_version"),
    )
    # makes it flexible to populate by field-name too
    model_config = ConfigDict(populate_by_name=True)

class PredictImageRequest(BaseModel):
    brakepad_id: Optional[str] = None
    image_base64: Optional[str] = None

class PredictImageResponse(BaseModel):
    defects: list[str] = []
    score: float | None = None
    stage_guess: str | None = None

    ml_model_version: str = Field(
        ...,
        serialization_alias="model_version",
        validation_alias=AliasChoices("model_version", "ml_model_version"),
    )

    model_config = ConfigDict(populate_by_name=True)