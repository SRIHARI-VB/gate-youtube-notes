/* Sweeping a vector around the unit circle through A = [[2,1],[1,2]] and watching for the two
   directions in which A does not turn the vector, only scale it.

   The matrix, its two eigenvalues 3 and 1, its eigenvectors (1,1) and (1,-1), its trace 4 and its
   determinant 3 are all recomputed in scripts/validate.py (check_eigenvalues_and_eigenvectors).
   Nothing here is drawn from a value that is not checked there. */

var A = [[2, 1], [1, 2]];

var BLUE = [31, 94, 255], ORANGE = [180, 90, 31], GREEN = [20, 107, 74], RED = [170, 40, 45];
var VIEW = 4.2;   /* the visible half-width of the plot, in matrix coordinates */

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

function textInk() { return darkMode() ? color(190, 197, 208) : color(105, 113, 126); }
function strongInk() { return darkMode() ? color(238, 241, 245) : color(20, 24, 31); }

/* A square plot on the left, an optional panel on the right. */
function layout(w, h) {
  var panelW = (w >= 620) ? 236 : 0;
  var side = Math.min(w - panelW - 26, h - 54);
  if (side < 80) { side = Math.max(60, Math.min(w, h) - 20); }
  var ox = 14 + side / 2;
  var oy = 14 + side / 2;
  return { w: w, h: h, panelW: panelW, side: side, ox: ox, oy: oy, s: side / (2 * VIEW) };
}

function px(f, x, y) { return [f.ox + x * f.s, f.oy - y * f.s]; }

function applyA(v) {
  return [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]];
}

function drawGrid(f) {
  var faint = darkMode() ? color(46, 53, 64) : color(233, 237, 243);
  var axis = darkMode() ? color(80, 88, 101) : color(198, 204, 212);
  strokeWeight(1);
  for (var i = -4; i <= 4; i++) {
    stroke(faint);
    var a = px(f, i, -VIEW), b = px(f, i, VIEW);
    line(a[0], a[1], b[0], b[1]);
    var c = px(f, -VIEW, i), d = px(f, VIEW, i);
    line(c[0], c[1], d[0], d[1]);
  }
  stroke(axis);
  var o = px(f, 0, 0), xe = px(f, VIEW, 0), ye = px(f, 0, VIEW);
  line(o[0], o[1], xe[0], xe[1]);
  line(o[0], o[1], ye[0], ye[1]);
  /* the unit circle: the track the input vector slides along */
  stroke(darkMode() ? color(58, 66, 79) : color(214, 219, 227));
  var prev = null;
  for (var k = 0; k <= 72; k++) {
    var t = (k / 72) * Math.PI * 2;
    var p = px(f, Math.cos(t), Math.sin(t));
    if (prev) { line(prev[0], prev[1], p[0], p[1]); }
    prev = p;
  }
  noStroke();
  fill(textInk());
  textSize(10.5);
  textAlign('center', 'top');
  for (var g = -4; g <= 4; g++) {
    if (g === 0) { continue; }
    var q = px(f, g, 0);
    text(String(g), q[0], q[1] + 4);
  }
  textAlign('left', 'baseline');
}

function arrow(f, v, col, weight) {
  var o = px(f, 0, 0), e = px(f, v[0], v[1]);
  stroke(col[0], col[1], col[2]);
  strokeWeight(weight || 2.5);
  line(o[0], o[1], e[0], e[1]);
  var dx = e[0] - o[0], dy = e[1] - o[1];
  var len = Math.sqrt(dx * dx + dy * dy);
  if (len < 6) { return; }
  var ux = dx / len, uy = dy / len;
  var head = Math.min(11, len * 0.4);
  line(e[0], e[1], e[0] - head * ux + head * 0.45 * uy, e[1] - head * uy - head * 0.45 * ux);
  line(e[0], e[1], e[0] - head * ux - head * 0.45 * uy, e[1] - head * uy + head * 0.45 * ux);
}

function label(f, v, txt, col) {
  var p = px(f, v[0], v[1]);
  noStroke();
  fill(col[0], col[1], col[2]);
  textSize(12);
  textAlign('left', 'baseline');
  text(txt, p[0] + 7, p[1] - 7);
}

function unit(deg) {
  var t = deg * Math.PI / 180;
  return [Math.cos(t), Math.sin(t)];
}

/* The signed factor by which A scales the direction of v: |Av| / |v| with the sign of the dot product. */
function scaleFactor(v) {
  var av = applyA(v);
  var nv = Math.sqrt(v[0] * v[0] + v[1] * v[1]);
  var na = Math.sqrt(av[0] * av[0] + av[1] * av[1]);
  if (nv === 0) { return 0; }
  var dot = v[0] * av[0] + v[1] * av[1];
  return (dot < 0 ? -1 : 1) * (na / nv);
}

function turnDegrees(v) {
  var av = applyA(v);
  var dot = v[0] * av[0] + v[1] * av[1];
  var nv = Math.sqrt(v[0] * v[0] + v[1] * v[1]);
  var na = Math.sqrt(av[0] * av[0] + av[1] * av[1]);
  if (nv === 0 || na === 0) { return 0; }
  var c = Math.max(-1, Math.min(1, dot / (nv * na)));
  return Math.acos(c) * 180 / Math.PI;
}

function num(x) { return (Math.round(x * 100) / 100).toString(); }

function panel(f, rows) {
  if (!f.panelW) {
    var y0 = f.h - 18;
    noStroke();
    fill(textInk());
    textSize(11.5);
    textAlign('left', 'baseline');
    text(rows[0], 14, y0);
    return;
  }
  var x = f.ox + f.side / 2 + 16;
  var y = 22;
  noStroke();
  textAlign('left', 'baseline');
  textSize(11);
  fill(textInk());
  text('A = [[2,1],[1,2]]', x, y);
  text('tr A = 4,  det A = 3', x, y + 18);
  for (var i = 0; i < rows.length; i++) {
    textSize(12);
    fill(strongInk());
    text(rows[i], x, y + 52 + i * 21);
  }
}

function baseFrame(w, h, rows) {
  inkBg();
  var f = layout(w, h);
  drawGrid(f);
  panel(f, rows);
  return f;
}

window.LESSON = {
  steps: [
    {
      duration: 2600,
      caption: "A is a rule that moves every vector. Take the input x at 25 degrees on the unit circle; the output Ax is the orange arrow. Its direction and its length both change, so this x is not special.",
      draw: function (progress, w, h) {
        var f = baseFrame(w, h, ['x: 25 degrees', 'Ax turns by ' + num(turnDegrees(unit(25))) + ' deg']);
        var x = unit(25);
        arrow(f, x, BLUE, 2.5);
        label(f, x, 'x', BLUE);
        arrow(f, applyA(x), ORANGE, 2.5);
        label(f, applyA(x), 'Ax', ORANGE);
      }
    },
    {
      duration: 2600,
      caption: "Turning by an angle is the normal case. An eigenvector is the rare input whose output stays on the same line through the origin: A may stretch it, shrink it or flip it, but it never turns it off that line.",
      draw: function (progress, w, h) {
        var f = baseFrame(w, h, ['turn angle: ' + num(turnDegrees(unit(25))) + ' deg', 'not an eigenvector']);
        var x = unit(25);
        arrow(f, x, BLUE, 2.5);
        label(f, x, 'x', BLUE);
        arrow(f, applyA(x), ORANGE, 2.5);
        label(f, applyA(x), 'Ax', ORANGE);
        var o = px(f, 0, 0), xa = px(f, x[0], x[1]), xb = px(f, -x[0], -x[1]);
        stroke(RED[0], RED[1], RED[2]);
        strokeWeight(1);
        line(xa[0], xa[1], xb[0], xb[1]);
      }
    },
    {
      duration: 6000,
      caption: "Sweep the input all the way round the circle. The turn angle drops to zero only at two angles, 45 degrees and 135 degrees. Those two directions are the only eigenvectors of this matrix.",
      draw: function (progress, w, h) {
        var deg = progress * 360;
        var v = unit(deg);
        var f = baseFrame(w, h, ['input at ' + num(deg) + ' deg', 'turn: ' + num(turnDegrees(v)) + ' deg']);
        arrow(f, v, BLUE, 2.5);
        label(f, v, 'x', BLUE);
        arrow(f, applyA(v), ORANGE, 2.5);
        label(f, applyA(v), 'Ax', ORANGE);
        var o = px(f, 0, 0), a = px(f, v[0], v[1]), b = px(f, -v[0], -v[1]);
        stroke(RED[0], RED[1], RED[2]);
        strokeWeight(1);
        line(a[0], a[1], b[0], b[1]);
      }
    },
    {
      duration: 2800,
      caption: "At 45 degrees the input is the unit vector in the direction of (1,1). A sends it to (3,3), which is 3 times the input: same line, no turn, factor 3. So 3 is an eigenvalue and (1,1) is an eigenvector.",
      draw: function (progress, w, h) {
        var f = baseFrame(w, h, ['x = (1,1)/sqrt2', 'Ax = 3x,  lambda = 3']);
        var v = unit(45);
        arrow(f, v, BLUE, 2.5);
        label(f, v, 'x', BLUE);
        arrow(f, applyA(v), GREEN, 3);
        label(f, applyA(v), 'Ax = 3x', GREEN);
      }
    },
    {
      duration: 2800,
      caption: "At 135 degrees the input is the unit vector in the direction of (1,-1). Here A returns exactly the same vector, (1,-1), so the eigenvalue is 1: this direction is not stretched at all, only left alone.",
      draw: function (progress, w, h) {
        var f = baseFrame(w, h, ['x = (1,-1)/sqrt2', 'Ax = 1x,  lambda = 1']);
        var v = unit(135);
        arrow(f, v, BLUE, 2.5);
        label(f, v, 'x', BLUE);
        arrow(f, applyA(v), GREEN, 3);
        label(f, applyA(v), 'Ax = x', GREEN);
      }
    },
    {
      duration: 3000,
      caption: "Both eigen-directions at once. The eigenvalue is the signed factor |Ax| / |x|: 3 along (1,1) and 1 along (1,-1). The sum 3 + 1 = 4 is the trace, and the product 3 x 1 = 3 is the determinant, which is where those two identities come from.",
      draw: function (progress, w, h) {
        var f = baseFrame(w, h, ['lambda = 3 along (1,1)', 'lambda = 1 along (1,-1)', 'sum 4 = trace, product 3 = det']);
        var v1 = unit(45), v2 = unit(135);
        arrow(f, v1, GREEN, 3);
        label(f, v1, 'lambda = 3', GREEN);
        arrow(f, v2, ORANGE, 3);
        label(f, v2, 'lambda = 1', ORANGE);
        arrow(f, applyA(v1), GREEN, 2);
      }
    },
    {
      duration: 3200,
      caption: "The two eigenvectors (1,1) and (1,-1) are perpendicular, because this A is symmetric. Every real symmetric matrix has real eigenvalues and orthogonal eigenvectors, and it can always be diagonalised.",
      draw: function (progress, w, h) {
        var f = baseFrame(w, h, ['(1,1) . (1,-1) = 0', 'A is symmetric, so the', 'eigenvectors are orthogonal']);
        var v1 = unit(45), v2 = unit(135);
        arrow(f, v1, GREEN, 3);
        label(f, v1, '(1,1)', GREEN);
        arrow(f, v2, ORANGE, 3);
        label(f, v2, '(1,-1)', ORANGE);
        var p1 = px(f, v1[0], v1[1]), p2 = px(f, v2[0], v2[1]);
        stroke(textInk());
        strokeWeight(1.2);
        noFill();
        var cx = px(f, 0.42, 0.42), cy = px(f, -0.42, 0.42);
        line(p1[0], p1[1], cx[0], cx[1]);
        line(cx[0], cx[1], p2[0], p2[1]);
        noStroke();
        fill(textInk());
        textSize(11);
        textAlign('left', 'baseline');
        text('90 degrees', cx[0] + 4, cx[1] + 4);
      }
    }
  ]
};
