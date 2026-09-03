# SG Trend Wire

Daily Singapore social trend brief for the TMRW Tech social team. Static HTML, one file per day, deployable to Vercel or Cloudflare Pages with no build step.

## Layout

```
index.html              today's brief — served at the root
archive/index.html      browsable list of every past day, newest first
archive/YYYY-MM-DD.html one file per day, never edited after the day it's written
manifest.json           one entry per day; drives archive/index.html
build_archive.py        regenerates archive/index.html from manifest.json
```

## Daily update

Each morning the run:

1. researches and writes `archive/YYYY-MM-DD.html`
2. copies it to `index.html`
3. appends the day's entry to `manifest.json`
4. runs `python3 build_archive.py`
5. commits and pushes — Pages deploys on push

To add a day by hand, do the same five steps. `build_archive.py` has no dependencies beyond Python 3.

## Deploy

**Cloudflare Pages:** connect the repo, framework preset *None*, build command empty, output directory `/`.

**Vercel:** import the repo, framework *Other*, no build command, output directory `.`.

Both redeploy automatically on every push to `main`.

## Design

Single-file pages, no external assets except Google Fonts (Archivo, Source Serif 4, JetBrains Mono). Light and dark themes follow the viewer's system setting. Keep the token block at the top of each page's `<style>` unchanged between days so the archive stays visually consistent.

## Automated daily update (GitHub Actions)

`.github/workflows/daily-brief.yml` runs at 01:35 UTC (09:35 SGT), after the
Cowork task has published the day's brief. It calls no AI service — it fetches
the published page, folds it into the archive, and pushes.

**Setup (one time):**

1. Publish the brief somewhere the workflow can fetch anonymously, and copy that URL.
2. Repo → *Settings → Secrets and variables → Actions → Variables → New variable*
   Name `BRIEF_SOURCE_URL`, value that URL.
3. Repo → *Settings → Actions → General → Workflow permissions* →
   **Read and write permissions**.
4. Repo → *Actions* tab → *Daily SG Trend Brief* → **Run workflow** to test.

No API key and no personal access token: the push uses the `GITHUB_TOKEN` that
GitHub issues to each run automatically, scoped to this repo and expired when
the job ends.

**If the test run fails**, the log says why in one line. The usual cause is the
source URL requiring a login, so the fetcher receives a sign-in page instead of
the brief. Verify with `curl -s '<url>' | head -40` — you should see the brief's
markup, not an empty `<div id="root">`.

## Publishing status

The brief is researched and built in a Claude Cowork scheduled task, then
committed here. As of 2 September 2026 the automated push is **not** running:
Cowork cloud sessions cannot push to repositories outside their authorised set,
and Cowork exposes no way to authorise one.

- anthropics/claude-code#76248 — git proxy blocks all pushes (regression, July 2026)
- anthropics/claude-code#84581 — no repo picker; the suggested `add_repo` tool does not exist

Until that is fixed the daily brief is pushed by hand. `build_archive.py`
regenerates the archive index and calendars identically either way, so nothing
needs changing when automation resumes.
