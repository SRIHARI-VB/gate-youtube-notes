# Cyclic subgroups and Lagrange's theorem in Z12

One element, one subgroup, four cosets, six subgroup orders - the counting picture behind GATE's
"largest possible proper subgroup" questions.

- `index.html` - the lesson page: canvas, controls, static explanation, misconception, quick check.
- `sketch.js` - the p5.js steps. Six steps: the ring of twelve residues; the multiples of 4 closing after three
  steps; the subgroup {0, 4, 8} and the order of the element; the four cosets of {0, 4, 8} tiling the group;
  the element 5 reaching all twelve residues, so the generators are 1, 5, 7 and 11; then the six subgroup
  orders of Z12, all divisors of 12, with the largest proper one of order 6.
- `lesson.json` - metadata read by the site and by `tests/visual-lessons.js`.

Every number on the page is recomputed by `scripts/validate.py` (`check_monoids_and_groups`): the order of each
element of Z12, the subgroup each element generates, the four cosets of {0, 4, 8} and their disjointness, the
count of generators (phi(12) = 4), the six subgroup orders, and that every subgroup order divides 12.

Sources: GeeksforGeeks GATE group-theory notes (English, read in full) for the coset partition and Lagrange's
theorem; GO Classes Module 7 lecture list (English, structure only, captions unavailable in this run) for the
lecture order. Verified PYQs: GATE CSE 2018 Q.19, GATE CSE 2020 Q.18.
