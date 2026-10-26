# Architecture

Static, dependency-light site: one HTML shell, two stylesheets, two scripts, JSON content.

## Why no framework

The content is small, the audience is one learner, and the deliverable must run by double-clicking `index.html`.
A hash-routed single page with generated data keeps the whole thing inspectable and portable.

## Data flow

```
content/**/*.json  --scripts/build-index.py-->  src/data/content.js  --src/app/app.js-->  DOM
                                  |
                                  +--> content/index.json  (machine-readable content map)
```

`content/` is the source of truth. `src/data/content.js` is generated and must never be hand-edited.
`src/app/app.js` renders from `window.GATE_DATA`; it contains no content of its own.

## Routes

| Route | View |
| --- | --- |
| `#/` | dashboard, P1 topics, coverage summary |
| `#/topics` | all topics, filter by priority |
| `#/topic/<id>` | the full revision card, linked PYQs, teaching videos, prerequisites |
| `#/pyqs` | verified PYQs, filter by year |
| `#/playlist` | playlist inventory with per-video processing status |
| `#/visuals` | lesson index (lessons are standalone pages under `visuals/`) |
| `#/last-minute` | formula sheet |
| `#/search?q=` | search across topics and PYQs |

## Visual lessons

Each lesson is a standalone page: `index.html` + `sketch.js` (p5.js) or inline HTML, plus `lesson.json` metadata.
They share `visuals/lesson.css` and `visuals/lesson.js` (the step/playback harness). A lesson must also work as
static text: every lesson ships a static explanation, a misconception and a quick check outside the canvas.

## Extending to another playlist

Add `content/playlists/<playlist-id>/` with a `playlist.json` and per-video folders, add topics under
`content/topics/`, rerun the build. The shell discovers everything from the generated data; no UI change is needed.
