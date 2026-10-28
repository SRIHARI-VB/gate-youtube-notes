/* The three cases of a 2 by 2 system, seen twice: as two lines that may cross, be parallel or coincide,
   and as the rank comparison that decides which of the three you are looking at.

   Every determinant, rank, verdict and solution shown here is recomputed in scripts/validate.py
   (check_system_of_linear_equations), including the two k cases from GATE CSE 2025 Set 1 Q.13. */

var SYSTEMS = [
  { A: [[1, 0], [0, 1]], b: [2, 1],
    caption: "Start with the identity. The two equations are x = 2 and y = 1, two lines that cross at the point (2, 1). The determinant is 1 and the columns of A are the two coordinate directions, so every b in the plane is reachable: one solution, always." },
  { A: [[1, 1], [1, -1]], b: [3, 1],
    caption: "A = [[1,1],[1,-1]] with b = (3,1). Row picture: the lines x + y = 3 and x - y = 1 cross at (2, 1). Column picture: 2 times the column (1,1) plus 1 times the column (1,-1) is exactly (3,1). The determinant is -2, not zero, so rank(A) = rank([A|b]) = 2 = n and the solution is unique." },
  { A: [[1, 1], [2, 2]], b: [1, 2],
    caption: "Now make the second row twice the first: x + y = 1 and 2x + 2y = 2. Both equations describe the same line, so every point on it solves the system. The determinant is 0, rank(A) = rank([A|b]) = 1, which is below n = 2, so there are infinitely many solutions with one free parameter." },
  { A: [[1, 1], [2, 2]], b: [1, 3],
    caption: "Keep the same singular A and change only b: x + y = 1 and 2x + 2y = 3, that is 2x + 2y = 3 against 2x + 2y = 2. The lines are parallel and distinct. The determinant is still 0, but now rank([A|b]) = 2 while rank(A) = 1, so the system has no solution. This is the whole point: the determinant alone cannot tell these two steps apart." },
  { A: [[1, 1], [1, 1]], b: [1, -1],
    caption: "The parameter case from GATE CSE 2025 Set 1 Q.13, at k = 1. The system x + ky = 1, kx + y = -1 becomes x + y = 1 and x + y = -1: two parallel lines, no solution. The determinant 1 - k^2 is 0 here, and rank([A|b]) = 2 against rank(A) = 1." },
  { A: [[1, -1], [-1, 1]], b: [1, -1],
    caption: "The same family at k = -1. The system becomes x - y = 1 and -x + y = -1, which is the same equation twice: the line x - y = 1. The determinant is 0 again, but now rank([A|b]) = rank(A) = 1, so there are infinitely many solutions. Same determinant, opposite answer, which is why every parameter question needs the consistency check as well." },
  { A: [[1, -1], [-1, 1]], b: [1, -1],
    caption: "The decision order to carry into the exam: compute the determinant. If it is not zero, the solution is unique and you are done. If it is zero, compare rank(A) with rank([A|b]): a difference means no solution, equality means infinitely many solutions with n - rank(A) free parameters. A determinant of zero is never the answer on its own." }
];

var BLUE = [31, 94, 255], ORANGE = [180, 90, 31], RED = [170, 40, 45], GREEN = [20, 107, 74];
var LO = -5, HI = 5;

function darkMode() {
  return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
}

function inkBg() {
  var d = darkMode();
  background(d ? color(23, 28, 36) : color(255));
  noStroke();
  fill(d ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}

function frame2() {
  var w = 800, h = 500;
  var padL = 56, padR = 300, padT = 34, padB = 40;
  var pw = w - padL - padR, ph = h - padT - padB;
  var s = Math.min(pw / (HI - LO), ph / (HI - LO));
  return { w: w, h: h, padL: padL, padT: padT, s: s,
           ox: padL + (pw - s * (HI - LO)) / 2, oy: padT + (ph + s * (HI - LO)) / 2 };
}

function toPixel(f, x, y) { return [f.ox + (x - LO) * f.s, f.oy - (y - LO) * f.s]; }

function drawGrid(f) {
  var d = darkMode();
  var faint = d ? color(48, 55, 66) : color(232, 236, 242);
  var grey = d ? color(78, 86, 99) : color(200, 206, 214);
  strokeWeight(1);
  for (var i = LO; i <= HI; i++) {
    stroke(faint);
    var a = toPixel(f, i, LO), b2 = toPixel(f, i, HI);
    line(a[0], a[1], b2[0], b2[1]);
    var c = toPixel(f, LO, i), e = toPixel(f, HI, i);
    line(c[0], c[1], e[0], e[1]);
  }
  stroke(grey);
  var o = toPixel(f, 0, 0), xr = toPixel(f, HI, 0), yt = toPixel(f, 0, HI);
  line(o[0], o[1], xr[0], xr[1]);
  line(o[0], o[1], yt[0], yt[1]);
  noStroke();
  fill(d ? color(150, 158, 170) : color(120, 128, 140));
  textSize(10.5); textAlign('center', 'top');
  for (var k = LO + 1; k <= HI - 1; k++) {
    if (k === 0) { continue; }
    var q = toPixel(f, k, 0);
    text(String(k), q[0], q[1] + 4);
  }
  textAlign('left', 'baseline');
}

/* a x + b y = c drawn across the visible window */
function drawConstraint(f, a, b, c, col, dashed) {
  var x0 = LO, x1 = HI, y0, y1;
  stroke(col[0], col[1], col[2]);
  strokeWeight(2.2);
  if (Math.abs(b) > 1e-9) {
    y0 = (c - a * x0) / b;
    y1 = (c - a * x1) / b;
    var p0 = toPixel(f, x0, y0), p1 = toPixel(f, x1, y1);
    if (dashed) {
      var steps = 24;
      for (var i = 0; i < steps; i += 2) {
        var t0 = i / steps, t1 = (i + 1) / steps;
        line(p0[0] + (p1[0] - p0[0]) * t0, p0[1] + (p1[1] - p0[1]) * t0,
             p0[0] + (p1[0] - p0[0]) * t1, p0[1] + (p1[1] - p0[1]) * t1);
      }
    } else {
      line(p0[0], p0[1], p1[0], p1[1]);
    }
  } else if (Math.abs(a) > 1e-9) {
    var xv = c / a;
    var q0 = toPixel(f, xv, LO), q1 = toPixel(f, xv, HI);
    line(q0[0], q0[1], q1[0], q1[1]);
  }
  noStroke();
}

function detOf2(A) { return A[0][0] * A[1][1] - A[0][1] * A[1][0]; }

function rankOf(M) {
  var R = [], i, j;
  for (i = 0; i < M.length; i++) { R.push(M[i].slice()); }
  var rows = R.length, cols = R[0].length, r = 0;
  for (var c = 0; c < cols && r < rows; c++) {
    var piv = -1;
    for (i = r; i < rows; i++) { if (Math.abs(R[i][c]) > 1e-9) { piv = i; break; } }
    if (piv < 0) { continue; }
    var tmp = R[r]; R[r] = R[piv]; R[piv] = tmp;
    var pv = R[r][c];
    for (j = c; j < cols; j++) { R[r][j] = R[r][j] / pv; }
    for (i = 0; i < rows; i++) {
      if (i === r) { continue; }
      var factor = R[i][c];
      if (Math.abs(factor) < 1e-9) { continue; }
      for (j = c; j < cols; j++) { R[i][j] = R[i][j] - factor * R[r][j]; }
    }
    r++;
  }
  return r;
}

function augmented(S) {
  return [[S.A[0][0], S.A[0][1], S.b[0]], [S.A[1][0], S.A[1][1], S.b[1]]];
}

function verdictOf(S) {
  var rA = rankOf(S.A), rAug = rankOf(augmented(S));
  if (rA !== rAug) { return { rA: rA, rAug: rAug, text: 'no solution', col: RED }; }
  if (rA === 2) { return { rA: rA, rAug: rAug, text: 'exactly one solution', col: GREEN }; }
  return { rA: rA, rAug: rAug, text: 'infinitely many solutions', col: ORANGE };
}

function solveOf(S) {
  var d = detOf2(S.A);
  if (Math.abs(d) < 1e-9) { return null; }
  return [(S.b[0] * S.A[1][1] - S.A[0][1] * S.b[1]) / d,
          (S.A[0][0] * S.b[1] - S.b[0] * S.A[1][0]) / d];
}

function num(v) {
  var r = Math.round(v * 100) / 100;
  return (r === Math.round(r)) ? String(Math.round(r)) : r.toFixed(2);
}

function sidePanel(S, v, sol) {
  var d = darkMode();
  var x = 800 - 282, y = 30;
  noStroke();
  fill(d ? color(32, 38, 48) : color(240, 244, 252));
  rect(x, y, 262, 250, 8);
  textAlign('left', 'baseline');
  fill(BLUE[0], BLUE[1], BLUE[2]); textSize(11.5); textStyle(BOLD);
  text('the system', x + 12, y + 20);
  textStyle(NORMAL);
  fill(d ? color(225, 230, 238) : color(35, 40, 50)); textSize(13.5);
  text('[' + num(S.A[0][0]) + '  ' + num(S.A[0][1]) + '] [x]   [' + num(S.b[0]) + ']', x + 12, y + 44);
  text('[' + num(S.A[1][0]) + '  ' + num(S.A[1][1]) + '] [y] = [' + num(S.b[1]) + ']', x + 12, y + 64);
  textSize(12);
  fill(d ? color(190, 196, 206) : color(80, 88, 100));
  text('det(A) = ' + num(detOf2(S.A)), x + 12, y + 92);
  text('rank(A) = ' + v.rA, x + 12, y + 112);
  text('rank([A|b]) = ' + v.rAug, x + 150, y + 112);
  text('n = 2 unknowns', x + 12, y + 132);
  text('free parameters = ' + (2 - v.rA), x + 12, y + 152);
  fill(v.col[0], v.col[1], v.col[2]); textSize(13); textStyle(BOLD);
  text(v.text, x + 12, y + 182);
  textStyle(NORMAL);
  textSize(11.5); fill(d ? color(160, 168, 180) : color(110, 118, 130));
  if (sol) {
    text('solution: x = ' + num(sol[0]) + ', y = ' + num(sol[1]), x + 12, y + 208);
  } else {
    text('no single point: the lines do not cross once', x + 12, y + 208);
  }
  text('blue: first equation   orange: second', x + 12, y + 232);
}

window.LESSON = {
  steps: SYSTEMS.map(function (S, idx) {
    return {
      duration: 3000,
      caption: S.caption,
      draw: function (progress, w, h) {
        inkBg();
        var f = frame2();
        drawGrid(f);
        var v = verdictOf(S);
        var sol = solveOf(S);
        var secondSame = (Math.abs(S.A[0][0] * S.A[1][1] - S.A[0][1] * S.A[1][0]) < 1e-9) &&
                         (Math.abs(S.A[0][0] * S.b[1] - S.b[0] * S.A[1][0]) < 1e-9);
        drawConstraint(f, S.A[0][0], S.A[0][1], S.b[0], BLUE, false);
        drawConstraint(f, S.A[1][0], S.A[1][1], S.b[1], ORANGE, secondSame);
        if (sol) {
          var p = toPixel(f, sol[0], sol[1]);
          noStroke(); fill(GREEN[0], GREEN[1], GREEN[2]);
          circle(p[0], p[1], 11);
          fill(darkMode() ? color(225, 230, 238) : color(35, 40, 50));
          textSize(12); textAlign('left', 'baseline');
          text('(' + num(sol[0]) + ', ' + num(sol[1]) + ')', p[0] + 10, p[1] - 10);
        }
        sidePanel(S, v, sol);
        var dk = darkMode();
        fill(dk ? color(150, 158, 170) : color(120, 128, 140));
        textSize(11.5); textAlign('left', 'baseline');
        text('each line is one equation; a solution is a point on every line at once',
             f.padL, 500 - 14);
      }
    };
  })
};
