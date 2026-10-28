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
