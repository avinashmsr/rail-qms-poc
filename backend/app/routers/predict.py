from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..deps import get_db
from ..models import Prediction, PredictionKind, BrakePad

# ✅ ML functions live here (as observed)
from ..ml.model import predict_mix
from ..ml.cv_defects import analyze_image

# Pydantic schemas – existing schema names
from ..schemas import (
    PredictMixRequest, PredictMixResponse,
    PredictImageRequest, PredictImageResponse,
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
        score=result.get("score", 0.0),
        explanation_json=result.get("explanation"),  # shap/weights/etc.
    )
    db.add(pred)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # if someone sends an invalid FK despite our check
        raise HTTPException(status_code=400, detail="Invalid brakepad_id")
   
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