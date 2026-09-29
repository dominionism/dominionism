#!/usr/bin/env python3
"""Render data/contributions.json (from fetch_contributions.py) as assets/contrib-heatmap.svg:
the last year of contributions in a terminal window, boxes cascading in diagonally once,
then holding still.

    python3 scripts/render_heatmap_svg.py
"""
import json, os
from datetime import date

from terminal import FG, GREEN, MUTED, PAD, USER, W, delay, prompt, window

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALETTE = ["#161B22", "#0E4429", "#006D32", "#26A641", "#39D353", "#69F0A0"]   # none -> neon peak
# Levels come from quantiles of my own active days, not GitHub's data-level: a single big day
# otherwise squeezes almost every active day into the dimmest green.
QUANTILES = [0.25, 0.5, 0.75, 0.95]

GX, GY = PAD + 30, 92          # grid origin, leaving room for day labels
STEP = (W - PAD - GX) / 53     # 53 week columns
CELL = round(STEP * 0.78, 1)
LFS = 10.5                     # label font size

data = json.load(open(f"{ROOT}/data/contributions.json"))
days = data["days"]
active = sorted(d["count"] for d in days if d["count"])
cuts = [active[min(len(active) - 1, int(q * len(active)))] for q in QUANTILES] if active else []


def level(n):
    return 0 if not n else 1 + sum(n > c for c in cuts)


first = date.fromisoformat(days[0]["date"])
origin = first.toordinal() - (first.weekday() + 1) % 7   # the Sunday that starts column 0

cmd_svg, cmd_css, t_grid = prompt(56, "./contributions.sh", 0.35, "cmd")

# Cells, grouped by diagonal (column + weekday) so each diagonal drops in together
diagonals, months = {}, []
for d in days:
    day = date.fromisoformat(d["date"])
    col, row = divmod(day.toordinal() - origin, 7)
    x, y = GX + col * STEP, GY + row * STEP
    diagonals.setdefault(col + row, []).append(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" rx="2.5" fill="{PALETTE[level(d["count"])]}"/>'
    )
    if row == 0 or d is days[0]:
        if not months or months[-1][1] != day.month:
            months.append((col, day.month, day.strftime("%b")))
if len(months) > 1 and months[1][0] - months[0][0] < 3:   # a stub first month would collide with the next label
    months.pop(0)

grid = "".join(
    f'  <g class="drop" {delay(t_grid + k * 0.012)}>{"".join(cells)}</g>\n' for k, cells in sorted(diagonals.items())
)
t_stats = t_grid + max(diagonals) * 0.012 + 0.3

labels = (
    f'  <g class="fade" {delay(t_grid)} font-size="{LFS}" fill="{MUTED}">\n'
    + "".join(f'    <text x="{GX + col * STEP:.1f}" y="{GY - 8}">{name}</text>\n' for col, _, name in months)
    + "".join(
        f'    <text x="{PAD}" y="{GY + r * STEP + CELL / 2 + 3.5:.1f}">{name}</text>\n'
        for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )
    + "  </g>\n"
)


def fmt_day(iso):
    d = date.fromisoformat(iso)
    return f"{d:%b} {d.day}"


# Stats: the headline on the left, the legend on the right, the streaks underneath
s = data["streak"]
y1, y2 = GY + 7 * STEP + 26, GY + 7 * STEP + 47
num = lambda v: f'<tspan fill="{FG}" font-weight="700">{v}</tspan>'
facts = []
if s["current"] > 1:
    facts.append(f"current streak {num(s['current'])} days")
facts.append(f"longest streak {num(s['longest'])} days ({fmt_day(s['longest_from'])} – {fmt_day(s['longest_to'])})")
facts.append(f"best day {num(data['best_day']['count'])} ({fmt_day(data['best_day']['date'])})")
facts.append(f"{num(data['active_days'])} active days")
legend_x = W - PAD - 6 * 13 - 30
stats = (
    f'  <g class="rise" {delay(t_stats)} font-size="12.5" fill="{MUTED}">\n'
    f'    <text x="{PAD}" y="{y1:.1f}"><tspan fill="{GREEN}" font-weight="700">{data["total"]:,}</tspan> '
    f'contributions in the last year</text>\n'
    f'    <text x="{legend_x - 8}" y="{y1:.1f}" font-size="{LFS}" text-anchor="end">Less</text>\n'
    + "".join(
        f'    <rect x="{legend_x + i * 13}" y="{y1 - 9.5:.1f}" width="10" height="10" rx="2" fill="{c}"/>\n'
        for i, c in enumerate(PALETTE)
    )
    + f'    <text x="{legend_x + 6 * 13 + 5}" y="{y1:.1f}" font-size="{LFS}">More</text>\n'
    f'  </g>\n'
    f'  <g class="rise" {delay(t_stats + 0.12)} font-size="12.5" fill="{MUTED}">\n'
    f'    <text x="{PAD}" y="{y2:.1f}">{"  ·  ".join(facts)}</text>\n'
    f'  </g>\n'
)
stamp = f'  <text x="{W - 16}" y="19" font-size="11" fill="{MUTED}" text-anchor="end">updated {fmt_day(data["fetched"][:10])}</text>\n'

H = round(y2 + 22)
css = (
    cmd_css
    + "\n    .drop { animation: drop .5s cubic-bezier(.2,.7,.2,1) both; }"
    + "\n    @keyframes drop { from { opacity: 0; transform: translateY(-7px); } }"
)
label = f"{USER}'s GitHub contributions over the last year: {data['total']:,} contributions, longest streak {s['longest']} days."
svg = window(H, f"{USER}@github: ~", stamp + cmd_svg + labels + grid + stats, css, label)

open(f"{ROOT}/assets/contrib-heatmap.svg", "w").write(svg)
print(f"wrote assets/contrib-heatmap.svg  ({W}x{H}, {len(days)} days, levels cut at {cuts}, {len(svg) // 1024} KB)")
