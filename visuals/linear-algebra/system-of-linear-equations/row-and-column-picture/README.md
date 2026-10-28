# Two lines, three cases, and the rank test that decides which one

The row picture behind the consistency test: a 2 by 2 system is two lines, the three arrangements they can
be in, and the comparison of rank(A) with rank([A|b]) that separates "no solution" from "infinitely many".

- `index.html` - the lesson page: canvas, controls, static explanation, misconception, quick check.
- `sketch.js` - the p5.js steps. Seven steps: the identity system with its crossing point (2,1); A =
  [[1,1],[1,-1]] with b = (3,1), two lines crossing at (2,1) and the column combination 2(1,1) + 1(1,-1);
  the same line twice with b = (1,2), infinitely many solutions; parallel distinct lines with b = (1,3), no
  solution; the k = 1 case of x + ky = 1, kx + y = -1, no solution; the k = -1 case, infinitely many; then
  the decision order to carry into the exam.
- `lesson.json` - metadata read by the site and by `tests/visual-lessons.js`.

Every number on the page is recomputed by `scripts/validate.py` (`check_system_of_linear_equations`): each
of the six systems has its determinant, its two ranks, its verdict and, where it exists, its solution
recomputed by Gaussian elimination over the rationals, and the two k cases are checked against the reduction
that GATE CSE 2025 Set 1 Q.13 needs.

Sources: GATE Overflow blog, "Linear Algebra (Gilbert Strang) Notes, Lecture 1 to 10" (English, read in part)
for the row picture, the column picture and the complete solution; SATHEE, IIT Kanpur, "Consistency and
Solution of Simultaneous Linear Equations" (English, read in part) for the rank criterion and the
plane-arrangement table; GATE Overflow blog, "Linear Algebra Important Points" (English, read in part) for the
consistency branches. Related verified PYQs: GATE CSE 2025 Set 1 Q.13, GATE CSE 1998 Q.1.2 and
GATE CSE 2003 Q.41.
