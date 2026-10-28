# Relations as matrices

A 3 by 3 grid of ordered pairs for a relation on {1, 2, 3}, used to read five properties off the picture.

- `index.html` - the lesson page: canvas, controls, static explanation, misconception, quick check.
- `sketch.js` - the p5.js steps. Six steps: the grid and the count 2^9; reflexive (2^6 = 64); symmetric
  (2^6 = 64); antisymmetric (2^3 x 3^3 = 216); transitivity and the missing shortcut (1,3) with its closure;
  equivalence relations as blocks on the diagonal (B(3) = 5, B(4) = 15).
- `lesson.json` - metadata read by the site and by `tests/visual-lessons.js`.

Every number on the page is recomputed by `scripts/validate.py` (`check_sets_relations_functions`), which
enumerates all 512 relations on a 3-element set and tallies reflexivity, irreflexivity, symmetry,
antisymmetry, asymmetry, transitivity and equivalence, and checks each tally against the closed formula.

Sources: the IIT lecture Lec 02 on set identities, Cartesian product and relations (English, full transcript);
GO Classes for GATE CS on counting relations (English, opening readable only); Rosen ch. 9.
