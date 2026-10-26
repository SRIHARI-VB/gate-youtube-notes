# Tests

- `python3 scripts/validate.py` - content schema, internal references, every published number recomputed, hygiene (no citation markers, no versioned filenames), shell files present.
- `node tests/visual-lessons.js` - loads each p5 sketch with stubbed p5 globals and draws every step at p = 0, 0.5 and 1, so reference errors and non-finite geometry fail loudly without a browser.

Browser checks performed for this run are recorded in `docs/RUN_REPORT.md`.
