# From a 4-to-1 Multiplexer to a Minimal Sum of Products

A p5.js lesson for the Digital Logic topic **Combinational Circuits**, subtopics the multiplexer
output equation, implementing a Boolean function on a multiplexer, and reading a minimal sum of
products off a group.

It works one circuit end to end: a 4-to-1 multiplexer with select lines `S1 = P` and `S0 = Q` and
data inputs `I0 = 0`, `I1 = 1`, `I2 = R`, `I3 = R'`, which is GATE CSE 2014 Set 1 Q.45. The seven
steps are the order that works - read the select codes, substitute the data inputs, expand to the
four minterms 2, 3, 5 and 6, place them on a three-variable map, group them as `P'Q`, `QR'` and
`PQ'R`, then read the answer and compare three terms and seven literals against four terms and
twelve.

Every cell number, minterm, group and literal count is recomputed in `scripts/validate.py`
(`check_combinational_circuits`), and `node tests/visual-lessons.js` draws all seven steps at
progress 0, 0.5 and 1 without a browser.

Sources for the teaching: NPTEL IIT Kharagpur Digital Electronic Circuits Lecture 16 (English) for
the multiplexer definition, the output equation and the Shannon-expansion reading. The question,
its four minterms and the accepted option (A) are on GATE Overflow's page for GATE CSE 2014
Set 1 Q.45.
