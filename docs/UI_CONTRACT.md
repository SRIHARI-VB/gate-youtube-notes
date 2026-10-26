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

## Collapsible folder tree (added on explicit request, 2026-10-26)

The sidebar and the Topics tab both show the content as folders: **subject > topic > subtopic**. Every level is
closed by default and the reader opens what they need; the open state is remembered in `localStorage` under
`gate-open-state-v1`, keyed `nav:s:<subject>`, `nav:t:<subject>/<topic>`, `topics:s:<subject>`, `topics:t:<subject>/<topic>`.

New classes, now part of the contract and safe to reuse:

- `.nav-tree`, `.nav-subject`, `.nav-topic`, `.nav-sub`, `.nav-label`, `.caret` — the sidebar tree.
- `.topic-group`, `.subtopic-group`, `.group-title`, `.group-count`, `.group-caret` — the Topics tab folders.
- `.search-group`, `.pyq-hit` — grouped search results, filtered by `#searchKindFilter` and `#searchSubjectFilter`.

Still frozen: design tokens, the sidebar width and layout skeleton, the existing route table, and the existing
component classes. Adding a class is allowed; restyling an existing one is not.

A priority filter that matches cards inside closed folders opens those folders, so a filter never hides its own results.

## Brand labels

The sidebar brand and browser title read "GATE CSE" rather than "Combinatorics", on the same explicit request, so the
shell no longer claims to be a single-subject site.

## Regression check

`scripts/validate.py` verifies the shell files exist, that every card's `visual` path resolves, and that no generated
file carries citation markers or versioned filenames. `node tests/visual-lessons.js` draws every step of every p5
lesson with stubbed globals. Visual changes to tokens or layout require an explicit user request and a separate commit.

## Accessibility

- Every control is a real button; the search input is labelled; lessons respond to arrow keys and space.
- Captions in lessons are `aria-live="polite"`.
- `prefers-reduced-motion` slows lesson playback; dark mode follows the OS preference.
