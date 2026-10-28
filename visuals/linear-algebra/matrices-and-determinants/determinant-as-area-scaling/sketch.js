/* The determinant as signed area: row operations seen as area operations.

   The six matrices below are the ones used in the "How row and column operations change a
   determinant" card. Every determinant shown is recomputed in scripts/validate.py
   (check_matrices_and_determinants): det([[1,0],[0,1]]) = 1, det([[2,1],[0,3]]) = 6,
   the row swap gives -6, scaling the first row by 3 gives 18, adding row 2 to row 1 leaves 6,
   and the dependent matrix [[2,1],[4,2]] gives 0. */

var STEPS_M = [
  { M: [[1, 0], [0, 1]], caption: "The unit square. Its two columns are (1,0) and (0,1), so the parallelogram they span is the unit square and its signed area is det = 1 x 1 - 0 x 0 = 1." },
  { M: [[2, 1], [0, 3]], caption: "A = [[2,1],[0,3]]. The columns are (2,0) and (1,3); the parallelogram they span has signed area 2 x 3 - 1 x 0 = 6, which is det(A). The determinant is the area scaling of the map x -> Ax." },
  { M: [[0, 3], [2, 1]], caption: "Swap the two rows of A. The new matrix has determinant 0 x 1 - 3 x 2 = -6: the same area, 6, but traversed the other way round, so the sign flips. One interchange multiplies a determinant by -1." },
  { M: [[6, 3], [0, 3]], caption: "Back to A and multiply its first row by 3, giving [[6,3],[0,3]]. The determinant is 6 x 3 - 3 x 0 = 18 = 3 x 6: scaling one row by 3 scales the area by 3, and scaling all n rows is why det(kA) = k^n det(A)." },
  { M: [[2, 4], [0, 3]], caption: "Back to A and add row 2 to row 1, giving [[2,4],[0,3]]. The determinant is 2 x 3 - 4 x 0 = 6, unchanged: the shear slides one edge along the other and leaves the area alone, which is why row reduction preserves the determinant." },
  { M: [[2, 1], [4, 2]], caption: "Now make the rows dependent: row 2 = 2 x row 1 gives [[2,1],[4,2]] with determinant 2 x 2 - 1 x 4 = 0. The parallelogram collapses onto a line, the area is 0, and the matrix is singular." },
  { M: [[2, 1], [4, 2]], caption: "The four rules in one place: a row swap flips the sign, scaling a row scales the determinant, adding a multiple of a row leaves it alone, and dependent rows give 0. A square matrix is singular exactly when its determinant is 0, that is, exactly when its columns stop spanning area." }
];

var BLUE = [31, 94, 255], ORANGE = [180, 90, 31], RED = [170, 40, 45], GREEN = [20, 107, 74];
var XMIN = -0.8, XMAX = 7.2, YMIN = -2.2, YMAX = 4.4;

function dark() {
  return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
}

function ink(w, h) {
  var d = dark();
  background(d ? color(23, 28, 36) : color(255));
  noStroke();
  fill(d ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}

function plot() {
  var w = 800, h = 500;
  var padL = 64, padR = 300, padT = 40, padB = 44;
  var pw = w - padL - padR, ph = h - padT - padB;
  var sx = pw / (XMAX - XMIN), sy = ph / (YMAX - YMIN);
  var s = Math.min(sx, sy);
  return { w: w, h: h, padL: padL, padT: padT, pw: pw, ph: ph, s: s,
           ox: padL + (pw - s * (XMAX - XMIN)) / 2, oy: padT + (ph + s * (YMAX - YMIN)) / 2 };
}

function P(p, x, y) { return [p.ox + (x - XMIN) * p.s, p.oy - (y - YMIN) * p.s]; }

function axes(p) {
  var d = dark();
  var grey = d ? color(70, 78, 90) : color(205, 210, 218);
  var o = P(p, 0, 0);
  stroke(grey); strokeWeight(1);
  line(o[0], P(p, 0, YMAX)[1], o[0], P(p, 0, YMIN)[1]);
  line(P(p, XMIN, 0)[0], o[1], P(p, XMAX, 0)[0], o[1]);
  noStroke(); fill(d ? color(150, 158, 170) : color(120, 128, 140));
  textSize(11); textAlign('center', 'top');
  for (var i = 1; i <= 6; i++) { var q = P(p, i, 0); text(String(i), q[0], q[1] + 4); }
}

function det2(M) { return M[0][0] * M[1][1] - M[0][1] * M[1][0]; }

function lerpM(A, B, t) {
  return [[A[0][0] + (B[0][0] - A[0][0]) * t, A[0][1] + (B[0][1] - A[0][1]) * t],
          [A[1][0] + (B[1][0] - A[1][0]) * t, A[1][1] + (B[1][1] - A[1][1]) * t]];
}

function shade(M, p, alphaName) {
  var d = det2(M);
  var col = Math.abs(d) < 1e-9 ? RED : (d > 0 ? BLUE : ORANGE);
  noStroke();
  fill(color(col[0], col[1], col[2]));
  var c1 = P(p, M[0][0], M[1][0]);
  var c2 = P(p, M[0][1], M[1][1]);
  var o = P(p, 0, 0);
  var sum = P(p, M[0][0] + M[0][1], M[1][0] + M[1][1]);
  beginShape();
  vertex(o[0], o[1]); vertex(c1[0], c1[1]); vertex(sum[0], sum[1]); vertex(c2[0], c2[1]);
  endShape(CLOSE);
  stroke(col[0], col[1], col[2]); strokeWeight(2.5);
  line(o[0], o[1], c1[0], c1[1]);
  line(o[0], o[1], c2[0], c2[1]);
  noStroke(); fill(col[0], col[1], col[2]);
  circle(c1[0], c1[1], 7); circle(c2[0], c2[1], 7);
  return d;
}

function panel(p, M, d) {
  var dk = dark();
  var x = 800 - 288, y = 40;
  noStroke(); fill(dk ? color(32, 38, 48) : color(240, 244, 252));
  rect(x, y, 268, 150, 8);
  fill(BLUE[0], BLUE[1], BLUE[2]); textSize(11.5); textStyle(BOLD);
  text('matrix (rows)', x + 12, y + 20);
  textStyle(NORMAL);
  fill(dk ? color(225, 230, 238) : color(35, 40, 50)); textSize(14);
  text('[' + fmt(M[0][0]) + '  ' + fmt(M[0][1]) + ']', x + 14, y + 44);
  text('[' + fmt(M[1][0]) + '  ' + fmt(M[1][1]) + ']', x + 14, y + 64);
  textSize(11.5); fill(BLUE[0], BLUE[1], BLUE[2]); textStyle(BOLD);
  text('determinant = signed area', x + 12, y + 96);
  textStyle(NORMAL);
  var col = Math.abs(d) < 1e-9 ? RED : (d > 0 ? BLUE : ORANGE);
  fill(col[0], col[1], col[2]); textSize(20); textStyle(BOLD);
  text(fmt(d), x + 14, y + 124);
  textStyle(NORMAL);
  textSize(11); fill(dk ? color(150, 158, 170) : color(110, 118, 130));
  text(Math.abs(d) < 1e-9 ? 'columns dependent: area 0' :
       (d > 0 ? 'orientation kept' : 'orientation reversed'), x + 96, y + 124);
}

function fmt(v) {
  var r = Math.round(v * 100) / 100;
  return (r === Math.round(r)) ? String(Math.round(r)) : r.toFixed(2);
}

window.LESSON = {
  steps: STEPS_M.map(function (s, i) {
    return {
      duration: 2600,
      caption: s.caption,
      draw: function (progress, w, h) {
        ink(w, h);
        var p = plot();
        axes(p);
        var prev = i === 0 ? s.M : STEPS_M[i - 1].M;
        var t = progress === undefined ? 1 : progress;
        var e = t < 0.5 ? 2 * t * t : 1 - 2 * (1 - t) * (1 - t);
        var M = lerpM(prev, s.M, e);
        var d = shade(M, p);
        panel(p, M, d);
        var dk = dark();
        fill(dk ? color(150, 158, 170) : color(120, 128, 140));
        textSize(11.5); textAlign('left', 'baseline');
        text('the shaded parallelogram is spanned by the two columns of the matrix', p.padL, 500 - 16);
      }
    };
  })
};
