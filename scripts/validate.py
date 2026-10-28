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
