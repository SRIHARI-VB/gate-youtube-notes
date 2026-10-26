# Run report

## Run 3 - first order logic playlist added

### Playlist

GO Classes for GATE CS, *First Order Logic - Complete Summary, All GATE PYQs & Practice Questions*
(`PLIPZ2_p3RNHidhFvyKH4U_VE1rFAyvG8U`), 8 videos, 14h 49m.

### Processing summary

| | |
| --- | --- |
| Videos discovered | 8 |
| Videos with complete captions | 1 |
| Videos with partial captions (opening only) | 6 |
| Videos with no retrievable caption text | 1 (`zdeKQ-nABtk`) |
| Videos inaccessible or removed | 0 |
| Videos skipped silently | 0 |

Captions were not retrievable through the YouTube caption API at all: the API reported an IP block and the player
API returned HTTP 403 for every player client tried. They were fetched instead through a page-fetch route that
truncates documents at about five thousand characters, so each long lecture yielded only its opening. The character
count actually read is recorded in every video's `transcript_status`. See `docs/PROCESSING_STATUS.md`.

### Content added

| Item | Added this run | Total in repository |
| --- | --- | --- |
| Revision cards | 10 | 37 |
| Verified PYQs | 9 | 36 |
| Question variations | 22 | 65 |
| Quick checks with answers | 10 | 37 |
| Visual lessons | 1 | 7 |
| Formula-sheet groups | 1 (8 formulas) | 12 (68 formulas) |
| Videos inventoried with status | 8 | 39 |
| Playlists | 1 | 3 |

New topic: **First Order Logic** (`first-order-logic`) under Discrete Mathematics, registered in
`content/syllabus.json` with its covering playlist. New PYQ years: 2003, 2004, 2013, 2016, 2018, 2020, 2023, 2025,
2026.

### Validation performed

- `python3 scripts/validate.py` - 11 checks passed, 0 failures, 8 warnings (all pre-existing: seven PYQs labelled
  `OFFICIAL_KEY` without an evidence line, and two combinatorics videos not referenced by any card).
- New check added to `scripts/validate.py`: `check_first_order()`. It recomputes every first-order claim published in
  the cards and in the quantifier lesson by exhaustive enumeration over domains of one, two and three elements -
  quantifier order and its one-way implication, quantifier negation, the four null-quantification laws and the arrow
  case that fails, the distribution laws in their valid directions only, the exactly-one and at-most-one patterns,
  the small-model argument for a three-existential prefix, the option verdicts of GATE 2003 Q.32, 2016 Set 2 Q.27,
  2020 Q.39, 2023 Q.16 and 2025 Set 1 Q.38, and the tautology-versus-validity distinction.
- `node tests/visual-lessons.js` - all six p5 sketches load and draw every step at three progress values, including
  the new `discrete-mathematics/first-order-logic/quantifier-order` lesson.
- Headless Chromium `--dump-dom` over the dashboard, topics, a new topic page, PYQs, playlist, last-minute and a
  search for "quantifier": every route renders, the Topics tab shows the new subject > topic > subtopic grouping,
  the playlist view lists three playlists, and the card breadcrumb reads
  `Topics / Discrete Mathematics > First Order Logic / <card>`.

### UI

No change. `src/styles/design-tokens.css`, the shell layout, the navigation labels, the routes and the component
classes are untouched; the new content renders through the existing components. The sidebar tree and the Topics tab
pick the new subject and topic up from the generated data with no code change.

### Limitations

1. **Lecture coverage is partial**, as in the earlier runs. Only the opening of each long lecture was readable, so
   later worked examples and any timestamped detail are absent rather than guessed. The topic structure is reliable:
   the instructor names the four question types of the series in the readable part of the PYQ lectures
   (translation, negation of quantifiers, nested quantifiers, validity and satisfiability).
2. **One video has no content at all.** `zdeKQ-nABtk` returned no caption text on any route tried. It is inventoried
   with status `NONE`, an empty concept list and a coverage note saying so, and its topic mapping is taken from its
   title alone.
3. **All nine new PYQs are `SOURCED`, not key-verified.** Each answer is confirmed against a named GATE Overflow
   question page with its accepted solution, not against the official answer key document. The 2004 question is
   additionally covered by a dedicated video in the playlist, which reaches the same answer.
4. **`content/coverage-map.json` was not updated.** It is produced by a separate mapping tool and is not read by the
   site; the ten new cards and the new playlist are therefore absent from it until that tool is run again.

## Run 2 - propositional logic playlist added, repository migrated

### Playlist

GO Classes for GATE CS, *Propositional Logic - Complete Summary, All GATE PYQs & Practice Questions*
(`PLIPZ2_p3RNHillKxh1_iFeZhy9MftHeWW`), 17 videos, 13h 12m.

### Processing summary

| | |
| --- | --- |
| Videos discovered | 17 |
| Videos with readable captions (complete) | 3 |
| Videos with readable captions (partial) | 14 |
| Videos with Devanagari (Hindi ASR) captions only | 4 |
| Videos inaccessible | 0 |
| Videos skipped | 0 |

Full captions were not retrievable for the long lectures: YouTube refuses caption requests from this build
environment's IP and the working fetch route truncates documents at about 5,000 characters. See
`docs/PROCESSING_STATUS.md`.

### Repository migration (completed first, as required)

- 15 combinatorics cards moved from `content/topics/` to
  `content/subjects/discrete-mathematics/combinatorics/`; `content/topics/` retired.
- The combinatorics playlist moved under the channel folder
  `content/playlists/go-classes-for-gate-cs/`.
- `scripts/build-index.py` and `scripts/validate.py` rewritten to walk the tree recursively, to carry every playlist
  (`playlists` array, `playlist` kept for the single-playlist fields the shell reads), and to validate the new layout.
- Both scripts pass on the migrated content before any new content was added.

### Learning materials created

| Item | Added this run | Total in repository |
| --- | --- | --- |
| Revision cards | 12 | 27 |
| Verified PYQs | 14 | 27 |
| Question variations | 24 | 43 |
| Quick checks with answers | 12 | 27 |
| Visual lessons | 2 | 6 |
| Formula-sheet groups | 6 | 11 (60 formulas) |
| Videos inventoried with status | 17 | 31 |

New PYQ years: 1991, 1992, 1998, 2002, 2003, 2004, 2007, 2015 (three papers), 2016, 2021, 2024.

### Validation performed

- `python3 scripts/validate.py` - 10 checks passed, 0 failures: card schema and slugs, PYQ fields and sources, video
  statuses, playlist manifests (video counts and duration totals), syllabus coverage, 56 recomputed numeric claims,
  every propositional equivalence/tautology/entailment count recomputed by exhaustive truth table, visual lesson
  metadata, hygiene.
- `node tests/visual-lessons.js` - all five p5 sketches (three existing, two new) load and draw every step at three
  progress values. The test now discovers lessons by walking `visuals/`.
- Headless Chromium `--dump-dom` over the dashboard, topics, a new topic page, PYQs, playlist, last-minute and
  visuals routes: every route rendered with the new data and no script error.

### UI

Design tokens, layout skeleton, navigation labels and routes are untouched. Three factual text/count updates were
made, in a separate `chore(ui)` commit, because the numbers and playlist names they printed were no longer true:
the topics-page count, the playlist-inventory lead (now names every processed playlist), the visuals index (now lists
the two new lessons) and the two static counts in `index.html`.

Still saying "Combinatorics": the sidebar brand text and the browser title in `index.html`, and the `document.title`
set in `src/app/app.js`. Renaming them is a UI change and was left for an explicit request.

### Limitations

1. **Lecture coverage is partial.** Only the opening minutes of the long lectures were readable. The topic structure
   is reliable because the instructor states it explicitly and the titles name the rest, but later worked examples
   and any timestamped detail are absent rather than guessed.
2. **Four videos have only Devanagari (Hindi ASR) captions.** They are marked as fragments-only; no formula is
   attributed to them, and two of the three GATE questions those videos cover (2006, 2015 Q28) are therefore not in
   the PYQ set.
3. **Nineteen of 27 PYQs are `SOURCED`, not key-verified.** Their answers are confirmed by a named published
   solution (mostly GATE Overflow question pages), not by opening the official key document. Only the GATE 2024
   Set 2 question is `OFFICIAL_KEY` from this run.
4. **Marks are recorded for one question only.** GATE Overflow does not display per-question marks and the older
   papers' key documents were not opened, so no marks were inferred.
5. **Question numbering** for 2003, 2004, 2007, 2015, 2016 and 2021 follows the numbering on GATE Overflow; the
   reference is recorded as printed there.
6. Two of the 14 new PYQs are filed under Digital Logic on GATE Overflow (2007 Q.48 on CNF, 2015 Set 1 Q.39 on
   functional completeness). Both are genuine GATE CSE questions on these topics and the label says so.
7. Visual lessons load p5.js and the site loads KaTeX from a CDN. Without internet the animations do not run (the
   page says so) and formulas fall back to readable monospace LaTeX.

### Git

Six commits were pushed to `main` on top of `3132647`:

| Commit | Content |
| --- | --- |
| `e54e76a`, `bd64551`, `a9c1ad8` | migration + new playlist content (one logical change, split into three API batches of 60/60/30 files) |
| `5b78945` | regenerated `src/data/content.js` and `content/index.json` |
| `38e7e94` | `chore(ui)` - factual text and count corrections |
| `c756f12` | docs |

**How it was pushed, and the one snag.** The GitHub App installation on this repository is read-only: `git push`
returns 403 ("Permission to deny to SRIHARI-VB") and the App token's Git Data API returns 403 "Resource not accessible
by integration". The GitHub OAuth connection does have write access, so the commits were created through the GitHub
API (`GITHUB_COMMIT_MULTIPLE_FILES`) instead of the git protocol. Nothing was force-pushed and no history was
rewritten.

Two consequences worth knowing:

1. The content commit appears three times in the log with the same message, because the API path commits in batches
   and each batch is its own commit. Squashing them would mean rewriting published history, so they are left as they
   are.
2. Because the API path recreates files rather than replaying the local commit objects, the local commit SHAs and the
   published ones differ. The published tree is what a fresh clone contains and it is verified below.

A fresh clone of `main` after the push: `python3 scripts/build-index.py` reproduces `src/data/content.js` byte for
byte (clean working tree), `python3 scripts/validate.py` reports 10 checks passed and 0 failures, and
`node tests/visual-lessons.js` draws every step of all five p5 lessons.

### Definition of done

Met for this playlist except where the limitations above apply: every video has an explicit processing status, every
card carries sources and a quick check, every PYQ carries a year, a question reference and a source URL, and no
question is presented as a previous-year question without one.
