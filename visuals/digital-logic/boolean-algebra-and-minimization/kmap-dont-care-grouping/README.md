# Don't-Care Grouping on a Karnaugh Map

A p5.js lesson for the Digital Logic topic **Boolean Algebra and Minimization**, subtopics the
Karnaugh map layout, the grouping rules, and don't-care conditions.

It works one function end to end: `F(P,Q,R,S) = sum(0, 2, 5, 7, 8, 10, 13, 15)` with minterms
2, 7, 8 and 13 as don't cares, which is GATE CSE 2014 Set 3 Q.7. The seven steps are the order that
works - number the cells from the Gray-code labels, place the four required 1s, place the four Xs,
form the corner quad `Q'S'`, form the second quad `QS`, read the variables that stay constant, and
compare the four-literal answer with the sixteen-literal canonical form.

Every cell number, both quads and both literal counts are recomputed in `scripts/validate.py`
(`check_boolean_algebra`), and `node tests/visual-lessons.js` draws all seven steps at progress 0,
0.5 and 1 without a browser.

Sources for the teaching: NPTEL IIT Kharagpur Digital Electronic Circuits Lecture 10 (English) for
the map, the SOP-cover rule and the don't-care rule; the Wikipedia Karnaugh map article (English)
for wrap-around adjacency and for reading a term off a group; eHindiStudy's K-map chapter (Hindi,
translated) for the pair/quad/octet ladder and the rolling of the map. The question and its accepted
answer are on GATE Overflow's page for GATE CSE 2014 Set 3 Q.7.
