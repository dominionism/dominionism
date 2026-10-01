#!/usr/bin/env python3
"""Build assets/experience.svg and assets/projects.svg: the README's Experience and Projects
sections, each in the same terminal window as whoami.svg.

    python3 scripts/make_sections_svg.py

Edit EXPERIENCE and PROJECTS below; **double asterisks** bold a phrase inside a bullet.
SVG text doesn't wrap, so lines are wrapped here at a fixed monospace width.
"""
import json, os, re
from html import escape

from terminal import BAR, FG, GREEN, MUTED, PAD, TEXT, W, window

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
icons = json.load(open(f"{ROOT}/scripts/icons.json"))

EXPERIENCE = [
    {
        "company": "Koda", "role": "Co-Founder", "dates": "Feb 2026 – Sep 2026",
        "summary": "Building an intelligent macOS personal agent translating natural language to "
                   "system-level execution tailored for developer workflows.",
        "bullets": [
            "Built a macOS menu bar utility using on-device STT for real-time shell, git, and app management",
            "Implemented hybrid AI orchestration using local pattern-matching for zero-latency and "
            "cloud-based LLM function calling for complex intent",
            "Integrated pre-execution command guards and macOS Keychain for encrypted credential storage",
        ],
    },
    {
        "company": "Standard", "role": "Lead Software Engineer", "dates": "June 2025 – Dec 2025",
        "summary": "Prototyping and scaling a real-time real estate data intelligence platform.",
        "bullets": [
            "Led full-stack development of a platform processing **40,000+ spatial data records**, "
            "featured at **NAR\u00a0NXT\u00a02025**",   # non-breaking: keep the event name on one line
            "Built production ETL pipelines in Python (Scrapy) with schema versioning and incremental validation",
            "Optimized query latency by **80%** (5s → 1s) via MongoDB aggregation and multi-tier Redis caching",
        ],
    },
]

PROJECTS = [
    {
        "name": "Koda",
        "tagline": "A voice-first AI pair programmer — talk to it; it does the engineering.",
        "bullets": [
            "Built a two-tier voice agent behind a LiveKit audio room, running 24/7 on a VPS with the "
            "phone as just a microphone and speaker",
            "Autonomously navigates codebases, manages version control, and delegates to coding tools, "
            "reporting back in plain speech",
            "Steerable by design: high-autonomy execution that stays conversational and under the user's direction",
        ],
        "stack": ["typescript", "python", "flutter", "docker", "livekit"],
    },
    {
        "name": "Grove",
        "tagline": "Human-curated agentic memory — a locator, not an injector.",
        "bullets": [
            "Designed a memory model of plain-folder \"context trees\" curated entirely by the user, "
            "with nothing auto-remembered or injected behind their back",
            "Built an engine that locates the right tree on return and reads it in full, resuming a "
            "session as if the abandoned one never ended",
            "Inverts mainstream agentic memory: the machine never quietly remembers or forgets anything",
        ],
        "stack": ["typescript", "bun", "huggingface", "zod"],
    },
    {
        "name": "Noesis",
        "tagline": "Persistent intelligence layer for AI coding agents.",
        "bullets": [
            "Fused memory, workflow, and auto-integration into a single layer spanning 9 CLI coding tools",
            "Engineered SQLite-backed memory with hybrid retrieval, a knowledge graph, and HMAC integrity",
            "Shipped distribution adapters for Claude Code, Cursor, Copilot, Aider, Codex CLI, and more",
        ],
        "stack": ["typescript", "nodejs", "sqlite", "onnx"],
    },
    {
        "name": "OpenVille",
        "tagline": "Autonomous Multi-Agent Tradespeople Marketplace & Negotiation Engine",
        "bullets": [
            "Built a semantic RAG engine using vector embeddings and cosine similarity for "
            "high-accuracy tradespeople discovery",
            "Implemented weighted multi-factor ranking with real-time preference adjustments and "
            "cost/quality outlier detection",
            "Designed a multi-stage pipeline handling reasoning, real-time agent negotiation, and "
            "transaction fulfillment",
        ],
        "stack": ["typescript", "nextjs", "react", "tailwind", "shadcn"],
    },
]

# Stack logos: brand colors, with black brands in light neutral so they show on the dark window
LIGHT = "#E6EDF3"
COLORS = {
    "typescript": "#3178C6", "python": "#3776AB", "flutter": "#02569B", "docker": "#2496ED",
    "bun": "#FBF0DF", "huggingface": "#FFD21E", "zod": "#3E67B1",
    "nodejs": "#5FA04E", "sqlite": LIGHT, "onnx": "#005CED",
    "nextjs": LIGHT, "react": "#61DAFB", "tailwind": "#06B6D4",
    "livekit": LIGHT, "shadcn": LIGHT,
}
LABELS = {
    "typescript": "TypeScript", "python": "Python", "flutter": "Flutter", "docker": "Docker",
    "bun": "Bun", "huggingface": "Hugging Face", "zod": "Zod",
    "nodejs": "Node", "sqlite": "SQLite", "onnx": "ONNX",
    "nextjs": "Next.js", "react": "React", "tailwind": "Tailwind",
    "livekit": "LiveKit", "shadcn": "shadcn",
}

FS, HFS, LH = 12.5, 14, 19       # body and heading font sizes, line height
EM = 0.65                        # widest monospace advance seen (WebKit's SF Mono); Menlo is 0.6
BULLET_X = PAD + 22              # bullet text; the ▸ marker sits in the gap before it
TOP = BAR + 36                   # first baseline under the title bar


def cols(x, size=FS):
    """How many characters fit between x and the window's right padding."""
    return int((W - PAD - x) / (size * EM))


def wrap(text, width):
    """Greedy word wrap that keeps **bold** markup: returns lines of (text, bold) runs."""
    plain, bold = "", []
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        plain += part
        bold += [i % 2 == 1] * len(part)
    lines, start = [], 0
    while start < len(plain):
        end = len(plain) if len(plain) - start <= width else plain.rfind(" ", start, start + width + 1)
        if end <= start:
            end = start + width
        runs, i = [], start
        while i < end:
            j = i
            while j < end and bold[j] == bold[i]:
                j += 1
            runs.append((plain[i:j], bold[i]))
            i = j
        lines.append(runs)
        start = end + 1 if end < len(plain) and plain[end] == " " else end
    return lines


def text_line(x, y, runs, italic=False):
    body = "".join(f'<tspan fill="{FG}" font-weight="700">{escape(t)}</tspan>' if b else escape(t) for t, b in runs)
    style = ' font-style="italic"' if italic else ""
    return f'  <text x="{x}" y="{y:.1f}" font-size="{FS}" fill="{TEXT}"{style}>{body}</text>\n'


def bullets(items, y):
    """▸ bullets with hanging indents; returns (svg, y of the last baseline)."""
    out = []
    for n, item in enumerate(items):
        y += LH + (3 if n else 0)
        out.append(f'  <text x="{PAD + 4}" y="{y:.1f}" font-size="{FS}" fill="{GREEN}">▸</text>\n')
        for k, runs in enumerate(wrap(item, cols(BULLET_X))):
            y += LH if k else 0
            out.append(text_line(BULLET_X, y, runs))
    return "".join(out), y


def stack_row(names, y):
    """Small brand logos with their names, left to right."""
    out, x, size = [], PAD, 15
    for name in names:
        ic = icons[name]
        minx, miny, vw, vh = [float(v) for v in ic["vb"].split()]
        s = size / max(vw, vh)
        tx, ty = x + size / 2 - (minx + vw / 2) * s, y - 4.5 - (miny + vh / 2) * s
        out.append(f'  <path transform="translate({tx:.2f},{ty:.2f}) scale({s:.4f})" d="{ic["d"]}" fill="{COLORS[name]}"/>\n')
        out.append(f'  <text x="{x + size + 6}" y="{y:.1f}" font-size="11" fill="{MUTED}">{LABELS[name]}</text>\n')
        x += size + 6 + len(LABELS[name]) * 11 * EM + 22
    return "".join(out)


def experience():
    out, y = [], TOP - LH - 22
    for job in EXPERIENCE:
        y += LH + 22
        out.append(
            f'  <text x="{PAD}" y="{y:.1f}" font-size="{HFS}" font-weight="700"><tspan fill="{GREEN}">{escape(job["company"])}</tspan>'
            f'<tspan fill="{MUTED}"> · </tspan><tspan fill="{FG}">{escape(job["role"])}</tspan></text>\n'
            f'  <text x="{W - PAD}" y="{y:.1f}" font-size="12" fill="{MUTED}" text-anchor="end">{escape(job["dates"])}</text>\n'
        )
        y += 4
        for runs in wrap(job["summary"], cols(PAD)):
            y += LH
            out.append(text_line(PAD, y, runs, italic=True))
        svg, y = bullets(job["bullets"], y + 4)
        out.append(svg)
    label = "Experience: " + "; ".join(f'{j["company"]}, {j["role"]} ({j["dates"]})' for j in EXPERIENCE)
    return window(round(y + 26), "Experience", "".join(out), "", label, heading=True)


def projects():
    out, y = [], TOP - LH - 22
    for p in PROJECTS:
        y += LH + 22
        out.append(
            f'  <text x="{PAD}" y="{y:.1f}"><tspan font-size="{HFS}" font-weight="700" fill="{GREEN}">{escape(p["name"])}</tspan>'
            f'<tspan dx="12" font-size="{FS}" fill="{TEXT}" font-style="italic">{escape(p["tagline"])}</tspan></text>\n'
        )
        svg, y = bullets(p["bullets"], y + 4)
        out.append(svg)
        y += LH + 10
        out.append(stack_row(p["stack"], y))
    label = "Projects: " + "; ".join(f'{p["name"]}: {p["tagline"]}' for p in PROJECTS)
    return window(round(y + 24), "Projects", "".join(out), "", label, heading=True)


for name, svg in (("experience", experience()), ("projects", projects())):
    open(f"{ROOT}/assets/{name}.svg", "w").write(svg)
    h = re.search(r'height="(\d+)"', svg)[1]
    print(f"wrote assets/{name}.svg  ({W}x{h}, {len(svg) // 1024} KB)")
