# Components

Components are CSS classes plus small render helpers inside `src/app/app.js`:

- `AppShell` - sidebar + topbar + content column (in `index.html`)
- `RevisionCard` - `.card .notecard` with `.field` rows
- `QuickCheck` - `<details>` inside `.q`
- `PyqCard` - `.q` with `.q-meta`, `.options`, `.verify-note`
- `TopicRow`, `StatCard`, `Chip` - list and filter primitives

Do not add a second visual language; extend these.
