# Run report

## Run 4 - sets, relations, functions; the syllabus cycle and the ledger start here

### The topic, and why it was next

**Discrete Mathematics > Sets, Relations, Functions** (`sets-relations-functions`), the third topic of the
GATE 2027 Discrete Mathematics line: *"Propositional and first order logic. Sets, relations, functions,
partial orders and lattices. Monoids, Groups. ..."*

This run began by doing what `references/topic-queue.md` asks of the first run: it enumerated the whole
official GATE 2027 CS syllabus (13 subjects, 74 topics, in official order, cited to the IIT Madras GATE 2027
CS syllabus document) into `content/syllabus.json`, and seeded `content/coverage.json` as the ledger. Until
that existed the cycle had nothing to walk over.

The ledger was seeded so that the cycle continues rather than restarting:

- `combinatorics`, `propositional-logic` and `first-order-logic` are `partial` - each was built from a single
  GO Classes playlist in runs 1 to 3, and none has been re-audited against the 2027 line.
- `cycle.last` was set to `discrete-mathematics/first-order-logic`, the last topic the repository actually
  covers (run 3).
- The next topic after that pointer, in official order, whose status is not `covered`, is
  **sets-relations-functions**. First order logic sits second in the enumeration because the GATE 2027 line
  reads "Propositional and first order logic", where earlier wording named propositional logic only.

**Skipped, and why.** The three `partial` topics were skipped because the cycle takes a second pass over
partial topics only after a full pass finds no `not_started` topic left; nothing was `blocked`. No topic was
skipped silently.

### Subtopics enumerated before any source was chosen

Sets: sets, elements, subsets, cardinality and the empty set; power sets and counting subsets; set operations,
De Morgan, distributive laws and element-chasing proofs; ordered pairs and the Cartesian product; countable and
uncountable sets. Relations: definition, matrix and digraph representation, counting; reflexive, symmetric,
antisymmetric and asymmetric relations and their counts; transitivity, transitive closure and Warshall;
equivalence relations, classes and partitions. Functions: total, injective, surjective and bijective functions
and their counts; composition and inverse functions. Eleven subtopics, one card each.

### Sources chosen, on merit

| Source | Channel | Language | Transcript | What it carries |
| --- | --- | --- | --- | --- |
| Lec 02 - Set identities, Cartesian product, relations and functions (`7djvJetFiSY`) | IIT lecture (NPTEL-style) | English | FULL | Set identities by element chasing, ordered pairs and the ZF construction of the product, the relation definition, all four relation properties, equivalence relations |
| Introduction to Set Theory (`tyDKR4FG3Yw`) | TrevTutor | English | FULL | Elements, cardinality, the empty set versus the set containing it, set-builder notation |
| Injective, Surjective and Bijective Functions (`PpA4LWPh40M`) | TrevTutor | English | FULL | The three function properties, the cardinality conditions, why an inverse needs a bijection |
| Relations - GATE PYQs - Part 2 (`Z9khyLCt2-I`) | GO Classes for GATE CS | English | PARTIAL (opening) | The 2^(n^2) count and the ternary-relation variation; the question types of the GATE series |

**Chosen and rejected, with reasons** are recorded in
`content/subjects/discrete-mathematics/sets-relations-functions/sources.json`: five rejected candidates,
including the 460-video NPTEL IIT Ropar playlist (every concept split into three-to-five minute fragments, so
no video covers a subtopic), the NPTEL IIT Kanpur *Set Theory and Mathematical Logic* course (ZFC, ordinals,
ultrafilters - mostly outside the GATE line), the Stanford CS103 set-theory slides (no video or transcript),
and two Hindi-language candidates searched for deliberately (no readable transcript, so nothing could be
verified or translated).

### Content added

| Item | Added this run | Total in repository |
| --- | --- | --- |
| Revision cards | 11 | 48 |
| Verified PYQs | 7 | 43 |
| Question variations | 33 (8 VERIFIED PYQ, 11 ORIGINAL PYQ-STYLE, 6 CONCEPTUAL PRACTICE, 8 PREDICTED VARIATION) | 98 |
| Quick checks with answers | 11 | 48 |
| Traps with counterexamples | 11 | 48 |
| Visual lessons | 1 (`sets-relations-functions/relation-matrix-properties`, 6 steps) | 8 |
| Topic source ledgers | 1 | 1 |

The seven PYQs are GATE CS 1995 Q.1.20 (power set of a nested set), 2015 Set 2 Q.18 (power-set cardinality),
1993 Q.8.4 (power set of A x A), 2015 Set 3 Q.41 (a relation that is symmetric but not reflexive), 2016 Set 2
Q.26 (a relation that is reflexive but not transitive), 1997 Q.6.3 (equivalence relations on four elements) and
2015 Set 2 Q.40 (onto functions from four elements to three). Each carries a year, a question reference, a
source URL and an `answer_evidence` line; all seven are `SOURCED` against the named GATE Overflow page with its
accepted answer, not against an official key document.

### The visual lesson

`visuals/discrete-mathematics/sets-relations-functions/relation-matrix-properties/` shows one 3 by 3 grid of
ordered pairs and reads five properties off it: the 2^9 total, reflexive as a full diagonal (2^6), symmetric as
mirror pairs that agree (2^6), antisymmetric as mirror pairs that never both appear (2^3 x 3^3), transitivity as
the missing shortcut (1,3) with its closure, and equivalence relations as blocks on the diagonal.

### Validation performed

- `python3 scripts/validate.py` - 14 checks passed, 0 failures, 8 warnings, all eight pre-existing (seven PYQs
  labelled `OFFICIAL_KEY` without an evidence line, two combinatorics videos not referenced by any card).
- Two new checks and one extended check in `scripts/validate.py`:
  - `check_sets_relations_functions()` enumerates all 512 relations on a 3-element set (and all on 1 and 2
    elements) and tallies reflexive, irreflexive, symmetric, antisymmetric, asymmetric, reflexive-and-symmetric,
    symmetric-and-antisymmetric, neither-reflexive-nor-irreflexive and equivalence relations, checking each
    against its closed formula; it also recomputes Bell and Stirling numbers, brute-forces the function counts
    (81 total, 36 onto, 0 injective for 4 to 3; 360 injective for 4 to 6; 21 neither for 3 to 3), the transitive
    closures used in the cards, the union-of-equivalence-relations counterexample, and the verdicts of the four
    relations-based PYQs by direct computation over small ranges.
  - `check_coverage()` holds the ledger to the syllabus: every enumerated topic appears exactly once, statuses
    are legal, a `partial` topic names its gaps, a `covered` topic names none, a topic with cards is never
    `not_started`, a topic claiming material has a card, and `cycle.last` points at a real topic that is not
    `not_started`.
  - `check_sources()` requires each topic ledger to record chosen sources with language and transcript status,
    rejected candidates with reasons, and no source both chosen and rejected.
  - `check_syllabus()` now accepts enumerated topics that have no cards yet (`material: planned`) and requires a
    folder for every topic marked `material: cards`, and requires the syllabus document to be cited.
- `python3 scripts/build-index.py` regenerates `content/index.json` and `src/data/content.js`: 48 topics, 43
  PYQs, 3 playlists, 39 videos.
- `node tests/visual-lessons.js` - all seven p5 sketches load and draw every step at three progress values,
  including the new six-step lesson.

### UI

No change to design tokens, shell layout, navigation labels, routes or component classes. The new cards render
through the existing components; the sidebar tree and the Topics tab pick up the new topic, its three units
(Sets, Relations, Functions) and its eleven subtopics from the generated data with no code change. Two scripts
learned to ignore `sources.json`, which is a content file at card depth, not a card.

### Limitations

1. **The GO Classes lecture used for GATE question patterns is only partly readable.** Its opening gives the
   2^(n^2) count and the ternary-relation variation; the later question types are past the truncation point and
   are not recorded.
2. **Countability has no lecture behind it.** No transcript on countable and uncountable sets was readable, so
   that card rests on Rosen and Grimaldi alone and is flagged in the card's source line and in the ledger's gaps.
3. **Closures rest on the standard reference.** Transitive closure and Warshall are taught from Rosen ch. 9.4;
   no lecture transcript for closures was readable.
4. **No verified PYQ exists in this topic for countability.** GATE tests countability inside Theory of
   Computation (for example GATE CS 2019 Q.34 on recursively enumerable languages), which belongs to that topic,
   so nothing was borrowed into this one.
5. **No playlist manifest was added for the GO Classes Set Theory playlist.** Its full video list could not be
   enumerated and verified, so inventing a `video_count` for it would have been a false statement. The four
   videos used are recorded in the topic's `sources.json` and on each card's `sourceLine` instead.
6. **All seven PYQs are `SOURCED`, not key-verified.** Answers come from the accepted answer on the named GATE
   Overflow page. Question numbering follows GATE Overflow.

### Generated data

`content/index.json` and `src/data/content.js` carry all eleven cards with their subject, topic and unit, and
every one of them resolves to a syllabus name: the breadcrumb reads `Discrete Mathematics > Sets, Relations,
Functions / Sets` (and `... / Relations`, `... / Functions` for the other units), which is what the shell
renders. The syllabus data now holds 13 subjects and 74 topics, and all seven new PYQs are linked from cards.

### Git

Five commits on `main`:

| Commit | Content |
| --- | --- |
| `073ad6c` | `feat(content)` - 11 cards, 7 PYQs, the topic source ledger and the p5 lesson |
| `b6c36a2` | `feat(content)` - the GATE 2027 syllabus enumeration and the seeded coverage ledger |
| `4399beb` | `fix(scripts)` - coverage, source-ledger and syllabus-material validation; `sources.json` skipped when indexing |
| `afa5802` | `chore(index)` - regenerated `content/index.json` and `src/data/content.js` |
| `b0e6271` | `docs` - run report, processing status, layout notes |

**How it was published, and the snag.** The GitHub App installation on this repository is read-only: `git push`
returns 403 ("Permission to deny to SRIHARI-VB"), and the App token's Git Data API returns 403 "Resource not
accessible by integration" for blobs as well. The commits were therefore created through the GitHub API on the
OAuth connection. Nothing was force-pushed, no history was rewritten and no unrelated file was deleted.

A fresh clone of `main` after the push reproduces the tree exactly: `python3 scripts/build-index.py` leaves the
working tree clean, `python3 scripts/validate.py` reports 14 checks passed and 0 failures, and
`node tests/visual-lessons.js` draws every step of all seven p5 lessons.

## Run 3 - first order logic playlist added

### Playlist

GO Classes for GATE CS, *First Order Logic - Complete Summary, All GATE PYQs & Practice Questions*
(`PLIPZ2_p3RNHidhFvyKH4U_VE1rFAyvG8U`), 8 videos, 14h 49m.

### Processing summary

| | |
| --- | --- |
| Videos discovered | 8 |
| Videos with complete captions | 1 |
| Videos with partial captions (opening only) | 6 |
| Videos with no retrievable caption text | 1 (`zdeKQ-nABtk`) |
| Videos inaccessible or removed | 0 |
| Videos skipped silently | 0 |

Captions were not retrievable through the YouTube caption API at all: the API reported an IP block and the player
API returned HTTP 403 for every player client tried. They were fetched instead through a page-fetch route that
truncates documents at about five thousand characters, so each long lecture yielded only its opening. The character
count actually read is recorded in every video's `transcript_status`. See `docs/PROCESSING_STATUS.md`.

### Content added

| Item | Added this run | Total in repository |
| --- | --- | --- |
| Revision cards | 10 | 37 |
| Verified PYQs | 9 | 36 |
| Question variations | 22 | 65 |
| Quick checks with answers | 10 | 37 |
| Visual lessons | 1 | 7 |
| Formula-sheet groups | 1 (8 formulas) | 12 (68 formulas) |
| Videos inventoried with status | 8 | 39 |
| Playlists | 1 | 3 |

New topic: **First Order Logic** (`first-order-logic`) under Discrete Mathematics, registered in
`content/syllabus.json` with its covering playlist. New PYQ years: 2003, 2004, 2013, 2016, 2018, 2020, 2023, 2025,
2026.

### Validation performed

- `python3 scripts/validate.py` - 11 checks passed, 0 failures, 8 warnings (all pre-existing: seven PYQs labelled
  `OFFICIAL_KEY` without an evidence line, and two combinatorics videos not referenced by any card).
- New check added to `scripts/validate.py`: `check_first_order()`. It recomputes every first-order claim published in
  the cards and in the quantifier lesson by exhaustive enumeration over domains of one, two and three elements -
  quantifier order and its one-way implication, quantifier negation, the four null-quantification laws and the arrow
  case that fails, the distribution laws in their valid directions only, the exactly-one and at-most-one patterns,
  the small-model argument for a three-existential prefix, the option verdicts of GATE 2003 Q.32, 2016 Set 2 Q.27,
  2020 Q.39, 2023 Q.16 and 2025 Set 1 Q.38, and the tautology-versus-validity distinction.
- `node tests/visual-lessons.js` - all six p5 sketches load and draw every step at three progress values, including
  the new `discrete-mathematics/first-order-logic/quantifier-order` lesson.
- Headless Chromium `--dump-dom` over the dashboard, topics, a new topic page, PYQs, playlist, last-minute and a
  search for "quantifier": every route renders, the Topics tab shows the new subject > topic > subtopic grouping,
  the playlist view lists three playlists, and the card breadcrumb reads
  `Topics / Discrete Mathematics > First Order Logic / <card>`.

### UI

No change. `src/styles/design-tokens.css`, the shell layout, the navigation labels, the routes and the component
classes are untouched; the new content renders through the existing components. The sidebar tree and the Topics tab
pick the new subject and topic up from the generated data with no code change.

### Limitations

1. **Lecture coverage is partial**, as in the earlier runs. Only the opening of each long lecture was readable, so
   later worked examples and any timestamped detail are absent rather than guessed. The topic structure is reliable:
   the instructor names the four question types of the series in the readable part of the PYQ lectures
   (translation, negation of quantifiers, nested quantifiers, validity and satisfiability).
2. **One video has no content at all.** `zdeKQ-nABtk` returned no caption text on any route tried. It is inventoried
   with status `NONE`, an empty concept list and a coverage note saying so, and its topic mapping is taken from its
   title alone.
3. **All nine new PYQs are `SOURCED`, not key-verified.** Each answer is confirmed against a named GATE Overflow
   question page with its accepted solution, not against the official answer key document. The 2004 question is
   additionally covered by a dedicated video in the playlist, which reaches the same answer.
4. **`content/coverage-map.json` was not updated.** It is produced by a separate mapping tool and is not read by the
   site; the ten new cards and the new playlist are therefore absent from it until that tool is run again.

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

Six commits were pushed to `main` on top of `3132647`:

| Commit | Content |
| --- | --- |
| `e54e76a`, `bd64551`, `a9c1ad8` | migration + new playlist content (one logical change, split into three API batches of 60/60/30 files) |
| `5b78945` | regenerated `src/data/content.js` and `content/index.json` |
| `38e7e94` | `chore(ui)` - factual text and count corrections |
| `c756f12` | docs |

**How it was pushed, and the one snag.** The GitHub App installation on this repository is read-only: `git push`
returns 403 ("Permission to deny to SRIHARI-VB") and the App token's Git Data API returns 403 "Resource not accessible
by integration". The GitHub OAuth connection does have write access, so the commits were created through the GitHub
API (`GITHUB_COMMIT_MULTIPLE_FILES`) instead of the git protocol. Nothing was force-pushed and no history was
rewritten.

Two consequences worth knowing:

1. The content commit appears three times in the log with the same message, because the API path commits in batches
   and each batch is its own commit. Squashing them would mean rewriting published history, so they are left as they
   are.
2. Because the API path recreates files rather than replaying the local commit objects, the local commit SHAs and the
   published ones differ. The published tree is what a fresh clone contains and it is verified below.

A fresh clone of `main` after the push: `python3 scripts/build-index.py` reproduces `src/data/content.js` byte for
byte (clean working tree), `python3 scripts/validate.py` reports 10 checks passed and 0 failures, and
`node tests/visual-lessons.js` draws every step of all five p5 lessons.

### Definition of done

Met for this playlist except where the limitations above apply: every video has an explicit processing status, every
card carries sources and a quick check, every PYQ carries a year, a question reference and a source URL, and no
question is presented as a previous-year question without one.

---

## Run 4 - Partial Orders and Lattices (2026-10-28)

**Why this topic.** `content/coverage.json` pointed at `discrete-mathematics/sets-relations-functions` after run 3. The
first topic strictly after that pointer in syllabus order whose status is not `covered` is
`discrete-mathematics/partial-orders-and-lattices`, which was `not_started`. Nothing was skipped: `partial-orders-and-lattices`
was the first candidate and it was processed.

**Subtopics enumerated first**, from the GATE 2027 CS line "partial orders and lattices": poset axioms; covering relation and
Hasse diagrams; comparability, chains and antichains; minimal/maximal/least/greatest elements; bounds, LUB and GLB; the lattice
test; the lattice laws; sublattices; bounded and complemented lattices; distributive lattices; Boolean lattices; complete
lattices.

**Sources chosen on merit** (full ledger in `content/subjects/discrete-mathematics/partial-orders-and-lattices/sources.json`):

- NPTEL IIT Madras, Lecture 40 "Lattices" - read in full from its published transcript PDF. It carries the lattice laws, the
  M3 and pentagon counterexamples, uniqueness of complements in a distributive lattice, and the chain/antichain decomposition
  theorem, all of which the cards use.
- NPTEL IIT Guwahati, NOC Discrete Mathematics Lec 21-23 - structure only; captions could not be retrieved in this run.
- GO Classes for GATE CS, "Lattice, POSET - GATE PYQs - Part 1" - auto-caption excerpt read for the GATE 1993, 1996 and 2003
  segments, which the Hasse-diagram and minimal/maximal cards draw on.
- GO Classes for GATE CS, "Constructing Total Order from Partial Order" (GATE 2024, 1997) - captions unavailable; both counts
  are recomputed instead.

Rejected, with reasons in the ledger: the Sandeep Kumar Gour Hindi playlist (16 videos, no readable content - rejected for
access, not for language), the NPTEL IIT Roorkee 2015 chapters 30-32 (all transcripts marked unavailable), the Neso Academy
sequence (complete but proof-free and unreadable here), and IIT Madras Lecture 39 (an automata lecture, read and discarded).

**Created.** 12 cards, one per subtopic; 6 verified PYQs (GATE CSE 1996 Q.1.2, 1997 Q.6.1, 2004 Q.73, 2017 Set 2 Q.21,
2024 Set 2 Q.24, 2025 Set 2 Q.32); one p5.js lesson `poset-to-lattice-pair-test`; a "Partial orders and lattices" group in
`content/revision/formulas.json`.

**Mathematics.** `scripts/validate.py` gains `check_lattices`, which counts the posets on 2, 3 and 4 elements (3, 19, 219),
recomputes every Hasse edge and relation count, verifies Mirsky's antichain partition on every poset up to four elements,
recomputes both linear-extension counts, checks the four lattice laws and the semi-distributive inequality on six lattices,
reproduces the M3 and N5 counterexamples, and decides every sublattice, complement, Boolean and completeness claim in the
cards and the lesson. Two claims were wrong on first draft and were corrected by these checks: the pentagon counterexample
(the meet-over-join form happens to hold in N5; it is the join-over-meet form that fails) and the complements in D12 (3 and 4
do complement each other; 2 and 6 do not).

**Gaps (topic stays `partial`).** Video captions were not retrievable in this run (YouTube answered `LOGIN_REQUIRED`, the
third-party transcript service was blocked), so four chosen video sources are structure-only and no card quotes or timestamps
them. Three figure-only PYQs could not be recomputed from text and are excluded: GATE CSE 1997 Q.3.3, 2005 Q.9 and 2015
Set 1 Q.34. Birkhoff's forbidden-sublattice characterisation is stated from the standard reference only.

**Checks.** `python3 scripts/build-index.py` and `python3 scripts/validate.py` pass (15 checks, 0 failures, 8 pre-existing
warnings), and `node tests/visual-lessons.js` draws every step of all nine p5 lessons.

## Run 5 - Monoids and Groups (2026-10-28)

### The topic, and why it was next

**Discrete Mathematics > Monoids and Groups** (`monoids-and-groups`), the fifth topic of the GATE 2027 Discrete
Mathematics line: *"Propositional and first order logic. Sets, relations, functions, partial orders and lattices.
Monoids, Groups. ..."*

The ledger's cycle pointer stood at `discrete-mathematics/partial-orders-and-lattices` after the previous run, and
that topic is `partial`. The first topic strictly after it, in syllabus order, whose status is not `covered`, is
`monoids-and-groups`, which was `not_started`. Nothing was skipped and nothing was `blocked`: the three earlier
`partial` topics (propositional logic, first order logic, combinatorics) are not candidates yet, because the cycle
takes a second pass over partial topics only after a full pass finds no `not_started` topic left.

Status before this run: `not_started`. Status after: `partial`, with five named gaps.

### Subtopics enumerated before any source was chosen

Eleven, from the GATE line plus the standard treatment of groups, checked for completeness against the published
GO Classes Module 7 lecture sequence:

1. binary operation, closure and the algebraic-structure ladder
2. monoids: identity, uniqueness of the identity, standard examples
3. group axioms, uniqueness of identity and inverse, cancellation and `(ab)^-1 = b^-1 a^-1`
4. order of a group and order of an element, and the divisibility corollary
5. abelian groups and the conditions that force commutativity
6. subgroups and the one-step and two-step tests
7. cyclic groups, generators and groups of prime order
8. cosets, the index and Lagrange's theorem
9. the small cast of groups GATE reuses: Z_n, direct products, matrix groups, power sets under symmetric difference
10. group homomorphism, kernel and isomorphism
11. permutation groups and the symmetric group

### Sources chosen, on merit

- **GeeksforGeeks, "Group theory Notes for GATE Exams"** (English, article text read in full) - the ladder, the group
  properties, the subgroup tests, cyclic groups and Lagrange's theorem. Chosen because it was the only GATE-oriented
  written source whose whole text could be read in this run, and because its vocabulary is the one GATE uses.
- **Pradeep Giri Academy, "Algebraic Structure | Group Theory | Discrete Mathematics | Lecture 01"** (Hindi
  auto-captions, read in part) - the rung-by-rung construction of the ladder with one worked example per rung. This
  is the only non-English source used, and **every sentence taken from it is translated into English and marked as
  translated, with the source language named (Hindi)**. It appears on the ladder and monoid cards.
- **GO Classes for GATE CS, Discrete Mathematics Module 7 lecture list** (English, structure only) - used to check
  that the subtopic enumeration is complete and in GATE order, not to source any statement. Its captions were not
  retrievable, so it is recorded as `UNAVAILABLE` and no card quotes it.

Rejected, with reasons in `sources.json`: the NPTEL IIT Madras "Algebras" lectures 35-37 (the same course that
supplied the full-text Lecture 40 for the previous topic - the transcript PDFs could not be fetched this run, so
nothing could be read); the NPTEL "Introduction to Abstract Group Theory" series (right topic, wrong depth, and
unreadable here); the Knowledge Gate Hindi playlist (a serious competitor, but no caption text retrievable); the
Dr. Gajendra Purohit playlist (large and complete, but an engineering-mathematics sequence with no GATE question
work and no readable captions); and the GATE answer aggregators (GateAI, Success Tracker, Testbook, EduRev,
BattleExam), which disagree with each other and were used only to cross-check paper numbering.

### Created

11 cards, one per subtopic; 13 verified PYQs (GATE CSE 1996 Q.2.4, 1997 Q.3.1, 2005 Q.46, 2014 Set 3 Q.3,
2014 Set 3 Q.50, 2018 Q.19, 2020 Q.18, 2021 Set 1 Q.34, 2022 Q.27, 2023 Q.41, 2024 Set 1 Q.42, 2024 Set 2 Q.53,
2025 Set 1 Q.39), each with its year, its question reference as the paper numbers it where the numbering is
disputed, a GATE Overflow URL and the accepted answer quoted in `answer_evidence`; one p5.js lesson
`cyclic-subgroup-and-lagrange`; and a "Monoids and groups" group in `content/revision/formulas.json`.

### Mathematics

`scripts/validate.py` gains `check_monoids_and_groups`, which: checks that Z_n is a group and that its element
orders are n/gcd(a,n) for every n up to 20; verifies that the generators of Z_n are the residues coprime to n and
that there are phi(n) of them; enumerates the subgroups of Z_n and checks Lagrange for each; recomputes every
"largest possible proper subgroup" claim (84 -> 42, 35 -> 7, 45 -> 15, and the 2014 Set 3 filter on 15 -> 5);
counts self-inverse elements in Z_2 x Z_3 x Z_4 and Z_4 x Z_6; rebuilds the cosets of {0, 4, 8} in Z_12 and checks
that they partition the group; checks the two made-up operations of the 2024 Set 1 question by brute force; verifies
S_3 and S_4 products, the nine elements of order 2 in S_4, and that A_4 of order 12 has no subgroup of order 6;
classifies every group of order up to 4 from reduced multiplication tables and confirms all four are abelian and
that order 4 has exactly two groups; checks the 2014 Set 3 Q.50 step (every pair of involutions with an involutive
product commutes, and {e, x, y, xy} is closed) over S_4 and S_5; verifies the 2005 upper-triangular matrix group by
exact-fraction inversion; verifies the 1996 options including the one-step test on all 4095 subsets of Z_12; and
checks the homomorphism and exponential-map claims.

Two claims were corrected by these checks before publication: the first draft of the S_3 example in the group-axioms
card computed `b^-1 a^-1` wrongly (it is `(2 3)`, not `(1 3)`; `(1 3)` is `a^-1 b^-1`), and the first draft of the
Z_4 x Z_6 count said 8 instead of gcd(2,4) x gcd(2,6) = 4.

### Gaps (the topic stays `partial`)

1. Video captions could not be retrieved in this run: YouTube watch pages carried no caption tracks and the
   timedtext endpoint returned an empty body. The GO Classes sequence is therefore structure-only.
2. The NPTEL IIT Madras "Algebras" transcripts (lectures 35-37) could not be fetched - the host refused the request
   from the sandbox. No claim rests on them; a later run should retry, since this course's published transcripts
   carried the previous topic.
3. Quotient groups, normal subgroups, Cauchy's and Sylow's theorems and group actions are outside the GATE line and
   are not covered at all; the homomorphism card is the only material beyond the two words "Monoids, Groups".
4. GATE CSE 1999 Q.4, the three-part descriptive question that derives Lagrange from cosets, is excluded because the
   PYQ schema holds only MCQ, MSQ and NAT records; the cosets card covers the same content.
5. Only one non-English source was readable (Hindi auto-captions), and its contribution is the structure ladder
   alone. No Tamil, Telugu or Bengali group-theory lecture could be read this run.

### Checks

`python3 scripts/build-index.py` indexes 3 playlists, 39 videos, 71 topics and 62 PYQs.
`python3 scripts/validate.py` passes with 16 checks, 0 failures and 8 pre-existing warnings.
`node tests/visual-lessons.js` draws every step of all ten p5 lessons.

### Next

`discrete-mathematics/graphs` - Graphs: connectivity, matching, colouring, the next `not_started` topic after this
one in the syllabus order.

## Run 6 - Graphs: Connectivity, Matching, Colouring (2026-10-28)

### The topic, and why it was next

`content/coverage.json` had `cycle.last = discrete-mathematics/monoids-and-groups`. The first topic strictly
after that pointer in the enumerated syllabus order whose status is not `covered` is
`discrete-mathematics/graphs`, which was `not_started`, so it was next. Nothing was skipped: no topic between the
pointer and this one exists in the Discrete Mathematics list, and no topic was marked `blocked` in this run.

The syllabus line is three words - "Graphs: connectivity, matching, colouring" - so the subtopics had to be
enumerated from the standard content those words name, not from any video.

### Subtopics enumerated before any source was chosen

1. Graph vocabulary, degree and the handshake lemma.
2. Paths, cycles, connected components, and the n-k and C(n-k+1,2) edge bounds.
3. Cut vertices, bridges, biconnected components and the two DFS criteria.
4. Vertex and edge connectivity, and the chain kappa <= lambda <= delta.
5. Eulerian and Hamiltonian graphs, including Dirac's sufficient condition.
6. Bipartite graphs, the odd-cycle criterion and the floor(n^2/4) edge bound.
7. Matching: maximal, maximum, perfect, and augmenting paths.
8. Hall's marriage theorem and complete matching.
9. Vertex cover, independent set, clique and Koenig's theorem.
10. Chromatic number, greedy bounds, Brooks' theorem and the standard families.
11. Chromatic polynomial and counting proper colourings.

Each of the eleven has exactly one card.

### Sources chosen, on merit

- **GATE Overflow GO Classroom deck, "Graph Theory: Connectivity, Coloring, Matching"** (English, read in part).
  Its title is the syllabus line, it uses GATE's vocabulary, and its pages were the only GATE-oriented graph text
  that could actually be read in this run. It supplied the definitions, the cut-set and connectivity bounds, the
  colouring families, the matching vocabulary and the r-subset form of Hall's theorem. The fetch was truncated
  after the Havel-Hakimi example, so the matching pages were read only as excerpts - recorded as `PARTIAL`.
- **GATE Overflow Graph Theory subject notes, Volume 1 chapter** (English, read in part). Used to confirm the
  subtopic enumeration against GATE's own question record and to check the counting formulas that border this
  topic. Not used as teaching for any claim.
- **NPTEL IIIT Bangalore Discrete Mathematics, lectures 44-52** (English, structure only). The published lecture
  list - Graph Theory Basics, Matching, Proof of Hall's Marriage Theorem, Vertex and Edge Connectivity, Euler
  Path and Circuit, Hamiltonian Circuit, Vertex and Edge Coloring - was used to confirm that the eleven subtopics
  are complete. The transcripts could not be fetched, so no card quotes it.

Rejected, with reasons recorded in `content/subjects/discrete-mathematics/graphs/sources.json`: the NPTEL "Graph
Theory" course by Soumen Maity (best scope of all, but no readable transcript and it runs into flow and planarity);
GeeksforGeeks (every request failed from the sandbox); Gate Vidyalay (snippet only); the Knowledge Gate AI
colouring blog (a question dump that agreed with one accepted answer, used only as a cross-check); the answer
aggregators ExamSIDE, GateAI, EduRev, Testbook and Zollege (they disagree on numbering, so no reference is taken
from them); and every video in every language, because YouTube served a consent wall with no caption tracks.

**No translated material appears in this topic.** No non-English source could be read this run, so no card is
marked as translated and no source language had to be named on a card.

### Created

11 cards, 9 PYQs and one p5.js lesson.

| Card | PYQs |
| --- | --- |
| graph vocabulary and the handshake lemma | - |
| paths, cycles and connected components | - |
| cut vertices, bridges and blocks | 2015 Set 2 Q.50, 2021 Set 1 Q.41 |
| vertex and edge connectivity | - |
| Eulerian and Hamiltonian graphs | - |
| bipartite graphs and the odd-cycle criterion | 2014 Set 2 Q.3, 2026 Set 1 Q.45 |
| matching: maximal, maximum, perfect | 2026 Set 1 Q.47 |
| Hall's marriage theorem | - |
| vertex cover, independent set and Koenig | 2026 Set 1 Q.37 |
| chromatic number, greedy and Brooks | 2024 Set 1 Q.41, 2002 Q.1.4, 2022 Q.40 |
| chromatic polynomial | - |

Every PYQ carries a year, a paper, a question reference and the GATE Overflow URL it was read on, with the
accepted answer quoted as evidence; all nine are labelled `SOURCED`, none `OFFICIAL_KEY`, because the official
papers and keys were not fetched this run. Variation labels stay distinct: `ORIGINAL PYQ-STYLE QUESTION`,
`CONCEPTUAL PRACTICE QUESTION` and `PREDICTED VARIATION` only, and no generated question is presented as a PYQ.

The lesson `visuals/discrete-mathematics/graphs/bipartite-matching-augmenting-path` shows a greedy matching get
stuck at size 2, the four blocked edges that make it maximal, the augmenting path b-1-a-2-c-3, the flip to a
perfect matching of size 3, and the cover {1, 2, c} that makes Koenig's equality visible.

`content/revision/formulas.json` gained a "Graphs" group of thirteen formulas, and `content/syllabus.json` now
marks the topic `cards` instead of `planned`.

### Mathematics

A new `check_graphs()` in `scripts/validate.py` recomputes every claim in the topic:

- the handshake lemma, the odd-degree parity, n(n-1)/2, and the n-k and C(n-k+1,2) bounds on **every** graph on up
  to 6 vertices; Havel-Hakimi accepts 3,3,2,2,2,2 and rejects 3,3,3,1;
- bridge-if-and-only-if-no-cycle on every graph on up to 5 vertices, the n-2 cut-vertex bound, and **both DFS
  rules over every DFS tree of every connected graph on up to 5 vertices** (every adjacency order, every root);
- kappa <= lambda <= delta and kappa <= floor(2|E|/n) on every connected graph on up to 4 vertices, plus the bowtie
  (kappa 1, lambda 2), K_4, K_5, K_3,3 and the Petersen graph (3-connected, 15 edges);
- the Euler parity criteria against brute-force trail existence, K_2,3 and K_3,3, K_4 plus a pendant edge, Dirac's
  non-necessity on C_5, Hamiltonicity of K_{m,n} for m,n in {2,3}, Petersen having a Hamiltonian path and no
  Hamiltonian cycle, and K_5 splitting into two edge-disjoint Hamiltonian cycles;
- the odd-cycle criterion as bipartite iff chromatic number at most 2 on every graph on up to 5 vertices, and
  floor(n^2/4) for n = 7, 9, 12;
- matchings of P_n = F(n+1) for n = 1 to 8, C_5 = 11, perfect matchings of K_{n,n} = n!, the empty matching
  included, and the half-size bound on every graph on up to 4 vertices;
- Hall's condition and its defect form on **every** bipartite graph up to 3 by 3, and a perfect matching in every
  d-regular bipartite graph on 4 plus 4 vertices for d = 1, 2, 3, including the split into two perfect matchings;
- alpha + tau = n, nu <= tau, Koenig on every bipartite graph on up to 5 vertices, the triangle and C_5 failures,
  and the 2026 forced-vertex claim over every minimum cover of every graph on up to 5 vertices;
- chromatic numbers of K_n, C_n for n = 3 to 10, trees and the Petersen graph; omega <= chi <= Delta+1, chi >= n/alpha,
  the C(k,2) edge bound and Brooks on every graph on up to 5 vertices; the 2002 formula against chi(C_n);
- the chromatic polynomial by deletion-contraction on every graph on up to 5 vertices: monic, degree n, k^(n-1)
  coefficient minus |E|, constant term 0 with edges, agreement with direct counting at k = 1, 2, 3, the smallest
  positive root equal to chi, plus the K_n, tree and cycle formulas and C_4 = k^4 - 4k^3 + 6k^2 - 3k.

Two claims were corrected before publication. The first draft of the lesson used a five-edge path, whose caption
claimed two 4-cycles; the graph has no cycle at all, so the sixth edge b-2 was added and the caption rewritten to
name the single 4-cycle. The first draft of the Fibonacci index in the check compared against F(n+2); the card's
claim F(n+1) is right and the check was the thing that was wrong.

### Gaps (the topic stays `partial`)

1. No video source was readable: YouTube served a consent wall with no caption tracks for every video tried, in
   every language. No card quotes or timestamps a lecture, and no translated material exists in this topic.
2. Four PYQs of this topic are figure-only and are excluded: GATE CSE 2024 Set 2 Q.50, GATE CSE 2018 Q.18 and
   GATE CSE 1999 Q.1.15. GATE CSE 2022 Q.40 is included, but its isomorphism option rests on the paper's drawing
   and is not re-derived.
3. Planar graphs, Euler's formula for plane graphs, edge colouring and network flow beyond bipartite matching are
   outside the syllabus line and are not covered.
4. GATE Overflow's subject page lists further graph-theory questions from 2010 to 2023 that were not read or
   recomputed in this run; only the nine recorded PYQs were verified.
5. The chromatic polynomial card rests on the standard references and on recomputation, because no verified GATE
   CSE previous-year question on the chromatic polynomial was found.
6. No `marks` field is recorded on any PYQ of this topic: the official papers were not fetched, so marks are left
   out rather than guessed.

### Checks

`python3 scripts/build-index.py` indexes 3 playlists, 39 videos, 82 topics and 71 PYQs.
`python3 scripts/validate.py` passes with 17 checks, 0 failures and 8 pre-existing warnings.
`node tests/visual-lessons.js` draws every step of all eleven p5 lessons.

### Next

The cycle pointer now sits on `graphs`. The topic immediately after it in the syllabus order is
`discrete-mathematics/combinatorics`, which is already `partial`; the skill's second-pass rule defers partial
topics until a full pass finds no `not_started` topic left, so the next run takes the first `not_started` topic
after the pointer, `linear-algebra/matrices-and-determinants`. `combinatorics` waits for the second pass, with its
two recorded gaps (no re-audit of its subtopics since it was built from a single playlist, and long lecture
transcripts readable only in their opening minutes).

## Run 7 - Matrices and Determinants (2026-10-28)

### The topic, and why it was next

**Linear Algebra > Matrices and Determinants** (`linear-algebra/matrices-and-determinants`), the first topic of the
GATE 2027 Linear Algebra line: *"Matrices, determinants, system of linear equations, eigenvalues and eigenvectors,
LU decomposition."*

`content/coverage.json` had `cycle.last = discrete-mathematics/graphs`. Walking the enumerated syllabus from there,
the topic immediately after `graphs` is `discrete-mathematics/combinatorics`, which is already `partial`; the skill's
second-pass rule defers partial topics until a full pass finds no `not_started` topic left, so the next candidate is
the first `not_started` topic after the pointer, `linear-algebra/matrices-and-determinants`. That is exactly what the
previous run's report predicted. **Skipped:** `combinatorics` (partial, second pass), and nothing was `blocked`.
Status before this run: `not_started`. Status after: `partial`, with seven named gaps.

### Subtopics enumerated before any source was chosen

The syllabus gives two words, "Matrices, determinants", so the subtopics come from the standard content those words
name, cross-checked against the NPTEL IIT Roorkee lecture order (types of matrices, determinant, rank):

1. matrix vocabulary, order, entry notation and the standard types
2. addition and scalar multiplication with their laws, additive identity and inverse
3. multiplication: the conformability rule, the row-times-column formula and non-commutativity
4. transpose and its laws, symmetric and skew-symmetric matrices, the symmetric-plus-skew decomposition
5. powers of a square matrix, and the idempotent, involutory, nilpotent and orthogonal identities
6. trace, its linearity, the cyclic law and the trace-eigenvalue link
7. the determinant: minors, cofactors, Laplace expansion and the triangular rule
8. how row and column operations change a determinant, and the laws det(AB), det(kA), det(A^T), det(A^-1)
9. cofactor matrix, adjoint, inverse, `A adj(A) = |A| I` and `|adj A| = |A|^(n-1)`
10. rank: row rank equals column rank, the echelon and minor definitions, and the rank inequalities
11. singular and non-singular matrices with the equivalent-condition list

Each of the eleven has exactly one card. The full ledger, with what was rejected and why, is
`content/subjects/linear-algebra/matrices-and-determinants/sources.json`.

### Sources chosen, on merit

| Source | Channel | Language | Transcript | What it carries |
| --- | --- | --- | --- | --- |
| CS6015 LARP 2018 slide decks: Matrices, Matrix multiplication, Gaussian Elimination, Inverses and Transposes, Determinants | IIT Madras (cse.iitm.ac.in) | English | FULL | Definitions, the multiplication and transpose rules, the pivot count behind rank, the inverse and reversal laws, the determinant as a signed volume and its four uses |
| Linear Algebra subject notes | GATE Overflow | English | PARTIAL | The per-year marks table, the determinant property list, and the named pitfalls including `det(A+B) = det(A)+det(B)` |
| Matrices and Determinant Notes for GATE CSE and DA | GeeksforGeeks | English | PARTIAL | The type list and the adjoint, inverse, trace and rank property lists |
| Mega OneShot: Aavyuh tatha Sarnik (Matrices And Determinants) | ashish singh lectures (Hindi) | Hindi | PARTIAL (opening) | The definition and order, the named matrix types, the equality rule, the addition and scalar laws, the multiplication condition - **translated into English and marked as translated** |
| NOC: Numerical Linear Algebra lecture list | NPTEL, IIT Roorkee | English | UNAVAILABLE | Structure only: confirms that types, determinant and rank are the elementary layer |

**Rejected, with reasons in `sources.json`:** the IIT Kanpur MTH102 lecture notes (downloaded, but scans of handwritten
pages whose text layer is OCR noise, so not one formula was recoverable); Ankur Gupta's GATE engineering-mathematics
PDF and the Vidyalankar GATE mathematics notes (well matched, but every fetch failed from the sandbox with a 502);
the Unacademy "(Hindi) All About Linear Algebra: GATE" series (the best GATE-focused Hindi candidate, but paywalled
with no transcript); the NPTEL IIT Kanpur Linear Algebra book by Arbind Kumar Lal (closest match of all on paper,
but the host returned 404 for every path tried); the NPTEL IISc course by Dilip Patil (determinants only in week 11,
via multilinear forms - a mathematics-major sequence); the NPTEL IIT Delhi web course (vector spaces and the eigen
spectrum, with the matrix basics assumed); the Manish Kalia formula sheet (a JEE revision sheet with no derivations);
and the answer aggregators ExamSIDE, GateAI and pyqbox, which disagree on question numbering and were used only to
corroborate one official answer.

### Translated material

The Hindi one-shot is the only non-English source, and it is the only readable non-English source found in this topic
after three runs in which YouTube supplied no caption text at all. It is a Class-12 NCERT lecture rather than a GATE
lecture, so it is used only for the elementary vocabulary, the matrix types and the operation laws. Every sentence
taken from it is translated into English and marked as translated on the three cards that use it, with the source
language (Hindi) named on the card, in the source ledger and here.

### Created

| Item | Added this run | Total in repository |
| --- | --- | --- |
| Revision cards | 11 | 93 |
| Verified PYQs | 13 | 84 |
| Question variations | 33 (11 ORIGINAL PYQ-STYLE, 11 CONCEPTUAL PRACTICE, 11 PREDICTED VARIATION) | 233 |
| Quick checks with answers | 11 | 93 |
| Traps with counterexamples | 11 | 93 |
| Visual lessons | 1 (`matrices-and-determinants/determinant-as-area-scaling`, 7 steps) | 12 |
| Formula-sheet groups | 1 (13 formulas) | 16 |
| Topic source ledgers | 1 | 5 |

The thirteen PYQs are GATE CSE 2026 Set 2 Q.52 (det of 2A), 2025 Set 2 Q.1 (A^8) and Q.4 (det of M - N), 2024 Set 2
Q.37 (what survives a row swap), 2023 Q.8 (a single row interchange), 2022 Q.10 (the cyclic trace law), 2020 Q.27
(rank and determinant statements), 2021 Set 2 Q.24 (rank from nullity), 2014 Set 2 Q.4 (a column times a row is
singular), 2000 Q.1.3 (expansion with zeros), 1998 Q.2.1, 1994 Q.1.9 and 2002 Q.1.1 (rank computations). Each carries
a year, a paper, a question reference and the GATE Overflow URL it was read on, with the accepted answer quoted as
`answer_evidence`. All thirteen are `SOURCED`, none `OFFICIAL_KEY`, because the official papers and keys were not
fetched; GATE CSE 2022 Q.10 is the only one with an independent corroboration of the official option.

### The visual lesson

`visuals/linear-algebra/matrices-and-determinants/determinant-as-area-scaling/` draws the determinant as the signed
area of the parallelogram spanned by the two columns, then walks the four row-operation rules as area operations: the
unit square with area 1; A = [[2,1],[0,3]] with area 6; the rows swapped, same area and reversed orientation, -6;
row 1 scaled by 3, area 18; row 2 added to row 1, a shear that leaves the area at 6; rows made dependent, area 0;
then the four rules together with the singularity equivalence.

### Mathematics

A new `check_matrices_and_determinants()` in `scripts/validate.py` recomputes every claim in the topic: the type and
diagonal counts; the addition, multiplication and transpose laws over every small integer matrix; the worked products
and the (AB)^2 counterexample; 64 symmetric 3x3 0/1 matrices counted by enumeration; the symmetric-plus-skew
decomposition on every 2x2 integer matrix; the odd-order skew-symmetric determinant over every skew 3x3 matrix with
entries in {-1,0,1} and the "rank is never 1" claim; the idempotent, nilpotent and involutory consequences over every
2x2 matrix in range, plus the 2025 Set 2 Q.1 and Q.4 chains on explicit matrices; `tr(AB) = tr(BA)` for square and
rectangular factors and the non-cyclic counterexample; every Laplace expansion along every row and column of every
3x3 0/1 matrix; the determinant laws `det(A^T)`, `det(kA)`, `det(AB)`, `det(A^-1)` and the four row-operation effects
of the lesson; `A adj(A) = |A| I`, `|adj A| = |A|^(n-1)`, `adj(adj A)`, `adj(AB)` and `adj(kA)` on every 3x3 0/1
matrix and on random matrices; the ranks of the 1994, 1998 and 2002 questions; the rank inequalities and Sylvester's
inequality over every 2x2 pair; `rank(adj A) = 1` at rank 2; the rank-nullity reading of the 2021 question; and the
equivalence of determinant zero, rank below n and non-invertibility on every 2x2 matrix.

One content claim was caught and corrected before publication: the first draft of the transpose card's quick check
asked for the determinant of a 4x4 skew-symmetric matrix, which is **not** necessarily zero - the odd-order argument
gives no constraint when n is even. The check now asks about a 3x3 matrix, and the card states the even-order
exception explicitly. Four of the new validator assertions were also wrong on first run (a mis-specified skew test,
an inverted counterexample test, a rank expectation of 2 where the matrix has rank 3, and a null vector that did not
annihilate the matrix built for it); the assertions were fixed, not the content, and the function now passes.

### Validation performed

- `python3 scripts/build-index.py` indexes 3 playlists, 39 videos, 93 topics and 84 PYQs.
- `python3 scripts/validate.py` - 18 checks passed, 0 failures, 8 warnings, all eight pre-existing (seven PYQs
  labelled `OFFICIAL_KEY` without an evidence line, two combinatorics videos not referenced by any card).
- `node tests/visual-lessons.js` - all twelve p5 sketches load and draw every step at three progress values,
  including the new seven-step lesson.

### UI

No change to design tokens, shell layout, navigation labels, routes or component classes. The new cards render
through the existing components, and the sidebar tree and the Topics tab pick up the new subject, its two units
(Matrices; Determinants and rank) and its eleven subtopics from the generated data with no code change.

### Gaps (the topic stays `partial`)

1. No GATE-oriented lecture was readable: every English GATE linear-algebra video page tried carried no caption
   track, so the teaching rests on the IIT Madras slide decks and two GATE revision texts.
2. The adjoint and inverse card carries no verified PYQ: the only GATE CSE inverse question found in this topic,
   1994 Q.3.12, is descriptive, and the PYQ schema holds only MCQ, MSQ and NAT records.
3. No `marks` field is recorded on any PYQ of this topic: the official papers were not fetched, so references follow
   the GATE Overflow numbering and marks are left out rather than guessed.
4. The one non-English source is a Class-12 Hindi one-shot read only in its opening; no GATE-level Hindi, Tamil,
   Telugu or Bengali lecture could be read this run.
5. Three full-text GATE note sets could not be fetched from the sandbox (Ankur Gupta, Vidyalankar, the NPTEL IIT
   Kanpur book); nothing rests on them and a later run should retry.
6. Every PYQ is `SOURCED` against a GATE Overflow accepted answer rather than key-verified against an official key.
7. GATE Overflow lists further linear algebra questions from 2010 to 2019 that were not individually read or
   recomputed; only the thirteen recorded PYQs were verified.

### Next

The cycle pointer now sits on `linear-algebra/matrices-and-determinants`. The topic immediately after it in the
syllabus order is `linear-algebra/system-of-linear-equations`, which is `not_started`, so that is the next run's
topic.
