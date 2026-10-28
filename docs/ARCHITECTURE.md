# Architecture

Static, dependency-light site: one HTML shell, two stylesheets, two scripts, JSON content.

## Why no framework

The content is small, the audience is one learner, and the deliverable must run by double-clicking `index.html`.
A hash-routed single page with generated data keeps the whole thing inspectable and portable.

## Two organising axes

Content is filed on exactly one axis per kind. Do not mix them.

| Content | Organised by | Path |
| --- | --- | --- |
| Playlists, video inventory, per-video analysis | channel -> playlist -> video | `content/playlists/<channel>/<playlist-id>/videos/<video-id>/` |
| Canonical revision cards | subject -> topic -> subtopic | `content/subjects/<subject>/<topic>/<subtopic>.json` |
| PYQs, formula sheet, syllabus | flat, referenced by id | `content/pyqs/`, `content/revision/`, `content/syllabus.json` |
| Coverage ledger (the cycle) | one file, one entry per syllabus topic | `content/coverage.json` |
| Topic source ledger (chosen and rejected sources) | subject -> topic | `content/subjects/<subject>/<topic>/sources.json` |

The channel axis keeps one instructor's material together. The subject axis keeps one concept in one place: if two
channels teach the same idea, both videos point at the same card and only `videoRefs` grows.

## Data flow

```
content/**/*.json  --scripts/build-index.py-->  src/data/content.js  --src/app/app.js-->  DOM
                                  |
                                  +--> content/index.json  (machine-readable content map)
```

`content/` is the source of truth. `src/data/content.js` is generated and must never be hand-edited.
`src/app/app.js` renders from `window.GATE_DATA`; it contains no content of its own.

`build-index.py` walks the tree recursively, so any number of subjects, topics, playlists and videos are picked up.
It emits `playlists` (an array, one entry per playlist, each with its own video ids) and keeps `playlist` as the
first playlist for the single-playlist fields the shell still reads. Each video record carries `playlist_id`,
`playlist_title` and `channel`, and each card carries its `subject`, `topic` and `path`.

## Routes

| Route | View |
| --- | --- |
| `#/` | dashboard, P1 topics, coverage summary |
| `#/topics` | all topics, filter by priority |
| `#/topic/<id>` | the full revision card, linked PYQs, teaching videos, prerequisites |
| `#/pyqs` | verified PYQs, filter by year |
| `#/playlist` | inventory of every processed playlist with per-video processing status |
| `#/visuals` | lesson index (lessons are standalone pages under `visuals/`) |
| `#/last-minute` | formula sheet |
| `#/search?q=` | search across topics and PYQs |

Routes, navigation labels and the layout skeleton are frozen. A new playlist adds content, not routes.

## Visual lessons

Each lesson is a standalone page: `index.html` + `sketch.js` (p5.js) or inline HTML, plus `lesson.json` metadata.
They share `visuals/lesson.css` and `visuals/lesson.js` (the step/playback harness). A lesson must also work as
static text: every lesson ships a static explanation, a misconception and a quick check outside the canvas.

Lessons for a subject live at `visuals/<subject>/<topic>/<subtopic>/`. A card points at its lesson through the
`visual` field, which is a path relative to `visuals/` (for example
`discrete-mathematics/propositional-logic/truth-tables`), and the shell builds `visuals/<visual>/index.html` from it.
Older lessons from before the subject axis keep their flat `visuals/<slug>/` paths; those paths are published and are
not renamed.

## Adding another playlist

1. Add `content/playlists/<channel-slug>/<playlist-id>/` with a `playlist.json` and one folder per video
   (`metadata.json`, `analysis.json`, `notes.md`).
2. Add or extend cards under `content/subjects/<subject>/<topic>/`. Search for an existing card on the same concept
   first and extend it instead of creating a near-duplicate.
3. Add verified PYQs under `content/pyqs/` and link them from the cards.
4. Rerun `python3 scripts/build-index.py` then `python3 scripts/validate.py`. Both must pass. No UI change is needed:
   the shell discovers everything from the generated data, and the inventory lists every playlist.
