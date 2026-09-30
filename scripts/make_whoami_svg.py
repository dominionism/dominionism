#!/usr/bin/env python3
"""Build assets/whoami.svg: `neofetch` in a terminal window, the ASCII portrait printing
row by row beside a card of who I am.

    python3 scripts/make_whoami_svg.py

Edit CARD to change the card. To change the portrait, rerun prep_photo.py and make_ascii.py first.
"""
import os
from html import escape

from terminal import BG, FG, GREEN, MUTED, PAD, TEXT, USER, W, delay, idle_prompt, prompt, window

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAMP = " .`:-=+*cs#%@"   # must match make_ascii.py

CARD = [
    ("Role",      "Founder · Software Engineer"),
    ("Focus",     "Agentic systems · high-perf infra"),
    ("Areas",     "Full stack · ML · Security · Automation"),
    ("Education", "B.S. Informatics · Univ. of Washington"),
    ("Motto",     "Security first. Always."),
]

START = 0.4              # a beat of idle prompt before the command types
PY = 72                  # top of the output area
# Portrait: 0.6em glyph advance, 1.2em line (the 2:1 cell make_ascii.py samples for)
PCW = 3.6
PFS = PCW / 0.6
PLH = PFS * 1.2
SCAN, STAGGER = 0.3, 0.04
# Card
CX, CFS, CLH = 440, 12.5, 21
CCW = CFS * 0.6
KEY_COLS = 12

rows = open(f"{ROOT}/data/portrait.txt").read().rstrip("\n").split("\n")
pw, ph = max(map(len, rows)) * PCW, len(rows) * PLH


def glyphs(row):
    """One portrait row: each run of a glyph is a tspan whose opacity follows its density.

    Every glyph gets an explicit column x, which holds the grid in any font and engine
    (WebKit ignores textLength on a text with tspans).
    """
    out, i = [], 0
    while i < len(row):
        j = i
        while j < len(row) and row[j] == row[i]:
            j += 1
        if row[i] != " ":
            lvl = RAMP.find(row[i])
            cls = f' class="g{lvl}"' if lvl > 0 else ""
            xs = " ".join(f"{PAD + c * PCW:.1f}" for c in range(i, j))
            out.append(f'<tspan{cls} x="{xs}">{escape(row[i:j])}</tspan>')
        i = j
    return "".join(out)


cmd_svg, cmd_css, t_out = prompt(56, "neofetch", START, "cmd")

# Portrait: every row prints behind a scan (a background-coloured cover with a block cursor on
# its leading edge) that slides off to the right, one row after another.
portrait = [f'  <g font-size="{PFS:.2f}" fill="{FG}">\n']
for i, row in enumerate(rows):
    if row.strip():
        portrait.append(f'    <text y="{PY + i * PLH + PLH * 0.8:.2f}">{glyphs(row)}</text>\n')
portrait.append(f'  </g>\n  <clipPath id="portrait"><rect x="{PAD}" y="{PY}" width="{pw:.1f}" height="{ph:.1f}"/></clipPath>\n')
portrait.append('  <g clip-path="url(#portrait)">\n')
for i in range(len(rows)):
    y, d = PY + i * PLH, delay(t_out + i * STAGGER)
    portrait.append(
        f'    <g class="scan" {d}><rect x="{PAD}" y="{y:.2f}" width="{pw:.1f}" height="{PLH + 0.4:.2f}" fill="{BG}"/>'
        f'<rect class="cur" {d} x="{PAD}" y="{y:.2f}" width="{PCW}" height="{PLH:.2f}" fill="{FG}"/></g>\n'
    )
portrait.append("  </g>\n")
t_done = t_out + len(rows) * STAGGER + SCAN


# Card: the classic `user@host`, a rule, then key/value lines rising in one by one, centred
# beside the portrait
CY = PY + (ph - (15 + (len(CARD) + 1) * CLH)) / 2


def at(n):
    return CY + 12 + n * CLH


title = f"{USER}@github"
lines = [
    f'<text x="{CX}" y="{at(0):.1f}" font-size="{CFS + 1}" font-weight="700"><tspan fill="{GREEN}">{USER}</tspan>'
    f'<tspan fill="{FG}">@</tspan><tspan fill="{GREEN}">github</tspan></text>',
    f'<text x="{CX}" y="{at(1):.1f}" font-size="{CFS}" fill="{MUTED}">{"-" * len(title)}</text>',
]
for n, (key, value) in enumerate(CARD, start=2):
    k = f'<text x="{CX}" y="{at(n):.1f}" font-size="{CFS}" font-weight="700" fill="{GREEN}">{escape(key)}:</text>' if key else ""
    lines.append(f'{k}<text x="{CX + KEY_COLS * CCW:.1f}" y="{at(n):.1f}" font-size="{CFS}" fill="{TEXT}">{escape(value)}</text>')
card = [f'  <g class="rise" {delay(t_out + 0.15 + i * 0.08)}>{l}</g>\n' for i, l in enumerate(lines)]
t_card = t_out + 0.15 + len(lines) * 0.08

H = round(PY + ph + 48)
body = (
    cmd_svg
    + "".join(portrait)
    + "".join(card)
    + idle_prompt(PY + ph + 30, max(t_done, t_card) + 0.1)
)
css = (
    cmd_css
    + f"\n    .scan {{ transform: translateX({pw:.1f}px); animation: scan {SCAN}s linear both; }}"
    + "\n    @keyframes scan { from { transform: translateX(0); } }"
    + f"\n    .cur {{ opacity: 0; animation: cur {SCAN}s linear both; }}"
    + "\n    @keyframes cur { 0%, 100% { opacity: 0; } 0.1%, 99.9% { opacity: 1; } }"
    + "".join(f"\n    .g{lvl} {{ fill-opacity: {0.28 + 0.72 * (lvl - 1) / (len(RAMP) - 2):.2f}; }}" for lvl in range(1, len(RAMP)))
)
label = f"{USER} running neofetch: an ASCII portrait beside a card. " + "; ".join(
    f"{k}: {v}" if k else v for k, v in CARD
)

svg = window(H, f"{USER}@github: ~", body, css, label)
open(f"{ROOT}/assets/whoami.svg", "w").write(svg)
print(f"wrote assets/whoami.svg  ({W}x{H}, portrait {len(rows)} rows, {len(svg) // 1024} KB)")
