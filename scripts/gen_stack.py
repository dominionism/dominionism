#!/usr/bin/env python3
"""Build a monochrome, infinitely-scrolling tech-logo marquee as an animated SVG."""
import json, os

SP = os.environ.get("SP", os.path.dirname(os.path.abspath(__file__)))
icons = json.load(open(f"{SP}/icons.json"))

# Two rows; order chosen so each row reads well
row1 = ["python", "nodejs", "react", "nextjs", "docker", "postgres", "redis", "kotlin", "threejs", "git"]
row2 = ["fastapi", "express", "tailwind", "mongodb", "firebase", "java", "html", "css", "github", "bash"]

W, H = 860, 150
ICON = 34          # icon box size
GAP = 62           # horizontal step between icons
PAD_Y1 = 44        # row 1 center y
PAD_Y2 = 104       # row 2 center y
DUR = 26           # seconds per full loop

def parse_vb(vb):
    p = [float(x) for x in vb.split()]
    return p if len(p) == 4 else [0, 0, 24, 24]

def logo_group(name, cx, cy, fill):
    ic = icons[name]
    minx, miny, vw, vh = parse_vb(ic["vb"])
    s = ICON / max(vw, vh)
    # translate so the icon is centered on (cx, cy)
    tx = cx - (minx + vw / 2) * s
    ty = cy - (miny + vh / 2) * s
    return (f'<path transform="translate({tx:.2f},{ty:.2f}) scale({s:.4f})" '
            f'd="{ic["d"]}" fill="{fill}"/>')

def build_row(names, cy, direction, fill):
    """One seamless belt: sequence laid out once, duplicated, translated by a full width."""
    n = len(names)
    span = n * GAP                      # width of one full sequence
    parts = []
    for rep in (0, 1):                  # two copies for a seamless loop
        base = rep * span
        for i, nm in enumerate(names):
            cx = base + i * GAP + GAP / 2
            parts.append(logo_group(nm, cx, cy, fill))
    inner = "\n      ".join(parts)
    if direction == "left":
        frm, to = "0", f"-{span}"
    else:
        frm, to = f"-{span}", "0"
    return (f'    <g>\n'
            f'      <animateTransform attributeName="transform" type="translate" '
            f'from="{frm} 0" to="{to} 0" dur="{DUR}s" repeatCount="indefinite"/>\n'
            f'      {inner}\n'
            f'    </g>')

r1 = build_row(row1, PAD_Y1, "left", "#8B949E")
r2 = build_row(row2, PAD_Y2, "right", "#6E7681")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" fill="none" role="img" aria-label="Tech stack">
  <defs>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"    stop-color="#0D1117" stop-opacity="1"/>
      <stop offset="0.10" stop-color="#0D1117" stop-opacity="0"/>
      <stop offset="0.90" stop-color="#0D1117" stop-opacity="0"/>
      <stop offset="1"    stop-color="#0D1117" stop-opacity="1"/>
    </linearGradient>
    <clipPath id="card"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18"/></clipPath>
  </defs>

  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="#0D1117" stroke="#21262D" stroke-width="1"/>

  <g clip-path="url(#card)">
{r1}
{r2}
    <!-- soft dark fade on both edges so logos glide in and out -->
    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#edge)"/>
  </g>
</svg>
'''

open("assets/stack.svg", "w").write(svg)
print(f"wrote assets/stack.svg  ({len(row1)}+{len(row2)} logos, {W}x{H})")
