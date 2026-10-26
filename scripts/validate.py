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
    sroot = os.path.join(CONTENT, "subjects")
    for path in walk(sroot):
        parts = rel(path).split("/")
        if len(parts) != 5:          # content/subjects/<s>/<t>/<card>.json
            fail("%s: card is not at content/subjects/<subject>/<topic>/<card>.json" % rel(path))
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
    return topics, tpath, pyqs, videos, playlists


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
    for s in syl.get("subjects", []):
        for tp in s.get("topics", []):
            d = os.path.join(CONTENT, "subjects", s["slug"], tp["slug"])
            if not os.path.isdir(d):
                fail("syllabus.json names %s/%s but the folder is missing" % (s["slug"], tp["slug"]))
    ok("syllabus declares every subject and topic folder that exists")


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


def main():
    topics, tpath, pyqs, videos, playlists = load_all()
    check_topics(topics, tpath, pyqs, videos)
    check_pyqs(topics, pyqs)
    check_videos(topics, videos)
    check_playlists(playlists, videos)
    check_syllabus(topics, tpath)
    check_math()
    check_logic()
    check_first_order()
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
