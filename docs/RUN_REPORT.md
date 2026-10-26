# Run report - combinatorics playlist

## Playlist

GO Classes for GATE CS, *Combinatorics - Complete Summary, All GATE PYQs, Revision & Practice Questions*.
14 videos, about 25 hours, `PLIPZ2_p3RNHjlC6eceG_vWSu-oA6Dc6aX`.

## Processing summary

| | |
| --- | --- |
| Videos discovered | 14 |
| Videos with a readable transcript segment | 14 (opening minutes only) |
| Videos fully analysed | 0 |
| Videos analysed in part | 14 |
| Videos inaccessible | 0 |
| Videos skipped | 0 |

Full captions were not retrievable: YouTube refused direct caption requests from the build environment and the one
working transcript service returns a length-capped slice of each track. See `docs/PROCESSING_STATUS.md`.

## Learning materials created

| Item | Count |
| --- | --- |
| Canonical topics | 15 |
| Verified PYQs | 13 (7 `OFFICIAL_KEY`, 6 `SOURCED`) |
| Original variations and practice questions | 19 (12 original PYQ-style, 4 predicted, 3 conceptual) |
| Quick checks with answers | 15 (one per topic) plus 4 inside lessons |
| Visual lessons | 4 (3 p5.js, 1 HTML decision aid) |
| Videos inventoried with status | 14 |

## Validation performed

- `python3 scripts/validate.py` - 6 checks passed, 0 failures: schema fields, priorities, variation labels,
  PYQ required fields and years, video statuses, 51 recomputed numeric claims, internal reference integrity,
  hygiene.
- `node tests/visual-lessons.js` - all three p5 sketches load and draw every step at three progress values.
- Headless Chromium (`--dump-dom`) against `index.html` for every route: dashboard, topics, two topic pages, PYQs,
  playlist, last-minute sheet, visuals index and search. All rendered the expected view with 13 PYQ cards on the PYQ
  page and 25 formulas on the last-minute sheet.
- One screenshot review of the dashboard and of a lesson page for layout sanity.

## Limitations

1. **Lecture coverage is partial.** Only the opening minutes of each lecture were readable. The topic structure is
   reliable because the instructor states it explicitly, but later worked examples and any timestamped detail are
   absent rather than guessed.
2. **Six PYQ answers are `SOURCED`, not key-verified** (GATE 1999 Q.1.3, 2000 cards, 2001 Q.2.1, 2003 Q.34,
   2004 IT Q.2, 2015 Set 3 Q.5): the answer is confirmed by a named published solution, but the official key document
   itself was not opened. The other seven carry `OFFICIAL_KEY`.
3. **Question numbering differs between repositories** for a few papers (2021 Set 2, 2022, 2025 Set 1). Both numbers
   are recorded in the `question_ref` field.
4. **One topic is a playlist gap**: recurrences and compositions are in the GATE syllabus and appear in a verified
   PYQ (2014 Set 1 Q.49) but this playlist does not teach them; the note says so.
5. **No git commit was made.** The repository is prepared and git-ready, but committing or pushing requires the
   user's authorisation.
6. Visual lessons load p5.js and the site loads KaTeX from a CDN. Without internet the animations do not run (the
   page says so) and formulas fall back to readable monospace LaTeX.
