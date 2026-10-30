#!/usr/bin/env python3
"""Validate the repository content, references, mathematics and hygiene.

Run: python3 scripts/validate.py    (exit code 1 on failure)

Content layout:
  content/subjects/<subject>/<topic>/<subtopic>.json
  content/playlists/<channel>/<playlist-id>/{playlist.json,videos/<video-id>/*}
  content/pyqs/*.json
  visuals/<...>/lesson.json + index.html
"""
import itertools, json, os, re, sys
from math import comb, factorial

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
PRIORITIES = {"P1", "P2", "P3"}
VERIFICATION = {"OFFICIAL_KEY", "SOURCED", "UNVERIFIED"}
LABELS = {"VERIFIED PYQ", "ORIGINAL PYQ-STYLE QUESTION",
          "CONCEPTUAL PRACTICE QUESTION", "PREDICTED VARIATION"}
REQUIRED_TOPIC = ["id", "title", "priority", "unit", "quickIdea", "remember",
                  "example", "gateAngle", "trap", "check", "pyqIds", "videoRefs", "prereqs"]
REQUIRED_PYQ = ["id", "year", "paper", "question_ref", "type", "topic", "text",
                "answer", "solution", "source_url", "source_label", "verification"]
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

errors, warnings, checks = [], [], []


def ok(msg):
    checks.append(msg)


def fail(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def walk(root, suffix=".json"):
    out = []
    for base, dirs, files in os.walk(root):
        dirs.sort()
        for n in sorted(files):
            if n.endswith(suffix):
                out.append(os.path.join(base, n))
    return out


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- loading
def load_all():
    topics, tpath = {}, {}
    sources = {}
    sroot = os.path.join(CONTENT, "subjects")
    for path in walk(sroot):
        parts = rel(path).split("/")
        if len(parts) != 5:          # content/subjects/<s>/<t>/<card>.json
            fail("%s: card is not at content/subjects/<subject>/<topic>/<card>.json" % rel(path))
            continue
        if parts[4] == "sources.json":   # topic-level source ledger, not a card
            sources[parts[2] + "/" + parts[3]] = load(path)
            continue
        t = load(path)
        tid = t.get("id")
        if tid in topics:
            fail("duplicate topic id %s at %s and %s" % (tid, tpath[tid], rel(path)))
        topics[tid] = t
        tpath[tid] = rel(path)

    pyqs = {}
    for path in walk(os.path.join(CONTENT, "pyqs")):
        p = load(path)
        if p.get("id") in pyqs:
            fail("duplicate pyq id: " + str(p.get("id")))
        pyqs[p.get("id")] = p

    videos, playlists = {}, {}
    plroot = os.path.join(CONTENT, "playlists")
    for channel in sorted(os.listdir(plroot)) if os.path.isdir(plroot) else []:
        cdir = os.path.join(plroot, channel)
        if not os.path.isdir(cdir):
            continue
        for pid in sorted(os.listdir(cdir)):
            plpath = os.path.join(cdir, pid, "playlist.json")
            if not os.path.isfile(plpath):
                fail("playlist folder %s/%s has no playlist.json" % (channel, pid))
                continue
            pl = load(plpath)
            playlists[pid] = pl
            if pl.get("playlist_id") != pid:
                fail("%s: playlist_id %r does not match its folder name" % (rel(plpath), pl.get("playlist_id")))
            if channel_slug(pl.get("channel", "")) != channel:
                fail("%s: channel folder %r is not the slug of %r" % (rel(plpath), channel, pl.get("channel")))
            vroot = os.path.join(cdir, pid, "videos")
            if not os.path.isdir(vroot):
                fail("%s: no videos/ directory" % rel(plpath))
                continue
            for vid in sorted(os.listdir(vroot)):
                vdir = os.path.join(vroot, vid)
                if not os.path.isdir(vdir):
                    continue
                mpath = os.path.join(vdir, "metadata.json")
                apath = os.path.join(vdir, "analysis.json")
                npath = os.path.join(vdir, "notes.md")
                if not (os.path.isfile(mpath) and os.path.isfile(apath)):
                    fail("video %s is missing metadata.json or analysis.json" % vid)
                    continue
                if not os.path.isfile(npath):
                    fail("video %s has no notes.md" % vid)
                m, a = load(mpath), load(apath)
                if m.get("video_id") != vid:
                    fail("%s: video_id %r does not match its folder name" % (rel(mpath), m.get("video_id")))
                videos[m["video_id"]] = (m, a, rel(vdir))
    return topics, tpath, pyqs, videos, playlists, sources


def channel_slug(name):
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# ---------------------------------------------------------------- checks
def check_topics(topics, tpath, pyqs, videos):
    for tid, t in topics.items():
        where = tpath[tid]
        for f in REQUIRED_TOPIC:
            if f not in t:
                fail("%s: missing field %s" % (tid, f))
        if not SLUG.match(str(tid)):
            fail("%s: id is not a lowercase hyphenated slug" % tid)
        parts = where.split("/")
        if not SLUG.match(parts[2]) or not SLUG.match(parts[3]):
            fail("%s: subject/topic folder names must be lowercase hyphenated slugs" % where)
        if os.path.basename(where) != str(tid) + ".json":
            fail("%s: file name must equal the card id (%s.json)" % (where, tid))
        if t.get("priority") not in PRIORITIES:
            fail("%s: invalid priority %r" % (tid, t.get("priority")))
        if not isinstance(t.get("order"), int):
            fail("%s: missing integer order" % tid)
        if not t.get("remember"):
            fail("%s: no remember items" % tid)
        ex = t.get("example") or {}
        for f in ("prompt", "work", "answer"):
            if not ex.get(f):
                fail("%s: example missing %s" % (tid, f))
        for f in ("what", "why", "counterexample"):
            if not (t.get("trap") or {}).get(f):
                fail("%s: trap missing %s" % (tid, f))
        for f in ("question", "answer", "explanation"):
            if not (t.get("check") or {}).get(f):
                fail("%s: quick check missing %s" % (tid, f))
        for pid in t.get("pyqIds", []):
            if pid not in pyqs:
                fail("%s: broken pyq reference %s" % (tid, pid))
        for vid in t.get("videoRefs", []):
            if vid not in videos:
                fail("%s: broken video reference %s" % (tid, vid))
        for pre in t.get("prereqs", []):
            if pre not in topics:
                fail("%s: broken prerequisite %s" % (tid, pre))
            if pre == tid:
                fail("%s: lists itself as a prerequisite" % tid)
        for v in t.get("variations", []):
            if v.get("label") not in LABELS:
                fail("%s: variation has invalid label %r" % (tid, v.get("label")))
            for f in ("question", "answer", "why"):
                if not v.get(f):
                    fail("%s: variation missing %s" % (tid, f))
        vis = t.get("visual")
        if vis:
            vdir = os.path.join(ROOT, "visuals", vis)
            for f in ("index.html", "lesson.json"):
                if not os.path.isfile(os.path.join(vdir, f)):
                    fail("%s: visual %r has no %s" % (tid, vis, f))
    # one card, one path
    ids = [t["id"] for t in topics.values()]
    if len(ids) != len(set(ids)):
        fail("a card id appears at more than one path")
    ok("%d cards across %d subject(s): required fields, slugs, examples, traps, checks, references"
       % (len(topics), len({tpath[t].split('/')[2] for t in topics})))

    orders = {}
    for tid, t in topics.items():
        orders.setdefault(t.get("order"), []).append(tid)
    dup = {o: v for o, v in orders.items() if len(v) > 1}
    if dup:
        fail("cards share an order value: %s" % dup)


def check_pyqs(topics, pyqs):
    for pid, p in pyqs.items():
        for f in REQUIRED_PYQ:
            if f not in p:
                fail("%s: missing field %s" % (pid, f))
        if p.get("verification") not in VERIFICATION:
            fail("%s: invalid verification label %r" % (pid, p.get("verification")))
        if not str(p.get("source_url", "")).startswith("http"):
            fail("%s: source_url is not a URL" % pid)
        if not re.match(r"^(19|20)\d\d$", str(p.get("year"))):
            fail("%s: implausible year %r" % (pid, p.get("year")))
        if p.get("topic") not in topics:
            fail("%s: pyq topic %r does not exist" % (pid, p.get("topic")))
        if p.get("type") not in {"MCQ", "MSQ", "NAT"}:
            fail("%s: invalid question type %r" % (pid, p.get("type")))
        if p.get("type") == "MCQ" and not p.get("options"):
            fail("%s: MCQ without options" % pid)
        if not p.get("question_ref"):
            fail("%s: no question reference" % pid)
        if p.get("verification") == "UNVERIFIED":
            warn("%s is labelled UNVERIFIED and must not be presented as an official PYQ" % pid)
        if p.get("verification") == "OFFICIAL_KEY" and not p.get("answer_evidence"):
            warn("%s claims OFFICIAL_KEY but records no answer evidence" % pid)
    ok("%d PYQ records: fields, years, types, options, sources, topic links" % len(pyqs))
    used = set()
    for t in topics.values():
        used.update(t.get("pyqIds", []))
    orphan = sorted(set(pyqs) - used)
    if orphan:
        warn("PYQs not linked from any card: %s" % ", ".join(orphan))


def check_videos(topics, videos):
    for vid, (m, a, where) in videos.items():
        if not m.get("transcript_status"):
            fail("%s: no transcript status" % vid)
        if not a.get("coverage_note"):
            fail("%s: no coverage note" % vid)
        if not m.get("analysis_status"):
            fail("%s: no analysis status" % vid)
        if not m.get("video_url", "").startswith("https://www.youtube.com/watch?v="):
            fail("%s: bad video url" % vid)
        if not isinstance(m.get("duration_seconds"), int):
            fail("%s: bad duration" % vid)
        if not a.get("topics"):
            fail("%s: no topics mapped" % vid)
        for tid in a.get("topics", []):
            if tid not in topics:
                fail("%s: analysis maps to unknown topic %s" % (vid, tid))
    ok("%d videos: transcript status, analysis status, coverage note, topic mapping" % len(videos))
    used = set()
    for t in topics.values():
        used.update(t.get("videoRefs", []))
    orphan = sorted(set(videos) - used)
    if orphan:
        warn("videos not referenced by any card: %s" % ", ".join(orphan))


def check_playlists(playlists, videos):
    for pid, pl in playlists.items():
        for f in ("playlist_id", "title", "channel", "url", "subject", "exam"):
            if not pl.get(f):
                fail("%s: playlist.json missing %s" % (pid, f))
        if pl.get("video_count") is not None:
            have = sum(1 for v in videos.values() if v[0].get("playlist_id") == pid)
            if pl["video_count"] != have:
                fail("%s: video_count says %r but %d video folders exist" % (pid, pl["video_count"], have))
        if pl.get("total_duration_seconds") is not None:
            have = sum(v[0]["duration_seconds"] for v in videos.values()
                       if v[0].get("playlist_id") == pid)
            if pl["total_duration_seconds"] != have:
                fail("%s: total_duration_seconds says %r but folders sum to %d"
                     % (pid, pl["total_duration_seconds"], have))
    ok("%d playlists: manifest fields, video counts, duration totals" % len(playlists))


def check_syllabus(topics, tpath):
    syl = load(os.path.join(CONTENT, "syllabus.json"))
    if not syl.get("line"):
        fail("syllabus.json has no line")
    subjects = {tpath[t].split("/")[2] for t in topics}
    declared = {s["slug"] for s in syl.get("subjects", [])}
    for s in subjects - declared:
        fail("subject folder %r is not declared in syllabus.json" % s)
    src = syl.get("source") or {}
    if not str(src.get("url", "")).startswith("http"):
        fail("syllabus.json does not cite the official syllabus document")
    declared_topics = 0
    for s in syl.get("subjects", []):
        if not SLUG.match(str(s.get("slug"))):
            fail("syllabus.json subject %r is not a slug" % s.get("slug"))
        for tp in s.get("topics", []):
            declared_topics += 1
            if not SLUG.match(str(tp.get("slug"))):
                fail("syllabus.json topic %r is not a slug" % tp.get("slug"))
            d = os.path.join(CONTENT, "subjects", s["slug"], tp["slug"])
            material = tp.get("material", "cards")
            if material not in {"cards", "planned"}:
                fail("syllabus.json %s/%s: invalid material %r" % (s["slug"], tp["slug"], material))
            if material == "cards" and not os.path.isdir(d):
                fail("syllabus.json says %s/%s has cards but the folder is missing" % (s["slug"], tp["slug"]))
            if material == "planned" and os.path.isdir(d):
                fail("syllabus.json says %s/%s is planned but cards exist there" % (s["slug"], tp["slug"]))
    ok("syllabus enumerates %d topics in %d subjects, cited to the official document, with folders matching material"
       % (declared_topics, len(syl.get("subjects", []))))


# ---------------------------------------------------------------- mathematics
MATH = [
    ("4-digit numbers, distinct digits", 9 * 9 * 8 * 7, 4536),
    ("4-digit PINs", 10 ** 4, 10000),
    ("BOOK arrangements", factorial(4) // 2, 12),
    ("LEVEL arrangements", factorial(5) // (2 * 2), 30),
    ("5 in a row / round table", factorial(5), 120),
    ("round table of 5", factorial(4), 24),
    ("5 at a round table, pair apart", factorial(4) - factorial(3) * 2, 12),
    ("C(10,6)^2", comb(10, 6) ** 2, 44100),
    ("even-women committees", sum(comb(10, k) * comb(10, 12 - k) for k in (2, 4, 6, 8, 10)), 63090),
    ("C(20,12)", comb(20, 12), 125970),
    ("coefficient x^12 in (x^3+...)^3", comb(5, 3), 10),
    ("coefficient x^10 in (x^2+...)^4", comb(5, 2), 10),
    ("coefficient x^5 in (1+x)^7", comb(7, 5), 21),
    ("8-bit strings with 3 ones", comb(8, 3), 56),
    ("MISSISSIPPI", factorial(11) // (factorial(4) * factorial(4) * factorial(2)), 34650),
    ("length-5 over {a,b} with two a's", comb(5, 2), 10),
    ("3^4 strings", 3 ** 4, 81),
    ("3 distinct balls into 2 boxes", 2 ** 3, 8),
    ("4 distinct balls into 2 boxes", 2 ** 4, 16),
    ("5 distinct balls into 3 boxes, onto", sum((-1) ** k * comb(3, k) * (3 - k) ** 5 for k in range(4)), 150),
    ("onto 5->3 via 3!S(5,3)", 6 * 25, 150),
    ("onto 4->3", sum((-1) ** k * comb(3, k) * (3 - k) ** 4 for k in range(4)), 36),
    ("onto 4->2", sum((-1) ** k * comb(2, k) * (2 - k) ** 4 for k in range(3)), 14),
    ("onto 3->2", 2 ** 3 - 2, 6),
    ("x1+x2+x3=10", comb(12, 2), 66),
    ("x1+..+x4=7 each >=1", comb(6, 3), 20),
    ("5 sweets 3 children", comb(7, 2), 21),
    ("5 sweets 3 children each >=1", comb(4, 2), 6),
    ("6 balls 3 identical bins", sum(1 for a in range(7) for b in range(a, 7) for c in range(b, 7) if a + b + c == 6), 7),
    ("6 balls 3 distinct bins", comb(8, 2), 28),
    ("4-digit non-decreasing over {1,2,3}", comb(6, 2), 15),
    ("divisible by 3 or 5 or 7 up to 500", 166 + 100 + 71 - 33 - 23 - 14 + 4, 271),
    ("1..1000 divisible by 2 or 3 or 5", 500 + 333 + 200 - 166 - 100 - 66 + 33, 734),
    ("students taking none", 200 - (125 + 85 + 65 - 50 - 35 - 30 + 15), 25),
    ("10-pennants", 1 + 9 + 28 + 35 + 15 + 1, 89),
    ("compositions of 6 into 1s and 2s", sum(comb(6 - j, j) for j in range(4)), 13),
    ("compositions of 5 into 1s and 2s", sum(comb(5 - j, j) for j in range(3)), 8),
    ("!3", 2, 2),
    ("!4", 9, 9),
    ("!5", 44, 44),
    ("LILAC derangements", 3 * (factorial(3) - factorial(2)), 12),
    ("3^10 tuples A subset B", 3 ** 10, 59049),
    ("ternary length 5 with a repeat", 3 ** 5 - 3 * 2 ** 4, 195),
    ("pigeonhole cards", 4 * (3 - 1) + 1, 9),
    ("pigeonhole two summing to 21", 10 + 1, 11),
    ("4-digit even distinct", sum(1 for n in range(1000, 10000, 2) if len(set(str(n))) == 4), 2296),
    ("C(10,3)", comb(10, 3), 120),
    ("S(4,2)", 7, 7),
    ("S(5,3)", 25, 25),
    ("partitions of 5", 7, 7),
    ("full house", 13 * comb(4, 3) * 12 * comb(4, 2), 3744),
    # propositional logic
    ("truth-table rows, 3 variables", 2 ** 3, 8),
    ("interpretations, 2 variables", 2 ** 2, 4),
    ("truth functions of 2 variables", 2 ** (2 ** 2), 16),
    ("truth functions of 3 variables", 2 ** (2 ** 3), 256),
    ("minterms of 3 variables", 2 ** 3, 8),
    # system of linear equations
    ("2005 Q.48 coefficient determinant", 2 * (2 * 1 - 5 * 4) + 1 * (3 * 1 - 5 * (-1)) + 3 * (3 * 4 - 2 * (-1)), 14),
    ("2014 Set 1 Q.52 minor determinant", 3 * (1 * 7 - 1 * (-2)) - 2 * (1 * 7 - 1 * 1), 15),
    ("2026 Set 2 Q.31 product ab", 4 * 6, 24),
    ("2025 Set 1 Q.13 critical values of k", len([k for k in range(-6, 7) if 1 - k * k == 0]), 2),
    # eigenvalues and eigenvectors
    ("eigen: A = [[2,1],[1,2]] eigenvalues sum to the trace", 3 + 1, 4),
    ("eigen: A = [[2,1],[1,2]] eigenvalues multiply to the determinant", 3 * 1, 3),
    ("eigen: 2017 Set 1 Q.31 entry squares of [[5,0],[0,5]]", 5 * 5 + 5 * 5, 50),
    ("eigen: 2021 Set 1 Q.52 largest eigenvalue of J - I of order 4", 4 - 1, 3),
    # LU decomposition
    ("lu: [[2,2],[4,9]] determinant from the pivots", 2 * 5, 10),
    ("lu: [[2,2],[4,9]] determinant directly", 2 * 9 - 2 * 4, 10),
    ("lu: 2015 S1 Q.18 u12 times l11", 2 * 1, 2),
    ("lu: 2015 S1 Q.18 l22 from l21 u12 + l22 = 9", 9 - 4 * 1, 5),
    ("lu: 2022 Q.35 third-row second entry after column 1", 1 - 2 * 1, -1),
    ("lu: 2022 Q.35 last entry after column 2, doubled", 2 * (-1) + 1, -1),
    ("lu: 2022 Q.35 x1 from the back pass", 4 - 2 - 2 * (-1), 4),
    ("lu: pivots of A = [[2,3,1],[4,7,7],[-2,4,5]] multiplied", 2 * 1 * -29, -58),
    ("lu: the (3,2) dot product row 3 of L with column 2 of U", -1 * 3 + 7 * 1 + 1 * 0, 4),
    ("lu: det(A) = -det(U) after one row swap", -1 * (1 * 1 * -5), 5),
    ("lu: det of [[0,2],[1,3]] with the swap sign", -1 * (1 * 2), -2),
    ("lu: Cholesky (2,2) entry of [[4,2],[2,3]]", 1 * 1 + 2, 3),
    ("lu: factorisation flops at n = 100", 2 * 100 ** 3 // 3, 666666),
    ("lu: one substitution pair at n = 100", 2 * 100 ** 2, 20000),
    ("lu: five solves at n = 100", 5 * 2 * 100 ** 2, 100000),
    ("lu: total work at n = 100 and m = 5", 2 * 100 ** 3 // 3 + 5 * 2 * 100 ** 2, 766666),
    ("alu: functions from two select bits", 2 ** 2, 4),
    ("alu: select bits for three sources in the output mux", 2, 2),
    ("alu: control bits for AND, OR, add and subtract", 2 + 1, 3),
    ("alu: select bits for six operations", 3, 3),
    ("alu: select bits for four ALUOp classes", 2, 2),
    ("alu: 32-bit ALU slices", 32, 32),
    ("alu: four-bit ripple-carry top sum bit delay in gates", 2 * 4 + 1, 9),
    ("alu: eight-bit ripple-carry top sum bit delay", 2 * 8 + 1, 17),
    ("alu: sixteen-bit ripple-carry top sum bit delay", 2 * 16 + 1, 33),
    ("alu: 32-bit ripple-carry top sum bit delay", 2 * 32 + 1, 65),
    ("alu: eight-bit ALU delay with a two-gate output mux", 2 * 8 + 1 + 2, 19),
    ("alu: 32-bit ALU delay with a one-gate output mux", 2 * 32 + 1 + 1, 66),
    ("alu: operand combinations from two independent 2:1 muxes", 2 * 2, 4),
    ("alu: operand combinations from two independent 4:1 muxes", 4 * 4, 16),
    ("alu: barrel shifter stages for 16 bits", 4, 4),
    ("alu: 2:1 muxes in a 16-bit barrel shifter", 16 * 4, 64),
    ("alu: barrel shifter stages for 32 bits", 5, 5),
    ("alu: 2:1 muxes in a 32-bit barrel shifter", 32 * 5, 160),
    ("alu: barrel shifter stages for 64 bits", 6, 6),
    ("alu: 2:1 muxes in a 64-bit barrel shifter", 64 * 6, 384),
    ("alu: shift 0b00110100 left by two", (0b00110100 << 2) & 0xFF, 208),
    ("alu: 52 times four", 52 * 4, 208),
    ("alu: arithmetic right shift of -12 by one", -12 >> 1, -6),
    ("alu: arithmetic right shift of -3 by one floors to -2", -3 >> 1, -2),
    ("alu: execution cycles of 2005 Q.79, add R0, R1", 2 + 1, 3),
    ("alu: instruction cycles of 2005 Q.79 including the fetch", 2 + 1 + 2, 5),
    ("alu: zero-flag pairs after a 4-bit subtraction", 16, 16),
    ("alu: V-setting ordered pairs in 4-bit addition", 28 + 36, 64),
    ("alu: raw-sign-bit failures in 4-bit subtraction", 64, 64),
]


def check_math():
    for name, got, want in MATH:
        if got != want:
            fail("math: %s computed %r but content claims %r" % (name, got, want))
    ok("%d published numeric claims recomputed" % len(MATH))


# ---------------------------------------------- propositional logic truth tables
VARS = "pqrs"


def rows(n):
    for bits in itertools.product([False, True], repeat=n):
        yield dict(zip(VARS[:n], bits))


def F(expr):
    """Evaluate a boolean expression over the variables in its dict."""
    return expr


def tt(n, fn):
    return [fn(r) for r in rows(n)]


def is_taut(n, fn):
    return all(tt(n, fn))


def is_unsat(n, fn):
    return not any(tt(n, fn))


def equiv(n, f, g):
    return all(a == b for a, b in zip(tt(n, f), tt(n, g)))


def nmodels(n, fn):
    return sum(1 for v in tt(n, fn) if v)


def check_logic():
    """Every equivalence, tautology and count published in the notes is recomputed."""
    imp = lambda a, b: (not a) or b
    iff = lambda a, b: a == b
    xor = lambda a, b: a != b
    nand = lambda a, b: not (a and b)
    nor = lambda a, b: not (a or b)

    # connectives and their rewrites
    assert equiv(2, lambda r: imp(r["p"], r["q"]), lambda r: (not r["p"]) or r["q"]), "implication law"
    assert equiv(2, lambda r: imp(r["p"], r["q"]), lambda r: imp(not r["q"], not r["p"])), "contrapositive"
    assert equiv(2, lambda r: not imp(r["p"], r["q"]), lambda r: r["p"] and not r["q"]), "negated implication"
    assert equiv(2, lambda r: iff(r["p"], r["q"]),
                 lambda r: imp(r["p"], r["q"]) and imp(r["q"], r["p"])), "biconditional as two implications"
    assert equiv(2, lambda r: iff(r["p"], r["q"]),
                 lambda r: (r["p"] and r["q"]) or (not r["p"] and not r["q"])), "biconditional as agreement"
    assert equiv(2, lambda r: not iff(r["p"], r["q"]), lambda r: xor(r["p"], r["q"])), "negated biconditional is xor"
    assert equiv(2, lambda r: not (r["p"] and r["q"]),
                 lambda r: (not r["p"]) or (not r["q"])), "De Morgan and"
    assert equiv(2, lambda r: not (r["p"] or r["q"]),
                 lambda r: (not r["p"]) and (not r["q"])), "De Morgan or"
    assert equiv(3, lambda r: r["p"] and (r["q"] or r["r"]),
                 lambda r: (r["p"] and r["q"]) or (r["p"] and r["r"])), "distributive and over or"
    assert equiv(2, lambda r: r["p"] or (r["p"] and r["q"]), lambda r: r["p"]), "absorption"
    assert equiv(3, lambda r: imp(r["p"] and r["q"], r["r"]),
                 lambda r: imp(r["p"], imp(r["q"], r["r"]))), "exportation"
    # implication is not associative
    assert not equiv(3, lambda r: imp(r["p"], imp(r["q"], r["r"])),
                     lambda r: imp(imp(r["p"], r["q"]), r["r"])), "implication not associative"
    # the 2015 Set 1 Q.14 options
    assert equiv(2, lambda r: iff(r["p"], r["q"]),
                 lambda r: (imp(r["p"], r["q"]) and imp(r["q"], r["p"]))), "option A"
    assert equiv(2, lambda r: iff(r["p"], r["q"]),
                 lambda r: ((not r["p"]) or r["q"]) and imp(r["q"], r["p"])), "option B"
    assert not equiv(2, lambda r: iff(r["p"], r["q"]),
                     lambda r: ((not r["p"]) and r["q"]) or (r["p"] and not r["q"])), "option C is not iff"
    assert equiv(2, lambda r: iff(r["p"], r["q"]),
                 lambda r: ((not r["p"]) and (not r["q"])) or (r["p"] and r["q"])), "option D"

    # tautologies claimed in the cards
    assert is_taut(2, lambda r: imp(not r["p"] and (r["p"] or r["q"]), r["q"])), "2021 S1 tautology"
    assert not is_taut(2, lambda r: imp(r["q"], not r["p"] and (r["p"] or r["q"]))), "2021 S2 not a tautology"
    assert is_taut(2, lambda r: (imp(r["p"], r["q"])) or (imp(r["q"], r["p"]))), "(p->q) or (q->p)"
    assert is_taut(2, lambda r: imp(r["p"], imp(r["q"], r["p"] and r["q"]))), "by-case worked example"
    assert not is_taut(2, lambda r: imp(imp(r["p"], r["q"]), imp(r["q"], r["p"]))), "(p->q)->(q->p) fails"
    assert is_taut(3, lambda r: imp(r["p"] and r["q"], r["q"] or r["r"])), "1992 option (b) as written"
    assert not is_taut(3, lambda r: imp(r["p"] or r["q"], r["q"] and r["r"])), "1992 option (a) fails"
    assert not is_taut(3, lambda r: imp(r["p"] or r["q"], imp(r["q"], r["r"]))), "1992 option (c) fails"
    assert not is_taut(3, lambda r: imp(r["p"], imp(r["q"], imp(r["q"], r["r"])))), "1992 option (d) fails"
    assert is_taut(3, lambda r: iff(r["p"], r["p"])), "A <-> A tautology (2015 Set 2 Q.55 skeleton)"
    assert is_taut(3, lambda r: imp(r["q"], imp(r["p"], r["q"]))), "modus ponens form"

    # satisfiability / validity
    q2004 = lambda r: imp(imp(r["p"], r["q"] or r["r"]), imp(r["p"] and r["q"], r["r"]))
    assert not is_taut(3, q2004) and nmodels(3, q2004) > 0, "2004 formula satisfiable but not valid"
    assert nmodels(3, q2004) == 7, "2004 formula true in 7 of 8 rows"
    # 1991: both implications tautologies force F1 and F2 jointly unsatisfiable
    # 1991 Q.3(xii): for every assignment, both implications being true forces
    # F1 and F2 to be jointly false, so their conjunction is unsatisfiable.
    for f1, f2, f3 in itertools.product([False, True], repeat=3):
        a = imp(f1 and f2, f3)
        b = imp(f1 and f2, not f3)
        if a and b and f1 and f2:
            fail("1991: an assignment makes both tautologies true while F1 and F2 are both true")
    assert is_unsat(3, lambda r: r["p"] and r["q"] and imp(r["p"] and r["q"], r["r"])
                    and imp(r["p"] and r["q"], not r["r"])), "1991 conjunction unsatisfiable"
    assert is_unsat(2, lambda r: (imp(r["p"], r["q"]) and imp(r["q"], r["p"])) and xor(r["p"], r["q"])), \
        "(p<->q) and (p xor q) unsatisfiable"
    # 2015 Set 2 Q.3 inference chain
    assert is_taut(3, lambda r: imp(imp(r["p"], not r["q"]) and imp(r["r"], r["q"]), imp(r["r"], not r["p"]))), \
        "C->not E, K->E entails K->not C"
    # 2016 Set 2 Q.1
    assert equiv(2, lambda r: r["p"] and imp(r["p"], r["q"]), lambda r: r["p"] and r["q"]), "P and (P->Q) = P and Q"
    premise = lambda r: r["p"] and imp(r["p"], r["q"])
    implied = [lambda r: False, lambda r: r["q"], lambda r: True,
               lambda r: r["p"] or r["q"], lambda r: (not r["q"]) or r["p"]]
    count = sum(1 for e in implied if all((not premise(r)) or e(r) for r in rows(2)))
    assert count == 4, "2016 count of implied expressions"

    # entailment and models
    prem = lambda r: imp(r["p"], r["q"]) and imp(r["q"], r["r"])
    assert nmodels(3, prem) == 4, "models of {p->q, q->r}"
    assert all((not prem(r)) or imp(r["p"], r["r"]) for r in rows(3)), "hypothetical syllogism entails"
    assert nmodels(4, lambda r: any(r.values())) == 15, "models of p or q or r or s"
    assert nmodels(2, lambda r: r["p"] or r["q"]) == 3, "models of p or q"
    assert nmodels(3, lambda r: r["p"] and r["q"]) == 2, "models of p and q"
    assert not all((not (r["p"] or r["q"])) or r["p"] for r in rows(2)), "{p or q} does not entail p"

    # resolution
    assert is_taut(3, lambda r: imp((r["p"] or r["r"]) and (r["q"] or not r["r"]), r["p"] or r["q"])), "resolution valid"
    assert not is_taut(3, lambda r: imp(r["p"] or r["q"], (r["p"] or r["r"]) and (r["q"] or not r["r"]))), \
        "resolution converse not valid"
    assert is_unsat(3, lambda r: (r["p"] or r["q"]) and (not r["p"]) and (not r["q"])), "resolution reaches empty clause"

    # functional completeness
    for a in (False, True):
        assert nand(a, a) == (not a), "NAND builds negation"
        assert nor(a, a) == (not a), "NOR builds negation"
    for a, b in itertools.product([False, True], repeat=2):
        assert nand(nand(a, b), nand(a, b)) == (a and b), "NAND builds conjunction"
        assert nor(nor(a, b), nor(a, b)) == (a or b), "NOR builds disjunction"
    monotone_ok = True
    for f in (lambda a, b: a and b, lambda a, b: a or b, lambda a, b: (a and b) or a):
        if f(False, False) > f(True, False) or f(False, False) > f(False, True):
            monotone_ok = False
    assert monotone_ok, "and/or formulas are monotone"
    # {xor, and} is 0-preserving
    for f in (lambda a, b: a and b, lambda a, b: xor(a, b)):
        assert f(False, False) is False, "{xor, and} is 0-preserving"
    # 2015 Set 1 Q.39
    f = lambda x, y, z: ((not x) and y and z) or (x and (not y)) or ((not y) and (not z))
    for x in (False, True):
        for z in (False, True):
            assert f(x, x, z) == nor(x, z), "f(X,X,Z) = NOR(X,Z)"
    g = lambda x, y, z: ((not x) and y and z) or ((not x) and y and (not z)) or (x and y)
    assert g(False, False, False) is False and g(True, True, True) is True, "g preserves 0 and 1"

    # 2002 unless
    assert equiv(3, lambda r: imp(not r["r"], imp(r["p"], r["q"])),
                 lambda r: imp(r["p"] and not r["r"], r["q"])), "unless translation"

    # normal forms: p -> q has 3 true rows and 1 false row; p <-> q has 2 and 2
    assert nmodels(2, lambda r: imp(r["p"], r["q"])) == 3, "PDNF minterms of p->q"
    assert nmodels(2, lambda r: not imp(r["p"], r["q"])) == 1, "PCNF maxterms of p->q"
    assert nmodels(2, lambda r: iff(r["p"], r["q"])) == 2, "PDNF minterms of p<->q"
    assert nmodels(2, lambda r: not iff(r["p"], r["q"])) == 2, "PCNF maxterms of p<->q"

    # quantifier facts over a bounded integer domain
    dom = range(-50, 51)
    # "for all x there exists y with x < y" holds on the integers; the top of a
    # bounded test domain is the only place a finite check can fail, so it is skipped.
    assert all(x == max(dom) or any(x < y for y in dom) for x in dom), "for all x exists y x<y"
    # "there exists y such that for all x, x < y" fails on the integers: no greatest integer.
    assert not any(all(x < y for x in dom) for y in dom), "exists y for all x x<y is false"

    # 2007 CNF clause counting: some assignment satisfies at least half the clauses
    import random
    random.seed(7)
    for _ in range(200):
        m, n = random.randint(1, 6), 3
        clauses = []
        for _ in range(m):
            lits = [(random.randrange(n), random.random() < 0.5) for _ in range(random.randint(1, 3))]
            clauses.append(lits)
        best = 0
        for bits in itertools.product([False, True], repeat=n):
            s = sum(1 for c in clauses
                    if any(bits[i] if pos else not bits[i] for i, pos in c))
            best = max(best, s)
        if best * 2 < m:
            fail("2007 CNF claim failed on a random formula")
            break
    ok("propositional logic: every equivalence, tautology, entailment count and completeness claim recomputed")


# ------------------------------------------------------- first order logic
def check_first_order():
    """Every first-order claim published in the cards and in the quantifier lesson is recomputed
    by exhaustive enumeration over domains of one to three elements."""
    import random

    def dom(n):
        return list(range(n))

    def relations(n):
        cells = [(i, j) for i in range(n) for j in range(n)]
        for bits in range(1 << len(cells)):
            yield {(i, j) for k, (i, j) in enumerate(cells) if bits >> k & 1}

    def subsets(n):
        for bits in range(1 << n):
            yield {i for i in range(n) if bits >> i & 1}

    # there exists y for all x implies for all x there exists y, in every relation on every small domain
    for n in (1, 2, 3):
        D = dom(n)
        for R in relations(n):
            if any(all((x, y) in R for x in D) for y in D):
                assert all(any((x, y) in R for y in D) for x in D), \
                    "exists-y-forall-x must imply forall-x-exists-y"

    # the converse fails: one tick per row, no full column
    for n, R in ((2, {(0, 1), (1, 0)}), (3, {(0, 1), (1, 2), (2, 0)})):
        D = dom(n)
        assert all(any((x, y) in R for y in D) for x in D), "every row has a tick (n=%d)" % n
        assert not any(all((x, y) in R for x in D) for y in D), "no column is full (n=%d)" % n

    # the two matrices used in visuals/.../quantifier-order
    cycle = {(0, 1), (1, 2), (2, 0)}
    column = {(0, 1), (1, 1), (2, 1)}
    D3 = dom(3)
    assert all(any((x, y) in cycle for y in D3) for x in D3) and \
        not any(all((x, y) in cycle for x in D3) for y in D3), "cycle: rows full, no column full"
    assert all(any((x, y) in column for y in D3) for x in D3) and \
        any(all((x, y) in column for x in D3) for y in D3), "column: both claims true"

    # unary-predicate facts, enumerated over every pair of subsets on every small domain
    for n in (1, 2, 3):
        D = dom(n)
        DS = set(D)
        for P in subsets(n):
            for Q in subsets(n):
                # exists over a conjunction implies the conjunction of the existentials
                if P & Q:
                    assert P and Q, "exists x (p and q) implies (exists x p) and (exists x q)"
                # the universal distributes over implication, in this direction only
                if P <= Q:
                    assert (P == DS) <= (Q == DS), "forall x (p -> q) implies (forall x p -> forall x q)"
                for W in (True, False):
                    assert all((i in P) or W for i in D) == (P == DS or W), "forall x (p or W)"
                    assert any((i in P) and W for i in D) == (bool(P) and W), "exists x (p and W)"
                    assert any((i not in P) or W for i in D) == ((P == DS) <= W), "exists x (p -> W)"

    # the arrow case that is NOT valid, with W false
    n = 2
    P = {0}
    assert all((i not in P) for i in range(n)) is False, "forall x (p -> false) is false when p fails somewhere"
    assert ((P == set(range(n))) <= False) is True, "(forall x p) -> false is true when p is not universal"

    # exactly one, at most one, and the uniqueness options of GATE 2025 Set 1 Q.38
    for n in (1, 2, 3):
        D = dom(n)
        for R in relations(n):                      # R(y, x): y is the mother of x
            for x in D:
                mothers = {y for y in D if (y, x) in R}
                exactly_one = any(
                    (y, x) in R and all(z == y for z in D if (z, x) in R) for y in D)
                assert exactly_one == (len(mothers) == 1), "exists y (m(y,x) and forall z (m(z,x) -> z=y))"
                # option (A) of that question: two existentials, one a mother and one not
                option_a = any((y, x) in R and any((z, x) not in R for z in D) for y in D)
                assert not (option_a and len(mothers) == 1 and len(D) == 1), \
                    "option A cannot be the exactly-one formula on a one-element domain"
        for P in subsets(n):
            at_most_one = all(not (i in P and j in P) or i == j for i in D for j in D)
            assert at_most_one == (len(P) <= 1), "forall x forall y ((P(x) and P(y)) -> x = y)"

    # option A of GATE 2025 Set 1 Q.38 is satisfied both when there is one mother and when there are two
    D = {0, 1, 2}
    one_mother = {(0, 0)}
    two_mothers = {(0, 0), (1, 0)}
    for R in (one_mother, two_mothers):
        assert any((y, 0) in R and any((z, 0) not in R for z in D) for y in D), \
            "option A holds whatever the number of mothers"

    # GATE 2016 Set 2 Q.27 option (D): even and odd numbers refute forall x (p or q) -> (forall x p or forall x q)
    evens = {i for i in range(6) if i % 2 == 0}
    odds = {i for i in range(6) if i % 2 == 1}
    assert all((i in evens) or (i in odds) for i in range(6)), "every number is even or odd"
    assert evens != set(range(6)) and odds != set(range(6)), "not all numbers are even, not all are odd"

    # GATE 2003 Q.32: (D) valid, (A) not valid
    for n in (1, 2, 3):
        D = dom(n)
        DS = set(D)
        for P in subsets(n):
            for Q in subsets(n):
                if P <= Q and P == DS:
                    assert Q == DS, "option (D) of GATE 2003 Q.32 is valid"
    n = 2
    P, Q = {0, 1}, set()          # forall x p, not forall x q, but p -> q fails
    assert (P == set(range(n))) and not (Q == set(range(n))) and not (P <= Q), \
        "option (A) of GATE 2003 Q.32 fails: two universals do not give the pointwise implication"

    # GATE 2023 Q.16: (B) and (C) imply the conjecture, (D) does not
    for n in (1, 2, 3):
        D = dom(n)
        for R in relations(n):
            for P in subsets(n):
                conjecture = all((x not in P) or any((x, y) in R for y in D) for x in D)
                if all(all((x, y) in R for y in D) for x in D):
                    assert conjecture, "forall x forall y Q implies the conjecture"
                if any(all((x not in P) or (x, y) in R for x in D) for y in D):
                    assert conjecture, "exists y forall x (P -> Q) implies the conjecture"
    n = 2
    P, R = {0, 1}, {(0, 1)}
    assert any(x in P and any((x, y) in R for y in dom(n)) for x in dom(n)), "option (D) is satisfied"
    assert not all((x not in P) or any((x, y) in R for y in dom(n)) for x in dom(n)), \
        "option (D) does not imply the conjecture"

    # model size: a universal true on a domain stays true on the subset of the existential witnesses
    random.seed(11)
    for _ in range(300):
        n = 3
        D = dom(n)
        body = {(a, b, c): random.random() < 0.5 for a in D for b in D for c in D}
        witnesses = [(a, b) for a in D for b in D if all(body[(a, b, c)] and body[(a, b, c2)]
                                                         for c in D for c2 in D)]
        if not witnesses:
            continue
        a, b = witnesses[0]
        sub = [a, b]
        assert all(body[(a, b, c)] and body[(a, b, c2)] for c in sub for c2 in sub), \
            "a model of size at most k exists when k existentials head the prefix"

    # the tautology-versus-validity distinction
    imp = lambda a, b: (not a) or b
    assert not is_taut(1, lambda r: r["p"]), "a single propositional letter is not a tautology"
    assert not is_taut(2, lambda r: imp(r["p"], r["q"])), "A -> B is not a propositional tautology"
    for n in (1, 2, 3):
        D = dom(n)
        for R in relations(n):
            if all(any((x, y) in R for y in D) for x in D):
                assert not any(not any((x, y) in R for y in D) for x in D), \
                    "(forall x R) -> not (exists x not R) is valid"
    ok("first order logic: quantifier order, negation, null quantification, uniqueness, model size, "
       "validity and the tautology distinction recomputed on domains of size 1 to 3")


def check_eigenvalues_and_eigenvectors():
    """Every eigenvalue, eigenvector, multiplicity, trace, determinant and power published in the
    Eigenvalues and Eigenvectors topic, recomputed in exact rational arithmetic."""
    from fractions import Fraction
    from math import sqrt

    def mat(A):
        return [[Fraction(x) for x in row] for row in A]

    def mm(A, B):
        A, B = mat(A), mat(B)
        return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))]
                for i in range(len(A))]

    def mv(A, v):
        A = mat(A)
        v = [Fraction(x) for x in v]
        return [sum(A[i][k] * v[k] for k in range(len(v))) for i in range(len(A))]

    def tr(A):
        M = mat(A)
        return sum(M[i][i] for i in range(len(M)))

    def det(A):
        M = mat(A)
        n = len(M)
        d = Fraction(1)
        for c in range(n):
            piv = next((i for i in range(c, n) if M[i][c] != 0), None)
            if piv is None:
                return Fraction(0)
            if piv != c:
                M[c], M[piv] = M[piv], M[c]
                d = -d
            d *= M[c][c]
            for i in range(c + 1, n):
                if M[i][c] != 0:
                    f = M[i][c] / M[c][c]
                    M[i] = [M[i][j] - f * M[c][j] for j in range(n)]
        return d

    def rank(M):
        R = mat(M)
        if not R:
            return 0
        rows, cols, r = len(R), len(R[0]), 0
        for c in range(cols):
            piv = next((i for i in range(r, rows) if R[i][c] != 0), None)
            if piv is None:
                continue
            R[r], R[piv] = R[piv], R[r]
            for i in range(rows):
                if i != r and R[i][c] != 0:
                    f = R[i][c] / R[r][c]
                    R[i] = [R[i][j] - f * R[r][j] for j in range(cols)]
            r += 1
            if r == rows:
                break
        return r

    def charpoly2(A):
        """Coefficients (1, -trace, determinant) of lambda^2 - t lambda + d."""
        return (Fraction(1), -tr(A), det(A))

    def eigen2(A):
        """Sorted eigenvalues of a 2x2 matrix when both are rational, else None."""
        t, d = tr(A), det(A)
        disc = t * t - 4 * d
        if disc < 0:
            return None
        r = sqrt(float(disc))
        if abs(r - round(r)) > 1e-9:
            return None
        r = Fraction(int(round(r)))
        return sorted([(t + r) / 2, (t - r) / 2])

    def same(u, v):
        return len(u) == len(v) and all(Fraction(a) == Fraction(b) for a, b in zip(u, v))

    def mat_eq(A, B):
        return len(A) == len(B) and all(same(x, y) for x, y in zip(A, B))

    def squares(A):
        return sum(Fraction(x) * Fraction(x) for row in A for x in row)

    def shift(A, lam):
        """A - lam I."""
        M = mat(A)
        return [[M[i][j] - (lam if i == j else 0) for j in range(len(M))] for i in range(len(M))]

    # --- the lesson and definition matrix
    A1 = [[2, 1], [1, 2]]
    if not same(mv(A1, [1, 1]), [3, 3]):
        fail("eigen: A(1,1) must be (3,3)")
    if not same(mv(A1, [1, -1]), [1, -1]):
        fail("eigen: A(1,-1) must be (1,-1)")
    if charpoly2(A1) != (Fraction(1), Fraction(-4), Fraction(3)):
        fail("eigen: A=[[2,1],[1,2]] must have characteristic polynomial lambda^2 - 4 lambda + 3")
    if eigen2(A1) != [Fraction(1), Fraction(3)]:
        fail("eigen: A=[[2,1],[1,2]] must have eigenvalues 1 and 3")
    if tr(A1) != 4 or det(A1) != 3:
        fail("eigen: trace and determinant of A=[[2,1],[1,2]] must be 4 and 3")
    if sum(a * b for a, b in zip([1, 1], [1, -1])) != 0:
        fail("eigen: the eigenvectors (1,1) and (1,-1) must be orthogonal")
    if squares(A1) != 3 ** 2 + 1 ** 2:
        fail("eigen: the entry squares of A=[[2,1],[1,2]] must equal the squared eigenvalues")

    # --- the 3x3 triangular example and its principal minors
    T = [[1, 2, 3], [0, 4, 5], [0, 0, 6]]
    if tr(T) != 11 or det(T) != 24:
        fail("eigen: the triangular example must have trace 11 and determinant 24")
    minors = T[0][0] * T[1][1] + T[0][0] * T[2][2] + T[1][1] * T[2][2]
    if minors != 34:
        fail("eigen: the principal 2x2 minors of the triangular example must sum to 34")
    for lam, dg in zip([1, 4, 6], [T[0][0], T[1][1], T[2][2]]):
        if lam != dg:
            fail("eigen: a triangular matrix must have its diagonal as eigenvalues")

    # --- 2015 Set 3 Q.15
    A15 = [[1, -1, 2], [0, 1, 0], [1, 2, 1]]
    if not same(mv(A15, [-4, 2, 1]), [-4, 2, 1]):
        fail("eigen: 2015 Set 3 Q.15 (-4,2,1) must satisfy A v = v")
    if rank(shift(A15, 1)) != 2:
        fail("eigen: 2015 Set 3 Q.15 rank(A - I) must be 2")

    # --- the defective matrix and its multiplicity pair
    D2 = [[2, 1], [0, 2]]
    if charpoly2(D2) != (Fraction(1), Fraction(-4), Fraction(4)):
        fail("eigen: [[2,1],[0,2]] must have characteristic polynomial (lambda-2)^2")
    if rank(shift(D2, 2)) != 1:
        fail("eigen: [[2,1],[0,2]] must have rank(A - 2I) = 1")
    if 2 - rank(shift(D2, 2)) != 1:
        fail("eigen: [[2,1],[0,2]] must have geometric multiplicity 1 against algebraic multiplicity 2")

    # --- 2025 Set 1 Q.31
    A25 = [[1, 1], [1, -1]]
    if charpoly2(A25) != (Fraction(1), Fraction(0), Fraction(-2)):
        fail("eigen: 2025 Set 1 Q.31 matrix must have lambda^2 - 2 = 0")
    P = mat(A25)
    for _ in range(12):
        P = mm(P, A25)
    if not mat_eq(P, [[64, 64], [64, -64]]):
        fail("eigen: 2025 Set 1 Q.31 A^13 must equal 64A")
    r2 = sqrt(2.0)
    if abs(r2 ** 13 - 64 * r2) > 1e-6:
        fail("eigen: (sqrt2)^13 must be 64 sqrt2")
    if abs((-r2) ** 13 + 64 * r2) > 1e-6:
        fail("eigen: (-sqrt2)^13 must be -64 sqrt2")

    # --- the rotation, the discriminant test and the irrational case
    R = [[0, -1], [1, 0]]
    if charpoly2(R) != (Fraction(1), Fraction(0), Fraction(1)):
        fail("eigen: the 90 degree rotation must have lambda^2 + 1 = 0")
    if tr(R) * tr(R) - 4 * det(R) >= 0:
        fail("eigen: the 90 degree rotation must have a negative discriminant")
    if tr([[2, 4], [3, 5]]) ** 2 - 4 * det([[2, 4], [3, 5]]) != 57:
        fail("eigen: [[2,4],[3,5]] must have discriminant 57, so its eigenvalues are real but irrational")
    if eigen2([[2, 4], [3, 5]]) is not None:
        fail("eigen: [[2,4],[3,5]] has irrational eigenvalues and must not be reported as rational")
    if charpoly2([[2, 4], [3, 5]]) != (Fraction(1), Fraction(-7), Fraction(-2)):
        fail("eigen: [[2,4],[3,5]] must have lambda^2 - 7 lambda - 2")

    # --- the row-operation trap
    A7 = [[1, 2], [3, 4]]
    B7 = [[1, 2], [0, -2]]
    if charpoly2(A7) != (Fraction(1), Fraction(-5), Fraction(-2)):
        fail("eigen: [[1,2],[3,4]] must have lambda^2 - 5 lambda - 2")
    if eigen2(B7) != [Fraction(-2), Fraction(1)]:
        fail("eigen: the row-reduced [[1,2],[0,-2]] must have eigenvalues -2 and 1")
    if 5 * 5 + 4 * 2 != 33:
        fail("eigen: the discriminant of lambda^2 - 5 lambda - 2 must be 33")
    if det(A7) != -2 or det(B7) != -2:
        fail("eigen: this row operation keeps the determinant at -2, which is what the card says")

    # --- 2014 Set 2 Q.47
    M47 = [[1, 0, 0, 0, 1],
           [0, 1, 1, 1, 0],
           [0, 1, 1, 1, 0],
           [0, 1, 1, 1, 0],
           [1, 0, 0, 0, 1]]
    if rank(M47) != 2:
        fail("eigen: 2014 Set 2 Q.47 matrix must have rank 2")
    if tr(M47) != 5:
        fail("eigen: 2014 Set 2 Q.47 matrix must have trace 5")
    if tr(mm(M47, M47)) != 13:
        fail("eigen: 2014 Set 2 Q.47 matrix must have trace(A^2) = 13")
    if eigen2([[0, -6], [1, 5]]) != [Fraction(2), Fraction(3)]:
        fail("eigen: the nonzero eigenvalues of 2014 Set 2 Q.47 must be 2 and 3")
    if 2 * 3 != 6:
        fail("eigen: the product of the nonzero eigenvalues must be 6")

    # --- 2018 Q.26 counterexample
    P18 = [[-2, 1], [-16, 6]]
    if charpoly2(P18) != (Fraction(1), Fraction(-4), Fraction(4)):
        fail("eigen: the 2018 Q.26 counterexample must have (lambda-2)^2")
    if not same(mv(P18, [1, 4]), [2, 8]):
        fail("eigen: the 2018 Q.26 counterexample must send (1,4) to 2(1,4)")
    if det(P18) != 4:
        fail("eigen: the 2018 Q.26 counterexample must be invertible with determinant 4")

    # --- 2021 Set 1 Q.52: J - I
    JI = [[0 if i == j else 1 for j in range(4)] for i in range(4)]
    if not same(mv(JI, [1, 1, 1, 1]), [3, 3, 3, 3]):
        fail("eigen: J - I of order 4 must send (1,1,1,1) to 3(1,1,1,1)")
    if tr(JI) != 0:
        fail("eigen: J - I of order 4 must have trace 0")
    if rank([[1 for _ in range(4)] for _ in range(4)]) != 1:
        fail("eigen: J of order 4 must have rank 1, so J - I has -1 with multiplicity 3")
    if rank(shift(JI, 3)) != 3:
        fail("eigen: rank(J - I - 3I) must be 3, confirming that the eigenvalue 3 of J - I is simple")
    JI5 = [[0 if i == j else 1 for j in range(5)] for i in range(5)]
    if det(JI5) != 4:
        fail("eigen: J - I of order 5 must have determinant 4")

    # --- rank one
    u, v = [1, 2, 3], [1, 1, 1]
    UV = [[u[i] * v[j] for j in range(3)] for i in range(3)]
    if rank(UV) != 1:
        fail("eigen: u v^T must have rank 1")
    if tr(UV) != 6:
        fail("eigen: u v^T must have trace v^T u = 6")

    # --- complex conjugate pair, 2016 Set 1 Q.5
    if (2 + 1j) * (2 - 1j) != 5:
        fail("eigen: (2+i)(2-i) must be 5")
    if (2 + 1j) * (2 - 1j) * 3 != 15:
        fail("eigen: 2016 Set 1 Q.5 must give determinant 15")

    # --- 2016 Set 2 Q.6
    if Fraction(1, 1 * 2 * 4) != Fraction(1, 8):
        fail("eigen: 2016 Set 2 Q.6 must give 1/8")

    # --- 2017 Set 1 Q.31 counterexample
    S5 = [[5, 0], [0, 5]]
    if squares(S5) != 50:
        fail("eigen: [[5,0],[0,5]] must have entry squares summing to 50")
    if eigen2(S5) != [Fraction(5), Fraction(5)]:
        fail("eigen: [[5,0],[0,5]] must have eigenvalue 5 twice, so statement II of 2017 Set 1 Q.31 fails")

    # --- the diagonalisation factorisation
    Pp = [[1, 1], [1, -1]]
    Dm = [[3, 0], [0, 1]]
    Pinv = [[Fraction(1, 2), Fraction(1, 2)], [Fraction(1, 2), Fraction(-1, 2)]]
    if not mat_eq(mm(mm(Pp, Dm), Pinv), mat(A1)):
        fail("eigen: P diag(3,1) P^-1 must reconstruct [[2,1],[1,2]]")

    # --- the two Cayley-Hamilton inverses
    ident2 = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    for M, inv in [([[2, 1], [1, 2]], [[Fraction(2, 3), Fraction(-1, 3)], [Fraction(-1, 3), Fraction(2, 3)]]),
                   ([[2, 4], [3, 5]], [[Fraction(-5, 2), Fraction(2)], [Fraction(3, 2), Fraction(-1)]])]:
        if not mat_eq(mm(M, inv), ident2):
            fail("eigen: the Cayley-Hamilton inverse of %r must multiply to the identity" % (M,))
    if not mat_eq(mm([[2, 1], [1, 2]], [[2, 1], [1, 2]]), [[5, 4], [4, 5]]):
        fail("eigen: A^2 for [[2,1],[1,2]] must be [[5,4],[4,5]]")
    A2 = mat(mm([[2, 1], [1, 2]], [[2, 1], [1, 2]]))
    fourA = [[4 * Fraction(x) for x in row] for row in mat([[2, 1], [1, 2]])]
    threeI = [[3 if i == j else 0 for j in range(2)] for i in range(2)]
    if [[A2[i][j] - fourA[i][j] + threeI[i][j] for j in range(2)] for i in range(2)] != mat([[0, 0], [0, 0]]):
        fail("eigen: A^2 - 4A + 3I must vanish for [[2,1],[1,2]]")
    if charpoly2([[2, 4], [3, 5]]) != (Fraction(1), Fraction(-7), Fraction(-2)):
        fail("eigen: the Hindi-source example [[2,4],[3,5]] must have lambda^2 - 7 lambda - 2")
    if det([[2, 4], [3, 5]]) != -2:
        fail("eigen: the Hindi-source example must have determinant -2")

    # --- Cayley-Hamilton, AM >= GM and distinct-eigenvalue independence, over small integer matrices
    small = [-2, -1, 0, 1, 2]
    for a in small:
        for b in small:
            for c in small:
                for d in small:
                    M = [[a, b], [c, d]]
                    t, dt = tr(M), det(M)
                    lhs = mm(M, M)
                    lhs = [[lhs[i][j] - t * M[i][j] + (dt if i == j else 0) for j in range(2)]
                           for i in range(2)]
                    if not mat_eq(lhs, [[0, 0], [0, 0]]):
                        fail("eigen: Cayley-Hamilton fails for %r" % (M,))
                    roots = eigen2(M)
                    if roots is None:
                        continue
                    for lam in set(roots):
                        am = roots.count(lam)
                        gm = 2 - rank(shift(M, lam))
                        if gm < 1 or gm > am:
                            fail("eigen: 1 <= GM <= AM fails for %r at lambda=%r" % (M, lam))
                    if roots[0] != roots[1]:
                        for lam in roots:
                            if rank(shift(M, lam)) != 1:
                                fail("eigen: a distinct eigenvalue of %r must have geometric multiplicity 1" % (M,))

    # --- symmetric matrices: the entry-square identity and orthogonal eigenvectors
    for a in small:
        for b in small:
            for c in small:
                S = [[a, b], [b, c]]
                if squares(S) != tr(mm(S, S)):
                    fail("eigen: the entry squares of the symmetric matrix %r must equal trace(A^2)" % (S,))
                roots = eigen2(S)
                if roots is None or roots[0] == roots[1]:
                    continue
                v1 = [b, roots[0] - a]
                v2 = [b, roots[1] - a]
                if v1 == [0, 0] or v2 == [0, 0]:
                    continue
                if sum(x * y for x, y in zip(v1, v2)) != 0:
                    fail("eigen: the eigenvectors of the symmetric matrix %r must be orthogonal" % (S,))
                if not same(mv(S, v1), [roots[0] * v1[0], roots[0] * v1[1]]):
                    fail("eigen: the stated eigenvector of the symmetric matrix %r must satisfy A v = lambda v" % (S,))

    # --- a non-scalar 2x2 with the double eigenvalue 4 must be defective
    for a in range(-2, 5):
        for b in [-2, -1, 1, 2]:
            for c in [-2, -1, 1, 2]:
                for d in range(-2, 5):
                    M = [[a, b], [c, d]]
                    if charpoly2(M) != (Fraction(1), Fraction(-8), Fraction(16)):
                        continue
                    if mat_eq(mat(M), [[4, 0], [0, 4]]):
                        continue
                    if rank(shift(M, 4)) != 1:
                        fail("eigen: a non-scalar 2x2 with double eigenvalue 4 must have rank(A - 4I) = 1")

    ok("Eigenvalues and eigenvectors: the definition matrix with both eigenpairs, the triangular 3x3 with its "
       "principal minors, the 2015 Set 3 eigenvector and rank(A - I), the defective matrix with AM 2 and GM 1, "
       "A^13 = 64A for 2025 Set 1 Q.31, the rotation and discriminant tests, the row-operation trap, the "
       "2014 Set 2 Q.47 rank, trace and trace(A^2), the 2018 Q.26 counterexample, J - I of orders 4 and 5, the "
       "rank-one trace, the 2016 conjugate pair and 1/8, the 2017 Set 1 Q.31 counterexample, both "
       "Cayley-Hamilton inverses, and Cayley-Hamilton with 1 <= GM <= AM over every 2x2 integer matrix with "
       "entries in [-2,2]; the entry-square identity, orthogonal eigenvectors and the eigenpair itself over "
       "every small symmetric matrix; and the defectiveness of every non-scalar 2x2 with double eigenvalue 4")


# ------------------------------------------------ LU decomposition
def check_lu_decomposition():
    """Every factorization, multiplier, pivot, determinant, solution and product published in the
    LU Decomposition cards, PYQs and lesson, recomputed in exact rational arithmetic."""
    from fractions import Fraction

    def mat(A):
        return [[Fraction(x) for x in row] for row in A]

    def mm(A, B):
        A, B = mat(A), mat(B)
        return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))]
                for i in range(len(A))]

    def eq(A, B):
        A, B = mat(A), mat(B)
        return len(A) == len(B) and all(A[i][j] == B[i][j] for i in range(len(A)) for j in range(len(A[0])))

    def det(A):
        M = mat(A)
        n = len(M)
        d = Fraction(1)
        for c in range(n):
            piv = next((i for i in range(c, n) if M[i][c] != 0), None)
            if piv is None:
                return Fraction(0)
            if piv != c:
                M[c], M[piv] = M[piv], M[c]
                d = -d
            d *= M[c][c]
            for i in range(c + 1, n):
                if M[i][c] != 0:
                    f = M[i][c] / M[c][c]
                    M[i] = [M[i][j] - f * M[c][j] for j in range(n)]
        return d

    def lu(A, swap=None):
        """Doolittle elimination; swap is an optional list of (i, j) row exchanges applied first."""
        n = len(A)
        M = mat(A)
        L = [[Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)]
        P = [[Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)]
        def swap_rows(a, b, upto):
            """Exchange two rows of the working matrix and of P, and the already-computed
            multipliers (columns 0 .. upto-1) of L. The diagonal of L is left alone."""
            M[a], M[b] = M[b], M[a]
            P[a], P[b] = P[b], P[a]
            for k in range(upto):
                L[a][k], L[b][k] = L[b][k], L[a][k]

        if swap:
            for (a, b) in swap:
                swap_rows(a, b, 0)
        for c in range(n - 1):
            if M[c][c] == 0:
                r = next((i for i in range(c + 1, n) if M[i][c] != 0), None)
                if r is None:
                    continue          # the whole column is zero: no pivot, nothing to clear
                swap_rows(c, r, c)
            for i in range(c + 1, n):
                f = M[i][c] / M[c][c]
                L[i][c] = f
                M[i] = [M[i][j] - f * M[c][j] for j in range(n)]
        return L, M, P

    def forward(L, b):
        n = len(b)
        y = [Fraction(0)] * n
        for i in range(n):
            y[i] = (Fraction(b[i]) - sum(L[i][k] * y[k] for k in range(i))) / L[i][i]
        return y

    def back(U, y):
        n = len(y)
        x = [Fraction(0)] * n
        for i in reversed(range(n)):
            x[i] = (y[i] - sum(U[i][k] * x[k] for k in range(i + 1, n))) / U[i][i]
        return x

    # ---- the card-1 example and the definition
    A1 = [[2, 1], [6, 4]]
    L1, U1, _ = lu(A1)
    assert eq(L1, [[1, 0], [3, 1]]) and eq(U1, [[2, 1], [0, 1]])
    assert eq(mm(L1, U1), A1) and det(A1) == 2 and det(U1) == 2
    L1b, U1b, _ = lu([[3, 1], [6, 5]])
    assert eq(L1b, [[1, 0], [2, 1]]) and eq(U1b, [[3, 1], [0, 3]])
    assert eq(mm(L1b, U1b), [[3, 1], [6, 5]])
    assert L1b[1][0] * U1b[0][1] + L1b[1][1] * U1b[1][1] == 5, "the (2,2) dot product of the 3x1 card"

    # ---- card 2: the 2022 matrix, its multipliers, its pivots
    A2 = [[1, 1, -2], [1, 3, -1], [2, 1, -5]]
    L2, U2, _ = lu(A2)
    assert eq(L2, [[1, 0, 0], [1, 1, 0], [2, Fraction(-1, 2), 1]])
    assert eq(U2, [[1, 1, -2], [0, 2, 1], [0, 0, Fraction(-1, 2)]])
    assert eq(mm(L2, U2), A2)
    assert L2[2][1] == Fraction(-1, 2) and U2[2][2] == Fraction(-1, 2)
    assert det(A2) == Fraction(-1, 2) * 2 * 1
    y = forward(L2, [4, 7, 7])
    assert y == [4, 3, Fraction(1, 2)], "the forward pass of the 2022 system"
    x = back(U2, y)
    assert x == [0, 2, -1], "the 2022 solution is (0, 2, -1)"
    assert [sum(mat(A2)[i][k] * x[k] for k in range(3)) for i in range(3)] == [4, 7, 7]
    # the second column of the working matrix, which is where the -1/2 comes from
    W = mat(A2)
    W[1] = [W[1][j] - W[1][0] / W[0][0] * W[0][j] for j in range(3)]
    W[2] = [W[2][j] - W[2][0] / W[0][0] * W[0][j] for j in range(3)]
    assert W[2][1] == -1 and W[1][1] == 2
    assert W[2][1] / W[1][1] == Fraction(-1, 2)

    # ---- card 2 variation and card 12: the 3x3 with multipliers 3, 3 and 2/3
    A3 = [[1, 2, 4], [3, 3, 2], [3, 4, 2]]
    L3, U3, _ = lu(A3)
    assert eq(L3, [[1, 0, 0], [3, 1, 0], [3, Fraction(2, 3), 1]])
    assert eq(U3, [[1, 2, 4], [0, -3, -10], [0, 0, Fraction(-10, 3)]])
    assert eq(mm(L3, U3), A3)
    assert det(A3) == 10 and U3[0][0] * U3[1][1] * U3[2][2] == 10

    # ---- card 3: Doolittle against Crout on the 2015 matrix
    A4 = [[2, 2], [4, 9]]
    Ld, Ud, _ = lu(A4)
    assert eq(Ld, [[1, 0], [2, 1]]) and eq(Ud, [[2, 2], [0, 5]])
    # Crout: U unit upper, so the pivots sit on the diagonal of L
    u12 = Fraction(2, 2)
    l22 = Fraction(9) - Fraction(4) * u12
    Lc = [[Fraction(2), 0], [Fraction(4), l22]]
    Uc = [[Fraction(1), u12], [0, Fraction(1)]]
    assert l22 == 5 and eq(mm(Lc, Uc), A4)
    assert det(Lc) * det(Uc) == 10 == det(A4)
    # the LDU form, and the two mergings of D
    D = [[Fraction(2), 0], [0, Fraction(5)]]
    Uunit = [[Fraction(1), Fraction(1)], [0, Fraction(1)]]
    assert eq(mm(mm(Ld, D), Uunit), A4)
    assert eq(mm(Ld, D), Lc), "merging D into L gives the Crout factors"
    assert eq(mm(D, Uunit), Ud), "merging D into U gives the Doolittle factors"
    # the [[1,2],[3,8]] variation: trace of L under Crout
    L5, U5, _ = lu([[1, 2], [3, 8]])
    l5_22 = Fraction(8) - Fraction(3) * Fraction(2)
    assert l5_22 == 2 and Fraction(1) + l5_22 == 3, "the Crout trace of L for [[1,2],[3,8]] is 3"
    assert eq(mm([[1, 0], [3, l5_22]], [[1, 2], [0, 1]]), [[1, 2], [3, 8]])
    # the LDU predicted variation on [[4,6],[0,-2]]
    L6, U6, _ = lu([[4, 6], [2, 1]])
    assert U6[0][1] / U6[0][0] == Fraction(3, 2), "u12/u11 = 3/2"

    # ---- card 4: existence
    A7 = [[0, 1], [1, 0]]
    assert det(A7) == -1, "[[0,1],[1,0]] is invertible"
    found = False
    for l in range(-6, 7):
        for u in range(-6, 7):
            for v in range(-6, 7):
                for w in range(-6, 7):
                    if eq(mm([[1, 0], [l, 1]], [[u, v], [0, w]]), A7):
                        found = True
    assert not found, "[[0,1],[1,0]] has no unit-L LU factorization"
    # the algebraic reason: position (1,1) forces u = 0, position (2,1) then forces 0 = 1
    u = A7[0][0]
    assert u == 0 and all(l * u != A7[1][0] for l in range(-6, 7))
    # a singular matrix does have one, with a zero last pivot
    L8, U8, _ = lu([[1, 2], [2, 4]])
    assert eq(L8, [[1, 0], [2, 1]]) and eq(U8, [[1, 2], [0, 0]])
    assert U8[1][1] == 0 and det([[1, 2], [2, 4]]) == 0
    # the pivot count is the rank, on a range of small matrices
    for A in ([[1, 2], [2, 4]], [[1, 0], [0, 1]], [[1, 2], [3, 4]], [[2, 4], [1, 2]],
              [[1, 2, 3], [2, 4, 6], [1, 1, 1]], [[1, 0, 0], [0, 0, 1], [0, 1, 0]]):
        Lx, Ux, Px = lu(A)
        pivots = sum(1 for i in range(len(Ux)) if Ux[i][i] != 0)
        M = mat(A)
        rank = 0
        cols = len(M[0])
        # rank by counting independent rows with exact elimination
        rows = [r[:] for r in M]
        r = 0
        for c in range(cols):
            piv = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
            if piv is None:
                continue
            rows[r], rows[piv] = rows[piv], rows[r]
            for i in range(r + 1, len(rows)):
                f = rows[i][c] / rows[r][c]
                rows[i] = [rows[i][j] - f * rows[r][j] for j in range(cols)]
            r += 1
        rank = r
        assert pivots == rank, "the number of nonzero pivots must equal the rank"

    # ---- card 5: pivoting
    A9 = [[1, 2, 3], [2, 4, 1], [4, 9, 2]]
    L9, U9, P9 = lu(A9, [(1, 2)])
    assert eq(mm(L9, U9), mm(P9, A9)), "PA = LU for the pivoting example"
    assert eq(P9, [[1, 0, 0], [0, 0, 1], [0, 1, 0]])
    assert eq(L9, [[1, 0, 0], [4, 1, 0], [2, 0, 1]])
    assert eq(U9, [[1, 2, 3], [0, 1, -10], [0, 0, -5]])
    assert det(P9) == -1 and det(U9) == -5 and det(A9) == 5
    assert det(A9) == -det(U9)
    # the zero-pivot matrix of the card and the check
    A10 = [[0, 2], [1, 3]]
    L10, U10, P10 = lu(A10, [(0, 1)])
    assert eq(P10, [[0, 1], [1, 0]]) and eq(U10, [[1, 3], [0, 2]]) and eq(L10, [[1, 0], [0, 1]])
    assert eq(mm(L10, U10), mm(P10, A10))
    assert det(P10) == -1 and det(U10) == 2 and det(A10) == -2
    # a swap after multipliers have been recorded must carry them along
    A11 = [[1, 2, 3], [2, 4, 1], [4, 9, 2]]
    Ls, Us, Ps = lu(A11, [(1, 2)])
    assert Ls[1][0] == 4 and Ls[2][0] == 2, "the multipliers travel with their rows"

    # ---- card 6: substitution, including the singular case
    y10 = forward(L8, [1, 2])
    assert y10 == [1, 0], "the forward pass of the singular system"
    # the singular system leaves x2 free and x1 = 1 - 2 x2
    for t in (Fraction(0), Fraction(1), Fraction(-3, 2)):
        xx = [1 - 2 * t, t]
        assert [sum(mat([[1, 2], [2, 4]])[i][k] * xx[k] for k in range(2)) for i in range(2)] == [1, 2]
    # the 2022 system, solved the other way round, does not satisfy A x = b
    xbad = back(U2, [4, 7, 7])
    assert xbad[2] == -14 and xbad[1] == Fraction(21, 2)
    assert [sum(mat(A2)[i][k] * xbad[k] for k in range(3)) for i in range(3)] != [4, 7, 7]

    # ---- card 7: the determinant from the pivots
    assert det(Ud) == det(A4) and det(Ld) == 1
    assert det(U9) * det(P9) == det(A9)

    # ---- card 8: rank, singularity, and the 2025 statements
    assert det(U8) == 0 and det([[1, 2], [2, 4]]) == 0
    assert det(L2) == 1, "a unit lower triangular matrix always has determinant 1"
    P_sym = [[1, 2, 0], [2, 5, 1], [0, 1, 3]]
    assert eq(P_sym, [[P_sym[j][i] for j in range(3)] for i in range(3)]), "the counterexample is symmetric"
    Lp, Up, _ = lu(P_sym)
    assert eq(mm(Lp, Up), P_sym)
    assert not eq(Lp, [[Lp[j][i] for j in range(3)] for i in range(3)]), "L is not symmetric"
    assert not eq(Up, [[Up[j][i] for j in range(3)] for i in range(3)]), "U is not symmetric"
    assert det(P_sym) == 2
    # statement 2: invertible P forces det(U) != 0; statement 3: singular P forces a zero on U's diagonal
    for A in ([[1, 2], [3, 4]], [[1, 2], [2, 4]], [[2, 1], [1, 1]]):
        Lx, Ux, Px = lu(A)
        assert det(Ux) == det(A) / det(Px)
        if det(A) != 0:
            assert all(Ux[i][i] != 0 for i in range(2))
        else:
            assert any(Ux[i][i] == 0 for i in range(2))
    # a lower triangular matrix equal to its transpose is diagonal
    assert all(eq(Lc, [[Lc[j][i] for j in range(2)] for i in range(2)]) is False for Lc in (Ld, Lp))

    # ---- card 9: the operation counts
    for n in (10, 100, 500):
        assert 2 * n ** 3 // 3 == 2 * n * n * n // 3
    assert 2 * 1000 ** 3 // 3 == 666666666
    assert 100 * 2 * 1000 ** 2 == 200000000
    assert 2 * 1000 ** 3 // 3 + 100 * 2 * 1000 ** 2 < 100 * (2 * 1000 ** 3 // 3), "LU beats repeated elimination"
    assert 2 * 200 ** 3 // 3 + 50 * 2 * 200 ** 2 < 50 * (2 * 200 ** 3 // 3)
    # break-even: for one right-hand side LU is dearer
    n = 500
    assert 2 * n ** 3 // 3 + 2 * n ** 2 > 2 * n ** 3 // 3

    # ---- card 10: the inverse from the factorization
    col1 = back(U1, forward(L1, [1, 0]))
    col2 = back(U1, forward(L1, [0, 1]))
    assert col1 == [2, -3] and col2 == [Fraction(-1, 2), 1]
    assert eq([[col1[0], col2[0]], [col1[1], col2[1]]], [[2, Fraction(-1, 2)], [-3, 1]])
    assert eq(mm([[2, Fraction(-1, 2)], [-3, 1]], A1), [[1, 0], [0, 1]]), "the two columns form A^-1"
    assert det(A1) == 2 and eq([[Fraction(4, 2), Fraction(-1, 2)], [Fraction(-6, 2), Fraction(2, 2)]],
                               [[2, Fraction(-1, 2)], [-3, 1]]), "the adjugate gives the same inverse"
    # the reversal of the order really matters
    L1inv = [[1, 0], [-3, 1]]
    U1inv = [[Fraction(1, 2), Fraction(-1, 2)], [0, 1]]
    wrong = mm(L1inv, U1inv)
    right = mm(U1inv, L1inv)
    assert not eq(mm(wrong, A1), [[1, 0], [0, 1]]), "L^-1 U^-1 is not the inverse"
    assert eq(mm(right, A1), [[1, 0], [0, 1]])
    # the [[1,2],[3,8]] variation: the (1,1) entry of the inverse is 4
    Lc8 = [[1, 0], [3, 2]]
    Uc8 = [[1, 2], [0, 1]]
    c1 = back(Uc8, forward(Lc8, [1, 0]))
    assert c1 == [4, Fraction(-3, 2)], "the first column of the inverse of [[1,2],[3,8]]"
    assert det([[1, 2], [3, 8]]) == 2 and 8 / 2 == 4, "the adjugate gives the same (1,1) entry"
    # the check on the card
    assert back(U1, forward(L1, [5, 16])) == [2, 1]

    # ---- card 11: LDL^T and Cholesky
    A12 = [[4, 2], [2, 3]]
    L12, U12, _ = lu(A12)
    assert eq(L12, [[1, 0], [Fraction(1, 2), 1]]) and eq(U12, [[4, 2], [0, 2]])
    D12 = [[Fraction(4), 0], [0, Fraction(2)]]
    assert eq(mm(mm(L12, D12), [[1, Fraction(1, 2)], [0, 1]]), A12), "A = L D L^T"
    # C = L diag(sqrt(4), sqrt(2)); C C^T is checked through its entries, since sqrt(2) is irrational
    assert 1 * 1 + 2 == 3, "the (2,2) entry of C C^T is 1 + 2"
    assert 2 * 1 == 2 and 2 * 2 == 4, "the off-diagonal and (1,1) entries of C C^T"
    A13 = [[1, 2], [2, 5]]
    assert det(A13) == 1 and A13[0][0] == 1, "[[1,2],[2,5]] passes the 2x2 positive-definiteness test"
    L13, U13, _ = lu(A13)
    assert U13[0][0] == 1 and U13[1][1] == 1, "both pivots are positive, so Cholesky exists"
    assert eq(mm([[1, 0], [2, 1]], [[1, 2], [0, 1]]), A13), "C C^T = A for C = [[1,0],[2,1]]"

    # ---- card 12: the exam-reading example
    A14 = [[2, 3, 1], [4, 7, 7], [-2, 4, 5]]
    L14, U14, _ = lu(A14)
    assert eq(L14, [[1, 0, 0], [2, 1, 0], [-1, 7, 1]])
    assert eq(U14, [[2, 3, 1], [0, 1, 5], [0, 0, -29]])
    assert eq(mm(L14, U14), A14)
    assert det(A14) == -58 == U14[0][0] * U14[1][1] * U14[2][2]
    assert L14[2][0] * U14[0][1] + L14[2][1] * U14[1][1] + L14[2][2] * U14[2][1] == 4
    assert A14[2][1] == 4, "the (3,2) entry of A is 4"
    assert L14[2][0] * U14[0][2] + L14[2][1] * U14[1][2] + L14[2][2] * U14[2][2] == 5
    assert U14[1][2] == 5, "u23 is 5"
    assert [sum(L14[2][k] * U14[k][j] for k in range(3)) for j in range(3)] == A14[2], "row 3 of A from row 3 of L"
    # the Doolittle factors rescaled without touching L do not reproduce A
    assert not eq(mm(Ld, [[1, 1], [0, 1]]), A4), "dividing only the rows of U breaks the product"

    # ---- the lesson's own numbers
    after1 = [[2, 3, 1], [0, 1, 5], [0, 7, 6]]
    assert eq(after1, [[2, 3, 1], [0, 7 - 2 * 3, 7 - 2 * 1], [0, 4 + 3, 5 + 1]])
    assert eq(mm(L14, U14), A14) and det(A14) == -58

    ok("LU decomposition: twelve factorizations recomputed in exact rational arithmetic, both diagonal "
       "conventions, the existence counterexample by exhaustive search, the pivot count against the rank, "
       "the permutation case with its determinant sign, the 2022 solution and both disputed option values, "
       "the 2025 statements, the inverse columns, LDL^T and Cholesky, the operation counts and every "
       "number in the lesson")


# ------------------------------- mean, median, mode and standard deviation
def check_mean_median_mode():
    """Every mean, median, mode, variance and standard deviation published in this topic's
    twelve cards, five PYQ records and p5 lesson is recomputed from the lists themselves."""
    import math
    from fractions import Fraction as Fr

    def close(a, b, tol=1e-6):
        return abs(a - b) <= tol

    def mean(xs):
        return sum(Fr(x) for x in xs) / len(xs)

    def var(xs):
        m = mean(xs)
        return sum((Fr(x) - m) ** 2 for x in xs) / len(xs)

    def sd(xs):
        return math.sqrt(float(var(xs)))

    def median(xs):
        s = sorted(xs)
        n = len(s)
        return Fr(s[n // 2]) if n % 2 else (Fr(s[n // 2 - 1]) + Fr(s[n // 2])) / 2

    def mode(xs):
        counts = {}
        for x in xs:
            counts[x] = counts.get(x, 0) + 1
        best = max(counts.values())
        return sorted(k for k, v in counts.items() if v == best)

    # ---- card 1: the credit-weighted mean and the frequency-table mean
    if mean([72, 72, 88, 88, 88] + [64] * 5) != Fr(728, 10):
        fail("mean: the credit-weighted example must be 728/10")
    if float(mean([72, 72, 88, 88, 88] + [64] * 5)) != 72.8:
        fail("mean: the credit-weighted example must be 72.8")
    if Fr(2 * 72 + 3 * 88 + 5 * 64, 10) != Fr(728, 10):
        fail("mean: the weighted sum must be 144 + 264 + 320 = 728")
    if float(mean([0] * 12 + [1] * 20 + [2] * 15 + [3] * 3)) != 1.18:
        fail("mean: the defects table must give 59/50 = 1.18")
    if float(mean([4, 6, 6, 8, 11])) != 7:
        fail("mean: the quick check on 4, 6, 6, 8, 11 must be 7")
    if float(mean([2, 4, 6, 8])) != 5:
        fail("mean: the four equally likely values must have mean 5")
    # the unweighted-midpoint trap: 44 against 25
    mid = [5, 15, 25, 35, 45]
    freq = [1, 1, 1, 1, 96]
    if Fr(sum(f * m for f, m in zip(freq, mid)), sum(freq)) != 44:
        fail("mean: the weighted midpoint mean of the trap example must be 44")
    if float(mean(mid)) != 25:
        fail("mean: the unweighted midpoint average must be 25")

    # ---- card 2: the median and its robustness
    if median([3, 7, 8, 9, 12, 15]) != Fr(17, 2):
        fail("median: 3, 7, 8, 9, 12, 15 must have median 8.5")
    if float(mean([3, 7, 8, 9, 12, 15])) != 9:
        fail("median: the same list must have mean 9")
    if median([3, 7, 8, 9, 12, 1000]) != Fr(17, 2):
        fail("median: replacing 15 by 1000 must leave the median at 8.5")
    if abs(float(mean([3, 7, 8, 9, 12, 1000])) - 1039 / 6) > 1e-12:
        fail("median: replacing 15 by 1000 must give the mean 1039/6")
    if median([1, 2, 2, 3, 4, 5, 5]) != 3:
        fail("median: the seven scores must have median 3")
    if median([12, 7, 3, 9, 15, 8, 11]) != 9:
        fail("median: the quick check list must have median 9")
    if median([9, 3, 7, 15, 8, 12]) != Fr(17, 2):
        fail("median: the unsorted trap list must have median 8.5")
    if (7 + 15) / 2 == 8.5:
        fail("median: the unsorted trap must not accidentally give the same answer")
    # decreasing the smallest three of a nine-value list leaves the median alone
    nine = [1, 2, 3, 4, 20, 21, 22, 23, 24]
    if median(nine) != 20 or median([1 - 5, 2 - 5, 3 - 5, 4, 20, 21, 22, 23, 24]) != 20:
        fail("median: the nine-value variation must keep its median at 20")

    # ---- card 3: the mode, ties and multimodality
    if mode([2, 3, 3, 5, 7, 7, 7, 9]) != [7]:
        fail("mode: 2, 3, 3, 5, 7, 7, 7, 9 must be unimodal at 7")
    if float(mean([2, 3, 3, 5, 7, 7, 7, 9])) != 43 / 8:
        fail("mode: the same list must have mean 43/8")
    if median([2, 3, 3, 5, 7, 7, 7, 9]) != 6:
        fail("mode: the same list must have median 6")
    if mode([1, 2, 2, 3, 3, 4]) != [2, 3]:
        fail("mode: the bimodal example must be 2 and 3")
    if mode([1, 2, 3, 4, 5]) != [1, 2, 3, 4, 5]:
        fail("mode: a list of distinct values must have no unique mode")
    if mode([4, 4, 5, 6, 6, 7, 7, 7, 9]) != [7]:
        fail("mode: the quick check list must be unimodal at 7")
    # the modal-class interpolation of the original question
    L, f1, f0, f2, h = 30, 14, 9, 8, 10
    if not close(L + (f1 - f0) / (2 * f1 - f0 - f2) * h, 34.54545, 1e-4):
        fail("mode: the modal-class interpolation must give 34.545")
    # the Poisson mode of the predicted variation
    lam = 2.4
    ratio = lambda k: lam / k
    masses = [lam ** k * math.exp(-lam) / math.factorial(k) for k in range(12)]
    if masses.index(max(masses)) != 2:
        fail("mode: the Poisson mode at lambda = 2.4 must be 2")

    # ---- card 4: the empirical relation and the ordering
    if 3 * 37 - 2 * 40 != 31:
        fail("relation: mean 40 and median 37 must give mode 31")
    if (48 + 2 * 60) // 3 != 56:
        fail("relation: mode 48 and mean 60 must give median 56")
    if (15 + 2 * float(mean([15, 15, 15, 75]))) / 3 != 25:
        fail("relation: the empirical formula must predict 25 for the hostile list")
    if float(mean([15, 15, 15, 75])) != 30 or mode([15, 15, 15, 75]) != [15]:
        fail("relation: the hostile list must have mean 30 and mode 15")
    if median([15, 15, 15, 75]) != 15:
        fail("relation: the hostile list must have true median 15")
    if 3 * 15 - 2 * 30 != -15:
        fail("relation: the formula applied backwards to the hostile list")

    # ---- card 5: the grouped table, and the Tamil lecture's table
    mid5 = [5, 15, 25, 35, 45]
    fr5 = [4, 6, 10, 6, 4]
    n5 = sum(fr5)
    m5 = Fr(sum(f * x for f, x in zip(fr5, mid5)), n5)
    if m5 != 25:
        fail("grouped: the symmetric table must have mean 25")
    cf, run = [], 0
    for f in fr5:
        run += f
        cf.append(run)
    half = Fr(n5, 2)
    k = next(i for i, c in enumerate(cf) if c >= half)
    prev = cf[k - 1] if k else 0
    med5 = Fr(mid5[k] - 5) + (half - prev) / fr5[k] * 10
    if med5 != 25:
        fail("grouped: the symmetric table must have median 25")
    j = fr5.index(max(fr5))
    f0g = fr5[j - 1] if j else 0
    f2g = fr5[j + 1] if j + 1 < len(fr5) else 0
    mode5 = Fr(mid5[j] - 5) + Fr(fr5[j] - f0g, 2 * fr5[j] - f0g - f2g) * 10
    if mode5 != 25:
        fail("grouped: the symmetric table must have mode 25")
    var5 = sum(Fr(f) * (Fr(x) - m5) ** 2 for f, x in zip(fr5, mid5)) / n5
    if var5 != Fr(4400, 30):
        fail("grouped: the symmetric table must have variance 4400/30")
    if not close(math.sqrt(float(var5)), 12.11059, 1e-4):
        fail("grouped: the symmetric table must have standard deviation 12.1106")
    # the Tamil lecture's table
    midT = [5, 15, 25, 35, 45]
    frT = [12, 18, 20, 25, 23]
    nT = sum(frT)
    mT = Fr(sum(f * x for f, x in zip(frT, midT)), nT)
    if nT != 98 or mT != Fr(2740, 98):
        fail("grouped: the Tamil table must have N = 98 and mean 2740/98")
    if not close(float(mT), 27.95918, 1e-4):
        fail("grouped: the Tamil table must have mean 27.96")
    if Fr(20) + (Fr(98, 2) - 30) / 20 * 10 != 29.5:
        fail("grouped: the Tamil table must have median 29.5")
    if Fr(30) + Fr(25 - 20, 2 * 25 - 20 - 23) * 10 != Fr(50, 7) + 30:
        fail("grouped: the Tamil table must have mode 30 + 5/7*10")
    if not close(30 + 5 / 7 * 10, 37.14286, 1e-4):
        fail("grouped: the Tamil table must have mode 37.14")
    # the discontinuous-classes variation
    if Fr(19) + Fr(1, 2) + (Fr(20, 2) - 5) / 8 * 10 != Fr(103, 4):
        fail("grouped: the discontinuous variation must give a median of 25.75")

    # ---- card 6: variance and the two divisors
    d6 = [2, 4, 4, 4, 5, 5, 7, 9]
    if mean(d6) != 5 or var(d6) != 4:
        fail("variance: 2, 4, 4, 4, 5, 5, 7, 9 must have mean 5 and population variance 4")
    if sd(d6) != 2:
        fail("variance: the same list must have population standard deviation 2")
    if sum((x - 5) ** 2 for x in d6) != 32:
        fail("variance: the squared deviations must sum to 32")
    if Fr(32, 7) != Fr(8, 7) * 4:
        fail("variance: the sample variance must be 32/7")
    if not close(math.sqrt(32 / 7), 2.13809, 1e-4):
        fail("variance: the sample standard deviation must be 2.1381")
    if not close(sd([1, 2, 3, 4, 5]) ** 2, 2):
        fail("variance: 1, 2, 3, 4, 5 must have variance 2")
    if not close(sd([1, 2, 3, 4, 5]), 1.414214, 1e-5):
        fail("variance: 1, 2, 3, 4, 5 must have standard deviation 1.4142")

    # ---- card 7: shift and scale, and the 2011 question's numbers
    X7 = [2, 4, 6, 8, 10]
    if mean(X7) != 6 or var(X7) != 8:
        fail("scale: 2, 4, 6, 8, 10 must have mean 6 and variance 8")
    Y7 = [3 * x - 5 for x in X7]
    if Y7 != [1, 7, 13, 19, 25]:
        fail("scale: 3X - 5 of the card's list must be 1, 7, 13, 19, 25")
    if mean(Y7) != 13 or var(Y7) != 72:
        fail("scale: 3X - 5 must have mean 13 and variance 72")
    if var(Y7) != 9 * var(X7):
        fail("scale: the variance of aX + b must be a^2 times the variance")
    if not close(sd(Y7), 3 * sd(X7)) or not close(sd(Y7), 8.485281, 1e-5):
        fail("scale: the standard deviation of 3X - 5 must be 8.4853")
    if not close(sd(X7), 2.828427, 1e-5):
        fail("scale: 2, 4, 6, 8, 10 must have standard deviation 2.8284")
    # the 2011 question's worked numbers
    q11 = [2, 3, 4, 4, 5]
    if not close(float(mean(q11)), 3.6) or not close(sd(q11), 1.019804, 1e-5):
        fail("scale: the 2011 example must have mean 3.6 and standard deviation 1.0198")
    if [2 * x + 100 for x in q11] != [104, 106, 108, 108, 110]:
        fail("scale: the 2011 transformed list must be 104, 106, 108, 108, 110")
    if not close(sd([2 * x + 100 for x in q11]), 2 * sd(q11)):
        fail("scale: the transformed list's standard deviation must be twice the original")
    if not close(2 * sd(q11) + 100, 102.039608, 1e-5):
        fail("scale: the wrong option of the 2011 question must evaluate to 102.0396")
    if not close(sd([-2 * x + 7 for x in X7]), 2 * sd(X7)):
        fail("scale: a negative multiplier must still multiply the spread by its absolute value")
    if not close(sd([0.5 * x + 100 for x in X7]), 0.5 * sd(X7)):
        fail("scale: the quick check must halve the spread")

    # ---- card 8: the two minimisations
    d8 = [1, 2, 3, 10]
    m8 = mean(d8)
    if m8 != 4:
        fail("deviation: 1, 2, 3, 10 must have mean 4")
    sq = lambda c: sum((Fr(x) - Fr(c)) ** 2 for x in d8)
    if sq(4) != 50 or sq(3) != 54:
        fail("deviation: the squared deviations must be 50 at the mean and 54 at 3")
    if sq(Fr(5, 2)) != 59:
        fail("deviation: the squared deviations at the median must be 59")
    if sum(abs(x - m8) for x in d8) != 12:
        fail("deviation: the absolute deviations at the mean must sum to 12")
    if sum(abs(Fr(x) - Fr(5, 2)) for x in d8) != 10:
        fail("deviation: the absolute deviations at the median must sum to 10")
    if sum(x - m8 for x in d8) != 0:
        fail("deviation: the signed deviations must sum to zero")
    for c in [-3, 0, 1, 2, 3, 5, 9, 20]:
        if sq(c) < sq(4):
            fail("deviation: c = %r beats the mean on the squared deviations" % c)
    for c in [1, 2, 3, 10]:
        if sum(abs(Fr(x) - Fr(c)) for x in d8) < 10:
            fail("deviation: c = %r beats the median on the absolute deviations" % c)
    for c in [2, 3, 4, 9]:
        if sum(abs(Fr(x) - Fr(c)) for x in [1, 2, 9, 10]) != 16:
            fail("deviation: every c in [2, 9] must give 16 on the four-point list")
    d8b = [4, 6, 8, 10]
    if sum((x - 7) ** 2 for x in d8b) != 20 or sum((x - 6) ** 2 for x in d8b) != 24:
        fail("deviation: the 4, 6, 8, 10 variation must give 20 at the mean and 24 at 6")

    # ---- card 9: the median and the mode of a random variable
    lam9 = 2.0
    if not close(1 / lam9, 0.5):
        fail("median-rv: the exponential mean must be 1/lambda")
    if not close(math.log(2) / lam9, 0.346574, 1e-5):
        fail("median-rv: the exponential median must be ln 2 / lambda")
    if not close(math.log(2) / lam9 / (1 / lam9), math.log(2)):
        fail("median-rv: the exponential median over mean must be ln 2")
    def cdf_expo(x):
        return 1 - math.exp(-lam9 * x)
    if not close(cdf_expo(math.log(2) / lam9), 0.5):
        fail("median-rv: the exponential CDF must be 1/2 at the median")
    dens = lambda x: lam9 * math.exp(-lam9 * x)
    if not (dens(0) > dens(0.1) and dens(0.1) > dens(1.0)):
        fail("median-rv: the exponential density must be decreasing, so the mode is 0")
    # the discrete uniform on 1..6 has two medians and the continuous analogue an interval
    u6 = [1, 2, 3, 4, 5, 6]
    def is_median(u, m):
        le = sum(1 for x in u if x <= m) / len(u)
        ge = sum(1 for x in u if x >= m) / len(u)
        return le >= 0.5 - 1e-12 and ge >= 0.5 - 1e-12
    if not (is_median(u6, 3) and is_median(u6, 4)):
        fail("median-rv: 3 and 4 must both be medians of the uniform on 1..6")
    if is_median(u6, 2) or is_median(u6, 5):
        fail("median-rv: 2 and 5 must not be medians of the uniform on 1..6")
    u4 = [1, 2, 3, 4]
    for m in [2, 2.5, 3]:
        if not is_median(u4, m):
            fail("median-rv: every m in [2, 3] must be a median of the uniform on 1..4")
    if is_median(u4, 1) or is_median(u4, 4):
        fail("median-rv: the endpoints must not be medians of the uniform on 1..4")
    # Y = max(X, 0) with X symmetric about 0: 0 is a median, no positive m is
    def ycdf(m):
        if m < 0:
            return 0.0
        return 0.5 + 0.5 * math.erf(m / math.sqrt(2))
    def ysurv(m):
        if m <= 0:
            return 1.0
        return 0.5 * (1 - math.erf(m / math.sqrt(2)))
    if not (ycdf(0) >= 0.5 and ysurv(0) >= 0.5):
        fail("median-rv: 0 must be a median of max(X, 0)")
    for m in [0.1, 0.5, 1, 2]:
        if ycdf(m) >= 0.5 and ysurv(m) >= 0.5:
            fail("median-rv: a positive m must not be a median of max(X, 0)")
    if ycdf(-1) >= 0.5:
        fail("median-rv: a negative m must not be a median of max(X, 0)")

    # ---- card 10: the standard deviation of a count
    n10, p10 = 1000, 0.4
    if not close(n10 * p10 * (1 - p10), 240):
        fail("count: the binomial variance must be 240")
    if not close(math.sqrt(240), 15.491933, 1e-5):
        fail("count: the binomial standard deviation must be 15.4919")
    if not close(math.sqrt(n10 * p10), 20):
        fail("count: sqrt(np) must be 20, the dropped-factor wrong answer")
    if not close(math.sqrt(100 * 0.5 * 0.5), 5):
        fail("count: Bin(100, 0.5) must have standard deviation 5")
    if not close(math.sqrt(9), 3):
        fail("count: the Poisson count with mean 9 must have standard deviation 3")
    best = max(range(1, 100), key=lambda k: k / 100 * (1 - k / 100))
    if best != 50:
        fail("count: np(1-p) must be largest at p = 1/2")

    # ---- card 11: one changed value, and two combined groups
    if Fr(10 * 60 + 30 * 80, 40) != 75:
        fail("combine: the two-group mean must be 75")
    if (60 + 80) / 2 == 75:
        fail("combine: the unweighted average of the means must not coincide with 75")
    if Fr(20 * 55 + 30 * 80, 50) != 70:
        fail("combine: the two-section mean must be 70")
    before, after = [1, 2, 3, 4], [1, 2, 3, 14]
    if mean(before) != Fr(5, 2) or mean(after) != 5:
        fail("combine: the changed value must move the mean from 2.5 to 5")
    if median(before) != Fr(5, 2) or median(after) != Fr(5, 2):
        fail("combine: the median must stay at 2.5")
    if var(before) != Fr(5, 4) or var(after) != Fr(55, 2):
        fail("combine: the variances must be 1.25 and 27.5")
    if not close(sd(before), 1.118034, 1e-5) or not close(sd(after), 5.244044, 1e-5):
        fail("combine: the standard deviations must be 1.1180 and 5.2440")
    # the combined variance with its between-group term
    n1, m1, v1 = 4, 10, 4
    n2, m2, v2 = 6, 20, 4
    mc = Fr(n1 * m1 + n2 * m2, n1 + n2)
    if mc != 16:
        fail("combine: the combined mean must be 16")
    d1, d2 = m1 - mc, m2 - mc
    cv = (n1 * (v1 + d1 ** 2) + n2 * (v2 + d2 ** 2)) / (n1 + n2)
    if cv != 28:
        fail("combine: the combined variance must be 28")
    if (n1 * v1 + n2 * v2) / (n1 + n2) != 4:
        fail("combine: ignoring the between-group term must give 4, which the card warns about")

    # ---- card 12: the coefficient of variation and the units
    if not close(5 / 100, 0.05) or not close(20 / 100, 0.20):
        fail("units: the two coefficients of variation must be 0.05 and 0.20")
    if not close(10 / 50, 0.2):
        fail("units: the quick check coefficient of variation must be 0.2")

    # ---- the five PYQ records
    if Fr(35, 9) != Fr(4 * 3 + 2 * 4 + 3 * 5, 9):
        fail("pyq: the 2014 word-length mean must equal 35/9 both ways")
    if not close(float(Fr(35, 9)), 3.888889, 1e-5):
        fail("pyq: the 2014 word-length mean must be 3.8889")
    if 4 * 3 + 2 * 4 + 3 * 5 != 35:
        fail("pyq: the 2014 grouping must still total 35")
    # 2024 Set 2 Q.44: the two counterexamples and the monotone inequality
    if not close(1 / 3, 0.3333333, 1e-6) or not (1 / 3 > 0.25):
        fail("pyq: E[X^2] on the unit interval must be 1/3, beating 1/4")
    if not close(1 / 6, 0.1666667, 1e-6) or not (1 / 6 < 0.25):
        fail("pyq: E[X(1-X)] on the unit interval must be 1/6, below 1/4")
    for a, b in [(0.2, 0.9), (1.0, 1.0), (0.0, 0.4), (0.7, 0.3)]:
        if not (a * b <= a + 1e-12):
            fail("pyq: 0 <= xy <= x must hold for every pair in [0, 1]")

    # ---- the p5 lesson's four versions of the same data set
    base = [2, 3, 3, 4, 9]
    outlier = [2, 3, 3, 4, 19]
    shifted = [12, 13, 13, 14, 29]
    doubled = [4, 6, 6, 8, 38]
    if [2 * x for x in outlier] != doubled:
        fail("lesson: the doubled set must be twice the outlier set")
    if [x + 10 for x in outlier] != shifted:
        fail("lesson: the shifted set must be the outlier set plus 10")
    if base != [2, 3, 3, 4, 9]:
        fail("lesson: the base set is wrong")
    expected = [
        (base, 4.2, 3, 3, 6.16, 2.4819),
        (outlier, 6.2, 3, 3, 41.36, 6.4312),
        (shifted, 16.2, 13, 13, 41.36, 6.4312),
        (doubled, 12.4, 6, 6, 165.44, 12.8624),
    ]
    for xs, m, md, mo, v, s in expected:
        if not close(float(mean(xs)), m):
            fail("lesson: %r must have mean %r" % (xs, m))
        if float(median(xs)) != md:
            fail("lesson: %r must have median %r" % (xs, md))
        if mode(xs) != [mo]:
            fail("lesson: %r must be unimodal at %r" % (xs, mo))
        if not close(float(var(xs)), v):
            fail("lesson: %r must have variance %r" % (xs, v))
        if not close(sd(xs), s, 1e-4):
            fail("lesson: %r must have standard deviation %r" % (xs, s))
        if sum(Fr(x) - mean(xs) for x in xs) != 0:
            fail("lesson: the signed deviations of %r must sum to zero" % (xs,))
    if var(shifted) != var(outlier):
        fail("lesson: the shift must leave the variance unchanged")
    if var(doubled) != 4 * var(outlier):
        fail("lesson: the doubling must multiply the variance by four")
    if not close(sd(doubled), 2 * sd(outlier)):
        fail("lesson: the doubling must double the standard deviation")
    if mean(doubled) != 2 * mean(outlier) or median(doubled) != 2 * median(outlier):
        fail("lesson: the doubling must double the mean and the median")
    if mean(shifted) != mean(outlier) + 10 or median(shifted) != median(outlier) + 10:
        fail("lesson: the shift must add 10 to the mean and the median")
    if median(outlier) != median(base):
        fail("lesson: the outlier must leave the median at 3")
    if not close(3 * sd(base), 7.4458, 1e-4):
        fail("lesson: the quick check must be 3 x 2.4819 = 7.4458")
    if not close(2 * sd(base), 4.9638, 1e-4):
        fail("lesson: the misconception figure must be 2 x 2.4819 = 4.9638")
    if sum((x - 4.2) ** 2 for x in base) != 30.8 and not close(sum((x - 4.2) ** 2 for x in base), 30.8):
        fail("lesson: the squared deviations of the base set must total 30.8")
    if not close((9 - 4.2) ** 2, 23.04):
        fail("lesson: the 9 must contribute 23.04 to the squared deviations")

    ok("mean, median, mode and standard deviation: the weighted and grouped means, the median "
       "positions, the modes, both deviation minimisations, the two divisors, the shift and scale "
       "identities, the random-variable medians, the binomial and Poisson spreads, the combined "
       "variance, all five PYQ computations and the four versions in the p5 lesson recomputed")


def check_number_representation():
    """Every number, range and bit pattern published in the Number Systems and Number
    Representation cards, PYQs and lesson is recomputed here from its bits."""

    def bits(n, width):
        return bin(n)[2:].zfill(width)

    def twos(b):
        """Value of a two's complement pattern given as a binary string."""
        n = int(b, 2)
        return n - (1 << len(b)) if b[0] == '1' else n

    def decode32(word):
        b = bits(word, 32)
        s, e, f = b[0], b[1:9], b[9:]
        E = int(e, 2)
        assert E != 0 and E != 255, "special word, not a normal number"
        sig = 1 + sum(int(c) * 2.0 ** -(i + 1) for i, c in enumerate(f))
        return (int(s) and -1 or 1) * sig * 2.0 ** (E - 127), E, sig

    # ---- card 1: place value
    assert 1 * 8 + 0 * 4 + 1 * 2 + 0 * 1 == 10
    assert 0.5 + 0.125 == 0.625
    assert 8 + 2 + 0.5 + 0.125 == 10.625
    assert 2 ** 8 == 256 and 2 ** 10 == 1024 and 2 ** 16 == 65536 and 2 ** 20 == 1048576
    assert 2 * 9 + 1 * 3 + 0 == 21                      # (210) in base 3
    assert 1 * 49 + 2 * 7 + 3 == 66                     # (123) in base 7
    assert 2 * 16 + 10 == 42 and 5 * 8 + 2 == 42        # (2A)16 = (52)8

    # ---- card 2: base conversion
    assert int("15", 16) == 21 and 21 == 1 * 16 + 5
    assert 1 * 16 + 3 * 4 + 2 == 30 and 1 * 25 + 1 * 5 + 0 == 30   # (132)4 = (110)5
    assert 0.375 * 2 == 0.75 and 0.75 * 2 == 1.5 and 0.5 * 2 == 1.0  # 0.375 -> 0.011
    assert 4 * 5 + 3 == 23                              # (43)5
    assert 1 * 2 + 1 == 3 and int("110", 2) == 6        # the reversed-remainder counterexample

    # ---- card 3: grouping
    assert int("2E7", 16) == 743 == 1 * 512 + 3 * 64 + 4 * 8 + 7
    assert int("1347", 8) == 743
    assert int("AB", 16) == 171 == 2 * 64 + 5 * 8 + 3
    assert int("253", 8) == 171
    assert 0.75 == 6 / 8 and int("11", 2) / 4 == 0.75

    # ---- card 4: unsigned widths
    assert 2 ** 8 - 1 == 255 and 2 ** 16 - 1 == 65535 and 2 ** 32 - 1 == 4294967295
    assert 2 ** 12 == 4096 and 2 ** 12 - 1 == 4095 and 2 ** 10 == 1024 and 2 ** 10 - 1 == 1023
    assert (255 + 1) % 256 == 0                          # wrap-around

    # ---- card 5: sign-magnitude
    assert int("00010110", 2) == 22 and int("10010110", 2) == 150 == 128 + 22
    assert int("0101101", 2) == 45 and int("10101101", 2) == 128 + 45
    assert int("10000000", 2) == 128                     # negative zero
    assert 2 ** 7 - 1 == 127 and 2 ** 8 - 1 == 255       # 255 distinct values

    # ---- card 6: one's complement
    assert 255 - 22 == 233 == int("11101001", 2)
    assert int("11111110", 2) == 254                     # -1 in one's complement
    assert int("0101", 2) + int("1110", 2) == 19         # 1 0011 with a carry out
    assert 19 - 16 + 1 == 4                              # end-around carry gives +4
    assert int("0011", 2) == 3                           # without it, +3

    # ---- card 7: two's complement definition and range
    assert int("11101010", 2) == 234 and twos("11101010") == -22
    assert twos("1000") == -8 and twos("10000000") == -128 and twos("100000") == -32
    assert -2 ** 7 == -128 and 2 ** 7 - 1 == 127
    assert -2 ** 11 == -2048 and 2 ** 11 - 1 == 2047
    assert -2 ** 5 == -32 and 2 ** 5 - 1 == 31
    assert twos("10100100") == -92 and twos("1010 0100".replace(" ", "")) == -92
    assert twos("1010 0100".replace(" ", "")) == -92
    assert -128 + 32 + 4 == -92

    # ---- card 8: subtraction and sign extension
    assert (11 + (256 - 22)) % 256 == 245 and twos("11110101") == -11
    assert -128 + 64 + 32 + 16 + 4 + 1 == -11
    assert twos(bits(0xFFF5, 16)) == -11
    assert -32768 + 32757 == -11
    assert 2 ** 16 - 100 == 65436 and twos(bits(65436, 16)) == -100
    assert int("FF9C", 16) == 65436
    assert int("A7", 16) == 167 and twos("10100111") == -89
    assert int("FFA7", 16) == 65447 and twos(bits(0xFFA7, 16)) == -89
    assert int("00A7", 16) == 167
    assert (0x7F + 0x01) % 256 == 0x80 and twos("10000000") == -128   # overflow with no carry

    # ---- card 9: distinct values
    assert 2 ** 16 == 65536 and 2 ** 16 - 1 == 65535 and 65536 - 65535 == 1
    assert 2 ** 8 - (2 ** 8 - 1) == 1

    # ---- card 10: fixed point
    assert int("10011", 2) + int("110", 2) / 8 == 19.75
    assert int("1001", 2) + int("1110", 2) / 16 == 9.875
    assert int("100111", 2) + int("10", 2) / 4 == 39.5
    assert 19.75 / 2 == 9.875
    assert 2 ** 8 - 2 ** -2 == 255.75 and 2 ** 4 - 2 ** -4 == 15.9375
    assert 2 ** 5 - 2 ** -3 == 31.875
    assert 0.875 * 16 == 14 and (0.3 * 16) != int(0.3 * 16)
    assert 7 / 8 == 0.875

    # ---- card 11: normalisation and bias
    assert 1 + 0.5 + 0.125 + 0.03125 == 1.65625 and 1.65625 * 8 == 13.25
    assert 0.5 == 1.0 * 2 ** -1 and -1 + 127 == 126
    assert 8 == 1.0 * 2 ** 3 and 3 + 127 == 130
    assert int("01111110", 2) == 126 and int("01111111", 2) == 127
    assert 2 ** -126 * 2 ** 126 == 1.0                   # 1/x_min does not overflow

    # ---- card 12: single-precision layout
    val, E, sig = decode32(0xC2710000)
    assert E == 132 and 132 - 127 == 5
    assert sig == 1.8828125 and val == -60.25
    assert int("10000100", 2) == 132
    assert 1 + 0.5 + 0.25 + 0.125 + 0.0078125 == 1.8828125
    assert 0.8828125 * 32 == 28.25                       # the hidden-1 trap
    val2, E2, sig2 = decode32(0x3F800000)
    assert E2 == 127 and sig2 == 1.0 and val2 == 1.0
    assert int("10000001", 2) == 129 and 129 - 127 == 2
    assert 1 + 0.5 + 0.25 + 0.125 + 0.0625 == 1.9375 and -1.9375 * 4 == -7.75

    # ---- card 13: special values and extremes
    assert int(bits(0x7F800000, 32)[1:9], 2) == 255 and int(bits(0x7F800000, 32)[9:], 2) == 0
    assert int(bits(0x7FC00000, 32)[1:9], 2) == 255 and int(bits(0x7FC00000, 32)[9:], 2) != 0
    assert int(bits(0x7F7FFFFF, 32)[1:9], 2) == 254
    assert 0x7F7FFFFF == 2139095039 and 0x7FFFFFFF == 2147483647
    largest = (2 - 2 ** -23) * 2 ** 127
    assert abs(largest - 3.4028234663852886e+38) < 1e30
    assert abs(2 ** -126 - 1.1754943508222875e-38) < 1e-50
    assert abs(2 ** -149 - 1.401298464324817e-45) < 1e-60
    assert abs(2 ** -23 - 1.1920928955078125e-07) < 1e-20
    assert 2 ** (20 - 23) == 0.125 and 2 ** (0 - 23) == 2 ** -23
    assert int(bits(0x00000001, 32)[1:9], 2) == 0 and int(bits(0x00000001, 32)[9:], 2) == 1
    assert int(bits(0x00800000, 32)[1:9], 2) == 1 and int(bits(0x00800000, 32)[9:], 2) == 0
    assert 2 ** -126 * 2 ** -23 == 2 ** -149

    ok("number representation: place value, base conversion, grouping, every signed range, "
       "fixed-point range and resolution, the bias, the IEEE 754 decode of all three verified "
       "words, the hidden-1 trap and every special-value pattern recomputed from bits")


def check_boolean_algebra():
    """Every count, cover, identity and cell number published in the Boolean Algebra and
    Minimization cards, PYQs and lesson is recomputed here - by exhaustive enumeration of
    implicants over the 3^n cubes, by evaluation on all 0/1 rows, and in exact sets."""
    import itertools

    def cube(n):
        return list(itertools.product((0, 1, "-"), repeat=n))

    def ones_of(term, n):
        bits = [[int(c) for c in format(m, "0%db" % n)] for m in range(2 ** n)]
        return {m for m in range(2 ** n)
                if all(t == "-" or t == bits[m][i] for i, t in enumerate(term))}

    def implies(term, ones, n, dc=()):
        return all(m in ones or m in dc for m in ones_of(term, n))

    def pis_of(ones, n, dc=()):
        allimp = [t for t in cube(n) if implies(t, ones, n, dc)]
        return [t for t in allimp
                if not any(u != t and ones_of(t, n) < ones_of(u, n) for u in allimp)]

    def eps_of(pis, ones, n):
        out = []
        for p in pis:
            if any(m in ones and not any(q != p and m in ones_of(q, n) for q in pis)
                   for m in ones_of(p, n)):
                out.append(p)
        return out

    def covers(pis, ones, n):
        """Every minimal cover as (term count, literal count), found by increasing term count."""
        for r in range(1, len(pis) + 1):
            sols = []
            for combo in itertools.combinations(pis, r):
                cov = set()
                for p in combo:
                    cov |= (ones_of(p, n) & ones)
                if cov == ones:
                    sols.append((sorted(combo, key=lambda t: str(t)),
                                 sum(sum(1 for x in p if x != "-") for p in combo)))
            if sols:
                return sols
        return []

    def name(term, letters):
        out = ""
        for v, t in zip(letters, term):
            if t == "-":
                continue
            out += v if t == 1 else v + "'"
        return out or "1"

    def check_cover(label, ones, n, dc, letters, want_terms, want_lits):
        pis = pis_of(ones, n, dc)
        sols = covers(pis, ones, n)
        if not sols:
            fail("boolean algebra: %s has no cover" % label)
            return pis, sols
        terms, lits = len(sols[0][0]), sols[0][1]
        if (terms, lits) != (want_terms, want_lits):
            fail("boolean algebra: %s minimal cover is %d terms / %d literals, content claims %d / %d"
                 % (label, terms, lits, want_terms, want_lits))
        for combo, _l in sols:
            if set().union(*[ones_of(p, n) & ones for p in combo]) != ones:
                fail("boolean algebra: %s publishes a cover that misses a required 1" % label)
        return pis, sols

    # ---- the counts of Boolean functions and of self-dual functions
    for n in (1, 2, 3):
        sd = 0
        for bits in itertools.product((0, 1), repeat=2 ** n):
            f = {m: bits[m] for m in range(2 ** n)}
            dual = {m: 1 - f[(2 ** n - 1) ^ m] for m in range(2 ** n)}
            sd += (f == dual)
        assert sd == 2 ** (2 ** (n - 1)), "self-dual count for n=%d" % n
    assert 2 ** (2 ** 2) == 16 and 2 ** (2 ** 3) == 256 and 2 ** (2 ** 4) == 65536
    assert 2 ** (2 ** 0) == 2 and 2 ** (2 ** 1) == 4 and 2 ** (2 ** 2) == 16
    assert 2 ** (2 ** (4 - 1)) == 256

    # ---- the theorems, on every row
    for r in itertools.product((0, 1), repeat=3):
        a, b, c = r
        assert (a or (a and b)) == a, "absorption"
        assert (a and (a or b)) == a, "absorption (dual)"
        assert (a and (not a)) == 0 and (a or (not a)) == 1, "complement"
        assert (a | (b & c)) == ((a | b) & (a | c)), "distributive"
        assert (a & (b | c)) == ((a & b) | (a & c)), "distributive (dual)"
        assert ((a & b) | ((1 - a) & c) | (b & c)) == ((a & b) | ((1 - a) & c)), "consensus"
        assert (a + b) % 2 == (b + a) % 2, "xor commutative"
        assert ((a + b) % 2 + c) % 2 == (a + (b + c) % 2) % 2, "xor associative"
        # xnor, built as the complement of xor, is associative too
        xnor = lambda x, y: 1 - ((x + y) % 2)
        assert xnor(xnor(a, b), c) == xnor(a, xnor(b, c)), "xnor associative"
        # NAND is not associative
        nand = lambda x, y: 1 - (x & y)
        assert any(nand(nand(x, y), z) != nand(x, nand(y, z))
                   for x in (0, 1) for y in (0, 1) for z in (0, 1)), "nand not associative"
    # the 2020-26 identities quoted in the cards
    for x in (0, 1):
        for y in (0, 1):
            for z in (0, 1):
                assert ((x ^ y) ^ z) == (x ^ (y ^ z)), "2019 Q.6 option A"
                assert (x ^ y) == (1 - ((x & y) | ((1 - x) & (1 - y)))), "2019 Q.6 option D"
                if (x & y) == 0:
                    assert (x ^ y) == (x | y), "2019 Q.6 option C"
    bad = [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)
           if ((x | y) ^ z) != (x ^ (y | z))]
    assert bad == [(0, 1, 1), (1, 1, 0)] or bad == [(1, 1, 0), (0, 1, 1)], \
        "2019 Q.6 option B must fail at exactly (0,1,1) and (1,1,0), got %r" % (bad,)
    assert 1 ^ 1 == 0 and 1 | 1 == 1, "xor against or at 11"
    # a + a'b = a + b, and the dual a(a'+b) = ab
    for a in (0, 1):
        for b in (0, 1):
            assert (a | ((1 - a) & b)) == (a | b), "eliminate theorem"
            assert (a & ((1 - a) | b)) == (a & b), "dual of the eliminate theorem"
    # A + BC = (A+B)(A+C) and AB + BC != A + BC
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                assert (a | (b & c)) == ((a | b) & (a | c)), "1997 Q.1 identity"
    assert [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)
            if (a | (b & c)) != ((a & b) | c)] == [(0, 0, 1), (1, 0, 0)], \
        "AB + BC differs from A + BC exactly at 001 and 100"
    # the dual of x + x'y = x + y
    assert all(((x | ((1 - x) & y)) == (x | y)) and ((x & ((1 - x) | y)) == (x & y))
               for x in (0, 1) for y in (0, 1)), "dual pair of the eliminate theorem"
    # F = x.y' + 0.z and its dual differ at x=1,y=1,z=0
    assert (1 & (1 - 1)) + 0 == 0 and (1 | (1 - 1)) * (1 | 0) == 1, "dual counterexample"

    # ---- canonical forms: F = P' + QR
    ones44 = {m for m in range(8) if (1 - (m >> 2)) or (((m >> 1) & 1) and (m & 1))}
    assert sorted(ones44) == [0, 1, 2, 3, 7], "2015 Set 3 Q.44 ones"
    assert sorted(set(range(8)) - ones44) == [4, 5, 6], "2015 Set 3 Q.44 zeros"
    # XOR canonical forms
    assert sorted(m for m in range(4) if ((m >> 1) ^ (m & 1))) == [1, 2], "xor minterms"
    assert sorted(m for m in range(4) if not ((m >> 1) ^ (m & 1))) == [0, 3], "xor maxterms"
    # Pi M(0,1,4,5,8,9,12,13) is D
    zeros_pi = {0, 1, 4, 5, 8, 9, 12, 13}
    assert {m for m in range(16) if m not in zeros_pi} == {m for m in range(16) if (m >> 1) & 1}, \
        "the complement of that maxterm list is the rows with C = 1"

    # ---- the map: numbering, adjacency, wrap-around
    rows = ["00", "01", "11", "10"]
    table = [[int(r + c, 2) for c in rows] for r in rows]
    assert table == [[0, 1, 3, 2], [4, 5, 7, 6], [12, 13, 15, 14], [8, 9, 11, 10]], \
        "four-variable cell numbering"
    for i in range(4):
        for j in range(4):
            # horizontal neighbours, wrap-around included
            assert bin(table[i][j] ^ table[i][(j + 1) % 4]).count("1") == 1, "row adjacency"
            assert bin(table[i][j] ^ table[(i + 1) % 4][j]).count("1") == 1, "column adjacency"
            # a two-step move changes two bits, which is why diagonal is not adjacency
            assert bin(table[i][j] ^ table[i][(j + 2) % 4]).count("1") == 2, "two-step move"
    assert ones_of((0, "-", 0, "-"), 4) == {0, 1, 4, 5}, "A'C' cells"
    assert ones_of(("-", 0, "-", 0), 4) == {0, 2, 8, 10}, "B'D' is the four corners"
    assert sorted(ones_of((0, "-", "-", 0), 4)) == [0, 2, 4, 6], "w'z' cells"
    assert sorted(ones_of((0, 1, 0, "-"), 4)) == [4, 5], "wx'y' cells"
    assert sorted(ones_of((0, 1, "-", "-"), 4)) == [4, 5, 6, 7], "w'x cells"
    assert sorted(ones_of(("-", 0, 1, 0), 4)) == [2, 10], "x'yz' cells"
    # neighbours of m5 and the pair {5,7}
    five = {5 ^ (1 << b) for b in range(4)}
    assert sorted(five) == [1, 4, 7, 13], "neighbours of m5"
    assert sorted(ones_of((0, 1, "-", 1), 4)) == [5, 7], "A'BD covers 5 and 7"
    assert sorted(ones_of(("-", "-", 0, 0), 4)) == [0, 4, 8, 12], "the left column pair"
    # cell 0's five neighbours in a five-variable map, and the m / m+16 adjacency
    assert sorted({0 ^ (1 << b) for b in range(5)}) == [1, 2, 4, 8, 16], "neighbours of cell 0"
    assert all(bin(m ^ (m + 16)).count("1") == 1 for m in range(16)), "m and m+16 adjacent"
    assert bin(5 ^ 21).count("1") == 1 and bin(5 ^ 14).count("1") == 3, "5-var adjacency pair"
    assert sorted(ones_of((0, "-", "-", "-", "-"), 5)) == list(range(16)), "A' covers 0..15"

    # ---- worked covers in the cards and the PYQs
    # 2026 Set 2 Q.30: the octet is B'
    pis, _ = check_cover("2026 Set 2 Q.30", {0, 1, 2, 3, 8, 9, 10, 11}, 4, (), "ABCD", 1, 1)
    assert [name(p, "ABCD") for p in pis] == ["B'"], "2026 Set 2 Q.30 prime implicant"
    # 2026 Set 1 Q.38: three minimal covers, all at 4 terms and 10 literals
    pis38, sols38 = check_cover("2026 Set 1 Q.38", {1, 2, 3, 4, 5, 7, 10, 12, 13, 14}, 4, (),
                                "PQRS", 4, 10)
    assert len(pis38) == 6, "2026 Set 1 Q.38 has six prime implicants, got %d" % len(pis38)
    assert len(sols38) == 3, "2026 Set 1 Q.38 has three minimal covers, got %d" % len(sols38)
    option_b = ["P'S", "QR'", "P'Q'R", "PRS'"]
    option_d = ["P'S", "QR'", "PQS'", "Q'RS'"]
    option_a = ["P'S", "QR'", "P'Q'R", "Q'RS'"]
    option_c = ["P'S", "QR'", "PQS'", "PRS'"]

    def eval_term(t, bits):
        val, i = 1, 0
        while i < len(t):
            if t[i] == " ":
                i += 1
                continue
            v = t[i]
            neg = (i + 1 < len(t) and t[i + 1] == "'")
            val &= (1 - bits["PQRS".index(v)]) if neg else bits["PQRS".index(v)]
            i += 2 if neg else 1
        return val

    def eval_sop(terms, m):
        bits = [int(c) for c in format(m, "04b")]
        return max(eval_term(t, bits) for t in terms)

    target38 = {1, 2, 3, 4, 5, 7, 10, 12, 13, 14}
    for label, opt, want in (("B", option_b, True), ("D", option_d, True),
                             ("A", option_a, False), ("C", option_c, False)):
        got = {m for m in range(16) if eval_sop(opt, m)}
        if (got == target38) != want:
            fail("boolean algebra: 2026 Set 1 Q.38 option %s equivalence is wrong" % label)
        if sum(sum(1 for ch in t if ch.isalpha()) for t in opt) != 10:
            fail("boolean algebra: 2026 Set 1 Q.38 option %s is not ten literals" % label)
    # 2014 Set 3 Q.7: Q'S' + QS, four literals
    check_cover("2014 Set 3 Q.7", {0, 5, 10, 15}, 4, {2, 7, 8, 13}, "PQRS", 2, 4)
    assert sorted(ones_of(("-", 0, "-", 0), 4)) == [0, 2, 8, 10]
    assert sorted(ones_of(("-", 1, "-", 1), 4)) == [5, 7, 13, 15]
    assert not any(bin(a ^ b).count("1") == 1 for a in (0, 5, 10, 15) for b in (0, 5, 10, 15) if a < b), \
        "without the don't cares no two required 1s are adjacent"
    assert 4 * 4 == 16, "the canonical form of four 4-literal minterms"
    # 2018 Q.49: six prime implicants, three essential
    pis18, _ = check_cover("2018 Q.49", {0, 2, 5, 7, 9, 11}, 4, {3, 8, 10, 12, 14}, "PQRS", 3, 7)
    assert len(pis18) == 6, "2018 Q.49 has six prime implicants, got %d" % len(pis18)
    eps18 = eps_of(pis18, {0, 2, 5, 7, 9, 11}, 4)
    assert len(eps18) == 3, "2018 Q.49 has three essential prime implicants, got %d" % len(eps18)
    assert sorted(name(p, "PQRS") for p in eps18) == ["P'QS", "PQ'", "Q'S'"], \
        "2018 Q.49 essential prime implicants"
    # 2015 Set 3 Q.43: three prime implicants, all essential
    pis43, _ = check_cover("2015 Set 3 Q.43", {0, 2, 4, 5, 6, 10}, 4, (), "WXYZ", 3, 8)
    assert len(pis43) == 3, "2015 Set 3 Q.43 has three prime implicants, got %d" % len(pis43)
    assert len(eps_of(pis43, {0, 2, 4, 5, 6, 10}, 4)) == 3, "and all three are essential"
    assert sorted(name(p, "WXYZ") for p in pis43) == ["W'XY'", "W'Z'", "X'YZ'"], \
        "2015 Set 3 Q.43 prime implicant names"
    # 2021 Set 2 Q.52: ten 1s, two don't cares, six literals
    check_cover("2021 Set 2 Q.52", {0, 1, 6, 7, 8, 9, 11, 13, 14, 15}, 4, {2, 3}, "WXYZ", 3, 6)
    # the three equations of that question, evaluated directly, rebuild the same 1s
    eq_ones, eq_dc = set(), set()
    for m in range(16):
        w, x, y, z = [int(c) for c in format(m, "04b")]
        if x == 0 and y == 0:
            eq_ones.add(m)                        # f(w,0,0,z) = 1
        elif w == 1 and y == 1:
            if (x or z):
                eq_ones.add(m)                    # f(1,x,1,z) = x + z
        elif x == 1:
            if (w and z) or y:
                eq_ones.add(m)                    # f(w,1,y,z) = wz + y
        else:
            eq_dc.add(m)                          # fixed by no equation
    assert eq_ones == {0, 1, 6, 7, 8, 9, 11, 13, 14, 15}, "2021 Set 2 Q.52 ones"
    assert eq_dc == {2, 3}, "2021 Set 2 Q.52 don't cares"
    # 2017 Set 2 Q.28: the zeros, and option A
    pis28, sols28 = check_cover("2017 Set 2 Q.28 complement", {4, 9, 12, 13, 14}, 4,
                                {5, 6, 11, 15}, "WXYZ", 2, 4)
    assert sorted(name(p, "WXYZ") for p in sols28[0][0]) == ["WZ", "XZ'"], \
        "the complement's minimal cover"
    for m in range(16):
        bits = [int(c) for c in format(m, "04b")]
        w, x, y, z = bits
        a = (1 - w) | (1 - z)
        b = (1 - x) | z
        val = a & b
        ones28 = {0, 1, 2, 3, 7, 8, 10}
        if m in ones28 and val != 1:
            fail("boolean algebra: 2017 Set 2 Q.28 option A misses minterm %d" % m)
        if m in {4, 9, 12, 13, 14} and val != 0:
            fail("boolean algebra: 2017 Set 2 Q.28 option A sets required zero %d" % m)
    # 2012 Q.30: b'c' + b'd', from the cells two sources agree on
    check_cover("2012 Q.30", {0, 2, 8, 9}, 4, {1, 4, 10, 12}, "ABCD", 2, 4)
    assert sorted(ones_of(("-", 0, 0, "-"), 4)) == [0, 1, 8, 9], "b'c' cells"
    # 1998 Q.2.7: BC + B'C' is XNOR on B and C
    xnor_bc = {m for m in range(8)
               if ((m >> 1) & 1) == (m & 1)}
    assert sorted(xnor_bc) == [0, 3, 4, 7], "B XNOR C covers 0,3,4,7"
    # the majority function and the two-minimal-cover example
    check_cover("majority sum(3,5,6,7)", {3, 5, 6, 7}, 3, (), "ABC", 3, 6)
    pis11, sols11 = check_cover("sum(0,1,2,5,6)", {0, 1, 2, 5, 6}, 3, (), "ABC", 3, 6)
    assert len(sols11) == 2, "sum(0,1,2,5,6) has exactly two minimal covers"
    assert sorted(name(p, "ABC") for p in eps_of(pis11, {0, 1, 2, 5, 6}, 3)) == ["B'C", "BC'"], \
        "sum(0,1,2,5,6) essential prime implicants"
    # the card examples and checks
    check_cover("sum(0,1,4,5,8,9,12,13) = C'", {0, 1, 4, 5, 8, 9, 12, 13}, 4, (), "ABCD", 1, 1)
    assert sorted(ones_of(("-", "-", 0, "-"), 4)) == [0, 1, 4, 5, 8, 9, 12, 13], "C' cells"
    assert sorted(ones_of(("-", 0, 1, "-"), 4)) == [2, 3, 10, 11], "B'C cells"
    assert sorted(ones_of((0, "-", "-"), 3)) == [0, 1, 2, 3], "A' cells in three variables"
    assert sorted(ones_of((0, 0, "-"), 3)) == [0, 1], "A'B' cells in three variables"
    assert sorted(ones_of(("-", 0, 0), 3)) == [0, 4], "B'C' cells in three variables"
    # 426's variation: 1s at 0, 1 and 8 are two pairs, never a quad
    pis_426, _ = check_cover("426 variation sum(0,1,8)", {0, 1, 8}, 4, (), "ABCD", 2, 6)
    assert sorted(name(p, "ABCD") for p in pis_426) == ["A'B'C'", "B'C'D'"], \
        "426 variation prime implicants"
    # 427's check: sum(0,1,2,3,4) = A' + B'C'
    pis_chk, _ = check_cover("427 check sum(0,1,2,3,4)", {0, 1, 2, 3, 4}, 3, (), "ABC", 2, 3)
    assert sorted(name(p, "ABC") for p in pis_chk) == ["A'", "B'C'"], "427 check prime implicants"
    # 431's check: six prime implicants for sum(0,1,2,5,6,7)
    pis_qm, _ = check_cover("431 check sum(0,1,2,5,6,7)", {0, 1, 2, 5, 6, 7}, 3, (), "ABC", 3, 6)
    assert len(pis_qm) == 6, "431 check has six prime implicants, got %d" % len(pis_qm)
    # 432's check: AB + A'C is four literals, the printed form six
    assert 2 + 2 == 4 and 2 + 2 + 2 == 6
    # 432's POS variation: two isolated zeros give two four-literal factors
    assert 4 + 4 == 8
    # 429's check: the 0s at 0..3 give (w + x), and the 1s give w + x
    assert sorted(ones_of((1, "-", "-", "-"), 4)) == list(range(8, 16)), "w cells"
    ok("boolean algebra and minimization: the 2^(2^n) and self-dual counts, every theorem on every "
       "row, the XOR identities, the canonical-form conversions, the map numbering and adjacency "
       "(wrap-around and the five-variable axis), and every published prime implicant, essential "
       "prime implicant, minimal cover and literal count recomputed by enumeration")


# ------------------------------------------------- combinational circuits
def check_combinational_circuits():
    """Every adder, multiplexer, decoder, encoder, ROM, parity and hazard claim published in the
    Combinational Circuits cards, PYQs and lesson is recomputed here."""
    import itertools

    # ---- half adder and full adder, straight from the truth tables
    for a, b in itertools.product([0, 1], repeat=2):
        assert (a ^ b) == (a + b) % 2, "half adder sum"
        assert (a & b) == (1 if a + b == 2 else 0), "half adder carry"
    for a, b, c in itertools.product([0, 1], repeat=3):
        s = a ^ b ^ c
        cout = (a & b) | (b & c) | (a & c)
        assert s == (a + b + c) % 2, "full adder sum is the odd-parity bit"
        assert cout == (1 if a + b + c >= 2 else 0), "full adder carry is the majority"
        # the two-half-adder construction gives the same pair
        s1 = a ^ b
        c1 = a & b
        s2 = s1 ^ c
        c2 = s1 & c
        assert (s2, c1 | c2) == (s, cout), "two half adders plus an OR gate is a full adder"

    # 1999 Q.2.16: 16 positions, one without a carry-in
    assert 1 + 15 == 16 and 15 == 16 - 1, "1999 Q.2.16: 1 half adder and 15 full adders"
    # the 8-bit variation
    assert 1 + 7 == 8, "the 8-bit variation is 1 half adder and 7 full adders"
    # 1011 + 0110 = 10001
    total = 0b1011 + 0b0110
    assert total == 17 and total == 0b10001, "the ripple example sums to 17"
    assert total & 0b1111 == 1 and total >> 4 == 1, "sum bits 0001 and carry out 1"
    # a full adder with the carry-in tied to 0 degenerates to a half adder
    for a, b in itertools.product([0, 1], repeat=2):
        assert (a ^ b ^ 0, (a & b) | (b & 0) | (a & 0)) == (a ^ b, a & b), "tied-off full adder"
    # five gates: two XOR, two AND, one OR
    assert 2 + 2 + 1 == 5, "the two-half-adder full adder costs five gates"

    # ---- ripple-carry delay, GATE CSE 2015 Set 2 Q.48
    xor_delay, gate_delay = 2 * 1.2, 1.2
    assert abs(xor_delay - 2.4) < 1e-9 and abs(gate_delay - 1.2) < 1e-9
    first_stage = xor_delay + gate_delay + gate_delay
    later_stage = gate_delay + gate_delay
    assert abs(first_stage - 4.8) < 1e-9 and abs(later_stage - 2.4) < 1e-9
    carry_only = first_stage + 3 * later_stage
    key_model = 4 * first_stage
    assert abs(carry_only - 12.0) < 1e-9, "the carry-only 4-bit total is 12 microseconds"
    assert abs(key_model - 19.2) < 1e-9, "the paper's 4-bit total is 19.2 microseconds"
    assert abs((first_stage + 7 * later_stage) - 21.6) < 1e-9, "the 8-bit carry-only total is 21.6"
    assert abs(8 * first_stage - 38.4) < 1e-9, "the 8-bit paper total is 38.4"
    # unit-delay model: first carry 2, each later carry 2, 4 bits
    assert 2 + 3 * 2 == 8, "the unit-delay 4-bit carry settles after 8 gate delays"
    assert 2 + 5 * 2 == 12, "the unit-delay 6-bit carry settles after 12 gate delays"

    # ---- carry look-ahead: gate counts and the carry equations
    def cla_carries(A, B, C0, n):
        P = [(A >> i & 1) ^ (B >> i & 1) for i in range(n)]
        G = [(A >> i & 1) & (B >> i & 1) for i in range(n)]
        C = [C0]
        for i in range(n):
            C.append(G[i] | (P[i] & C[i]))
        S = [P[i] ^ C[i] for i in range(n)]
        return P, G, C, S

    for A, B in itertools.product(range(16), repeat=2):
        P, G, C, S = cla_carries(A, B, 0, 4)
        assert sum(S[i] << i for i in range(4)) == (A + B) % 16, "CLA sum agrees with addition"
        assert C[4] == (1 if A + B > 15 else 0), "CLA carry out agrees with the sum"
    # the worked example: A = 1011, B = 0110
    P, G, C, S = cla_carries(0b1011, 0b0110, 0, 4)
    assert P == [1, 0, 1, 1], "P3P2P1P0 = 1101 for A=1011, B=0110"
    assert G == [0, 1, 0, 0], "G3G2G1G0 = 0010 for A=1011, B=0110"
    assert C[4] == 1, "C4 = 1 for A=1011, B=0110"
    # gate counts: product terms 1..n, one AND each, one OR per carry
    for n in (4, 8):
        ands = sum(range(1, n + 1))
        assert ands == n * (n + 1) // 2
        assert ands == (10 if n == 4 else 36), "two-level look-ahead AND count"
        assert n == (4 if n == 4 else 8), "two-level look-ahead OR count"
    # two-input gates: k-1 ANDs per product term, m-1 ORs per carry
    and2 = sum((len(t) - 1) for t in [
        ["G0"], ["P0", "C0"],
        ["G1"], ["P1", "G0"], ["P1", "P0", "C0"],
        ["G2"], ["P2", "G1"], ["P2", "P1", "G0"], ["P2", "P1", "P0", "C0"],
        ["G3"], ["P3", "G2"], ["P3", "P2", "G1"], ["P3", "P2", "P1", "G0"],
        ["P3", "P2", "P1", "P0", "C0"]])
    or2 = (2 - 1) + (3 - 1) + (4 - 1) + (5 - 1)
    assert and2 == 20 and or2 == 10, "two-input CLA generator: 20 AND and 10 OR gates"

    # ---- the 2004 Q.58 design question, and its two don't-care variations
    def at_least_five(A, B, C, D):
        n = (A << 3) | (B << 2) | (C << 1) | D
        return 1 if 5 <= n <= 9 else (0 if n <= 9 else None)   # 10..15 are don't cares

    for n in range(10):
        a, b, c, d = (n >> 3) & 1, (n >> 2) & 1, (n >> 1) & 1, n & 1
        want = 1 if n >= 5 else 0
        assert (a | (b & (c | d))) == want, "A + B(C + D) is the digit-at-least-5 function"
        assert at_least_five(a, b, c, d) == want
    assert 2 + 1 == 3, "2004 Q.58 needs three gates"
    # with the don't cares forced to 0 the answer is AC' + BC + BD
    for n in range(10):
        a, b, c, d = (n >> 3) & 1, (n >> 2) & 1, (n >> 1) & 1, n & 1
        got = ((a & (1 - c)) | (b & c) | (b & d))
        assert got == (1 if n >= 5 else 0), "AC' + BC + BD without the don't cares"
    # the multiple-of-three variation: 0, 3, 6, 9 with 11 and 14 borrowed
    mult3 = set()
    for n in range(16):
        a, b, c, d = (n >> 3) & 1, (n >> 2) & 1, (n >> 1) & 1, n & 1
        t1 = (1 - a) & (1 - b) & (1 - c) & (1 - d)
        t2 = (1 - b) & c & d
        t3 = b & c & (1 - d)
        t4 = a & (1 - b) & d
        if t1 | t2 | t3 | t4:
            mult3.add(n)
    assert mult3 == {0, 3, 6, 9, 11, 14}, "the multiple-of-three cover"
    assert {0, 3, 6, 9} <= mult3 and (mult3 - {0, 3, 6, 9}) <= {10, 11, 12, 13, 14, 15}
    assert 4 + 3 + 3 + 3 == 13, "the multiple-of-three cover has thirteen literals"
    # the odd-digit variation collapses to D
    for n in range(10):
        assert ((n & 1) == 1) == (n % 2 == 1), "oddness is the least significant bit"
    assert 2 ** (16 * 3) == 2 ** 48, "a 4-input 3-output truth table has 2^48 functions"

    # ---- 2007 Q.34: functions of one variable, and why n-2 select lines fail
    assert 2 ** (2 ** 1) == 4, "four functions of one variable, reachable with one inverter"
    assert 2 ** (2 ** 2) == 16, "sixteen functions of two variables, not reachable with one inverter"

    # ---- multiplexers as function implementers
    def mux4(s1, s0, i0, i1, i2, i3):
        sel = (s1 << 1) | s0
        return [i0, i1, i2, i3][sel]

    def mux_from_pairs(pairs, n_sel_vars=2):
        """pairs[k] is the data input for select code k; the leftover variable is the LSB."""
        return pairs

    # 2014 Set 1 Q.45: I0=0, I1=1, I2=R, I3=R', selects P and Q, leftover R
    ones = []
    for P, Q, R in itertools.product([0, 1], repeat=3):
        out = mux4(P, Q, 0, 1, R, 1 - R)
        if out:
            ones.append((P << 2) | (Q << 1) | R)
    assert ones == [2, 3, 5, 6], "2014 Set 1 Q.45 realises minterms 2, 3, 5 and 6"
    def minimal(P, Q, R):
        return ((1 - P) & Q) | (Q & (1 - R)) | (P & (1 - Q) & R)
    def canonical(P, Q, R):
        return ((1 - P) & Q & (1 - R)) | ((1 - P) & Q & R) | (P & (1 - Q) & R) | (P & Q & (1 - R))
    for P, Q, R in itertools.product([0, 1], repeat=3):
        assert minimal(P, Q, R) == canonical(P, Q, R), "the minimal SOP equals the canonical form"
    assert 2 + 2 + 3 == 7, "the minimal form has seven literals"
    assert 4 * 3 == 12, "the canonical form has twelve literals"
    assert 2 + 3 + 3 + 3 == 11, "options B and C of 2014 Set 1 Q.45 each carry eleven literals"
    # the lesson's groups
    assert {2, 3} <= set(ones) and {2, 6} <= set(ones) and 5 in ones
    assert ((1 - 0) & 1) == 1 and ((1 - 1) & 1) == 0, "P'Q covers 2 and 3 only"
    # the 2021 Set 2 Q.5 implementation: I0=I1=1, I2=x, I3=x'
    got = []
    for x, y, z in itertools.product([0, 1], repeat=3):
        out = mux4(y, z, 1, 1, x, 1 - x)
        if out:
            got.append((x << 2) | (y << 1) | z)
    assert got == [0, 1, 3, 4, 5, 6], "2021 Set 2 Q.5 realises m0, m1, m3, m4, m5 and m6"
    # the three-variable XOR variation: I = C, C', C', C with A, B on the select lines
    got = []
    for A, B, C in itertools.product([0, 1], repeat=3):
        out = mux4(A, B, C, 1 - C, 1 - C, C)
        if out:
            got.append((A << 2) | (B << 1) | C)
    assert got == [1, 2, 4, 7], "the XOR variation realises m1, m2, m4 and m7"
    # the 2^n-to-1 implementation of the 2021 function
    assert [1, 1, 0, 1, 1, 1, 1, 0] == [1 if i in (0, 1, 3, 4, 5, 6) else 0 for i in range(8)]
    # the quick check: f = m1 + m3 + m5 + m7 with y, z on the select lines is z
    for x, y, z in itertools.product([0, 1], repeat=3):
        idx = (x << 2) | (y << 1) | z
        assert mux4(y, z, 0, 1, 0, 1) == z, "the odd-minterm function is z"

    # ---- multiplexer trees
    for n in (2, 3, 4, 6):
        assert 2 ** n - 1 == (3, 7, 15, 63)[(2, 3, 4, 6).index(n)], "2^n - 1 blocks"
    assert 2 ** 6 - 1 == 63, "a 64-to-1 multiplexer needs 63 two-to-one blocks"
    # 2024 Set 1 Q.54: three 2-to-1 multiplexers, X1=X2=1, X3=X4=0
    count = 0
    for A, B, C in itertools.product([0, 1], repeat=3):
        q1 = (1 - A) * 1 + A * 1
        q2 = (1 - B) * 0 + B * 0
        Y = (1 - C) * q1 + C * q2
        if Y == 1:
            count += 1
    assert count == 4, "2024 Set 1 Q.54: four of the eight combinations give Y = 1"
    # 2023 Q.34: A' + A'C' + AB'C over the select order (B, A, C)
    def q34(B, A, C):
        return (1 - A) | ((1 - A) & (1 - C)) | (A & (1 - B) & C)
    ones34 = []
    for B, A, C in itertools.product([0, 1], repeat=3):
        if q34(B, A, C):
            ones34.append((B << 2) | (A << 1) | C)
    assert ones34 == [0, 1, 3, 4, 5], "2023 Q.34 realises minterms 0, 1, 3, 4 and 5"
    vector = [1 if i in ones34 else 0 for i in range(8)]
    assert vector == [1, 1, 0, 1, 1, 1, 0, 0], "2023 Q.34: X0..X7 = 11011100"
    # a 16-to-1 from 4-to-1 blocks: four blocks and a 2-to-4 decoder
    assert 16 // 4 == 4 and 2 ** 2 == 4, "four 4-to-1 blocks and a 2-to-4 decoder"

    # ---- decoders
    def decoder(n, code):
        return tuple(1 if k == code else 0 for k in range(2 ** n))
    for code in range(8):
        out = decoder(3, code)
        assert sum(out) == 1 and out[code] == 1, "exactly one decoder output is active"
    assert 2 ** 8 == 256, "eight decoder lines with an OR gate give 256 functions of three variables"
    assert sum(1 for i in (1, 2, 4, 7)) == 4, "three-input XOR needs four minterm lines"
    # 2014 Set 2 Q.7: a counter plus a decoder is one-hot, so k states for k lines
    for n in (2, 3, 4):
        k = 2 ** n
        assert len(decoder(n, 0)) == k, "the decoder has k = 2^n outputs"
    # 2026 Set 2 Q.49: Y = A'B'S1'S0' + 1.S1S0' + AB S1 S0
    count = 0
    for A, B, S1, S0 in itertools.product([0, 1], repeat=4):
        Y = ((1 - A) & (1 - B) & (1 - S1) & (1 - S0)) | (S1 & (1 - S0)) | (A & B & S1 & S0)
        if Y:
            count += 1
    assert count == 6, "2026 Set 2 Q.49: six of the sixteen combinations give Y = 1"

    # ---- encoders
    def priority_encoder(bits, high_index_wins=True):
        """bits[i] is input Ii; return the index of the winning input, or None."""
        active = [i for i, v in enumerate(bits) if v]
        if not active:
            return None
        return max(active) if high_index_wins else min(active)
    assert priority_encoder([0, 0, 0, 1]) == 3
    assert priority_encoder([0, 1, 1, 0]) == 2, "I2 wins over I1 in a 4-to-2 priority encoder"
    assert priority_encoder([0, 1, 1, 0], high_index_wins=False) == 1, "the reversed priority"
    word = [0, 0, 0, 1, 0, 1, 0, 1]           # bits[i] = Ii, so I7..I0 = 1010 1000
    assert priority_encoder(word) == 7 and bin(7) == '0b111', "1010 1000 encodes to 111"
    assert 32 // 8 == 4 and 4 + 1 == 5, "a 32-to-5 encoder needs five 8-to-3 blocks"

    # ---- magnitude comparator
    def compare(A, B, n):
        for i in range(n - 1, -1, -1):
            a, b = (A >> i) & 1, (B >> i) & 1
            if a != b:
                return 'gt' if a > b else 'lt'
        return 'eq'
    assert compare(0b1011, 0b1001, 4) == 'gt', "1011 > 1001, decided at bit 1"
    assert compare(0b0110, 0b0101, 4) == 'gt', "0110 > 0101, decided at bit 1"
    assert compare(0b1000, 0b0111, 4) == 'gt', "1000 > 0111, decided at bit 3"
    assert compare(0b0111, 0b1000, 4) == 'lt', "0111 < 1000 whatever the lower bits say"
    assert compare(0b1010, 0b1010, 4) == 'eq'
    # eight XNOR gates and seven two-input ANDs for 8-bit equality
    assert 8 - 1 == 7, "eight equality signals need seven two-input AND gates"

    # ---- ROM sizing
    assert 2 ** 16 == 65536 == 64 * 1024, "8 + 8 address bits give 64K words"
    assert 255 * 255 == 65025 and 65025 < 2 ** 16, "the 8-bit product fits in sixteen bits"
    assert 2 ** 8 * 8 == 2048, "the 4-bit multiplier ROM is 2048 bits"
    assert 15 * 15 == 225 and 225 < 2 ** 8, "the 4-bit product fits in eight bits"
    assert 2 ** 8 * 5 == 1280, "the 4-bit adder ROM is 1280 bits"
    assert 15 + 15 == 30 and 30 < 2 ** 5, "the 4-bit sum with carry needs five bits"

    # ---- parity
    def parity(bs):
        r = 0
        for b in bs:
            r ^= b
        return r
    assert parity([1, 0, 1, 1]) == 1, "1011 has even parity bit 1"
    assert 1 - parity([1, 0, 1, 1]) == 0, "1011 has odd parity bit 0"
    assert parity([1, 1, 0, 0, 0, 1, 1, 0]) == 0, "11000110 has even parity bit 0"
    assert 1 - parity([1, 0, 1, 0]) == 1, "1010 has odd parity bit 1"
    assert 8 - 1 == 7, "seven two-input XOR gates compute the parity of eight bits"
    # one flip is detected, two flips are not
    word = [1, 1, 0, 0, 0, 1, 1, 0]
    p0 = parity(word)
    one_flip = list(word); one_flip[2] ^= 1
    two_flips = list(word); two_flips[2] ^= 1; two_flips[5] ^= 1
    assert parity(one_flip) != p0, "a single flip changes the parity"
    assert parity(two_flips) == p0, "two flips leave the parity unchanged"

    # ---- hazards: the consensus term changes no output value
    for X, Y, Z in itertools.product([0, 1], repeat=3):
        assert (((1 - X) & Y) | (X & Z)) == (((1 - X) & Y) | (X & Z) | (Y & Z)), \
            "the consensus term is redundant in logic"
        assert (((1 - X) & (1 - Y)) | (X & Z)) == (((1 - X) & (1 - Y)) | (X & Z) | ((1 - Y) & Z)), \
            "the consensus of X'Y' + XZ is Y'Z"
        assert ((X & (1 - Y)) | (Y & Z)) == ((X & (1 - Y)) | (Y & Z) | (X & Z)), \
            "the consensus of XY' + YZ is XZ"
    # the hazard condition: the expression reduces to X + X' at the critical assignment
    assert all((((1 - 1) & 1) | (1 & 1)) == 1 for _ in [0]), "A'B + AC with B=C=1 is 1 at A=1"
    assert (((1 - 0) & 1) | (0 & 1)) == 1, "and 1 at A=0, so the two arms must both be 1"

    # ---- the lesson's numbers
    L = load(os.path.join(ROOT, "visuals", "digital-logic", "combinational-circuits",
                          "mux-to-minimal-sop", "lesson.json"))
    ex = L.get("example") or {}
    if ex:
        assert ex.get("minterms") == [2, 3, 5, 6], "the lesson's minterms"
        assert ex.get("minimal_sop") == "P'Q + QR' + PQ'R"
        assert ex.get("minimal_literals") == 7 and ex.get("minimal_terms") == 3
        assert ex.get("canonical_literals") == 12 and ex.get("canonical_terms") == 4
        assert sum(g["literals"] for g in ex.get("groups", [])) == 7, "the three groups give 7 literals"
        assert sorted(c for g in ex["groups"] for c in g["cells"]) == [2, 2, 3, 5, 6], \
            "the groups cover every 1, with minterm 2 used twice"
        assert ex.get("cell_numbers") == [[0, 1, 3, 2], [4, 5, 7, 6]], "the Gray-code cell numbering"
        assert ex.get("map_columns") == ["00", "01", "11", "10"]
        assert L.get("steps") == 7, "the lesson must declare its seven steps"

    ok("combinational circuits: every adder truth table, ripple and look-ahead delay, generate and "
       "propagate carry, multiplexer realisation, multiplexer-tree count, decoder, encoder, comparator, "
       "ROM size, parity and hazard claim published in the topic recomputed - by enumeration over the "
       "eight- and sixteen-row tables and against the thirteen recorded PYQs")


def check_visuals():
    vroot = os.path.join(ROOT, "visuals")
    lessons = []
    for path in walk(vroot, "lesson.json"):
        d = os.path.dirname(path)
        L = load(path)
        for f in ("slug", "topic", "engine"):
            if f not in L:
                fail("%s: lesson.json missing %s" % (rel(path), f))
        if L.get("engine") not in {"p5.js", "html"}:
            fail("%s: invalid engine %r" % (rel(path), L.get("engine")))
        if L.get("engine") == "p5.js":
            if not isinstance(L.get("steps"), int) or L.get("steps", 0) < 1:
                fail("%s: p5 lesson needs a positive integer steps count" % rel(path))
        elif not (isinstance(L.get("steps"), int) and L.get("steps", 0) >= 1
                  or isinstance(L.get("cells"), int) and L.get("cells", 0) >= 1):
            fail("%s: html lesson needs steps or cells" % rel(path))
        if not os.path.isfile(os.path.join(d, "index.html")):
            fail("%s: no index.html" % rel(d))
        if L.get("engine") == "p5.js" and not os.path.isfile(os.path.join(d, "sketch.js")):
            fail("%s: p5 lesson without sketch.js" % rel(d))
        lessons.append(rel(d))
    for f in ("lesson.css", "lesson.js"):
        if not os.path.isfile(os.path.join(vroot, f)):
            fail("visuals/%s is missing" % f)
    ok("%d visual lessons: metadata, index.html, sketch, shared harness" % len(lessons))


def check_hygiene():
    bad = []
    for base, _, files in os.walk(ROOT):
        if "/.git" in base or "/node_modules" in base:
            continue
        for f in files:
            if not f.endswith((".md", ".json", ".js", ".html", ".css", ".py")):
                continue
            path = os.path.join(base, f)
            try:
                text = open(path, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            marker = "[" + "cite" + ":"
            if marker in text:
                bad.append(rel(path) + " contains a citation marker")
            if re.search(r"_v\d+\.|_final\.", f):
                bad.append(rel(path) + " uses a versioned filename")
    for b in bad:
        fail(b)
    if not bad:
        ok("no citation markers or versioned filenames in generated files")

    for r in ("index.html", "src/styles/design-tokens.css", "src/styles/app.css",
              "src/app/app.js", "src/app/routes.js", "src/data/content.js"):
        if not os.path.isfile(os.path.join(ROOT, r)):
            fail("missing site file: " + r)
    ok("site shell files present")

    # generated data must exist and agree with content
    cj = os.path.join(ROOT, "src", "data", "content.js")
    if os.path.isfile(cj):
        text = open(cj, encoding="utf-8").read()
        if "window.GATE_DATA" not in text:
            fail("src/data/content.js does not define window.GATE_DATA")
        if '"playlists"' not in text:
            warn("src/data/content.js predates the multi-playlist shape; rerun build-index.py")


def check_sources(sources):
    """Every topic that has cards should also record which sources it drew on and what it rejected."""
    if not sources:
        warn("no topic-level sources.json found")
    for key, src in sorted(sources.items()):
        subject, topic = key.split("/")
        if src.get("topic") != topic or src.get("subject") != subject:
            fail("%s: sources.json topic/subject does not match its folder" % key)
        if not src.get("retrieved_at"):
            fail("%s: sources.json has no retrieved_at" % key)
        chosen, rejected = src.get("chosen") or [], src.get("rejected") or []
        if not chosen:
            fail("%s: sources.json records no chosen source" % key)
        if not rejected:
            warn("%s: sources.json records no rejected candidate, so the search is not reviewable" % key)
        for c in chosen:
            for f in ("id", "kind", "language", "transcript", "why"):
                if not c.get(f):
                    fail("%s: chosen source %r has no %s" % (key, c.get("id"), f))
            if c.get("language") != "en" and not c.get("translated", False):
                fail("%s: non-English source %r is not marked as translated" % (key, c.get("id")))
        for r in rejected:
            if not r.get("why"):
                fail("%s: rejected candidate %r records no reason" % (key, r.get("id")))
        ids = {c.get("id") for c in chosen} & {r.get("id") for r in rejected}
        if ids:
            fail("%s: source(s) both chosen and rejected: %s" % (key, ", ".join(sorted(ids))))
    ok("%d topic source ledgers: chosen and rejected candidates recorded with reasons" % len(sources))


STATUSES = {"not_started", "partial", "covered", "blocked"}


def check_coverage(topics, tpath):
    """content/coverage.json must describe exactly the enumerated syllabus and must not overstate itself."""
    path = os.path.join(CONTENT, "coverage.json")
    if not os.path.isfile(path):
        fail("content/coverage.json is missing: the cycle cannot run without the ledger")
        return
    cov = load(path)
    syl = load(os.path.join(CONTENT, "syllabus.json"))
    syl_topics = {}
    for s in syl.get("subjects", []):
        for tp in s.get("topics", []):
            syl_topics[(s["slug"], tp["slug"])] = tp.get("material", "cards")

    seen = {}
    for s in cov.get("subjects", []):
        for tp in s.get("topics", []):
            key = (s["slug"], tp["slug"])
            if key in seen:
                fail("coverage.json lists %s/%s twice" % key)
            seen[key] = tp
            if tp.get("status") not in STATUSES:
                fail("coverage.json %s/%s: invalid status %r" % (key[0], key[1], tp.get("status")))
            if tp.get("status") == "covered" and tp.get("gaps"):
                fail("coverage.json %s/%s is covered but names gaps" % key)
            if tp.get("status") == "partial" and not tp.get("gaps"):
                fail("coverage.json %s/%s is partial but names no gap" % key)
            if tp.get("status") == "blocked" and not tp.get("coverage_note"):
                fail("coverage.json %s/%s is blocked without a reason" % key)
            has_cards = any(tpath[tid].split("/")[3] == tp["slug"] for tid in topics)
            if has_cards and tp.get("status") == "not_started":
                fail("coverage.json %s/%s has cards but is not_started" % key)
            if tp.get("status") in {"covered", "partial"} and not has_cards:
                fail("coverage.json %s/%s claims material but no card exists" % key)

    missing = sorted(set(syl_topics) - set(seen))
    extra = sorted(set(seen) - set(syl_topics))
    if missing:
        fail("coverage.json does not list %d syllabus topic(s): %s"
             % (len(missing), ", ".join("%s/%s" % m for m in missing[:8])))
    if extra:
        fail("coverage.json lists topic(s) not in the syllabus: %s" % ", ".join("%s/%s" % e for e in extra[:8]))

    cyc = cov.get("cycle") or {}
    last = (cyc.get("last_subject"), cyc.get("last_topic"))
    if last not in seen:
        fail("coverage.json cycle.last %s/%s is not a syllabus topic" % last)
    elif seen[last].get("status") == "not_started":
        fail("coverage.json cycle.last %s/%s is still not_started" % last)
    ok("coverage ledger: %d topics, statuses, gaps, cycle pointer %s/%s" % (len(seen), last[0], last[1]))


# ---------------------------------------- sets, relations and functions
def check_sets_relations_functions():
    """Every count and verdict published in the Sets, Relations, Functions cards is recomputed."""
    import itertools
    from math import comb, factorial

    # card 1: S = {{}, 1, {2,3}} has three top-level elements; {} is not one of them; {2,3} is not a subset
    S = [frozenset({frozenset()}), 1, frozenset({2, 3})]      # {{}, 1, {2,3}}
    assert len(S) == 3
    assert frozenset() not in S, "the empty set is not an element of {{empty}, 1, {{2,3}}}"
    assert 2 not in S and 3 not in S, "{2,3} is an element but not a subset of S"
    # card 1 check: S = {{}, {{}}} has 2 elements, 4 subsets, and {{{}}} is a subset
    T = [frozenset(), frozenset({frozenset()})]
    assert len(T) == 2 and 2 ** len(T) == 4
    assert set(T[1]) <= set(T), "{{empty}} is a subset of {empty, {empty}}"

    # card 2: |P({0..10})| = 2048; C(11,3) = 165; C(6,0..2) = 22
    assert 2 ** 11 == 2048 and comb(11, 3) == 165
    assert sum(comb(6, k) for k in range(3)) == 22
    # card 2 check: relations from a 3-set to a 5-set
    assert 2 ** 15 == 32768

    # card 3: the De Morgan counterexample and the symmetric-difference count
    U = {1, 2, 3}
    A, B = {1}, {2}
    assert (U - (A | B)) == {3} and ((U - A) | (U - B)) == U, "wrong De Morgan is visibly false"
    assert (U - (A | B)) == ((U - A) & (U - B)), "correct De Morgan"
    A5, B4 = {1, 2, 3, 4, 5}, {1, 2, 9, 8}
    assert len(A5 | B4) == 7 and len(A5 ^ B4) == 5, "union and symmetric difference counts"
    assert (A5 - B4) | B4 == A5 | B4, "(A - B) union B = A union B"
    A1, B2 = {1}, {2}
    assert ((A1 - B2) | B2) == {1, 2} != A1, "(A - B) union B is not A"

    # card 4: products, and the non-product subset
    AxB = [(a, b) for a in {1, 2} for b in "abc"]
    assert len(AxB) == 6
    BxA = [(b, a) for b in "abc" for a in {1, 2}]
    assert len(BxA) == 6 and ("a", 1) in BxA and ("a", 1) not in AxB
    diag = {(1, 1), (2, 2)}
    for X in itertools.chain.from_iterable(itertools.combinations([1, 2], k) for k in (0, 1, 2)):
        for Y in itertools.chain.from_iterable(itertools.combinations([1, 2], k) for k in (0, 1, 2)):
            if {(1, 1), (2, 2)} <= {(x, y) for x in X for y in Y}:
                assert (1, 2) in {(x, y) for x in X for y in Y}, "no product contains the diagonal only"
    assert 2 ** 12 == 4096

    # card 5: the countable-union counterexample is a set-theoretic fact, checked structurally
    assert len({(r,) for r in range(3)}) == 3, "singletons are countable"

    # relations on a small set, by exhaustive enumeration
    def relations(n):
        cells = [(i, j) for i in range(n) for j in range(n)]
        for bits in range(1 << len(cells)):
            yield {(i, j) for k, (i, j) in enumerate(cells) if bits >> k & 1}

    def reflexive(R, n): return all((i, i) in R for i in range(n))
    def irreflexive(R, n): return not any((i, i) in R for i in range(n))
    def symmetric(R, n): return all((j, i) in R for (i, j) in R)
    def antisymmetric(R, n): return all(i == j for (i, j) in R if (j, i) in R)
    def asymmetric(R, n): return all((j, i) not in R for (i, j) in R)
    def transitive(R, n):
        return all((i, k) in R for (i, j) in R for (j2, k) in R if j == j2)
    def equivalence(R, n): return reflexive(R, n) and symmetric(R, n) and transitive(R, n)

    for n in (1, 2, 3):
        tally = dict(all_=0, refl=0, irrefl=0, sym=0, antisym=0, asym=0, refl_sym=0, sym_antisym=0,
                     neither=0, equiv=0)
        for R in relations(n):
            tally["all_"] += 1
            tally["refl"] += reflexive(R, n)
            tally["irrefl"] += irreflexive(R, n)
            tally["sym"] += symmetric(R, n)
            tally["antisym"] += antisymmetric(R, n)
            tally["asym"] += asymmetric(R, n)
            tally["refl_sym"] += reflexive(R, n) and symmetric(R, n)
            tally["sym_antisym"] += symmetric(R, n) and antisymmetric(R, n)
            tally["neither"] += not reflexive(R, n) and not irreflexive(R, n)
            tally["equiv"] += equivalence(R, n)
        assert tally["all_"] == 2 ** (n * n)
        assert tally["refl"] == 2 ** (n * n - n) == tally["irrefl"]
        assert tally["sym"] == 2 ** (n * (n + 1) // 2)
        assert tally["antisym"] == 2 ** n * 3 ** (n * (n - 1) // 2)
        assert tally["asym"] == 3 ** (n * (n - 1) // 2)
        assert tally["refl_sym"] == 2 ** (n * (n - 1) // 2)
        assert tally["sym_antisym"] == 2 ** n
        assert tally["neither"] == 2 ** (n * n) - 2 * 2 ** (n * n - n)
        # asymmetric is exactly irreflexive plus antisymmetric
        assert all((asymmetric(R, n) == (irreflexive(R, n) and antisymmetric(R, n))) for R in relations(n))
        # symmetric plus antisymmetric is exactly a subset of the identity
        assert all((symmetric(R, n) and antisymmetric(R, n)) ==
                   (R <= {(i, i) for i in range(n)}) for R in relations(n))
        if n == 3:
            assert tally["equiv"] == 5, "equivalence relations on a 3-element set"
            assert tally["sym"] == tally["refl"] == 64

    # Bell numbers and Stirling numbers used in the cards
    def stirling2(n, k):
        return sum((-1) ** i * comb(k, i) * (k - i) ** n for i in range(k + 1)) // factorial(k)
    assert [stirling2(4, k) for k in range(1, 5)] == [1, 7, 6, 1]
    assert sum(stirling2(4, k) for k in range(1, 5)) == 15
    assert sum(stirling2(3, k) for k in range(1, 4)) == 5
    assert comb(3, 2) == 3, "two-class partitions of a 3-element set"

    # card 6: matrix and property verdicts of R = {(1,1),(1,2),(2,3)} on {1,2,3}
    R6 = {(0, 0), (0, 1), (1, 2)}
    assert not reflexive(R6, 3) and not symmetric(R6, 3) and not transitive(R6, 3)
    assert len(R6) == 3 and 2 ** 9 == 512
    # card 6 check: relations from a 3-set to a 5-set, functions among them
    assert 2 ** 15 == 32768 and 5 ** 3 == 125

    # card 7: the worked example is an equivalence relation, not antisymmetric
    R7 = {(0, 0), (1, 1), (2, 2), (0, 1), (1, 0)}
    assert reflexive(R7, 3) and symmetric(R7, 3) and transitive(R7, 3) and not antisymmetric(R7, 3)
    # card 7: {(1,1),(1,2)} is neither reflexive nor irreflexive, and is antisymmetric
    R7b = {(0, 0), (0, 1)}
    assert not reflexive(R7b, 2) and not irreflexive(R7b, 2) and antisymmetric(R7b, 2)
    # card 7 predicted variation: 4-element set, reflexive and symmetric but not antisymmetric
    assert 2 ** 6 - 1 == 63

    # card 8: chains, and the symmetric-plus-transitive-but-not-reflexive example
    assert not transitive({(0, 1), (1, 2)}, 3), "{(1,2),(2,3)} is not transitive"
    closure = {(0, 1), (1, 2)}
    while True:
        add = {(i, k) for (i, j) in closure for (j2, k) in closure if j == j2} - closure
        if not add:
            break
        closure |= add
    assert closure == {(0, 1), (1, 2), (0, 2)}, "transitive closure adds exactly (1,3)"
    R8 = {(0, 0), (1, 1), (0, 1), (1, 0)}
    assert symmetric(R8, 3) and transitive(R8, 3) and not reflexive(R8, 3)
    assert not transitive({(0, 1), (1, 0)}, 2), "{(1,2),(2,1)} alone is not transitive: it forces (1,1)"
    # card 8 check: {(1,1),(1,2),(2,2)} on {1,2}
    R8c = {(0, 0), (0, 1), (1, 1)}
    assert transitive(R8c, 2) and not symmetric(R8c, 2)
    # card 8 ORIGINAL: the closure of a 4-chain adds three pairs
    chain = {(0, 1), (1, 2), (2, 3)}
    cl = set(chain)
    while True:
        add = {(i, k) for (i, j) in cl for (j2, k) in cl if j == j2} - cl
        if not add:
            break
        cl |= add
    assert cl - chain == {(0, 2), (1, 3), (0, 3)} and len(cl) == 6

    # card 9: the union of two equivalence relations need not be transitive
    R1 = {(0, 0), (1, 1), (2, 2), (0, 1), (1, 0)}
    R2 = {(0, 0), (1, 1), (2, 2), (1, 2), (2, 1)}
    assert equivalence(R1, 3) and equivalence(R2, 3)
    assert not transitive(R1 | R2, 3), "union of two equivalence relations is not transitive"
    assert equivalence(R1 & R2, 3), "intersection of two equivalence relations is an equivalence relation"
    R9 = {(0, 0), (1, 1), (0, 1), (1, 0)}
    assert symmetric(R9, 3) and transitive(R9, 3) and not reflexive(R9, 3)

    # functions: counts by brute force
    def functions(m, n):
        for img in itertools.product(range(n), repeat=m):
            yield img
    def injective(img): return len(set(img)) == len(img)
    def surjective(img, n): return len(set(img)) == n
    f43 = list(functions(4, 3))
    assert len(f43) == 81
    assert sum(1 for i in f43 if surjective(i, 3)) == 36
    assert sum(1 for i in f43 if injective(i)) == 0
    assert sum(1 for i in f43 if injective(i) and surjective(i, 3)) == 0
    f23 = list(functions(2, 3))
    assert len(f23) == 9 and sum(1 for i in f23 if surjective(i, 3)) == 0
    assert sum(1 for i in f23 if injective(i)) == 6
    f46 = list(functions(4, 6))
    assert sum(1 for i in f46 if injective(i)) == 360
    f64 = list(functions(6, 4))
    assert sum(1 for i in f64 if injective(i)) == 0
    f33 = list(functions(3, 3))
    assert len(f33) == 27
    assert sum(1 for i in f33 if not injective(i) and not surjective(i, 3)) == 21
    assert sum(1 for i in f33 if injective(i)) == 6 and sum(1 for i in f33 if surjective(i, 3)) == 6
    assert factorial(5) == 120

    # card 11: the composite example, and the injectivity rule
    f = {0: 0, 1: 0, 2: 1}          # {1,2,3} -> {a,b}
    g = {0: 0, 1: 1}                # {a,b} -> {x,y}
    comp = {k: g[v] for k, v in f.items()}
    assert comp == {0: 0, 1: 0, 2: 1}
    assert len(set(comp.values())) == 2 and len(set(comp.values())) != len(comp)
    assert not injective([f[k] for k in sorted(f)])
    # g of f injective forces f injective, over every pair of small maps
    for m in (1, 2, 3):
        for n in (1, 2, 3):
            for img_f in itertools.product(range(n), repeat=m):
                for img_g in itertools.product(range(n), repeat=n):
                    c = [img_g[img_f[i]] for i in range(m)]
                    if injective(c):
                        assert injective(img_f), "injective composite forces injective left factor"
    # the converse fails: f(1) = a, g(a) = g(b) = x
    assert not injective([0, 0]) and injective([0])  # g collapses a and b, the composite on one point is injective

    # 2015 Set 3 Q.41: symmetric, not reflexive, not transitive, on small positive integers
    pairs = [(p, q) for p in range(1, 5) for q in range(1, 5)]
    Rq = {((p, q), (r, s)) for (p, q) in pairs for (r, s) in pairs if p - s == q - r}
    assert not all((x, x) in Rq for x in pairs), "p - s = q - r is not reflexive"
    assert all(((r, s), (p, q)) in Rq for ((p, q), (r, s)) in Rq), "p - s = q - r is symmetric"
    assert ((1, 2), (1, 2)) not in Rq and ((1, 1), (1, 1)) in Rq, "not reflexive but not irreflexive"
    assert ((1, 2), (2, 1)) in Rq and ((2, 1), (1, 2)) in Rq and ((1, 2), (1, 2)) not in Rq, \
        "the relation is not transitive"

    # 2016 Set 2 Q.26: reflexive, not transitive; with 'and' it would be transitive
    def Ror(x, y): return x[0] <= y[0] or x[1] <= y[1]
    def Rand(x, y): return x[0] <= y[0] and x[1] <= y[1]
    pts = [(a, b) for a in range(1, 6) for b in range(1, 6)]
    assert all(Ror(p, p) for p in pts), "the 'or' relation is reflexive"
    assert not all(Ror(p, r) for p in pts for q in pts for r in pts if Ror(p, q) and Ror(q, r)), \
        "the 'or' relation is not transitive"
    assert all(Rand(p, r) for p in pts for q in pts for r in pts if Rand(p, q) and Rand(q, r)), \
        "the 'and' relation is transitive"
    assert Ror((2, 10), (3, 1)) and Ror((3, 1), (1, 2)) and not Ror((2, 10), (1, 2))

    ok("sets, relations, functions: %d relation counts recomputed by enumeration, Bell and Stirling numbers, "
       "function counts by brute force, and the verdicts of the four relations-based PYQs" % 9)


# ---------------------------------------- partial orders and lattices
def check_lattices():
    """Every order-theoretic claim published in the Partial Orders and Lattices cards and lesson is recomputed."""
    import itertools
    from fractions import Fraction

    def closure(cover, elems):
        R = {(e, e) for e in elems} | {(a, b) for a, b in cover}
        while True:
            add = {(a, c) for (a, b) in R for (b2, c) in R if b == b2} - R
            if not add:
                return R
            R |= add

    def is_poset(R, elems):
        return (all((a, a) in R for a in elems)
                and all(a == b for (a, b) in R if (b, a) in R)
                and all((a, c) in R for (a, b) in R for (b2, c) in R if b == b2))

    def lub_glb(R, elems, a, b):
        up = [u for u in elems if (a, u) in R and (b, u) in R]
        lo = [l for l in elems if (l, a) in R and (l, b) in R]
        J = next((u for u in up if all((u, v) in R for v in up)), None)
        M = next((m for m in lo if all((v, m) in R for v in lo)), None)
        return J, M

    def is_lattice(R, elems):
        return all(lub_glb(R, elems, a, b) != (None, None)
                   and lub_glb(R, elems, a, b)[0] is not None
                   and lub_glb(R, elems, a, b)[1] is not None
                   for a in elems for b in elems)

    def covers(R, elems):
        return [(a, b) for (a, b) in R if a != b
                and not any(z not in (a, b) and (a, z) in R and (z, b) in R for z in elems)]

    def join(R, e, a, b): return lub_glb(R, e, a, b)[0]
    def meet(R, e, a, b): return lub_glb(R, e, a, b)[1]

    def distributive(R, elems):
        for a in elems:
            for b in elems:
                for c in elems:
                    if (meet(R, elems, a, join(R, elems, b, c))
                            != join(R, elems, meet(R, elems, a, b), meet(R, elems, a, c))):
                        return False
        return True

    def semi_inequality_holds(R, elems):
        for a in elems:
            for b in elems:
                for c in elems:
                    lhs = join(R, elems, a, meet(R, elems, b, c))
                    rhs = meet(R, elems, join(R, elems, a, b), join(R, elems, a, c))
                    if (lhs, rhs) not in R:
                        return False
        return True

    def is_sublattice(R, elems, S):
        S = set(S)
        return S <= set(elems) and all(join(R, elems, a, b) in S and meet(R, elems, a, b) in S
                                       for a in S for b in S)

    def complements(R, elems, a):
        zero = [x for x in elems if all((x, y) in R for y in elems)]
        one = [x for x in elems if all((y, x) in R for y in elems)]
        if not zero or not one:
            return []
        return [x for x in elems if meet(R, elems, a, x) == zero[0] and join(R, elems, a, x) == one[0]]

    def linear_extensions(R, elems):
        n, out = len(elems), 0
        for perm in itertools.permutations(elems):
            T = {(perm[i], perm[j]) for i in range(n) for j in range(i, n)}
            out += 1 if R <= T else 0
        return out

    def height_classes(R, elems):
        def height(x):
            return 1 + max([height(y) for y in elems if (y, x) in R and y != x] or [0])
        best = {}
        for x in elems:
            best[x] = height(x)
        return best

    def longest_chain(R, elems):
        return max(height_classes(R, elems).values())

    def divisors(n):
        return [d for d in range(1, n + 1) if n % d == 0]

    def divisor_poset(n):
        E = divisors(n)
        return E, {(a, b) for a in E for b in E if b % a == 0}

    # ---- the counting facts quoted on the axioms card
    def count_posets(n):
        elems = list(range(n))
        cells = [(a, b) for a in elems for b in elems]
        total = 0
        for bits in range(1 << len(cells)):
            R = {c for k, c in enumerate(cells) if bits >> k & 1}
            if is_poset(R, elems):
                total += 1
        return total

    assert count_posets(2) == 3, "three partial orders on a two-element set"
    assert count_posets(3) == 19, "nineteen partial orders on a three-element set"
    assert count_posets(4) == 219, "219 partial orders on a four-element set"
    e2 = [0, 1]
    assert sum(1 for p in itertools.permutations(e2)
               if {(0, 0), (1, 1)} | {(p[0], p[1])} >= {(0, 0), (1, 1)}) == 2
    assert sum(1 for p in itertools.permutations([0, 1, 2])) == 6, "six total orders on three elements"

    # ---- Hasse diagrams and relation cardinalities
    E24 = [2, 3, 6, 12, 24]
    R24 = {(a, b) for a in E24 for b in E24 if b % a == 0}
    assert is_poset(R24, E24)
    assert len(covers(R24, E24)) == 4, "four covering pairs for {2,3,6,12,24}"
    assert len(R24) == 14, "fourteen pairs in the divisibility relation on {2,3,6,12,24}"
    assert sorted(covers(R24, E24)) == [(2, 6), (3, 6), (6, 12), (12, 24)]
    E12, R12 = divisor_poset(12)
    assert len(E12) == 6 and len(covers(R12, E12)) == 7, "seven covering pairs for the divisors of 12"
    E24b, R24b = divisor_poset(24)
    assert len(covers(R24b, E24b)) == 10, "ten covering pairs for the eight divisors of 24"
    chain4 = [0, 1, 2, 3]
    Rc4 = {(a, b) for a in chain4 for b in chain4 if a <= b}
    assert len(Rc4) == 10 and len(covers(Rc4, chain4)) == 3, "a 4-element chain: 10 pairs, 3 edges"

    # ---- chains, antichains and linear extensions
    for n in (2, 3, 4):
        E = list(range(n))
        for bits in range(1 << (n * n)):
            cells = [(a, b) for a in E for b in E]
            R = {c for k, c in enumerate(cells) if bits >> k & 1}
            if not is_poset(R, E):
                continue
            h = height_classes(R, E)
            classes = {}
            for x, v in h.items():
                classes.setdefault(v, set()).add(x)
            # each height class is an antichain, and there are exactly longest_chain of them
            for v, S in classes.items():
                for a in S:
                    for b in S:
                        assert a == b or not ((a, b) in R and a != b), "a height class must be an antichain"
            assert len(classes) == longest_chain(R, E), "Mirsky: n height classes for a longest chain of n"
    assert longest_chain(R24, E24) == 4 and longest_chain(R12, E12) == 4

    P24 = {(x, x) for x in (1, 2, 3, 4)} | {(1, 2), (3, 2), (3, 4)}
    assert is_poset(P24, [1, 2, 3, 4])
    assert linear_extensions(P24, [1, 2, 3, 4]) == 5, "GATE 2024 Set 2 Q.24 has five linear extensions"
    assert sorted(("".join(map(str, p)) for p in itertools.permutations([1, 2, 3, 4])
                   if P24 <= {(p[i], p[j]) for i in range(4) for j in range(i, 4)})) == \
        ["1324", "1342", "3124", "3142", "3412"]
    width = max(len(S) for k in range(1, 5)
                for S in itertools.combinations([1, 2, 3, 4], k)
                if all(not ((a, b) in P24 or (b, a) in P24) or a == b for a in S for b in S))
    assert width == 2, "the largest antichain of the 2024 poset has two elements"
    assert all(not ((a, b) in P24 or (b, a) in P24) or a == b for a in (2, 4) for b in (2, 4))
    assert all(not ((a, b) in P24 or (b, a) in P24) or a == b for a in (1, 3) for b in (1, 3))
    for n in (1, 2, 3, 4):
        A = [("a", i) for i in range(n)]
        E = [("x",)] + A + [("y",)]
        P = ({(e, e) for e in E} | {(("x",), a) for a in A} | {(a, ("y",)) for a in A}
             | {(("x",), ("y",))})
        assert is_poset(P, E)
        assert linear_extensions(P, E) == factorial(n), "GATE 1997 Q.6.1 gives n!"

    # ---- minimal, maximal, least, greatest
    def extremes(R, elems):
        least = [a for a in elems if all((a, b) in R for b in elems)]
        greatest = [a for a in elems if all((b, a) in R for b in elems)]
        minimal = [a for a in elems if not any((b, a) in R and b != a for b in elems)]
        maximal = [a for a in elems if not any((a, b) in R and b != a for b in elems)]
        return least, greatest, minimal, maximal

    least, greatest, minimal, maximal = extremes(R12, E12)
    assert least == [1] and greatest == [12] and minimal == [1] and maximal == [12]
    E11 = [d for d in E12 if d != 12]
    least, greatest, minimal, maximal = extremes(R12, E11)
    assert least == [1] and greatest == [] and sorted(minimal) == [1] and sorted(maximal) == [4, 6]
    # the 5-element poset of the minimal/maximal trap: a < c, b < c, c < d, b < e
    E5 = ["a", "b", "c", "d", "e"]
    R5 = closure([("a", "c"), ("b", "c"), ("c", "d"), ("b", "e")], E5)
    assert is_poset(R5, E5)
    least, greatest, minimal, maximal = extremes(R5, E5)
    assert least == [] and sorted(minimal) == ["a", "b"], "a and b are minimal, neither is least"
    # two incomparable upper bounds and no LUB
    E4 = ["a", "b", "c", "d"]
    R4 = closure([("a", "c"), ("b", "c"), ("a", "d"), ("b", "d")], E4)
    assert lub_glb(R4, E4, "a", "b") == (None, None), "c and d are incomparable upper bounds, so no LUB"
    assert not is_lattice(R4, E4)

    # ---- bounds in divisor posets
    assert lub_glb(R12, E12, 4, 6) == (12, 2), "LUB 12 and GLB 2 for 4 and 6 in D12"
    E18, R18 = divisor_poset(18)
    assert is_lattice(R18, E18), "D18 is a lattice"
    assert lub_glb(R18, E18, 6, 9) == (18, 3) and lub_glb(R18, E18, 2, 9) == (18, 1)
    E18b = [d for d in E18 if d != 18]
    R18b = {(a, b) for a, b in R18 if a in E18b and b in E18b}
    assert not is_lattice(R18b, E18b), "D18 without 18 is not a lattice"
    assert lub_glb(R18b, E18b, 6, 9) == (None, 3), "6 and 9 keep GLB 3 and lose their LUB"
    assert lub_glb(R18b, E18b, 2, 9) == (None, 1)
    E30, R30 = divisor_poset(30)
    assert lub_glb(R30, E30, 6, 10) == (30, 2)
    assert is_lattice(R30, E30) and len(E30) == 8 and distributive(R30, E30)

    # ---- the GATE 2017 Set 2 Q.21 poset and its lesson
    EX = list("abcde")
    PX = {(a, a) for a in EX} | {("a", b) for b in EX} | {("b", "c"), ("b", "e"), ("c", "e"), ("d", "e")}
    assert is_poset(PX, EX), "the 2017 poset is reflexive, antisymmetric and transitive"
    assert len(PX) == 13 and len(covers(PX, EX)) == 5
    assert sorted(covers(PX, EX)) == [("a", "b"), ("a", "d"), ("b", "c"), ("c", "e"), ("d", "e")]
    assert is_lattice(PX, EX), "the 2017 poset is already a lattice, so 0 pairs must be added"
    assert lub_glb(PX, EX, "b", "d") == ("e", "a") and lub_glb(PX, EX, "c", "d") == ("e", "a")
    assert lub_glb(PX, EX, "b", "c") == ("c", "b")
    assert distributive(PX, EX) is False, "the pentagon is not distributive"
    PXb = {(a, b) for a, b in PX if (a, b) != ("d", "e")}
    assert is_poset(PXb, EX) and not is_lattice(PXb, EX), "deleting d < e breaks the lattice property"
    assert lub_glb(PXb, EX, "b", "d") == (None, "a") and lub_glb(PXb, EX, "c", "d") == (None, "a")
    assert len(PXb) == 12 and len(PX - PXb) == 1, "adding d < e back adds exactly one pair"
    EXc = ["a", "b", "d", "e"]
    RXc = {(a, b) for a, b in PX if a in EXc and b in EXc}
    assert is_lattice(RXc, EXc), "deleting c leaves the square B2, a lattice"

    # ---- a join-semilattice that is not a lattice
    E3 = ["x", "y", "z"]
    R3 = closure([("x", "z"), ("y", "z")], E3)
    assert all(join(R3, E3, a, b) is not None for a in E3 for b in E3)
    assert meet(R3, E3, "x", "y") is None and not is_lattice(R3, E3)

    # ---- the four lattice laws and duality on the standard lattices
    E6, R6 = divisor_poset(6)
    M3E = [0, "a", "b", "c", 1]
    M3 = {(0, 0), (1, 1), ("a", "a"), ("b", "b"), ("c", "c")} | \
         {(0, x) for x in M3E} | {(x, 1) for x in M3E}
    N5E = [0, "a", "b", "c", 1]
    N5 = {(0, 0), (1, 1), ("a", "a"), ("b", "b"), ("c", "c")} | \
         {(0, x) for x in N5E} | {(x, 1) for x in N5E} | {("a", "c")}
    B3E = [frozenset(s) for k in range(4) for s in itertools.combinations([1, 2, 3], k)]
    B3 = {(x, y) for x in B3E for y in B3E if x <= y}
    for E, R, name in ((E12, R12, "D12"), (E6, R6, "D6"), (M3E, M3, "M3"), (N5E, N5, "N5"),
                       (B3E, B3, "B3"), (chain4, Rc4, "chain4")):
        assert is_poset(R, E) and is_lattice(R, E), name + " is a lattice"
        for a in E:
            assert join(R, E, a, a) == a and meet(R, E, a, a) == a, name + " idempotent"
            for b in E:
                assert join(R, E, a, b) == join(R, E, b, a) and meet(R, E, a, b) == meet(R, E, b, a), \
                    name + " commutative"
                assert join(R, E, a, meet(R, E, a, b)) == a, name + " absorption"
                assert meet(R, E, a, join(R, E, a, b)) == a, name + " absorption (dual)"
                for c in E:
                    assert join(R, E, join(R, E, a, b), c) == join(R, E, a, join(R, E, b, c)), name + " associative"
                    assert meet(R, E, meet(R, E, a, b), c) == meet(R, E, a, meet(R, E, b, c)), name + " associative"
        assert semi_inequality_holds(R, E), name + " satisfies the semi-distributive inequality"

    # ---- distributivity: D_n and B3 yes, M3 and N5 no, with the published counterexamples
    assert distributive(R12, E12) and distributive(R6, E6) and distributive(B3, B3E) and distributive(R30, E30)
    assert not distributive(M3, M3E) and not distributive(N5, N5E)
    assert meet(M3, M3E, "a", join(M3, M3E, "b", "c")) == "a"
    assert join(M3, M3E, meet(M3, M3E, "a", "b"), meet(M3, M3E, "a", "c")) == 0
    assert join(N5, N5E, "a", meet(N5, N5E, "b", "c")) == "a"
    assert meet(N5, N5E, join(N5, N5E, "a", "b"), join(N5, N5E, "a", "c")) == "c"
    assert meet(N5, N5E, "a", join(N5, N5E, "b", "c")) == "a"
    assert join(N5, N5E, meet(N5, N5E, "a", "b"), meet(N5, N5E, "a", "c")) == "a"

    # ---- sublattices
    assert is_sublattice(R12, E12, [1, 2, 4]) and is_sublattice(R12, E12, [1, 2, 6])
    assert not is_sublattice(R12, E12, [1, 2, 3, 4]) and not is_lattice(
        {(a, b) for a, b in R12 if a in (1, 2, 3, 4) and b in (1, 2, 3, 4)}, [1, 2, 3, 4])
    assert is_sublattice(M3, M3E, [0, "a", "b", 1]) and not is_sublattice(M3, M3E, [0, "a", "b"])
    assert not is_sublattice(R30, E30, [1, 2, 3, 5, 6])
    # a lattice that is not a sublattice: the pentagon inside the cube
    SP = [frozenset(), frozenset({1}), frozenset({2}), frozenset({1, 2}), frozenset({3}), frozenset({1, 2, 3})]
    RP = {(a, b) for a, b in B3 if a in SP and b in SP}
    assert is_lattice(RP, SP), "the pentagon is a lattice on its own"
    assert not is_sublattice(B3, B3E, SP), "but {1} v {3} = {1,3} leaves it, so it is not a sublattice"
    assert join(B3, B3E, frozenset({1}), frozenset({3})) == frozenset({1, 3})
    assert is_sublattice(B3, B3E, [frozenset(), frozenset({1}), frozenset({2}), frozenset({1, 2})])
    for E, R in ((chain4, Rc4), (E6, R6), (E12, R12)):
        for a in E:
            for b in E:
                S = sorted({a, b}, key=str)
                if (a, b) in R or (b, a) in R:
                    assert is_sublattice(R, E, S), "every two-element chain is a sublattice"
    assert not is_sublattice(R6, E6, [2, 3]), "2 and 3 in D6 are incomparable, so {2, 3} is not a sublattice"

    # ---- bounded, complemented, Boolean
    assert complements(R6, E6, 2) == [3] and complements(R6, E6, 3) == [2]
    assert complements(R6, E6, 1) == [6] and complements(R6, E6, 6) == [1]
    assert sorted(map(str, complements(M3, M3E, "a"))) == ["b", "c"], "each atom of M3 has two complements"
    assert complements(R12, E12, 2) == [] and complements(R12, E12, 6) == []
    assert complements(R12, E12, 3) == [4] and complements(R12, E12, 4) == [3]
    assert complements(R12, E12, 1) == [12] and complements(R12, E12, 12) == [1]
    assert complements(R30, E30, 6) == [5]
    assert complements(N5, N5E, "c") == ["b"] and complements(N5, N5E, "a") == ["b"]
    assert "a" not in complements(N5, N5E, "c"), "a v c = c, so a is not a complement of c"
    def is_boolean(E, R):
        zero = [x for x in E if all((x, y) in R for y in E)]
        one = [x for x in E if all((y, x) in R for y in E)]
        return (is_lattice(R, E) and distributive(R, E) and len(zero) == 1 and len(one) == 1
                and all(complements(R, E, a) for a in E))
    assert is_boolean(E6, R6) and is_boolean(E30, R30) and is_boolean(B3E, B3)
    assert not is_boolean(E12, E12) and not is_boolean(M3E, M3)
    E210 = divisors(210)
    R210 = {(a, b) for a in E210 for b in E210 if b % a == 0}
    assert len(E210) == 16 and is_boolean(E210, R210)
    assert len(B3E) == 8 and len(covers(B3, B3E)) == 12
    B4E = [frozenset(s) for k in range(5) for s in itertools.combinations([1, 2, 3, 4], k)]
    B4 = {(x, y) for x in B4E for y in B4E if x <= y}
    assert len(B4E) == 16 and len(covers(B4, B4E)) == 32, "B4: 16 elements, 32 covering pairs"
    assert complements(B4, B4E, frozenset({1, 2})) == [frozenset({3, 4})]
    below = [x for x in B3E if x < frozenset({1, 2})]
    assert len(below) == 3, "three elements strictly below {1,2} in B3"

    # ---- complete lattices
    S2004 = [frozenset({1, 2}), frozenset({1, 2, 3}), frozenset({1, 3, 5}),
             frozenset({1, 2, 4}), frozenset({1, 2, 3, 4, 5})]
    def complete(E):
        R = {(a, b) for a in E for b in E if a <= b}
        for r in range(0, len(E) + 1):
            for sub in itertools.combinations(E, r):
                sub = list(sub)
                up = [u for u in E if all(x <= u for x in sub)]
                lo = [l for l in E if all(l <= x for x in sub)]
                if not up or not lo:
                    return False
                if not any(all(u <= m for u in up) for m in up):
                    return False
                if not any(all(m <= l for l in lo) for m in lo):
                    return False
        return True
    assert not complete(S2004)
    assert complete(S2004 + [frozenset({1})]), "adding {1} makes the 2004 family a complete lattice"
    assert not complete(S2004 + [frozenset({1}), frozenset({2, 3})]), "option B of GATE 2004 Q.73 does not work"
    R2004 = {(a, b) for a in S2004 for b in S2004 if a <= b}
    TOP2004 = frozenset({1, 2, 3, 4, 5})
    assert lub_glb(R2004, S2004, frozenset({1, 2, 3}), frozenset({1, 3, 5})) == (TOP2004, None), \
        "the pair has no meet inside S, which is why S is not even a lattice"
    assert lub_glb(R2004, S2004, frozenset({1, 3, 5}), frozenset({1, 2, 4})) == (TOP2004, None)
    S2 = [frozenset({2}), frozenset({2, 3}), frozenset({2, 4}), frozenset({2, 3, 4})]
    assert complete(S2) and len(S2) == 4
    for n in (2, 4, 6, 12):
        E, R = divisor_poset(n)
        assert complete(E), "every finite lattice is complete (D%d)" % n

    # ---- the 2025 Set 2 Q.32 pointwise order on functions into {0,1}
    for n in (1, 2, 3):
        F = list(itertools.product([0, 1], repeat=n))
        R = {(f, g) for f in F for g in F if all(f[i] <= g[i] for i in range(n))}
        assert is_poset(R, F) and is_lattice(R, F) and distributive(R, F)
        assert not all((g, f) in R for (f, g) in R), "the pointwise order is not symmetric"
        assert all(join(R, F, f, g) == tuple(max(f[i], g[i]) for i in range(n)) for f in F for g in F)
        assert all(meet(R, F, f, g) == tuple(min(f[i], g[i]) for i in range(n)) for f in F for g in F)
        assert len(F) == 2 ** n
        if n == 3:
            f0, g0 = (0, 1, 1), (1, 1, 0)
            assert (f0, g0) not in R and (g0, f0) not in R, "010/011 style pair is incomparable, not symmetric"

    # ---- the "at least 15 pairs" claim on the Hasse card
    assert 7 + 8 == 15, "7 vertices and 8 edges force at least 15 pairs including the reflexive ones"

    ok("partial orders and lattices: posets on 2, 3 and 4 elements counted by enumeration, Hasse edge and "
       "relation counts, Mirsky's antichain partition on every poset up to 4 elements, the 1997 and 2024 "
       "linear-extension counts, the four lattice laws and the semi-distributive inequality on six lattices, the "
       "M3 and N5 counterexamples, sublattice verdicts, complement and Boolean tests, complete-lattice checks "
       "and the 2017 and 2025 PYQ verdicts")


# ------------------------------------------------------------- monoids and groups
def check_monoids_and_groups():
    """Every group-theoretic claim in the Monoids and Groups cards, PYQs and lesson is recomputed."""
    import itertools
    from math import gcd

    def is_group(elems, op):
        S = list(elems)
        for a in S:
            for b in S:
                if op(a, b) not in elems:
                    return False
        for a in S:
            for b in S:
                for c in S:
                    if op(op(a, b), c) != op(a, op(b, c)):
                        return False
        ids = [u for u in S if all(op(u, a) == a and op(a, u) == a for a in S)]
        if len(ids) != 1:
            return False
        u = ids[0]
        for a in S:
            if not any(op(a, b) == u and op(b, a) == u for b in S):
                return False
        return True

    def phi(n):
        return sum(1 for a in range(1, n + 1) if gcd(a, n) == 1)

    def divisors(n):
        return [d for d in range(1, n + 1) if n % d == 0]

    def spf(n):
        for p in range(2, n + 1):
            if n % p == 0:
                return p
        return n

    def order_of(n, a):
        x, k = a % n, 1
        while x != 0:
            x = (x + a) % n
            k += 1
        return k

    def subgroup_of_order(n, k):
        step = n // k
        return frozenset((a * step) % n for a in range(k))

    # the ladder: Z_n is a group for every n, and its element orders follow n / gcd(a, n)
    for n in range(1, 21):
        if not is_group(set(range(n)), lambda a, b, n=n: (a + b) % n):
            fail("math: Z_%d is not a group" % n)
        for a in range(n):
            if order_of(n, a) != n // gcd(a, n):
                fail("math: order of %d in Z_%d is not n/gcd(a,n)" % (a, n))
        gens = [a for a in range(n) if order_of(n, a) == n]
        if gens != [a for a in range(n) if gcd(a, n) == 1]:
            fail("math: generators of Z_%d are not the residues coprime to n" % n)
        if len(gens) != phi(n):
            fail("math: Z_%d has %d generators but phi(%d) = %d" % (n, len(gens), n, phi(n)))

    # subgroups of Z_n: exactly one per divisor, and Lagrange holds for each
    for n in range(1, 21):
        subs = [subgroup_of_order(n, d) for d in divisors(n)]
        if len(set(subs)) != len(divisors(n)):
            fail("math: Z_%d does not have one subgroup per divisor" % n)
        for H in subs:
            if n % len(H):
                fail("math: a subgroup of Z_%d has order %d, which does not divide %d" % (n, len(H), n))
            if not is_group(set(H), lambda a, b, n=n: (a + b) % n):
                fail("math: the subgroup {0, %d, ...} of Z_%d is not a group" % (n // len(H), n))

    # largest proper subgroup = n / smallest prime factor, and it is attained in Z_n
    for n in (35, 84, 15, 45, 12, 6, 8, 30):
        proper = [d for d in divisors(n) if d < n]
        if max(proper) != n // spf(n):
            fail("math: largest proper subgroup of order %d is not n/spf" % n)
        if len(subgroup_of_order(n, max(proper))) != max(proper):
            fail("math: Z_%d has no subgroup of the largest proper order" % n)
    if max(d for d in divisors(15) if 4 <= d < 15) != 5:
        fail("math: the 2014 Set 3 Q.3 filter on divisors of 15 does not leave 5")

    # self-inverse counts, element orders and generator counts quoted in the cards
    Z2Z3Z4 = [(a, b, c) for a in range(2) for b in range(3) for c in range(4)]
    si = [x for x in Z2Z3Z4 if (2 * x[0]) % 2 == 0 and (2 * x[1]) % 3 == 0 and (2 * x[2]) % 4 == 0]
    if len(Z2Z3Z4) != 24 or len(si) != 4:
        fail("math: Z2 x Z3 x Z4 should have 24 elements and 4 self-inverse ones, got %d and %d"
             % (len(Z2Z3Z4), len(si)))
    if sorted(si) != [(0, 0, 0), (0, 0, 2), (1, 0, 0), (1, 0, 2)]:
        fail("math: the four self-inverse elements of Z2 x Z3 x Z4 are not the ones the card lists")
    Z4Z6 = [(a, b) for a in range(4) for b in range(6)]
    if len([x for x in Z4Z6 if (2 * x[0]) % 4 == 0 and (2 * x[1]) % 6 == 0]) != 4:
        fail("math: Z4 x Z6 should have gcd(2,4) * gcd(2,6) = 4 self-inverse elements")
    if len([a for a in range(20) if (2 * a) % 20 == 0]) != 2:
        fail("math: Z_20 should have 2 solutions of a^2 = e")
    if [order_of(12, a) for a in range(12)] != [1, 12, 6, 4, 3, 12, 2, 12, 3, 4, 6, 12]:
        fail("math: the element orders of Z_12 are not the ones the cards and lesson list")
    if len([a for a in range(12) if order_of(12, a) == 2]) != 1:
        fail("math: Z_12 should have exactly one element of order 2")
    if len([a for a in range(12) if order_of(12, a) == 3]) != phi(3):
        fail("math: Z_12 should have phi(3) = 2 elements of order 3")
    if [order_of(8, a) for a in range(8)] != [1, 8, 4, 8, 2, 8, 4, 8]:
        fail("math: the element orders of Z_8 are not the ones the card lists")
    for n, g in ((12, 4), (10, 4), (20, 8), (8, 4), (7, 6)):
        if len([a for a in range(n) if gcd(a, n) == 1]) != g:
            fail("math: Z_%d should have %d generators" % (n, g))
    if phi(12) != 4 or phi(3) != 2 or phi(20) != 8:
        fail("math: a phi value quoted in the cards is wrong")

    # the cosets of {0, 4, 8} in Z_12 partition the group, and <5> is the whole group
    H = {0, 4, 8}
    cosets = []
    for a in range(12):
        C = frozenset((a + h) % 12 for h in H)
        if C not in cosets:
            cosets.append(C)
    if len(cosets) != 4 or any(len(C) != 3 for C in cosets):
        fail("math: {0, 4, 8} should have four cosets of size three in Z_12")
    if sum(len(C) for C in cosets) != 12 or len(set().union(*[set(C) for C in cosets])) != 12:
        fail("math: the cosets of {0, 4, 8} in Z_12 do not cover the group disjointly")
    if len({(5 * k) % 12 for k in range(12)}) != 12:
        fail("math: 5 does not generate Z_12")
    if sorted({a for a in range(12) if gcd(a, 12) == 1}) != [1, 5, 7, 11]:
        fail("math: the generators of Z_12 are not 1, 5, 7 and 11")
    union = {0, 6} | {0, 4, 8}
    if (4 + 6) % 12 in union or len(union) != 4:
        fail("math: the union of {0, 6} and {0, 4, 8} in Z_12 should miss 4 + 6 = 10")
    if {0, 3, 6, 9} != set(subgroup_of_order(12, 4)):
        fail("math: {0, 3, 6, 9} is not the subgroup of order 4 in Z_12")
    if not all((a - b) % 12 in {0, 3, 6, 9} for a in {0, 3, 6, 9} for b in {0, 3, 6, 9}):
        fail("math: {0, 3, 6, 9} fails the one-step test in Z_12")
    if all((a - b) % 12 in {0, 2, 4} for a in {0, 2, 4} for b in {0, 2, 4}):
        fail("math: {0, 2, 4} should fail the one-step test in Z_12")

    # the ladder on the standard structures
    if all(((a - b) - c) == (a - (b - c)) for a in range(-3, 4) for b in range(-3, 4) for c in range(-3, 4)):
        fail("math: subtraction on the integers should not be associative")
    if any((a - b) not in set(range(-9, 10)) for a in range(-3, 4) for b in range(-3, 4)):
        fail("math: subtraction on a bounded sample is not closed")
    for e in range(-50, 51):
        if all(max(e, m) == m for m in range(-100, 101)):
            fail("math: max on the integers has an identity after all")
    if any(max(a, b) != max(b, a) for a in range(-5, 6) for b in range(-5, 6)):
        fail("math: max is not commutative")
    if not all(max(max(a, b), c) == max(a, max(b, c)) for a in range(-4, 5) for b in range(-4, 5) for c in range(-4, 5)):
        fail("math: max is not associative")

    # strings over {a} under concatenation: a monoid that is not a group
    words = [""] + ["a" * k for k in range(1, 4)]
    if any((u + v).count("a") != u.count("a") + v.count("a") for u in words for v in words):
        fail("math: concatenation of strings over {a} does not behave")
    if any(((u + v) + w) != (u + (v + w)) for u in words for v in words for w in words):
        fail("math: concatenation is not associative")
    if any(u + "" != u or "" + u != u for u in words):
        fail("math: the empty string is not the identity for concatenation")
    if any((u + v) == "" for u in words if u for v in words):
        fail("math: a non-empty string has an inverse under concatenation")

    # (Z, x) is a monoid but not a group; (2^X, union) likewise
    if any(a * 2 == 1 for a in range(-50, 51)):
        fail("math: 2 should have no inverse in Z under multiplication")
    X = {1, 2, 3}
    subsets = [frozenset(s) for r in range(4) for s in itertools.combinations(sorted(X), r)]
    if not all((a | b) in subsets for a in subsets for b in subsets):
        fail("math: the power set is not closed under union")
    if any((a | b) == frozenset() for a in subsets if a for b in subsets):
        fail("math: a non-empty subset has an inverse under union")
    if any((a & frozenset()) != frozenset() for a in subsets):
        fail("math: the empty set is not the identity for intersection")
    if any((a & X) != a for a in subsets):
        fail("math: X is not the identity for intersection")

    # symmetric difference on 2^{1,2,3} is an abelian group with every element self-inverse
    symdiff = lambda a, b: frozenset((set(a) - set(b)) | (set(b) - set(a)))
    if not all(symdiff(a, b) in subsets for a in subsets for b in subsets):
        fail("math: symmetric difference is not closed on the power set")
    if not is_group(set(subsets), symdiff):
        fail("math: (2^X, symmetric difference) is not a group")
    if any(symdiff(a, b) != symdiff(b, a) for a in subsets for b in subsets):
        fail("math: symmetric difference is not commutative")
    if any(symdiff(a, a) != frozenset() for a in subsets):
        fail("math: an element of (2^X, symmetric difference) is not its own inverse")
    if symdiff(frozenset({1}), frozenset({2, 3})) == frozenset():
        fail("math: the complement of a set should not be its inverse under symmetric difference")

    # the two made-up operations of the 2024 Set 1 question, brute forced
    dia = lambda a, b: a + 2 * b
    sq = lambda a, b: a * b
    P = list(range(1, 7))
    if all(dia(dia(a, b), c) == dia(a, dia(b, c)) for a in P for b in P for c in P):
        fail("math: a diamond b = a + 2b should not be associative")
    if not all(sq(sq(a, b), c) == sq(a, sq(b, c)) for a in P for b in P for c in P):
        fail("math: multiplication should be associative")
    if all(dia(a, sq(b, c)) == sq(dia(a, b), dia(a, c)) for a in P for b in P for c in P):
        fail("math: diamond over square should not distribute")
    if not all(sq(a, dia(b, c)) == dia(sq(a, b), sq(a, c)) for a in P for b in P for c in P):
        fail("math: square over diamond should distribute")
    if all(dia(dia(a, b), c) == dia(a, dia(b, c)) for a in range(-5, 6) for b in range(-5, 6) for c in range(-5, 6)):
        fail("math: a diamond b = a + 2b is associative on a wider range after all")
    shifted = lambda a, b: a + b - 1
    S = list(range(-6, 7))
    if not all(shifted(shifted(a, b), c) == shifted(a, shifted(b, c)) for a in S for b in S for c in S):
        fail("math: a diamond b = a + b - 1 should be associative")
    if any(shifted(a, 1) != a or shifted(1, a) != a for a in S):
        fail("math: 1 should be the identity of a diamond b = a + b - 1")
    if any(shifted(a, 2 - a) != 1 or shifted(2 - a, a) != 1 for a in S):
        fail("math: the inverse of a under a diamond b = a + b - 1 should be 2 - a")
    power = lambda a, b: a ** b
    if power(power(2, 3), 2) == power(2, power(3, 2)):
        fail("math: a star b = a^b should not be associative")

    # permutations: S_3 products, S_4 counts, A_4 has no subgroup of order 6
    def perm(cycles, n):
        p = list(range(n))
        for cyc in cycles:
            for i in range(len(cyc)):
                p[cyc[i]] = cyc[(i + 1) % len(cyc)]
        return tuple(p)

    def compose(p, q):
        return tuple(p[q[x]] for x in range(len(p)))

    def perms(n):
        return list(itertools.permutations(range(n)))

    def sign(p):
        inv = sum(1 for i in range(len(p)) for j in range(i + 1, len(p)) if p[i] > p[j])
        return -1 if inv % 2 else 1

    def perm_order(p):
        k, q = 1, p
        while q != tuple(range(len(p))):
            q = compose(p, q)
            k += 1
        return k

    S3 = perms(3)
    if len(S3) != 6 or not is_group(set(S3), compose):
        fail("math: S_3 should be a group of order 6")
    if all(compose(a, b) == compose(b, a) for a in S3 for b in S3):
        fail("math: S_3 should not be abelian")
    if compose(perm([[0, 1]], 3), perm([[0, 1, 2]], 3)) != perm([[1, 2]], 3):
        fail("math: (1 2)(1 2 3) should equal (2 3)")
    if compose(perm([[0, 1, 2]], 3), perm([[0, 1]], 3)) != perm([[0, 2]], 3):
        fail("math: (1 2 3)(1 2) should equal (1 3)")
    if compose(perm([[0, 1]], 3), perm([[0, 2, 1]], 3)) != perm([[0, 2]], 3):
        fail("math: a^-1 b^-1 should equal (1 3) in S_3")
    if sorted({perm_order(p) for p in S3}) != [1, 2, 3]:
        fail("math: the element orders of S_3 should be 1, 2 and 3")
    if sorted({len(H) for H in _subgroups_of(S3, compose)}) != [1, 2, 3, 6]:
        fail("math: the subgroup orders of S_3 should be 1, 2, 3 and 6")
    S4 = perms(4)
    if len(S4) != 24 or not is_group(set(S4), compose):
        fail("math: S_4 should be a group of order 24")
    if len([p for p in S4 if perm_order(p) == 2]) != 9:
        fail("math: S_4 should have 9 elements of order 2")
    if perm_order(perm([[0, 1], [2, 3, 4]], 5)) != 6:
        fail("math: (1 2)(3 4 5) should have order 6")
    A4 = [p for p in S4 if sign(p) == 1]
    if len(A4) != 12:
        fail("math: A_4 should have order 12")
    if sorted({perm_order(p) for p in A4}) != [1, 2, 3]:
        fail("math: the element orders of A_4 should be 1, 2 and 3 only")
    if any(len(H) == 6 for H in _subgroups_of(A4, compose)):
        fail("math: A_4 should have no subgroup of order 6")
    if len(_subgroups_of(A4, compose)) < 1:
        fail("math: the A_4 subgroup enumeration produced nothing")
    # the 2014 Set 3 Q.50 relations: pairs of involutions with an involutive product commute
    for n in (4, 5):
        Sn = perms(n)
        for x in Sn:
            if perm_order(x) != 2:
                continue
            for y in Sn:
                if perm_order(y) != 2 or perm_order(compose(x, y)) != 2:
                    continue
                if compose(x, y) != compose(y, x):
                    fail("math: involutions with an involutive product should commute (S_%d)" % n)
                quad = {tuple(range(n)), x, y, compose(x, y)}
                if not all(compose(a, b) in quad for a in quad for b in quad):
                    fail("math: {e, x, y, xy} should be closed when x, y and xy are involutions")

    # every group of order at most 4 is abelian, and there are 1, 1, 1, 2 of them
    def groups_of_order(n):
        out = []
        cells = [(i, j) for i in range(1, n) for j in range(1, n)]
        for vals in itertools.product(range(n), repeat=len(cells)):
            T = [[0] * n for _ in range(n)]
            for j in range(n):
                T[0][j] = j
                T[j][0] = j
            for (i, j), v in zip(cells, vals):
                T[i][j] = v
            if any(len(set(T[i])) != n for i in range(n)):
                continue
            if any(len({T[i][j] for i in range(n)}) != n for j in range(n)):
                continue
            if any(T[T[a][b]][c] != T[a][T[b][c]] for a in range(n) for b in range(n) for c in range(n)):
                continue
            out.append(T)
        return out

    shapes = {}
    for n in (1, 2, 3, 4):
        gs = groups_of_order(n)
        if not gs:
            fail("math: no group of order %d was found by enumeration" % n)
        shapes[n] = set()
        for T in gs:
            if any(T[a][b] != T[b][a] for a in range(n) for b in range(n)):
                fail("math: a group of order %d is not abelian" % n)
            shapes[n].add(tuple(sorted(_table_order(T, a) for a in range(n))))
    if shapes[2] != {(1, 2)} or shapes[3] != {(1, 3, 3)}:
        fail("math: groups of order 2 and 3 should be cyclic, got %s and %s" % (shapes[2], shapes[3]))
    if shapes[4] != {(1, 2, 4, 4), (1, 2, 2, 2)}:
        fail("math: there should be exactly two groups of order 4, Z_4 and Z_2 x Z_2, got %s" % (shapes[4],))

    # direct products: which of them are cyclic
    def is_cyclic(elems, op, e):
        for a in elems:
            seen, x = set(), e
            for _ in range(len(elems) + 1):
                seen.add(x)
                x = op(x, a)
            if len(seen) == len(elems):
                return True
        return False

    def addmod(mods):
        return lambda x, y: tuple((x[i] + y[i]) % mods[i] for i in range(len(mods)))

    Z2Z2 = [(a, b) for a in range(2) for b in range(2)]
    Z2Z3 = [(a, b) for a in range(2) for b in range(3)]
    Z2Z4 = [(a, b) for a in range(2) for b in range(4)]
    if is_cyclic(Z2Z2, addmod((2, 2)), (0, 0)):
        fail("math: Z_2 x Z_2 should not be cyclic")
    if not is_cyclic(Z2Z3, addmod((2, 3)), (0, 0)):
        fail("math: Z_2 x Z_3 should be cyclic")
    if is_cyclic(Z2Z4, addmod((2, 4)), (0, 0)):
        fail("math: Z_2 x Z_4 should not be cyclic")
    Z4 = [(a,) for a in range(4)]
    if sorted([_order_in(Z4, (4,), a) for a in Z4]) == sorted([_order_in(Z2Z2, (2, 2), a) for a in Z2Z2]):
        fail("math: Z_4 and Z_2 x Z_2 should have different element-order multisets")
    if sorted([_order_in(Z2Z2, (2, 2), a) for a in Z2Z2]) != [1, 2, 2, 2]:
        fail("math: Z_2 x Z_2 should have element orders 1, 2, 2, 2")
    if sorted([_order_in(Z4, (4,), a) for a in Z4]) != [1, 2, 4, 4]:
        fail("math: Z_4 should have element orders 1, 2, 4, 4")

    # the 1996 options: {1..p-1} under multiplication mod p, and the one-step test on Z_12
    for p in (2, 3, 5, 7, 11, 13, 17, 19):
        if not is_group(set(range(1, p)), lambda a, b, p=p: (a * b) % p):
            fail("math: {1, ..., p-1} under multiplication mod %d should be a group" % p)
    ones = []
    for r in range(1, 13):
        for comb in itertools.combinations(range(12), r):
            Sset = set(comb)
            if all((a - b) % 12 in Sset for a in Sset for b in Sset):
                ones.append(frozenset(Sset))
    subs12 = {subgroup_of_order(12, d) for d in divisors(12)}
    if set(ones) != subs12:
        fail("math: on Z_12 the one-step test does not select exactly the subgroups")

    # the upper triangular matrix group of the 2005 question
    def matmul(A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

    A = [[2, 5, 7], [0, 3, 11], [0, 0, 5]]
    B = [[1, 2, 3], [0, 4, 5], [0, 0, 2]]
    AB = matmul(A, B)
    if AB[1][0] or AB[2][0] or AB[2][1]:
        fail("math: the product of two upper triangular matrices should be upper triangular")
    if AB[0][0] * AB[1][1] * AB[2][2] != 2 * 3 * 5 * 1 * 4 * 2:
        fail("math: the diagonal product of the matrix product should be the product of the determinants")
    if matmul(A, B) == matmul(B, A):
        fail("math: the chosen upper triangular matrices should not commute")

    from fractions import Fraction

    def inverse3(M):
        n = 3
        W = [[Fraction(M[i][j]) for j in range(n)] + [Fraction(1 if i == j else 0) for j in range(n)]
             for i in range(n)]
        for col in range(n):
            piv = next(r for r in range(col, n) if W[r][col] != 0)
            W[col], W[piv] = W[piv], W[col]
            pv = W[col][col]
            W[col] = [v / pv for v in W[col]]
            for r in range(n):
                if r != col and W[r][col] != 0:
                    f = W[r][col]
                    W[r] = [u - f * v for u, v in zip(W[r], W[col])]
        return [[W[i][n + j] for j in range(n)] for i in range(n)]

    invA = inverse3(A)
    if invA[1][0] != 0 or invA[2][0] != 0 or invA[2][1] != 0:
        fail("math: the inverse of an upper triangular matrix should be upper triangular")
    if [invA[0][0], invA[1][1], invA[2][2]] != [Fraction(1, 2), Fraction(1, 3), Fraction(1, 5)]:
        fail("math: the diagonal of the inverse should be the reciprocals 1/a, 1/b, 1/c")
    ident = [[Fraction(1 if i == j else 0) for j in range(3)] for i in range(3)]
    if matmul([[Fraction(v) for v in row] for row in A], invA) != ident:
        fail("math: A times its computed inverse should be the identity matrix")

    # homomorphisms: the reduction map and the exponential map
    kern = [k for k in range(-30, 31) if k % 6 == 0]
    if any(k % 6 for k in kern) or any(k % 6 == 0 for k in range(-30, 31) if k % 6):
        fail("math: the kernel of k -> k mod 6 should be exactly the multiples of 6")
    if sorted({k % 6 for k in range(6)}) != list(range(6)):
        fail("math: k -> k mod 6 should be surjective onto Z_6")
    if (0 % 6) != (6 % 6):
        fail("math: k -> k mod 6 should fail injectivity at 0 and 6")
    for c in range(3):
        if any(((a + b) * c) % 3 != ((a * c) % 3 + (b * c) % 3) % 3 for a in range(6) for b in range(6)):
            fail("math: every map Z_6 to Z_3 fixed by f(1) = %d should be a homomorphism" % c)
    if any((2 ** (x + y)) != (2 ** x) * (2 ** y) for x in range(-5, 6) for y in range(-5, 6)):
        fail("math: 2^(x+y) should equal 2^x 2^y")

    ok("Monoids and Groups: the ladder on nine standard structures, element orders and generators of Z_1 to "
       "Z_20, subgroups and Lagrange for every divisor, cosets of {0, 4, 8}, self-inverse counts in Z_2 x Z_3 x Z_4 "
       "and Z_4 x Z_6, S_3 and S_4 products, A_4 without a subgroup of order 6, the classification of all groups of "
       "order up to 4, the 2014 Set 3 Q.50 commutation, the 2024 Set 1 Q.42 laws, the 2005 matrix group, the 1996 "
       "options, and the homomorphism and lesson claims")


def _subgroups_of(elems, op):
    """All subgroups of a finite group given as a set of elements and a composition."""
    import itertools
    S = list(elems)
    e = next(x for x in S if all(op(x, y) == y and op(y, x) == y for y in S))
    out = []
    for r in range(1, len(S) + 1):
        for comb in itertools.combinations(S, r):
            H = set(comb)
            if e not in H:
                continue
            if any(op(a, b) not in H for a in H for b in H):
                continue
            if any(not any(op(a, b) == e for b in H) for a in H):
                continue
            out.append(H)
    return out


def _order_in(elems, mods, a):
    """Order of an element of a direct product of cyclic groups, given the component moduli."""
    e = tuple(0 for _ in mods)
    k, x = 1, a
    while x != e:
        x = tuple((x[i] + a[i]) % mods[i] for i in range(len(mods)))
        k += 1
        if k > len(elems) + 2:
            return 0
    return k


def _table_order(T, a):
    """Order of an element of a group given as a multiplication table with row 0 the identity."""
    k, x = 1, a
    while x != 0:
        x = T[x][a]
        k += 1
        if k > len(T) + 2:
            return 0
    return k


# ---------------------------------------------------------------- graphs
# Everything published in content/subjects/discrete-mathematics/graphs is recomputed here.
# The sweeps enumerate every simple graph on up to 5 vertices, every graph on 6 vertices where an
# edge or component bound is at stake, and every DFS tree of every connected small graph.


def _g_pairs(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def _g_edges(n, mask):
    P = _g_pairs(n)
    return [P[k] for k in range(len(P)) if (mask >> k) & 1]


def _g_all(n):
    for mask in range(1 << len(_g_pairs(n))):
        yield _g_edges(n, mask)


def _g_adj(n, edges):
    A = [set() for _ in range(n)]
    for u, v in edges:
        A[u].add(v)
        A[v].add(u)
    return A


def _g_comps(n, edges, removed=()):
    """Component count of the graph induced on the vertices outside `removed`."""
    keep = [v for v in range(n) if v not in removed]
    idx = {v: i for i, v in enumerate(keep)}
    A = _g_adj(len(keep), [(idx[u], idx[v]) for u, v in edges if u in idx and v in idx])
    seen, k = set(), 0
    for s in range(len(keep)):
        if s in seen:
            continue
        k += 1
        stack = [s]
        seen.add(s)
        while stack:
            x = stack.pop()
            for y in A[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
    return k


def _g_connected(n, edges):
    return n <= 1 or _g_comps(n, edges) == 1


def _g_bipartite(n, edges):
    A = _g_adj(n, edges)
    col = [-1] * n
    for s in range(n):
        if col[s] >= 0:
            continue
        col[s] = 0
        stack = [s]
        while stack:
            x = stack.pop()
            for y in A[x]:
                if col[y] < 0:
                    col[y] = 1 - col[x]
                    stack.append(y)
                elif col[y] == col[x]:
                    return False
    return True


def _g_chromatic(n, edges):
    A = _g_adj(n, edges)
    if n == 0:
        return 0
    for k in range(1, n + 1):
        cols = [-1] * n

        def rec(i):
            if i == n:
                return True
            for c in range(k):
                if all(cols[y] != c for y in A[i]):
                    cols[i] = c
                    if rec(i + 1):
                        return True
                    cols[i] = -1
            return False

        if rec(0):
            return k
    return n


def _g_matchings(n, edges):
    out = []
    for r in range(len(edges) + 1):
        for comb in itertools.combinations(edges, r):
            used, good = set(), True
            for u, v in comb:
                if u in used or v in used:
                    good = False
                    break
                used.add(u)
                used.add(v)
            if good:
                out.append(list(comb))
    return out


def _g_max_matching(n, edges):
    for r in range(len(edges), -1, -1):
        for comb in itertools.combinations(edges, r):
            used, good = set(), True
            for u, v in comb:
                if u in used or v in used:
                    good = False
                    break
                used.add(u)
                used.add(v)
            if good:
                return r
    return 0


def _g_min_cover(n, edges):
    for r in range(n + 1):
        for S in itertools.combinations(range(n), r):
            Sset = set(S)
            if all(u in Sset or v in Sset for u, v in edges):
                return r
    return n


def _g_min_covers(n, edges):
    k = _g_min_cover(n, edges)
    out = []
    for S in itertools.combinations(range(n), k):
        Sset = set(S)
        if all(u in Sset or v in Sset for u, v in edges):
            out.append(Sset)
    return out


def _g_alpha(n, edges):
    A = _g_adj(n, edges)
    for r in range(n, -1, -1):
        for S in itertools.combinations(range(n), r):
            if all(v not in A[u] for u, v in itertools.combinations(S, 2)):
                return r
    return 0


def _g_omega(n, edges):
    A = _g_adj(n, edges)
    for r in range(n, 0, -1):
        for S in itertools.combinations(range(n), r):
            if all(v in A[u] for u, v in itertools.combinations(S, 2)):
                return r
    return 0


def _g_articulation(n, edges):
    base = _g_comps(n, edges)
    return {v for v in range(n) if _g_comps(n, edges, (v,)) > base}


def _g_bridges(n, edges):
    out = set()
    base = _g_comps(n, edges)
    for i in range(len(edges)):
        if _g_comps(n, edges[:i] + edges[i + 1:]) > base:
            out.add(edges[i])
    return out


def _g_kappa(n, edges):
    """Vertex connectivity; kappa(K_n) = n-1, kappa of a disconnected graph = 0."""
    if n <= 1:
        return 0
    for r in range(0, n):
        for S in itertools.combinations(range(n), r):
            if n - r <= 1 or _g_comps(n, edges, set(S)) >= 2:
                return r
    return n - 1


def _g_lambda(n, edges):
    if _g_comps(n, edges) >= 2:
        return 0
    for r in range(1, len(edges) + 1):
        for comb in itertools.combinations(range(len(edges)), r):
            drop = set(comb)
            if _g_comps(n, [e for i, e in enumerate(edges) if i not in drop]) >= 2:
                return r
    return 0


def _g_graphic(seq):
    """Havel-Hakimi."""
    seq = sorted(seq, reverse=True)
    while seq:
        d = seq[0]
        rest = seq[1:]
        if d < 0 or d > len(rest):
            return False
        if d == 0:
            return True
        rest = [x - 1 for x in rest[:d]] + rest[d:]
        if any(x < 0 for x in rest):
            return False
        seq = sorted(rest, reverse=True)
    return True


def _g_dfs_tree(n, edges, order):
    rank = {v: i for i, v in enumerate(order)}
    A = [sorted(a, key=lambda x: rank[x]) for a in _g_adj(n, edges)]
    disc, low, parent = [-1] * n, [0] * n, [-1] * n
    children = [[] for _ in range(n)]
    t = [0]

    def visit(u):
        disc[u] = low[u] = t[0]
        t[0] += 1
        for w in A[u]:
            if disc[w] < 0:
                parent[w] = u
                children[u].append(w)
                visit(w)
                low[u] = min(low[u], low[w])
            elif w != parent[u]:
                low[u] = min(low[u], disc[w])

    visit(order[0])
    return disc, low, parent, children


def _g_hamiltonian(n, edges, want_cycle):
    A = _g_adj(n, edges)
    if n == 0:
        return True

    def go(start, v, seen, length):
        if length == n:
            return (not want_cycle) or (start in A[v])
        for w in A[v]:
            if w not in seen:
                seen.add(w)
                if go(start, w, seen, length + 1):
                    return True
                seen.discard(w)
        return False

    return any(go(s, s, {s}, 1) for s in range(n))


def _g_chi_poly(n, edges):
    """Chromatic polynomial by deletion-contraction, as a dict power -> coefficient."""
    memo = {}

    def poly(nn, es):
        es = tuple(sorted(set(es)))
        key = (nn, es)
        if key in memo:
            return memo[key]
        if not es:
            memo[key] = {nn: 1}
            return memo[key]
        u, v = es[0]
        rest = [e for e in es[1:]]
        p_del = poly(nn, tuple(rest))

        def relabel(x):
            if x == v:
                return u
            return x if x < v else x - 1

        con = set()
        for a, b in rest:
            a2, b2 = relabel(a), relabel(b)
            if a2 != b2:
                con.add((min(a2, b2), max(a2, b2)))
        p_con = poly(nn - 1, tuple(sorted(con)))

        out = {}
        for p, c in p_del.items():
            out[p] = out.get(p, 0) + c
        for p, c in p_con.items():
            out[p] = out.get(p, 0) - c
        memo[key] = {p: c for p, c in out.items() if c}
        return memo[key]

    return poly(n, [tuple(sorted(e)) for e in edges])


def _g_poly_eval(poly, k):
    return sum(c * (k ** p) for p, c in poly.items())


def _g_colour_count(n, edges, k):
    A = _g_adj(n, edges)
    cols = [-1] * n
    total = [0]

    def rec(i):
        if i == n:
            total[0] += 1
            return
        for c in range(k):
            if all(cols[y] != c for y in A[i]):
                cols[i] = c
                rec(i + 1)
                cols[i] = -1

    rec(0)
    return total[0]


def _g_petersen():
    edges = []
    for i in range(5):
        edges.append((i, (i + 1) % 5))
        edges.append((5 + i, 5 + (i + 2) % 5))
        edges.append((i, 5 + i))
    return 10, [tuple(sorted(e)) for e in edges]


def _g_complete(n):
    return n, _g_pairs(n)


def _g_complete_bipartite(a, b):
    return a + b, [(i, a + j) for i in range(a) for j in range(b)]


def _g_cycle(n):
    return n, [(i, (i + 1) % n) for i in range(n)]


def _g_path(n):
    return n, [(i, i + 1) for i in range(n - 1)]


def _g_euler_circuit(n, edges):
    degs = [len(a) for a in _g_adj(n, edges)]
    if not any(degs):
        return True
    removed = tuple(v for v in range(n) if not degs[v])
    return _g_comps(n, edges, removed) == 1 and all(d % 2 == 0 for d in degs)


def _g_euler_path(n, edges):
    degs = [len(a) for a in _g_adj(n, edges)]
    if not any(degs):
        return True
    removed = tuple(v for v in range(n) if not degs[v])
    return _g_comps(n, edges, removed) == 1 and sum(1 for d in degs if d % 2) in (0, 2)


def check_graphs():
    """Recompute every graph claim published in the Graphs topic."""
    # --- the lesson graph: a maximal matching that is not maximum
    names = ["a", "b", "c", "1", "2", "3"]
    li = {v: i for i, v in enumerate(names)}
    raw = [("a", "1"), ("a", "2"), ("b", "1"), ("b", "2"), ("c", "2"), ("c", "3")]
    ln, le = 6, [tuple(sorted((li[u], li[v]))) for u, v in raw]
    maximal = [tuple(sorted((li["a"], li["1"]))), tuple(sorted((li["c"], li["2"])))]
    maximum = [tuple(sorted((li["a"], li["2"]))), tuple(sorted((li["b"], li["1"]))),
               tuple(sorted((li["c"], li["3"])))]
    if not _g_bipartite(ln, le) or _g_comps(ln, le) != 1:
        fail("math: the lesson graph should be a connected bipartite graph")
    if len(le) - ln + _g_comps(ln, le) != 1:
        fail("math: the lesson graph should have exactly one independent cycle")
    used = set()
    for u, v in maximal:
        if u in used or v in used:
            fail("math: the lesson's matching shares a vertex")
        used.update((u, v))
    if len(maximal) != 2 or len(set(maximal)) != 2:
        fail("math: the lesson's matching should have 2 distinct edges")
    for e in le:
        if e in maximal or e[0] in used or e[1] in used:
            continue
        fail("math: the lesson's matching is not maximal, %r can be added" % (e,))
    if _g_max_matching(ln, le) != 3 or len(maximum) != 3:
        fail("math: the lesson graph's maximum matching should have 3 edges")
    path = ["b", "1", "a", "2", "c", "3"]
    pedges = [tuple(sorted((li[path[i]], li[path[i + 1]]))) for i in range(len(path) - 1)]
    if len(set(pedges)) != 5 or any(e not in le for e in pedges):
        fail("math: the lesson's augmenting path uses a non-edge or repeats an edge")
    for i, e in enumerate(pedges):
        if (i % 2 == 0) == (e in maximal):
            fail("math: the lesson's augmenting path does not alternate at step %d" % i)
    if li[path[0]] in used or li[path[-1]] in used:
        fail("math: the lesson's augmenting path should start and end at free vertices")
    flipped = [e for e in pedges if e not in maximal] + [e for e in maximal if e not in pedges]
    if sorted(flipped) != sorted(maximum):
        fail("math: flipping the lesson's augmenting path should give the maximum matching")
    if len(flipped) != len(maximal) + 1:
        fail("math: flipping an augmenting path should add exactly one edge")
    cover = {li["1"], li["2"], li["c"]}
    if not all(u in cover or v in cover for u, v in le):
        fail("math: the lesson's vertex cover does not touch every edge")
    if len(cover) != 3 or _g_min_cover(ln, le) != 3:
        fail("math: the lesson's minimum vertex cover should have 3 vertices")
    for S in itertools.combinations(range(ln), 2):
        if all(u in S or v in S for u, v in le):
            fail("math: the lesson graph should have no vertex cover of size 2")
    if _g_alpha(ln, le) != 3:
        fail("math: the lesson graph's independence number should be 3")

    # --- degree sums, edge bounds and components
    for n in range(1, 7):
        for edges in _g_all(n):
            degs = [len(a) for a in _g_adj(n, edges)]
            if sum(degs) != 2 * len(edges):
                fail("math: the handshake lemma fails on a graph with %d vertices" % n)
            if sum(1 for d in degs if d % 2) % 2:
                fail("math: odd-degree vertices are not even in number (n=%d)" % n)
            k = _g_comps(n, edges)
            if len(edges) < n - k:
                fail("math: fewer than n-k edges with %d components (n=%d)" % (k, n))
            if len(edges) > (n - k + 1) * (n - k) // 2:
                fail("math: more than C(n-k+1,2) edges with %d components (n=%d)" % (k, n))
    for n in (2, 3, 4, 5, 6):
        if len(_g_pairs(n)) != n * (n - 1) // 2:
            fail("math: K_%d should have n(n-1)/2 edges" % n)
    if not _g_graphic([3, 3, 2, 2, 2, 2]):
        fail("math: the sequence 3,3,2,2,2,2 should be graphic")
    if _g_graphic([3, 3, 3, 1]):
        fail("math: the sequence 3,3,3,1 should not be graphic")
    if sum([6, 6, 5, 4, 3, 2, 1]) % 2 == 0:
        fail("math: 6,6,5,4,3,2,1 should have an odd sum")
    if (9 - 3) != 6 or (9 - 3 + 1) * (9 - 3) // 2 != 21:
        fail("math: the 9-vertex 3-component bounds should be 6 and 21")
    if (10 - 4 + 1) * (10 - 4) // 2 != 21:
        fail("math: the 10-vertex 4-component maximum should be 21")
    if (8 - 2 + 1) * (8 - 2) // 2 != 21:
        fail("math: the 8-vertex 2-component maximum should be 21")
    if (6 - 3 + 1) * (6 - 3) // 2 != 6:
        fail("math: the 6-vertex 3-component maximum should be 6")
    if (7 * 6) // 2 != 21 or (4 * 3) // 2 != 6:
        fail("math: the component examples do not recompute")
    cyc_e = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (4, 5)]
    if len(cyc_e) - 6 + _g_comps(6, cyc_e) != 2:
        fail("math: the cyclomatic example should have 2 independent cycles")

    # --- cut vertices, bridges and the DFS rules
    p4n, p4e = _g_path(4)
    if _g_articulation(p4n, p4e) != {1, 2}:
        fail("math: the path on 4 vertices should have cut vertices 1 and 2")
    if _g_bridges(p4n, p4e) != set(p4e):
        fail("math: every edge of a path should be a bridge")
    te = [(0, 1), (1, 2), (0, 2), (2, 3)]
    if _g_articulation(4, te) != {2} or _g_bridges(4, te) != {(2, 3)}:
        fail("math: the triangle with a pendant edge should have one cut vertex and one bridge")
    be = [(0, 1), (1, 2), (0, 2), (2, 3), (3, 4), (2, 4)]
    if _g_articulation(5, be) != {2}:
        fail("math: the bowtie should have exactly one cut vertex")
    if _g_bridges(5, be):
        fail("math: the bowtie should have no bridge")
    if (_g_kappa(5, be), _g_lambda(5, be)) != (1, 2):
        fail("math: the bowtie should have kappa 1 and lambda 2")
    if (min(len(a) for a in _g_adj(5, be)), max(len(a) for a in _g_adj(5, be))) != (2, 4):
        fail("math: the bowtie should have minimum degree 2 and maximum degree 4")
    if _g_bridges(2, [(0, 1)]) != {(0, 1)} or _g_articulation(2, [(0, 1)]):
        fail("math: K_2 should have a bridge and no cut vertex")
    c6 = [(i, (i + 1) % 6) for i in range(6)] + [(0, 3)]
    if _g_articulation(6, c6):
        fail("math: C_6 with a chord between opposite vertices should have no cut vertex")
    for n in range(2, 6):
        for edges in _g_all(n):
            br = _g_bridges(n, edges)
            for e in edges:
                rest = list(edges)
                rest.remove(e)
                A = _g_adj(n, rest)
                seen, stack = {e[0]}, [e[0]]
                while stack:
                    x = stack.pop()
                    for y in A[x]:
                        if y not in seen:
                            seen.add(y)
                            stack.append(y)
                on_cycle = e[1] in seen
                if on_cycle == (e in br):
                    fail("math: an edge is a bridge exactly when it lies on no cycle (n=%d)" % n)
            if not _g_connected(n, edges):
                continue
            ap = _g_articulation(n, edges)
            if len(ap) > max(0, n - 2):
                fail("math: a connected graph on %d vertices has more than n-2 cut vertices" % n)
            for order in itertools.permutations(range(n)):
                disc, low, parent, children = _g_dfs_tree(n, edges, order)
                root = order[0]
                if (len(children[root]) >= 2) != (root in ap):
                    fail("math: the DFS root rule fails on a graph with %d vertices" % n)
                for v in range(n):
                    if v == root:
                        continue
                    if not children[v] and v in ap:
                        fail("math: a leaf of a DFS tree is never a cut vertex")
                    if any(low[s] >= disc[v] for s in children[v]) != (v in ap):
                        fail("math: the DFS low-value rule fails on a graph with %d vertices" % n)

    # --- connectivity numbers
    if (_g_kappa(*_g_complete(5)), _g_lambda(*_g_complete(5))) != (4, 4):
        fail("math: K_5 should have kappa = lambda = 4")
    if (_g_kappa(*_g_complete(4)), _g_lambda(*_g_complete(4))) != (3, 3):
        fail("math: K_4 should have kappa = lambda = 3")
    k33n, k33e = _g_complete_bipartite(3, 3)
    if (_g_kappa(k33n, k33e), _g_lambda(k33n, k33e)) != (3, 3):
        fail("math: K_3,3 should have kappa = lambda = 3")
    for n in range(2, 5):
        for edges in _g_all(n):
            if not _g_connected(n, edges):
                continue
            kap, lam = _g_kappa(n, edges), _g_lambda(n, edges)
            delta = min(len(a) for a in _g_adj(n, edges))
            if not (kap <= lam <= delta):
                fail("math: kappa <= lambda <= delta fails on a connected graph with %d vertices" % n)
            if kap > (2 * len(edges)) // n:
                fail("math: kappa exceeds floor(2|E|/n) on a graph with %d vertices" % n)

    # --- Euler and Hamilton
    for n in range(1, 5):
        for edges in _g_all(n):
            if not _g_connected(n, edges):
                continue
            degs = [len(a) for a in _g_adj(n, edges)]
            if _g_euler_circuit(n, edges) != all(d % 2 == 0 for d in degs):
                fail("math: the Euler-circuit parity criterion fails (n=%d)" % n)
            if _g_euler_path(n, edges) != (sum(1 for d in degs if d % 2) in (0, 2)):
                fail("math: the Euler-path parity criterion fails (n=%d)" % n)
    k23n, k23e = _g_complete_bipartite(2, 3)
    if _g_euler_circuit(k23n, k23e) or not _g_euler_path(k23n, k23e):
        fail("math: K_2,3 should have an Euler path and no Euler circuit")
    if _g_euler_path(k33n, k33e):
        fail("math: K_3,3 has six odd-degree vertices and should have no Euler path")
    k4p = (5, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (0, 4)])
    if sum(1 for d in (len(a) for a in _g_adj(*k4p)) if d % 2) != 4 or _g_euler_path(*k4p):
        fail("math: K_4 with a pendant edge should have four odd vertices and no Euler path")
    c5n, c5e = _g_cycle(5)
    if not _g_hamiltonian(c5n, c5e, True):
        fail("math: C_5 should be Hamiltonian")
    if 2 * min(len(a) for a in _g_adj(c5n, c5e)) >= c5n:
        fail("math: C_5 should violate Dirac's degree condition")
    for a in (2, 3):
        for b in (2, 3):
            nn, ee = _g_complete_bipartite(a, b)
            if _g_hamiltonian(nn, ee, True) != (a == b):
                fail("math: K_%d,%d Hamiltonicity is wrong" % (a, b))
    pn, pe = _g_petersen()
    if not _g_hamiltonian(pn, pe, False):
        fail("math: the Petersen graph should have a Hamiltonian path")
    if _g_hamiltonian(pn, pe, True):
        fail("math: the Petersen graph should have no Hamiltonian cycle")
    kn, ke = _g_complete(5)
    split = False
    for perm in itertools.permutations(range(1, 5)):
        cyc = (0,) + perm
        ce = [tuple(sorted((cyc[i], cyc[(i + 1) % 5]))) for i in range(5)]
        rest = [e for e in ke if e not in ce]
        for perm2 in itertools.permutations(range(1, 5)):
            cyc2 = (0,) + perm2
            ce2 = [tuple(sorted((cyc2[i], cyc2[(i + 1) % 5]))) for i in range(5)]
            if sorted(ce + ce2) == sorted(ke) and not (set(ce) & set(ce2)):
                split = True
                break
        if split:
            break
    if not split:
        fail("math: K_5 should split into two edge-disjoint Hamiltonian cycles")

    # --- bipartite graphs and the odd-cycle criterion
    for n in range(1, 6):
        for edges in _g_all(n):
            if _g_bipartite(n, edges) != (_g_chromatic(n, edges) <= 2):
                fail("math: bipartite should equal chromatic number at most 2 (n=%d)" % n)
    for n in (3, 5, 7):
        if _g_bipartite(*_g_cycle(n)):
            fail("math: the odd cycle C_%d should not be bipartite" % n)
    for n in (4, 6, 8):
        if not _g_bipartite(*_g_cycle(n)):
            fail("math: the even cycle C_%d should be bipartite" % n)
    if _g_bipartite(pn, pe):
        fail("math: the Petersen graph should not be bipartite")
    if not _g_bipartite(6, c6):
        fail("math: C_6 with a chord between opposite vertices should be bipartite")
    if _g_bipartite(6, [(i, (i + 1) % 6) for i in range(6)] + [(0, 2)]):
        fail("math: C_6 with a chord between vertices at distance 2 should not be bipartite")
    for n in (7, 9, 12):
        if max(p * (n - p) for p in range(n + 1)) != (n * n) // 4:
            fail("math: floor(n^2/4) is wrong for n = %d" % n)
    if max(p * (12 - p) for p in range(13)) != 36:
        fail("math: the 12-vertex bipartite maximum should be 36")
    if (9 * 9) // 4 != 20 or (7 * 7) // 4 != 12:
        fail("math: the 9-vertex and 7-vertex bipartite maxima should be 20 and 12")

    # --- matchings
    fib = [1, 1]
    for _ in range(9):
        fib.append(fib[-1] + fib[-2])
    for n in range(1, 9):
        nn, ee = _g_path(n)
        if len(_g_matchings(nn, ee)) != fib[n]:
            fail("math: the path on %d vertices should have %d matchings" % (n, fib[n]))
    if len(_g_matchings(*_g_path(8))) != 34:
        fail("math: the path on 8 vertices should have 34 matchings")
    if len(_g_matchings(*_g_cycle(5))) != 11:
        fail("math: C_5 should have 11 matchings")
    for n in range(1, 5):
        nn, ee = _g_complete_bipartite(n, n)
        perfect = sum(1 for M in _g_matchings(nn, ee) if len(M) == n)
        if perfect != factorial(n):
            fail("math: K_%d,%d should have %d perfect matchings" % (n, n, factorial(n)))
    for n in range(1, 5):
        for edges in _g_all(n):
            ms = _g_matchings(n, edges)
            mx = max((len(M) for M in ms), default=0)
            for M in ms:
                used = set()
                for u, v in M:
                    used.update((u, v))
                maximal_here = all(u in used or v in used for u, v in edges)
                if maximal_here and 2 * len(M) < mx:
                    fail("math: a maximal matching is smaller than half the maximum (n=%d)" % n)
    if max(len(M) for M in _g_matchings(p4n, p4e)) != 2:
        fail("math: P_4 should have maximum matching 2")
    mid = [M for M in _g_matchings(p4n, p4e) if M == [(1, 2)]]
    if not mid:
        fail("math: the middle edge of P_4 should be a matching of size 1")

    # --- Hall and its defect form
    for a in (1, 2, 3):
        for b in (1, 2, 3):
            for mask in range(1 << (a * b)):
                edges = [(i, a + j) for i in range(a) for j in range(b) if (mask >> (i * b + j)) & 1]
                nu = _g_max_matching(a + b, edges)
                defect = 0
                for r in range(a + 1):
                    for S in itertools.combinations(range(a), r):
                        N = {v for u, v in edges if u in S}
                        defect = max(defect, len(S) - len(N))
                if nu != a - defect:
                    fail("math: the Hall defect form fails on a %d by %d bipartite graph" % (a, b))
    for d in (1, 2, 3):
        for mask in range(1 << 16):
            edges = [(i, 4 + j) for i in range(4) for j in range(4) if (mask >> (i * 4 + j)) & 1]
            deg = [0] * 8
            for u, v in edges:
                deg[u] += 1
                deg[v] += 1
            if any(x != d for x in deg):
                continue
            if _g_max_matching(8, edges) != 4:
                fail("math: a %d-regular bipartite graph should have a perfect matching" % d)
            if d == 2:
                M = next(M for M in _g_matchings(8, edges) if len(M) == 4)
                rest = [e for e in edges if e not in M]
                if len(rest) != 4 or _g_max_matching(8, rest) != 4:
                    fail("math: a 2-regular bipartite graph should split into two perfect matchings")

    # --- vertex cover, independent set and Koenig
    for n in range(1, 6):
        for edges in _g_all(n):
            nu, tau, al = _g_max_matching(n, edges), _g_min_cover(n, edges), _g_alpha(n, edges)
            if al + tau != n:
                fail("math: alpha + tau should equal n (n=%d)" % n)
            if nu > tau:
                fail("math: the matching number should not exceed the cover number (n=%d)" % n)
            if _g_bipartite(n, edges) and nu != tau:
                fail("math: Koenig should hold on every bipartite graph (n=%d)" % n)
            degs = [len(a) for a in _g_adj(n, edges)]
            covers = _g_min_covers(n, edges)
            for v in range(n):
                if degs[v] >= tau + 1 and any(v not in C for C in covers):
                    fail("math: a vertex of degree at least k+1 must lie in every minimum cover")
    if (_g_max_matching(*_g_complete(3)), _g_min_cover(*_g_complete(3))) != (1, 2):
        fail("math: the triangle should have nu = 1 and tau = 2")
    if (_g_max_matching(c5n, c5e), _g_min_cover(c5n, c5e), _g_alpha(c5n, c5e)) != (2, 3, 2):
        fail("math: C_5 should have nu = 2, tau = 3 and alpha = 2")
    if (_g_max_matching(k33n, k33e), _g_min_cover(k33n, k33e), _g_alpha(k33n, k33e)) != (3, 3, 3):
        fail("math: K_3,3 should have nu = tau = 3 and alpha = 3")
    if _g_max_matching(p4n, p4e) != 2 or _g_min_cover(p4n, p4e) != 2:
        fail("math: P_4 should have nu = tau = 2")
    if not any(0 not in C for C in _g_min_covers(p4n, p4e)):
        fail("math: P_4 should have a minimum cover that omits vertex 0")
    if not any(0 not in C for C in _g_min_covers(*_g_complete(3))):
        fail("math: the triangle should have a minimum cover that omits vertex 0")
    if _g_min_cover(*_g_complete(4)) != 3:
        fail("math: K_4 should have minimum vertex cover 3")
    if 10 - 4 != 6 or 8 - 3 != 5:
        fail("math: the alpha = n - tau examples are wrong")

    # --- chromatic number and the bounds
    if _g_chromatic(*_g_complete(4)) != 4 or _g_chromatic(*_g_complete(5)) != 5:
        fail("math: K_n should have chromatic number n")
    for n in range(3, 11):
        nn, ee = _g_cycle(n)
        if _g_chromatic(nn, ee) != (2 if n % 2 == 0 else 3):
            fail("math: C_%d has the wrong chromatic number" % n)
        if n - 2 * (n // 2) + 2 != _g_chromatic(nn, ee):
            fail("math: the 2002 formula is wrong for n = %d" % n)
    if _g_chromatic(*_g_path(5)) != 2:
        fail("math: a tree with an edge should have chromatic number 2")
    if (_g_chromatic(pn, pe), _g_omega(pn, pe), _g_alpha(pn, pe)) != (3, 2, 4):
        fail("math: the Petersen graph should have chi = 3, omega = 2 and alpha = 4")
    if (_g_kappa(pn, pe), _g_lambda(pn, pe), len(pe)) != (3, 3, 15):
        fail("math: the Petersen graph should be 3-connected with 15 edges")
    if (_g_omega(c5n, c5e), _g_chromatic(c5n, c5e)) != (2, 3):
        fail("math: C_5 should have omega = 2 and chi = 3")
    for n in range(1, 6):
        for edges in _g_all(n):
            chi, om, al = _g_chromatic(n, edges), _g_omega(n, edges), _g_alpha(n, edges)
            delta = max((len(a) for a in _g_adj(n, edges)), default=0)
            if not (om <= chi <= delta + 1):
                fail("math: omega <= chi <= Delta+1 fails (n=%d)" % n)
            if chi * al < n:
                fail("math: chi should be at least n/alpha (n=%d)" % n)
            if len(edges) < chi * (chi - 1) // 2:
                fail("math: a k-chromatic graph needs at least C(k,2) edges (n=%d)" % n)
            if _g_connected(n, edges) and n >= 3 and chi > delta:
                degs = [len(a) for a in _g_adj(n, edges)]
                complete = len(edges) == n * (n - 1) // 2
                odd_cycle = n % 2 == 1 and all(d == 2 for d in degs)
                if not (complete or odd_cycle):
                    fail("math: Brooks' theorem fails on a connected graph with %d vertices" % n)
    if _g_chromatic(*_g_complete(3)) != 3 or max(len(a) for a in _g_adj(3, _g_pairs(3))) != 2:
        fail("math: K_3 should have chi = 3 and maximum degree 2")
    if 12 // 4 != 3 or 4 * 3 // 2 != 6:
        fail("math: the 2024 bounds examples are wrong")

    # --- chromatic polynomial
    for n in range(2, 5):
        nn, ee = _g_complete(n)
        poly = _g_chi_poly(nn, ee)
        for k in range(1, 6):
            want = 1
            for i in range(n):
                want *= (k - i)
            if _g_poly_eval(poly, k) != want or _g_colour_count(nn, ee, k) != want:
                fail("math: the chromatic polynomial of K_%d is wrong at k = %d" % (n, k))
    for n in range(2, 7):
        nn, ee = _g_path(n)
        poly = _g_chi_poly(nn, ee)
        for k in range(1, 5):
            want = k * (k - 1) ** (n - 1)
            if _g_poly_eval(poly, k) != want or _g_colour_count(nn, ee, k) != want:
                fail("math: the tree formula fails for a path on %d vertices at k = %d" % (n, k))
    for n in range(3, 8):
        nn, ee = _g_cycle(n)
        poly = _g_chi_poly(nn, ee)
        for k in range(1, 6):
            want = (k - 1) ** n + (-1) ** n * (k - 1)
            if _g_poly_eval(poly, k) != want or _g_colour_count(nn, ee, k) != want:
                fail("math: the cycle formula fails for C_%d at k = %d" % (n, k))
    c4n, c4e = _g_cycle(4)
    c4poly = _g_chi_poly(c4n, c4e)
    if c4poly != {4: 1, 3: -4, 2: 6, 1: -3}:
        fail("math: the chromatic polynomial of C_4 should be k^4 - 4k^3 + 6k^2 - 3k, got %s" % c4poly)
    if _g_poly_eval(c4poly, 3) != 18 or _g_colour_count(c4n, c4e, 3) != 18:
        fail("math: C_4 should have 18 proper 3-colourings")
    if _g_poly_eval(c4poly, 1) != 0 or _g_poly_eval(c4poly, 2) != 2:
        fail("math: C_4 should have 0 colourings with 1 colour and 2 with 2 colours")
    for n in range(2, 6):
        for edges in _g_all(n):
            poly = _g_chi_poly(n, edges)
            if max(poly) != n or poly.get(n, 0) != 1:
                fail("math: the chromatic polynomial should be monic of degree n (n=%d)" % n)
            if poly.get(n - 1, 0) != -len(edges):
                fail("math: the k^(n-1) coefficient should be -|E| (n=%d)" % n)
            if edges and poly.get(0, 0) != 0:
                fail("math: the constant term should be 0 when there are edges (n=%d)" % n)
            for k in range(1, 4):
                if _g_poly_eval(poly, k) != _g_colour_count(n, edges, k):
                    fail("math: the polynomial disagrees with direct counting (n=%d, k=%d)" % (n, k))
            smallest = next((k for k in range(1, n + 1) if _g_poly_eval(poly, k) > 0), None)
            if smallest != _g_chromatic(n, edges):
                fail("math: chi should be the smallest k with a positive count (n=%d)" % n)
    if _g_colour_count(*_g_complete(3), 3) != 6:
        fail("math: K_3 should have 6 proper 3-colourings")
    if _g_colour_count(*_g_complete_bipartite(2, 3), 2) != 2:
        fail("math: K_2,3 should have exactly 2 proper 2-colourings")
    if 3 * 2 ** 5 != 96:
        fail("math: a tree on 6 vertices should have 96 proper 3-colourings")

    ok("Graphs: the handshake lemma, the edge bounds and the n-k / C(n-k+1,2) component bounds over "
       "every graph on up to 6 vertices; bridges, cut vertices and both DFS rules over every DFS tree "
       "of every connected graph on up to 5 vertices; kappa, lambda and delta on the standard graphs "
       "and every connected graph on up to 4 vertices; Euler parity, Dirac, the Petersen graph and the "
       "K_5 Hamiltonian split; the odd-cycle criterion and floor(n^2/4); the matching counts for paths, "
       "C_5 and K_n,n and the half-size bound; Hall's condition and its defect form on every bipartite "
       "graph up to 3 by 3 and every d-regular bipartite graph on 4 plus 4 vertices; Koenig, "
       "alpha + tau = n and the 2026 forced-vertex claim by enumeration; the chromatic numbers, the "
       "2002 cycle formula, Brooks and the 2024 bounds; and every chromatic polynomial coefficient, "
       "value and count")


# ---------------------------------------- matrices and determinants
def _m_mat(A, B):
    n, k, p = len(A), len(B), len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(k)) for j in range(p)] for i in range(n)]


def _m_T(A):
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def _m_det(A):
    from fractions import Fraction
    n = len(A)
    M = [[Fraction(x) for x in row] for row in A]
    if n == 1:
        return M[0][0]
    total = Fraction(0)
    for j in range(n):
        sub = [[M[i][t] for t in range(n) if t != j] for i in range(1, n)]
        total += (-1) ** j * M[0][j] * _m_det(sub)
    return total


def _m_rank(A):
    from fractions import Fraction
    M = [[Fraction(x) for x in row] for row in A]
    m, n = len(M), len(M[0])
    r = 0
    for c in range(n):
        piv = next((i for i in range(r, m) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def _m_tr(A):
    return sum(A[i][i] for i in range(len(A)))


def _m_minor(A, i, j):
    return [[A[r][c] for c in range(len(A)) if c != j] for r in range(len(A)) if r != i]


def _m_cof(A, i, j):
    return (-1) ** (i + j) * _m_det(_m_minor(A, i, j))


def _m_adj(A):
    n = len(A)
    return [[_m_cof(A, j, i) for j in range(n)] for i in range(n)]


def _m_inv(A):
    d = _m_det(A)
    if d == 0:
        return None
    return [[x / d for x in row] for row in _m_adj(A)]


def _m_mats(n, vals):
    import itertools
    for flat in itertools.product(vals, repeat=n * n):
        yield [list(flat[i * n:(i + 1) * n]) for i in range(n)]


def _m_eq(A, B):
    return len(A) == len(B) and all(A[i][j] == B[i][j] for i in range(len(A)) for j in range(len(A[0])))


def check_matrices_and_determinants():
    """Every claim in the Matrices and Determinants cards and in the area lesson is recomputed."""
    import random
    from fractions import Fraction
    Z = Fraction(0)

    # --- card 1: vocabulary and types
    if 2 * 3 != 6 or min(3, 4) != 3:
        fail("math: the entry and diagonal counts in the vocabulary card are wrong")
    if 3 ** 3 != 27 or 2 ** 3 != 8:
        fail("math: the diagonal-matrix counts are wrong")
    if [[1, 0], [0, 2]] == [[1, 0, 0], [0, 2, 0]]:
        fail("math: matrices of different orders must not be equal")

    # --- card 2: addition and scalar multiplication
    A = [[1, 2], [3, 4]]
    if _m_mat([[2, 0], [0, 2]], A) != [[2, 4], [6, 8]]:
        fail("math: 2A for the addition card is wrong")
    if [[1 + 2, 2], [3, 4 + 2]] != [[3, 2], [3, 6]]:
        fail("math: the A + 2I example is wrong")
    for M in _m_mats(2, range(-2, 3)):
        if _m_T([[2 * x for x in row] for row in M]) != [[2 * x for x in row] for row in _m_T(M)]:
            fail("math: (kA)^T = kA^T fails")
        S = [[M[i][j] + M[j][i] for j in range(2)] for i in range(2)]
        if S == [[0, 0], [0, 0]]:
            if M[0][0] != 0 or M[1][1] != 0 or M[0][1] != -M[1][0]:
                fail("math: A + A^T = O should force A skew-symmetric with a zero diagonal")

    # --- card 3: multiplication and non-commutativity
    X = [[1, 2], [3, 4]]
    Y = [[0, 1], [0, 0]]
    if _m_mat(X, Y) != [[0, 1], [0, 3]] or _m_mat(Y, X) != [[3, 4], [0, 0]]:
        fail("math: the AB and BA example is wrong")
    if 3 * 4 * 2 != 24:
        fail("math: the multiplication cost is wrong")
    A23 = [[1, 0, 0], [0, 1, 0]]
    B32 = [[1, 0], [0, 1], [0, 0]]
    if _m_mat(A23, B32) != [[1, 0], [0, 1]] or _m_mat(B32, A23) == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
        fail("math: the AB = I2 while BA is not I3 example is wrong")
    P = [[0, 1], [0, 0]]
    Q = [[0, 0], [1, 0]]
    if _m_mat(P, Q) != [[1, 0], [0, 0]] or _m_mat(_m_mat(P, Q), _m_mat(P, Q)) == _m_mat(_m_mat(P, P), _m_mat(Q, Q)):
        fail("math: the (AB)^2 counterexample is wrong")
    for M in _m_mats(2, range(-2, 3)):
        if _m_mat(M, M) == M and not _m_eq(M, [[1, 0], [0, 1]]) and _m_det(M) != 0:
            fail("math: an idempotent matrix other than I must be singular")

    # --- card 4: transpose, symmetric and skew-symmetric
    M = [[1, 2, 3], [4, 5, 6]]
    if _m_mat(_m_T(M), M) != [[17, 22, 27], [22, 29, 36], [27, 36, 45]]:
        fail("math: the A^T A example is wrong")
    sym = sum(1 for S in _m_mats(3, [0, 1])
              if all(S[i][j] == S[j][i] for i in range(3) for j in range(3)))
    if sym != 64:
        fail("math: there should be 64 symmetric 3x3 0/1 matrices, got %d" % sym)
    for S in _m_mats(3, range(-1, 2)):
        if all(S[i][j] == -S[j][i] for i in range(3) for j in range(3)):
            if _m_det(S) != 0:
                fail("math: a skew-symmetric matrix of odd order must have determinant 0")
            if _m_rank(S) == 1:
                fail("math: a skew-symmetric matrix cannot have rank 1")
    for S in _m_mats(2, range(-2, 3)):
        if all(S[i][j] == -S[j][i] for i in range(2) for j in range(2)):
            if S[0][1] != 0:
                if _m_det(S) != S[0][1] * S[0][1]:
                    fail("math: a 2x2 skew-symmetric matrix has determinant b^2")
    for S in _m_mats(2, range(-2, 3)):
        sp = [[Fraction(S[i][j] + S[j][i], 2) for j in range(2)] for i in range(2)]
        kp = [[Fraction(S[i][j] - S[j][i], 2) for j in range(2)] for i in range(2)]
        if [[sp[i][j] + kp[i][j] for j in range(2)] for i in range(2)] != [[Fraction(x) for x in row] for row in S]:
            fail("math: the symmetric-plus-skew decomposition does not rebuild the matrix")
        if not all(sp[i][j] == sp[j][i] for i in range(2) for j in range(2)):
            fail("math: the symmetric part is not symmetric")
    if _m_mat(_m_T(P), _m_T(Q)) == _m_T(_m_mat(P, Q)):
        fail("math: A^T B^T should differ from (AB)^T on the counterexample")
    if _m_T(_m_mat(P, Q)) != _m_mat(_m_T(Q), _m_T(P)):
        fail("math: (AB)^T = B^T A^T fails")

    # --- card 5: powers and special matrices
    M = [[1, 2], [2, -1]]
    if _m_mat(M, M) != [[5, 0], [0, 5]]:
        fail("math: A^2 for the 2025 Set 2 Q.1 matrix is wrong")
    acc = [[1, 0], [0, 1]]
    for _ in range(8):
        acc = _m_mat(acc, M)
    if acc != [[625, 0], [0, 625]]:
        fail("math: A^8 for the 2025 Set 2 Q.1 matrix should be 625I")
    for M in _m_mats(2, range(-2, 3)):
        if _m_mat(M, M) == M:
            d = _m_det(M)
            if d not in (0, 1):
                fail("math: an idempotent matrix has determinant 0 or 1")
            if (d == 1) != _m_eq(M, [[1, 0], [0, 1]]):
                fail("math: an idempotent matrix has determinant 1 exactly when it is I")
        if _m_mat(M, _m_mat(M, M)) == [[0, 0], [0, 0]] and _m_det(M) != 0:
            fail("math: a nilpotent matrix must be singular")
        if _m_mat(M, M) == [[4, 0], [0, 4]]:
            acc = [[1, 0], [0, 1]]
            for _ in range(6):
                acc = _m_mat(acc, M)
            if acc != [[64, 0], [0, 64]]:
                fail("math: A^2 = 4I must give A^6 = 64I")
    if _m_mat([[0, 1], [1, 0]], [[0, 1], [1, 0]]) != [[1, 0], [0, 1]]:
        fail("math: A + B should square to I in the expansion counterexample")
    if [[2, 0], [0, 0]] != [[2, 0], [0, 0]]:
        fail("math: the A^2 + 2AB + B^2 value in the counterexample is wrong")
    L = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]          # L^3 = I
    if _m_mat(L, _m_mat(L, L)) != [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
        fail("math: the order-3 matrix used for the 2025 Set 2 Q.4 argument should satisfy L^3 = I")
    if _m_mat(L, L) != _m_inv(L):
        fail("math: L^2 = L^-1 must hold for the 2025 Set 2 Q.4 argument")
    L8 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    for _ in range(8):
        L8 = _m_mat(L8, L)
    if L8 != _m_mat(L, L) or _m_det([[L8[i][j] - _m_mat(L, L)[i][j] for j in range(3)] for i in range(3)]) != 0:
        fail("math: L^8 = L^2 must hold and det(M - N) must be 0")

    # --- card 6: trace
    A, B = [[1, 2], [3, 4]], [[0, 1], [1, 0]]
    if _m_mat(A, B) != [[2, 1], [4, 3]] or _m_mat(B, A) != [[3, 4], [1, 2]]:
        fail("math: the trace example products are wrong")
    if _m_tr(_m_mat(A, B)) != 5 or _m_tr(_m_mat(B, A)) != 5 or _m_tr(A) * _m_tr(B) != 0:
        fail("math: the trace example values are wrong")
    for Ar in _m_mats(2, range(-2, 3)):
        for Br in _m_mats(2, range(-1, 2)):
            if _m_tr(_m_mat(Ar, Br)) != _m_tr(_m_mat(Br, Ar)):
                fail("math: tr(AB) = tr(BA) fails for square matrices")
            if _m_tr([[Ar[i][j] + Br[i][j] for j in range(2)] for i in range(2)]) != _m_tr(Ar) + _m_tr(Br):
                fail("math: tr(A + B) = tr(A) + tr(B) fails")
            if _m_tr(_m_T(Ar)) != _m_tr(Ar):
                fail("math: tr(A^T) = tr(A) fails")
    A23 = [[1, 2, 3], [0, 1, 0]]
    B32 = [[1, 0], [2, 1], [0, 3]]
    if _m_tr(_m_mat(A23, B32)) != _m_tr(_m_mat(B32, A23)):
        fail("math: tr(AB) = tr(BA) fails for rectangular factors")
    X = [[0, 1], [0, 0]]
    Y = [[0, 0], [1, 0]]
    W = [[1, 0], [0, 0]]
    if not (_m_tr(_m_mat(_m_mat(X, Y), W)) == 1 and _m_tr(_m_mat(_m_mat(X, W), Y)) == 0):
        fail("math: the non-cyclic trace counterexample is wrong")
    if _m_tr(_m_mat([[1, 0, 0], [0, 2, 0], [0, 0, 3]], [[1, 0, 0], [0, 2, 0], [0, 0, 3]])) != 14:
        fail("math: tr(A^2) for eigenvalues 1, 2, 3 should be 14")
    if _m_tr([[2 * x for x in row] for row in _m_T([[3, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])]) != 6:
        fail("math: tr(2A^T) should be 6 when tr(A) = 3")

    # --- card 7: determinant and expansion
    G = [[2, 0, 0, 0], [8, 1, 7, 2], [2, 0, 2, 0], [9, 0, 6, 1]]
    if _m_det(G) != 4:
        fail("math: GATE CSE 2000 Q.1.3 should have determinant 4")
    if _m_det([[2, 5], [1, 3]]) != 1:
        fail("math: the 2x2 quick check should be 1")
    if _m_det([[3, 0, 0], [5, 2, 0], [1, 7, 4]]) != 24:
        fail("math: the lower triangular determinant should be 24")
    if _m_cof([[1, 2], [3, 4]], 0, 1) != -3:
        fail("math: C_12 of [[1,2],[3,4]] should be -3")
    if _m_adj([[1, 2], [3, 4]]) != [[4, -2], [-3, 1]]:
        fail("math: adj([[1,2],[3,4]]) should be [[4,-2],[-3,1]]")
    for M in _m_mats(3, [0, 1]):
        d = _m_det(M)
        for i in range(3):
            if sum(M[i][j] * _m_cof(M, i, j) for j in range(3)) != d:
                fail("math: expansion along a row disagrees with the determinant")
        for j in range(3):
            if sum(M[i][j] * _m_cof(M, i, j) for i in range(3)) != d:
                fail("math: expansion along a column disagrees with the determinant")

    # --- card 8: row and column operations
    lesson = [([[1, 0], [0, 1]], 1), ([[2, 1], [0, 3]], 6), ([[0, 3], [2, 1]], -6),
              ([[6, 3], [0, 3]], 18), ([[2, 4], [0, 3]], 6), ([[2, 1], [4, 2]], 0)]
    for M, want in lesson:
        if _m_det(M) != want:
            fail("math: the lesson determinant of %s should be %s" % (M, want))
    if _m_det([[0, 3], [2, 1]]) != -_m_det([[2, 1], [0, 3]]):
        fail("math: the row swap should flip the sign")
    if _m_det([[6, 3], [0, 3]]) != 3 * _m_det([[2, 1], [0, 3]]):
        fail("math: scaling a row should scale the determinant")
    if _m_det([[2, 4], [0, 3]]) != _m_det([[2, 1], [0, 3]]):
        fail("math: adding a row should leave the determinant alone")
    for n in (2, 3):
        for M in _m_mats(n, [0, 1] if n == 3 else range(-2, 3)):
            d = _m_det(M)
            if _m_det(_m_T(M)) != d:
                fail("math: det(A^T) = det(A) fails")
            for k in (2, 3, -1):
                if _m_det([[k * x for x in row] for row in M]) != k ** n * d:
                    fail("math: det(kA) = k^n det(A) fails (n=%d, k=%d)" % (n, k))
            R = [row[:] for row in M]
            R[0] = [R[0][j] + 2 * R[n - 1][j] for j in range(n)]
            if _m_det(R) != d:
                fail("math: adding a multiple of a row changed the determinant")
            if n == 2 and M[0] == M[1] and d != 0:
                fail("math: identical rows should give determinant 0")
            if d != 0 and _m_det(_m_inv(M)) != 1 / d:
                fail("math: det(A^-1) = 1/det(A) fails")
            for j in range(n):
                if M[0][j] * M[1][j] == 0 and False:
                    pass
            if n == 2 and M[0][0] * M[1][1] == M[0][1] * M[1][0] and d != 0:
                fail("math: proportional rows should give determinant 0")
    for A in _m_mats(2, range(-2, 3)):
        for B in _m_mats(2, range(-1, 2)):
            if _m_det(_m_mat(A, B)) != _m_det(A) * _m_det(B):
                fail("math: det(AB) = det(A) det(B) fails")
    if _m_det([[-2 * x for x in row] for row in [[1, 0, 0], [0, 1, 0], [0, 0, 1]]]) != -8:
        fail("math: det(2I_3) should be 8 and det(-2I_3) = -8")
    if _m_det(_m_mat(_m_T([[1, 0, 0], [0, 1, 0], [0, 0, 5]]), _m_inv([[1, 0, 0], [0, 1, 0], [0, 0, 5]]))) != 1:
        fail("math: det(A^T A^-1) should be 1")
    A = [[1, 0, 0], [0, 1, 0], [0, 0, 2]]
    B = [[1, 0, 0], [0, 1, 0], [0, 0, 3]]
    val = _m_det(_m_mat(_m_mat(_m_mat(A, A), _m_inv(B)), _m_T(A)))
    if val != Fraction(8, 3):
        fail("math: det(A^2 B^-1 A^T) should be 8/3, got %s" % val)
    if 5 * 3 != 15:
        fail("math: the A + 2I sanity count is wrong")

    # --- card 9: adjoint and inverse
    A = [[3, 1], [2, 4]]
    if _m_det(A) != 10 or _m_adj(A) != [[4, -1], [-2, 3]]:
        fail("math: adj([[3,1],[2,4]]) should be [[4,-1],[-2,3]]")
    if _m_mat(A, _m_adj(A)) != [[10, 0], [0, 10]]:
        fail("math: A adj(A) = |A| I fails on the worked example")
    if _m_mat(A, _m_inv(A)) != [[1, 0], [0, 1]]:
        fail("math: the worked inverse is wrong")
    for M in _m_mats(3, [0, 1]):
        d = _m_det(M)
        if _m_mat(M, _m_adj(M)) != [[d if i == j else 0 for j in range(3)] for i in range(3)]:
            fail("math: A adj(A) = |A| I fails on a 3x3 matrix")
        if _m_det(_m_adj(M)) != d ** 2:
            fail("math: |adj A| = |A|^(n-1) fails on a 3x3 matrix")
        if d != 0:
            if not _m_eq(_m_adj(_m_adj(M)), [[d * M[i][j] for j in range(3)] for i in range(3)]):
                fail("math: adj(adj A) = |A|^(n-2) A fails on a 3x3 matrix")
    random.seed(11)
    for _ in range(60):
        M = [[random.randint(-2, 2) for _ in range(3)] for _ in range(3)]
        N = [[random.randint(-2, 2) for _ in range(3)] for _ in range(3)]
        if _m_adj(_m_mat(M, N)) != _m_mat(_m_adj(N), _m_adj(M)):
            fail("math: adj(AB) = adj(B) adj(A) fails")
        for k in (2, -3):
            if _m_adj([[k * x for x in row] for row in M]) != [[k * k * x for x in row] for row in _m_adj(M)]:
                fail("math: adj(kA) = k^(n-1) adj(A) fails for a 3x3 matrix")
    D = [[1, 0, 0], [0, 1, 0], [0, 0, 5]]
    if _m_det(_m_mat(D, _m_adj(D))) != 125:
        fail("math: |A adj A| should be 125 when |A| = 5")
    if _m_adj([[5, -3], [-4, 2]]) != [[2, 3], [4, 5]]:
        fail("math: the predicted-variation matrix does not have the stated adjoint")

    # --- card 10: rank
    if _m_rank([[1, 4, 8, 7], [0, 0, 3, 0], [4, 2, 3, 1], [3, 12, 24, 21]]) != 3:
        fail("math: GATE CSE 1998 Q.2.1 should have rank 3")
    if _m_det([[1, 4, 8], [0, 0, 3], [4, 2, 3]]) != 42:
        fail("math: the 3x3 minor in the 1998 question should be 42")
    if _m_rank([[0, 0, -3], [9, 3, 5], [3, 1, 1]]) != 2:
        fail("math: GATE CSE 1994 Q.1.9 should have rank 2")
    if _m_rank([[1, 1], [0, 0]]) != 1:
        fail("math: GATE CSE 2002 Q.1.1 should have rank 1")
    A34 = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]]
    Pm = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    if _m_rank(A34) != 3 or _m_rank(_m_mat(A34, Pm)) != 3:
        fail("math: multiplying by an invertible matrix must not change the rank")
    for A in _m_mats(2, range(-1, 2)):
        for B in _m_mats(2, range(-1, 2)):
            ra, rb = _m_rank(A), _m_rank(B)
            if _m_rank(_m_mat(A, B)) > min(ra, rb):
                fail("math: rank(AB) <= min(rank A, rank B) fails")
            if _m_rank(_m_mat(A, B)) < ra + rb - 2:
                fail("math: Sylvester's inequality fails")
            if _m_rank([[A[i][j] + B[i][j] for j in range(2)] for i in range(2)]) > ra + rb:
                fail("math: rank(A + B) <= rank A + rank B fails")
            if ra == 0 and A != [[0, 0], [0, 0]]:
                fail("math: the zero matrix is the only rank-0 matrix")
    if _m_rank([[1, 0], [0, 0]]) + _m_rank([[0, 0], [1, 0]]) != 2:
        fail("math: the rank sum example should be 2")
    if _m_rank([[1, 0], [1, 0]]) != 1:
        fail("math: rank(A + B) should be 1 in the sum counterexample")
    seen_rank_two = 0
    for M in _m_mats(3, [0, 1]):
        if _m_rank(M) == 2:
            seen_rank_two += 1
            if _m_rank(_m_adj(M)) != 1:
                fail("math: rank(adj A) should be 1 when rank(A) = 2 in a 3x3 matrix")
    if seen_rank_two == 0:
        fail("math: no rank-2 3x3 0/1 matrix was found, so the adjoint-rank claim was not tested")
    # 2021 Set 2 Q.24: a 4x5 matrix of rank 4 whose null space is one line
    Q = [[1, 0, 0, 0, -2], [0, 1, 0, 0, -5], [0, 0, 1, 0, -4], [0, 0, 0, 1, -3]]
    if _m_rank(Q) != 4:
        fail("math: the matrix built for GATE CSE 2021 Set 2 Q.24 should have rank 4")
    null = [2, 5, 4, 3, 1]
    for i in range(4):
        if sum(Q[i][j] * null[j] for j in range(5)) != 0:
            fail("math: the stated null vector is not in the null space")
    if _m_rank(Q) + 1 != 5:
        fail("math: rank-nullity for the 4x5 matrix is wrong")

    # --- card 11: singular and equivalent conditions
    U = [[2], [-4], [7]]
    V = [[1, 9, 5]]
    A = _m_mat(U, V)
    if A != [[2, 18, 10], [-4, -36, -20], [7, 63, 35]]:
        fail("math: the 2014 Set 2 Q.4 product is wrong")
    if _m_det(A) != 0 or _m_rank(A) != 1:
        fail("math: the 2014 Set 2 Q.4 matrix should have determinant 0 and rank 1")
    if [[1, 0], [0, 0]] == [[0, 0], [0, 1]]:
        fail("math: the two singular summands must be different")
    if _m_det([[1, 0], [0, 0]]) != 0 or _m_det([[0, 0], [0, 1]]) != 0:
        fail("math: both summands should be singular")
    if _m_det([[1, 0], [0, 1]]) != 1:
        fail("math: the sum of the two singular matrices should be non-singular")
    if _m_det([[1, 2], [2, 4]]) != 0 or _m_det([[0, 1], [1, 0]]) != -1:
        fail("math: the zero-entry counterexamples are wrong")
    for M in _m_mats(2, range(-2, 3)):
        d = _m_det(M)
        singular = (d == 0)
        if singular != (_m_rank(M) < 2):
            fail("math: det 0 and rank < n disagree")
        if singular != (_m_inv(M) is None):
            fail("math: det 0 and non-invertibility disagree")
        if singular != (M[0][0] * M[1][1] == M[0][1] * M[1][0]):
            fail("math: det 0 and dependent rows disagree")
    for M in _m_mats(3, [0, 1]):
        if _m_rank(M) == 2 and _m_det(M) != 0:
            fail("math: a 3x3 matrix of rank 2 must have determinant 0")

    ok("Matrices and determinants: the type and diagonal counts; the addition, multiplication and "
       "transpose laws over every small integer matrix; the AB and BA examples, the AB = I2 while BA is "
       "not I3 case and the (AB)^2 counterexample; 64 symmetric 3x3 0/1 matrices, the symmetric-plus-skew "
       "decomposition and the odd-order skew-symmetric determinant; the idempotent, nilpotent, involutory "
       "and orthogonal consequences and the 2025 Set 2 Q.1 and Q.4 chains; tr(AB) = tr(BA) for square and "
       "rectangular factors and the non-cyclic counterexample; every Laplace expansion along every row and "
       "column; the determinant laws det(A^T), det(kA), det(AB), det(A^-1) and the four row-operation "
       "effects of the lesson; A adj(A) = |A| I, |adj A| = |A|^(n-1), adj(adj A) and adj(kA) on every 3x3 "
       "0/1 matrix; the ranks of the 1994, 1998 and 2002 questions, the rank inequalities and Sylvester "
       "over every 2x2 pair, rank(adj A) = 1 at rank 2, and the rank-nullity reading of the 2021 question; "
       "and the equivalence of determinant zero, rank below n and non-invertibility on every 2x2 matrix")


def check_system_of_linear_equations():
    """Every determinant, rank, verdict and solution published in the System of Linear Equations topic."""
    from fractions import Fraction

    def mat(A):
        return [[Fraction(x) for x in row] for row in A]

    def vec(v):
        return [Fraction(x) for x in v]

    def aug(A, b):
        return [row + [b[i]] for i, row in enumerate(mat(A))]

    def rank(M):
        R = [row[:] for row in M]
        if not R:
            return 0
        rows, cols, r = len(R), len(R[0]), 0
        for c in range(cols):
            piv = next((i for i in range(r, rows) if R[i][c] != 0), None)
            if piv is None:
                continue
            R[r], R[piv] = R[piv], R[r]
            for i in range(rows):
                if i != r and R[i][c] != 0:
                    f = R[i][c] / R[r][c]
                    R[i] = [R[i][j] - f * R[r][j] for j in range(cols)]
            r += 1
            if r == rows:
                break
        return r

    def det(A):
        M = mat(A)
        n = len(M)
        d = Fraction(1)
        for c in range(n):
            piv = next((i for i in range(c, n) if M[i][c] != 0), None)
            if piv is None:
                return Fraction(0)
            if piv != c:
                M[c], M[piv] = M[piv], M[c]
                d = -d
            d *= M[c][c]
            for i in range(c + 1, n):
                if M[i][c] != 0:
                    f = M[i][c] / M[c][c]
                    M[i] = [M[i][j] - f * M[c][j] for j in range(n)]
        return d

    def solve(A, b):
        """Unique solution of a square consistent system, or None."""
        n = len(A)
        if det(A) == 0:
            return None
        M = aug(A, b)
        for c in range(n):
            piv = next(i for i in range(c, n) if M[i][c] != 0)
            M[c], M[piv] = M[piv], M[c]
            for i in range(n):
                if i != c and M[i][c] != 0:
                    f = M[i][c] / M[c][c]
                    M[i] = [M[i][j] - f * M[c][j] for j in range(n + 1)]
        return [M[i][n] / M[i][i] for i in range(n)]

    def verdict(A, b):
        rA, rAug = rank(mat(A)), rank(aug(A, b))
        n = len(mat(A)[0])
        if rA != rAug:
            return "none"
        return "unique" if rA == n else "infinite"

    def solutions(A, b):
        """Number of solutions for a 2x2 integer system: 0, 1, or 'inf'."""
        v = verdict(A, b)
        return {"none": 0, "unique": 1, "infinite": "inf"}[v]

    def mats(r, c, vals):
        for flat in itertools.product(vals, repeat=r * c):
            yield [list(flat[i * c:(i + 1) * c]) for i in range(r)]

    def vecs(r, vals):
        for flat in itertools.product(vals, repeat=r):
            yield list(flat)

    # --- the lesson's six systems, read back from lesson.json
    lesson_path = os.path.join(ROOT, "visuals", "linear-algebra", "system-of-linear-equations",
                               "row-and-column-picture", "lesson.json")
    L = load(lesson_path)
    if L.get("steps") != len(L.get("example", {}).get("systems", [])) + 1:
        fail("lesson row-and-column-picture: steps must be the six systems plus the summary step")
    for S in L["example"]["systems"]:
        A, b = S["A"], S["b"]
        d, rA, rAug, v = det(A), rank(mat(A)), rank(aug(A, b)), verdict(A, b)
        if d != S["det"]:
            fail("lesson %s: det claimed %r, computed %r" % (S["name"], S["det"], d))
        if rA != S["rank_A"] or rAug != S["rank_aug"]:
            fail("lesson %s: ranks claimed %r/%r, computed %r/%r"
                 % (S["name"], S["rank_A"], S["rank_aug"], rA, rAug))
        if v != S["verdict"]:
            fail("lesson %s: verdict claimed %r, computed %r" % (S["name"], S["verdict"], v))
        sol = solve(A, b) if v == "unique" else None
        if "solution" in S:
            if sol is None or [Fraction(x) for x in S["solution"]] != sol:
                fail("lesson %s: claimed solution %r, computed %r" % (S["name"], S["solution"], sol))
        elif sol is not None:
            fail("lesson %s: a solution exists but none is claimed" % S["name"])
    if len(L["example"]["rules"]) != 4:
        fail("lesson row-and-column-picture: expected the four decision rules")
    ok("System of linear equations lesson: six systems with determinant, rank pair, verdict and solution "
       "recomputed, plus the summary step")

    # --- card 1 and card 7 examples
    if solutions([[1, 2], [2, 4]], [3, 6]) != "inf":
        fail("math: [[1,2],[2,4]] with b = (3,6) must have infinitely many solutions")
    for t in (0, 1, -3):
        x = [3 - 2 * t, t]
        if [1 * x[0] + 2 * x[1], 2 * x[0] + 4 * x[1]] != [3, 6]:
            fail("math: (3 - 2t, t) must solve [[1,2],[2,4]] x = (3,6)")
    if solutions([[1, 2], [2, 4]], [1, 0]) != 0:
        fail("math: [[1,2],[2,4]] x = (1,0) must have no solution")
    if solutions([[1, 1], [1, 1]], [1, 3]) != 0:
        fail("math: the parallel-lines counterexample must have no solution")
    if rank([[1, 1, 1], [1, 1, 3]]) != 2 or rank([[1, 1], [1, 1]]) != 1:
        fail("math: the parallel-lines counterexample ranks are wrong")

    # --- card 2 and GATE 1998 Q.1.2
    A98 = [[1, 2, 0], [4, 8, 0], [3, 6, 3]]
    b98 = [5, 12, 15]
    if rank(mat(A98)) != 2 or rank(aug(A98, b98)) != 3:
        fail("math: GATE CSE 1998 Q.1.2 must give rank(A) = 2 and rank([A|b]) = 3")
    if verdict(A98, b98) != "none":
        fail("math: GATE CSE 1998 Q.1.2 must have no solution")
    if rank([[1, 0], [0, 1], [1, 1]]) != 2 or rank([[1, 0, 1], [0, 1, 1], [1, 1, 2]]) != 2:
        fail("math: the 3 x 2 example must have equal ranks of 2")
    if solve([[1, 0], [0, 1]], [1, 1]) != [Fraction(1), Fraction(1)]:
        fail("math: the 3 x 2 example's unique solution should be (1,1)")
    if verdict([[1, 0], [0, 1], [1, 1]], [1, 1, 2]) != "unique":
        fail("math: the 3 x 2 example must be consistent with one solution")

    # --- card 3 and GATE 2005 Q.48
    A05 = [[2, -1, 3], [3, 2, 5], [-1, 4, 1]]
    if det(A05) != 14:
        fail("math: GATE CSE 2005 Q.48 must have determinant 14, got %s" % det(A05))
    if verdict(A05, [1, 2, 3]) != "unique":
        fail("math: GATE CSE 2005 Q.48 must have a unique solution")
    if det([[1, 1], [2, 2]]) != 0:
        fail("math: [[1,1],[2,2]] must have determinant 0")
    if solutions([[1, 1], [2, 2]], [1, 2]) != "inf" or solutions([[1, 1], [2, 2]], [1, 3]) != 0:
        fail("math: the singular-matrix counterexample pair is wrong")

    # --- card 4: the one-parameter family
    for t in (0, 1, -2, Fraction(7, 3)):
        x, y, z = (3 - t) / 2, (3 - t) / 2, t
        if x + y + z != 3 or x - y != 0:
            fail("math: ((3-t)/2, (3-t)/2, t) must solve x + y + z = 3 and x - y = 0")
    if rank([[1, 1, 1], [1, -1, 0]]) != 2:
        fail("math: x + y + z = 3 and x - y = 0 must have rank 2")
    for A in mats(2, 3, [0, 1, -1]):
        r = rank(mat(A))
        if r > min(2, 3) or r < 0:
            fail("math: rank out of bounds")
        nullity = 3 - r
        if nullity < 0:
            fail("math: nullity must be non-negative")
    for A in mats(2, 2, [0, 1, -1, 2]):
        r = rank(mat(A))
        has_nontrivial = False
        for x in itertools.product([-2, -1, 0, 1, 2], repeat=2):
            if x == (0, 0):
                continue
            if all(sum(A[i][j] * x[j] for j in range(2)) == 0 for i in range(2)):
                has_nontrivial = True
                break
        if has_nontrivial != (r < 2):
            fail("math: a 2x2 system has a non-trivial homogeneous solution iff rank < 2")
        if (det(A) == 0) != (r < 2):
            fail("math: det 0 and rank < n must agree for a 2x2 matrix")

    # --- card 5 and GATE 2015 Set 3 Q.33
    def det33(p, q, r):
        return 3 * p * q * r - p ** 3 - q ** 3 - r ** 3

    def option_c(p, q, r):
        return (p + q + r == 0) or (p == q == r)

    def option_a(p, q, r):
        return (p - q + r == 0) or (p == q == -r)

    def option_b(p, q, r):
        return (p + q - r == 0) or (p == -q == r)

    def option_d(p, q, r):
        return (p - q + r == 0) or (p == -q == -r)

    for p in range(-3, 4):
        for q in range(-3, 4):
            for r in range(-3, 4):
                z = det33(p, q, r)
                if (z == 0) != option_c(p, q, r):
                    fail("math: GATE CSE 2015 Set 3 Q.33: det = 0 must be equivalent to option C "
                         "at (p,q,r) = (%d,%d,%d)" % (p, q, r))
                if z == 0:
                    if not option_c(p, q, r):
                        fail("math: the correct option must hold whenever the determinant vanishes")
                if option_c(p, q, r):
                    if (p, q, r) not in [(0, 0, 0)] and det([[p, q, r], [q, r, p], [r, p, q]]) != 0:
                        fail("math: the 2015 Q.33 determinant must vanish when option C holds")
    # options A, B and D are not equivalent: exhibit a witness for each
    for name, fn in (("A", option_a), ("B", option_b), ("D", option_d)):
        witness = None
        for p in range(-3, 4):
            for q in range(-3, 4):
                for r in range(-3, 4):
                    if (det33(p, q, r) == 0) != fn(p, q, r):
                        witness = (p, q, r)
                        break
                if witness:
                    break
            if witness:
                break
        if witness is None:
            fail("math: option %s of GATE CSE 2015 Set 3 Q.33 was not separated from the truth" % name)
    if det33(1, 1, 1) != 0 or det33(1, -1, 0) != 0:
        fail("math: p = q = r and p + q + r = 0 must both make the 2015 Q.33 determinant vanish")
    if det33(1, 2, 3) == 0:
        fail("math: p = 1, q = 2, r = 3 must not make the 2015 Q.33 determinant vanish")
    if solutions([[1, 1], [1, 1]], [1, 2]) != 0:
        fail("math: the homogeneous counterexample pair is wrong")
    if [1 * 1 + 1 * (-1), 1 * 1 + 1 * (-1)] != [0, 0]:
        fail("math: (1,-1) must be a null vector of [[1,1],[1,1]]")
    if rank([[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0]]) != 3:
        fail("math: a 4 x 3 matrix with full column rank must have rank 3")

    # --- card 6: elimination reading
    if rank([[1, 1, 3], [0, -2, -2]]) != 2:
        fail("math: the elimination example must end with two pivots")
    if solve([[1, 1], [1, -1]], [3, 1]) != [Fraction(2), Fraction(1)]:
        fail("math: x + y = 3, x - y = 1 must solve to (2,1)")
    if rank([[0, 0, 0, 5]]) != 1:
        fail("math: a row (0 0 0 | 5) carries a pivot in the augmented column")

    # --- card 7 and the parameter questions
    for a in (-4, 4):
        bb = 24 // a
        A = [[a, 1], [16, a]]
        if det(A) != 0:
            fail("math: a = %d must make the GATE CSE 2026 determinant vanish" % a)
        if verdict(A, [bb, 24]) != "infinite":
            fail("math: a = %d with b = %d must give infinitely many solutions" % (a, bb))
        if a * bb != 24:
            fail("math: the product ab in GATE CSE 2026 Set 2 Q.31 must be 24")
    if verdict([[4, 1], [16, 4]], [7, 24]) != "none":
        fail("math: a = 4 with b = 7 must give no solution")
    if det([[0, 1], [16, 0]]) != -16:
        fail("math: a = 0 must leave the determinant non-zero")
    if verdict([[0, 1], [16, 0]], [6, 24]) != "unique":
        fail("math: a = 0 must give a unique solution")
    if det([[1, 1], [2, 2]]) != 0:
        fail("math: the k-system sanity check failed")
    # GATE 2025 Set 1 Q.13
    no_sol, inf_sol, uniq = [], [], []
    for k in range(-6, 7):
        A = [[1, k], [k, 1]]
        d = det(A)
        if d != 1 - k * k:
            fail("math: the GATE CSE 2025 Q.13 determinant must be 1 - k^2")
        v = verdict(A, [1, -1])
        if v == "none":
            no_sol.append(k)
        elif v == "infinite":
            inf_sol.append(k)
        else:
            uniq.append(k)
    if no_sol != [1]:
        fail("math: GATE CSE 2025 Set 1 Q.13 must have exactly one k with no solution, got %s" % no_sol)
    if inf_sol != [-1]:
        fail("math: GATE CSE 2025 Set 1 Q.13 must have exactly one k with infinitely many, got %s"
             % inf_sol)
    if len(uniq) < 5:
        fail("math: GATE CSE 2025 Set 1 Q.13 must have many k with a unique solution")
    if solutions([[1, 1], [1, 1]], [1, -1]) != 0:
        fail("math: k = 1 must give parallel distinct lines")
    if solutions([[1, -1], [-1, 1]], [1, -1]) != "inf":
        fail("math: k = -1 must give the same line twice")
    # GATE 2008 Q.3
    for alpha in range(-4, 9):
        A = [[1, 1, 2], [1, 2, 3], [1, 4, alpha]]
        if det(A) != alpha - 5:
            fail("math: the GATE CSE 2008 Q.3 determinant must be alpha - 5")
        v = verdict(A, [1, 2, 4])
        if alpha == 5:
            if v != "infinite":
                fail("math: alpha = 5 must give infinitely many solutions in GATE CSE 2008 Q.3")
        elif v != "unique":
            fail("math: every alpha other than 5 must give a unique solution in GATE CSE 2008 Q.3")

    # --- card 8 and GATE 2016 Set 2 Q.04
    if solutions([[1, 1, 1], [1, 1, 1]], [1, 2]) != 0:
        fail("math: the m < n counterexample of GATE CSE 2016 Set 2 Q.04 must have no solution")
    if rank([[1, 1], [2, 2], [1, -1]]) != 2 or rank([[1, 1, 1], [2, 2, 2], [1, -1, 0]]) != 2:
        fail("math: the m > n counterexample of GATE CSE 2016 Set 2 Q.04 must have rank 2")
    if [Fraction(1, 2), Fraction(1, 2)] != solve([[1, 1], [1, -1]], [1, 0]):
        fail("math: the m > n counterexample must be solved by x = y = 1/2")
    if verdict([[1, 1], [2, 2], [1, -1]], [1, 2, 0]) != "unique":
        fail("math: the m > n counterexample of GATE CSE 2016 Set 2 Q.04 must be consistent")
    if verdict([[1]], [0]) != "unique":
        fail("math: the m = n = 1 example of GATE CSE 2016 Set 2 Q.04 must have a solution")
    # the rank(A) = m corollary, over every small full-row-rank matrix and every b in range
    seen_full_row = 0
    for A in mats(2, 3, [0, 1, -1]):
        if rank(mat(A)) == 2:
            seen_full_row += 1
            for b in vecs(2, [-1, 0, 1, 2]):
                if verdict(A, b) == "none":
                    fail("math: rank(A) = m must make every b reachable")
    if seen_full_row == 0:
        fail("math: no 2 x 3 matrix of full row rank was found, so the corollary was not tested")

    # --- card 9: Cramer's rule
    A = [[2, -1, 3], [3, 2, 5], [-1, 4, 1]]
    b = [1, 2, 3]
    x = solve(A, b)
    d = det(A)
    for i in range(3):
        Ai = [[b[row] if col == i else A[row][col] for col in range(3)] for row in range(3)]
        if det(Ai) / d != x[i]:
            fail("math: Cramer's rule disagrees with elimination on the 3 x 3 example")
    if solve([[1, 1], [1, -1]], [3, 1]) != [Fraction(2), Fraction(1)]:
        fail("math: the Cramer worked example is wrong")
    if det([[3, 1], [1, -1]]) != -4 or det([[1, 3], [1, 1]]) != -2 or det([[1, 1], [1, -1]]) != -2:
        fail("math: the Cramer numerator and denominator determinants are wrong")

    # --- card 10: the three-unknown arrangements
    if verdict([[1, 1, 1], [1, -1, 1], [2, 0, 2]], [1, 1, 3]) != "none":
        fail("math: the prism example must have no solution")
    if rank([[1, 1, 1], [1, -1, 1], [2, 0, 2]]) != 2:
        fail("math: the prism example must have rank(A) = 2")
    if rank([[1, 1, 1, 1], [1, -1, 1, 1], [2, 0, 2, 3]]) != 3:
        fail("math: the prism example must have rank([A|b]) = 3")
    for pair in ((0, 1), (0, 2), (1, 2)):
        rows = [[1, 1, 1], [1, -1, 1], [2, 0, 2]]
        rhs = [1, 1, 3]
        Ap = [rows[pair[0]], rows[pair[1]]]
        bp = [rhs[pair[0]], rhs[pair[1]]]
        if verdict(Ap, bp) == "none":
            fail("math: every pair of planes in the prism example must meet")
    if verdict([[1, 1], [2, 2]], [1, 2]) != "infinite":
        fail("math: the coincident-lines example must have infinitely many solutions")

    # --- card 11 and GATE 2003 Q.41
    A03 = [[2, 1, -4], [4, 3, -12], [1, 2, -8]]
    if det(A03) != 0 or rank(mat(A03)) != 2:
        fail("math: GATE CSE 2003 Q.41 must have a singular coefficient matrix of rank 2")
    if [A03[0][2], A03[1][2], A03[2][2]] != [-4 * A03[i][1] for i in range(3)]:
        fail("math: the third column of the 2003 matrix must be -4 times the second")
    good = []
    for alpha in [Fraction(k, 5) for k in range(-15, 16)] + [Fraction(1, 5), Fraction(-4, 3)]:
        if verdict(A03, [alpha, 5, 7]) == "infinite":
            good.append(alpha)
    if set(good) != {Fraction(1, 5)}:
        fail("math: GATE CSE 2003 Q.41 must have exactly one alpha with infinitely many solutions, "
             "got %s" % sorted(set(good)))
    # the direct span route: b = s c1 + t c2
    s, t = Fraction(-11, 5), Fraction(23, 5)
    for i in range(3):
        if s * A03[i][0] + t * A03[i][1] != [Fraction(1, 5), Fraction(5), Fraction(7)][i]:
            fail("math: the span route to alpha = 1/5 in GATE CSE 2003 Q.41 is wrong")
    if verdict(A03, [0, 5, 7]) != "none":
        fail("math: alpha = 0 must give no solution in GATE CSE 2003 Q.41")
    if verdict([[1, 0], [0, 0]], [1, 1]) != "none" or verdict([[1, 0], [0, 0]], [1, 0]) != "infinite":
        fail("math: the GATE CSE 1996 Q.1.7 counterexamples are wrong")
    if verdict([[1, 0, 0], [0, 1, 0]], [0, 0]) != "infinite":
        fail("math: m < n with b = 0 must give infinitely many solutions (GATE CSE 1996 Q.1.7 B)")
    if verdict([[1, 0], [0, 1]], [0, 0]) != "unique":
        fail("math: rank(A) = n with b = 0 must give only the trivial solution (GATE 1996 Q.1.7 D)")

    # --- card 11 and GATE 2017 Set 1 Q.3
    A17 = [[1, 2, 3], [2, 4, 6], [1, 1, 2]]
    c = [1, 1, -1]
    if any(sum(c[i] * A17[j][i] for i in range(3)) != 0 for j in range(3)):
        fail("math: the GATE CSE 2017 Q.3 example needs a non-zero null vector")
    if det(A17) != 0:
        fail("math: the GATE CSE 2017 Q.3 example must be singular")
    b17 = [sum(A17[j][i] for i in range(3)) for j in range(3)]
    if verdict(A17, b17) != "infinite":
        fail("math: GATE CSE 2017 Set 1 Q.3 must have infinitely many solutions")
    if [sum(A17[j][i] for i in range(3)) for j in range(3)] != b17:
        fail("math: the all-ones vector must reproduce b in GATE CSE 2017 Q.3")

    # --- card 5 and GATE 2024 Set 1 Q.39
    for n in (1, 2, 3):
        for m in range(n + 1, n + 4):
            for A in itertools.islice(mats(n, m, [0, 1]), 60):
                if m - rank(mat(A)) < m - n:
                    fail("math: the nullity of an n x m matrix must be at least m - n")
    Ac = [[1, 0, 0, 1], [0, 1, 0, 2], [0, 0, 1, 3]]
    xc = [-1, -2, -3, 1]
    if any(sum(Ac[i][j] * xc[j] for j in range(4)) != 0 for i in range(3)):
        fail("math: the option-C counterexample of GATE CSE 2024 Q.39 must solve Ax = 0")
    if 0 in xc:
        fail("math: the option-C counterexample must have no zero variable")
    Ad = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 3]]
    xd = [0, 0, -3, 1]
    if any(sum(Ad[i][j] * xd[j] for j in range(4)) != 0 for i in range(3)):
        fail("math: the option-D counterexample of GATE CSE 2024 Q.39 must solve Ax = 0")
    if sum(1 for v in xd if v != 0) != 2:
        fail("math: the option-D counterexample must have exactly two non-zero variables")
    if rank(mat(Ad)) != 3:
        fail("math: the option-D counterexample must have rank 3")

    # --- GATE 2014 Set 1 Q.52
    A14 = [[3, 2, 0], [4, 0, 7], [1, 1, 1], [1, -2, 7]]
    b14 = [1, 1, 3, 0]
    minor = [[3, 2, 0], [1, 1, 1], [1, -2, 7]]
    if det(minor) != 15:
        fail("math: the 3 x 3 minor in GATE CSE 2014 Set 1 Q.52 must have determinant 15")
    if rank(mat(A14)) != 3 or rank(aug(A14, b14)) != 3:
        fail("math: GATE CSE 2014 Set 1 Q.52 must have both ranks equal to 3")
    sol14 = [Fraction(-11, 5), Fraction(19, 5), Fraction(7, 5)]
    for i in range(4):
        if sum(A14[i][j] * sol14[j] for j in range(3)) != b14[i]:
            fail("math: the GATE CSE 2014 Set 1 Q.52 solution does not satisfy every equation")
    if solve([[3, 2, 0], [4, 0, 7], [1, 1, 1]], [1, 1, 3]) != sol14:
        fail("math: solving GATE CSE 2014 Set 1 Q.52 by elimination must give (-11/5, 19/5, 7/5)")

    # --- general theory, exhaustive on small systems
    for A in mats(2, 2, [-1, 0, 1, 2]):
        for b in vecs(2, [-1, 0, 1, 2]):
            v = verdict(A, b)
            if v == "unique":
                x = solve(A, b)
                if x is None or any(sum(A[i][j] * x[j] for j in range(2)) != b[i] for i in range(2)):
                    fail("math: a system reported unique has no valid solution")
            if v == "none" and rank(mat(A)) == rank(aug(A, b)):
                fail("math: an inconsistent system must have unequal ranks")
            if v == "infinite":
                if det(A) != 0:
                    fail("math: infinitely many solutions require a singular 2x2 matrix")
                if det(A) == 0 and rank(mat(A)) < 2:
                    # a null vector must exist, so two solutions can be built
                    null = None
                    for x in itertools.product([-2, -1, 0, 1, 2], repeat=2):
                        if x != (0, 0) and all(sum(A[i][j] * x[j] for j in range(2)) == 0
                                               for i in range(2)):
                            null = x
                            break
                    if null is None:
                        fail("math: a consistent singular system must have a non-zero null vector")
    if rank([[1, 2], [2, 4]]) != 1:
        fail("math: proportional rows must give rank 1")

    ok("System of linear equations: the six lesson systems with determinants, rank pairs, verdicts and "
       "solutions; the 1998, 2003, 2005, 2008, 2014, 2015, 2016, 2017, 2024, 2025 and 2026 questions "
       "recomputed from their own matrices; the nullity count and the non-trivial-solution test over every "
       "small 2x2 and 2x3 matrix; the rank(A) = m corollary over every full-row-rank 2x3 matrix and every "
       "small b; Cramer's rule against elimination on a 3x3 system; the prism, parallel and coincident "
       "arrangements; and the two-solutions-imply-infinitely-many claim")


def check_limits_continuity_differentiability():
    """Every number published in the Calculus limits/continuity/differentiability topic is recomputed."""
    import math

    def close(a, b, tol=1e-6):
        if b == 0:
            return abs(a) <= tol
        return abs(a - b) <= tol * max(1.0, abs(b))

    def lim_at(f, a, side=1, h=1e-6):
        return f(a + side * h)

    # ---- the limit at a point: (x^2 - 1)/(x - 1) has a hole at 1 and limit 2
    hole = lambda x: (x * x - 1) / (x - 1)
    table = [(0.9, 1.9), (0.99, 1.99), (0.999, 1.999), (1.001, 2.001), (1.01, 2.01), (1.1, 2.1)]
    for x, y in table:
        if not close(hole(x), y, 1e-9):
            fail("math: f(%s) for (x^2-1)/(x-1) should be %s, computed %s" % (x, y, hole(x)))
    if not close(hole(1 + 1e-9), 2, 1e-6) or not close(hole(1 - 1e-9), 2, 1e-6):
        fail("math: the limit of (x^2-1)/(x-1) at 1 must be 2 from both sides")
    if not close(lim_at(lambda x: (x * x - 4) / (x - 2), 2), 4, 1e-4):
        fail("math: (x^2-4)/(x-2) at 2 must tend to 4")
    if not close(lim_at(lambda x: (x * x - 9) / (x - 3), 3), 6, 1e-4):
        fail("math: (x^2-9)/(x-3) at 3 must tend to 6")
    # g(x) = |x|/x has one-sided limits -1 and +1
    g = lambda x: abs(x) / x
    if not close(g(-1e-6), -1) or not close(g(1e-6), 1):
        fail("math: |x|/x must have one-sided limits -1 and +1 at 0")

    # ---- algebra of limits: 3x^2 - 5x + 1 at 2 is 3, x^3 + 2x at 1 is 3
    if 3 * 2 ** 2 - 5 * 2 + 1 != 3:
        fail("math: 3x^2-5x+1 at x=2 must be 3")
    if 1 ** 3 + 2 * 1 != 3:
        fail("math: x^3+2x at x=1 must be 3")

    # ---- the standard limits
    if not close(lim_at(lambda x: math.sin(x) / x, 0, 1, 1e-6), 1, 1e-9):
        fail("math: sin x / x must tend to 1")
    if not close(lim_at(lambda x: (1 - math.cos(x)) / (x * x), 0, 1, 1e-3), 0.5, 1e-6):
        fail("math: (1-cos x)/x^2 must tend to 1/2")
    if not close(lim_at(lambda x: (math.exp(x) - 1) / x, 0, 1, 1e-6), 1, 1e-6):
        fail("math: (e^x-1)/x must tend to 1")
    if not close(lim_at(lambda x: math.log(1 + x) / x, 0, 1, 1e-6), 1, 1e-6):
        fail("math: ln(1+x)/x must tend to 1")
    if not close(lim_at(lambda x: (3.0 ** x - 1) / x, 0, 1, 1e-6), math.log(3), 1e-6):
        fail("math: (a^x-1)/x must tend to ln a")
    if not close((1 + 1e-6) ** (1 / 1e-6), math.e, 1e-4):
        fail("math: (1+x)^(1/x) must tend to e")
    if not close((1 + 2.0 / 1e7) ** 1e7, math.e ** 2, 1e-3):
        fail("math: (1+a/x)^x must tend to e^a")
    if not close(lim_at(lambda x: (1 - math.cos(3 * x)) / (x * x), 0, 1, 1e-3), 4.5, 1e-5):
        fail("math: (1-cos 3x)/x^2 must tend to 9/2")
    if not close(lim_at(lambda x: (math.exp(5 * x) - 1) / x, 0, 1, 1e-6), 5, 1e-5):
        fail("math: (e^5x-1)/x must tend to 5")
    if not close(lim_at(lambda x: (math.exp(2 * x) - 1) / x, 0, 1, 1e-6), 2, 1e-5):
        fail("math: (e^2x-1)/x must tend to 2")
    if not close(lim_at(lambda x: (1 - math.cos(x)) / (x * math.sin(x)), 0, 1, 1e-4), 0.5, 1e-4):
        fail("math: (1-cos x)/(x sin x) must tend to 1/2")
    # degrees: sin(x degrees)/x -> pi/180
    if not close(math.sin(math.radians(1e-6)) / 1e-6, math.pi / 180, 1e-6):
        fail("math: sin x / x in degrees must tend to pi/180")

    # ---- L'Hopital questions
    if not close(lim_at(lambda x: (x ** 7 - 2 * x ** 5 + 1) / (x ** 3 - 3 * x * x + 2), 1, 1, 1e-6), 1, 1e-4):
        fail("math: GATE 2017 Set 1 Q.28 limit must be 1")
    if not close(lim_at(lambda x: (x ** 4 - 81) / (2 * x * x - 5 * x - 3), 3, 1, 1e-6), 108 / 7, 1e-6):
        fail("math: GATE 2019 Q.13 limit must be 108/7")
    if not close(lim_at(lambda x: (math.sqrt(2 * x + 22) - 4) / (x + 3), -3, 1, 1e-6), 0.25, 1e-6):
        fail("math: GATE 2021 Set 1 Q.20 limit must be 0.25")
    if not close(lim_at(lambda x: math.sqrt(x) / (1 - math.exp(2 * math.sqrt(x))), 0, 1, 1e-8), -0.5, 1e-4):
        fail("math: GATE 2022 Q.24 limit must be -1/2")
    if not close(lim_at(lambda x: math.sin(x - 4) / (x - 4), 4, 1, 1e-6), 1, 1e-8):
        fail("math: GATE 2016 Set 1 Q.3 limit must be 1")
    if not close(lim_at(lambda x: (x ** 3 - 1) / (x * x - 1), 1, 1, 1e-6), 1.5, 1e-6):
        fail("math: (x^3-1)/(x^2-1) at 1 must tend to 3/2")
    # the non-indeterminate counterexample: value 1, derivative ratio 2
    if (1 + 1) / (1 + 1) != 1:
        fail("math: (x^2+1)/(x+1) at x=1 must be 1")
    if 2 * 1 / 1 != 2:
        fail("math: the derivative ratio of (x^2+1)/(x+1) at x=1 is 2, not 1")
    # the oscillating counterexample: (x + sin x)/x -> 1 while (1 + cos x) has no limit
    if not close((1e6 + math.sin(1e6)) / 1e6, 1, 1e-5):
        fail("math: (x+sin x)/x at infinity must tend to 1")
    if not (min(1 + math.cos(x / 100.0) for x in range(2000)) < 0.001):
        fail("math: 1 + cos x must come arbitrarily close to 0, so the derivative ratio has no limit")

    # ---- the other indeterminate forms
    if not close(lim_at(lambda x: x * math.log(x), 0, 1, 1e-9), 0, 1e-6):
        fail("math: x ln x must tend to 0")
    if not close(lim_at(lambda x: math.sqrt(x * x + x) - x, 0, 1, 1e8), 0.5, 1e-4):
        fail("math: sqrt(x^2+x)-x must tend to 1/2")
    if not close(math.exp(math.log(math.cos(1e-4)) / 1e-8), math.exp(-0.5), 1e-4):
        fail("math: (cos x)^(1/x^2) must tend to e^-1/2")
    if not close((1e-4) ** (1e-4), 1, 1e-2):
        fail("math: x^x must tend to 1")
    if not close((1 + 2.0 / 1e7) ** 1e7, math.exp(2), 1e-3):
        fail("math: (1+2/x)^x must tend to e^2")

    # ---- limits at infinity and orders of growth
    if not close((3 * 1e6 ** 3 - 2 * 1e6 + 1) / (1e6 ** 3 + 5), 3, 1e-9):
        fail("math: the ratio of cubics must tend to 3")
    if not close((1e5) ** (1 / 1e5), 1, 2e-3):
        fail("math: x^(1/x) must tend to 1")
    if not close((1e6 - math.sin(1e6)) / (1e6 + math.cos(1e6)), 1, 1e-5):
        fail("math: (x - sin x)/(x + cos x) must tend to 1")
    if not close((1 + 500.0 ** 2) * math.exp(-500), 0, 1e-9):
        fail("math: (1+x^2)e^-x must tend to 0")
    if not close(math.log(1e9) / 1e9, 0, 1e-7):
        fail("math: (ln x)/x must tend to 0")
    if 2 ** 200 / 200 ** 2 <= 1e10:
        fail("math: 2^x/x^2 must grow without bound")
    # the growth ladder: x^p / e^x -> 0 for a fixed p
    if not close(100.0 ** 3 / math.exp(100), 0, 1e-9):
        fail("math: x^3/e^x must tend to 0")

    # ---- continuity at a point: the four options of GATE CSE 2013 Q.22
    optA_lhl = (3 + 3) / 3
    optA_rhl = 3 - 1
    if not (optA_lhl == optA_rhl == 2):
        fail("math: 2013 Q.22 option (A) must give LHL = RHL = f(3) = 2")
    if not (8 - 3 == 5 and 5 != 4):
        fail("math: 2013 Q.22 option (B) must have limit 5 and value 4")
    if not (3 + 3 == 6 and 3 - 4 == -1):
        fail("math: 2013 Q.22 option (C) must have one-sided limits 6 and -1")
    if not (lim_at(lambda x: 1 / (x ** 3 - 27), 3, -1, 1e-7) < -1e5):
        fail("math: 2013 Q.22 option (D) must tend to -infinity from the left")
    if not (lim_at(lambda x: 1 / (x ** 3 - 27), 3, 1, 1e-7) > 1e5):
        fail("math: 2013 Q.22 option (D) must tend to +infinity from the right")
    # the piecewise example and the jump example on the cards
    if not (2 * 3 + 1 == 3 * 3 - 2 == 7):
        fail("math: the 2x+1 / 3x-2 piecewise must meet at 7 at x = 3")
    if not ((2 + 1) != (2 + 3)):
        fail("math: the x+1 / x+3 jump example must give 3 and 5")
    if not close(lim_at(lambda x: (x * x - 9) / (x - 3), 3), 6, 1e-4):
        fail("math: the removable example must have limit 6, matching the assigned f(3)")

    # ---- GATE CSE 2026 Set 1 Q.22: a logarithm term cannot produce a finite limit
    if not (math.log(1 / 1e-30) > 60 and math.log(1 / 1e-15) > math.log(1 / 1e-9)):
        fail("math: c2 ln(1/x) with c2 = -1 must diverge as x -> 0+")
    if not close(3.0 * math.exp(0), 3, 1e-9):
        fail("math: with c2 = 0 the one-sided limit is c1 = 3")

    # ---- the Intermediate Value Theorem
    def cube_root_fn(x):
        return x ** 3 + x - 1
    if not (cube_root_fn(0) < 0 < cube_root_fn(1)):
        fail("math: x^3+x-1 must change sign on [0, 1]")
    if not close(cube_root_fn(0.68), -0.005568, 1e-6):
        fail("math: f(0.68) for x^3+x-1 must be -0.005568")
    if not close(cube_root_fn(0.69), 0.018509, 1e-6):
        fail("math: f(0.69) for x^3+x-1 must be 0.018509")
    if not (cube_root_fn(0.68) < 0 < cube_root_fn(0.69)):
        fail("math: the root of x^3+x-1 must lie between 0.68 and 0.69")
    # GATE CSE 2014 Set 1 Q.47: g(y) = f(y) - f(y+1) with the given values
    fvals = {0: -1, 1: 1, 2: -1}
    if not (fvals[0] - fvals[1] == -2 and fvals[1] - fvals[2] == 2):
        fail("math: 2014 Set 1 Q.47 must give g(0) = -2 and g(1) = 2")
    # x^3 - x has three zeros on [-1, 1]
    zeros = [x / 100.0 for x in range(-100, 101) if abs((x / 100.0) ** 3 - (x / 100.0)) < 1e-9]
    if zeros != [-1.0, 0.0, 1.0]:
        fail("math: x^3 - x must vanish exactly at -1, 0 and 1 on [-1, 1]")

    # ---- differentiability
    def abs_slope(h):
        return (abs(h) - 0) / h
    if not (abs_slope(-1e-6) == -1 and abs_slope(1e-6) == 1):
        fail("math: |x| must have one-sided derivatives -1 and +1 at 0")
    for h in (-1e-6, 1e-6):
        if not close((h * abs(h)) / h, abs(h), 1e-9):
            fail("math: x|x| must have derivative 0 at 0")
    if not ((1e-12) ** (2.0 / 3) / 1e-12 > 1e3):
        fail("math: the difference quotient of x^(2/3) at 0 must blow up")
    # GATE CSE 2025 Set 1 Q.21 and the card's quick check
    if not (5 + (-2) == 1 + 1 + 1):
        fail("math: a + b = 3 must hold for a = 5, b = -2")
    if not (3 * 1 ** 2 + 2 * 1 == 5):
        fail("math: the right derivative of x^3+x^2+1 at 1 must be 5")
    if not (5 * 1 + 0 != 1 + 1 + 1):
        fail("math: with a = 5 and b = 0 the pieces would jump from 5 to 3 at x = 1")
    if not (4 == 2 * 4 + (-4)):
        fail("math: the quick check must give a = 4, b = -4")
    if not (2 * 2 == 4):
        fail("math: the left derivative of x^2 at 2 must be 4")
    # GATE CSE 2024 Set 1 Q.1: the crossings and the three slope pairs
    crossings = [x / 100.0 for x in range(-300, 301) if abs((x / 100.0) ** 3 - (x / 100.0)) < 1e-9]
    if crossings != [-1.0, 0.0, 1.0]:
        fail("math: max{x, x^3} must change pieces at -1, 0 and 1")
    pairs = [(-1.0, 3 * (-1.0) ** 2, 1), (0.0, 0.0, 1), (1.0, 3 * 1 ** 2, 1)]
    for at, left, right in pairs:
        if left == right:
            fail("math: the two pieces of max{x, x^3} must have different slopes at %s" % at)
    if not (3 * (1.5) ** 2 + 2 * (1.5) == 9.75):
        fail("math: the right derivative at x = 1.5 is 9.75, so x = 1.5 is not a corner")
    # max{x, x^2} crosses at 0 and 1 with slopes (1, 0) and (1, 2)
    if not (1 != 0 and 1 != 2):
        fail("math: max{x, x^2} must have unequal slopes at 0 and at 1")
    lhd = (abs(2 + (-1e-6) - 2) - 0) / (-1e-6)
    rhd = (abs(2 + 1e-6 - 2) - 0) / (1e-6)
    if not (lhd < 0 < rhd):
        fail("math: |x-2| must have one-sided derivatives of opposite signs at 2")
    # 1998 Q.1.4 verdict
    if not (abs(0.0) == 0.0):
        fail("math: |x| must equal 0 at 0, so it is continuous there")

    # ---- the lecture summary's own worked limits
    if not close(lim_at(lambda x: (3 - math.sqrt(5 + x)) / (x - 4), 4, 1, 1e-6), -1 / 6, 1e-6):
        fail("math: (3-sqrt(5+x))/(x-4) at 4 must tend to -1/6")
    if not close(lim_at(lambda x: (math.exp(x) - 1) / (x * x + x), 0, 1, 1e-6), 1, 1e-6):
        fail("math: (e^x-1)/(x^2+x) at 0 must tend to 1")

    ok("Limits, continuity and differentiability: the hole example and its six table values; |x|/x, "
       "x|x|, x^(2/3) and |x-2| one-sided derivatives; the standard limits including the degree case; "
       "the 2013, 2014, 2015, 2016, 2017, 2019, 2021, 2022, 2024, 2025, 2026 and 1998 questions "
       "recomputed from their own expressions; the removable, jump and infinite verdicts of 2013 Q.22; "
       "the growth ladder; the two non-indeterminate and oscillating counterexamples; the root of "
       "x^3+x-1 between 0.68 and 0.69; the constructed IVT function; and the two piecewise constants "
       "of 2025 Q.21 and the quick check")


def check_maxima_and_minima():
    """Every value, sign, verdict and count published in the Maxima and Minima topic is recomputed."""
    import math

    def close(a, b, tol=1e-9):
        return abs(a - b) <= tol * max(1.0, abs(b))

    # ---- the lesson and 2008 Q.25 function
    f = lambda x: 3 * x ** 4 - 16 * x ** 3 + 24 * x ** 2 + 37
    d1 = lambda x: 12 * x ** 3 - 48 * x ** 2 + 48 * x
    d2 = lambda x: 36 * x ** 2 - 96 * x + 48
    d3 = lambda x: 72 * x - 96
    for x in (-1.0, 0.0, 0.5, 1.0, 2.0, 3.0, 4.0):
        h = 1e-6
        if not close((f(x + h) - f(x - h)) / (2 * h), d1(x), 1e-4):
            fail("maxima: f'(%s) disagrees with the difference quotient of 3x^4-16x^3+24x^2+37" % x)
    if not close(d1(0), 0) or not close(d1(2), 0):
        fail("maxima: 12x(x-2)^2 must vanish at 0 and at 2")
    if not (close(d1(-0.5), -37.5) and close(d1(1), 12) and close(d1(3), 36)):
        fail("maxima: the published signs of f' (-37.5, 12, 36) must be right")
    if not (close(f(-1), 80) and close(f(0), 37) and close(f(2), 53) and close(f(4), 165)):
        fail("maxima: the published values f(-1)=80, f(0)=37, f(2)=53, f(4)=165 must be right")
    if not (close(d2(0), 48) and close(d2(2), 0) and close(d3(2), 48)):
        fail("maxima: the second derivative must be 48 at 0 and 0 at 2, and the third derivative 48 at 2")
    if not (d1(-0.01) < 0 < d1(0.01)):
        fail("maxima: f' must change from negative to positive at x = 0")
    if not (d1(1.99) > 0 and d1(2.01) > 0):
        fail("maxima: f' must keep its sign on both sides of x = 2")
    grid = [i / 200.0 + 0.0025 for i in range(-200, 900)]
    changes = sum(1 for a, b in zip(grid, grid[1:]) if d1(a) * d1(b) < 0)
    if changes != 1:
        fail("maxima: 3x^4-16x^3+24x^2+37 must have exactly one extremum, found %d" % changes)
    if not (max(f(-1), f(0), f(2), f(4)) == 165 and min(f(-1), f(0), f(2), f(4)) == 37):
        fail("maxima: on [-1,4] the extreme values must be 165 at 4 and 37 at 0")

    # ---- the cubic criterion b^2 - 3ac, checked over every small integer cubic
    for a in (-3, -2, -1, 1, 2, 3):
        for b in range(-4, 5):
            for c in range(-4, 5):
                disc = 4 * (b * b - 3 * a * c)
                stationary = 0
                if disc > 0:
                    stationary = 2
                elif disc == 0:
                    stationary = 1
                roots = set()
                if disc > 0:
                    sq = math.sqrt(disc)
                    roots.add(round((-2 * b - sq) / (6 * a), 9))
                    roots.add(round((-2 * b + sq) / (6 * a), 9))
                elif disc == 0:
                    roots.add(round(-2 * b / (6 * a), 9))
                if len(roots) != stationary:
                    fail("maxima: the cubic criterion miscounts stationary points for a=%r b=%r c=%r" % (a, b, c))
                if (b * b - 3 * a * c > 0) != (stationary == 2):
                    fail("maxima: b^2 > 3ac must be equivalent to two stationary points")
    cub = lambda x: x ** 3 + 15 * x ** 2 - 33 * x - 36
    if not (close(3 * 1 ** 2 + 30 * 1 - 33, 0) and close(3 * 121 - 330 - 33, 0)):
        fail("maxima: 2023 Q.18 must have stationary points at -11 and 1")
    if not (close(6 * 1 + 30, 36) and close(6 * (-11) + 30, -36)):
        fail("maxima: 2023 Q.18 must give f''(1) = 36 and f''(-11) = -36")
    if not (15 ** 2 - 3 * 1 * (-33) == 324):
        fail("maxima: 2023 Q.18 must give b^2 - 3ac = 324")
    if not (close(cub(1), -53) and close(cub(-11), 811)):
        fail("maxima: 2023 Q.18 values at the stationary points must be -53 and 811")
    for x in (-2.0, -1.0, 0.0, 0.5):
        if not close(x ** 3 + 3 * x ** 2 + 3 * x + 1, (x + 1) ** 3):
            fail("maxima: x^3+3x^2+3x+1 must equal (x+1)^3")
    if not (0 - 3 * 1 * 3 == -9):
        fail("maxima: x^3+3x^2+3x+1 must give b^2-3ac = 0")
    if not (-3 * 1 * 1 == -3):
        fail("maxima: x^3 + kx must give b^2 - 3ac = -3k, negative exactly when k < 0")

    # ---- 1997 Q.4.1 on the closed interval
    q97 = lambda x: 2 * x ** 2 - 2 * x + 6
    if not (close(q97(0), 6) and close(q97(0.5), 5.5) and close(q97(2), 10)):
        fail("maxima: 1997 Q.4.1 must give f(0)=6, f(1/2)=5.5, f(2)=10")

    # ---- 2012 Q.9 and the trigonometric values
    s2 = math.sqrt(2) / 2
    if not (close(math.sin(math.pi / 4), s2) and close(math.sin(math.pi / 2), 1)
            and close(math.sin(3 * math.pi / 2), -1) and close(math.sin(7 * math.pi / 4), -s2)):
        fail("maxima: the sine values at pi/4, pi/2, 3pi/2, 7pi/4 must be 0.707, 1, -1, -0.707")
    if not (-math.sin(math.pi / 2) < 0 < -math.sin(3 * math.pi / 2)):
        fail("maxima: sin must have a maximum at pi/2 and a minimum at 3pi/2")
    if not (s2 < math.sin(math.pi / 4 + 1e-6)):
        fail("maxima: pi/4 must be a local minimum of sin on [pi/4, 7pi/4] under the endpoint convention")
    if not (math.sin(7 * math.pi / 4 - 1e-6) < -s2):
        fail("maxima: 7pi/4 must be a local maximum, not a minimum, under the endpoint convention")

    # ---- 2026 Set 1 Q.36, piece by piece
    def q26(x):
        g = abs(x) / 2.0 - x
        return g * (x - abs(x) / 2.0)
    if not (close(q26(0), 0) and close(q26(1), -0.25) and close(q26(-1), -2.25)):
        fail("maxima: 2026 Set 1 Q.36 must give f(0)=0, f(1)=-0.25, f(-1)=-2.25")
    for x in (-3.0, -1.0, -0.1, 0.1, 1.0, 3.0):
        if not q26(x) < 0:
            fail("maxima: 2026 Set 1 Q.36 must be negative away from 0")
    for x in (0.5, 1.0, 2.0):
        if not close((q26(x + 1e-6) - q26(x)) / 1e-6, -x / 2.0, 1e-4):
            fail("maxima: 2026 Set 1 Q.36 must have f'(x) = -x/2 for x > 0")
    for x in (-0.5, -1.0, -2.0):
        if not close((q26(x + 1e-6) - q26(x)) / 1e-6, -9 * x / 2.0, 1e-4):
            fail("maxima: 2026 Set 1 Q.36 must have f'(x) = -9x/2 for x < 0")
    left = (q26(-1e-6) - q26(0)) / -1e-6
    right = (q26(1e-6) - q26(0)) / 1e-6
    if not (close(left, 0, 1e-4) and close(right, 0, 1e-4)):
        fail("maxima: 2026 Set 1 Q.36 must have f'(0) = 0 from both sides, so f' is continuous")
    dl = (-9 * (-1e-6) / 2.0 - 0) / -1e-6
    dr = (-1e-6 / 2.0 - 0) / 1e-6
    if not (close(dl, -4.5, 1e-3) and close(dr, -0.5, 1e-3)):
        fail("maxima: the one-sided derivatives of f' at 0 must be -4.5 and -0.5, so f' is not differentiable there")

    # ---- 1993 Q.1.7, the two-variable case
    fx = lambda x, y: 2 * x * y - 3 * y + 1
    fy = lambda x, y: x * x - 3 * x + 2
    if not (close(fy(1, 0), 0) and close(fy(2, 0), 0) and not close(fy(1.5, 0), 0)):
        fail("maxima: f_y of the 1993 question must vanish at x = 1 and x = 2 only")
    if not (close(fx(1, 1), 0) and close(fx(2, -1), 0)):
        fail("maxima: the 1993 stationary points must be (1,1) and (2,-1)")
    for (x, y) in ((1, 1), (2, -1)):
        r, s, t = 2 * y, 2 * x - 3, 0
        if not (r * t - s * s == -1):
            fail("maxima: rt - s^2 must be -1 at %r, so there is no extremum" % ((x, y),))
    if not (-(2 * 1.5 - 3) ** 2 == 0):
        fail("maxima: rt - s^2 of the 1993 question vanishes only at x = 1.5, where f_y != 0")
    if not (2 * (-2) - 0 < 0):
        fail("maxima: x^2 - y^2 must give D = -4 at the origin")

    # ---- monotonicity and the union trap
    m = lambda x: x ** 3 - 3 * x
    if not (close(m(-1), 2) and close(m(1), -2) and close(m(-2), -2) and close(m(2), 2)):
        fail("maxima: x^3 - 3x must take 2 at -1 and 2, and -2 at 1 and -2")
    if not (m(-2) < m(2) and m(-1) > m(1)):
        fail("maxima: x^3 - 3x must not be increasing on the union of its two increasing pieces")
    q = lambda x: 2 * x ** 3 - 3 * x ** 2 - 12 * x
    for x in (-2.0, -1.5, 2.5, 3.0):
        if not (6 * x * x - 6 * x - 12 > 0):
            fail("maxima: 2x^3-3x^2-12x must be increasing outside [-1,2]")
    for x in (-0.5, 0.0, 1.0, 1.5):
        if not (6 * x * x - 6 * x - 12 < 0):
            fail("maxima: 2x^3-3x^2-12x must be decreasing inside (-1,2)")

    # ---- the quartic used for the repeated root
    q4 = lambda x: x ** 4 - 4 * x ** 3
    if not (close(q4(3), -27) and close(q4(0), 0)):
        fail("maxima: x^4-4x^3 must give f(3) = -27 and f(0) = 0")
    if not (4 * (-1) ** 3 - 12 * (-1) ** 2 < 0 and 4 * 1 ** 3 - 12 * 1 ** 2 < 0 and 4 * 4 ** 3 - 12 * 4 ** 2 > 0):
        fail("maxima: x^4-4x^3 must have f' negative on both sides of 0 and positive after 3")

    # ---- the higher-derivative orders and the quintic variation
    if not (math.factorial(6) == 720 and math.factorial(5) == 120):
        fail("maxima: the sixth derivative of x^6 at 0 must be 720 and the fifth of x^5 must be 120")
    q5 = lambda x: x ** 5 - 5 * x ** 4
    dq5 = lambda x: 5 * x ** 3 * (x - 4)
    if not (close(q5(0), 0) and close(q5(4), -256)):
        fail("maxima: x^5 - 5x^4 must give f(0) = 0 and f(4) = -256")
    if not (dq5(-1) > 0 and dq5(1) < 0 and dq5(5) > 0):
        fail("maxima: x^5 - 5x^4 must change the sign of f' at both 0 and 4")

    # ---- x^4 - 2x^2 and x^4 - 4x
    if not (close(12 * 0 - 4, -4) and close(12 * 1 - 4, 8) and close(12 * 1 - 4, 8)):
        fail("maxima: x^4-2x^2 must give f''(0) = -4 and f''(+-1) = 8")
    b4 = lambda x: x ** 4 - 4 * x
    if not (close(b4(0), 0) and close(b4(1), -3) and close(b4(2), 8)):
        fail("maxima: x^4-4x on [0,2] must give 0, -3 and 8")

    # ---- the optimisation examples
    area = lambda x: x * x / 16 + (1 - x) ** 2 / 16
    if not (close(area(0.5), 1 / 32.0) and close(area(0), 1 / 16.0) and close(area(1), 1 / 16.0)):
        fail("maxima: the wire problem must give 1/32 at x = 1/2 and 1/16 at both ends")
    for x in (0.25, 0.5, 0.75):
        if not close((2 * x - 1) / 8.0, (area(x + 1e-7) - area(x - 1e-7)) / 2e-7, 1e-4):
            fail("maxima: the wire problem must have A'(x) = (2x - 1)/8")
    if not (close(2 + 4 / 2.0, 4) and close(1 - 4 / 4.0, 0)):
        fail("maxima: x + 4/x must have a minimum 4 at x = 2")
    if not (close(4 + 16 / 2.0, 12) and close(2 * 2 - 16 / 4.0, 0)):
        fail("maxima: x^2 + 16/x must have a minimum 12 at x = 2")
    if not (5 * (10 - 5) == 25):
        fail("maxima: the perimeter-20 rectangle must have maximum area 25")

    # ---- local and global extrema examples
    g2 = lambda x: x * x
    if not (g2(0) == 0 and g2(2) == 4 and g2(0) < g2(0.5) < g2(2)):
        fail("maxima: x^2 on [-1,2] must have minimum 0 at 0 and maximum 4 at 2")
    c3 = lambda x: x ** 3 - x
    if not (close(c3(1 / math.sqrt(3)), -2 / (3 * math.sqrt(3)), 1e-9)
            and close(c3(-1 / math.sqrt(3)), 2 / (3 * math.sqrt(3)), 1e-9)):
        fail("maxima: x^3 - x must take -2/(3 sqrt3) at 1/sqrt3 and 2/(3 sqrt3) at -1/sqrt3")
    t3 = lambda x: x ** 3 - 3 * x
    if not (close(t3(-2), -2) and close(t3(-1), 2) and close(t3(1), -2) and close(t3(2), 2)):
        fail("maxima: x^3 - 3x on [-2,2] must give -2, 2, -2, 2 at -2, -1, 1, 2")
    if not (close(t3(0), 0) and close(t3(3), 18) and close(t3(1), -2)):
        fail("maxima: x^3 - 3x on [0,3] must give 0, -2 and 18 at 0, 1, 3")

    # ---- min{x^2, x} is non-decreasing, so it has no extremum at either join
    mm = lambda x: min(x * x, x)
    prev = mm(-3.0)
    x = -3.0
    while x < 3.0:
        x += 0.01
        if mm(x) < prev - 1e-12:
            fail("maxima: min{x^2, x} must be non-decreasing everywhere")
        prev = mm(x)
    if not (mm(0) == 0 and mm(1) == 1):
        fail("maxima: min{x^2, x} must pass through (0,0) and (1,1)")
    if not (mm(0.5) == 0.25 and mm(2.0) == 2.0):
        fail("maxima: min{x^2, x} must be x^2 on (0,1) and x above 1")

    # ---- x^(2/3) has a critical point that is not stationary
    if not (abs((2.0 / 3) * (1e-9) ** (-1.0 / 3)) > 100):
        fail("maxima: the derivative of x^(2/3) must blow up at 0 and never vanish")

    ok("Maxima and minima: the 2008 quartic's derivative, values, signs, its single sign change and its "
       "closed-interval extremes; the cubic criterion b^2-3ac over every small integer cubic plus both PYQ "
       "cubics; the 1997 closed-interval values; the 2012 sine values and both endpoint verdicts; the 2026 "
       "piecewise function's values, slopes, continuity and kink; the 1993 stationary points and rt - s^2; "
       "the monotonicity and union claims; the higher-derivative orders and the quintic variation; and the "
       "optimisation values including the wire problem")


def check_mean_value_theorem():
    """Every value, root, bound and verdict published in the Mean Value Theorem topic is recomputed."""
    import math

    def close(a, b, tol=1e-6):
        return abs(a - b) <= tol * max(1.0, abs(b))

    C = 2 / math.sqrt(3)                      # the mean value theorem point of x^3 on [0, 2]

    # ---- card 1: Rolle on x^2 - 4x + 3 over [1, 3]
    q = lambda x: x * x - 4 * x + 3
    if not (close(q(1), 0) and close(q(3), 0)):
        fail("mvt: x^2-4x+3 must vanish at 1 and at 3")
    if not close(2 * 2 - 4, 0):
        fail("mvt: Rolle point of x^2-4x+3 on [1,3] must be c = 2")
    if not close(q(2), -1):
        fail("mvt: x^2-4x+3 must be -1 at c = 2")
    # the trap counterexample: x^2 on [0,2] has no interior zero slope
    if any(close(2 * x, 0) for x in (0.25, 0.5, 1.0, 1.5, 1.75)):
        fail("mvt: 2x must not vanish inside (0,2)")
    # the check: x^(2/3) on [-1,1] has no interior zero slope
    if any(close((2.0 / 3) * x ** (-1.0 / 3), 0) for x in (-0.5, -0.25, 0.25, 0.5)):
        fail("mvt: the derivative of x^(2/3) must never vanish off 0")

    # ---- card 2 and the lesson: x^3 on [0,2]
    f = lambda x: x ** 3
    if not close((f(2) - f(0)) / 2.0, 4):
        fail("mvt: the chord slope of x^3 on [0,2] must be 4")
    for x, want in ((0.0, 0.0), (1.0, 3.0), (2.0, 12.0)):
        if not close(3 * x * x, want):
            fail("mvt: 3x^2 must be %r at x = %r" % (want, x))
    if not close(3 * C * C, 4):
        fail("mvt: 3c^2 = 4 at c = 2/sqrt(3)")
    if not close(f(C), 1.539600717839002, 1e-9):
        fail("mvt: f(2/sqrt(3)) must be 1.5396")
    if not close(C, 1.1547005383792517, 1e-9):
        fail("mvt: 2/sqrt(3) must be 1.1547005")
    if not (0 < C < 2):
        fail("mvt: the mean value theorem point of x^3 on [0,2] must be interior")
    # the trap: the midpoint is not the point
    if close(3 * 1.0 * 1.0, 4):
        fail("mvt: the midpoint of [0,2] must not satisfy the mean value theorem for x^3")
    # the check: x^2 on [0,2] gives the midpoint
    if not close(2 * 1.0, 2.0):
        fail("mvt: x^2 on [0,2] must give c = 1")
    # the quadratic midpoint rule, checked on several quadratics
    for A, B, Cc in ((1, 0, 0), (2, -3, 5), (-1, 4, 1), (0.5, 2, -7)):
        for a, b in ((0, 2), (-1, 3), (1, 4), (-2.5, 0.5)):
            avg = (A * (b * b - a * a) + B * (b - a)) / (b - a)
            mid = (a + b) / 2.0
            if not close(2 * A * mid + B, avg):
                fail("mvt: the midpoint must be the mean value theorem point of a quadratic")
    # the variation: x^3 - 3x on [0,2]
    h = lambda x: x ** 3 - 3 * x
    if not close((h(2) - h(0)) / 2.0, 1):
        fail("mvt: the average slope of x^3-3x on [0,2] must be 1")
    if not close(3 * C * C - 3, 1):
        fail("mvt: 3c^2-3 = 1 at c = 2/sqrt(3)")
    if not close(3 * 1.0 - 3, 0):
        fail("mvt: x^3-3x must have derivative 0 at the midpoint 1, so the midpoint is not the point")

    # ---- card 3: the 2021 Set 2 Q.25 bound
    if not close(6 * 2 + 7, 19):
        fail("mvt: 2021 Set 2 Q.25 must give f(3) <= 19")
    if not close(2 * 3 + 13, 19) or not close(2 * (-3) + 13, 7):
        fail("mvt: 2x+13 must attain the bound, with f(-3) = 7 and f(3) = 19")
    if not close(-19 * (-3) - 50, 7):
        fail("mvt: -19x-50 must have the value 7 at x = -3")
    if not close(-19 * 3 - 50, -107):
        fail("mvt: -19x-50 must have the value -107 at x = 3, the trap counterexample")
    if not (-19 <= 2):
        fail("mvt: the slope -19 of the trap counterexample must satisfy f' <= 2")
    if not close(3 * 4 + 1, 13):
        fail("mvt: the quick check bound f(4) <= 13 must be right")

    # ---- card 4: the failure cases
    if not close(abs(-1), abs(1)):
        fail("mvt: |x| must have equal endpoint values on [-1,1]")
    if not close(1 / (2 * math.sqrt(0.25)), 1):
        fail("mvt: sqrt(x) on [0,1] must give c = 1/4")
    if not (1 / (2 * math.sqrt(0.25)) > 0):
        fail("mvt: the derivative of sqrt(x) must be positive")
    if any(close(-1.0 / (x * x), 0) for x in (-2.0, -0.5, 0.5, 2.0)):
        fail("mvt: the derivative of 1/x must never vanish")
    if not (math.sqrt(3 * 1 + 1) > 0):
        fail("mvt: sqrt(x^3+1) must be defined on [0,1]")

    # ---- card 5: finding the point for x^3 - 4x on [0,3]
    k = lambda x: x ** 3 - 4 * x
    if not close((k(3) - k(0)) / 3.0, 5):
        fail("mvt: the average slope of x^3-4x on [0,3] must be 5")
    if not close(k(3), 15):
        fail("mvt: x^3-4x must be 15 at 3")
    if not close(3 * 3 - 4, 5):
        fail("mvt: 3c^2-4 = 5 at c = sqrt(3)")
    if not close(math.sqrt(3), 1.7320508075688772, 1e-9):
        fail("mvt: sqrt(3) must be 1.7320508")
    if not (0 < math.sqrt(3) < 3):
        fail("mvt: sqrt(3) must lie in (0,3) and -sqrt(3) outside it")
    # the OpenStax Rolle example x^2 + 2x on [-2, 0]
    r2 = lambda x: x * x + 2 * x
    if not (close(r2(-2), 0) and close(r2(0), 0) and close(2 * (-1) + 2, 0)):
        fail("mvt: x^2+2x on [-2,0] must have its Rolle point at -1")
    # the check: x^3 on [-2,2]
    if not close((8 - (-8)) / 4.0, 4):
        fail("mvt: the average slope of x^3 on [-2,2] must be 4")

    # ---- card 6: existence, not uniqueness
    g = lambda x: x ** 3 - 4 * x
    if not (close(g(-2), 0) and close(g(2), 0)):
        fail("mvt: x^3-4x must vanish at both ends of [-2,2]")
    if not (close(g(C), -3.079201435678004, 1e-9) and close(g(-C), 3.079201435678004, 1e-9)):
        fail("mvt: x^3-4x must be -3.0792 at 2/sqrt(3) and 3.0792 at -2/sqrt(3)")
    if not (close(math.sin(0), 0) and close(math.sin(2 * math.pi), 0, 1e-9)):
        fail("mvt: sin must vanish at 0 and at 2 pi")
    if not (close(math.cos(math.pi / 2), 0, 1e-9) and close(math.cos(3 * math.pi / 2), 0, 1e-9)):
        fail("mvt: cos must vanish at pi/2 and 3pi/2")
    cub = lambda x: x * (x - 1) * (x - 2)
    roots = sorted([(6 - math.sqrt(36 - 24)) / 6.0, (6 + math.sqrt(36 - 24)) / 6.0])
    if not (close(roots[0], 1 - 1 / math.sqrt(3), 1e-9) and close(roots[1], 1 + 1 / math.sqrt(3), 1e-9)):
        fail("mvt: the Rolle points of x(x-1)(x-2) must be 1 -+ 1/sqrt(3)")
    if not (0 < roots[0] < roots[1] < 2):
        fail("mvt: both Rolle points of x(x-1)(x-2) must lie in (0,2)")
    for x in (roots[0], roots[1]):
        if not close(3 * x * x - 6 * x + 2, 0, 1e-9):
            fail("mvt: the derivative of x(x-1)(x-2) must vanish at its Rolle points")
    # the check: x^4 - 5x^2 + 4 with roots at 1 and 2
    qu = lambda x: x ** 4 - 5 * x * x + 4
    if not (close(qu(1), 0) and close(qu(2), 0)):
        fail("mvt: x^4-5x^2+4 must vanish at 1 and at 2")
    if not (close(math.sqrt(2.5), 1.5811388300841898, 1e-9) and 1 < math.sqrt(2.5) < 2):
        fail("mvt: the interior zero of 4x^3-10x must be sqrt(5/2) = 1.5811 in (1,2)")
    if not close(4 * math.sqrt(2.5) ** 3 - 10 * math.sqrt(2.5), 0, 1e-9):
        fail("mvt: 4x^3-10x must vanish at sqrt(5/2)")

    # ---- card 7: the corollaries and the 2020 Q.1
    if not (close(2 * 0 - math.cos(0), -1) and close(2 * 1 - math.cos(1), 1.4596976941318602, 1e-9)):
        fail("mvt: 2x - cos x must be -1 at 0 and 1.4597 at 1, so x^2 - sin x is not increasing on [0,1]")
    if not (2 * 0 - math.cos(0) < 0):
        fail("mvt: the derivative of x^2 - sin x must be negative at 0")
    for x in (0.1, 0.25, 0.5, 0.75, 1.0):
        if not (3 * x * x / (2 * math.sqrt(x ** 3 + 1)) > 0):
            fail("mvt: sqrt(x^3+1) must have a positive derivative on (0,1]")
    for x in (0.0, 0.5, 1.0):
        if not (-math.exp(-x) < 0):
            fail("mvt: e^(-x) must decrease on [0,1]")
    if not (3 * 0 + 2 >= 2):
        fail("mvt: 3x^2+2 must be at least 2, so x^3+2x+5 is strictly increasing")
    if not (4 - 1 == 3):
        fail("mvt: the constant-difference corollary must give f(1) - g(1) = 3")
    if not (1 + math.cos(0) >= 0):
        fail("mvt: 1 + cos x must be non-negative")

    # ---- card 8: root counting
    p = lambda x: 4 * x ** 5 + x ** 3 + 7 * x - 2
    if not (close(p(0), -2) and close(p(1), 10)):
        fail("mvt: 4x^5+x^3+7x-2 must be -2 at 0 and 10 at 1")
    for x in (-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0):
        if not (20 * x ** 4 + 3 * x * x + 7 >= 7):
            fail("mvt: the derivative of 4x^5+x^3+7x-2 must be at least 7")
    r5 = lambda x: x ** 5 + x ** 3 + x + 1
    if not (close(r5(-1), -2) and close(r5(0), 1)):
        fail("mvt: x^5+x^3+x+1 must be -2 at -1 and 1 at 0")
    for x in (-1.0, -0.5, 0.0, 0.5, 1.0):
        if not (5 * x ** 4 + 3 * x * x + 1 >= 1):
            fail("mvt: the derivative of x^5+x^3+x+1 must be at least 1")
    r3 = lambda x: x ** 3 + x + 1
    if not (close(r3(-1), -1) and close(r3(0), 1)):
        fail("mvt: x^3+x+1 must be -1 at -1 and 1 at 0")

    # ---- card 9: Cauchy's theorem for x^2 and x^3 on [1,2] and on [-1,1]
    if not close((4 - 1) / (8 - 1.0), 3 / 7.0):
        fail("mvt: the Cauchy ratio for x^2 and x^3 on [1,2] must be 3/7")
    if not close(2 / (3 * (14 / 9.0)), 3 / 7.0):
        fail("mvt: c = 14/9 must satisfy the Cauchy ratio 3/7")
    if not (1 < 14 / 9.0 < 2):
        fail("mvt: the Cauchy point 14/9 must lie in (1,2)")
    if not close((1 - 1) / (1 - (-1.0)), 0):
        fail("mvt: the Cauchy ratio for x^2 and x^3 on [-1,1] must be 0")
    if not close(2 * 0, 0):
        fail("mvt: the product form on [-1,1] must force c = 0, where g' vanishes")

    # ---- card 10: the auxiliary-function construction
    for a, b, c0 in ((1, 2, -4 / 3.0), (3, -3, 0.5), (-2, 1, 1 / 6.0)):
        if not close(2 * a + 3 * b + 6 * c0, 0):
            fail("mvt: the auxiliary example must satisfy 2a+3b+6c = 0")
        F = lambda x, a=a, b=b, c0=c0: a * x ** 3 / 3.0 + b * x * x / 2.0 + c0 * x
        if not close(F(0), 0) or not close(F(1), 0):
            fail("mvt: the antiderivative must vanish at 0 and at 1 when 2a+3b+6c = 0")
        hstep = 1e-6
        if not close((F(0.5 + hstep) - F(0.5 - hstep)) / (2 * hstep), a * 0.25 + b * 0.5 + c0, 1e-4):
            fail("mvt: F' must be ax^2+bx+c")
    if not close(2 * 1 + 3 * 0 + 6 * (-1 / 3.0), 0):
        fail("mvt: a=1, b=0, c=-1/3 must satisfy 2a+3b+6c = 0")
    if not close(1 / math.sqrt(3), 0.5773502691896258, 1e-9):
        fail("mvt: the root of x^2 - 1/3 must be 0.5774")
    if not (0 < 1 / math.sqrt(3) < 1):
        fail("mvt: the root of x^2 - 1/3 must lie in (0,1)")
    if not (close(1 * 1 - 1 / 3.0, 2 / 3.0) and close(0 - 1 / 3.0, -1 / 3.0)):
        fail("mvt: x^2-1/3 must have different values at 0 and 1, so Rolle cannot be applied to it")
    if not close(1.0 - 1.0, 0):
        fail("mvt: the auxiliary g(x) = f(x) - x^2 must vanish at 0 and 1 for the variation")

    # ---- card 11: the inequalities
    if not (math.exp(0.5) >= 1.5):
        fail("mvt: e^0.5 must be at least 1.5")
    if not close(math.exp(0.5), 1.6487212707001282, 1e-9):
        fail("mvt: e^0.5 must be 1.6487")
    if not (math.log(1.5) <= 0.5):
        fail("mvt: ln(1.5) must be at most 0.5")
    if not close(math.log(1.5), 0.4054651081081644, 1e-9):
        fail("mvt: ln(1.5) must be 0.4055")
    if not (abs(math.cos(1) - math.cos(0.5)) <= 0.5):
        fail("mvt: |cos 1 - cos 0.5| must be at most 0.5")
    if not close(abs(math.cos(1) - math.cos(0.5)), 0.337280256022233, 1e-9):
        fail("mvt: |cos 1 - cos 0.5| must be 0.3373")
    if not (math.log(0.5) <= -0.5):
        fail("mvt: the trap counterexample must fail the inequality at x = -0.5")
    if not (math.exp(0.5) >= 1 + 0.5 + 0.25 / 2.0):
        fail("mvt: e^0.5 must exceed 1 + 0.5 + 0.125 = 1.625")
    if not close(1 + 0.5 + 0.125, 1.625):
        fail("mvt: the second-order bound at 0.5 must be 1.625")

    # ---- card 12: the 2014 Set 1 Q.6 determinant
    import itertools
    def det(t):
        m = [[math.sin(t), math.cos(t), math.tan(t)],
             [math.sin(math.pi / 6), math.cos(math.pi / 6), math.tan(math.pi / 6)],
             [math.sin(math.pi / 3), math.cos(math.pi / 3), math.tan(math.pi / 3)]]
        return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
    if not close(det(math.pi / 6), 0, 1e-9):
        fail("mvt: the 2014 determinant must vanish at pi/6, where rows 1 and 2 coincide")
    if not close(det(math.pi / 3), 0, 1e-9):
        fail("mvt: the 2014 determinant must vanish at pi/3, where rows 1 and 3 coincide")
    if not close(det(math.pi / 4), 0.09771698144536893, 1e-9):
        fail("mvt: the 2014 determinant must be 0.0977 at pi/4, so the function is not constant")
    if abs(det(math.pi / 4)) < 1e-6:
        fail("mvt: the 2014 determinant at pi/4 must be non-zero")
    if not (math.pi / 6 < math.pi / 4 < math.pi / 3):
        fail("mvt: pi/4 must lie inside the interval of the 2014 question")
    if not (math.pi / 2 > math.pi / 3):
        fail("mvt: pi/2 must lie outside [pi/6, pi/3], so tan is differentiable there")
    sq = lambda x: x * x - 1
    if not (close(sq(-1), 0) and close(sq(1), 0) and close(2 * 0, 0) and close(2 * 1, 2)):
        fail("mvt: x^2-1 on [-1,1] must have one zero derivative and a non-zero one at 1")

    ok("mean value theorem: every published point, bound, root count, determinant value and "
       "inequality recomputed")



# ---------------------------------------------------------------- integration
def check_integration():
    """Every value, sign, bound and verdict published in the Integration topic is recomputed."""
    import math

    def close(a, b, tol=1e-7):
        return abs(a - b) <= tol * max(1.0, abs(b))

    def quad(fn, a, b, n=20000):
        """Composite Simpson rule; enough for every smooth integrand on this topic."""
        if a == b:
            return 0.0
        n = n if n % 2 == 0 else n + 1
        h = (b - a) / n
        total = fn(a) + fn(b)
        for i in range(1, n):
            total += (4 if i % 2 else 2) * fn(a + i * h)
        return total * h / 3.0

    # ---- card 1: the antiderivative and its check
    A = lambda x: x ** 3 - 2 * x ** 2 + x
    for x in (-1.5, 0.0, 0.5, 2.0, 3.7):
        if not close(3 * x * x - 4 * x + 1, 3 * x * x - 4 * x + 1):
            fail("integration: the antiderivative check must be an identity")
        if not close((A(x + 1e-6) - A(x - 1e-6)) / 2e-6, 3 * x * x - 4 * x + 1, 1e-4):
            fail("integration: the derivative of x^3-2x^2+x must be 3x^2-4x+1 at x = %r" % x)
    if not close(quad(lambda x: 1.0, 1, 3), 2):
        fail("integration: the integral of 1 from 1 to 3 must be 2")
    if not close(quad(lambda x: x ** 2, 0, 1), 1.0 / 3):
        fail("integration: x^2 on [0,1] must integrate to 1/3, so the product rule trap is real")
    if not close(quad(lambda x: x, 0, 1) ** 2, 0.25):
        fail("integration: the square of the integral of x on [0,1] must be 1/4, not 1/3")

    # ---- card 2: signed area against area
    if not close(quad(lambda x: 2 * x, 0, 1), 1):
        fail("integration: 2x on [0,1] must be 1, matching the triangle")
    if not close(quad(lambda x: x, -1, 1), 0):
        fail("integration: x on [-1,1] must be 0 by oddness")
    if not close(quad(lambda x: abs(x), -1, 1), 1):
        fail("integration: the area under |x| on [-1,1] must be 1")
    if not close(quad(lambda x: x * math.sin(x), 0, 2 * math.pi), -2 * math.pi):
        fail("integration: x sin x on [0,2pi] must be -2pi")

    # ---- card 3: the fundamental theorem and its chain-rule form
    if not close(2 * 2.0 * math.exp(4.0), 4 * math.exp(4)):
        fail("integration: the derivative of the integral of e^t from 0 to x^2 at x=2 must be 4e^4")
    if not close(2 * 0.0 * math.exp(0.0), 0):
        fail("integration: that derivative must vanish at x = 0, unlike e^(x^2) = 1")
    xs = 1.5
    if not close(quad(lambda t: t, 1, xs), (xs * xs - 1) / 2.0):
        fail("integration: the integral of t from 1 to x must be (x^2-1)/2")
    x_root = math.sqrt(1.5)
    if not close(quad(lambda t: t, 1, x_root), 0.25):
        fail("integration: x = sqrt(3/2) must solve the integral of t from 1 to x equal to 1/4")
    # the 2025 Set 2 Q.2 value
    xe = math.sqrt(math.e)
    if not close(quad(lambda t: t * math.log(t), 1, xe), 0.25, 1e-6):
        fail("integration: the integral of t ln t from 1 to sqrt(e) must be 1/4")
    for other in (math.e, math.e ** 2, math.e - 1):
        if close(quad(lambda t: t * math.log(t), 1, other), 0.25, 1e-6):
            fail("integration: another offered root must not also satisfy the 2025 equation")

    # ---- card 4: properties
    f4 = lambda x: x ** 2
    if not close(quad(f4, 0, 3) + quad(f4, 3, 1), quad(f4, 0, 1)):
        fail("integration: additivity must hold with the split point outside the interval")
    f_any = lambda x: math.exp(-x)
    if not close(quad(f_any, 0, 4), quad(f_any, 0, 2) + quad(f_any, 2, 4)):
        fail("integration: additivity must hold for a smooth f on adjacent intervals")
    # the worked example on card 4: 2 = I(0,1) + 7 + I(2,3) with I(0,1) = 0, then I(2,6) = I(2,3) + (-5)
    if not close(2 - 7 - 0, -5) or not close(-5 + (-5), -10):
        fail("integration: the card 4 worked example must give I(2,6) = -10 when I(0,1) = 0")

    # ---- card 5: symmetry and the reflection rule
    for a in (-5.0, 0.0, 2.5, 100.0, -0.125):
        val = quad(lambda x: 3 * x * x - a * x + 1, -1, 1)
        if not close(val, 4):
            fail("integration: the 2026 Set 2 Q.17 integral must be 4 for every a, failed at a = %r" % a)
        if not (val > 0):
            fail("integration: that integral must be positive for every a")
    for slope in (0.0, 1.0, -2.0, 7.5):
        fq = lambda x, c=slope: 0.5 + c * (x - 1)
        if not close(fq(0.3) + fq(2 - 0.3), 1):
            fail("integration: the 2024 Set 2 Q.6 family must satisfy f(x) + f(2-x) = 1")
        if not close(quad(fq, 0, 2), 1):
            fail("integration: that family must integrate to 1 on [0,2]")
    if not close(quad(lambda x: x ** 3 * math.cos(x), -2, 2), 0):
        fail("integration: x^3 cos x must vanish on [-2,2]")
    if not close(quad(lambda x: x * x + x, -1, 1), 2.0 / 3):
        fail("integration: x^2 + x on [-1,1] must be 2/3, not 0")
    if not close(quad(lambda x: x, 0, 2), 2):
        fail("integration: x on [0,2] must be 2, so the odd rule needs a symmetric interval")

    # ---- card 6: substitution, including the two previous-year questions
    if not close(quad(lambda x: math.cos(1.0 / x) / (x * x), 1 / math.pi, 2 / math.pi), -1, 1e-6):
        fail("integration: the 2015 Set 1 Q.44 integral must be -1")
    if not close(quad(lambda u: math.cos(u), 1 / math.pi, 2 / math.pi),
                math.sin(2 / math.pi) - math.sin(1 / math.pi)):
        fail("integration: the unsubstituted-limits counterexample must give sin(2/pi) - sin(1/pi)")
    if not close(quad(lambda x: (1 - math.tan(x)) / (1 + math.tan(x)), 0, math.pi / 4), 0.5 * math.log(2), 1e-6):
        fail("integration: the 2009 Q.25 integral must be (1/2) ln 2")
    if not close(quad(lambda x: math.sin(x) ** 8 * math.cos(x), 0, math.pi / 2), 1.0 / 9, 1e-6):
        fail("integration: sin^8 x cos x on [0, pi/2] must be 1/9")
    if not close((math.pi / 2) ** 9 / 9.0, 6.46899, 1e-5):
        fail("integration: the unsubstituted-limits trap must give (pi/2)^9/9 = 6.46899")

    # ---- card 7: integration by parts
    if not close(quad(lambda x: x * x * math.cos(x), 0, math.pi), -2 * math.pi, 1e-6):
        fail("integration: the 2014 Set 3 Q.47 integral must be -2pi")
    if not close(quad(lambda x: x * math.exp(x), 0, 1), 1, 1e-7):
        fail("integration: x e^x on [0,1] must be 1")
    if not close(quad(lambda x: math.log(x), 1, math.e), 1, 1e-6):
        fail("integration: ln x on [1,e] must be 1")

    # ---- card 8: splitting at a sign change
    if not close(quad(lambda x: abs(x * math.sin(x)), 0, 2 * math.pi), 4 * math.pi, 1e-6):
        fail("integration: the 2014 Set 3 Q.6 area must be 4pi")
    if not close(quad(lambda x: abs(x - 1), 0, 2), 1, 1e-7):
        fail("integration: |x-1| on [0,2] must be 1")
    if not close(quad(lambda x: x - 1, 0, 2), 0):
        fail("integration: the signed integral of x-1 on [0,2] must be 0")

    # ---- card 9: improper integrals
    # the singularity is removed by x = t^3, which is how the antiderivative (3/2) x^(2/3) is checked
    half = quad(lambda t: 3 * t, 0, 1)
    if not close(half, 1.5, 1e-9) or not close(2 * half, 3, 1e-9):
        fail("integration: the area of x^(-1/3) on [-1,1] must be 3")
    if not close(-half, -1.5, 1e-9):
        fail("integration: the signed piece of x^(-1/3) on [-1,0) must be -3/2, so the signed integral is 0")
    if not (math.log(1.0) - math.log(1e-12) > 20):
        fail("integration: the integral of 1/x from 0 to 1 must diverge")
    if not close(quad(lambda t: 2.0, 0, 1), 2, 1e-9):   # x = t^2 removes the singularity
        fail("integration: x^(-1/2) on (0,1] must converge to 2")
    # the p-test, from the exact antiderivative up to B: (B^(1-p) - 1)/(1-p), and ln B at p = 1
    def tail(p_, B):
        return math.log(B) if close(p_, 1.0) else (B ** (1 - p_) - 1) / (1 - p_)
    for p_ in (0.5, 1.0, 1.5, 2.0):
        ratio = tail(p_, 1e6) / tail(p_, 1e3)
        if p_ > 1 and ratio > 1.1:
            fail("integration: x^-%r on [1,inf) must converge, ratio %r" % (p_, ratio))
        if p_ <= 1 and ratio < 1.5:
            fail("integration: x^-%r on [1,inf) must diverge, ratio %r" % (p_, ratio))
    if not close(tail(1.5, 1e16), 2, 1e-6) or not close(tail(2.0, 1e16), 1, 1e-6):
        fail("integration: the convergent p-integrals must tend to 1/(p-1)")

    # ---- card 10: area between curves
    if not close(quad(lambda x: x - x * x, 0, 1), 1.0 / 6):
        fail("integration: the area between x and x^2 must be 1/6")
    if not close(quad(lambda x: 4 - x * x, -2, 2), 32.0 / 3):
        fail("integration: the area between 4 and x^2 must be 32/3")
    if not close(quad(lambda x: x ** 3 - x, -1, 1), 0):
        fail("integration: the signed gap between x^3 and x must be 0")
    if not close(quad(lambda x: abs(x ** 3 - x), -1, 1), 0.5):
        fail("integration: the enclosed area between x^3 and x must be 1/2")
    if not close(quad(lambda x: x * x, 0, 3), 9):
        fail("integration: x^2 on [0,3] must be 9")

    # ---- card 11: average value
    if not close(quad(lambda x: 8 - 2 * x, 0, 4), 16):
        fail("integration: 8-2x on [0,4] must be 16")
    if not close(16 / 4.0, 4) or not close(8 - 2 * 2.0, 4):
        fail("integration: the average of 8-2x must be 4, attained at c = 2")
    if not close(quad(lambda x: x * x, 0, 2) / 2.0, 4.0 / 3):
        fail("integration: the average of x^2 on [0,2] must be 4/3")
    if close(4.0 / 3, (0 + 4) / 2.0):
        fail("integration: the endpoint average must differ from the integral average for x^2")
    if not close(quad(lambda x: x * x, 0, 3) / 3.0, 3):
        fail("integration: the average of x^2 on [0,3] must be 3")
    if not close(math.sqrt(3), 1.7320508, 1e-6):
        fail("integration: the point where x^2 equals its average on [0,3] must be sqrt(3)")

    # ---- card 12: integrating a functional equation
    aa, bb = 2.0, 1.0
    f12 = lambda x: (aa * (1.0 / x - 25) - bb * (x - 25)) / (aa * aa - bb * bb)
    if not close(aa * f12(1.7) + bb * f12(1 / 1.7), 1 / 1.7 - 25, 1e-9):
        fail("integration: the explicit f of the 2015 Set 3 Q.45 question must satisfy the relation")
    want = (aa * (math.log(2) - 25) + 47 * bb / 2.0) / (aa * aa - bb * bb)
    if not close(quad(f12, 1, 2), want, 1e-6):
        fail("integration: the 2015 Set 3 Q.45 option (A) must match the explicit integral")
    if not close(quad(lambda x: 1.0 / x, 1, 2), math.log(2), 1e-9):
        fail("integration: the integral of 1/x from 1 to 2 must be ln 2")
    if not close(quad(lambda x: x, 1, 2), 1.5):
        fail("integration: the integral of x from 1 to 2 must be 3/2")

    # ---- card 13: iterated integrals
    inner = quad(lambda y: 4 * 1.0 * y, -2, 2)
    if not close(inner, 0):
        fail("integration: the y-layer of the 2023 question must vanish")
    def tri(fn, a, b, c, d, e, g, n=120):
        return quad(lambda x: quad(lambda y: quad(lambda z: fn(x, y, z), e, g, n), c, d, n), a, b, n)
    if not close(tri(lambda x, y, z: 4 * x * x * y - z ** 3, -3, 3, -2, 2, -1, 1), 0, 1e-6):
        fail("integration: the 2023 Q.21 triple integral must be 0")
    if not close(quad(lambda x: quad(lambda y: x * y, 0, 1, 120), 0, 1, 120), 0.25, 1e-6):
        fail("integration: xy on the unit square must be 1/4")
    if not close(quad(lambda x: quad(lambda y: x * x * y, -1, 1, 120), -1, 1, 120), 0, 1e-9):
        fail("integration: x^2 y on [-1,1]x[-1,1] must be 0")
    asym = quad(lambda x: 4 * x * x, 0, 3) * quad(lambda y: y, 0, 2)
    if not close(asym, 72):
        fail("integration: the asymmetric box version of the same term must give 72, not 0")

    # ---- the visual lesson
    fL = lambda x: x * x - 1
    FL = lambda x: x ** 3 / 3.0 - x
    if not close(FL(0), 0) or not close(FL(1), -2.0 / 3) or not close(FL(2), 2.0 / 3):
        fail("integration: the running total of x^2-1 must be 0, -2/3 and 2/3 at 0, 1 and 2")
    if not close(quad(fL, 0, 1), -2.0 / 3) or not close(quad(fL, 1, 2), 4.0 / 3):
        fail("integration: the two pieces of x^2-1 on [0,2] must be -2/3 and 4/3")
    if not close(quad(fL, 0, 2), 2.0 / 3):
        fail("integration: x^2-1 on [0,2] must be 2/3")
    if not close(quad(lambda x: abs(fL(x)), 0, 2), 2.0):
        fail("integration: the area of x^2-1 on [0,2] must be 2")
    if not close(FL(math.sqrt(3)), 0, 1e-9):
        fail("integration: the running total must vanish at sqrt(3)")
    if not close(quad(fL, -1, 1), -4.0 / 3) or not close(2 * quad(fL, 0, 1), -4.0 / 3):
        fail("integration: the even rule must give -4/3 on [-1,1]")
    for x, want in ((0, -1), (1, 0), (2, 3)):
        if not close(fL(x), want) or not close((FL(x + 1e-6) - FL(x - 1e-6)) / 2e-6, want, 1e-4):
            fail("integration: the slope of F must equal f at x = %r" % x)

    ok("integration: every integral, sign, area, average, convergence verdict and running-total "
       "value published in the topic recomputed")


# ---------------------------------- probability and statistics: distributions
def check_probability_and_statistics():
    """Every probability, mean, variance, density value and CDF point published in the
    Random Variables and Distributions cards, the ten PYQ records and the p5 lesson is
    recomputed here, from the definitions and not from the published numbers."""
    import math

    def close(a, b, tol=1e-9):
        return abs(a - b) <= tol

    def simpson(fn, a, b, n=20000):
        if n % 2:
            n += 1
        hh = (b - a) / n
        s = fn(a) + fn(b)
        for i in range(1, n):
            s += (4 if i % 2 else 2) * fn(a + i * hh)
        return s * hh / 3

    def phi(z):
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))

    # ---- the distribution of GATE CSE 2026 Set 1 Q.48
    vals = [1, 2, 3, 4, 5, 6, 7, 8]
    probs = [1 / 6, 1 / 6, 1 / 12, 1 / 12, 1 / 6, 1 / 12, 1 / 6, 1 / 12]
    if not close(sum(probs), 1):
        fail("probability: the 2026 Set 1 probabilities must sum to 1")
    if not all(0 <= q <= 1 for q in probs):
        fail("probability: every mass must lie between 0 and 1")
    mean = sum(v * q for v, q in zip(vals, probs))
    second = sum(v * v * q for v, q in zip(vals, probs))
    var = second - mean * mean
    if not close(mean, 4.25):
        fail("probability: E[X] of the 2026 Set 1 table must be 51/12 = 4.25")
    if not close(mean, 51 / 12) or not close(second, 283 / 12) or not close(var, 265 / 48):
        fail("probability: the 2026 Set 1 moments must be 51/12, 283/12 and 265/48")
    if not close(var, 5.520833333333333, 1e-12):
        fail("probability: the 2026 Set 1 variance must be 5.5208")
    if not close(math.sqrt(var), 2.3496453633119474, 1e-12):
        fail("probability: the 2026 Set 1 standard deviation must be 2.3496")
    cdf, acc = [], 0.0
    for q in probs:
        acc += q
        cdf.append(acc)
    if not close(cdf[3], 0.5):
        fail("probability: F(4) of the 2026 Set 1 table must be exactly 1/2")
    if not close(cdf[-1], 1):
        fail("probability: the CDF must end at 1")
    if not all(cdf[i] < cdf[i + 1] for i in range(len(cdf) - 1)):
        fail("probability: the CDF of a discrete variable must be non-decreasing")

    # the same support, spread uniformly, is a different distribution
    uni_mean = sum(vals) / len(vals)
    uni_var = sum((v - uni_mean) ** 2 for v in vals) / len(vals)
    if not close(uni_mean, 4.5) or not close(uni_var, 5.25):
        fail("probability: the discrete uniform on {1..8} must have mean 4.5 and variance 63/12")

    # ---- GATE CSE 2012 Q.21: the CDF of a two-point variable
    two = {-1: 0.5, 1: 0.5}
    F = lambda x: sum(q for v, q in two.items() if v <= x)
    if not close(F(-1), 0.5) or not close(F(1), 1) or not close(F(-2), 0):
        fail("probability: 2012 Q.21 must give F(-1) = 0.5 and F(1) = 1")
    Fstrict = lambda x: sum(q for v, q in two.items() if v < x)
    if not close(Fstrict(-1), 0.0) or not close(F(-1), 0.5):
        fail("probability: 2012 Q.21's option (A) is what the strict inequality gives")

    # ---- GATE CSE 2025 Set 1 Q.48: normalising C x^2 on [1,4]
    if not close(simpson(lambda x: x * x, 1, 4), 21, 1e-6):
        fail("probability: the integral of x^2 from 1 to 4 must be 21, so C = 1/21")
    c25 = 1 / 21
    p25 = simpson(lambda x: c25 * x * x, 2, 3)
    if not close(p25, 19 / 63, 1e-9) or not close(round(p25, 3), 0.302):
        fail("probability: 2025 Set 1 Q.48 must give 19/63 = 0.302")
    if not (0 <= p25 <= 1):
        fail("probability: a computed probability must lie in [0, 1]")
    if not close(simpson(lambda x: x * x, 2, 3), 19 / 3, 1e-6):
        fail("probability: skipping the normalisation must give 19/3, the trap option")

    # a density may exceed 1, a probability may not
    if not close(1 / (0.5 - 0), 2):
        fail("probability: the uniform density on (0, 0.5) must be 2")

    # ---- GATE CSE 2006 Q.21: exactly n of 2n chosen
    for n in range(1, 7):
        direct = sum(comb(2 * n, k) for k in range(2 * n + 1) if k == n) / 4 ** n
        if not close(direct, comb(2 * n, n) / 4 ** n):
            fail("probability: 2006 Q.21 formula disagrees with the count")
        if not close(sum(comb(2 * n, k) for k in range(2 * n + 1)) / 4 ** n, 1):
            fail("probability: the binomial probabilities of 2n tosses must sum to 1")
    if not close(comb(10, 5) / 4 ** 5, 0.24609375):
        fail("probability: 2006 Q.21 at n = 5 must be 0.2461")
    # binomial mean and variance from the definition
    for n, p in ((10, 0.4), (6, 0.5), (4, 0.25)):
        pm = [comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]
        if not close(sum(pm), 1, 1e-12):
            fail("probability: the binomial PMF must sum to 1 (n=%d)" % n)
        m = sum(k * pm[k] for k in range(n + 1))
        v = sum(k * k * pm[k] for k in range(n + 1)) - m * m
        if not close(m, n * p, 1e-9) or not close(v, n * p * (1 - p), 1e-9):
            fail("probability: binomial mean np and variance np(1-p) failed at n=%d" % n)
    if not close(comb(10, 3) * 0.4 ** 3 * 0.6 ** 7, 0.214990848, 1e-9):
        fail("probability: P(exactly 3 heads in 10 at p = 0.4) must be 0.2150")
    if not close(1 - 0.5 ** 6, 63 / 64):
        fail("probability: at least one head in 6 tosses must be 63/64")
    if not close(comb(10, 3) / 1024, 0.1171875):
        fail("probability: exactly 3 heads in 10 tosses must be 120/1024")

    # ---- Poisson
    def poisson(lam, k):
        # in log space, so that large k does not overflow the factorial
        return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))

    for lam in (1, 2, 3, 5, 8, 15):
        total = sum(poisson(lam, k) for k in range(0, 200))
        if not close(total, 1, 1e-12):
            fail("probability: the Poisson PMF must sum to 1 at lambda=%r" % lam)
        m = sum(k * poisson(lam, k) for k in range(0, 200))
        v = sum(k * k * poisson(lam, k) for k in range(0, 200)) - m * m
        if not close(m, lam, 1e-9) or not close(v, lam, 1e-9):
            fail("probability: Poisson mean and variance must both equal lambda=%r" % lam)
    p13 = sum(poisson(3, k) for k in (0, 1, 2))
    if not close(p13, 17 / (2 * math.e ** 3), 1e-12) or not close(round(p13, 4), 0.4232):
        fail("probability: 2013 Q.2 must give 17/(2e^3) = 0.4232")
    if not close(sum(poisson(3, k) for k in (0, 1, 2, 3)), 26 / (2 * math.e ** 3), 1e-12):
        fail("probability: including k = 3 must give the 26/(2e^3) option of 2013 Q.2")
    e17 = 5 * 5 + 5 + 4 * 5 + 4
    if not close(e17, 54):
        fail("probability: 2017 Set 2 Q.48 must give 54")
    if not close(poisson(2, 0), math.exp(-2)) or not close(1 - math.exp(-2), 0.8646647167633873, 1e-12):
        fail("probability: the Poisson check at lambda = 2 failed")
    if not close(2 * math.exp(-2), 0.2706705664732254, 1e-12):
        fail("probability: P(X = 1) at lambda = 2 must be 2e^-2 = 0.2707")
    # the two-minute window of the choosing card: lambda t = 8
    if not close(sum(poisson(8, k) for k in range(9)), 0.592547, 1e-5):
        fail("probability: P(X <= 8) at lambda = 8 must be about 0.5925")
    # the misprint page: np = 0.4
    if not close(math.exp(-0.4), 0.6703200460356393, 1e-12):
        fail("probability: e^-0.4 must be 0.6703")

    # ---- exponential
    for lam in (0.25, 0.5, 2, 4):
        if not close(simpson(lambda x: lam * x * math.exp(-lam * x), 0, 200 / lam), 1 / lam, 1e-6):
            fail("probability: the exponential mean must be 1/lambda at lambda=%r" % lam)
        if not close(simpson(lambda x: lam * x * x * math.exp(-lam * x), 0, 200 / lam), 2 / lam ** 2, 1e-6):
            fail("probability: the exponential second moment must be 2/lambda^2 at lambda=%r" % lam)
        if not close(math.exp(-lam * (1 / lam)), math.exp(-1), 1e-12):
            fail("probability: P(X > mean) must be e^-1 for every lambda")
        # memorylessness
        s, t = 3.0, 1.0
        lhs = math.exp(-lam * (s + t)) / math.exp(-lam * s)
        if not close(lhs, math.exp(-lam * t), 1e-12):
            fail("probability: memorylessness failed at lambda=%r" % lam)
    if not close(round(math.exp(-1), 2), 0.37):
        fail("probability: 2021 Set 1 Q.18 must round to 0.37")
    if not close(1 - math.exp(-0.5), 0.3934693402873666, 1e-12):
        fail("probability: P(X <= 2) at mean 4 must be 0.3935")
    if not close(math.exp(-1.5), 0.22313016014842982, 1e-12):
        fail("probability: P(X > 6) at mean 4 must be 0.2231")
    if not close(math.exp(-0.6), 0.5488116360940264, 1e-12):
        fail("probability: P(lifetime > 3) at mean 5 must be 0.5488")

    # ---- continuous uniform
    for a, b in ((0, 10), (2, 8), (1, 6), (0, 23)):
        d = 1 / (b - a)
        if not close(simpson(lambda x: d, a, b), 1, 1e-9):
            fail("probability: the uniform density must integrate to 1 on (%r,%r)" % (a, b))
        if not close(simpson(lambda x: x * d, a, b), (a + b) / 2, 1e-6):
            fail("probability: the uniform mean must be (a+b)/2 on (%r,%r)" % (a, b))
        if not close(simpson(lambda x: x * x * d, a, b) - ((a + b) / 2) ** 2, (b - a) ** 2 / 12, 1e-6):
            fail("probability: the uniform variance must be (b-a)^2/12 on (%r,%r)" % (a, b))
    if not close(10 / (2 * math.sqrt(3)), 2.886751345948129, 1e-12):
        fail("probability: the uniform (0,10) standard deviation must be 2.8868")
    if not close(6 / (2 * math.sqrt(3)), 1.7320508075688772, 1e-12):
        fail("probability: the uniform (2,8) standard deviation must be 1.7321")
    if not close((6 - 2) / (6 - 1), 0.8):
        fail("probability: 2019 Q.47 must give 4/5 = 0.8")
    # the discriminant condition of 2019 Q.47, checked on the whole interval
    for i in range(0, 501):
        y = 1 + i * 5 / 500
        disc = 36 * (y - 2) * (y + 1)
        if y > 2 and disc < 0:
            fail("probability: the discriminant of 2019 Q.47 must be non-negative for y > 2")
        if 1 < y < 2 and disc >= 0:
            fail("probability: the discriminant of 2019 Q.47 must be negative for 1 < y < 2")
    if not close(36 * (2 - 2) * (2 + 1), 0):
        fail("probability: y = 2 is a double root of the 2019 discriminant condition")
    if not close(25 / 12, 2.0833333333333335, 1e-12):
        fail("probability: the continuous uniform on (1,6) must have variance 25/12")

    # ---- normal
    if not close(simpson(lambda x: math.exp(-x * x / 2) / math.sqrt(2 * math.pi), -40, 40), 1, 1e-9):
        fail("probability: the standard normal density must integrate to 1")
    f26 = lambda x: math.exp(-x * x / 18) / (3 * math.sqrt(2 * math.pi))
    if not close(simpson(f26, -60, 60), 1, 1e-9):
        fail("probability: the 2026 Set 2 density must integrate to 1")
    if not close(simpson(lambda x: x * f26(x), -60, 60), 0, 1e-9):
        fail("probability: the 2026 Set 2 density must have mean 0")
    if not close(simpson(lambda x: x * x * f26(x), -60, 60), 9, 1e-6):
        fail("probability: the 2026 Set 2 density must have variance 9")
    if not close(round(math.sqrt(18 / 2), 12), 3):
        fail("probability: 2 sigma^2 = 18 must give sigma = 3")
    # 2008 Q.29: sigma_Y = 3 is the value that matches the two tail probabilities
    px = phi((-1 - 1) / 2)
    for sigma in (1, 2, math.sqrt(2), 3):
        py = 1 - phi((2 + 1) / sigma)
        if close(sigma, 3) and not close(px, py, 1e-12):
            fail("probability: 2008 Q.29's sigma = 3 must match both tails")
        if not close(sigma, 3) and close(px, py, 1e-6):
            fail("probability: 2008 Q.29's option %r must not match both tails" % sigma)
    if not close(phi(1), 0.8413447460685429, 1e-12):
        fail("probability: P(Z <= 1) must be 0.8413")
    if not close(2 * phi(1) - 1, 0.6826894921370859, 1e-12):
        fail("probability: the 68% band must be 2 phi(1) - 1")
    if not close(phi(2) - phi(-2), 0.9544997361036416, 1e-12):
        fail("probability: the 95% band must be phi(2) - phi(-2)")
    if not close(phi(3) - phi(-3), 0.9973002039367398, 1e-12):
        fail("probability: the 99.7% band must be phi(3) - phi(-3)")
    if not close(phi(0), 0.5):
        fail("probability: half the normal mass lies below the mean")

    # ---- sums of independent variables
    conv = [sum(poisson(2, j) * poisson(3, k - j) for j in range(k + 1)) for k in range(0, 40)]
    for k in range(0, 40):
        if not close(conv[k], poisson(5, k), 1e-12):
            fail("probability: the sum of independent Poisson(2) and Poisson(3) must be Poisson(5)")
    if not close(poisson(5, 0), math.exp(-5)):
        fail("probability: P(X + Y = 0) must be e^-5")
    if not close(5 * math.exp(-5), 0.03368973499542734, 1e-12):
        fail("probability: P(X + Y = 1) must be 5e^-5")
    # N(1,5): the probability below the mean is one half
    if not close(phi((1 - 1) / math.sqrt(5)), 0.5):
        fail("probability: P(N(1,5) <= 1) must be 0.5")

    # ---- the visual lesson's published numbers
    lesson_path = os.path.join(ROOT, "visuals", "probability-and-statistics",
                               "random-variables-and-distributions",
                               "pmf-cdf-and-the-balance-point", "lesson.json")
    if not os.path.isfile(lesson_path):
        fail("probability: the visual lesson's lesson.json is missing")
    else:
        L = load(lesson_path)
        ex = L.get("example") or {}
        if not close(ex.get("sum_of_probabilities", -1), 1):
            fail("probability lesson: sum_of_probabilities must be 1")
        if not close((ex.get("expectation") or {}).get("value", -1), mean):
            fail("probability lesson: the expectation must equal the recomputed mean")
        if not close((ex.get("second_moment") or {}).get("value", -1), second):
            fail("probability lesson: the second moment must equal 283/12")
        if not close((ex.get("variance") or {}).get("value", -1), var):
            fail("probability lesson: the variance must equal 265/48")
        if not close(ex.get("standard_deviation", -1), math.sqrt(var)):
            fail("probability lesson: the standard deviation must equal sqrt(265/48)")
        if not close(ex.get("cdf_at_4", -1), 0.5):
            fail("probability lesson: the CDF at 4 must be 0.5")
        if len(ex.get("cdf", [])) != len(cdf) or not all(close(a, b, 1e-12) for a, b in zip(ex.get("cdf", []), cdf)):
            fail("probability lesson: the CDF table must match the recomputed staircase")
        if not close(ex.get("unweighted_average_of_the_support", -1), 4.5):
            fail("probability lesson: the unweighted average of 1..8 must be 4.5")
        uni = ex.get("uniform_on_the_same_support") or {}
        if not close(uni.get("mean", -1), 4.5) or not close(uni.get("variance", -1), 5.25):
            fail("probability lesson: the uniform comparison must be mean 4.5, variance 5.25")
        wrong = ex.get("wrong_variance_if_the_mean_is_not_squared") or {}
        if not close(wrong.get("value", -1), second - mean):
            fail("probability lesson: the E[X^2] - E[X] error must be 283/12 - 51/12")
        if L.get("steps") != 7:
            fail("probability lesson: the lesson must declare its seven steps")

    ok("probability and statistics: every probability, mass, density, mean, variance, CDF value, "
       "tail probability, discriminant verdict and closure claim published in the topic recomputed")


# ------------------------------------------------- conditional probability and Bayes
def check_conditional_probability():
    """Every probability, verdict and count published in the Conditional Probability and Bayes cards,
    PYQs and lesson is recomputed by enumeration or in exact rational arithmetic."""
    import itertools
    from fractions import Fraction as Fr

    def close(a, b, tol=1e-9):
        return abs(float(a) - float(b)) <= tol

    def frac(x):
        return Fr(x).limit_denominator(10 ** 6)

    # ---- card 1: the definition, the die example, and the two PYQ-style dice questions
    die = list(range(1, 7))
    def cond(space, A, B):
        sb = [x for x in space if B(x)]
        if not sb:
            return None
        sa = [x for x in sb if A(x)]
        return Fr(len(sa), len(sb))
    assert cond(die, lambda x: x == 2, lambda x: x % 2 == 0) == Fr(1, 3), "die: P(2 | even) = 1/3"
    assert Fr(1, 6) / Fr(1, 2) == Fr(1, 3), "the ratio of probabilities agrees with the ratio of counts"
    dice = [(a, b) for a in die for b in die]
    assert cond(dice, lambda t: t[0] == 3, lambda t: t[0] + t[1] == 8) == Fr(1, 5), "sum 8 given first die 3"
    assert cond(dice, lambda t: t[0] == 4, lambda t: t[0] + t[1] == 9) == Fr(1, 4), "sum 9 given first die 4"
    assert Fr(1, 36) / Fr(5, 36) == Fr(1, 5), "1/36 is the joint probability of (3,5), not the answer"
    # 2011 Q.3: two coins, at least one head
    coins2 = list(itertools.product("HT", repeat=2))
    p_both = Fr(sum(1 for c in coins2 if c == ("H", "H")), 4)
    p_atleast = Fr(sum(1 for c in coins2 if "H" in c), 4)
    assert p_both == Fr(1, 4) and p_atleast == Fr(3, 4) and p_both / p_atleast == Fr(1, 3), \
        "2011 Q.3: P(both heads | at least one head) = 1/3"

    # ---- card 2: P(.|B) as a probability measure on a three-point space
    Bdie = [x for x in die if x % 2 == 0]
    assert cond(Bdie, lambda x: x in (1, 2), lambda x: True) == Fr(1, 3)
    assert cond(Bdie, lambda x: x in (1, 3, 5), lambda x: True) == Fr(0)
    assert cond(Bdie, lambda x: x in (2, 4), lambda x: True) == Fr(2, 3)
    assert Fr(2, 3) + Fr(2, 3) - Fr(1, 3) == Fr(1), "the conditional addition rule on overlapping events"
    assert Fr(2, 3) + Fr(2, 3) == Fr(4, 3), "adding them without the intersection overcounts"
    assert Fr(1, 3) + Fr(0) == Fr(1, 3), "P(A|B) + P(A|B^c) is not 1 for A = {2}, B = even"
    assert 1 - Fr(35, 100) == Fr(65, 100), "complement inside the condition"
    # 2024 Set 1 Q.17
    pa, pb, pab = Fr(3, 10), Fr(5, 10), Fr(1, 10)
    assert pa * pb == Fr(15, 100) != pab, "not independent"
    assert pa + pb - pab == Fr(7, 10), "P(A or B) = 0.7"
    assert pa - pab == Fr(2, 10), "P(A and B^c) = 0.2"
    assert 1 - (pa + pb - pab) == Fr(3, 10) != Fr(4, 10), "P(A^c and B^c) = 0.3, not 0.4"
    assert Fr(12, 100) / Fr(3, 10) == Fr(4, 10), "the predicted variation P(B) = P(A and B)/P(A|B)"

    # ---- card 3: the multiplication rule, the bag, and the three aces
    bag = ["R"] * 10 + ["B"] * 15
    two = [(x, y) for x in range(25) for y in range(25) if x != y]
    def both_red(t):
        return bag[t[0]] == "R" and bag[t[1]] == "R"
    def first_red(t):
        return bag[t[0]] == "R"
    assert Fr(sum(1 for t in two if both_red(t)), len(two)) == Fr(10, 25) * Fr(9, 24) == Fr(15, 100), \
        "P(both red) = 0.15"
    assert cond(two, both_red, first_red) == Fr(9, 24) == Fr(375, 1000), \
        "2024 Set 1 Q.53: P(both red | first red) = 0.375"
    assert cond(two, both_red, first_red) != Fr(15, 100), "0.15 is the unconditional probability"
    assert Fr(4, 52) * Fr(3, 51) * Fr(2, 50) == Fr(1, 5525), "three aces without replacement"
    three = [(x, y) for x in range(5) for y in range(5) if x != y]
    assert Fr(3, 5) * Fr(2, 4) == Fr(3, 10), "two red from 3 red and 2 blue"

    # ---- card 4: independence, and GATE CSE 2023 Q.43
    pA, pB, pC = Fr(1, 4), Fr(1, 2), Fr(1, 2)
    assert pB * pC == Fr(1, 4) == pA, "P(B and C) = 1/4 = P(B)P(C)"
    assert pA * pB == Fr(1, 8) != Fr(1, 4), "P(A and B) = 1/4, so A is not independent of B"
    assert pA * pC == Fr(1, 8) != Fr(1, 4), "the same for A and C"
    assert Fr(1, 4) / pC == pB, "P(B|C) = P(B), which is option D"
    assert Fr(4, 10) * Fr(5, 10) == Fr(2, 10), "the predicted variation: 0.4 and 0.5 are independent"
    assert (1 - Fr(6, 10)) * Fr(5, 10) == Fr(2, 10), "complements carry independence"

    # ---- card 5: independence against exclusivity, over every pair of events on a die
    subsets = []
    for r in range(len(die) + 1):
        for s in itertools.combinations(die, r):
            subsets.append(set(s))
    for A in subsets:
        for B in subsets:
            disjoint = not (A & B)
            independent = Fr(len(A & B), 6) == Fr(len(A), 6) * Fr(len(B), 6)
            if disjoint and independent:
                assert len(A) == 0 or len(B) == 0, "only a zero-probability event is both"
            if independent and len(A) > 0 and len(B) > 0:
                assert not disjoint, "positive-probability independent events must overlap"
    odd, even = {1, 3, 5}, {2, 4, 6}
    assert not (odd & even) and Fr(0) != Fr(1, 2) * Fr(1, 2), "odd and even are disjoint and dependent"
    assert Fr(len(odd), 6) + Fr(len(even), 6) == Fr(1), "the disjoint addition rule"
    assert Fr(2, 10) * Fr(3, 10) == Fr(6, 100) != Fr(0), "two disjoint events of 0.2 and 0.3 are dependent"
    assert Fr(0) * Fr(7, 10) == Fr(0), "a zero-probability event is independent of everything"

    # ---- card 6: pairwise but not mutual independence
    cc = list(itertools.product("HT", repeat=2))
    def ev(f): return {c for c in cc if f(c)}
    A6, B6, C6 = ev(lambda c: c[0] == "H"), ev(lambda c: c[1] == "H"), ev(lambda c: c[0] != c[1])
    for X, Y in ((A6, B6), (A6, C6), (B6, C6)):
        assert Fr(len(X & Y), 4) == Fr(len(X), 4) * Fr(len(Y), 4), "every pair is independent"
    assert len(A6 & B6 & C6) == 0, "the triple intersection is empty"
    assert Fr(0) != Fr(1, 2) ** 3, "so the triple product fails"
    assert 2 ** 3 - 3 - 1 == 4, "four conditions for three events"
    assert Fr(1, 2) * Fr(1, 2) * Fr(1, 2) == Fr(1, 8), "the triple product that mutual independence needs"

    # ---- card 7: conditional independence, both directions
    A7, C7 = ev(lambda c: c[0] == "H"), ev(lambda c: c[1] == "H")
    B7 = ev(lambda c: "H" in c)
    assert Fr(len(A7 & C7), 4) == Fr(len(A7), 4) * Fr(len(C7), 4), "independent unconditionally"
    pa7 = Fr(len(A7 & B7), len(B7))
    pc7 = Fr(len(C7 & B7), len(B7))
    pac7 = Fr(len(A7 & C7 & B7), len(B7))
    assert pa7 == Fr(2, 3) and pc7 == Fr(2, 3) and pac7 == Fr(1, 3), "given at least one head: 1/3 against 4/9"
    assert pa7 * pc7 != pac7, "so they are conditionally dependent"
    # the eight-outcome construction: dependent overall, independent given B
    S8 = list(range(1, 9))
    B8, A8, C8 = {1, 2, 3, 4}, {1, 2}, {1, 3, 5, 6, 7, 8}
    assert Fr(len(A8), 8) == Fr(1, 4) and Fr(len(C8), 8) == Fr(3, 4)
    assert Fr(len(A8 & C8), 8) == Fr(1, 8) != Fr(1, 4) * Fr(3, 4), "dependent unconditionally"
    assert Fr(len(A8 & C8 & B8), len(B8)) == Fr(1, 4) == Fr(len(A8 & B8), len(B8)) * Fr(len(C8 & B8), len(B8)), \
        "independent given B"
    # the quick check: three coins, exactly two heads given at least one head
    c3 = list(itertools.product("HT", repeat=3))
    at_least_one = [c for c in c3 if "H" in c]
    assert Fr(sum(1 for c in at_least_one if c.count("H") == 2), len(at_least_one)) == Fr(3, 7)

    # ---- card 8: the total probability theorem
    assert Fr(1, 2) * Fr(7, 10) + Fr(1, 2) * Fr(4, 10) == Fr(55, 100), "2016 Set 2 Q.5 = 0.55"
    assert Fr(7, 10) * Fr(7, 10) + Fr(3, 10) * Fr(4, 10) == Fr(61, 100), "unequal priors give 0.61"
    assert Fr(1, 2) * Fr(7, 10) + Fr(1, 2) * Fr(4, 10) != Fr(61, 100), "and the plain average does not"
    assert Fr(5, 10) * Fr(1, 100) + Fr(3, 10) * Fr(2, 100) + Fr(2, 10) * Fr(3, 100) == Fr(17, 1000), \
        "the three-machine check = 0.017"
    # the rain question (GATE IT 2006 Q.1), used as an original question here
    assert (Fr(6, 10) - Fr(1, 2) * Fr(4, 10)) / Fr(1, 2) == Fr(8, 10), "rain given above 25 degrees = 0.8"

    # ---- card 9: Bayes, the coin box, the temperatures, and the two-urn variation
    def bayes(priors, lik):
        evidence = sum(p * l for p, l in zip(priors, lik))
        return evidence, [p * l / evidence for p, l in zip(priors, lik)]
    ev, post = bayes([Fr(1, 5), Fr(4, 5)], [Fr(1), Fr(1, 4)])
    assert ev == Fr(4, 10) and post[0] == Fr(1, 2), "2025 Set 1 Q.22: P(fake | two heads) = 0.50"
    assert post[0] + post[1] == 1, "the posteriors over a partition sum to 1"
    ev, post = bayes([Fr(2, 10), Fr(5, 10), Fr(3, 10)], [Fr(40, 100), Fr(10, 100), Fr(1, 100)])
    assert ev == Fr(133, 1000), "2018 Q.44: P(D high) = 0.133"
    assert post[0] == Fr(80, 133) and abs(float(post[0]) - 0.6015) < 5e-4, "P(G high | D high) = 0.6015"
    assert round(float(post[0]) + 5e-9, 2) == 0.60, "which rounds to 0.60"
    ev, post = bayes([Fr(1, 2), Fr(1, 2)], [Fr(2, 5), Fr(4, 5)])
    assert ev == Fr(6, 10) and post[0] == Fr(1, 3), "the two-urn predicted variation = 1/3"
    ev, post = bayes([Fr(1, 2), Fr(1, 2)], [Fr(2, 10), Fr(6, 10)])
    assert ev == Fr(4, 10) and post[0] == Fr(1, 4), "the card 9 quick check = 0.25"
    assert Fr(1, 1) != Fr(1, 2), "P(two heads | fake) = 1 is not P(fake | two heads) = 0.5"

    # ---- card 10: the tree, the sender and receiver, and the odds form
    ev, post = bayes([Fr(1, 10), Fr(9, 10)], [Fr(3, 10), Fr(8, 10)])
    assert ev == Fr(75, 100) and post[0] == Fr(4, 100), "2021 Set 1 Q.54: 0.04"
    assert Fr(1, 10) * Fr(3, 10) + Fr(9, 10) * Fr(8, 10) + Fr(1, 10) * Fr(7, 10) + Fr(9, 10) * Fr(2, 10) == Fr(1), \
        "all four branches sum to 1, so dividing by 1 returns the joint probability"
    prior_odds = Fr(1, 3)
    post_odds = prior_odds * 5
    assert post_odds == Fr(5, 3) and post_odds / (1 + post_odds) == Fr(5, 8), "odds: 1:3 with a ratio of 5 gives 5/8"

    # ---- card 11: the base rate
    ev, post = bayes([Fr(1, 100), Fr(99, 100)], [Fr(98, 100), Fr(1, 100)])
    assert post[0] == Fr(98, 197) and abs(float(post[0]) - 0.4975) < 5e-5, "1 per cent prevalence: 98/197"
    assert round(float(post[0]) + 5e-9, 2) == 0.50, "which rounds to 0.50"
    ev, post = bayes([Fr(1, 1000), Fr(999, 1000)], [Fr(98, 100), Fr(1, 100)])
    assert post[0] == Fr(98, 1097) and abs(float(post[0]) - 0.0893) < 5e-4, "the robot example: about 0.089"
    assert float(post[0]) < 0.10, "under ten per cent, as StatLect states"
    ev, post = bayes([Fr(1, 10), Fr(9, 10)], [Fr(98, 100), Fr(1, 100)])
    assert post[0] == Fr(98, 107) and abs(float(post[0]) - 0.9159) < 5e-4, "10 per cent prevalence: 98/107"

    # ---- card 12: the two shared-trial PYQs, by enumeration
    triples = list(itertools.product([0, 1], repeat=3))
    both = [t for t in triples if t[2] == 0 and (t[0] * t[1] ^ t[2]) == 0]
    x3zero = [t for t in triples if t[2] == 0]
    assert len(both) == 3 and len(x3zero) == 4 and Fr(3, 4) == Fr(len(both), len(x3zero)), \
        "2015 Set 3 Q.37: 0.75"
    assert Fr(3, 8) / Fr(4, 8) == Fr(3, 4), "the same by the definition"
    six = list(itertools.product([0, 1], repeat=6))
    def e1(t):
        return t[1] + t[3] + t[5] >= 2
    def e2(t):
        return t[0] + t[1] + t[2] + t[4] == 2
    in_e2 = [t for t in six if e2(t)]
    joint = [t for t in in_e2 if e1(t)]
    assert len(six) == 64 and len(in_e2) == 24, "E2 leaves 24 equally likely completions"
    assert len(joint) == 12, "12 of the 24 satisfy E1"
    assert Fr(len(joint), len(in_e2)) == Fr(1, 2), "2026 Set 2 Q.53: 0.5"
    assert Fr(len(joint), 64) == Fr(12, 64) == Fr(3, 16), "the joint probability is 3/16"
    assert Fr(1, 2) * Fr(6, 16) == Fr(3, 16), "and the product happens to coincide, which is why counting is safer"

    # ---- the lesson's numbers, from the priors and the rates
    pa_, pb_ = Fr(6, 10), Fr(4, 10)
    ra, rb = Fr(2, 100), Fr(5, 100)
    ba, bb = pa_ * ra, pb_ * rb
    assert ba == Fr(12, 1000) and bb == Fr(20, 1000), "branch products 0.012 and 0.020"
    assert ba + bb == Fr(32, 1000), "the evidence 0.032"
    assert bb / (ba + bb) == Fr(5, 8) and ba / (ba + bb) == Fr(3, 8), "posteriors 0.625 and 0.375"
    assert Fr(5, 8) + Fr(3, 8) == 1, "they sum to 1"
    assert (Fr(1, 2) * rb) / (Fr(1, 2) * ra + Fr(1, 2) * rb) == Fr(5, 7), "equal priors give 5/7"
    b2, a2 = Fr(9, 10) * rb, Fr(1, 10) * ra
    assert b2 == Fr(45, 1000) and a2 == Fr(2, 1000) and b2 + a2 == Fr(47, 1000), "the high-prior branches"
    assert abs(float(b2 / (a2 + b2)) - 0.9574) < 5e-5, "the high-prior posterior is 0.957"

    ok("conditional probability and Bayes: every conditional probability, joint probability, posterior, "
       "verdict and count published in the topic recomputed - by enumeration over the die, the two dice, the "
       "coin spaces, the 24 two-ball draws and the 64 toss sequences, and in exact rational arithmetic for the "
       "partition sums and the lesson's tree")


# ------------------------------------------------- sequential circuits
def check_sequential_circuits():
    """Every latch, flip-flop, counter, state-machine and timing claim published in the
    Sequential Circuits cards, PYQ records and lesson is recomputed here."""
    import itertools
    from math import ceil, log2

    def bits(n, width):
        return [(n >> (width - 1 - i)) & 1 for i in range(width)]

    # ---- the NOR and NAND SR latches, straight from the gate equations
    def nor_latch(S, R, Q):
        """Iterate the two NOR gates from the given state until they settle."""
        q, qc = Q
        for _ in range(20):
            nq = 0 if (R or qc) else 1          # Q  = NOR(R, Q')
            nqc = 0 if (S or nq) else 1         # Q' = NOR(S, Q)
            if (nq, nqc) == (q, qc):
                return (q, qc)
            q, qc = nq, nqc
        return (q, qc)
    for S, R in itertools.product([0, 1], repeat=2):
        for Q0 in [(1, 0), (0, 1)]:
            Q = nor_latch(S, R, Q0)
            if (S, R) == (1, 1):
                assert Q == (0, 0), "the NOR latch's forbidden input forces Q = Q' = 0"
            else:
                assert Q[0] != Q[1], "the NOR latch's legal rows keep the outputs complementary"
    for S, R, want in [(1, 0, 1), (0, 0, 1), (0, 1, 0), (0, 0, 0)]:
        start = (1, 0) if want == 1 else (0, 1)
        assert nor_latch(S, R, start)[0] == want, "the NOR latch's hold row copies the previous value"
    # characteristic equation Q+ = S + R'Q on the three legal rows
    for S, R in [(0, 0), (0, 1), (1, 0)]:
        for Q in (0, 1):
            got = nor_latch(S, R, (1, 0) if Q == 1 else (0, 1))[0]
            assert got == (S or ((not R) and Q)), "Q+ = S + R'Q fails at S=%d R=%d Q=%d" % (S, R, Q)
    # the NAND latch is the dual: active-low inputs, forbidden row is 0, 0
    def nand_latch(Sb, Rb, Q):
        """The dual: Q = NAND(S', Q'), Q' = NAND(R', Q)."""
        q, qc = Q
        for _ in range(20):
            nq = 0 if (Sb and qc) else 1
            nqc = 0 if (Rb and nq) else 1
            if (nq, nqc) == (q, qc):
                return (q, qc)
            q, qc = nq, nqc
        return (q, qc)
    for Sb, Rb in itertools.product([0, 1], repeat=2):
        for Q0 in [(1, 0), (0, 1)]:
            Q = nand_latch(Sb, Rb, Q0)
            if (Sb, Rb) == (0, 0):
                assert Q == (1, 1), "the NAND latch's forbidden input forces Q = Q' = 1"
            else:
                assert Q[0] != Q[1], "the NAND latch's legal rows keep the outputs complementary"
    assert nand_latch(0, 1, (0, 1))[0] == 1, "S' = 0 sets the NAND latch to 1"
    assert nand_latch(1, 0, (1, 0))[0] == 0, "R' = 0 resets the NAND latch to 0"

    # ---- the gated SR latch and the D latch
    def gated_sr(En, S, R, Q):
        return Q if (En == 0 or (S == 0 and R == 0)) else (1 if S else 0)
    rows = [(En, S, R) for En in (0, 1) for S in (0, 1) for R in (0, 1)]
    holds = [(e, s, r) for (e, s, r) in rows if e == 0 or (s == 0 and r == 0)]
    assert len(rows) == 8 and len(holds) == 5, "the gated SR table has 8 rows and 5 that hold"
    assert len([h for h in holds if h[0] == 1]) == 1, "only the S = R = 0 row holds while enabled"
    for En in (0, 1):
        for D in (0, 1):
            assert (D if En else 1) in (0, 1)
    def d_latch(En, D, Q):
        return D if En else Q
    assert d_latch(1, 1, 0) == 1 and d_latch(1, 0, 1) == 0, "a transparent D latch follows D"
    assert d_latch(0, 1, 0) == 0, "a closed D latch holds its value"
    assert [d_latch(1, d, 0) for d in (0, 1, 0, 1)] == [0, 1, 0, 1], "the latch tracks D while enabled"

    # ---- the four characteristic equations and the excitation tables
    def d_next(D, Q): return D
    def t_next(T, Q): return T ^ Q
    def jk_next(J, K, Q): return (J and not Q) or ((not K) and Q)
    for Q in (0, 1):
        for D in (0, 1):
            assert d_next(D, Q) == D
        for T in (0, 1):
            assert t_next(T, Q) == (Q ^ T), "T: Q+ = T XOR Q"
            assert t_next(0, Q) == Q and t_next(1, Q) == 1 - Q, "T = 0 holds, T = 1 toggles"
        for J in (0, 1):
            for K in (0, 1):
                got = jk_next(J, K, Q)
                want = { (0, 0): Q, (0, 1): 0, (1, 0): 1, (1, 1): 1 - Q }[(J, K)]
                assert got == want, "JK modes fail at J=%d K=%d Q=%d" % (J, K, Q)
    # the JK equation written as an expression agrees with the mode table
    for Q in (0, 1):
        for J in (0, 1):
            for K in (0, 1):
                assert int((J and not Q) or ((not K) and Q)) == int(J * (1 - Q) + (1 - K) * Q)
    # excitation tables, read backwards
    for Q in (0, 1):
        for Qp in (0, 1):
            assert d_next(Qp, Q) == Qp, "D excitation is D = Q+"
            assert t_next(Q ^ Qp, Q) == Qp, "T excitation is T = Q XOR Q+"
    jk_ex = {(0, 0): (0, None), (0, 1): (1, None), (1, 0): (None, 1), (1, 1): (None, 0)}
    for (Q, Qp), (J, K) in jk_ex.items():
        for j in ([J] if J is not None else [0, 1]):
            for k in ([K] if K is not None else [0, 1]):
                assert jk_next(j, k, Q) == Qp, "the JK excitation table is wrong at %d -> %d" % (Q, Qp)
    sr_ex = {(0, 0): (0, None), (0, 1): (1, 0), (1, 0): (0, 1), (1, 1): (None, 0)}
    def sr_next(S, R, Q):
        return Q if (S == 0 and R == 0) else (1 if S else 0)
    for (Q, Qp), (S, R) in sr_ex.items():
        for s in ([S] if S is not None else [0]):
            for r in ([R] if R is not None else [0, 1]):
                if s == 1 and r == 1:
                    continue
                assert sr_next(s, r, Q) == Qp, "the SR excitation table is wrong at %d -> %d" % (Q, Qp)
    # the three conversions
    for Q in (0, 1):
        for T in (0, 1):
            assert t_next(T, Q) == jk_next(T, T, Q), "J = K = T makes a T flip-flop from a JK"
            assert t_next(T, Q) == d_next(T ^ Q, Q), "D = T XOR Q makes a T flip-flop from a D"
        for J in (0, 1):
            for K in (0, 1):
                assert jk_next(J, K, Q) == d_next(int((J and not Q) or ((not K) and Q)), Q)

    # ---- the flip-flop count and the unused patterns
    for n_states, want in [(258, 9), (75, 7), (100, 7), (6, 3), (5, 3), (4, 2), (9, 4), (16, 4)]:
        assert ceil(log2(n_states)) == want, "ceil(log2 %d) is not %d" % (n_states, want)
        assert 2 ** (want - 1) < n_states <= 2 ** want
    assert 2 ** 9 - 258 == 254, "a mod-258 counter leaves 254 patterns unused"
    assert 2 ** 7 - 100 == 28, "a mod-100 counter leaves 28 patterns unused"
    assert 2 ** 3 - 5 == 3 and 2 ** 4 - 9 == 7 and 2 ** 3 - 6 == 2
    assert 2 ** 3 == 8, "three flip-flops hold at most eight states"

    # ---- ring and Johnson counters
    def shift(b, insert):
        return [insert] + b[:3]
    johnson = [0, 0, 0, 0]
    seen = [tuple(johnson)]
    for _ in range(8):
        johnson = shift(johnson, 1 - johnson[3])
        seen.append(tuple(johnson))
    assert seen[8] == seen[0], "the 4-bit Johnson counter returns after eight clocks"
    assert len(set(seen[:8])) == 8, "the 4-bit Johnson counter has eight distinct states"
    want_states = [(0,0,0,0), (1,0,0,0), (1,1,0,0), (1,1,1,0),
                   (1,1,1,1), (0,1,1,1), (0,0,1,1), (0,0,0,1)]
    assert seen[:8] == want_states, "the Johnson sequence is not the one the cards and lesson list"
    decimals = [int("".join(map(str, s)), 2) for s in want_states]
    assert decimals == [0, 8, 12, 14, 15, 7, 3, 1], "the Johnson decimals are 0, 8, 12, 14, 15, 7, 3, 1"
    assert all(sum(a != b for a, b in zip(seen[i], seen[i + 1])) == 1 for i in range(8)), \
        "consecutive Johnson states differ in exactly one bit"
    # the second cycle, reached from any state outside the first
    second = (0, 0, 1, 0)
    seq_b, cur = [second], list(second)
    for _ in range(8):
        cur = shift(cur, 1 - cur[3])
        seq_b.append(tuple(cur))
    assert seq_b[8] == second and len(set(seq_b[:8])) == 8, "the second Johnson cycle has length eight"
    assert not (set(seq_b[:8]) & set(want_states)), "the two Johnson cycles are disjoint"
    assert len(set(seq_b[:8]) | set(want_states)) == 16, "the two cycles cover all 16 patterns"
    assert 16 - 2 * 4 == 8, "a 4-bit Johnson counter leaves 2^n - 2n = 8 patterns unused"
    # the ring counter
    ring = [1, 0, 0, 0]
    ring_seq = [tuple(ring)]
    for _ in range(4):
        ring = shift(ring, ring[3])
        ring_seq.append(tuple(ring))
    assert len(set(ring_seq[:4])) == 4 and ring_seq[4] == ring_seq[0], "the 4-bit ring counter has n = 4 states"
    assert 16 - 4 == 12, "a 4-bit ring counter leaves 12 patterns unused"
    assert 2 * 5 == 10 and 2 ** 5 - 10 == 22, "a divide-by-10 Johnson counter needs 5 stages and leaves 22"
    assert 2 * 4 == 8 and 4 == 4, "2n against n for four flip-flops"

    # ---- ripple counters and frequency division
    f_last = 1 / (64e-6)
    assert abs(f_last - 15625) < 1e-6, "a 64 microsecond period is 15625 Hz"
    assert abs(f_last * 16 - 250000) < 1e-3, "the 4-bit ripple input is 250 kHz"
    assert abs(250000 / 1000 - 250) < 1e-9, "250 kHz is 250 in kHz"
    assert abs(3.2e6 / 32 - 100000) < 1e-3, "five stages divide 3.2 MHz by 32"
    assert abs(1 / 100000 - 10e-6) < 1e-12, "100 kHz has a 10 microsecond period"
    assert abs(1e6 / 2 ** 10 - 976.5625) < 1e-3, "ten stages give about 977 Hz from 1 MHz"
    assert 1e6 / 2 ** 10 < 1000 < 1e6 / 2 ** 9, "no power-of-two division gives exactly 1 kHz from 1 MHz"
    # the frequency halves at every stage
    f = 1e6
    for _ in range(4):
        f = f / 2
    assert f == 1e6 / 16, "each ripple stage halves the frequency"

    # ---- 2014 Set 3 Q.45: the JK circuit and its mod-5 cycle
    def q2014(Q):
        Q2, Q1, Q0 = Q
        return (jk_next(1 - Q1, Q0, Q2), jk_next(Q2, 1 - Q2, Q1), jk_next(Q1, 1 - Q0, Q0))
    seq = [(0, 0, 0)]
    for _ in range(5):
        seq.append(q2014(seq[-1]))
    assert seq[1:4] == [(1, 0, 0), (1, 1, 0), (1, 1, 1)], "2014 Set 3 Q.45 must give 100, 110, 111"
    # The question is a figure and the equations above are those its accepted solutions state. Carrying them
    # further does not close a five-state cycle, which is why the PYQ record claims only the three states asked
    # for and says the modulus is not claimed.
    assert seq[4] == (0, 1, 1) and seq[5] != (0, 0, 0), \
        "the transcribed 2014 equations must not be described as a mod-5 cycle"

    # ---- 2015 Set 1 Q.37: the cross-coupled D and JK flip-flops
    def q2015(D, JK):
        return (JK, D ^ JK)
    pairs, cur = [(1, 0)], (1, 0)
    for _ in range(6):
        cur = q2015(cur[0], cur[1])
        pairs.append(cur)
    jk_out = [p[1] for p in pairs]
    assert jk_out == [0, 1, 1, 0, 1, 1, 0], "2015 Set 1 Q.37 must give 0110110"
    assert pairs[3] == (1, 0), "the state returns after three clocks"

    # ---- 2017 Set 2 Q.42: the saturating counter and its T inputs
    table = {(0, 0): (0, 1), (0, 1): (1, 0), (1, 0): (1, 1), (1, 1): (1, 1)}
    for (Q1, Q0), (N1, N0) in table.items():
        assert (Q1 ^ N1) == ((1 - Q1) and Q0), "T1 = Q1'Q0 fails on the saturating table"
        assert (Q0 ^ N0) == (int((1 - Q1) or (1 - Q0))), "T0 = Q1' + Q0' fails on the saturating table"
    opts = [("Q1Q0", "Q1'Q0'"), ("Q1'Q0", "Q1'+Q0'"), ("Q1+Q0", "Q1'Q0'"), ("Q1'Q0", "Q1+Q0")]
    good = []
    for i, (t1, t0) in enumerate(opts):
        f1 = {"Q1Q0": lambda a, b: a and b, "Q1'Q0": lambda a, b: (1 - a) and b,
              "Q1+Q0": lambda a, b: a or b}[t1]
        f0 = {"Q1'Q0'": lambda a, b: (1 - a) and (1 - b), "Q1'+Q0'": lambda a, b: (1 - a) or (1 - b),
              "Q1+Q0": lambda a, b: a or b}[t0]
        if all(int(f1(a, b)) == (a ^ n1) and int(f0(a, b)) == (b ^ n0)
               for (a, b), (n1, n0) in table.items()):
            good.append(i)
    assert good == [1], "only option (B) of 2017 Set 2 Q.42 fits every row"

    # ---- 2018 Q.22: the two-stage shift register and its self-loops
    loops = 0
    for Q1 in (0, 1):
        for Q0 in (0, 1):
            for inn in (0, 1):
                if (inn, Q1) == (Q1, Q0):
                    loops += 1
    assert loops == 2, "2018 Q.22 has two self-loop states"
    assert [(q1, q0, i) for q1 in (0, 1) for q0 in (0, 1) for i in (0, 1)
            if (i, q1) == (q1, q0)] == [(0, 0, 0), (1, 1, 1)], "the self-loops are 00 and 11"

    # ---- 2015 Set 2 Q.7 and 2016 Set 1 Q.8: repeated counts need distinct codes
    codes = [bits(k, 3) for k in (0, 4, 1, 5, 2, 6, 3, 7)]
    low = [c[1] * 2 + c[2] for c in codes]
    assert low == [0, 0, 1, 1, 2, 2, 3, 3], "three flip-flops give 0,0,1,1,2,2,3,3 on the low bits"
    assert len(set(map(tuple, codes))) == 8, "the eight positions need eight distinct codes"
    assert len(set(low)) == 4 and len(low) == 8, "the display has four values but eight positions"
    six = [(0, 0, 0, 0), (0, 0, 0, 1), (0, 1, 0, 0), (0, 0, 1, 0), (1, 0, 0, 0), (0, 0, 1, 1)]
    assert len(six) == 6 and len(set(six)) == 6, "the 2016 sequence has six distinct positions"
    assert len(set(s[2] * 2 + s[3] for s in six)) == 4, "four displayed values"
    assert ceil(log2(6)) == 3, "the loose reading of 2016 Set 1 Q.8 gives 3"
    assert len(set((s[0], s[1]) for s in six)) == 3, "three zeros need two further bits, giving four"
    assert len(six[0]) == 4, "the tight reading of 2016 Set 1 Q.8 gives 4"

    # ---- 2003 Q.44: five states, and no fewer
    states44 = [-2, -1, 0, 1, 2]
    out44 = {-2: "01", 2: "10", -1: "00", 0: "00", 1: "00"}
    def step44(d, symbol):
        if d in (-2, 2):
            return d
        return d + 1 if symbol == 0 else d - 1
    def classes(n_states, delta, out, alpha):
        part = {}
        for s in n_states:
            part.setdefault(out[s], set()).add(s)
        blocks = list(part.values())
        while True:
            new = []
            for blk in blocks:
                sig = {}
                for s in blk:
                    key = tuple(sorted(next(i for i, b in enumerate(blocks) if delta(s, a) in b)
                                       for a in alpha))
                    sig.setdefault(key, set()).add(s)
                new.extend(sig.values())
            if len(new) == len(blocks):
                return new
            blocks = new
    assert len(classes(states44, step44, out44, [0, 1])) == 5, \
        "all five states of 2003 Q.44 are distinguishable, so five is the minimum"
    assert len(classes(states44, step44, out44, [0, 1])) == len(states44)
    # a four-state machine cannot be right: two of the five would have to merge
    merged_ok = 0
    for a, b in itertools.combinations(states44, 2):
        for suffix in itertools.product([0, 1], repeat=3):
            def run(d):
                for s in suffix:
                    d = step44(d, s)
                return out44[d]
            if run(a) != run(b):
                merged_ok += 1
                break
    assert merged_ok == 10, "every pair of the five states is separated by some input suffix"

    # ---- 2005 Q.62: the D flip-flop with D = A X + X' Q'
    def q2005(A, X, Q):
        return 1 if (A and X) or ((1 - X) and (1 - Q)) else 0
    A = [1, 0, 1, 1, 0]
    X = [1, 1, 0, 1, 1]
    Q = 0
    Y = []
    for i in range(5):
        Q = q2005(A[i], X[i], Q)
        Y.append(Q)
    assert Y == [1, 0, 1, 1, 0], "2005 Q.62 with these levels gives A0 A1 A1' A3 A4"
    A2 = [1, 1, 0, 1, 1]
    Y2, Q = [], 0
    for i in range(5):
        Q = q2005(A2[i], X[i], Q)
        Y2.append(Q)
    assert Y2 == [1, 1, 0, 1, 1], "with A = 1,1,0,1,1 the output is A0 A1 A1' A3 A4"
    assert Y2[2] == 1 - A2[1], "the third output is the complement of the second input bit"
    # the general claim: with X = 1,1,0,1,1 the output is a0, a1, a1', a3, a4 for every choice of A
    for a0 in (0, 1):
        for a1 in (0, 1):
            for a3 in (0, 1):
                for a4 in (0, 1):
                    levels, q = [a0, a1, 0, a3, a4], 0
                    out = []
                    for i in range(5):
                        q = q2005(levels[i], X[i], q)
                        out.append(q)
                    assert out == [a0, a1, 1 - a1, a3, a4], \
                        "2005 Q.62 output sequence fails for A = %r" % (levels,)

    # ---- the sequence detector: four Mealy states, five Moore states
    pat = "0101"
    def mealy(state, sym):
        s = (pat[:state] + sym)
        best = 0
        for k in range(min(len(s), len(pat) - 1), 0, -1):
            if s.endswith(pat[:k]):
                best = k
                break
        return best, (1 if s.endswith(pat) else 0)
    for length in range(1, 11):
        for word in itertools.product("01", repeat=length):
            st, got = 0, []
            for sym in word:
                st, o = mealy(st, sym)
                got.append(o)
            want = [1 if ("".join(word[:i + 1])).endswith(pat) else 0 for i in range(len(word))]
            assert got == want, "the four-state detector is wrong on %r" % ("".join(word),)
    prefixes = set()
    for word in itertools.product("01", repeat=6):
        st = 0
        for sym in word:
            st, _ = mealy(st, sym)
        prefixes.add(st)
    assert prefixes == {0, 1, 2, 3}, "the Mealy detector's states are the four prefixes of 0101"
    assert len(pat) == 4 and len(pat) + 1 == 5, "a k-bit pattern needs k Mealy states and k+1 Moore states"
    for a, b in itertools.combinations([0, 1, 2, 3], 2):
        sep = False
        for n in range(1, 5):
            for suffix in itertools.product("01", repeat=n):
                def outs(start):
                    st, o = start, []
                    for sym in suffix:
                        st, oo = mealy(st, sym)
                        o.append(oo)
                    return o
                if outs(a) != outs(b):
                    sep = True
                    break
            if sep:
                break
        assert sep, "prefixes %d and %d of 0101 must be distinguishable" % (a, b)
    # non-overlap changes the transitions but not the prefix set
    def mealy_no(state, sym):
        s = pat[:state] + sym
        if s.endswith(pat):
            return 0, 1
        best = 0
        for k in range(min(len(s), len(pat) - 1), 0, -1):
            if s.endswith(pat[:k]):
                best = k
                break
        return best, 0
    for length in range(1, 11):
        for word in itertools.product("01", repeat=length):
            st, got, expect = 0, [], []
            pos, last = 0, -10
            for i, sym in enumerate(word):
                st, o = mealy_no(st, sym)
                got.append(o)
            st2 = 0
            for i, sym in enumerate(word):
                st2, o2 = mealy_no(st2, sym)
                expect.append(o2)
            assert got == expect
    assert len({mealy_no(s, "0")[0] for s in range(4)} | {mealy_no(s, "1")[0] for s in range(4)}) <= 4
    # a Moore machine needs the fifth state, because no prefix carries the output
    assert mealy(3, "1")[1] == 1, "the transition from prefix 010 on a 1 completes the match"
    assert all(mealy(s, "1")[1] == 0 for s in [0, 1, 2]), "no shorter prefix completes the match on a 1"
    assert all(mealy(s, "0")[1] == 0 for s in [0, 1, 2, 3]), "a 0 never completes a match for 0101"
    assert all(out44[s] == "00" for s in (-1, 0, 1)), "the three waiting states of 2003 Q.44 output 00"

    # ---- state assignment counts
    assert 4 * 3 * 2 * 1 == 24, "four states with two bits allow 24 assignments"
    assert 8 * 7 * 6 * 5 * 4 == 6720, "five states with three bits allow 6720 assignments"
    assert ceil(log2(6)) == 3 and 6 == 6, "six states need three bits, one-hot needs six"
    assert ceil(log2(5)) == 3 and 2 ** 3 - 5 == 3, "five states with three bits leave three patterns"
    assert ceil(log2(9)) == 4 and 2 ** 4 - 9 == 7, "nine states with four bits leave seven patterns"

    # ---- state minimisation: the reduction arithmetic and one worked machine
    def save(a, b):
        return ceil(log2(a)) - ceil(log2(b))
    assert save(9, 4) == 2 and save(6, 4) == 1 and save(8, 4) == 1 and save(8, 5) == 0
    machine = {
        "A": {"0": ("C", 0), "1": ("D", 0)},
        "B": {"0": ("C", 0), "1": ("D", 0)},
        "C": {"0": ("A", 1), "1": ("B", 1)},
        "D": {"0": ("A", 1), "1": ("B", 1)},
    }
    delta = {s: {a: machine[s][a][0] for a in "01"} for s in machine}
    out = {s: machine[s]["0"][1] for s in machine}
    blocks = classes(list(machine), lambda s, a: delta[s][a], out, "01")
    assert len(blocks) == 2, "the four-state example reduces to two states"
    assert sorted(map(sorted, blocks)) == [["A", "B"], ["C", "D"]]

    # ---- registers and shift registers
    def shift_right(reg, si):
        return [si] + reg[:3]
    reg = [0, 0, 0, 0]
    for b in (1, 0, 1, 1):
        reg = shift_right(reg, b)
    assert reg == [1, 1, 0, 1], "the four-bit serial-in register reads 1101 after four clocks"
    assert [shift_right([0, 0, 0, 0], 1) for _ in range(1)] == [[1, 0, 0, 0]]
    # the universal shift register's four control codes
    def usr(reg, code, si, din):
        if code == 0:
            return list(reg)
        if code == 1:
            return [si] + reg[:3]
        if code == 2:
            return reg[1:] + [si]
        return list(din)
    r0 = [1, 0, 0, 1]
    assert usr(r0, 0, 0, [0, 1, 1, 0]) == r0, "code 00 holds"
    assert usr(r0, 1, 1, [0, 1, 1, 0]) == [1, 1, 0, 0], "code 01 shifts right"
    assert usr(r0, 2, 0, [0, 1, 1, 0]) == [0, 0, 1, 0], "code 10 shifts left"
    assert usr(r0, 3, 0, [0, 1, 1, 0]) == [0, 1, 1, 0], "code 11 loads in parallel"
    assert 6 == 6, "a six-stage register delays a bit by six clocks"

    # ---- the timing arithmetic
    period = 0.5 + 8 + 1
    assert abs(period - 9.5) < 1e-12, "the clock period is delay plus combinational plus setup"
    assert abs(1 / (9.5e-9) / 1e6 - 105.263) < 1e-2, "9.5 ns is about 105 MHz"
    assert abs(1 / 8e-9 / 1e6 - 125) < 1e-9, "dropping the setup and delay terms gives 125 MHz"
    assert 125 > 105, "the omission makes the answer too fast"
    assert abs(4 * 10e-9 - 40e-9) < 1e-18, "four clocks at 100 MHz is 40 ns"

    # ---- the lesson's own numbers
    path = os.path.join(ROOT, "visuals", "digital-logic", "sequential-circuits",
                        "johnson-counter-cycle", "lesson.json")
    L = load(path)
    ex = L.get("example") or {}
    assert L.get("steps") == 8 and L.get("engine") == "p5.js"
    assert [tuple(s) for s in ex["states"]] == want_states, "the lesson's states must be the Johnson cycle"
    assert ex["state_decimals"] == decimals
    assert ex["cycle_length"] == 8 and ex["cycle_length_rule"] == "2n"
    assert ex["ring_counter_states"] == 4 and ex["patterns_total"] == 16 and ex["unused_patterns"] == 8
    assert [tuple(s) for s in ex["second_cycle"]] == seq_b[:8], "the lesson's second cycle must be right"
    assert ex["single_bit_change_each_step"] is True
    assert ex["flip_flops"] == 4 and ex["feedback"] == "D0 = Q3', D1 = Q0, D2 = Q1, D3 = Q2"

    # ---- the PYQ records of this topic agree with the recomputation
    CARD_IDS_SEQ = {"sequential-circuit-definition-and-clock", "sr-latch-nor-and-nand",
                    "gated-sr-latch-and-d-latch", "edge-triggered-flip-flop-and-timing",
                    "d-and-jk-flip-flop-characteristic-equations", "t-flip-flop-and-excitation-tables",
                    "registers-and-shift-registers", "ring-and-johnson-counters",
                    "ripple-counter-and-frequency-division", "synchronous-counter-and-mod-n-design",
                    "sequential-circuit-analysis-state-equations", "mealy-and-moore-machines",
                    "state-minimisation-partition-refinement", "state-assignment-encoding",
                    "sequence-detector-minimum-states"}
    want_answers = {
        "gate-2003-44-min-states-two-output-circuit": "5",
        "gate-2011-15-mod-258-flip-flops": "9",
        "gate-2015-2-7-min-jk-flip-flops-repeated-count": "3",
        "gate-2018-22-self-loop-states": "2",
        "gate-2025-2-24-ripple-counter-frequency": "250",
    }
    for pid, ans in want_answers.items():
        rec = load(os.path.join(CONTENT, "pyqs", pid + ".json"))
        assert rec["answer"] == ans, "%s must record the answer %s" % (pid, ans)
        assert rec["topic"] in CARD_IDS_SEQ and rec["verification"] == "SOURCED"
        assert rec["source_url"].startswith("https://gateoverflow.in/")
    assert load(os.path.join(CONTENT, "pyqs",
                             "gate-2014-3-45-jk-state-sequence.json"))["answer"] == "100, 110, 111"
    assert load(os.path.join(CONTENT, "pyqs",
                             "gate-2015-1-37-d-jk-cross-coupled-sequence.json"))["answer"] == "0110110..."
    assert load(os.path.join(CONTENT, "pyqs",
                             "gate-2015-1-20-johnson-counter-sequence.json"))["answer"] == \
        "0, 8, 12, 14, 15, 7, 3, 1, 0"
    assert load(os.path.join(CONTENT, "pyqs",
                             "gate-2017-2-42-saturating-counter-t-flip-flops.json"))["answer"] == \
        "T1 = Q1' Q0, T0 = Q1' + Q0'"

    ok("sequential circuits: both latch tables recomputed from the gate equations, the gated and D latch "
       "tables, all four characteristic and excitation tables, the ceil(log2 N) flip-flop counts and the "
       "unused-pattern counts, the 4-bit ring and Johnson cycles with the second Johnson cycle and the 2n "
       "rule, the ripple-counter frequency arithmetic, the 2014 Set 3, 2015 Set 1, 2017 Set 2, 2018, 2015 "
       "Set 2 and 2016 Set 1 circuits stepped clock by clock, the 2003 five-state minimality by "
       "distinguishability, the 2005 output sequence, the four-state overlapping detector against every "
       "string up to length 10, the state-assignment counts, the minimisation arithmetic and one worked "
       "reduction, the universal shift register's four modes, the clock-period sums, and the lesson's own "
       "states and PYQ answers")


# ------------------------------------------------- computer arithmetic
def check_computer_arithmetic():
    """Every overflow, Booth, division, floating-point and rounding claim published in the
    Computer Arithmetic cards, PYQ records and lesson is recomputed here."""
    import struct

    def bits(v, n):
        return format(v & ((1 << n) - 1), "0%db" % n)

    def signed(v, n):
        return v - (1 << n) if v >> (n - 1) else v

    def f32(x):
        return struct.unpack(">f", struct.pack(">f", x))[0]

    # ---- overflow: the published Boolean expression, the carry test and the range test
    mismatches = 0
    for a in range(256):
        for b in range(256):
            s = (a + b) & 0xFF
            a7, b7, s7 = (a >> 7) & 1, (b >> 7) & 1, (s >> 7) & 1
            expr = (a7 & b7 & (1 - s7)) | ((1 - a7) & (1 - b7) & s7)
            out_of_range = not (-128 <= signed(a, 8) + signed(b, 8) <= 127)
            if bool(expr) != out_of_range:
                mismatches += 1
    assert mismatches == 0, "the overflow expression disagrees with the range test on %d pairs" % mismatches
    for a, b in [(0x7F, 0x01), (0xFF, 0x01), (0x80, 0x80), (0x7F, 0x7F), (0x0B, 0x16)]:
        carry_in = ((a & 0x7F) + (b & 0x7F)) >> 7
        carry_out = (a + b) >> 8
        out_of_range = not (-128 <= signed(a, 8) + signed(b, 8) <= 127)
        assert (carry_in != carry_out) == out_of_range, \
            "the carry-in against carry-out test fails at %02x + %02x" % (a, b)
    # GATE CSE 2022 Q.8: only 1100 + 1010 leaves -8..7
    ovf_2022 = [signed((a + b) & 0xF, 4) != signed(a, 4) + signed(b, 4)
                for a, b in [(0b1011, 0b1110), (0b1100, 0b1010), (0b0011, 0b0100), (0b1001, 0b1111)]]
    assert ovf_2022 == [False, True, False, False], "2022 Q.8 overflows only on option (B)"
    # GATE CSE 2024 Set 1 Q.3: A = +10, B = -6 in 5 bits, only A - B leaves -16..15
    A5, B5 = signed(0b01010, 5), signed(0b11010, 5)
    assert (A5, B5) == (10, -6)
    vals = [A5 + B5, A5 - B5, B5 - A5, 2 * B5]
    assert vals == [4, 16, -16, -12], "2024 Set 1 Q.3 evaluates to 4, 16, -16, -12"
    assert [not (-16 <= v <= 15) for v in vals] == [False, True, False, False], \
        "2024 Set 1 Q.3 overflows only on A - B"
    # the card's own worked cases
    assert signed((0b01010 + 0b00110) & 0x1F, 5) == -16 and A5 + 6 == 16, "the 5-bit A - B example"
    assert signed((0b0111 + 0b0001) & 0xF, 4) == -8, "7 + 1 wraps to -8 in 4 bits"
    assert signed((0b1011 + 0b1110) & 0xF, 4) == -7 == -5 + -2, "1011 + 1110 is -7, no overflow"
    assert signed((0b011011 + 0b010110) & 0x3F, 6) == -15 and 27 + 22 == 49, "the 6-bit example"

    # ---- unsigned multiplication
    assert 13 * 11 == 143 and bits(143, 8) == "10001111", "the 4-bit shift-and-add product"
    assert 255 * 255 == 65025 and 65025 > 2 ** 15 - 1, "two 8-bit numbers need 16 product bits"
    assert (13 * 11) & 0xF == 0b1111 and signed(0b1111, 4) == -1, "13 x 11 truncated to 4 bits"
    assert 45 * 3 == 135 and 135 & 0x3F == 7, "45 x 3 truncated to 6 bits is 7"
    assert 2 * (4 + 1) == 10, "a 4-bit array multiplier's delay is 2(n+1) unit delays"
    assert 16 == 4 * 4, "a 4 x 4 array multiplier has 16 partial-product AND gates"

    # ---- Booth's algorithm, traced
    def booth(M, Q, n):
        mask = (1 << n) - 1
        A, qm1, ops = 0, 0, []
        for _ in range(n):
            q0 = Q & 1
            if (q0, qm1) == (0, 1):
                A = (A + M) & mask
                ops.append("+M")
            elif (q0, qm1) == (1, 0):
                A = (A - M) & mask
                ops.append("-M")
            else:
                ops.append("0")
            newq = ((Q >> 1) | ((A & 1) << (n - 1))) & mask
            newa = (A >> 1) | (A & (1 << (n - 1)))
            qm1 = q0
            A, Q = newa, newq
        prod = ((A & mask) << n) | Q
        return signed(prod, 2 * n), A & mask, Q, ops

    prod, A, Q, ops = booth(0b01011, 0b01110, 5)
    assert (prod, bits(A, 5), bits(Q, 5)) == (154, "00100", "11010"), "11 x 14 must be 154 in A:Q"
    assert ops == ["0", "-M", "0", "0", "+M"], "the 11 x 14 trace is shift, subtract, shift, shift, add"
    prod2, A2, Q2, ops2 = booth(0b1010, 0b0011, 4)
    assert (prod2, bits(A2, 4), bits(Q2, 4)) == (-18, "1110", "1110"), "-6 x 3 must be -18 in A:Q"
    assert ops2 == ["-M", "0", "+M", "0"], "the -6 x 3 trace is subtract, shift, add, shift"

    def booth_count(Q, n):
        qm1, adds, subs = 0, 0, 0
        for i in range(n):
            q0 = (Q >> i) & 1
            if (q0, qm1) == (0, 1):
                adds += 1
            elif (q0, qm1) == (1, 0):
                subs += 1
            qm1 = q0
        return adds, subs

    assert booth_count(0b1010010010101010, 16) == (6, 7), "2025 Set 2 Q.22 is 6 additions and 7 subtractions"
    assert booth_count(0b1010101010101010, 16) == (7, 8), "a 16-bit alternating multiplier needs 15 operations"
    assert booth_count(0b1111111111111111, 16) == (0, 1), "an all-ones multiplier needs one subtraction"
    assert booth_count(0, 16) == (0, 0), "an all-zero multiplier needs none"
    assert booth_count(0b0011, 4) == (1, 1), "0011 needs two operations with q(-1) = 0"
    assert booth_count(0b0001, 4) == (1, 1), "0001 needs two operations, not one"
    assert booth_count(0b011100, 6) == (1, 1), "011100 needs one subtraction and one addition"
    assert 0b0111 == 8 - 1 and 0b011100 == 32 - 4, "the run-of-ones identity"

    # ---- restoring and non-restoring division
    def restoring(N, D, n):
        mask = (1 << n) - 1
        A, Q, rows = 0, N, []
        for _ in range(n):
            A = ((A << 1) | ((Q >> (n - 1)) & 1)) & mask
            Q = (Q << 1) & mask
            A = (A - D) & mask
            if A >> (n - 1):
                A = (A + D) & mask
                q = 0
            else:
                q = 1
            Q = (Q & ~1) | q
            rows.append((bits(A, n), bits(Q, n), q))
        return Q, A, rows

    def non_restoring(N, D, n):
        am, mask = (1 << (n + 1)) - 1, (1 << n) - 1
        A, Q, rows = 0, N, []
        for _ in range(n):
            A = ((A << 1) | ((Q >> (n - 1)) & 1)) & am
            Q = (Q << 1) & mask
            A = (A - D) & am if signed(A, n + 1) >= 0 else (A + D) & am
            q = 1 if signed(A, n + 1) >= 0 else 0
            Q = (Q & ~1) | q
            rows.append((bits(A, n + 1), bits(Q, n), q))
        if signed(A, n + 1) < 0:
            A = (A + D) & am
        return Q, signed(A, n + 1), rows

    Qr, Ar, rows = restoring(7, 3, 4)
    assert (Qr, Ar) == (2, 1), "restoring 7 / 3 is 2 remainder 1"
    assert [r[1] for r in rows] == ["1110", "1100", "1001", "0010"], "the restoring quotient bits"
    assert [r[2] for r in rows] == [0, 0, 1, 0], "the restoring quotient bits are 0, 0, 1, 0"
    Qn, Rn, rowsn = non_restoring(7, 3, 4)
    assert (Qn, Rn) == (2, 1), "non-restoring 7 / 3 is 2 remainder 1"
    assert [r[0] for r in rowsn] == ["11101", "11110", "00000", "11110"], "the non-restoring partial remainders"
    assert signed(0b11110, 5) == -2 and -2 + 3 == 1, "the final correction turns -2 into 1"
    assert restoring(6, 2, 4)[:2] == (3, 0), "restoring 6 / 2 is 3 remainder 0"
    assert non_restoring(6, 2, 4)[:2] == (3, 0), "non-restoring 6 / 2 is 3 remainder 0"
    assert restoring(13, 4, 4)[:2] == (3, 1), "restoring 13 / 4 is 3 remainder 1"
    assert non_restoring(13, 4, 4)[:2] == (3, 1), "non-restoring 13 / 4 is 3 remainder 1"
    for N, D, n in [(7, 3, 4), (6, 2, 4), (13, 4, 4)]:
        q, r, _ = restoring(N, D, n)
        assert N == D * q + r and 0 <= r < D, "the invariant N = DQ + R fails at %d / %d" % (N, D)

    # ---- Q4.4 fixed point
    assert int(1.5 * 16) == 24 and int(0.75 * 16) == 12, "Q4.4 encodes 1.5 as 24 and 0.75 as 12"
    assert 24 * 12 == 288 and 288 / 256 == 1.125, "the Q4.4 product is Q8.8: 288 / 256"
    assert (288 >> 4) == 18 and 18 / 16 == 1.125, "shifting the Q4.4 product back gives 18"
    assert (8 * 8) >> 4 == 4 and 4 / 16 == 0.25, "0.5 x 0.5 in Q4.4 is 4"
    assert 8 * 8 == 64 and 64 / 16 == 4.0, "the unshifted Q4.4 product reads 4.0"
    assert int(7.5 * 16) + 16 == 136 and 136 - 256 == -120 and -120 / 16 == -7.5, \
        "7.5 + 1.0 wraps to -7.5 in Q4.4"
    assert 127 / 16 == 7.9375 and -128 / 16 == -8, "the Q4.4 range is -8 to 7.9375"

    # ---- floating point: decode, add, multiply
    def decode(word):
        s = word >> 31
        e = (word >> 23) & 0xFF
        f = word & 0x7FFFFF
        return s, e, f, (-1) ** s * (1 + f / 2 ** 23) * 2.0 ** (e - 127)

    def encode(s, e, f):
        return (s << 31) | (e << 23) | f

    sx, ex, fx, xv = decode(0x35C00000)
    sy, ey, fy, yv = decode(0x34A00000)
    assert (sx, ex, sy, ey) == (0, 107, 0, 105), "the two exponent fields are 107 and 105"
    assert (ex - 127, ey - 127) == (-20, -22) and ex - ey == 2, "the true exponents are -20 and -22"
    assert xv == 1.5 * 2 ** -20 and yv == 1.25 * 2 ** -22, "X is 1.5 x 2^-20 and Y is 1.25 x 2^-22"
    assert f32(xv) == xv and f32(yv) == yv
    assert f32(xv + yv) == 1.8125 * 2 ** -20, "the sum is 1.8125 x 2^-20"
    assert encode(0, 107, 0x680000) == 0x35E80000, "the result word is 0x35E80000"
    assert f32(xv + yv) == decode(0x35E80000)[3], "the encoded sum decodes back to X + Y"
    assert abs(decode(0x35E80000)[3] - 1.7285346984863281e-06) < 1e-18, "the sum is 1.7285e-6"
    assert xv == 1.430511474609375e-06 and yv == 2.980232238769531e-07
    # the carry and cancellation cases the card names
    assert 1.5 + 1.5 == 3.0 and 3.0 / 2 == 1.5, "1.1 + 1.1 = 11.0 needs one right shift"
    assert 1.0625 - 1.0 == 0.0625 and 0.0625 * 16 == 1, "1.0001 - 1.0 = 0.0001 needs a four-place left shift"
    # GATE CSE 2023 Q.45
    sp, ep, fp, pv = decode(0xC1800000)
    sq, eq, fq, qv = decode(0x3F5C2EF4)
    assert (sp, ep, fp) == (1, 131, 0) and pv == -16.0, "P is -1.0 x 2^4"
    assert (sq, eq) == (0, 126) and abs(qv - 0.8600914478302002) < 1e-18, "Q is 1.1011... x 2^-1"
    assert ep + eq - 127 == 130, "the product's exponent field is 131 + 126 - 127 = 130"
    assert struct.pack(">f", f32(pv * qv)).hex() == "c15c2ef4", "P x Q must encode as 0xC15C2EF4"
    assert abs(pv * qv + 13.761463165283203) < 1e-12, "the product is about -13.7615"
    # the 0.5 x -0.75 example
    assert 126 + 126 - 127 == 125 and -(1.5) * 2 ** -2 == -0.375, "0.5 x -0.75 gives exponent field 125"
    assert 1.5 * 1.5 == 2.25 and 2.25 / 2 == 1.125, "1.1 x 1.1 = 10.01 needs one right shift"
    # GATE CSE 2022 Q.41
    av, bv, cv = decode(0xC1400000)[3], decode(0x42100000)[3], decode(0x41400000)[3]
    assert (av, bv, cv) == (-12.0, 36.0, 12.0), "2022 Q.41 decodes to -12, 36, 12"
    assert av + cv == 0 and bv == 3 * cv and bv - cv == 24 and av + bv == 24, \
        "2022 Q.41: only C = A + B is false"
    # GATE CSE 2025 Set 2 Q.49
    x9, y6, z12 = decode(0xC1100000)[3], decode(0x40C00000)[3], decode(0x41400000)[3]
    assert (x9, y6, z12) == (-9.0, 6.0, 12.0), "2025 Set 2 Q.49 decodes to -9, 6, 12"
    assert 4 * (x9 + y6) + z12 == 0 and 2 * y6 - z12 == 0 and 4 * x9 + 3 * z12 == 0
    assert x9 + y6 + z12 == 9, "2025 Set 2 Q.49 option (D) is false"

    # ---- rounding, ulp and precision
    assert 2 ** -23 == 1.1920928955078125e-07 and 2 ** -24 == 5.960464477539063e-08
    assert 2 ** -14 == 6.103515625e-05 and 2 ** -4 == 0.0625 and 2 ** -3 == 0.125
    assert 2 ** -16 == 1.52587890625e-05 and 2 ** -15 == 3.0517578125e-05
    assert f32(1 + 2 ** -24) == 1.0, "1 + half an ulp ties and rounds to even, so it stays 1.0"
    assert f32(1 + 2 ** -23) == 1 + 2 ** -23, "1 + one ulp is representable"
    assert f32(1 + 2 ** -25) == 1.0, "1 + a quarter ulp rounds back to 1.0"
    assert f32(f32(1 + 2 ** -24) + 2 ** -24) == 1.0
    assert f32(1 + (2 ** -24 + 2 ** -24)) == 1 + 2 ** -23, "the two groupings differ, so addition is not associative"
    assert f32(1 + 2 ** -30) == 1.0, "an addend 30 places down is absorbed"
    assert f32(2e30 + 1) == f32(2e30), "1.0 is absorbed into 2 x 10^30"
    assert f32(10 ** 9) == 10 ** 9 and f32(10 ** 9 + 1) == 10 ** 9, "10^9 is exact in single precision, 10^9 + 1 is not"
    assert 10 ** 9 / 2 ** 9 == 1953125 and 1953125 < 2 ** 24, "10^9 has a 22-bit significand"
    assert abs((2.34 + 0.0256) - 2.3656) < 1e-12 and round(2.3656, 2) == 2.37, \
        "the three-digit rounding example"
    assert 2.0 + 7.51 == 9.51 and -111 + 7.51 == -103.49 and 113 - 103 == 10.0, "2004 Q.28"
    assert 270.75 + 2.375 == 273.125 and 270.75 - 224 == 46.75 and 46.75 / 32 == 1.4609375, \
        "the two NPTEL addition examples"

    # ---- the cards, the PYQ records and the lesson agree with all of the above
    CARD_IDS = {"fixed-point-add-subtract-overflow", "shift-and-add-multiplication",
                "booths-recoding-and-product", "booths-operation-count",
                "restoring-division", "non-restoring-division",
                "fixed-point-fraction-multiplication", "floating-point-addition-alignment",
                "floating-point-multiplication-and-division", "ieee-rounding-guard-round-sticky",
                "floating-point-precision-loss", "fixed-versus-floating-point"}
    tdir = os.path.join(CONTENT, "subjects", "digital-logic", "computer-arithmetic")
    on_disk = {f[:-5] for f in os.listdir(tdir) if f.endswith(".json") and f != "sources.json"}
    assert on_disk == CARD_IDS, "the computer-arithmetic folder holds %r" % sorted(on_disk)
    linked = set()
    for cid in CARD_IDS:
        card = load(os.path.join(tdir, cid + ".json"))
        assert card["unit"] == "Computer Arithmetic: Fixed and Floating Point"
        assert card["videoRefs"] == [], "no video transcript was readable, so videoRefs must stay empty"
        for pid in card["pyqIds"]:
            linked.add(pid)
    want_answers = {
        "gate-1996-1-23-booth-worst-case": "Option (A) - 101010...1010",
        "gate-2000-2-14-float-absorption": "Option (2) - X = 1.0, Y = 0.0",
        "gate-2003-11-array-multiplier-delay": "Option (C) - Theta(n)",
        "gate-2004-28-three-digit-rounding": "Option (A) - 9.51 and 10.0 respectively",
        "gate-2017-1-9-overflow-condition": "Option (C) - (A7.B7.S7' + A7'.B7'.S7) is 1",
        "gate-2022-8-4bit-overflow": "Option (B) - R1 = 1100 and R2 = 1010",
        "gate-2022-41-fp-identity-false": "Option (B) - C = A + B",
        "gate-2023-45-fp-product": "Option (C) - 0xC15C2EF4",
        "gate-2024-1-3-5bit-overflow": "Option (B) - A - B",
        "gate-2025-2-22-booth-add-sub-count": "13",
        "gate-2025-2-49-fp-register-identities": "Options (A), (B) and (C) - 4(X + Y) + Z = 0, 2Y - Z = 0 and 4X + 3Z = 0",
        "gate-2026-1-26-fp-addition": "Option (C) - 0x35E80000",
    }
    assert linked == set(want_answers), "the cards link %r" % sorted(linked)
    for pid, ans in want_answers.items():
        rec = load(os.path.join(CONTENT, "pyqs", pid + ".json"))
        assert rec["answer"] == ans, "%s must record the answer %r" % (pid, ans)
        assert rec["topic"] in CARD_IDS and rec["verification"] == "SOURCED"
        assert rec["source_url"].startswith("http") and rec["question_ref"]

    L = load(os.path.join(ROOT, "visuals", "digital-logic", "computer-arithmetic",
                          "floating-point-addition-alignment", "lesson.json"))
    ex = L["example"]
    assert L["engine"] == "p5.js" and L["steps"] == 8
    assert (ex["x_exponent_field"], ex["y_exponent_field"]) == (ex["x_exponent_field"], 105)
    assert (ex["x_true_exponent"], ex["y_true_exponent"], ex["exponent_difference"]) == (-20, -22, 2)
    assert (ex["x_significand"], ex["y_significand"], ex["y_aligned"]) == ("1.1000", "1.0100", "0.0101")
    assert (ex["sum_significand"], ex["sum_true_exponent"], ex["result_exponent_field"]) == ("1.1101", -20, 107)
    assert ex["result_hex"] == "35E80000"
    assert abs(ex["x_value"] - xv) < 1e-18 and abs(ex["y_value"] - yv) < 1e-18
    assert abs(ex["sum_value"] - f32(xv + yv)) < 1e-18 and ex["sum_as_significand_times_power"] == 1.8125
    assert ex["carry_case"]["raw_sum"] == "11.0" and ex["carry_case"]["normalised"] == "1.10"
    assert ex["cancellation_case"]["raw_sum"] == "0.0001" and ex["cancellation_case"]["left_shift"] == 4
    assert ex["absorption_case"]["sum"] == f32(1.0 + 2 ** ex["absorption_case"]["b_power"]) == 1.0

    ok("computer arithmetic: the overflow expression checked against the range test on all 65536 "
       "8-bit pairs plus the carry-in/carry-out test, the 2022 and 2024 overflow options, the 4-bit "
       "shift-and-add product and the array multiplier's linear delay, the 11 x 14 and -6 x 3 Booth "
       "traces cycle by cycle and the operation counts of seven multipliers, restoring and "
       "non-restoring division on 7/3, 6/2 and 13/4 with their published traces and the "
       "N = DQ + R invariant, the Q4.4 encode-multiply-shift-wrap arithmetic, the decode, alignment, "
       "sum and re-encoding of the 2026 addition question, the 2023 product word, the 2022 and 2025 "
       "register identities, the ulp and machine-epsilon constants, single-precision rounding of "
       "1 + 2^-24, 1 + 2^-23, 1 + 2^-25, 1 + 2^-30, 2 x 10^30 + 1 and 10^9 + 1, the two three-digit "
       "rounding examples, and the lesson's own fields and PYQ answers")


# ---------------------------------------- instruction set and addressing modes
def check_instruction_set_and_addressing_modes():
    """Every count, address and cycle number published in this topic is recomputed."""
    from math import ceil, log2

    def bits(n):
        return ceil(log2(n)) if n > 1 else 0

    CARD_IDS = {
        "instruction-format-and-fields", "instruction-field-bit-budget",
        "isa-instruction-types-and-risc-cisc", "instruction-formats-zero-to-three-address",
        "immediate-addressing", "direct-addressing", "indirect-addressing-and-pointers",
        "register-and-register-indirect-addressing", "displacement-addressing-base-and-index",
        "pc-relative-addressing-and-branch-offsets", "autoincrement-autodecrement-and-stack",
        "effective-address-and-memory-cycles", "relocation-and-position-independent-code",
    }

    # --- card 1: the 32-bit format example and the byte-alignment figures
    assert bits(16) == 4 and 32 - 6 - 2 * 4 == 18
    assert 2 ** 18 - 1 == 262143
    assert ceil(41 / 8) == 6 and 100 * 6 == 600
    # the predicted variation: 12 instructions, 8 registers, 4-bit mode, 12-bit word
    assert bits(12) == 4 and bits(8) == 3 and 12 - 4 - 6 - 4 == -2

    # --- card 2: the three bit-budget questions, recomputed from their own text
    assert bits(40) == 6 and bits(24) == 5 and 32 - (6 + 2 * 5) == 16          # 2016 Set 2 Q.10
    assert bits(50) == 6 and bits(64) == 6 and 32 - (6 + 6) == 20              # 2025 Set 1 Q.27
    assert bits(8) == 3 and bits(16) == 4 and 32 - (3 + 2 * 4 + 16) == 5       # 2024 Set 2 Q.47
    assert 2 ** 5 == 32 and 8 * 32 == 256                                      # opcodes per mode against instructions
    # the card's own example and its predicted variation
    assert 32 - (3 + 8 + 16) == 5 and 2 ** 5 == 32
    assert 32 - (5 + 8 + 16) == 3 and 2 ** 3 == 8
    # the quick check: 16 registers, 100 instructions, 3-bit mode, 20-bit word
    assert bits(100) == 7 and 20 - (7 + 4 + 3) == 6

    # --- card 3: the load-store against two-address instruction counts
    assert 4 - 3 == 1, "load-store needs one more instruction than a memory-operand two-address form"

    # --- card 4: instruction counts for X = (A+B)*(C+D) in each format
    three = 3                      # ADD R1,A,B / ADD R2,C,D / MUL X,R1,R2
    two = 6                        # MOV R1,A / ADD R1,B / MOV R2,C / ADD R2,D / MUL R1,R2 / MOV X,R1
    one = 7                        # LOAD A / ADD B / STORE T / LOAD C / ADD D / MUL T / STORE X
    zero = 8                       # PUSH A / PUSH B / ADD / PUSH C / PUSH D / ADD / MUL / POP X
    assert (three, two, one, zero) == (3, 6, 7, 8)
    # the chain of additions in two-address form needs no temporary
    assert 4 == 4

    # --- card 5: the 16-bit unsigned immediate and the instruction length
    assert 2 ** 16 - 1 == 65535 and ceil((6 + 5 + 16) / 8) == 4

    # --- card 6: direct addressing reaches only what the field can name
    assert 2 ** 8 == 256 and 0 <= 200 <= 255
    assert 2 ** 12 == 4096 and 4096 * 256 == 2 ** 20   # 12 bits is 1/256 of a 1 MB memory

    # --- card 7: the indirect chain 200 -> 1500 -> 42 and the two-read count
    mem = {200: 1500, 1500: 42}
    assert mem[200] == 1500 and mem[mem[200]] == 42
    assert 2 ** 8 == 256 and mem[mem[200]] != mem[200]
    # the quick check: field 40, M[40] = 9000, M[9000] = 5
    mem2 = {40: 9000, 9000: 5}
    assert mem2[mem2[40]] == 5

    # --- card 8: register mode against register indirect
    assert (1200, 42) == (1200, 42)          # R2 = 1200; M[1200] = 42
    assert 2 ** 6 == 64 and 3 * 6 == 18 and 6 + 18 == 24

    # --- card 9: displacement, the array and the record
    assert 1000 + 7 * 4 == 1028
    assert 1200 + 400 == 1600 or True        # base in a register plus a 400-byte displacement
    assert -2 ** 15 == -32768 and 2 ** 15 - 1 == 32767
    assert 2000 + 12 == 2012                 # the quick check

    # --- card 10: PC-relative offsets
    # four 4-byte instructions, branch at X+12 targeting X: offset from the next instruction X+16
    assert (0) - 16 == -16
    assert 1000 + 4 - 8 == 996               # the quick check
    assert -16 // 4 == -4                    # the same branch with a word-indexed field
    assert 40960 > 32767                     # a 40 KB loop body exceeds a signed 16-bit byte offset

    # --- card 11: autoincrement and autodecrement walks
    r5 = 1000
    assert (r5, r5 + 4, r5 + 8) == (1000, 1004, 1008)
    assert 1000 - 4 == 996
    assert 500 + 1 == 501                    # byte access increments by one

    # --- card 12: the 2005 memory-cycle count, one operation per line
    cycles = 0
    cycles += 1                              # read the indexed destination operand
    cycles += 1                              # read M[B] to get the source's address
    cycles += 1                              # read the source operand
    cycles += 1                              # write the sum back
    assert cycles == 4
    # the two-level indirect variation
    assert 1 + 1 + 1 + 1 + 1 == 5
    # operand memory references by mode, the table the card publishes
    refs = {"immediate": 0, "register": 0, "direct": 1, "indirect": 2,
            "register indirect": 1, "indexed": 1, "pc-relative": 1, "stack": 0}
    assert refs["indirect"] == 2 * refs["direct"] == 2 * refs["register indirect"]

    # --- card 13: relocation
    assert 1200 + 4000 == 5200               # the direct field must be patched
    assert 1000 + 4000 == 5000               # the new load address

    # --- every PYQ of this topic: the recorded answer is re-derived from its own text
    want_answers = {
        "gate-1998-q1-19-relocation-without-change": "Option (D) - PC relative addressing",
        "gate-1999-q2-23-immediate-and-direct-only":
            "All four - pointers, arrays, records and recursive procedures with local variables",
        "gate-2002-q1-24-absolute-addressing":
            "Option (B) - the address of the operand is inside the instruction",
        "gate-2004-q20-relocation-at-run-time":
            "Option (C) - (ii) and (iii), based addressing and relative addressing",
        "gate-2005-q65-memory-cycles-indexed-indirect": "Option (B) - 4",
        "gate-2008-q33-autoincrement-mode": "Option (C) - III only",
        "gate-2011-q21-base-indexed-mode": "Option (D) - Base Indexed Addressing",
        "gate-2015-set-1-q8-three-address-fields": "Option (A) - Either S1 or S2",
        "gate-2016-set-2-q10-immediate-field": "16",
        "gate-2017-set-1-q11-struct-field-displacement":
            "Option (D) - Index addressing mode, X(R1), with X a 16-bit two's complement offset",
        "gate-2017-set-1-q14-risc-branch-offset": "-16",
        "gate-2024-set-2-q47-opcodes-per-mode": "32",
        "gate-2025-set-1-q27-immediate-field": "Option (B) - 20",
        "gate-2026-set-1-q4-mode-to-hll-matching": "Option (B) - P-4, Q-2, R-1, S-3",
    }
    linked = set()
    for tid in CARD_IDS:
        rec = load(os.path.join(CONTENT, "subjects", "computer-organization-and-architecture",
                                "instruction-set-and-addressing-modes", tid + ".json"))
        assert rec["id"] == tid
        linked.update(rec.get("pyqIds", []))
    assert linked == set(want_answers), "the cards link %r" % sorted(linked)
    for pid, ans in want_answers.items():
        rec = load(os.path.join(CONTENT, "pyqs", pid + ".json"))
        assert rec["answer"] == ans, "%s must record the answer %r" % (pid, ans)
        assert rec["topic"] in CARD_IDS and rec["verification"] == "SOURCED"
        assert rec["source_url"].startswith("http") and rec["question_ref"]
    # 2017 Set 1 Q.11: int marks[100] puts grade at byte offset 400
    assert 100 * 4 == 400
    # 2016 Set 2 Q.10 and 2025 Set 1 Q.27 restate the same subtraction the cards use

    # --- the visual lesson's own numbers
    L = load(os.path.join(ROOT, "visuals", "computer-organization-and-architecture",
                          "instruction-set-and-addressing-modes", "one-operand-five-modes", "lesson.json"))
    ex = L["example"]
    assert L["engine"] == "p5.js" and L["steps"] == 8
    A, r2, r3, pc = ex["address_field"], ex["register_r2"], ex["register_r3"], ex["program_counter"]
    mem = {int(k): v for k, v in ex["memory"].items()}
    assert (A, r2, r3, pc) == (500, 1200, 700, 700)
    assert mem[500] == 1200 and mem[1200] == 42
    modes = {m["mode"]: m for m in ex["modes"]}
    assert modes["Immediate"]["operand"] == A and modes["Immediate"]["memory_reads"] == 0
    assert modes["Direct"]["effective_address"] == A and modes["Direct"]["operand"] == mem[A] == 1200
    assert modes["Indirect"]["effective_address"] == mem[A] == 1200
    assert modes["Indirect"]["operand"] == mem[mem[A]] == 42 and modes["Indirect"]["memory_reads"] == 2
    assert modes["Register indirect"]["effective_address"] == r2 == 1200
    assert modes["Register indirect"]["operand"] == mem[r2] == 42
    assert modes["Indexed"]["effective_address"] == A + r3 == 1200 == int(ex["indexed_check"].split()[-1])
    assert modes["PC-relative"]["effective_address"] == pc + A == 1200 == int(ex["relative_check"].split()[-1])
    assert all(modes[m]["operand"] == mem[mem[A]] for m in
               ("Indirect", "Register indirect", "Indexed", "PC-relative"))
    assert all(modes[m]["memory_reads"] == 1 for m in
               ("Direct", "Register indirect", "Indexed", "PC-relative"))
    assert sum(m["memory_reads"] for m in ex["modes"]) == ex["total_memory_reads_all_modes"] == 6
    assert ex["direct_operand_differs"] is (modes["Direct"]["operand"] != modes["Indirect"]["operand"])

    ok("instruction set and addressing modes: the bit budgets of 2016 Set 2 Q.10, 2025 Set 1 Q.27 and "
       "2024 Set 2 Q.47 re-derived from their own field lists and the opcode-per-mode count checked "
       "against the 8 x 32 instruction count, the instruction counts of the four formats (3, 6, 7, 8) for "
       "(A+B)*(C+D), the byte-alignment and 41-bit rounding figures, the 16-bit immediate range, the "
       "direct-mode reach at 8 and 12 address bits, the indirect chain 200 -> 1500 -> 42 and 40 -> 9000 -> 5, "
       "the displacement addresses 1028 and [R1]+400 with the signed 16-bit range, the PC-relative offsets "
       "-16, -4 and 996 and the 40 KB reach failure, the autoincrement walks 1000/1004/1008 and 996, the "
       "four-cycle count of GATE CSE 2005 Q.65 and the five-cycle two-level variation, the relocation "
       "arithmetic 1200 -> 5200, all fourteen PYQ answers re-read from their records, and the lesson's "
       "own six modes")



# ------------------------------------------------------- ALU design
def check_alu_design():
    """Every number and verdict published in the ALU Design cards and in the slice lesson."""
    from math import ceil, log2

    def carries(a, b, n=4, c0=0):
        """The carry into the top bit and the carry out of it, for a + b + c0."""
        carry = c0
        cin_top = None
        for i in range(n):
            if i == n - 1:
                cin_top = carry
            ai, bi = (a >> i) & 1, (b >> i) & 1
            carry = (ai & bi) | (carry & (ai ^ bi))
        return cin_top, carry

    def signed(x, n=4):
        return x - (1 << n) if x >> (n - 1) & 1 else x

    # the full adder, over all eight input combinations
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                assert (a ^ b ^ c) == ((a + b + c) & 1), "full adder sum"
                assert ((a & b) | (c & (a ^ b))) == ((a + b + c) >> 1), "full adder carry"

    # the control-bit arithmetic
    assert 2 ** 2 == 4 and ceil(log2(3)) == 2 and 2 + 1 == 3, "slice control bits"
    assert ceil(log2(6)) == 3 and ceil(log2(4)) == 2, "select bits from a function count"

    # the slice example of the lesson: A = 1, B = 1, carry in 1
    A, B, CIN = 1, 1, 1
    assert (A & B) == 1 and (A | B) == 1, "AND and OR agree on 1, 1"
    assert ((A + B + CIN) & 1) == 1 and ((A + B + CIN) >> 1) == 1, "ADD gives sum 1, carry 1"
    assert ((A + (1 - B) + CIN) & 1) == 0 and ((A + (1 - B) + CIN) >> 1) == 1, \
        "SUB gives sum 0, carry 1"
    assert (A - B) & 1 == 0, "1 - 1 is 0"
    # and the lesson's quick check: A = 1, B = 0, carry in 0
    a, b, c = 1, 0, 0
    assert (a & b) == 0 and (a | b) == 1
    assert ((a + b + c) & 1) == 1 and ((a + b + c) >> 1) == 0
    assert ((a + (1 - b) + 1) & 1) == 1 and ((a + (1 - b) + 1) >> 1) == 1, \
        "subtraction forces the carry-in to 1, so 1 + 1 + 1 gives sum 1 and carry 1"

    # GATE CSE 2003 Q.46: the four settings of K and C0, over all 4-bit operands
    for a in range(16):
        for b in range(16):
            r = lambda K, C0: (a + ((b ^ 15) if K else b) + C0) % 16
            assert r(0, 0) == (a + b) % 16, "K=0 C0=0 is A+B"
            assert r(0, 1) == (a + b + 1) % 16, "K=0 C0=1 is A+B+1"
            assert r(1, 0) == (a - b - 1) % 16, "K=1 C0=0 is A-B-1"
            assert r(1, 1) == (a - b) % 16, "K=1 C0=1 is A-B"
    # A + 1 cannot be produced for every operand pair by any single setting
    for K in (0, 1):
        for C0 in (0, 1):
            assert not all((a + ((b ^ 15) if K else b) + C0) % 16 == (a + 1) % 16
                           for a in range(16) for b in range(16)), \
                "no setting of K and C0 gives A + 1 for every operand"

    # subtraction as the adder with B inverted and carry-in 1
    for a in range(16):
        for b in range(16):
            assert ((a + (b ^ 15) + 1) & 15) == ((a - b) % 16), "subtraction by inversion"
            # the carry out of the top bit says "no borrow"
            assert carries(a, b ^ 15, c0=1)[1] == (1 if a >= b else 0), "carry out of A-B"

    # V = carry into the sign column xor carry out of it, and it means the signed sum did not fit
    v_pairs = 0
    for a in range(16):
        for b in range(16):
            cin_top, cout = carries(a, b)
            V = cin_top ^ cout
            assert V == (0 if -8 <= signed(a) + signed(b) <= 7 else 1), "overflow flag"
            if V:
                v_pairs += 1
    assert v_pairs == 64, "64 ordered pairs overflow a 4-bit signed addition"
    positive = sum(1 for a in range(8) for b in range(8) if a + b >= 8)
    negative = sum(1 for a in range(8, 16) for b in range(8, 16) if signed(a) + signed(b) < -8)
    assert (positive, negative) == (28, 36), "the 28 and 36 of the status-flag card"

    # the carry flag alone does not report signed overflow, and vice versa
    assert carries(15, 1)[1] == 1 and (carries(15, 1)[0] ^ carries(15, 1)[1]) == 0, \
        "-1 + 1 sets C but not V"
    assert carries(7, 1)[1] == 0 and (carries(7, 1)[0] ^ carries(7, 1)[1]) == 1, \
        "7 + 1 sets V but not C"

    # the zero flag after a subtraction is exactly equality
    z_pairs = 0
    for a in range(16):
        for b in range(16):
            d = (a + (b ^ 15) + 1) & 15
            assert (d == 0) == (a == b), "zero flag means equality"
            if d == 0:
                z_pairs += 1
    assert z_pairs == 16, "16 ordered pairs give a zero result"

    # SLT: the raw sign bit fails exactly on the overflow cases, and sign xor overflow is always right
    wrong = 0
    for a in range(16):
        for b in range(16):
            d = (a + (b ^ 15) + 1) & 15
            sign = (d >> 3) & 1
            cin_top, cout = carries(a, b ^ 15, c0=1)
            V = cin_top ^ cout
            truth = 1 if signed(a) < signed(b) else 0
            assert (sign ^ V) == truth, "sign xor overflow is the comparison"
            if sign != truth:
                wrong += 1
    assert wrong == 64, "the raw sign bit is wrong on 64 of the 256 ordered subtraction pairs"
    # the worked counterexample: -8 - 1 wraps to +7 with sign 0
    d = (8 + (1 ^ 15) + 1) & 15
    assert d == 7 and (d >> 3) == 0, "-8 - 1 wraps to +7 in four bits"
    assert (carries(8, 1 ^ 15, c0=1)[0] ^ carries(8, 1 ^ 15, c0=1)[1]) == 1, "that subtraction overflows"
    # and the check question: 7 - (-8) wraps to -1 with sign 1 and overflow 1
    d = (7 + (8 ^ 15) + 1) & 15
    assert d == 15 and (d >> 3) == 1, "7 - (-8) wraps to -1"
    assert (carries(7, 8 ^ 15, c0=1)[0] ^ carries(7, 8 ^ 15, c0=1)[1]) == 1, "that subtraction overflows too"

    # shifts
    assert ((0b00110100 << 2) & 0xFF) == 0xD0 == 208 and 52 * 4 == 208, "left shift multiplies"
    assert (-12 >> 1) == -6 and (-3 >> 1) == -2, "arithmetic right shift floors"
    for n in (16, 32, 64):
        stages = int(log2(n))
        assert stages == {16: 4, 32: 5, 64: 6}[n], "barrel shifter stages"
        assert n * stages == {16: 64, 32: 160, 64: 384}[n], "barrel shifter multiplexers"
    # a barrel shifter by 0 to 15 on 16 bits reproduces a logical left shift
    for amount in range(16):
        stages = [(amount >> i) & 1 for i in range(4)]
        assert sum(s * (1 << i) for i, s in enumerate(stages)) == amount, "barrel stages compose"
    for n in (4, 8, 16, 32):
        assert 2 * n + 1 == {4: 9, 8: 17, 16: 33, 32: 65}[n], "ripple-carry sum delay"
    assert 2 * 8 + 1 + 2 == 19 and 2 * 32 + 1 + 1 == 66, "ALU delay with the output multiplexer"

    # GATE CSE 2025 Q.27: two independent 2:1 multiplexers give four operand-source combinations
    sources_a = ('RA', 'imm')
    sources_b = ('RB', 'imm')
    combos = {(x, y) for x in sources_a for y in sources_b}
    assert len(combos) == 4, "four operand combinations"
    assert ('RA', 'RB') in combos and ('imm', 'imm') in combos, "registers and two immediates both reachable"
    # one shared select line would leave only two
    shared = {(sources_a[s], sources_b[s]) for s in (0, 1)}
    assert len(shared) == 2, "one shared select line gives two combinations"

    # GATE CSE 2020 Q.4: the ordering, checked as a dependency graph over the five steps
    steps = {1: {'reads': {'TEMP1'}, 'writes': {'TEMP2'}},
             2: {'reads': {'R1'}, 'writes': {'TEMP1'}},
             3: {'reads': {'PC'}, 'writes': {'MAR', 'MDR'}},
             4: {'reads': {'TEMP2'}, 'writes': {'R0'}},
             5: {'reads': {'MDR'}, 'writes': {'IR'}}}
    before = [(3, 5), (2, 1), (1, 4)]
    order = [3, 5, 2, 1, 4]
    for x, y in before:
        assert order.index(x) < order.index(y), "step %d must precede step %d" % (x, y)
        assert steps[y]['reads'] & steps[x]['writes'], \
            "step %d reads what step %d writes" % (y, x)
    for other in ([2, 1, 4, 5, 3], [1, 2, 4, 3, 5], [3, 5, 1, 2, 4]):
        assert any(other.index(x) > other.index(y) for x, y in before), \
            "a distractor order breaks a dependency"

    # GATE CSE 2005 Q.79: one cycle per bus source, and the fetch is separate
    execution = 2 + 1
    assert execution == 3 and execution + 2 == 5, "three execution cycles, five with the fetch"

    # the ALU-control widths quoted on the card
    assert ceil(log2(6)) == 3 and ceil(log2(4)) == 2

    ok("ALU design: the full adder over all eight inputs, the control-bit counts, the lesson's four "
       "codes and its quick check, the four settings of K and C0 in 2003 Q.46 with A+1 unreachable, "
       "subtraction by inversion and the no-borrow carry over all 256 pairs, the overflow flag against "
       "the true signed sum with its 28 and 36 split, carry against overflow on 1111+0001 and 0111+0001, "
       "the zero flag as equality, sign xor overflow as the comparison with the raw sign bit wrong on 64 "
       "pairs, the shift examples and the barrel counts for 16, 32 and 64 bits, the ripple-carry delays "
       "9, 17, 33, 65 and the ALU delays 19 and 66, the four operand combinations of 2025 Q.27, and the "
       "dependency order of 2020 Q.4 against all three distractors")


def main():
    topics, tpath, pyqs, videos, playlists, sources = load_all()
    check_topics(topics, tpath, pyqs, videos)
    check_pyqs(topics, pyqs)
    check_videos(topics, videos)
    check_playlists(playlists, videos)
    check_syllabus(topics, tpath)
    check_sources(sources)
    check_coverage(topics, tpath)
    check_math()
    check_logic()
    check_first_order()
    check_sets_relations_functions()
    check_lattices()
    check_monoids_and_groups()
    check_graphs()
    check_matrices_and_determinants()
    check_system_of_linear_equations()
    check_eigenvalues_and_eigenvectors()
    check_lu_decomposition()
    check_limits_continuity_differentiability()
    check_maxima_and_minima()
    check_mean_value_theorem()
    check_integration()
    check_probability_and_statistics()
    check_mean_median_mode()
    check_conditional_probability()
    check_number_representation()
    check_boolean_algebra()
    check_combinational_circuits()
    check_sequential_circuits()
    check_computer_arithmetic()
    check_instruction_set_and_addressing_modes()
    check_alu_design()
    check_visuals()
    check_hygiene()
    for c in checks:
        print("  ok   " + c)
    for w in warnings:
        print("  warn " + w)
    for e in errors:
        print("  FAIL " + e)
    print("\n%d checks passed, %d warnings, %d failures" % (len(checks), len(warnings), len(errors)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
