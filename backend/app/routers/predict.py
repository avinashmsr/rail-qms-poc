from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..schemas import PredictMixRequest, PredictMixResponse, PredictImageRequest, PredictImageResponse
from ..ml.model import predict_mix
from ..ml.cv_defects import analyze_image
from ..models import Prediction, PredictionKind

router = APIRouter()

@router.post("/mix", response_model=PredictMixResponse)
def predict_mix_quality(req: PredictMixRequest, db: Session = Depends(get_db)):
    result = predict_mix(req.dict())
    pred = Prediction(
        brakepad_id=req.brakepad_id or "N/A",
        kind=PredictionKind.MIX,
        model_version=result["model_version"],
        label=result["label"],
        score=result["score"],
        explanation_json=result["explanation"],
    )
    db.add(pred); db.commit()
    return result


@router.post("/image", response_model=PredictImageResponse)
def predict_image(req: PredictImageRequest, db: Session = Depends(get_db)):
    result = analyze_image(req.image_base64, req.brakepad_id)
    pred = Prediction(
        brakepad_id=req.brakepad_id or "N/A",
        kind=PredictionKind.IMAGE,
        model_version=result["model_version"],
        label=",".join(result["defects"]),
        score=result["score"],
        explanation_json={"stage_guess": result.get("stage_guess")},
    )
    db.add(pred); db.commit()
    return result