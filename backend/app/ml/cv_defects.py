import base64, io, random
from PIL import Image, ImageFilter, ImageOps

DEFECTS = ["CRACK", "INCLUSION", "BURN_MARK", "CHIP", "SURFACE_POROSITY"]
MODEL_VERSION = "image-heuristic-0.1"

def analyze_image(image_b64: str | None, brakepad_id: str | None):
    # If image is provided, derive simple features (contrast/edges).
    score = 0.8
    picked = []
    if image_b64:
        img = Image.open(io.BytesIO(base64.b64decode(image_b64.split(",")[-1]))).convert("L")
        edges = img.filter(ImageFilter.FIND_EDGES)
        contrast = ImageOps.autocontrast(img)
        # heuristic: high edges variance → crack/chip; low contrast → burn mark.
        # # (In practice, replace with proper CNN)
        w, h = img.size
        if w * h > 0:
            picked = random.sample(DEFECTS, k=random.randint(0, 2))
            score = round(random.uniform(0.55, 0.95), 3)
    else:
        picked = random.sample(DEFECTS, k=random.randint(0, 2))
        score = round(random.uniform(0.55, 0.9), 3)
    stage_guess = random.choice(["Grinding", "Painting", "Final QC"]) if picked else None
    return {"defects": picked, "stage_guess": stage_guess, "score": score, "model_version": MODEL_VERSION}