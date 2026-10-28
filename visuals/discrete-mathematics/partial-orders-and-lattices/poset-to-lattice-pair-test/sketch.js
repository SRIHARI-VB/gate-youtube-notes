/* From poset to lattice: the pair-by-pair test on the GATE CSE 2017 Set 2 Q.21 poset.
   Every join and meet shown here is recomputed in scripts/validate.py (check_lattices), which
   enumerates all pairs of the poset and checks the LUB and GLB of each against the drawing. */
window.LESSON = {
  steps: [
    {
      duration: 2600,
      caption: 'The poset X = {a, b, c, d, e}: a is below everything, e is above everything, b is below c, and d sits on its own between a and e. A Hasse diagram draws one segment per covering pair and nothing else.',
      draw: function (p, w, h) {
        ink(); head('The poset, drawn as its Hasse diagram', 30, 32);
        diagram(FULL, {}, p, w, h);
        panel(w - 210, 60, ['a is the least element', 'e is the greatest element', 'b < c', 'a < d < e'], 1, w);
        note('5 elements, 5 covering pairs, 13 ordered pairs in the relation', 30, h - 24);
      }
    },
    {
      duration: 2800,
      caption: 'A lattice needs a join and a meet for every pair. Start with the incomparable pair b and d: the elements above both of them are e alone, so the join is e.',
      draw: function (p, w, h) {
        ink(); head('Pair {b, d}: the upper bounds', 30, 32);
        diagram(FULL, { pair: ['b', 'd'], join: 'e', showUpper: true }, p, w, h);
        panel(w - 210, 60, ['upper bounds of {b, d}: e', 'so b v d = e', 'join exists'], 1, w);
        note('only incomparable pairs need checking: a comparable pair has its own join and meet', 30, h - 24);
      }
    },
    {
      duration: 2800,
      caption: 'The same pair below: the only element under both b and d is a, so the meet is a. The pair {b, d} has both bounds.',
      draw: function (p, w, h) {
        ink(); head('Pair {b, d}: the lower bounds', 30, 32);
        diagram(FULL, { pair: ['b', 'd'], meet: 'a', showLower: true }, p, w, h);
        panel(w - 210, 60, ['lower bounds of {b, d}: a', 'so b ^ d = a', 'meet exists'], 1, w);
        note('b ^ d = a and b v d = e: this pair is settled', 30, h - 24);
      }
    },
    {
      duration: 2800,
      caption: 'The other incomparable pair is c and d. Above both there is only e, below both there is only a, so c v d = e and c ^ d = a. The pair {b, c} is comparable, so it needs no work.',
      draw: function (p, w, h) {
        ink(); head('Pair {c, d}: both bounds at once', 30, 32);
        diagram(FULL, { pair: ['c', 'd'], join: 'e', meet: 'a', showUpper: true, showLower: true }, p, w, h);
        panel(w - 210, 60, ['c v d = e', 'c ^ d = a', 'b and c are comparable', 'every pair is settled'], 1, w);
        note('two incomparable pairs, four bounds, all of them inside X', 30, h - 24);
      }
    },
    {
      duration: 3000,
      caption: 'Every pair has a join and a meet inside X, so the poset is already a lattice. The minimum number of ordered pairs that must be added is 0 - the answer to GATE CSE 2017 Set 2 Q.21.',
      draw: function (p, w, h) {
        ink(); head('Already a lattice: add 0 pairs', 30, 32);
        diagram(FULL, { allGreen: true }, p, w, h);
        panel(w - 210, 60, ['all 10 pairs checked', 'each has a join and a meet', 'answer: 0'], 1, w);
        note('the lattice test is a sweep over pairs, never a judgement about the shape', 30, h - 24);
      }
    },
    {
      duration: 3200,
      caption: 'Now delete the single covering pair d to e. The pair {b, d} has no element above both, so it has no join, and the poset is no longer a lattice. Adding that one pair back repairs it, which is what "minimum number of pairs to add" means when the answer is not 0.',
      draw: function (p, w, h) {
        ink(); head('Break one edge: no join for {b, d}', 30, 32);
        diagram(BROKEN, { pair: ['b', 'd'], missingJoin: true, addBack: true }, p, w, h);
        panel(w - 210, 60, ['remove d < e', '{b, d} has no upper bound', 'not a lattice', 'add 1 pair: d < e'], 1, w);
        note('one missing bound is enough to refute the lattice property', 30, h - 24);
      }
    }
  ]
};

var POS = { a: [0.50, 0.90], b: [0.32, 0.58], c: [0.32, 0.26], d: [0.72, 0.58], e: [0.50, 0.08] };
var FULL = [['a', 'b'], ['a', 'd'], ['b', 'c'], ['c', 'e'], ['d', 'e']];
var BROKEN = [['a', 'b'], ['a', 'd'], ['b', 'c'], ['c', 'e']];

function ink() {
  var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  background(dark ? color(23, 28, 36) : color(255));
  noStroke(); fill(dark ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}
function head(t, x, y) { textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function note(t, x, y) { textSize(12.5); fill(90, 100, 116); noStroke(); text(t, x, y); }
function panel(x, y, lines, prog, w) {
  noStroke(); fill(232, 238, 255);
  var bw = Math.min(w - x - 14, 200);
  rect(x, y, bw, 22 + lines.length * 20, 8);
  fill(31, 94, 255); textSize(12); textStyle(BOLD); text('what the diagram shows', x + 10, y + 17);
  textStyle(NORMAL); textSize(11.5); fill(31, 60, 140);
  for (var i = 0; i < lines.length; i++) { text(lines[i], x + 10, y + 36 + i * 19); }
}
function xy(k, w, h) { var s = POS[k]; return [40 + s[0] * (w - 250), 50 + s[1] * (h - 90)]; }

function diagram(edges, opt, prog, w, h) {
  var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  var lineCol = dark ? color(120, 130, 145) : color(190, 196, 206);
  var accent = color(31, 94, 255), good = color(20, 107, 74), bad = color(180, 69, 31);
  var pairs = opt.pair || [];
  for (var i = 0; i < edges.length; i++) {
    var e0 = edges[i], A = xy(e0[0], w, h), B = xy(e0[1], w, h);
    var on = pairs.indexOf(e0[0]) >= 0 || pairs.indexOf(e0[1]) >= 0;
    stroke(on ? accent : lineCol); strokeWeight(on ? 2.6 : 1.6);
    line(A[0], A[1], B[0], B[1]);
  }
  if (opt.addBack) {
    var D = xy('d', w, h), E = xy('e', w, h);
    stroke(bad); strokeWeight(2.2); dashed(D[0], D[1], E[0], E[1]);
    fill(bad); noStroke(); textSize(11); text('add this pair back', (D[0] + E[0]) / 2 + 8, (D[1] + E[1]) / 2);
  }
  for (var k in POS) {
    var P = xy(k, w, h);
    var isPair = pairs.indexOf(k) >= 0;
    var isJoin = opt.join === k, isMeet = opt.meet === k;
    var col = isJoin ? good : (isMeet ? accent : (isPair ? (opt.missingJoin ? bad : accent) : (opt.allGreen ? good : (dark ? color(210) : color(60)))));
    noStroke(); fill(col);
    ellipse(P[0], P[1], isPair || isJoin || isMeet ? 26 : 20, isPair || isJoin || isMeet ? 26 : 20);
    fill(255); textSize(12); textStyle(BOLD); textAlign(CENTER, CENTER);
    text(k, P[0], P[1] - 0.5); textAlign('left', 'baseline'); textStyle(NORMAL);
    if (isJoin || isMeet) {
      fill(isJoin ? good : accent); textSize(11);
      text(isJoin ? 'join' : 'meet', P[0] + 16, P[1] + 4);
    }
  }
  if (opt.missingJoin) {
    var B2 = xy('b', w, h), D2 = xy('d', w, h);
    fill(bad); noStroke(); textSize(11.5);
    text('nothing above both', Math.min(B2[0], D2[0]) - 6, Math.min(B2[1], D2[1]) - 16);
  }
}

/* A dashed segment, drawn by hand so the lesson needs no drawing-context API. */
function dashed(x1, y1, x2, y2) {
  var dx = x2 - x1, dy = y2 - y1, len = Math.sqrt(dx * dx + dy * dy);
  if (!isFinite(len) || len === 0) { return; }
  var step = 9, t = 0;
  while (t < len) {
    var a = t / len, b = Math.min((t + step * 0.6) / len, 1);
    line(x1 + dx * a, y1 + dy * a, x1 + dx * b, y1 + dy * b);
    t += step;
  }
}
