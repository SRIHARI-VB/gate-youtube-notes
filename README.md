# GATE CSE revision system

A revision system for GATE CSE YouTube playlists, in one repository and one website. Two playlists are processed so far, both from **GO Classes for GATE CS**:

- *Combinatorics - Complete Summary, All GATE PYQs, Revision & Practice Questions* (14 videos)
- *Propositional Logic - Complete Summary, All GATE PYQs & Practice Questions* (17 videos)

Open `index.html` in a browser. No build step, no server, no dependencies to install (the page loads KaTeX from a CDN for maths; everything else is local).

## What is in here

- **27 revision cards** in short-card form: five-second idea, remember, tiny example, GATE angle, variations, trap alert, quick check with answer. Cards are filed by subject, topic and subtopic, so a concept lives in one place however many videos taught it.
- **27 verified previous-year questions**, each with paper, question reference, answer, solution and a source link. Verified means the answer was checked against an official answer key or a named published solution - the label on each question says which (8 `OFFICIAL_KEY`, 19 `SOURCED`, none `UNVERIFIED`).
- **6 visual lessons** (five p5.js, one HTML) with play/pause/step controls, a static explanation, a misconception and a quick check. The p5 lessons load the p5.js library from a CDN, so they need internet on first open; the static lesson below each canvas works regardless.
- **A last-minute formula sheet**: 60 formulas in 11 groups, each grouped by the decision the formula belongs to.
- **Full playlist inventory**: all 31 videos with an explicit transcript and analysis status.

## Honest scope

The two playlists are about 38 hours of lecture. Auto-captions were retrievable for part of each video, not all of it: 3 videos have complete captions (short question videos), 28 are `PARTIAL`, and each one states exactly what was and was not read in its `coverage_note`. Topic cards are therefore built from the recoverable transcript segments, the topic structure the instructor names, and independent verification of every formula and number - every claim is recomputed by `scripts/validate.py`. Nothing was invented to fill a gap, and the two videos whose captions are Hindi speech-recognition in Devanagari are marked as such instead of being quoted.

## Layout

```
content/
  subjects/<subject>/<topic>/<subtopic>.json   revision cards (one concept, one file)
  playlists/<channel>/<playlist-id>/           playlist.json + videos/<video-id>/{metadata,analysis}.json + notes.md
  pyqs/                                        one file per verified PYQ
  revision/formulas.json                       last-minute sheet
  syllabus.json                                syllabus mapping, per subject and topic
src/                site shell: styles, app, generated data
visuals/            p5.js and HTML lessons (visuals/<subject>/<topic>/<subtopic>/)
scripts/            build-index.py, validate.py
schemas/            JSON schemas for the content types
docs/               architecture, content rules, source policy, UI contract, status, run report
```

## Regenerating

```bash
python3 scripts/build-index.py   # content/**/*.json -> src/data/content.js + content/index.json
python3 scripts/validate.py      # content, references, maths, hygiene
node tests/visual-lessons.js     # every p5 lesson draws every step
```

`src/data/content.js` and `content/index.json` are generated. Edit `content/`, then rerun the scripts.

## Progress tracking

"Mark as revised" is stored in the browser's `localStorage` under `gate-revision-progress-v1`. It never touches the content files.
