# Routine prompt — TMRW Tech Daily Singapore Social Trend Brief

This is the stored prompt for the Claude routine. Paste everything below the
rule into the routine. `CLAUDE.md` in the repo carries the detail; where the
two disagree, `CLAUDE.md` wins.

---

Produce the **TMRW Tech Daily Singapore Social Trend Brief** for the social
media team. Market: **Singapore only**. This runs unattended — make reasonable
calls and state them in the ledger rather than asking questions.

## 0. SETUP

Run `date` in bash first and establish today's date in SGT (UTC+8).

Work inside the repository this session already has access to:
`joshuaTMRWsg/trendgenerator-sg-test`

If the working directory isn't this repo, or the expected files (`index.html`,
`archive/`, `manifest.json`, `build_archive.py`, `brands.json`, `sources.json`,
`CLAUDE.md`) are missing, **stop and report the exact error**. Do not
reconstruct the page from memory, do not build a zip, do not work around it.

Read `CLAUDE.md` in full before anything else. It carries the creative
standard, the sensitivity check, the festival rule, the source mix, the
platform-card workflow and the client-brand rules. Where it is more detailed
than this prompt, follow `CLAUDE.md`.

## 1. RESEARCH

Verify everything against a source you fetched today. Never from memory, never
from yesterday's page. Cover: Google Trends SG, Mothership, CNA, Straits Times,
AsiaOne, r/singapore, TikTok/IG Reels SG (via the Apify actors in
`sources.json`), Marketing-Interactive.

Read `archive/` for the last 2–3 days first so you don't repeat a trend that
has already run, and so you can close out anything you flagged as unresolved.

Read `brands.json` (the client roster). For every brand, search its
`watch_for` terms today. Any brand event you verify today goes into the
Calendar as its own entry. Use each brand's `tone`, `platforms` and
`objective` where filled; where empty, use the defaults in `CLAUDE.md` and
don't mention it on the page.

If a source is dead or blocked, log it in the source ledger with its real
status. Never invent a trend, a date or an engagement figure — an honest gap
is more useful than a confident guess.

## 2. THE PAGE — FOUR VISIBLE SECTIONS + HIDDEN SOURCE LEDGER

A morning scan with real depth on every entry: 1400–2000 visible words (see
`CLAUDE.md` for what counts). Match the existing pages exactly: same fonts, same CSS token
block (including the client-brands CSS), both theme blocks,
`<nav class="nav">`, and the `<!--CAL--><!--/CAL-->` markers after the
counters strip. Copy the structure from the existing `index.html` — do not
invent a new design.

**1. This week** — three lines: act today / start building / avoid.

**2. Trending now** — six to seven entries: 2 TikTok, 2 Instagram, 2–3 news,
per `CLAUDE.md`. Each a `<dl>` with rows in this order:
- **What** — one sentence. Genuinely one.
- **Trendjack** — **3–5 numbered ideas** via `.cal-ideas` / `.cal-idea`
  inside `<dd class="angle">`, each a different mechanic, each opening with
  its mechanic in two or three words (*Product punchline:*, *Into the
  reaction:*, *Utility:*, *Format remix:*, *Reply in the comments:* …). An
  idea is the actual headline, caption or format a brand would post, and it
  ends with its aim tag: `award` or `viral`. Where there is no honest
  trendjack, say so in `<dd class="none">` with one line explaining why —
  none means none, not one weak idea. Policy stories, ongoing tragedies and pure industry news
  usually have none. **Never invent an opportunity to fill the slot.**
- **Risk** — only when flagged. ⚠ DO NOT TOUCH or ⚠ HANDLE CAREFULLY plus one
  clause.
- **Our brands** — check the entry against every brand in `brands.json` and
  follow the "Client brands" rules in `CLAUDE.md`. Lines only where a brand
  genuinely fits; most entries get none to three; never force one. If the
  trend is bad news for a roster brand, show a visible ⚠ brand flag instead
  of ideas.
- **Source** — the link.
Heat chip on each: Peaking / Rising / Cooling.

**3. No-go list** — trending but untouchable. Tragedy, active court cases,
race/religion, politics, anything near SG's OB markers. One line each. No
brand lines on anything in this list.

**4. Calendar** — ~12 entries by date with days-away counts. ★★★ major · ★★
worth a post · ★ only if it fits. ⏰ Lead time on anything needing more than
a week. Include SG public holidays and world observance days where they fall.
Every entry: one line on why it matters in SG (`.cal-why`), then numbered
post ideas — **3–5 on every ★★★ and ★★ row**, 1–2 on a ★ row. An idea is
an actual headline, caption or format a designer could brief from, tagged
`award` or `viral`, and no two ideas on a row share a mechanic — not just
"one with product, one without": a different mechanic, a different platform,
a different emotional register, each named in its two-word lead. Then the **Our brands** block for that entry,
same rules as above. The "Beyond 30 days" note gets a brand block too where
one fits. Religious and cultural festivals follow the festival rule in
`CLAUDE.md`: a correct greeting is the floor and often the ceiling.

**5. Source ledger** — hidden unless `?debug` or `#debug`, per `CLAUDE.md`:
every source touched with URL and real status, then an Unresolved list. Every
High-risk idea you dropped goes in Unresolved with one line on why.

**Do not add any other section.** Never print the creative standard, the
sensitivity check, methodology notes, or anything explaining your own process.

## 3. THE CREATIVE STANDARD — FOR YOUR JUDGMENT ONLY, NEVER PRINTED

The full standard is in `CLAUDE.md` ("Creative standard", "Sensitivity and
risk", "Festivals and community moments"). The short version:

**The bar** is work a creative director at Ogilvy, BBH, Wieden+Kennedy,
Droga5 or Mother would sign, or a post a Singaporean would screenshot and
send to a friend. Every idea aims at one and says which: `award` (a real
insight, one single-minded idea, craft in the line — the kind that holds up
in a Cannes Lions, Spikes Asia or D&AD case film) or `viral` (timing, a live
format or sound, an emotional hook, a share mechanic that fits how the
platform behaves this week).

**Five tests, all of them:** Insight (what's true here that hasn't been
said?), Single-minded (one idea, one line, one image), Screenshot (would
someone send it to a friend?), Insider (would a member of that community
proudly post it from their own account?), Front page (would the brand regret
it beside today's headlines?).

**The story is rarely the trendjack — the second-day reaction to it is.**
Before writing an angle, ask who is arguing in the comments, who feels left
out, what the conversation actually is. That is where the post lives.

**Volume and variety.** 3–5 ideas on every entry that has a trendjack and
on every ★★★/★★ Calendar row, each a different mechanism, each opening
with its mechanic named. Fewer than three means you haven't looked hard
enough, or the honest answer is none. The page never leans on one
mechanic: at most two comment-prompt ideas on the whole page, no line
formula used twice. The mechanic follows the brand and the moment; the
leads in `CLAUDE.md` are examples, not a menu. Think out of the box before
reaching for the familiar.

**Sensitivity check on every idea, no exceptions:** race, ethnicity and
religion; gender and identity; disability and health; nationality and
politics; tragedy and timing; multicultural fairness; legal and regulatory.
The banned shorthand in `CLAUDE.md` (relative-words as ethnic shorthand,
festivals reduced to food or lights, religious objects as props, enclaves as
backdrops, "restock before [group] clears the shelf") never appears. Rate
every idea Low / Medium / High: Low ships; Medium ships with `⚠ review:` and
one clause on what to check; High never reaches the page and is logged in
Unresolved.

**Restraint is part of the standard.** "No clean trendjack" and "no fit for
our brands" are correct answers and beat a weak line. Never name the
reference examples or agencies in the brief, and never print these rules.

## 4. BUILD

1. Write today's brief as a complete standalone HTML document
   (`<!doctype html>`, full head and body).
2. Save as `archive/<YYYY-MM-DD>.html` **and** as `index.html`.
3. Run the platform-card script per `CLAUDE.md` to stamp the TikTok and
   Instagram cards.
4. Append to `manifest.json`: `date`, `compiled`, `headline` (the "act today"
   line), `trends`, `nogo`, `calendar`, `file`. Newest first, one entry per
   date — replace the entry if today's date is already present.
5. Run `python3 build_archive.py`.
6. Verify before committing — the full list is in `CLAUDE.md`
   ("Verification, amended"); in short: four visible `<h2>` plus the hidden
   ledger; visible word count 1400–2000; 3–5 ideas on every entry and ★★★/★★
   row; no horizontal scroll at 390px; every
   source link resolves and every ledger row has a status; all day-counts
   match today; every `.chip` matches `brands.json`; no brand line on a No-go
   item; every idea tagged; no banned shorthand; every Medium line flagged;
   no High line on the page; at most two comment prompts.

## 5. COMMIT, PUSH, MERGE

`git add -A && git commit -m "Brief for <YYYY-MM-DD>" && git push origin HEAD`

If the push fails, report the exact error and stop. Then open a pull request
from the branch into `main` and merge it immediately — do not leave it for
manual review. Confirm with `git fetch origin main && git log origin/main -1
--oneline` and report the merge commit SHA.

## 6. IF AVAILABLE

If an Artifact tool is present, also update the live page at
`https://claude.ai/code/artifact/3eb3a7ff-207a-48f4-925e-ae6a316bceaa` — read
it with `action: "read"` first, publish with the same `url`, no `favicon`,
keep `<title>` as "SG Trend Wire". If the tool is not present, skip silently.

If a notification tool is present, send the brief in plain text with the most
useful line of the day first, followed by any brand flags (⚠), any `⚠ review`
lines a human needs to clear, and the day's best brand fits. If not, skip.

## 7. REPLY

Three lines maximum: what led the brief, merge commit SHA, page status.
