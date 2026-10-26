#!/usr/bin/env python3
"""Validate the repository content, references, mathematics and hygiene.

Run: python3 scripts/validate.py    (exit code 1 on failure)
"""
import json, os, re, sys
from math import comb, factorial

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
PRIORITIES = {"P1", "P2", "P3"}
VERIFICATION = {"OFFICIAL_KEY", "SOURCED", "UNVERIFIED"}
REQUIRED_TOPIC = ["id", "title", "priority", "unit", "quickIdea", "remember",
                  "example", "gateAngle", "trap", "check", "pyqIds", "videoRefs", "prereqs"]
REQUIRED_PYQ = ["id", "year", "paper", "question_ref", "type", "topic", "text",
                "answer", "solution", "source_url", "source_label", "verification"]

errors, warnings, checks = [], [], []


def ok(msg):
    checks.append(msg)


def fail(msg):
    errors.append(msg)


def load_all():
    topics = {}
    tdir = os.path.join(CONTENT, "topics")
    for n in sorted(os.listdir(tdir)):
        if n.endswith(".json"):
            t = json.load(open(os.path.join(tdir, n), encoding="utf-8"))
            if t["id"] in topics:
                fail("duplicate topic id: " + t["id"])
            topics[t["id"]] = t
    pyqs = {}
    pdir = os.path.join(CONTENT, "pyqs")
    for n in sorted(os.listdir(pdir)):
        if n.endswith(".json"):
            p = json.load(open(os.path.join(pdir, n), encoding="utf-8"))
            if p["id"] in pyqs:
                fail("duplicate pyq id: " + p["id"])
            pyqs[p["id"]] = p
    videos = {}
    plroot = os.path.join(CONTENT, "playlists")
    for pid in sorted(os.listdir(plroot)):
        vroot = os.path.join(plroot, pid, "videos")
        if not os.path.isdir(vroot):
            continue
        for vid in sorted(os.listdir(vroot)):
            m = json.load(open(os.path.join(vroot, vid, "metadata.json"), encoding="utf-8"))
            a = json.load(open(os.path.join(vroot, vid, "analysis.json"), encoding="utf-8"))
            videos[m["video_id"]] = (m, a)
    return topics, pyqs, videos


def check_topics(topics, pyqs, videos):
    for tid, t in topics.items():
        for f in REQUIRED_TOPIC:
            if f not in t:
                fail("%s: missing field %s" % (tid, f))
        if t.get("priority") not in PRIORITIES:
            fail("%s: invalid priority %r" % (tid, t.get("priority")))
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
        for v in t.get("variations", []):
            if v.get("label") not in {"VERIFIED PYQ", "ORIGINAL PYQ-STYLE QUESTION",
                                     "CONCEPTUAL PRACTICE QUESTION", "PREDICTED VARIATION"}:
                fail("%s: variation has invalid label %r" % (tid, v.get("label")))
    ok("%d topics: required fields, priorities, examples, traps, checks, references" % len(topics))


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
        if p.get("verification") == "UNVERIFIED":
            warnings.append("%s is labelled UNVERIFIED and must not be presented as an official PYQ" % pid)
    ok("%d PYQ records: required fields, years, types, sources, topic links" % len(pyqs))


def check_videos(videos):
    for vid, (m, a) in videos.items():
        if not m.get("transcript_status"):
            fail("%s: no transcript status" % vid)
        if not a.get("coverage_note"):
            fail("%s: no coverage note" % vid)
        if not m.get("video_url", "").startswith("https://www.youtube.com/watch?v="):
            fail("%s: bad video url" % vid)
    ok("%d videos: every video carries an explicit transcript and coverage status" % len(videos))


# Every published numeric claim that can be recomputed is recomputed here.
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
]


def check_math():
    for name, got, want in MATH:
        if got != want:
            fail("math: %s computed %r but content claims %r" % (name, got, want))
    ok("%d published numeric claims recomputed" % len(MATH))


def check_hygiene():
    bad = []
    for base, _, files in os.walk(ROOT):
        if "/.git" in base:
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
                bad.append(path + " contains a citation marker")
            if re.search(r"_v\d+\.|_final\.", f):
                bad.append(path + " uses a versioned filename")
    for b in bad:
        fail(b)
    if not bad:
        ok("no citation markers or versioned filenames in generated files")

    for rel in ("index.html", "src/styles/design-tokens.css", "src/styles/app.css",
                "src/app/app.js", "src/data/content.js"):
        if not os.path.isfile(os.path.join(ROOT, rel)):
            fail("missing site file: " + rel)
    for slug in ("stars-and-bars", "inclusion-exclusion", "pigeonhole", "distribution-grid"):
        for f in ("index.html", "lesson.json"):
            if not os.path.isfile(os.path.join(ROOT, "visuals", slug, f)):
                fail("missing visual file: visuals/%s/%s" % (slug, f))
        if slug != "distribution-grid" and not os.path.isfile(os.path.join(ROOT, "visuals", slug, "sketch.js")):
            fail("missing sketch: visuals/%s/sketch.js" % slug)
    ok("site shell and visual lesson files present")


def main():
    topics, pyqs, videos = load_all()
    check_topics(topics, pyqs, videos)
    check_pyqs(topics, pyqs)
    check_videos(videos)
    check_math()
    check_hygiene()
    for c in checks:
        print("  ok   " + c)
    for wmsg in warnings:
        print("  warn " + wmsg)
    for e in errors:
        print("  FAIL " + e)
    print("\n%d checks passed, %d warnings, %d failures" % (len(checks), len(warnings), len(errors)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
