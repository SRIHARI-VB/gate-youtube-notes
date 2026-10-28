# Processing status

Three playlists, all from GO Classes for GATE CS (instructor: Deepak Poonia). 39 videos, about 53 hours.

## Playlist 3 - First Order Logic (8 videos, 14h 49m)

`PLIPZ2_p3RNHidhFvyKH4U_VE1rFAyvG8U`

| # | Video | Length | Transcript | Analysis |
| --- | --- | --- | --- | --- |
| 1 | Complete Summary Part 1 | 2h 30m | PARTIAL (opening, 4,663 chars) | analysed, opening only |
| 2 | Practice Questions (standard resources) | 1h 56m | NONE - nothing retrievable | not analysed, title only |
| 3 | Complete Summary Part 2 | 3h 33m | PARTIAL (Devanagari ASR, opening, 4,663 chars) | analysed, opening only |
| 4 | GATE PYQs Part 1 | 1h 29m | PARTIAL (Devanagari ASR, opening, 4,670 chars) | analysed, opening only |
| 5 | GATE PYQs Part 2 | 2h 24m | PARTIAL (opening, 4,667 chars) | analysed, opening only |
| 6 | GATE CSE 2004 - some boys taller than all girls | 4m 45s | FULL (Devanagari ASR) | analysed |
| 7 | Mathematical Logic - GATE 2026 PYQs | 1h 06m | PARTIAL (opening, 4,687 chars) | analysed, opening only |
| 8 | Practice Questions (standard resources) | 1h 48m | PARTIAL (opening, 4,687 chars) | analysed, opening only |

Video 2 returned an empty page on every attempt, including an alternate transcript host, so it carries an
explicit `NONE` status and an empty concept list rather than a guess. Its topic mapping comes from its title alone.

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

YouTube blocks caption requests from this build environment's IP (an IP-blocked response from the caption API and
HTTP 403 from the player API on every player client tried), so captions were retrieved through a page-fetch route instead. That route returns caption text through a document-extraction
service, which truncates long documents: English tracks arrived as roughly the first 5,000 characters, which is the
opening minutes of a two-to-three hour lecture. Short videos (under about ten minutes) therefore arrived complete;
long ones did not.

Several videos have only a Hindi auto-generated caption track, written in Devanagari script. Those tracks are noisy
speech recognition of Hinglish and are not reliable enough to quote, so the meaning is translated and paraphrased in
the analysis, never quoted, and the status line of each such video says so.

## What this means for the notes

The topic structure is reliable: the instructor states it explicitly in the readable openings (propositions,
connectives, the by-case method, arguments, interpretation and models), and the playlist titles name the rest. Every
formula, equivalence, tautology and count published in the cards is recomputed from scratch by
`scripts/validate.py` (`check_logic` for propositional logic, `check_first_order` for first-order logic, which
enumerates every interpretation on domains of one to three elements), and every PYQ answer is checked against an
official key or a named published solution. Anything that depended on a segment that was not readable is either omitted or named as a gap.

## Run 4 - Sets, Relations, Functions (four sources, three read in full)

| Source | Channel | Length | Transcript | Analysis |
| --- | --- | --- | --- | --- |
| Lec 02 - Set identities, Cartesian product, relations and functions (`7djvJetFiSY`) | IIT lecture (NPTEL-style) | about 1h | FULL | analysed in full |
| Introduction to Set Theory (`tyDKR4FG3Yw`) | TrevTutor | 16m 38s | FULL | analysed in full |
| Injective, Surjective and Bijective Functions (`PpA4LWPh40M`) | TrevTutor | 15m 00s | FULL | analysed in full |
| Relations - GATE PYQs - Part 2 (`Z9khyLCt2-I`) | GO Classes for GATE CS | 1h 35m | PARTIAL (opening) | analysed, opening only |

Unlike runs 1 to 3, three of the four transcripts arrived complete: the page-fetch route returned whole
documents for these lectures, so nothing in those three cards depends on an unread segment. The long GO Classes
lecture still arrived as its opening only, which is why the counting question types it names are recorded and the
rest are not.

No Hindi-language source could be read: two candidates were searched for and only their playlist or lesson pages
were retrievable, so nothing is translated in this run and no card draws on a non-English source.
