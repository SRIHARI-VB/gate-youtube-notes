# IEEE 754 Bit Fields to Value

A p5.js lesson for the Digital Logic topic **Number Systems and Number Representation**,
subtopics the IEEE 754 single-precision layout, normalisation with a biased exponent, and the
special values.

It decodes one word, `0xC2710000`, in the order that works: hex to bits, cut 1 / 8 / 23, read the
sign, subtract the bias of 127, restore the hidden leading 1, move the binary point five places
right, and apply the sign. The last step draws the two reserved exponent fields, because that is
what the largest-finite-number questions turn on.

Every number shown is recomputed from its bits in `scripts/validate.py`
(`check_number_representation`), and `node tests/visual-lessons.js` draws all seven steps at
progress 0, 0.5 and 1 without a browser.

Sources for the teaching: University College Cork CS1101 Lecture 31 (English, read in full) for the
layout, the bias and the implied leading 1; Intel's IEEE 754 field documentation for the reserved
exponent fields; Zimmermann's IEEE 754 module for the extremal values.
