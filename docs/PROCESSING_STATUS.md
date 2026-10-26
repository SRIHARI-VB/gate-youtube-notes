# Processing status

Playlist: `PLIPZ2_p3RNHjlC6eceG_vWSu-oA6Dc6aX` - GO Classes for GATE CS, Combinatorics.

Total duration: about 25 hours across 14 videos.

| # | Video | Length | Transcript | Analysis |
| --- | --- | --- | --- | --- |
| 1 | Part 1 - Basic Principles of Counting | 2h 54m | PARTIAL (opening) | analysed, opening only |
| 2 | Part 2 - Permutation & Combination | 3h 01m | PARTIAL (opening) | analysed, opening only |
| 3 | Practice - Full House in poker | 11m | PARTIAL (~2/3) | analysed |
| 4 | Practice - Permutation & Combination | 15m | PARTIAL (~2/3) | analysed |
| 5 | Part 3 - Binomial Theorem & Permutation with Repetition | 1h 49m | PARTIAL (opening) | analysed, opening only |
| 6 | Part 4 - DODB template | 1h 13m | PARTIAL (opening) | analysed, opening only |
| 7 | Part 5 - IODB | 3h 02m | PARTIAL (opening) | analysed, opening only |
| 8 | Part 6 - IODB template: multiset, integer composition | 2h 03m | PARTIAL (opening) | analysed, opening only |
| 9 | Part 7 - DOIB, IOIB | 1h 37m | PARTIAL (opening) | analysed, opening only |
| 10 | Part 8 - Inclusion-Exclusion | 1h 14m | PARTIAL (opening) | analysed, opening only |
| 11 | Part 9 - IEP applications: derangements, onto functions | 1h 50m | PARTIAL (opening) | analysed, opening only |
| 12 | GATE, CMI, ISI, NET PYQs | 2h 00m | PARTIAL (opening) | analysed, opening only |
| 13 | GATE, TIFR, CMI, ISI PYQs | 1h 42m | PARTIAL (opening) | analysed, opening only |
| 14 | Part 10 - Pigeonhole Principle | 2h 56m | PARTIAL (opening) | analysed, opening only |

## Why partial

YouTube's caption endpoints refused direct requests from this environment ("sign in to confirm you're not a bot"),
and the one transcript service that did respond returns a length-capped slice of each caption track. Repeated
requests for the same video return the same opening slice, so later portions were not recoverable.

## What this means for the notes

The topic structure (which the instructor states in the opening of Parts 1, 3, 4 and 10) is reliable. The formulas,
examples and traps in the notes were verified independently: every published number is recomputed by
`scripts/validate.py`, and PYQ answers are checked against official keys or named published solutions.
Anything that depended on a segment that was not readable is either omitted or marked as a gap
(`recurrences-and-compositions` is flagged as a playlist gap).
