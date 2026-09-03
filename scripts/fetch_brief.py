#!/usr/bin/env python3
"""Fetch the day's published brief and fold it into the repo.

Runs inside GitHub Actions. Does NOT call any AI service — it fetches an
already-published page, validates it, and writes it into the archive.

    BRIEF_SOURCE_URL=https://... python3 scripts/fetch_brief.py

Steps:
  1. fetch the source page
  2. validate it is a real brief, not an empty app shell or an error page
  3. patch in the calendar stylesheet, markers and nav if absent
  4. write archive/YYYY-MM-DD.html and index.html
  5. upsert today's entry in manifest.json
  6. run build_archive.py to regenerate the archive index and calendars

Exits non-zero with a plain-English reason if anything looks wrong, so a bad
fetch fails the workflow loudly instead of committing a broken page.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "archive"
MANIFEST = ROOT / "manifest.json"

SGT = timezone(timedelta(hours=8))
TODAY = datetime.now(SGT).date()

# Markers that prove we fetched the brief and not something else.
REQUIRED = ["Trend Wire", "TMRW"]
MIN_BYTES = 4000


def die(msg: str) -> None:
    print(f"::error::{msg}")
    sys.exit(1)


# ------------------------------------------------------------------- fetch --
url = (os.environ.get("BRIEF_SOURCE_URL") or "").strip()
if not url:
    die(
        "BRIEF_SOURCE_URL is not set. Add it under "
        "Settings > Secrets and variables > Actions > Variables."
    )

req = urllib.request.Request(
    url,
    headers={
        "User-Agent": "trendgenerator-sg/1.0 (+github actions)",
        "Accept": "text/html,application/xhtml+xml",
    },
)
try:
    with urllib.request.urlopen(req, timeout=45) as r:
        html = r.read().decode("utf-8", errors="replace")
except urllib.error.HTTPError as e:
    die(f"Source returned HTTP {e.code}. Is the page shared publicly?")
except Exception as e:  # noqa: BLE001 - surface anything as a clear failure
    die(f"Could not fetch the source page: {type(e).__name__}: {e}")


# ---------------------------------------------------------------- validate --
if len(html) < MIN_BYTES:
    die(
        f"Fetched only {len(html)} bytes — too small to be the brief. "
        "The URL probably returns an empty app shell rather than the page. "
        "Check it with: curl -s '<url>' | head -40"
    )

missing = [m for m in REQUIRED if m not in html]
if missing:
    die(
        f"Fetched page is missing expected content: {', '.join(missing)}. "
        "This usually means the URL needs a login, so the fetcher got a "
        "sign-in or placeholder page instead of the brief."
    )


# ------------------------------------------------------------------- patch --
# The published page may lack the calendar CSS, markers and nav, since those
# live only in the repo copy. Add whatever is absent so every archived day
# renders identically.

CAL_CSS = """
<style>
  .cal{border:1px solid var(--rule,#D8DED7);border-radius:3px;background:var(--surface,#fff);padding:14px 16px 12px;margin:22px 0 0}
  .cal-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px}
  .cal-title{font-family:var(--display,sans-serif);font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft,#4A5450)}
  .cal-nav{font-family:var(--mono,monospace);font-size:15px;line-height:1;background:none;border:1px solid var(--rule,#D8DED7);color:var(--ink-soft,#4A5450);border-radius:2px;width:24px;height:24px;cursor:pointer;padding:0}
  .cal-nav:hover:not(:disabled){border-color:var(--signal,#B4531A);color:var(--signal,#B4531A)}
  .cal-nav:disabled{opacity:.3;cursor:default}
  .cal-nav:focus-visible{outline:2px solid var(--signal,#B4531A);outline-offset:2px}
  .cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px}
  .cal-dow{font-family:var(--mono,monospace);font-size:9.5px;color:var(--ink-faint,#77827D);text-align:center;padding-bottom:4px}
  .cal-cell{font-family:var(--mono,monospace);font-size:11.5px;font-variant-numeric:tabular-nums;text-align:center;padding:5px 0;border-radius:2px;color:var(--ink-faint,#77827D);text-decoration:none;border-bottom:0}
  .cal-cell.out{visibility:hidden}
  a.cal-cell.has{color:var(--signal,#B4531A);font-weight:600;background:color-mix(in srgb,var(--signal,#B4531A) 10%,transparent)}
  a.cal-cell.has:hover{background:var(--signal,#B4531A);color:var(--surface,#fff)}
  .cal-cell.here{outline:1px solid var(--signal,#B4531A);outline-offset:-1px}
  .cal-all{display:block;margin-top:10px;font-family:var(--mono,monospace);font-size:11px;color:var(--ink-faint,#77827D);text-decoration:none;border-bottom:0}
  .cal-all:hover{color:var(--signal,#B4531A)}
  .nav{font-family:var(--mono,monospace);font-size:11.5px;display:flex;gap:14px;padding:14px 0 0;color:var(--ink-faint,#77827D)}
  .nav a{color:inherit;text-decoration:none;border-bottom:0}
  .nav a:hover{color:var(--signal,#B4531A)}
</style>
"""

if ".cal-grid" not in html:
    html = (
        html.replace("</head>", CAL_CSS + "</head>", 1)
        if "</head>" in html
        else CAL_CSS + html
    )

if "<!--CAL-->" not in html:
    # Prefer just before the first content section; fall back to after the
    # masthead; last resort, top of the wrapper.
    for anchor in ('<section class="sec">', "</header>", '<div class="wrap">'):
        if anchor in html:
            ins = "<!--CAL--><!--/CAL-->"
            html = (
                html.replace(anchor, ins + "\n" + anchor, 1)
                if anchor.startswith("<section")
                else html.replace(anchor, anchor + "\n" + ins, 1)
            )
            break
    else:
        die("Could not find anywhere to insert the calendar markers.")

if 'class="nav"' not in html:
    nav = '<div class="wrap"><nav class="nav"><a href="/">today</a><span>/</span><a href="/archive/">archive</a></nav></div>'
    html = html.replace("<body>", "<body>\n" + nav, 1)


# ------------------------------------------------------------------- write --
ARCHIVE.mkdir(exist_ok=True)
day_file = ARCHIVE / f"{TODAY.isoformat()}.html"
day_file.write_text(html)
(ROOT / "index.html").write_text(html)
print(f"wrote {day_file.name} and index.html ({len(html)} bytes)")


# ---------------------------------------------------------------- manifest --
def grab(pattern: str, default: str) -> str:
    m = re.search(pattern, html, re.S)
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else default


headline = grab(r'class="prio-row act">.*?<p>(.*?)</p>', "")
if not headline:
    headline = grab(r"<h1[^>]*>(.*?)</h1>", "Daily Singapore trend brief")
headline = re.sub(r"\s+", " ", headline)[:160]

nums = re.findall(r'class="n">(\d+)<', html)
compiled = grab(r"COMPILED ([^<]+)", "")

entry = {
    "date": TODAY.isoformat(),
    "compiled": compiled or "09:00 SGT",
    "headline": headline,
    "trends": int(nums[0]) if len(nums) > 0 else 0,
    "nogo": int(nums[1]) if len(nums) > 1 else 0,
    "calendar": int(nums[2]) if len(nums) > 2 else 0,
    "file": f"{TODAY.isoformat()}.html",
}

data = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"briefs": []}
data["briefs"] = [b for b in data["briefs"] if b["date"] != entry["date"]]
data["briefs"].append(entry)
data["briefs"].sort(key=lambda b: b["date"], reverse=True)
MANIFEST.write_text(json.dumps(data, indent=2) + "\n")
print(f"manifest: {len(data['briefs'])} entries — {entry['headline'][:60]}")


# ------------------------------------------------------------------- build --
subprocess.run([sys.executable, str(ROOT / "build_archive.py")], check=True)
