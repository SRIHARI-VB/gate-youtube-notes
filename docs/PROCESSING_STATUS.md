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

## Run 7 - source access for Matrices and Determinants

This topic used no playlist. What could be read, and what could not:

| Source | Route | Result |
| --- | --- | --- |
| IIT Madras CS6015 (LARP 2018) slide decks, 5 files | direct HTTPS from the sandbox | FULL: every page carries a text layer, all five decks read in full |
| GATE Overflow Linear Algebra notes | extraction service | PARTIAL: the matrix and determinant sections read |
| GeeksforGeeks GATE matrices and determinants notes | extraction service | PARTIAL: the types, operations, adjoint, inverse, trace, determinant and rank sections read |
| ashish singh lectures, Matrices and Determinants one-shot (Hindi) | search route | PARTIAL: the Hindi transcript was returned, and the opening (definition, types, operation laws) was read and translated |
| NPTEL IIT Roorkee Numerical Linear Algebra | extraction service | structure only: the lecture list; transcript PDFs returned 404 |
| IIT Kanpur MTH102 lecture notes (LA1 to LA18) | direct HTTPS | downloaded, but handwritten scans with an OCR-noise text layer, so unusable |
| Ankur Gupta GATE engineering-mathematics PDF | extraction service / direct | truncated extract only; the full PDF returned 502 through the egress proxy |
| Vidyalankar GATE mathematics notes PDF | direct HTTPS | 502 through the egress proxy |
| NPTEL IIT Kanpur Linear Algebra book | direct HTTPS | 404 for every path tried |
| Unacademy Hindi linear algebra series | extraction service | paywalled lesson pages, no transcript |
| English GATE linear-algebra lecture videos | extraction service | no caption track on any page tried |

The one change from runs 4 to 6 is the Hindi video: the search route returned its Hindi transcript, so this topic
contains the first translated material since the Monoids and Groups run. No English lecture transcript could be read.

## Run 10 - source access for the Mean Value Theorem

This topic used no playlist. What could be read, and what could not:

| Source | Route | Result |
| --- | --- | --- |
| OpenStax Calculus Volume 1, section 4.4 | extraction service | PARTIAL: the opening through the proof of the mean value theorem, including both worked Rolle examples and the |x| - 1 counterexample |
| Paul's Online Math Notes, Calculus I section 4.7 | extraction service | PARTIAL: the opening through the geometric interpretation, including the 4x^5 + x^3 + 7x - 2 root-counting example |
| Knowledge Gate, "13 Oct - EM - Calculus Part 3" (Hindi) | extraction service | SUMMARY_ONLY: the platform's published English AI chapter summary with all thirteen chapters read in full |
| MIT 18.01 Lecture 14 transcript | extraction service | PARTIAL, unusable for this topic: the readable part is the Newton's-method error analysis, and Lecture 15 opens by moving on from the mean value theorem |
| MIT 18.01 Lectures 13 and 15 transcripts | extraction service | read only to establish which lecture covers the theorem; 13 is related rates, 15 is differentials and integration |
| BYJU'S GATE mean value theorems (UawXU1TEI7o) | search route | no caption track, page boilerplate only |
| GATE Wallah Calculus Lec 3 (DWkkX25k5Mc) | search route | title only, no caption track |
| Unacademy Hindi MVT lesson (Sweta Kumari) | extraction service | description and lesson list only, video behind an account wall |
| GeeksforGeeks Rolle's theorem page | extraction service | readable, but stops at Rolle's theorem |
| MindSpan GATE DA/CS MVT quiz page | extraction service | readable, but a commercial quiz page with no source and no proof |
| GATE Overflow mean-value-theorem tag | extraction service | five questions, none of them a GATE CSE paper question |
| GateAI GATE CSE calculus PYQ index | extraction service | used as an index; it is what established that only two CSE questions turn on a mean value theorem |
| YouTube, every other lecture tried | search route | consent wall, no caption tracks |

The one change from the previous topic is that both English textbook sources arrived at all: the extraction
service returned them from the opening to the proof of the mean value theorem. Neither arrived complete, so
the corollary subsections are not quoted anywhere. The Hindi source is again a Knowledge Gate class read
through its published English AI summary.

## Run 13 - source access for Sequential Circuits

This topic used no playlist. What could be read, and what could not:

| Source | Route | Result |
| --- | --- | --- |
| IIT Bombay CS 226, Lecture 7 (Synchronous Sequential Logic) | extraction service | FULL: every slide's text, from the objectives to the synthesis procedure, including both latch tables, the three-latch D flip-flop, all four characteristic equations, the analysis example and the binary/Gray/one-hot table |
| Auburn ELEC 2200, Lecture 7 (Sequential Circuits, FSMs) | extraction service | FULL: the latch equation derived from its table, the Huffman model, the 9-to-4 reduction, both adjacency rules, the literal-cost comparison and the Mealy/Moore diagrams |
| KFUPM COE 202, Lecture 16 (Registers and Counters) | extraction service | FULL: registers and load, the four shift-register kinds, the universal register's control table, the ripple delay, the F/2 to F/16 table and the BCD reset |
| Wikipedia, Counter (digital) | extraction service | PARTIAL: characteristics, synchronous and asynchronous, binary, ring and Johnson sections |
| Wikipedia (Hindi), अनुक्रमिक लॉजिक | extraction service | FULL, translated: the sequential definition, the memory property and the Moore and Mealy definitions |
| Wikipedia (Hindi), फ्लिप-फ्लॉप | extraction service | FULL, translated: the four kinds, the T equation and the combined characteristic and excitation table |
| NPTEL noc25_cs67, Switching Circuits and Logic Design | extraction service | OUTLINE_ONLY: the week 7 to week 9 layout, which is what the subtopic enumeration was checked against |
| NPTEL Digital Electronic Circuits, digimat.in lecture PDFs | direct HTTP | 403 on every request, http and https, with and without a browser user agent - the same host that served four lectures in full to the previous run |
| YouTube, every lecture tried | search and direct routes | no caption track on any watch page |
| Knowledge Gate sequential MCQ blog | extraction service | readable, used as an index only; one year attribution is wrong (GATE IT 2005 Q.11 labelled as CSE) |
| GeeksforGeeks GATE digital-logic quiz pages | extraction service | readable, used to locate question years; strips the paper numbering and the figures |

The change from run 12 is that three English lecture decks arrived complete, so for the first time in
several runs a topic's teaching rests on text that was fully in front of the run rather than on an
opening excerpt. The cost is that no video was readable at all, and that the NPTEL transcript host which
carried the previous topic refused every request this time.
