#!/usr/bin/env python3
"""Regenerate the archive index and inject the calendar into every page.

Run after adding a day's brief:
    python3 build_archive.py

Reads manifest.json, then:
  * writes archive/index.html  — list view, newest first, grouped by month
  * injects a month-grid calendar between the <!--CAL--> markers in
    index.html and every archive/YYYY-MM-DD.html

Pages are plain static HTML with no include mechanism, so the calendar is
stamped into each file rather than shared. Re-running is always safe: the
markers are replaced, never appended to.

Standard library only.
"""
import calendar
import html
import json
import pathlib
import re
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent
MANIFEST = ROOT / "manifest.json"
ARCHIVE = ROOT / "archive"

CAL_RE = re.compile(r"<!--CAL-->.*?<!--/CAL-->", re.S)

# Each brief's own "Calendar" section rows carry id="ev-YYYY-MM-DD[-b]" (the
# suffix disambiguates two events landing on the same date). Extracted per
# page so the mini calendar's star badges and anchors always match that
# page's own list further down.
EVENT_ROW_RE = re.compile(
    r'<div class="cal-row[^"]*"\s+id="(ev-\d{4}-\d{2}-\d{2}(?:-[a-z])?)"[^>]*>'
    r".*?<h4>(.*?)<span class=\"stars[^\"]*\">(★+)</span>",
    re.S,
)

# Gazetted SG public holidays (MOM). Extend this as future years are needed;
# an unlisted year just means no page will highlight a holiday for it yet.
SG_PUBLIC_HOLIDAYS = {
    "2026-01-01": "New Year's Day",
    "2026-02-17": "Chinese New Year",
    "2026-02-18": "Chinese New Year",
    "2026-03-21": "Hari Raya Puasa",
    "2026-04-03": "Good Friday",
    "2026-05-01": "Labour Day",
    "2026-05-27": "Hari Raya Haji",
    "2026-05-31": "Vesak Day",
    "2026-06-01": "Vesak Day (in lieu)",
    "2026-08-09": "National Day",
    "2026-08-10": "National Day (in lieu)",
    "2026-11-08": "Deepavali",
    "2026-11-09": "Deepavali (in lieu)",
    "2026-12-25": "Christmas Day",
}

briefs = json.loads(MANIFEST.read_text())["briefs"]
briefs.sort(key=lambda b: b["date"], reverse=True)
by_date = {b["date"]: b for b in briefs}
latest = briefs[0]["date"] if briefs else None


def parse_events(page_html: str) -> dict[str, tuple[int, str, str]]:
    """iso -> (max stars, combined title, anchor id of the first row that day)."""
    events: dict[str, tuple[int, str, str]] = {}
    for m in EVENT_ROW_RE.finditer(page_html):
        anchor, title_html, stars = m.groups()
        iso = anchor[3:13]
        title = html.unescape(re.sub(r"<[^>]+>", "", title_html)).strip()
        n = len(stars)
        if iso in events:
            prev_n, prev_title, prev_anchor = events[iso]
            events[iso] = (max(prev_n, n), f"{prev_title} · {title}", prev_anchor)
        else:
            events[iso] = (n, title, anchor)
    return events


# ---------------------------------------------------------------- calendar --
def build_calendar(rel: str, current: str | None, events: dict[str, tuple[int, str, str]]) -> str:
    """Month grids covering every month with a brief or a calendar-section
    event on this page. `rel` prefixes hrefs so the same markup works from
    the root and from inside archive/."""
    months: set[tuple[int, int]] = set()
    for b in briefs:
        d = date.fromisoformat(b["date"])
        months.add((d.year, d.month))
    for iso in events:
        d = date.fromisoformat(iso)
        months.add((d.year, d.month))

    if not months:
        return "<!--CAL--><!--/CAL-->"

    keys = sorted(months, reverse=True)
    grids = []
    for i, (yr, mo) in enumerate(keys):
        cells = []
        # Monday-first grid; leading blanks keep the columns aligned.
        for week in calendar.Calendar(firstweekday=0).monthdatescalendar(yr, mo):
            for d in week:
                if d.month != mo:
                    cells.append('<span class="cal-cell out"></span>')
                    continue
                iso = d.isoformat()
                classes = ["cal-cell"]
                if iso == current:
                    classes.append("here")
                holiday = SG_PUBLIC_HOLIDAYS.get(iso)
                if holiday:
                    classes.append("holiday")
                elif d.weekday() >= 5:
                    classes.append("weekend")
                ev = events.get(iso)
                if ev:
                    classes.append(f"ev{min(ev[0], 3)}")

                titles = [t for t in (holiday,) if t]
                if iso in by_date:
                    classes.append("has")
                    titles.append(by_date[iso]["headline"])
                    href = f"{rel}archive/{iso}.html"
                elif ev:
                    titles.append(ev[1])
                    href = f"#{ev[2]}"
                else:
                    href = None

                title_attr = html.escape(" — ".join(titles))
                if href:
                    cells.append(
                        f'<a class="{" ".join(classes)}" href="{href}" '
                        f'title="{title_attr}">{d.day}</a>'
                    )
                elif titles:
                    cells.append(f'<span class="{" ".join(classes)}" title="{title_attr}">{d.day}</span>')
                else:
                    cells.append(f'<span class="{" ".join(classes)}">{d.day}</span>')

        label = date(yr, mo, 1).strftime("%B %Y")
        grids.append(
            f'<div class="cal-grid">'
            f'<span class="cal-dow">M</span><span class="cal-dow">T</span>'
            f'<span class="cal-dow">W</span><span class="cal-dow">T</span>'
            f'<span class="cal-dow">F</span><span class="cal-dow">S</span>'
            f'<span class="cal-dow">S</span>{"".join(cells)}</div>'
            f'<div class="cal-label" hidden>{label}</div>'
        )

    # Open on the month containing `current` (today's page) rather than
    # always the chronologically latest grid, so a brief whose Calendar
    # section reaches into next month doesn't hide the current month.
    default_i = 0
    if current:
        cur_ym = (date.fromisoformat(current).year, date.fromisoformat(current).month)
        if cur_ym in keys:
            default_i = keys.index(cur_ym)
    grids = [
        f'<div class="cal-month" data-i="{i}"{"" if i == default_i else " hidden"}>{body}</div>'
        for i, body in enumerate(grids)
    ]

    default_label = date(*keys[default_i], 1).strftime("%B %Y")
    earlier_disabled = " disabled" if default_i >= len(keys) - 1 else ""
    later_disabled = " disabled" if default_i <= 0 else ""
    nav = (
        '<div class="cal-head">'
        f'<button class="cal-nav" data-step="-1" aria-label="Earlier month"{earlier_disabled}>&#8249;</button>'
        f'<span class="cal-title">{default_label}</span>'
        f'<button class="cal-nav" data-step="1" aria-label="Later month"{later_disabled}>&#8250;</button>'
        "</div>"
    )
    script = f"""
<script>
(function(){{
  var root=document.currentScript.closest('.cal'); if(!root) return;
  var months=[].slice.call(root.querySelectorAll('.cal-month')),
      title=root.querySelector('.cal-title'),
      btns=[].slice.call(root.querySelectorAll('.cal-nav')), i={default_i};
  function show(n){{
    if(n<0||n>=months.length) return;
    months[i].hidden=true; i=n; months[i].hidden=false;
    title.textContent=months[i].querySelector('.cal-label').textContent;
    btns[0].disabled=(i>=months.length-1); btns[1].disabled=(i<=0);
  }}
  btns[0].addEventListener('click',function(){{show(i+1);}});
  btns[1].addEventListener('click',function(){{show(i-1);}});
}})();
</script>"""
    legend = (
        '<p class="cal-legend">'
        '<span class="lg holiday">Public holiday</span>'
        '<span class="lg weekend">Weekend</span>'
        '<span class="lg">&#9733; calendar item &mdash; tap to jump</span>'
        "</p>"
    )
    return (
        f'<!--CAL--><nav class="cal" aria-label="Brief archive calendar">{nav}'
        f'{"".join(grids)}{legend}'
        f'<a class="cal-all" href="{rel}archive/">All briefs &#8594;</a>'
        f"{script}</nav><!--/CAL-->"
    )


# ------------------------------------------------------------------ inject --
pages = [(ROOT / "index.html", "", latest)]
for f in sorted(ARCHIVE.glob("*.html")):
    if f.name != "index.html":
        pages.append((f, "../", f.stem))

stamped = 0
for path, rel, current in pages:
    if not path.exists():
        continue
    page_html = path.read_text()
    if not CAL_RE.search(page_html):
        print(f"  !! no <!--CAL--> markers in {path.name}, skipped")
        continue
    events = parse_events(page_html)
    path.write_text(CAL_RE.sub(lambda _: build_calendar(rel, current, events), page_html))
    stamped += 1


# ------------------------------------------------------------ archive list --
months_list: dict[str, list] = {}
for b in briefs:
    d = date.fromisoformat(b["date"])
    months_list.setdefault(d.strftime("%B %Y"), []).append((d, b))

rows = []
for month, items in months_list.items():
    rows.append(f'<h2 class="month">{month}</h2>')
    for d, b in items:
        rows.append(f"""
<a class="row" href="{b['file']}">
  <span class="d">{d.strftime('%a %-d').upper()}</span>
  <span class="body">
    <span class="h">{b['headline']}</span>
    <span class="meta">{b['trends']} trends &middot; {b['nogo']} no-go &middot; {b['calendar']} calendar &middot; compiled {b['compiled']}</span>
  </span>
</a>""")

(ARCHIVE / "index.html").write_text(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>SG Trend Wire — Archive</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
  :root{{--paper:#F5F7F4;--ink:#141A17;--ink-soft:#4A5450;--ink-faint:#77827D;
        --rule-soft:#E6EAE4;--signal:#B4531A;
        --display:'Archivo','Helvetica Neue',Arial,sans-serif;--body:'Source Serif 4',Georgia,serif;
        --mono:'JetBrains Mono',ui-monospace,Menlo,monospace}}
  @media (prefers-color-scheme:dark){{:root{{--paper:#0E1211;--ink:#E6EBE7;--ink-soft:#A3AEA8;
        --ink-faint:#7C8781;--rule-soft:#212927;--signal:#E08544}}}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.5}}
  .wrap{{max-width:820px;margin:0 auto;padding:0 24px 72px}}
  .nav{{font-family:var(--mono);font-size:11.5px;display:flex;gap:14px;padding:14px 0 0;color:var(--ink-faint)}}
  .nav a{{color:inherit;text-decoration:none}} .nav a:hover{{color:var(--signal)}}
  .masthead{{border-bottom:2px solid var(--ink);padding:36px 0 14px}}
  .org{{font-family:var(--display);font-weight:700;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--signal);margin:0 0 10px}}
  h1{{font-family:var(--display);font-weight:700;font-size:clamp(30px,6vw,46px);line-height:1.02;letter-spacing:-.02em;margin:0}}
  .count{{font-family:var(--mono);font-size:12px;color:var(--ink-soft);margin-top:14px}}
  .month{{font-family:var(--display);font-size:13px;letter-spacing:.13em;text-transform:uppercase;margin:44px 0 6px;padding-bottom:6px;border-bottom:1px solid var(--ink)}}
  .row{{display:grid;grid-template-columns:72px 1fr;gap:16px;padding:14px 0;border-bottom:1px solid var(--rule-soft);
        color:inherit;text-decoration:none;align-items:baseline}}
  .row:hover .h{{color:var(--signal)}}
  .d{{font-family:var(--mono);font-size:12.5px;font-weight:600;font-variant-numeric:tabular-nums}}
  .h{{display:block;font-family:var(--display);font-weight:600;font-size:16px;margin-bottom:3px}}
  .meta{{display:block;font-family:var(--mono);font-size:11px;color:var(--ink-faint)}}
</style>
</head>
<body>
<div class="wrap">
  <nav class="nav"><a href="../">today</a><span>/</span><a href="./">archive</a></nav>
  <header class="masthead">
    <p class="org">TMRW Tech &middot; Social</p>
    <h1>Trend Wire Archive</h1>
    <div class="count">{len(briefs)} brief{'s' if len(briefs) != 1 else ''} &middot; newest first</div>
  </header>
  {''.join(rows)}
</div>
</body>
</html>
""")

print(f"archive/index.html: {len(briefs)} entries · calendar stamped into {stamped} page(s)")
