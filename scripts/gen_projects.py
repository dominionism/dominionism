#!/usr/bin/env python3
"""Build compact, full-color tech-logo strips (with labels) per project."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
icons = json.load(open(f"{HERE}/icons.json"))

# Per-project stacks (pulled from each repo's languages / dependencies)
projects = {
    "koda":      ["typescript", "python", "flutter", "docker", "livekit"],
    "grove":     ["typescript", "bun", "huggingface", "zod"],
    "noesis":    ["typescript", "nodejs", "sqlite", "onnx"],
    "openville": ["typescript", "nextjs", "react", "tailwind", "shadcn"],
}

LIGHT = "#E6EDF3"
colors = {
    "typescript": "#3178C6", "python": "#3776AB", "flutter": "#02569B", "docker": "#2496ED",
    "bun": "#FBF0DF", "huggingface": "#FFD21E", "zod": "#3E67B1",
    "nodejs": "#5FA04E", "sqlite": LIGHT, "onnx": "#005CED",
    "nextjs": LIGHT, "react": "#61DAFB", "tailwind": "#06B6D4",
    "livekit": LIGHT, "shadcn": LIGHT,
}
labels = {
    "typescript": "TypeScript", "python": "Python", "flutter": "Flutter", "docker": "Docker",
    "bun": "Bun", "huggingface": "Hugging Face", "zod": "Zod",
    "nodejs": "Node", "sqlite": "SQLite", "onnx": "ONNX",
    "nextjs": "Next.js", "react": "React", "tailwind": "Tailwind",
    "livekit": "LiveKit", "shadcn": "shadcn",
}

ICON = 26
STEP = 96          # horizontal step per item (wide enough for "Hugging Face")
PAD_X = 16
ICON_CY = 30
LABEL_Y = 54
H = 68


def parse_vb(vb):
    p = [float(x) for x in vb.split()]
    return p if len(p) == 4 else [0, 0, 24, 24]


def item(name, cx):
    ic = icons[name]
    minx, miny, vw, vh = parse_vb(ic["vb"])
    s = ICON / max(vw, vh)
    tx = cx - (minx + vw / 2) * s
    ty = ICON_CY - (miny + vh / 2) * s
    return (
        f'  <path transform="translate({tx:.2f},{ty:.2f}) scale({s:.4f})" d="{ic["d"]}" fill="{colors[name]}"/>\n'
        f'  <text x="{cx:.1f}" y="{LABEL_Y}" font-family="ui-monospace,\'SF Mono\',monospace" '
        f'font-size="9" letter-spacing="0.3" fill="#8B949E" text-anchor="middle">{labels[name]}</text>'
    )


def build(name, stack):
    W = PAD_X * 2 + len(stack) * STEP
    body = "\n".join(item(nm, PAD_X + i * STEP + STEP / 2) for i, nm in enumerate(stack))
    label_list = " · ".join(labels[n] for n in stack)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" fill="none" '
        f'role="img" aria-label="{name} stack: {label_list}">\n'
        f'  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="#0D1117" stroke="#21262D" stroke-width="1"/>\n'
        f'{body}\n'
        f'</svg>\n'
    )
    out = f"assets/{name}-stack.svg"
    open(out, "w").write(svg)
    print(f"wrote {out}  ({W}x{H})  [{label_list}]")


for name, stack in projects.items():
    build(name, stack)
