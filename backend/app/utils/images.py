from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Iterable, Optional

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------
# Where images are stored
#   - honors IMAGE_DIR env var if set
#   - defaults to <repo>/backend/app_data/images (matches main.py behavior)
# ---------------------------------------------------------------------
def get_image_dir() -> Path:
    default_dir = Path(__file__).resolve().parents[2] / "app_data" / "images"
    img_dir = Path(os.getenv("IMAGE_DIR", str(default_dir)))
    img_dir.mkdir(parents=True, exist_ok=True)
    return img_dir


# Simple set of defect types for the PoC
DEFECT_TYPES = [
    "crack",
    "chip",
    "surface_pit",
    "glaze",
    "uneven_wear",
    "contamination",
]

# A tiny, safe font fallback (Pillow will default if not found)
def _load_font(size: int = 14):
    try:
        return ImageFont.truetype("arial.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def _draw_defect(draw: ImageDraw.ImageDraw, defect: str, w: int, h: int) -> None:
    """
    Draw a crude visual for a given defect on the pad area.
    This is *only* for demo visuals; replace with real CV later.
    """
    # pad rectangle is centered; we roughly target that area
    pad_left, pad_top = int(w * 0.12), int(h * 0.18)
    pad_right, pad_bottom = int(w * 0.88), int(h * 0.82)

    if defect == "crack":
        # jagged polyline from left to right
        y = random.randint(pad_top + 20, pad_bottom - 20)
        x = pad_left
        prev = (x, y)
        for _ in range(10):
            x += (pad_right - pad_left) // 10
            y += random.randint(-12, 12)
            draw.line([prev, (x, y)], fill=(180, 30, 30), width=3)
            prev = (x, y)

    elif defect == "chip":
        # cut-out triangle on an edge
        tri = [
            (pad_left + 6, pad_top + 6),
            (pad_left + 38, pad_top + 10),
            (pad_left + 10, pad_top + 40),
        ]
        draw.polygon(tri, fill=(160, 45, 45))

    elif defect == "surface_pit":
        # a cluster of dots
        for _ in range(25):
            x = random.randint(pad_left + 40, pad_right - 40)
            y = random.randint(pad_top + 40, pad_bottom - 40)
            r = random.randint(1, 3)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(120, 120, 120))

    elif defect == "glaze":
        # glossy streak
        x1 = random.randint(pad_left + 40, pad_right - 100)
        y1 = random.randint(pad_top + 20, pad_bottom - 60)
        x2 = x1 + random.randint(60, 140)
        y2 = y1 + random.randint(10, 30)
        draw.rounded_rectangle((x1, y1, x2, y2), radius=10, outline=(200, 200, 240), width=3)

    elif defect == "uneven_wear":
        # height gradient bar across pad
        for i, x in enumerate(range(pad_left, pad_right, 6)):
            hbar = int(8 + (i % 7))
            y = pad_top + (i % 9)
            draw.rectangle((x, y, x + 4, y + hbar), fill=(90, 90, 90))

    elif defect == "contamination":
        # dark smudges
        for _ in range(6):
            x = random.randint(pad_left + 30, pad_right - 30)
            y = random.randint(pad_top + 30, pad_bottom - 30)
            r = random.randint(12, 24)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(60, 60, 60))


def generate_pad_image(
    outfile: Path,
    pad_type: str = "TRANSIT",
    defects: Optional[list[str]] = None,
    stage_hint: Optional[str] = None,
    size: tuple[int, int] = (640, 360),
) -> None:
    """
    Create a synthetic pad image with light UI annotations.
    - pad_type: "TRANSIT" | "FREIGHT"
    - defects: list from DEFECT_TYPES
    - stage_hint: optional (e.g., 'Grinding')
    """
    defects = defects or []
    w, h = size
    img = Image.new("RGB", size, color=(245, 246, 248))
    draw = ImageDraw.Draw(img)

    # Pad background
    pad_color = (130, 130, 135) if pad_type == "FREIGHT" else (150, 150, 155)
    pad_left, pad_top = int(w * 0.12), int(h * 0.18)
    pad_right, pad_bottom = int(w * 0.88), int(h * 0.82)
    draw.rounded_rectangle((pad_left, pad_top, pad_right, pad_bottom), radius=24, fill=pad_color)

    # Backplate / slots hints
    draw.line((pad_left + 20, pad_top + 20, pad_right - 20, pad_top + 20), fill=(100, 100, 100), width=2)
    draw.line((pad_left + 20, pad_bottom - 20, pad_right - 20, pad_bottom - 20), fill=(100, 100, 100), width=2)

    # Apply defects
    for d in defects:
        _draw_defect(draw, d, w, h)

    # Header text
    font = _load_font(14)
    hdr = f"{pad_type} | defects: {', '.join(defects) if defects else 'none'}"
    if stage_hint:
        hdr += f" | stage: {stage_hint}"
    draw.text((10, 8), hdr, fill=(30, 30, 30), font=font)

    img.save(outfile, format="PNG")


def generate_image_set(
    count: int = 50,
    out_dir: Optional[str | Path] = None,
    *,
    seed: Optional[int] = None,
    pad_infos: Optional[Iterable[dict]] = None,
) -> list[dict]:
    """
    Generate a batch of synthetic pad images.

    Args:
      - count: number of images to generate *if* pad_infos is not provided.
      - out_dir: directory to write images (defaults to get_image_dir()).
      - seed: for reproducibility.
      - pad_infos: optional iterable of dicts describing pads; if given, we use
        these to name files / choose pad_type, e.g.:
          {"id": 12, "serial_number": "TR-00012", "pad_type": "TRANSIT", "stage_name": "Grinding"}

    Returns: list of dicts:
      [{ "filename": "pad_00001.png", "path": "/abs/path/...png", "url": "/images/pad_00001.png",
         "pad_type": "TRANSIT", "defects": ["crack"], "stage": "Grinding" }, ...]
    """
    rng = random.Random(seed)
    out = []

    img_dir = Path(out_dir) if out_dir else get_image_dir()
    img_dir.mkdir(parents=True, exist_ok=True)

    def pick_defects() -> list[str]:
        # 60% none/minor, 25% one, 10% two, 5% three defects
        roll = rng.random()
        if roll < 0.60:
            return []
        elif roll < 0.85:
            return [rng.choice(DEFECT_TYPES)]
        elif roll < 0.95:
            return rng.sample(DEFECT_TYPES, 2)
        else:
            return rng.sample(DEFECT_TYPES, 3)

    def pick_pad_type(info: Optional[dict]) -> str:
        if info and "pad_type" in info and info["pad_type"]:
            # allow any casing
            return str(info["pad_type"]).upper()
        return "TRANSIT" if rng.random() < 0.5 else "FREIGHT"

    # Build the work list
    if pad_infos:
        work = list(pad_infos)
    else:
        work = [{"id": i + 1, "serial_number": f"PAD-{i+1:05d}"} for i in range(count)]

    for i, info in enumerate(work, start=1):
        ptype = pick_pad_type(info)
        stage = info.get("stage_name") if isinstance(info, dict) else None
        defects = pick_defects()

        # Prefer serial_number then id for filename
        basis = str(info.get("serial_number") or info.get("id") or f"{i:05d}")
        filename = f"pad_{basis}.png"
        path = img_dir / filename

        generate_pad_image(path, pad_type=ptype, defects=defects, stage_hint=stage)

        out.append({
            "filename": filename,
            "path": str(path),
            "url": f"/images/{filename}",
            "pad_type": ptype,
            "defects": defects,
            "stage": stage,
        })

    return out