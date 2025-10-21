from pydantic import BaseModel, Field, AliasChoices, ConfigDict, model_validator
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
    resin_pct: float = Field(ge=0, le=100)
    fiber_pct: float = Field(ge=0, le=100)
    metal_powder_pct: float = Field(ge=0, le=100)
    filler_pct: float = Field(ge=0, le=100)
    abrasives_pct: float = Field(ge=0, le=100)
    binder_pct: float = Field(ge=0, le=100)
    temp_c: float
    pressure_mpa: float
    cure_time_s: float
    moisture_pct: float = Field(ge=0, le=100)

    # prefer forbidding unknowns so clients can’t send typos
    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def _sum_to_100(self):
        EPS = 0.01
        total = (
            float(self.resin_pct) + float(self.fiber_pct) + float(self.metal_powder_pct) +
            float(self.filler_pct) + float(self.abrasives_pct) + float(self.binder_pct)
        )
        if abs(total - 100.0) > EPS:
            raise ValueError(f"Material mix percentages must sum to 100%. Got {total:.2f}%.")
        return self

class PredictMixRequest(MixIn):
    brakepad_id: Optional[str] = None

class PredictMixResponse(BaseModel):
    label: str | None = None
    score: float | None = None
    confidence: float | None = None
    explanation: dict[str, float] | None = None
    quality: str | None = None
    probability: float | None = None

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

# --- NEW small DTOs for pad + mix ---
class MaterialMixOut(BaseModel):
    resin_pct: float | None = None
    fiber_pct: float | None = None
    metal_powder_pct: float | None = None
    filler_pct: float | None = None
    abrasives_pct: float | None = None
    binder_pct: float | None = None
    temp_c: float | None = None
    pressure_mpa: float | None = None
    cure_time_s: float | None = None
    moisture_pct: float | None = None

class PadMeta(BaseModel):
    id: str
    serial_number: str | None = None

# --- NEW: response for /predict/pad that includes pad & material_mix ---
class PredictPadResponse(PredictMixResponse):
    pad: PadMeta | None = None
    material_mix: MaterialMixOut | None = None