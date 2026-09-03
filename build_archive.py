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
import json
import pathlib
import re
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent
MANIFEST = ROOT / "manifest.json"
ARCHIVE = ROOT / "archive"

CAL_RE = re.compile(r"<!--CAL-->.*?<!--/CAL-->", re.S)

briefs = json.loads(MANIFEST.read_text())["briefs"]
briefs.sort(key=lambda b: b["date"], reverse=True)
by_date = {b["date"]: b for b in briefs}
latest = briefs[0]["date"] if briefs else None


# ---------------------------------------------------------------- calendar --
def build_calendar(rel: str, current: str | None) -> str:
    """Month grids for every month that has briefs. `rel` prefixes hrefs so the
    same markup works from the root and from inside archive/."""
    months: dict[tuple[int, int], list[date]] = {}
    for b in briefs:
        d = date.fromisoformat(b["date"])
        months.setdefault((d.year, d.month), []).append(d)

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
                if iso in by_date:
                    classes.append("has")
                    title = by_date[iso]["headline"].replace('"', "&quot;")
                    cells.append(
                        f'<a class="{" ".join(classes)}" href="{rel}archive/{iso}.html" '
                        f'title="{title}">{d.day}</a>'
                    )
                else:
                    cells.append(f'<span class="{" ".join(classes)}">{d.day}</span>')

        label = date(yr, mo, 1).strftime("%B %Y")
        grids.append(
            f'<div class="cal-month" data-i="{i}"{"" if i == 0 else " hidden"}>'
            f'<div class="cal-grid">'
            f'<span class="cal-dow">M</span><span class="cal-dow">T</span>'
            f'<span class="cal-dow">W</span><span class="cal-dow">T</span>'
            f'<span class="cal-dow">F</span><span class="cal-dow">S</span>'
            f'<span class="cal-dow">S</span>{"".join(cells)}</div>'
            f'<div class="cal-label" hidden>{label}</div></div>'
        )

    first_label = date(*keys[0], 1).strftime("%B %Y")
    nav = (
        '<div class="cal-head">'
        '<button class="cal-nav" data-step="-1" aria-label="Earlier month">&#8249;</button>'
        f'<span class="cal-title">{first_label}</span>'
        '<button class="cal-nav" data-step="1" aria-label="Later month" disabled>&#8250;</button>'
        "</div>"
    )
    script = """
<script>
(function(){
  var root=document.currentScript.closest('.cal'); if(!root) return;
  var months=[].slice.call(root.querySelectorAll('.cal-month')),
      title=root.querySelector('.cal-title'),
      btns=[].slice.call(root.querySelectorAll('.cal-nav')), i=0;
  function show(n){
    if(n<0||n>=months.length) return;
    months[i].hidden=true; i=n; months[i].hidden=false;
    title.textContent=months[i].querySelector('.cal-label').textContent;
    btns[0].disabled=(i>=months.length-1); btns[1].disabled=(i<=0);
  }
  btns[0].addEventListener('click',function(){show(i+1);});
  btns[1].addEventListener('click',function(){show(i-1);});
})();
</script>"""
    return (
        f'<!--CAL--><nav class="cal" aria-label="Brief archive calendar">{nav}'
        f'{"".join(grids)}'
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
    html = path.read_text()
    if not CAL_RE.search(html):
        print(f"  !! no <!--CAL--> markers in {path.name}, skipped")
        continue
    path.write_text(CAL_RE.sub(lambda _: build_calendar(rel, current), html))
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
