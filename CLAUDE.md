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
`This week` 90 · `Trending now` 560 · `No-go` 130 · `Calendar` 420.
Visible total has to land inside 1250 — count before committing and cut
the calendar whys first, never the ideas.

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
- visible word count 900–1250, counted after stripping tags, the
  `<!--CAL-->` block, the `#debug` section, the collapsed
  `<details class="more">` lists **and** every client-brand element
  (`<dt>Our brands</dt>`, `details.brand-fit`, `.brand-flag`) — keep a flag
  to one short line all the same;
- loading the page with no query and no hash shows four sections and no
  ledger; `?debug` and `#debug` each reveal it;
- every ledger row carries a status;
- both `index.html` and `archive/<today>.html` carry the ledger;
- every `.chip` on the page matches a `chip` in `brands.json`, and no
  brand line sits on an entry that is also on the No-go list;
- every Trendjack idea, Calendar idea and brand line ends with `award` or
  `viral`, or is a plain greeting under the festival rule;
- none of the banned shorthand from the sensitivity check appears anywhere
  on the page — grep for it;
- every Medium-risk line carries `⚠ review:`; no High-risk line is on the
  page, and each one dropped is in the ledger's Unresolved list;
- no more than two comment-prompt ideas on the whole page, and no line
  formula used twice.

## Creative standard

This replaces the scheduled prompt's "angle standard" wherever the two
disagree. It applies to every Trendjack idea, every Calendar idea and every
brand line. Never print any of it on the page.

**The bar** is work a creative director at Ogilvy, BBH, Wieden+Kennedy,
Droga5 or Mother would put their name to, or a post a Singaporean would
screenshot and send to a friend. Nothing in between. Each idea aims at one
of two things and says which, in a one-word tag at the end of the line:

- `award` — built on a real insight (a truth the audience recognises but
  hasn't seen said), one single-minded idea, and craft in the line. The
  kind of thing that holds up in a Cannes Lions, Spikes Asia or D&AD case
  film.
- `viral` — built on timing, a live format or sound, an emotional hook
  (surprise, relatability, humour that punches nowhere) or a share
  mechanic (a challenge, a remix, a reply the original poster would
  repost) that fits how the platform behaves this week.

**Five tests, all of them, before an idea goes on the page:**

1. *Insight* — can you say in one sentence what's true here that people
   haven't seen said? If not, it's a caption, not an idea.
2. *Single-minded* — one idea, one line, one image. If it needs a
   paragraph to explain, cut it.
3. *Screenshot* — would someone send it to a friend? Product descriptions,
   generic greetings and "did you know" posts fail unless the execution
   is genuinely sharp.
4. *Insider* — for anything touching a community, a festival or a group:
   would a member of that community proudly post it from their own
   account? If you're not sure, it fails.
5. *Front page* — if it ran beside today's headlines on the front of the
   Straits Times, would the brand regret it?

**Two reference moves, never to be printed or attributed:** the product is
the punchline (a furniture chain answering a stolen-bus-bench story with
one product shot and a line about buying a cheaper bench), and posting into
the reaction rather than the news (a bed retailer answering the singles who
felt left out of a parental-leave announcement). The second is the more
important: the story is rarely the trendjack — the second-day argument in
the comments is.

**Variety.** Ideas on one entry must differ in kind, and the page as a whole
may not lean on one mechanic: at most two comment-prompt ideas ("Comments
open", "Pick a side") on the whole page, and no line formula used twice.
The mechanic follows the brand and the moment. Product-as-punchline,
posting into the second-day reaction, a utility the moment creates, an
insider observation, a format or sound remix, a reply in the comments of
the original post, a collab, a stunt or an OOH-able idea (Calendar only), a
LinkedIn post for B2B — these are examples, not a menu, and the best idea
some days is one none of them describes. Think out of the box before
reaching for the familiar.

**Restraint is part of the standard.** "No clean trendjack" and "no fit for
our brands" are correct answers and beat a weak line every time. A festival
or observance whose honest answer is a plain, correct greeting gets exactly
that, tagged neither `award` nor `viral`.

## Sensitivity and risk — mandatory on every idea

Run every Trendjack idea, Calendar idea and brand line through all of these
before it goes on the page. This is the check that was missing when a
Deepavali row shipped with "restock before the aunties clear the shelf" and
a "Little India, the week before" photo essay — both offensive, both
avoidable.

- **Race, ethnicity, religion** — no stereotypes, caricature or
  appropriation. Banned outright: "aunties", "uncles" or any relative-word
  used as shorthand for an ethnic community; accents or Singlish put in a
  community's mouth; a festival reduced to its food, lights or clothes;
  religious objects (diya, kolam, ketupat, lanterns, crosses, prayer
  items) as product props; photo essays of Little India, Geylang Serai,
  Chinatown or any enclave as a backdrop; "our version of [festival
  food]"; "restock before [group] clears the shelf" and its relatives.
- **Gender, sexuality, identity** — no assumptions about who does what at
  home, no tokenising, nothing that mocks or excludes.
- **Disability and health** — illness, disability, mental health, haze
  symptoms and injury are never punchlines or props. Haze lines are about
  comfort, never breathing.
- **Nationality and politics** — nothing on active political disputes,
  government policy, ministerial pay, foreign workers, naturalisation, or
  bilateral matters (Malaysia, Indonesia, the source of the haze). OB
  markers stay untouched.
- **Tragedy and timing** — check each line against today's No-go list and
  feeds. A line that's fine on a quiet day is tone-deaf beside a death;
  drop it and say so in the ledger.
- **Multicultural fairness** — a line written like a tourist's or a
  commentator's fails. For CMIO festivals the brand speaks as a
  participant (only if it genuinely is one), as a respectful guest (a
  greeting, a gift, a utility for hosts and guests), or not at all.
- **Legal and regulatory** — flag anything needing compliance review: MAS
  rules for AIA, AUFF and UOB; the ASAS code; health or wellness claims
  (OSIM, AIA); alcohol; PDPA; protected marks.

**Rate every idea Low, Medium or High.**

- *Low* — ships as is, no annotation.
- *Medium* — ships with `⚠ review:` plus one clause on what a human must
  check, appended to the line. It is not ready-to-run until cleared.
- *High* — never on the page. Log it in the ledger's Unresolved list with
  one line on why it was dropped, so the team sees the thinking.

## Festivals and community moments

Deepavali, Hari Raya Puasa and Haji, Vesak, Chinese New Year, Thaipusam,
Pongal, Good Friday, Christmas, Mid-Autumn and the like:

- The default is a greeting that is correct — spelling, language, date,
  form — and nothing else. It is the floor and, for most brands, the
  ceiling.
- Anything beyond it must pass the insider test and be about a practice
  the community would recognise as accurately and warmly observed — never
  about the community itself.
- Utility ideas (extended hours, parking, a delivery cut-off, open-house
  supplies) are the strongest honest move for a brand outside the
  community, and every fact in them comes from the brand's own page
  fetched that day.
- No casting, "no models", "shot in [enclave]" or "the week before" shoot
  directions on the page.
- Rolls-Royce's "ceremony" means one restrained image and a greeting, not
  a product-as-festival analogy.

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

**A brand line meets the creative standard below and passes the sensitivity
check below** — the same bar as the Trendjack row. Format: the actual
caption or headline in `<em>`, then platform and format in a few words,
then one clause on why it works, then the aim tag (`award` or `viral`).
Under 35 words. If it needs a shoot or budget, it goes on a Calendar row,
not a trend. Where one line suits several brands (the three malls, say),
write it once and give the others "Same line, own storefront shot."

The roster may carry three optional keys per brand — `tone`, `platforms`,
`objective`. Use them when filled. When empty, default platforms to
Instagram and TikTok for consumer brands and LinkedIn for Maersk Air Cargo,
use the category's obvious register, and say nothing about it on the page.

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
