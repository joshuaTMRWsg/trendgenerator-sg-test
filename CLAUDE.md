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
  `<!--CAL-->` block, the `#debug` section, the collapsed
  `<details class="more">` lists **and** every client-brand element
  (`<dt>Our brands</dt>`, `details.brand-fit`, `.brand-flag`) — keep a flag
  to one short line all the same;
- loading the page with no query and no hash shows four sections and no
  ledger; `?debug` and `#debug` each reveal it;
- every ledger row carries a status;
- both `index.html` and `archive/<today>.html` carry the ledger;
- every `.chip` on the page matches a `chip` in `brands.json`, and no
  brand line sits on an entry that is also on the No-go list.

## Client brands

The roster is `brands.json` — the only place brands are listed. Read it at
the start of every run; to add, drop or change a brand, edit that file and
nothing else.

**Check every entry against every brand.** Each Trending-now entry
(platform slots included), each Calendar row and the "Beyond 30 days" note
gets checked against each brand's `fits` and `never`. Where a brand has an
honest fit, write its line. Most entries end up with none to three brands.
An entry with no fit gets no block — never stretch a brand to fill it, and
never give every brand a line just because it's on the roster.

**A brand line meets the same standard as the Trendjack row**: the actual
caption or headline, then the format in a few words. The brand's product
is the punchline, or the brand speaks into the public reaction rather than
the news. If it needs a shoot or budget, it goes on a Calendar row, not a
trend. Where one line suits several brands (the three malls, say), write it
once and give the others "Same line, own storefront shot."

**Hard stops, on top of each brand's `never`:**

- Nothing on the No-go list gets a brand line, whatever the fit.
- No athlete names or photos, and no protected event marks (Asian Games,
  Olympics, F1, Grand Prix logos) in a brand line unless the brand holds
  those rights. Celebrate the moment, not the person.
- No facts about a brand — price, spec, offer, store hours, event date —
  unless they come from the brand's own page fetched that day. Log the page
  in the source ledger.
- AIA, AUFF and UOB: no rates, returns, cover or approvals in the line, and
  never post into loss, illness or money trouble.
- Ferrari and Rolls-Royce: restraint is the brand. Expect "none" on most
  days; never humour, memes or discounts.
- Maersk Air Cargo is B2B: LinkedIn-style lines only, never consumer memes.

**Brand watch.** If a trend or No-go item involves a roster brand, its
parent group or a named rival in a way the client would want to know about
(an incident, a recall, a complaint going viral), add a visible flag instead
of ideas: `⚠` plus one line on what the client team should know and whether
the brand should stay out. A flag is never collapsed.

**Brands' own moments.** Each run, search every brand's `watch_for` terms.
A brand event verified that day (a race date, a launch, a store opening)
goes into the Calendar as its own row, with that brand's line in its block.
Anything you couldn't confirm goes in the ledger's Unresolved list, not on
the page.

Markup — inside a trend's `<dl>`, just before `<dt>Source</dt>`:

```html
<dt>Our brands</dt><dd><details class="brand-fit"><summary>For our brands (2) <span class="chip">OSIM</span><span class="chip">HYROX</span></summary><ul class="brand-ideas">
  <li class="brand-idea"><span class="chip">OSIM</span><span>One chair shot: <em>"22.78 seconds of work. The recovery takes longer."</em></span></li>
  <li class="brand-idea"><span class="chip">HYROX</span><span><em>"Watched the 200m on repeat? Now do 8 × 1km."</em> One line, sign-up link.</span></li>
</ul></details></dd>
```

A flag uses the same row with `<p class="brand-flag"><span class="chip">BMW</span><span>⚠ …</span></p>`
in place of the `<details>`. On a Calendar row the `<details class="brand-fit">`
block goes straight after that row's `<ul class="cal-ideas">`; in "Beyond 30
days" it goes after the `<p>`. The count in `<summary>` is the number of
brands in the block. The CSS (`/* client brands */` in the style block) is
already in `index.html` — copy it forward like the rest of the tokens.

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

Every TikTok and Instagram link on the page — cards and Source lines —
opens in a new tab with `target="_blank" rel="noopener noreferrer"`.

The Instagram actor's `country` setting does not geolocate. Title the card
`Instagram · Explore feed (SG locale)` and say plainly in `What` whether any
post carries a Singapore creator, location or hashtag. If none does, the
trendjack is `<dd class="none">`. Never call that feed "trending in SG".

If an actor run fails, leave its markers empty and fall back to the evidence
ladder above for that slot.
