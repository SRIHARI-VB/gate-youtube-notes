# Quantifier order: for all x there exists y, versus there exists y for all x

p5.js lesson. Four steps: the two claims side by side, a relation where every row has an entry
(so the for-all-there-exists form holds), the same relation where no column is full (so the
there-exists-for-all form fails), and a relation with one full column where both hold.

Verified facts (recomputed in `scripts/validate.py`, `check_first_order`): on the domain {1, 2, 3}
with R = {(1,2), (2,3), (3,1)} every element has an R-partner, so for all x there exists y R(x, y)
is true, while no single y is related to all three elements, so there exists y for all x R(x, y)
is false. The implication there exists y for all x R(x, y) implies for all x there exists y R(x, y)
is valid, and the converse is not.

Source: playlist GATE PYQs Part 2 (wzVFO4hyVfo), which lists nested quantifiers as the third
question type of the series; PYQ GATE CS 2023 Q.16 uses the same implication.
