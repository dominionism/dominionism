#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["rembg[cpu]", "opencv-python-headless", "numpy", "pillow"]
# ///
"""Prep a photo for the ASCII portrait: cut out the subject, lift local contrast, crop to it.

Run once per photo (the first run downloads the background-removal model):

    uv run scripts/prep_photo.py ~/Desktop/photo.jpg

Writes data/portrait.png (grayscale + alpha, background fully transparent).
"""
import os, sys

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{ROOT}/data/portrait.png"
MODEL = os.environ.get("MODEL", "u2net_human_seg")   # rembg model trained on people
MAX_H = 900                                          # the ASCII grid is ~60 rows; no need for more

src = Image.open(sys.argv[1]).convert("RGB")

# 1. Cut the subject out. Only the mask is kept: brightness comes from the original pixels.
alpha = np.array(remove(src, session=new_session(MODEL), only_mask=True, post_process_mask=True))

# 2. Blur away print texture (halftone dots, JPEG grain), then lift local contrast with CLAHE
#    so a flatly-lit face still gets real highlights and shadows.
gray = cv2.cvtColor(np.array(src), cv2.COLOR_RGB2GRAY)
gray = cv2.GaussianBlur(gray, (0, 0), 1.5)
gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)

# 3. Crop to the subject and save grayscale + alpha
ys, xs = np.nonzero(alpha > 127)
y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
out = Image.fromarray(np.dstack([gray, alpha])[y0:y1, x0:x1], "LA")
if out.height > MAX_H:
    out = out.resize((round(out.width * MAX_H / out.height), MAX_H), Image.LANCZOS)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
out.save(OUT, optimize=True)
print(f"wrote data/portrait.png  ({out.width}x{out.height}, model {MODEL})")
