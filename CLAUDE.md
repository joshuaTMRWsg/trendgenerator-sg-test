# Project instructions

These rules override the scheduled-task prompt wherever the two disagree —
specifically its "max 5" trend count, its reader-facing **Gaps in today's
scan** section, and the "exactly five `<h2>` sections" line in its
verification list.

## Daily brief workflow

After committing and pushing a day's brief to its feature branch
(`claude/...`), open a pull request into `main` and merge it immediately —
don't leave the branch waiting for manual review. Confirm the merge landed
by checking `git log origin/main -1 --oneline` and report the merge commit
SHA.

## Trending now — required source mix

**Trending now** carries six to seven entries, and the mix is fixed:

| Slot | Count | What goes in it |
|---|---|---|
| TikTok | 2 | The **top two** trending items for Singapore — hashtag, sound or clip, in rank order |
| Instagram | 2 | Trending Story or Reel formats circulating in SG |
| News | 2–3 | As before, off the feed / API / publisher ladder |

The four platform entries are **in addition to** the news trends, not a
replacement for them. Name the platform in the `Source` row so the mix reads
at a glance: `TikTok · #hashtag · No. 1 SG`, `Instagram · Reel`, or the
publisher URL for news.

**Evidence for a platform slot — work down, stop at the first that works:**

1. A direct authenticated read (`TIKTOK_CC_COOKIE` or `APIFY_TOKEN` in env).
   Cite the rank and the metric you actually saw.
2. SG media reporting the clip — The Independent SG, Stomp, Mothership
   Trending, The Smart Local, Goody Feed. Attribute it as what it is:
   *"a TikTok clip reported at 189,000 views by Stomp"* — platform, figure,
   and who reported the figure.
3. Search results that name the platform plus the creator or hashtag, and
   carry a date inside 48h.

Never print a rank, a view count or the word "trending" for something you did
not see in one of those three. If a slot cannot be filled honestly, ship the
slot empty: a `<dd class="none">` naming the platform that returned nothing
and what was tried. An empty slot is a fact about the day; an invented trend
is a lie about it. The 48h freshness rule applies to platform slots exactly as
it does to news.

**Word budget moves with the mix.** The ledger below is debug-only and no
longer counts toward the visible total, so allocate:
`This week` 90 · `Trending now` 550 · `No-go` 130 · `Calendar` 380.
Visible total still has to land inside 1200 — count before committing and cut
the calendar whys first.

## Gaps → debug-only source ledger

**Gaps in today's scan** is no longer reader-facing. Replace it with a source
ledger that ships on every page but stays hidden unless the URL carries
`?debug` or `#debug`.

It holds two things, in this order:

1. **Every source touched this run**, one row each — the 1a feeds and APIs,
   the named HTML pages, any primary source, any substitute publisher, and
   any search fallback. Each row: name, full URL, HTTP status, and what it
   fed. Status is the real one — `200`, `404`, `403`, `500`, `blocked`
   (egress refused the connection), `timeout`. No row without a status.
2. **Unresolved** — the old Gaps bullets, same discipline: name the specific
   thing you could not confirm and what you tried. No cap now that it is
   behind a flag, but a permanently blocked domain is still a ledger row, not
   an unresolved item.

Markup — last section on the page, after the calendar:

```html
<section class="sec" id="debug" hidden>
  <div class="sec-head"><h2>Source ledger</h2><span class="note">debug</span></div>
  <div class="sec-rule"></div>
  <table class="srcs">
    <tr><th>Source</th><th>URL</th><th>Status</th><th>Fed</th></tr>
    <tr><td>Mothership</td><td>https://mothership.sg/feed/</td><td class="ok">200</td><td>Trend 1</td></tr>
    <tr><td>Live PSI</td><td>https://api.data.gov.sg/v1/environment/psi</td><td class="bad">blocked</td><td>—</td></tr>
  </table>
  <div class="gap">
    <h4>Unresolved</h4>
    <p><strong>Thing you could not confirm</strong> — what you tried.</p>
  </div>
</section>
<script>
(function(){
  var d=document.getElementById('debug'); if(!d) return;
  function sync(){
    d.hidden=!(/(^|[?&])debug\b/.test(location.search)||/(^|#)debug\b/.test(location.hash));
  }
  sync(); addEventListener('hashchange',sync);
})();
</script>
```

CSS, added once to the token block so every day matches:

```css
.srcs{width:100%;border-collapse:collapse;font-family:var(--mono);font-size:11.5px;margin-top:4px}
.srcs th{text-align:left;color:var(--ink-faint);font-weight:600;padding:0 10px 6px 0}
.srcs td{padding:4px 10px 4px 0;border-top:1px solid var(--rule-soft);vertical-align:top;word-break:break-all}
.srcs .ok{color:var(--clear)}
.srcs .bad{color:var(--risk)}
```

## Verification, amended

Replacing the matching lines in the scheduled prompt's checklist:

- **four visible `<h2>` sections** — This week, Trending now, No-go list,
  Calendar — plus the `#debug` one, so five `<h2>` in the file;
- visible word count 900–1200, counted after stripping tags, the
  `<!--CAL-->` block, the `#debug` section **and** the collapsed
  `<details class="more">` lists;
- loading the page with no query and no hash shows four sections and no
  ledger; `?debug` and `#debug` each reveal it;
- every ledger row carries a status;
- both `index.html` and `archive/<today>.html` carry the ledger.

## Platform cards (TikTok + Instagram)

Both platform slots come from the Apify actors pinned in `sources.json`, one
run each per day, `maxItems`/`max_results` 20. Save each dataset to a temp
file (never commit it) and stamp the cards with:

```bash
python3 scripts/platform_cards.py tiktok.json instagram.json index.html archive/<today>.html
```

The script fills the `<!--TIKTOK--><!--/TIKTOK-->` and `<!--IG--><!--/IG-->`
markers inside each platform card (directly under its `.trend-top`): the top
two items show, the other 18 sit behind a "Show 18 more" toggle. Instagram
tiles are thumbnails whose `src` is the Apify-hosted cover and which link to
the post; TikTok rows show rank, hashtag, posts, views, the top creator's
avatar and a 7-day sparkline. Media is hotlinked, never stored — it is only
valid for the day, and older archive pages losing their thumbnails is
expected.

The Instagram actor's `country` setting does not geolocate. Title the card
`Instagram · Explore feed (SG locale)` and say plainly in `What` whether any
post carries a Singapore creator, location or hashtag. If none does, the
trendjack is `<dd class="none">`. Never call that feed "trending in SG".

If an actor run fails, leave its markers empty and fall back to the evidence
ladder above for that slot.
