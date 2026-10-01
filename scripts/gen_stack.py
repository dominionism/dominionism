#!/usr/bin/env python3
"""Build a full-color, infinitely-scrolling tech-logo marquee (with labels) as an animated SVG,
in the same terminal window as the rest of the profile."""
import json, os

from terminal import BAR, BG, W, window

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SP = os.environ.get("SP", os.path.dirname(os.path.abspath(__file__)))
icons = json.load(open(f"{SP}/icons.json"))

# Two rows; order chosen so each row reads well
row1 = ["python", "nodejs", "react", "nextjs", "docker", "postgres", "redis", "kotlin", "threejs", "git"]
row2 = ["fastapi", "express", "tailwind", "mongodb", "firebase", "java", "html", "css", "github", "bash"]

# Brand colors. Black/near-black brands are rendered in light neutral so they stay visible on the dark card.
LIGHT = "#E6EDF3"
colors = {
    "python": "#3776AB", "nodejs": "#5FA04E", "react": "#61DAFB", "nextjs": LIGHT,
    "docker": "#2496ED", "postgres": "#4169E1", "redis": "#FF4438", "kotlin": "#7F52FF",
    "threejs": LIGHT, "git": "#F05032", "fastapi": "#009688", "express": LIGHT,
    "tailwind": "#06B6D4", "mongodb": "#47A248", "firebase": "#FFCA28", "java": LIGHT,
    "html": "#E34F26", "css": "#1572B6", "github": LIGHT, "bash": "#4EAA25",
}
labels = {
    "python": "Python", "nodejs": "Node", "react": "React", "nextjs": "Next.js",
    "docker": "Docker", "postgres": "Postgres", "redis": "Redis", "kotlin": "Kotlin",
    "threejs": "Three.js", "git": "Git", "fastapi": "FastAPI", "express": "Express",
    "tailwind": "Tailwind", "mongodb": "MongoDB", "firebase": "Firebase", "java": "Java",
    "html": "HTML5", "css": "CSS3", "github": "GitHub", "bash": "Bash",
}

ICON = 34
GAP = 78
R1_ICON, R1_LABEL = 66, 92    # row 1: icon center y, label baseline y (below the title bar)
R2_ICON, R2_LABEL = 136, 162  # row 2
H = 188
DUR = 30                      # seconds per full loop


def parse_vb(vb):
    p = [float(x) for x in vb.split()]
    return p if len(p) == 4 else [0, 0, 24, 24]


def item(name, cx, icon_cy, label_y):
    ic = icons[name]
    minx, miny, vw, vh = parse_vb(ic["vb"])
    s = ICON / max(vw, vh)
    tx = cx - (minx + vw / 2) * s
    ty = icon_cy - (miny + vh / 2) * s
    return (
        f'<path transform="translate({tx:.2f},{ty:.2f}) scale({s:.4f})" d="{ic["d"]}" fill="{colors[name]}"/>'
        f'<text x="{cx:.1f}" y="{label_y}" font-family="ui-monospace,\'SF Mono\',monospace" '
        f'font-size="9" letter-spacing="0.5" fill="#8B949E" text-anchor="middle">{labels[name]}</text>'
    )


def build_row(names, icon_cy, label_y, direction):
    n = len(names)
    span = n * GAP
    parts = []
    for rep in (0, 1):                       # duplicate for a seamless loop
        base = rep * span
        for i, nm in enumerate(names):
            cx = base + i * GAP + GAP / 2
            parts.append(item(nm, cx, icon_cy, label_y))
    inner = "\n      ".join(parts)
    frm, to = ("0", f"-{span}") if direction == "left" else (f"-{span}", "0")
    return (
        f'    <g>\n'
        f'      <animateTransform attributeName="transform" type="translate" '
        f'from="{frm} 0" to="{to} 0" dur="{DUR}s" repeatCount="indefinite"/>\n'
        f'      {inner}\n'
        f'    </g>'
    )


r1 = build_row(row1, R1_ICON, R1_LABEL, "left")
r2 = build_row(row2, R2_ICON, R2_LABEL, "right")

# Fade the rows out at both sides of the window body, below the title bar
body = f'''  <defs>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"    stop-color="{BG}" stop-opacity="1"/>
      <stop offset="0.09" stop-color="{BG}" stop-opacity="0"/>
      <stop offset="0.91" stop-color="{BG}" stop-opacity="0"/>
      <stop offset="1"    stop-color="{BG}" stop-opacity="1"/>
    </linearGradient>
  </defs>
{r1}
{r2}
  <rect x="0" y="{BAR}" width="{W}" height="{H - BAR}" fill="url(#edge)"/>
'''
label = "Tech stack: " + ", ".join(labels[n] for n in row1 + row2)
svg = window(H, "Tech Stack", body, "", label, heading=True)

open(f"{ROOT}/assets/tech-stack.svg", "w").write(svg)
print(f"wrote assets/tech-stack.svg  ({len(row1)}+{len(row2)} logos + labels, {W}x{H})")
