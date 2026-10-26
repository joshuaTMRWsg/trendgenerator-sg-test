#!/usr/bin/env python3
"""Render the TikTok and Instagram trend cards from the day's Apify datasets.

    python3 scripts/platform_cards.py OUT/tiktok_sg.json OUT/instagram_sg.json index.html archive/YYYY-MM-DD.html

Takes the Singapore-only lists written by scripts/sg_platforms.py. The older
raw formats (TikTok Creative Center hashtags, Instagram Explore) still render,
for re-stamping archive pages.

Replaces the <!--TIKTOK-->…<!--/TIKTOK--> and <!--IG-->…<!--/IG--> blocks in
each page. Top two items show; the rest sit behind a "Show N more" toggle.
Thumbnails are hotlinked from Apify / TikTok's CDN, not stored, and each links
to the post. Those URLs expire, so thumbnails on archive pages stop loading
after a few days by design; the post links keep working.
"""
import html
import json
import re
import sys

VISIBLE = 2
NEWTAB = ' target="_blank" rel="noopener noreferrer"'


def esc(s):
    return html.escape(str(s or ""), quote=True)


def safe_url(u):
    return esc(u) if isinstance(u, str) and u.startswith("https://") else ""


def short(n):
    if n is None:
        return "—"
    n = float(n)
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if n >= div:
            return f"{n / div:.1f}".rstrip("0").rstrip(".") + suf
    return str(int(n))


def spark(points):
    vals = [p.get("value", 0) or 0 for p in points or []]
    if len(vals) < 2:
        return ""
    w, h = 64, 18
    xs = [i * w / (len(vals) - 1) for i in range(len(vals))]
    ys = [h - 1 - (v / 100) * (h - 2) for v in vals]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    return (f'<svg class="spark" viewBox="0 0 {w} {h}" width="{w}" height="{h}" aria-hidden="true">'
            f'<polyline points="{pts}" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>')


def tiktok_row(x):
    creators = x.get("Top Creators") or []
    top = creators[0] if creators else {}
    avatar = safe_url(top.get("avatar"))
    img = (f'<img class="av" src="{avatar}" alt="" loading="lazy" referrerpolicy="no-referrer" '
           f'onerror="this.style.visibility=\'hidden\'">' if avatar else '<span class="av"></span>')
    arrow = "▲" if x.get("Trend Direction") == "up" else "▼"
    cls = "up" if x.get("Trend Direction") == "up" else "down"
    who = f'top creator {esc(top.get("handle"))}' if top.get("handle") else ""
    return (f'<li class="tt"><span class="rk">{esc(x.get("Rank"))}</span>{img}'
            f'<span class="tt-main"><a href="{safe_url(x.get("TikTok URL"))}"{NEWTAB}>{esc(x.get("Hashtag"))}</a>'
            f'<span class="tt-meta">{short(x.get("Posts"))} posts · {short(x.get("Video Views"))} views · {who}</span></span>'
            f'<span class="tt-trend {cls}">{spark(x.get("Trend Data"))}{arrow}</span></li>')


def ig_tile(i, x):
    media = (x.get("media_items") or [{}])[0]
    cover = safe_url(x.get("cover_url") or media.get("cover_url"))
    post = safe_url(x.get("post_url"))
    badge = '<span class="play">▶</span>' if x.get("has_video") else ""
    body = (f'<a class="ig-cover" href="{post}"{NEWTAB}><img src="{cover}" alt="" loading="lazy" '
            f'onerror="this.style.visibility=\'hidden\'">{badge}</a>')
    return (f'<figure class="ig">{body}<figcaption>'
            f'<span class="ig-meta"><b>{i}</b> <a href="{post}"{NEWTAB}>@{esc(x.get("owner_username"))}</a> · {short(x.get("view_count"))} views</span>'
            '</figcaption></figure>')


# Captions are other people's words. One that uses the shorthand banned by the
# sensitivity check in CLAUDE.md is left off the card rather than edited.
BANNED = re.compile(r"\baunt|\buncle|阿叔|阿姨|安娣|安哥|clears? the shelf", re.I)


def snippet(text, n=70):
    if BANNED.search(text or ""):
        return ""
    t = " ".join(re.sub(r"#\S+", "", text or "").split())
    return t[:n].rstrip() + ("…" if len(t) > n else "")


def video_row(x):
    """A row for one Singapore video from scripts/sg_platforms.py."""
    avatar = safe_url(x.get("avatar"))
    img = (f'<img class="av" src="{avatar}" alt="" loading="lazy" referrerpolicy="no-referrer" '
           f'onerror="this.style.visibility=\'hidden\'">' if avatar else '<span class="av"></span>')
    return (f'<li class="tt"><span class="rk">{esc(x.get("rank"))}</span>{img}'
            f'<span class="tt-main"><a href="{safe_url(x.get("url"))}"{NEWTAB}>@{esc(x.get("handle"))}</a>'
            f'<span class="tt-meta">{short(x.get("views"))} views · {short(x.get("likes"))} likes · {esc(x.get("signal"))}</span>'
            f'<span class="tt-meta">{esc(snippet(x.get("caption")))}</span></span>'
            f'<span class="tt-trend">{esc(x.get("age_h"))}h ago</span></li>')


def video_tile(x):
    cover = safe_url(x.get("cover"))
    post = safe_url(x.get("url"))
    return (f'<figure class="ig"><a class="ig-cover" href="{post}"{NEWTAB}><img src="{cover}" alt="" loading="lazy" '
            f'referrerpolicy="no-referrer" onerror="this.style.visibility=\'hidden\'"><span class="play">▶</span></a><figcaption>'
            f'<span class="ig-meta"><b>{esc(x.get("rank"))}</b> <a href="{post}"{NEWTAB}>@{esc(x.get("handle"))}</a> · '
            f'{short(x.get("views"))} views · {esc(x.get("age_h"))}h · {esc(x.get("signal"))}</span>'
            f'{esc(snippet(x.get("caption"), 60))}</figcaption></figure>')


def more(n, inner):
    return (f'<details class="more"><summary>Show {n} more</summary>{inner}</details>' if n > 0 else "")


def tiktok_block(data):
    if data and data[0].get("platform"):
        rows = [video_row(x) for x in data]
        return ('<!--TIKTOK--><ol class="tt-list">' + "".join(rows[:VISIBLE]) + "</ol>"
                + more(len(rows) - VISIBLE, '<ol class="tt-list">' + "".join(rows[VISIBLE:]) + "</ol>")
                + "<!--/TIKTOK-->")
    data = sorted(data, key=lambda x: x.get("Rank") or 999)
    rows = [tiktok_row(x) for x in data]
    return ('<!--TIKTOK--><ol class="tt-list">' + "".join(rows[:VISIBLE]) + "</ol>"
            + more(len(rows) - VISIBLE, '<ol class="tt-list">' + "".join(rows[VISIBLE:]) + "</ol>")
            + "<!--/TIKTOK-->")


def ig_block(data):
    if data and data[0].get("platform"):
        tiles = [video_tile(x) for x in data]
        return ('<!--IG--><div class="ig-grid top">' + "".join(tiles[:VISIBLE]) + "</div>"
                + more(len(tiles) - VISIBLE, '<div class="ig-grid">' + "".join(tiles[VISIBLE:]) + "</div>")
                + "<!--/IG-->")
    tiles_big = [ig_tile(i, x) for i, x in enumerate(data[:VISIBLE], 1)]
    tiles = [ig_tile(i, x) for i, x in enumerate(data[VISIBLE:], VISIBLE + 1)]
    return ('<!--IG--><div class="ig-grid top">' + "".join(tiles_big) + "</div>"
            + more(len(tiles), '<div class="ig-grid">' + "".join(tiles) + "</div>")
            + "<!--/IG-->")


def main():
    tiktok, ig, *pages = sys.argv[1:]
    tt_html = tiktok_block(json.load(open(tiktok)))
    ig_html = ig_block(json.load(open(ig)))
    for p in pages:
        s = open(p, encoding="utf-8").read()
        for tag, block in (("TIKTOK", tt_html), ("IG", ig_html)):
            pat = re.compile(rf"<!--{tag}-->.*?<!--/{tag}-->", re.S)
            if not pat.search(s):
                sys.exit(f"{p}: no <!--{tag}--> markers")
            s = pat.sub(lambda _: block, s)
        open(p, "w", encoding="utf-8").write(s)
        print(f"{p}: platform cards stamped")


if __name__ == "__main__":
    main()
