# UI contract

The shell is protected. A content run must not change it.

## Frozen

- `src/styles/design-tokens.css` - colours, radii, shadows, spacing scale, type stack.
- The layout skeleton: sidebar (264px) + main column, sticky topbar, `.content` max width 1060px.
- Navigation labels and routes.
- Component classes: `.card`, `.notecard`, `.field`, `.badge`, `.q`, `.chip`, `.trap`, `.example`, `.empty`.

## Allowed

- New content in `content/`.
- New topics, PYQs, variations and checks, rendered through the existing components.
- New visual lessons under `visuals/`, reusing `lesson.css` and `lesson.js`.
- Factual text and count updates where a hardcoded number or playlist name in the shell has become untrue. These go
  in their own `chore(ui)` commit, never mixed with content, and never touch tokens, layout or routes.

## Known stale labels

The sidebar brand text and browser title still read "Combinatorics" while the site now serves two subjects. Renaming
the brand is a UI change and needs an explicit request; it is deliberately not folded into a content run.

## Regression check

`scripts/validate.py` verifies the shell files exist, that every card's `visual` path resolves, and that no generated
file carries citation markers or versioned filenames. `node tests/visual-lessons.js` draws every step of every p5
lesson with stubbed globals. Visual changes to tokens or layout require an explicit user request and a separate commit.

## Accessibility

- Every control is a real button; the search input is labelled; lessons respond to arrow keys and space.
- Captions in lessons are `aria-live="polite"`.
- `prefers-reduced-motion` slows lesson playback; dark mode follows the OS preference.
