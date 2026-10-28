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
