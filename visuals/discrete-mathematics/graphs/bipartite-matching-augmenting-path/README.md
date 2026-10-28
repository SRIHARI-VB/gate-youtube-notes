# Augmenting paths, maximal versus maximum, and Koenig's theorem

The six-edge bipartite graph used to separate a maximal matching from a maximum one, to show the flip that
proves a matching is not maximum, and to exhibit the equality of maximum matching and minimum vertex cover.

- `index.html` - the lesson page: canvas, controls, static explanation, misconception, quick check.
- `sketch.js` - the p5.js steps. Six steps: the bipartite graph and its single 4-cycle; the greedy matching
  {a-1, c-2}; the four blocked edges that make it maximal; the augmenting path b-1-a-2-c-3 with free endpoints;
  the flip, giving the perfect matching {b-1, a-2, c-3}; then Koenig, with the cover {1, 2, c} of size 3.
- `lesson.json` - metadata read by the site and by `tests/visual-lessons.js`.

Every number on the page is recomputed by `scripts/validate.py` (`check_graphs`): the graph is rebuilt from its
edge list, the maximal matching is checked to be maximal and of size 2, the maximum matching is found by brute
force over all edge subsets and is of size 3, the augmenting path is checked to alternate outside/inside the
matching with both endpoints free, the cover {1, 2, c} is checked to touch every edge, and every pair of vertices
is checked to fail to be a cover.

Sources: GATE Overflow GO Classroom deck "Graph Theory: Connectivity, Coloring, Matching" (English, read in part)
for the matching vocabulary, the complete-matching condition and the independent-set bound; CLRS ch. 26 for
augmenting paths and the symmetric-difference argument. Related verified PYQs: GATE CSE 2026 Set 1 Q.47 and
GATE CSE 2026 Set 1 Q.37.
