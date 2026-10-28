# The determinant as signed area, and what row operations do to it

The 2 by 2 picture behind the determinant rules: the parallelogram spanned by the two columns of a
matrix, its signed area equal to the determinant, and the four row operations acting on that area.

- `index.html` - the lesson page: canvas, controls, static explanation, misconception, quick check.
- `sketch.js` - the p5.js steps. Seven steps: the unit square with determinant 1; A = [[2,1],[0,3]] with
  area 6; the rows swapped, same area and reversed orientation, determinant -6; row 1 scaled by 3,
  determinant 18; row 2 added to row 1, a shear that leaves the area at 6; rows made dependent,
  determinant 0; then the four rules together with the singularity equivalence.
- `lesson.json` - metadata read by the site and by `tests/visual-lessons.js`.

Every number on the page is recomputed by `scripts/validate.py` (`check_matrices_and_determinants`):
each of the six determinants is evaluated twice, by cofactor expansion and by elimination, the scaling
rule is checked on every 2 by 2 and 3 by 3 integer matrix in a small range, and the 3 by 3 and 4 by 4
scalars used in the quick check and the PYQ link are recomputed.

Sources: IIT Madras CS6015 (LARP 2018) slides, deck 4 "Determinants" (English, read in full) for the
determinant as a signed volume; GATE Overflow Linear Algebra notes (English, read in part) for the
property list; GeeksforGeeks GATE notes (English, read in part) for det(kA) = k^n det(A). Related
verified PYQs: GATE CSE 2026 Set 2 Q.52, GATE CSE 2023 Q.8 and GATE CSE 2024 Set 2 Q.37.
