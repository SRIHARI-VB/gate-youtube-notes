# From a Shift Register to the Johnson Cycle

A p5.js lesson for the Digital Logic topic **Sequential Circuits**, subtopics the ring and Johnson
counters, the shift register they are built from, and the 2n state count.

It works one circuit end to end: four D flip-flops in a chain with `D0 = Q3'`, `D1 = Q0`, `D2 = Q1`
and `D3 = Q2`. The eight steps are the order that works - see the feedback wire, shift the first 1
in, watch the block of ones grow to 1111, watch it shrink to 0001, close the cycle at 0000, find the
second cycle that the other eight patterns form, and then read the answer off the two accepted
forms of the question.

The circuit is the subject of two verified GATE CSE questions: 2015 Set 1 Q.20 asks for the counting
sequence (accepted option D) and 2025 Set 1 Q.50 asks for the number of distinct states (8, with 7
also accepted).

Every state, the cycle length 2n, the ring-counter count n, the 16 patterns and the 8 unused ones
are recomputed in `scripts/validate.py` (`check_sequential_circuits`), and
`node tests/visual-lessons.js` draws all eight steps at progress 0, 0.5 and 1 without a browser.

Sources for the teaching: the English Wikipedia article on digital counters for the ring and Johnson
definitions and the mod-n and mod-2n statements; KFUPM COE 202 Lecture 16 (English) for the
shift-register parent circuit; Auburn ELEC 2200 Lecture 7 (English) for the state count and the
Gray-code property. The questions and their accepted answers are on GATE Overflow's pages for GATE
CSE 2015 Set 1 Q.20 and GATE CSE 2025 Set 1 Q.50.
