# Two directions a matrix cannot turn

Sweeping an input vector around the unit circle through A = [[2,1],[1,2]] to find the two directions in
which the matrix only scales the vector instead of turning it, and to read the trace and the determinant
off the two scale factors.

- `index.html` - the lesson page: canvas, controls, static explanation, misconception, quick check.
- `sketch.js` - the p5.js steps. Seven steps: the input at 25 degrees and its image; the same pair with the
  input's own line drawn, to show the turn; a full sweep in which the turn angle falls to zero only at
  45 and 135 degrees; the eigenpair 3 with (1,1); the eigenpair 1 with (1,-1); both directions with the
  sum and product read as trace and determinant; and the right angle between the two eigenvectors, which
  holds because A is symmetric.
- `lesson.json` - metadata read by the site and by `tests/visual-lessons.js`.

Every number on the page is recomputed by `scripts/validate.py` (`check_eigenvalues_and_eigenvectors`):
A(1,1) = (3,3) and A(1,-1) = (1,-1), the characteristic polynomial lambda^2 - 4 lambda + 3 with roots 3
and 1, the trace 4 and the determinant 3, and the dot product of the two eigenvectors.

Sources: NPTEL, IIT Kharagpur, Engineering Mathematics I, Lecture 46 "Eigenvalues and Eigenvectors"
(English, read in full) for the definition and the geometric reading; NPTEL-NOC IIT Madras, CS7015
Lec 6.1 (English, read in part) for what a matrix does to a vector; GanitAnk's Hindi one-shot (Hindi,
read in part, translated) for the nonzero condition. Related verified PYQ: GATE CSE 2015 Set 3 Q.15.
