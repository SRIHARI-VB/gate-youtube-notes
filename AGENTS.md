# Instructions for an agent working in this repository

This repository is a GATE CSE revision system generated from YouTube playlists. One repository, one website shell,
many playlists. Read `docs/ARCHITECTURE.md`, `docs/CONTENT_RULES.md`, `docs/SOURCE_POLICY.md` and
`docs/UI_CONTRACT.md` before changing anything.

## Hard rules

1. **Never invent** a GATE year, question number, official answer, marks, timestamp or transcript line. If you cannot
   check it, label it `UNVERIFIED` and do not present it as a previous-year question.
2. **Never present a generated question as a PYQ.** Variation labels are fixed: `VERIFIED PYQ`,
   `ORIGINAL PYQ-STYLE QUESTION`, `CONCEPTUAL PRACTICE QUESTION`, `PREDICTED VARIATION`.
3. **Mathematics before brevity.** Any numeric or logical claim you add must be recomputed. Add it to `MATH` or to
   `check_logic()` in `scripts/validate.py` so it stays checked.
4. **Do not restyle the site.** New content uses the existing components and design tokens. Changing
   `src/styles/design-tokens.css`, the shell layout, the navigation labels or the routes is out of scope for a content
   run.
5. **Do not delete unrelated files, reset the tree, force-push or rewrite history.** Do not commit secrets.
6. **State partial coverage honestly.** A video whose transcript was only partly readable keeps its `PARTIAL` status
   and coverage note.
7. **One concept, one card, one path.** File playlist material by channel -> playlist -> video and revision cards by
   subject -> topic -> subtopic. Extend an existing card instead of adding a near-duplicate, and never rename a
   published slug or id.

## Workflow

- Add or edit content under `content/` only.
- Run `python3 scripts/build-index.py` then `python3 scripts/validate.py`. Both must pass.
- Run `node tests/visual-lessons.js` after touching a lesson.
- Keep `content/index.json` and `src/data/content.js` generated, never hand-edited.
- Commits, when authorised, are small and scoped: `feat(content): ...`, `fix(content): ...`, `chore(index): ...`,
  `chore(ui): ...`.
