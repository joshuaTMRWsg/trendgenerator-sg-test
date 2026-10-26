#!/usr/bin/env python3
"""Fetch and filter the day's Singapore-only TikTok and Instagram videos.

    python3 scripts/sg_platforms.py OUTDIR            # run the actors, then filter
    python3 scripts/sg_platforms.py OUTDIR --no-fetch # re-filter raw files already in OUTDIR

Runs the four Apify actors pinned under "sg_platforms" in sources.json (one
run each, needs APIFY_TOKEN), saves their raw datasets to OUTDIR, and writes
OUTDIR/tiktok_sg.json and OUTDIR/instagram_sg.json: videos posted inside the
freshness window by Singapore creators only, ranked by views. Feed those two
files to scripts/platform_cards.py.

A video counts as Singapore only if one of these holds:
  * its account is on the SG watchlist in sources.json (SG publishers and
    creators, checked by hand); a publisher's video also needs a local
    marker in its caption text, hashtags aside, so their world-news clips
    drop out; or
  * it carries a local hashtag (#sgtiktok, #sgig, #新加坡生活 …), has no
    travel or tourist marker, and is not geotagged outside Singapore.
Plain #singapore is not enough on its own: tourists and overseas accounts use
it. Everything else is dropped and counted in the summary, never shown.
OUTDIR holds scraped data; keep it out of the repo.
"""
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "sources.json").read_text())["sg_platforms"]
SGT = timezone(timedelta(hours=8))
KEEP = 20


API = "https://api.apify.com/v2"


def api(path, payload=None, timeout=120):
    sep = "&" if "?" in path else "?"
    req = urllib.request.Request(f"{API}{path}{sep}token={os.environ['APIFY_TOKEN']}",
                                 json.dumps(payload).encode() if payload is not None else None,
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def run_actor(actor, payload, dest):
    # Started async and polled: the Instagram reel scraper can take longer
    # than the 300s cap on Apify's run-sync endpoints.
    try:
        run = api(f"/acts/{actor}/runs", payload)["data"]
        deadline = time.time() + 1200
        while run["status"] in ("READY", "RUNNING") and time.time() < deadline:
            run = api(f"/actor-runs/{run['id']}?waitForFinish=60", timeout=90)["data"]
        items = api(f"/datasets/{run['defaultDatasetId']}/items?clean=1", timeout=300)
        dest.write_text(json.dumps(items, ensure_ascii=False))
        return f"{actor}: run {run['id']} {run['status']}, {len(items)} items"
    except Exception as e:  # logged in the source ledger, never fatal
        dest.write_text("[]")
        return f"{actor}: failed ({e})"


def fetch(out, since):
    jobs = []
    for key, spec in CFG["actors"].items():
        payload = json.loads(json.dumps(spec["input"]).replace("{SINCE}", since))
        if "watchlist" in spec:
            payload[spec["watchlist"]["field"]] = CFG["watchlist"][spec["watchlist"]["platform"]]
        jobs.append((spec["id"], payload, out / f"raw_{key}.json"))
    with ThreadPoolExecutor(len(jobs)) as ex:
        for line in ex.map(lambda j: run_actor(*j), jobs):
            print(line)


def load(path):
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return []
    return [x for x in data if isinstance(x, dict) and not x.get("error")] if isinstance(data, list) else []


def tags_of(text, listed):
    found = {t.lower().lstrip("#") for t in listed or []}
    found |= {t.lower() for t in re.findall(r"#([^\s#]+)", text or "")}
    return found


def classify(handle, text, tags, place, platform):
    """Return the SG signal for a video, or None to drop it."""
    rules = CFG["rules"]
    watch = {h.lower() for h in CFG["watchlist"][platform]}
    if handle.lower() in watch:
        if handle.lower() in {h.lower() for h in rules["publishers"]}:
            # publishers post world news too; keep only their Singapore stories
            body = re.sub(r"#\S+", "", text or "")  # #singapore on a world-news clip doesn't count
            return "SG publisher" if re.search(rules["local_caption_pattern"], body, re.I) else None
        return "SG creator"
    low = (text or "").lower()
    if any(m in low for m in rules["travel_markers"]) or tags & set(rules["travel_hashtags"]):
        return None
    if place and not re.search(rules["sg_place_pattern"], place, re.I):
        return None
    local = tags & set(rules["local_hashtags"])
    if not local:
        return None
    sig = "#" + sorted(local)[0]
    return f"{sig} · {place}" if place else sig


def tiktok_items(out):
    seen, rows = set(), []
    for f in ("raw_tiktok_watchlist.json", "raw_tiktok_hashtags.json"):
        for x in load(out / f):
            vid = x.get("id")
            if not vid or vid in seen:
                continue
            seen.add(vid)
            a = x.get("authorMeta") or {}
            loc = x.get("locationMeta") or {}
            place = loc.get("locationName") or loc.get("city") or ""
            if loc and "singapore" in (loc.get("address", "") + loc.get("city", "")).lower():
                place = place or "Singapore"
            text = x.get("text") or ""
            sig = classify(a.get("name") or "", text, tags_of(text, [h.get("name") for h in x.get("hashtags") or [] if isinstance(h, dict)]), place, "tiktok")
            rows.append(dict(platform="tiktok", url=x.get("webVideoUrl"), handle=a.get("name"),
                             name=a.get("nickName"), avatar=a.get("avatar"), cover=(x.get("videoMeta") or {}).get("coverUrl"),
                             caption=text, views=x.get("playCount"), likes=x.get("diggCount"),
                             comments=x.get("commentCount"), posted=x.get("createTimeISO"), signal=sig))
    return rows


def instagram_items(out):
    seen, rows = set(), []
    for f in ("raw_instagram_watchlist.json", "raw_instagram_hashtags.json"):
        for x in load(out / f):
            sc = x.get("shortCode")
            if not sc or sc in seen:
                continue
            seen.add(sc)
            text = x.get("caption") or ""
            sig = classify(x.get("ownerUsername") or "", text, tags_of(text, x.get("hashtags")), x.get("locationName") or "", "instagram")
            rows.append(dict(platform="instagram", url=x.get("url") or f"https://www.instagram.com/reel/{sc}/",
                             handle=x.get("ownerUsername"), name=x.get("ownerFullName"), avatar=None,
                             cover=x.get("displayUrl"), caption=text,
                             views=x.get("videoPlayCount") or x.get("igPlayCount") or x.get("videoViewCount"),
                             likes=x.get("likesCount"), comments=x.get("commentsCount"),
                             posted=x.get("timestamp"), signal=sig))
    return rows


def pick(rows, now):
    def age_h(r):
        try:
            return (now - datetime.fromisoformat(r["posted"].replace("Z", "+00:00"))).total_seconds() / 3600
        except (TypeError, ValueError, AttributeError):
            return 1e9
    sg = [r for r in rows if r["signal"]]
    for window in (CFG["rules"]["fresh_hours"], CFG["rules"]["fallback_hours"]):
        fresh = [r for r in sg if age_h(r) <= window]
        if len(fresh) >= 2:
            break
    fresh.sort(key=lambda r: -(r["views"] or r["likes"] or 0))
    for i, r in enumerate(fresh[:KEEP], 1):
        r["rank"], r["age_h"], r["window_h"] = i, round(age_h(r)), window
    return fresh[:KEEP], dict(scraped=len(rows), sg=len(sg), dropped_non_sg=len(rows) - len(sg),
                              shown=min(len(fresh), KEEP), window_h=window)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    out = Path(args[0])
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    if "--no-fetch" not in sys.argv:
        fetch(out, (now.astimezone(SGT) - timedelta(days=3)).strftime("%Y-%m-%d"))
    for name, fn in (("tiktok_sg.json", tiktok_items), ("instagram_sg.json", instagram_items)):
        items, stats = pick(fn(out), now)
        (out / name).write_text(json.dumps(items, ensure_ascii=False, indent=1))
        print(f"{name}: {stats}")
        for r in items[:5]:
            print(f"  {r['rank']}. @{r['handle']} · {r['views']} views · {r['age_h']}h · {r['signal']} · {r['caption'][:60]!r}")


if __name__ == "__main__":
    main()
