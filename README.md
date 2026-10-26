# Combinatorics revision system (GATE CSE)

A revision system for one YouTube playlist: **GO Classes - Combinatorics: Complete Summary, All GATE PYQs, Revision & Practice Questions**.

Open `index.html` in a browser. No build step, no server, no dependencies to install (the page loads KaTeX from a CDN for maths; everything else is local).

## What is in here

- **15 revision topics** in short-card form: five-second idea, remember, tiny example, GATE angle, variations, trap alert, quick check with answer.
- **13 verified previous-year questions**, each with paper, question reference, answer, solution and a source link. Verified means the answer was checked against an official answer key or a named published solution - the label on each question says which.
- **4 visual lessons** (three p5.js, one HTML) with play/pause/step controls, a static explanation, a misconception and a quick check. The p5 lessons load the p5.js library from a CDN, so they need internet on first open; the static lesson below each canvas works regardless.
- **A last-minute formula sheet** grouped by the decision the formula belongs to.
- **Full playlist inventory**: all 14 videos with an explicit transcript and analysis status.

## Honest scope

The playlist is 25 hours of lecture. Auto-captions were retrievable only for the opening minutes of each video, so each video's analysis is marked PARTIAL and states exactly what was and was not read. Topic notes are therefore built from: the recoverable transcript segments, the topic structure the instructor names, and independent verification of every formula and number. Nothing was invented to fill a gap.

## Layout

```
content/            canonical JSON content (source of truth)
  topics/           one file per topic
  pyqs/             one file per verified PYQ
  playlists/        playlist manifest + per-video metadata, analysis, notes
  revision/         formula sheet
src/                site shell: styles, app, generated data
visuals/            p5.js and HTML lessons
scripts/            build-index.py, validate.py
schemas/            JSON schemas for the content types
docs/               architecture, content rules, source policy, UI contract, status
```

## Regenerating

```bash
python3 scripts/build-index.py   # content/*.json -> src/data/content.js
python3 scripts/validate.py      # checks content, references, maths, hygiene
```

`src/data/content.js` is generated. Edit `content/`, then rerun the two scripts.

## Progress tracking

"Mark as revised" is stored in the browser's `localStorage` under `gate-revision-progress-v1`. It never touches the content files.
