# Run report

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

Four commits were created on top of `3132647`: the content and migration commit, a `chore(ui)` commit, a `docs`
commit and a commit adding the two lessons plus the regenerated content index.

**Pushing to `main` was blocked.** The GitHub App installation on this repository is read-only: `git push` returns
403 ("Permission to deny to SRIHARI-VB") and the Git Data API returns 403 "Resource not accessible by integration".
Nothing was force-pushed and no history was rewritten. Until write access is granted, the changes are supplied as
`gate-youtube-notes-propositional-logic.patch` (apply with `git am --3way` on a clone of `main`; verified to apply
cleanly and to pass both checks on a fresh clone).

### Definition of done

Met for this playlist except where the limitations above apply: every video has an explicit processing status, every
card carries sources and a quick check, every PYQ carries a year, a question reference and a source URL, and no
question is presented as a previous-year question without one.
