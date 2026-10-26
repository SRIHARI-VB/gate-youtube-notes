# Processing status

Two playlists, both from GO Classes for GATE CS (instructor: Deepak Poonia). 31 videos, about 38 hours.

## Playlist 2 - Propositional Logic (17 videos, 13h 12m)

`PLIPZ2_p3RNHillKxh1_iFeZhy9MftHeWW`

| # | Video | Length | Transcript | Analysis |
| --- | --- | --- | --- | --- |
| 1 | Complete Summary Part 1 | 2h 35m | PARTIAL (opening) | analysed, opening only |
| 2 | Complete Summary Part 2 | 3h 03m | PARTIAL (opening) | analysed, opening only |
| 3 | Complete Summary Part 3 | 1h 49m | PARTIAL (Devanagari ASR, opening) | fragments only |
| 4 | GATE PYQs Part 1 | 1h 56m | PARTIAL (opening) | analysed, opening only |
| 5 | GATE PYQs Part 2 | 1h 31m | PARTIAL (opening) | analysed, opening only |
| 6 | GATE CSE 2006 - logical binary relation | 7m | PARTIAL (Devanagari ASR) | fragments only |
| 7 | GATE CSE 1991 Q.3(xii) | 27m | PARTIAL (opening) | analysed, opening only |
| 8 | GATE CSE 2015 Q28 - binary operator | 7m | PARTIAL (Devanagari ASR) | fragments only |
| 9 | Model in propositional logic | 31m | PARTIAL (opening) | analysed, opening only |
| 10 | Practice Q1 (Levin 0.2.7) | 40s | FULL | analysed |
| 11 | Practice Q1 solution | 12m | PARTIAL (Devanagari ASR, opening) | fragments only |
| 12 | Practice Q2 (Levin 0.2.8) | 33s | FULL | analysed |
| 13 | Practice Q2 solution | 12m | PARTIAL (opening) | analysed, opening only |
| 14 | Practice Q3 (Levin 0.2.11) | 41s | FULL | analysed |
| 15 | Practice Q3 solution | 26m | PARTIAL (opening) | analysed, opening only |
| 16 | Practice Q4 (Grimaldi) | 1m | PARTIAL (Devanagari ASR) | fragments only |
| 17 | Practice Q4 solution | 14m | PARTIAL (opening) | analysed, opening only |

## Playlist 1 - Combinatorics (14 videos, about 25 hours)

`PLIPZ2_p3RNHjlC6eceG_vWSu-oA6Dc6aX` - processed in the previous run; see the per-video
`transcript_status` and `coverage_note` under `content/playlists/go-classes-for-gate-cs/PLIPZ2_p3RNHjlC6eceG_vWSu-oA6Dc6aX/videos/`.

## Why partial

YouTube blocks caption requests from this build environment's IP ("sign in to confirm you're not a bot"), so captions
were retrieved through a page-fetch route instead. That route returns caption text through a document-extraction
service, which truncates long documents: English tracks arrived as roughly the first 5,000 characters, which is the
opening minutes of a two-to-three hour lecture. Short videos (under about ten minutes) therefore arrived complete;
long ones did not.

Four videos in this playlist have only a Hindi auto-generated caption track, written in Devanagari script. Those
tracks are noisy speech recognition of Hinglish and are not reliable enough to quote, so those videos carry a
fragments-only analysis and no formula is attributed to them.

## What this means for the notes

The topic structure is reliable: the instructor states it explicitly in the readable openings (propositions,
connectives, the by-case method, arguments, interpretation and models), and the playlist titles name the rest. Every
formula, equivalence, tautology and count published in the cards is recomputed from scratch by
`scripts/validate.py` (`check_logic`), and every PYQ answer is checked against an official key or a named published
solution. Anything that depended on a segment that was not readable is either omitted or named as a gap.
