import math, random

FEATURES = [
"resin_pct","fiber_pct","metal_powder_pct","filler_pct","abrasives_pct","binder_pct",
"temp_c","pressure_mpa","cure_time_s","moisture_pct"
]

MODEL_VERSION = "mix-baseline-0.1"

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
    contribs = {}
    total = 0.0
    for k in FEATURES:
        lo, hi = NOMINAL[k]
        d = _deviation_score(float(row[k]), lo, hi)
        c = WEIGHTS[k] * d
        contribs[k] = c
        total += c
    # map to probability-like score [0,1]
    risk = min(1.0, total / 5.0)
    label = "FAIL" if risk > 0.45 else "PASS"
    return label, risk, contribs

def permutation_importance(row: dict):
    # simple local importance: random shuffle baseline
    baseline_label, baseline_risk, _ = score_features(row)
    importances = {}
    for k in FEATURES:
        tmp = dict(row)
        tmp[k] = (NOMINAL[k][0] + NOMINAL[k][1]) / 2.0 # replace with nominal midpoint
        _, new_risk, _ = score_features(tmp)
        importances[k] = max(0.0, baseline_risk - new_risk)
    return importances

def predict_mix(row: dict):
    label, risk, _ = score_features(row)
    expl = permutation_importance(row)
    return {
        "label": label, "score": 1.0 - risk, "explanation": expl, "model_version": MODEL_VERSION
    }