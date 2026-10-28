# From poset to lattice: one pair at a time

The five-element poset of GATE CSE 2017 Set 2 Q.21, used to run the pairwise join/meet test.

- `index.html` - the lesson page: canvas, controls, static explanation, misconception, quick check.
- `sketch.js` - the p5.js steps. Six steps: the Hasse diagram and its five covering pairs; the upper bounds of
  {b, d}; the lower bounds of {b, d}; both bounds of {c, d} plus the comparable pair {b, c}; the verdict, 0 pairs
  to add; then the broken variant with d < e deleted, where {b, d} has no upper bound and one pair must be added.
- `lesson.json` - metadata read by the site and by `tests/visual-lessons.js`.

Every join, meet and count on the page is recomputed by `scripts/validate.py` (`check_lattices`), which builds
the relation from the covering pairs, verifies that it is a partial order, and checks the join and meet of every
pair against the values the lesson displays - for both the full poset and the broken variant.

Sources: NPTEL IIT Madras Lecture 40 "Lattices" (English, full transcript); GO Classes for GATE CS
"Lattice, POSET - GATE PYQs - Part 1" (English, auto-caption excerpt read). Verified PYQ: GATE CSE 2017 Set 2 Q.21.
