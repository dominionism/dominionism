#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pillow"]
# ///
"""Turn data/portrait.png (from prep_photo.py) into a monochrome ASCII grid, data/portrait.txt.

    uv run scripts/make_ascii.py

The glyphs print light-on-dark, so brighter pixels get denser glyphs. The transparent
background prints as spaces, and the subject never drops below the faintest glyph, so its
silhouette survives even in deep shadow.
"""
import os

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLS = int(os.environ.get("COLS", 106))
CROP = float(os.environ.get("CROP", 0.74))    # keep the top of the cutout: head and shoulders
GAMMA = float(os.environ.get("GAMMA", 0.75))  # <1 lifts mid-tones out of the shadows
PEAK = 0.35                                   # share of each cell's brightest pixel, so thin highlights (glasses rims) survive
CELL = 2.0                                    # glyph cell height/width: 0.6em advance, 1.2em line
RAMP = " .`:-=+*cs#%@"                        # sparse -> dense; keep in sync with make_whoami_svg.py

im = Image.open(f"{ROOT}/data/portrait.png").convert("LA")
im = im.crop((0, 0, im.width, round(im.height * CROP)))
lum, alpha = im.split()
lum = np.asarray(lum.filter(ImageFilter.UnsharpMask(radius=3, percent=120, threshold=2)), dtype=float) / 255
alpha = np.asarray(alpha, dtype=float) / 255

rows = round(COLS * im.height / im.width / CELL)
ys = np.linspace(0, im.height, rows + 1).astype(int)
xs = np.linspace(0, im.width, COLS + 1).astype(int)
cells = [[(slice(ys[r], ys[r + 1]), slice(xs[c], xs[c + 1])) for c in range(COLS)] for r in range(rows)]

bright = np.array([[(1 - PEAK) * lum[s].mean() + PEAK * lum[s].max() for s in row] for row in cells])
solid = np.array([[alpha[s].mean() > 0.5 for s in row] for row in cells])

idx = np.rint(np.clip(bright, 0, 1) ** GAMMA * (len(RAMP) - 1)).astype(int)
idx = np.where(solid, np.maximum(idx, 1), 0)

lines = ["".join(RAMP[i] for i in row).rstrip() for row in idx]
while lines and not lines[-1]:
    lines.pop()

open(f"{ROOT}/data/portrait.txt", "w").write("\n".join(lines) + "\n")
print(f"wrote data/portrait.txt  ({COLS}x{len(lines)}, crop {CROP}, gamma {GAMMA})")
