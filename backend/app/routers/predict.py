from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from ..deps import get_db
from ..models import Prediction, PredictionKind, BrakePad, MaterialMix

# ✅ ML functions live here (as observed)
from ..ml.model import predict_mix
from ..ml.cv_defects import analyze_image

# Pydantic schemas – existing schema names
from ..schemas import (
    PredictMixRequest, PredictMixResponse,
    PredictImageRequest, PredictImageResponse, PredictPadResponse
)

router = APIRouter()

@router.post("/material_mix", response_model=PredictMixResponse, name="predict:material_mix")
def predict_material_mix(req: PredictMixRequest, db: Session = Depends(get_db)):
    """
    Predict quality from a material mix/process parameters payload.
    Frontend calls POST /predict/material_mix.
    """
    try:
        result = predict_mix(req.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"predict_mix failed: {e}")

    # Log prediction for audit/expert-in-the-loop
    # use None unless caller provided a real pad ID
    bp_id = getattr(req, "brakepad_id", None) or None
    if bp_id:
        exists = db.query(BrakePad.id).filter(BrakePad.id == bp_id).first()
        if not exists:
            raise HTTPException(status_code=400, detail=f"Unknown brakepad_id: {bp_id}")
        
    pred = Prediction(
        brakepad_id=bp_id,                    # ← None is OK now
        kind=PredictionKind.MIX,
        model_version=result.get("model_version", "demo"),
        label=result.get("label"),
        score=result.get("score", 0.0),           # score = P(FAIL)
        explanation_json=result.get("explanation"),  # shap/weights/etc.
    )
    db.add(pred)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # if someone sends an invalid FK despite our check
        raise HTTPException(status_code=400, detail="Invalid brakepad_id")

    # result already includes quality/probability (UI aliases)
    return result

# Back-compat alias so older clients using /predict/mix continue to work
@router.post("/mix", response_model=PredictMixResponse, include_in_schema=False)
def predict_material_mix_alias(req: PredictMixRequest, db: Session = Depends(get_db)):
    return predict_material_mix(req, db)


@router.post("/image", response_model=PredictImageResponse, name="predict:image")
def predict_image(req: PredictImageRequest, db: Session = Depends(get_db)):
    """
    Run the CV model over a base64 image (synthetic or captured) and return detected defects.
    """
    try:
        result = analyze_image(req.image_base64, req.brakepad_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"analyze_image failed: {e}")

    bp_id = req.brakepad_id or None
    if bp_id:
        exists = db.query(BrakePad.id).filter(BrakePad.id == bp_id).first()
        if not exists:
            raise HTTPException(400, detail=f"Unknown brakepad_id: {bp_id}")

    pred = Prediction(
        brakepad_id=bp_id,
        kind=PredictionKind.IMAGE,
        model_version=result.get("model_version", "demo"),
        label=",".join(result.get("defects", [])),
        score=result.get("score", 0.0),
        explanation_json={"stage_guess": result.get("stage_guess")},
    )
    db.add(pred)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid brakepad_id")

    return result

@router.get("/pad", response_model=PredictPadResponse, name="predict:pad")
def predict_for_pad(
    id: str = Query(..., description="Pad UUID or serial_number"),
    db: Session = Depends(get_db),
):
    """
    Predict quality for a *specific pad* by loading its latest MaterialMix
    and calling the same predict_mix() logic under the hood.
    Accepts either BrakePad.id (UUID) or BrakePad.serial_number.
    """
    # 1) Find the pad by id or serial_number
    pad = (
        db.query(BrakePad)
        .filter(or_(BrakePad.id == id, BrakePad.serial_number == id))
        .first()
    )
    if not pad:
        raise HTTPException(status_code=404, detail=f"Pad not found: {id}")

    # 2) Get the most recent material mix for this pad
    mix = (
        db.query(MaterialMix)
        .filter(MaterialMix.brakepad_id == pad.id)
        .order_by(MaterialMix.id.desc())
        .first()
    )
    if not mix:
        raise HTTPException(
            status_code=400,
            detail=f"No material mix found for pad {pad.serial_number or pad.id}",
        )

    # 3) Build payload expected by predict_mix() The exact features we used to predict (matches model.py)
    mix_payload = {
        "resin_pct":        mix.resin_pct,
        "fiber_pct":        mix.fiber_pct,
        "metal_powder_pct": mix.metal_powder_pct,
        "filler_pct":       mix.filler_pct,
        "abrasives_pct":    mix.abrasives_pct,
        "binder_pct":       mix.binder_pct,
        "temp_c":           mix.temp_c,
        "pressure_mpa":     mix.pressure_mpa,
        "cure_time_s":      mix.cure_time_s,
        "moisture_pct":     mix.moisture_pct,
    }

    # 4) Run the model
    try:
        raw = predict_mix(mix_payload)  # returns label, score=P(FAIL), confidence, quality/probability, model_version
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"predict_mix failed: {e}")

    # 5) Persist for audit / expert-in-the-loop Log prediction
    pred = Prediction(
        brakepad_id=pad.id,
        kind=PredictionKind.MIX,  # reusing MIX since we predicted from the material mix
        model_version=raw.get("model_version", "demo"),
        label=raw.get("label"),
        score=raw.get("score", 0.0),
        explanation_json=raw.get("explanation"),
    )
    db.add(pred)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to log prediction")

    # 6) Enrich response with pad meta + material mix used
    return {
        **raw,
        "pad": {"id": pad.id, "serial_number": pad.serial_number},
        "material_mix": mix_payload,
    }