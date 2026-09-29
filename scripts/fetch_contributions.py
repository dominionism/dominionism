#!/usr/bin/env python3
"""Scrape the public contribution calendar into data/contributions.json. No token needed:
GitHub serves the same fragment the profile page embeds at /users/<user>/contributions.

    python3 scripts/fetch_contributions.py

Exits non-zero, writing nothing, if the page no longer parses, so a markup change on
GitHub's side fails the workflow loudly instead of committing an empty graph.
"""
import json, os, re, sys, urllib.request
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser

USER = "dominionism"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = f"https://github.com/users/{USER}/contributions"


class Calendar(HTMLParser):
    """Day cells (id -> date, level), their tooltips ("17 contributions on October 5th."), and the headline."""

    def __init__(self):
        super().__init__()
        self.cells, self.tips, self.headline = {}, {}, ""
        self._into, self._buf = None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "td" and a.get("data-date") and "ContributionCalendar-day" in (a.get("class") or ""):
            self.cells[a.get("id")] = (a["data-date"], int(a.get("data-level") or 0))
        elif tag == "tool-tip" and a.get("for"):
            self._into, self._buf = a["for"], []
        elif tag == "h2" and a.get("id") == "js-contribution-activity-description":
            self._into, self._buf = "headline", []

    def handle_data(self, data):
        if self._into:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if self._into and tag in ("tool-tip", "h2"):
            text = " ".join("".join(self._buf).split())
            if self._into == "headline":
                self.headline = text
            else:
                self.tips[self._into] = text
            self._into = None


def count(tip):
    m = re.match(r"(No|[\d,]+) contributions? on", tip or "")
    if not m:
        sys.exit(f"unrecognised tooltip: {tip!r}")
    return 0 if m[1] == "No" else int(m[1].replace(",", ""))


req = urllib.request.Request(URL, headers={"User-Agent": f"{USER}-profile-readme"})
cal = Calendar()
cal.feed(urllib.request.urlopen(req, timeout=30).read().decode())

days = sorted(
    ({"date": d, "count": count(cal.tips.get(cid)), "level": lvl} for cid, (d, lvl) in cal.cells.items()),
    key=lambda d: d["date"],
)
if len(days) < 360:
    sys.exit(f"expected a year of days, parsed {len(days)}; has the calendar markup changed?")

# Streaks: the longest run of active days, and the run ending today (a quiet today doesn't
# break it yet; the day isn't over).
longest, run, start, span = 0, 0, None, (None, None)
for d in days:
    run = run + 1 if d["count"] else 0
    if run == 1:
        start = d["date"]
    if run > longest:
        longest, span = run, (start, d["date"])
current = 0
for d in reversed(days[:-1] if not days[-1]["count"] else days):
    if not d["count"]:
        break
    current += 1

best = max(days, key=lambda d: d["count"])
months = Counter()
for d in days:
    months[d["date"][:7]] += d["count"]

summary = {
    "user": USER,
    "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
    "headline": cal.headline,
    "total": sum(d["count"] for d in days),
    "active_days": sum(1 for d in days if d["count"]),
    "streak": {"current": current, "longest": longest, "longest_from": span[0], "longest_to": span[1]},
    "best_day": {"date": best["date"], "count": best["count"]},
    "months": dict(sorted(months.items())),
}
# One day per line keeps the daily diff readable
text = json.dumps(summary, indent=2)[:-2] + ',\n  "days": [\n'
text += ",\n".join(f"    {json.dumps(d)}" for d in days) + "\n  ]\n}\n"

os.makedirs(f"{ROOT}/data", exist_ok=True)
open(f"{ROOT}/data/contributions.json", "w").write(text)
print(f"wrote data/contributions.json  ({len(days)} days, {summary['total']} contributions; "
      f"streak {current} now / {longest} best; best day {best['count']} on {best['date']})")
