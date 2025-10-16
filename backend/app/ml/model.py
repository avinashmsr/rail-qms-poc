import os
import math, random

FEATURES = [
    "resin_pct","fiber_pct","metal_powder_pct","filler_pct","abrasives_pct","binder_pct",
    "temp_c","pressure_mpa","cure_time_s","moisture_pct"
]

MODEL_VERSION = "mix-baseline-0.1"

# Fail decision threshold (env overrideable)
MIX_FAIL_THRESHOLD = float(os.getenv("MIX_FAIL_THRESHOLD", "0.5"))
# Optional AT_RISK band via env: e.g. "0.4,0.6" (leave empty to disable)
_MIX_RISK_BAND = os.getenv("MIX_RISK_BAND", "").strip()
if _MIX_RISK_BAND:
    try:
        LOW, HIGH = [float(x) for x in _MIX_RISK_BAND.split(",", 1)]
    except Exception:
        LOW, HIGH = None, None
else:
    LOW, HIGH = None, None

# crude scoring: weighted deviations from nominal ranges
NOMINAL = {
    "resin_pct": (12, 18),
    "fiber_pct": (8, 14),
    "metal_powder_pct": (20, 30),
    "filler_pct": (10, 20),
    "abrasives_pct": (5, 12),
    "binder_pct": (3, 8),
    "temp_c": (140, 190),
    "pressure_mpa": (30, 50),
    "cure_time_s": (900, 1400),
    "moisture_pct": (0.2, 0.8),
}

WEIGHTS = {k: 1.0 for k in FEATURES}
WEIGHTS["moisture_pct"] = 1.5
WEIGHTS["temp_c"] = 1.2
WEIGHTS["pressure_mpa"] = 1.2

def _deviation_score(x, lo, hi):
    if x < lo:
        return (lo - x) / max(1e-6, lo)
    if x > hi:
        return (x - hi) / max(1e-6, hi)
    return 0.0

def score_features(row: dict):
    """
    Returns:
      label: str ("PASS"/"FAIL"/"AT_RISK" if band enabled)
      risk:  float in [0,1], explicitly P(FAIL)
      contribs: dict[str, float] raw contributions per feature
    """
    contribs = {}
    total = 0.0
    for k in FEATURES:
        lo, hi = NOMINAL[k]
        d = _deviation_score(float(row[k]), lo, hi)
        c = WEIGHTS[k] * d
        contribs[k] = c
        total += c

    # Map deviation sum to a probability-like risk of FAIL
    risk = min(1.0, total / 5.0)  # “5.0” just scales the synthetic PoC

    # Decide label
    if LOW is not None and HIGH is not None and LOW < HIGH:
        if risk < LOW:
            label = "PASS"
        elif risk > HIGH:
            label = "FAIL"
        else:
            label = "AT_RISK"
    else:
        label = "FAIL" if risk >= MIX_FAIL_THRESHOLD else "PASS"

    return label, risk, contribs

def permutation_importance(row: dict):
    """
    Local importance: impact of moving each feature to the nominal midpoint.
    Positive means it *reduced* risk when corrected -> important contributor.
    """
    _, baseline_risk, _ = score_features(row)
    importances = {}
    for k in FEATURES:
        tmp = dict(row)
        tmp[k] = (NOMINAL[k][0] + NOMINAL[k][1]) / 2.0  # midpoint
        _, new_risk, _ = score_features(tmp)
        importances[k] = max(0.0, baseline_risk - new_risk)
    return importances

def predict_mix(row: dict):
    """
    Returns a dict with:
      - label           : "PASS"/"FAIL"/"AT_RISK"
      - score           : P(FAIL) in [0,1]   <-- canonical scalar
      - confidence      : confidence in chosen label (matches label)
      - explanation     : per-feature local importance
      - model_version   : id of the model artifact
      - threshold       : decision threshold used (if no band)
      - risk_band       : optional (LOW,HIGH) if AT_RISK band is active
      - quality         : alias of label  (for UI)
      - probability     : alias of confidence (for UI)
    """
    label, risk, _ = score_features(row)  # risk = P(FAIL)
    expl = permutation_importance(row)

    # confidence should align with the chosen label
    if label == "FAIL":
        confidence = risk
    elif label == "PASS":
        confidence = 1.0 - risk
    else:  # AT_RISK: confidence is ambiguous; set None or a conservative value
        confidence = None

    out = {
        "label": label,
        "score": risk,                      # P(FAIL)
        "confidence": confidence,           # aligns with label
        "explanation": expl,
        "model_version": MODEL_VERSION,
    }
    if LOW is not None and HIGH is not None and LOW < HIGH:
        out["risk_band"] = [LOW, HIGH]
    else:
        out["threshold"] = MIX_FAIL_THRESHOLD

    # UI-friendly aliases (your frontend uses these)
    out["quality"] = out["label"]
    out["probability"] = out["confidence"] if out["confidence"] is not None else (
        None
    )

    return out