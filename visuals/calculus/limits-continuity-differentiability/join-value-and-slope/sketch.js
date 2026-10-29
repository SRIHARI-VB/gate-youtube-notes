/* Matching value and slope at a join.
   f(x) = ax + b for x < 1, f(x) = x^3 + x^2 + 1 for x >= 1.
   Continuity at 1: a + b = 3. Differentiability at 1: a = 3(1)^2 + 2(1) = 5, so b = -2.
   The three parameter settings shown are (0, 0) - a jump from 0 to 3, (1, 2) - continuous but
   with slopes 1 and 5, and (5, -2) - continuous with both slopes 5, which is GATE CSE 2025 Set 1
   Q.21. Every value is recomputed in scripts/validate.py (check_limits_continuity_differentiability). */
window.LESSON = {
  steps: [
    {
      duration: 2600,
      caption: 'One function, two formulas. Below x = 1 it is the line ax + b; from x = 1 upwards it is the cubic x^3 + x^2 + 1. The question is which a and b make it differentiable everywhere - and everything depends on what happens at the join x = 1.',
      draw: function (p, w, h) {
        ink();
        head('Two formulas meeting at x = 1', 30, 34);
        box(30, 60, w - 60, h - 130, 0, 1.7, -1.5, 9, 0, 0);
        note('Right-hand piece at x = 1: 1 + 1 + 1 = 3. Left-hand piece at x = 1: a + b.', 30, h - 24);
      }
    },
    {
      duration: 3000,
      caption: 'Start with a = 0 and b = 0. The line sits at 0 right up to x = 1, while the cubic starts at 3. The two pieces never meet: this is a jump, so the function is not even continuous, and continuity is the first thing differentiability needs.',
      draw: function (p, w, h) {
        ink();
        head('a = 0, b = 0: a jump of 3', 30, 34);
        var b = box(30, 60, w - 60, h - 130, 0, 1.7, -1.5, 9, 0, 0);
        piece(b, 0, 0);
        tag(b, 1, 0, 'left value 0', [31, 94, 255]);
        tag(b, 1, 3, 'right value 3', [180, 90, 31]);
        note('0 is not 3, so f is not continuous at 1 - and not differentiable there.', 30, h - 24);
      }
    },
    {
      duration: 3000,
      caption: 'Now choose a + b = 3, for example a = 1 and b = 2. The pieces meet at (1, 3), so the function is continuous. But the line rises at slope 1 while the cubic leaves x = 1 at slope 3 + 2 = 5. Two different slopes meeting at a point is a corner: continuous, still not differentiable.',
      draw: function (p, w, h) {
        ink();
        head('a = 1, b = 2: continuous, but a corner', 30, 34);
        var b = box(30, 60, w - 60, h - 130, 0, 1.7, -1.5, 9, 1, 2);
        piece(b, 1, 2);
        tangents(b, 1, 5, 1);
        tag(b, 1, 3, 'both values 3', [20, 107, 74]);
        note('Left slope 1, right slope 5: the derivative does not exist at x = 1.', 30, h - 24);
      }
    },
    {
      duration: 3000,
      caption: 'Finally set the slope to 5, which forces a = 5, and keep continuity, which gives b = 3 - 5 = -2. The line now arrives at (1, 3) with slope 5 and the cubic leaves with slope 5. The pieces join smoothly: f is differentiable everywhere, and b = -2 is the answer to the GATE 2025 question.',
      draw: function (p, w, h) {
        ink();
        head('a = 5, b = -2: differentiable everywhere', 30, 34);
        var b = box(30, 60, w - 60, h - 130, 0, 1.7, -1.5, 9, 5, -2);
        piece(b, 5, -2);
        tangents(b, 5, 5, 1);
        tag(b, 1, 3, 'value 3, slope 5 on both sides', [20, 107, 74]);
        note('b = 3 - a = 3 - 5 = -2.', 30, h - 24);
      }
    },
    {
      duration: 2600,
      caption: 'The whole method in two equations. Continuity gives a + b = 3, because the values must agree at x = 1. Differentiability gives a = 5, because the slopes must agree there. Solve them in that order: the slope equation fixes a, then the value equation fixes b.',
      draw: function (p, w, h) {
        ink();
        head('The method: value first, then slope', 30, 34);
        equation(30, 62, 'Continuity at 1', 'a(1) + b = 1^3 + 1^2 + 1', 'a + b = 3');
        equation(30, 150, 'Differentiability at 1', 'a = 3x^2 + 2x at x = 1', 'a = 5');
        equation(30, 238, 'Solve', 'b = 3 - a', 'b = -2');
        note('Differentiability needs continuity, so the value equation is never optional.', 30, h - 24);
      }
    }
  ]
};

/* ---------------------------------------------------------------- helpers */
function ink() {
  var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  background(dark ? color(23, 28, 36) : color(255));
  noStroke();
  fill(dark ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}
function head(t, x, y) { textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function note(t, x, y) { textSize(12.5); fill(90, 100, 116); noStroke(); text(t, x, y); }

function box(x, y, w, h, xmin, xmax, ymin, ymax, a, b) {
  var bx = { x: x, y: y, w: w, h: h, xmin: xmin, xmax: xmax, ymin: ymin, ymax: ymax };
  stroke(206, 212, 222); strokeWeight(1);
  var o = map2(bx, 0, 0);
  line(bx.x, o[1], bx.x + bx.w, o[1]);
  line(o[0], bx.y, o[0], bx.y + bx.h);
  noStroke(); fill(140, 148, 160); textSize(11);
  text('x', bx.x + bx.w - 10, o[1] - 6);
  text('y', o[0] + 6, bx.y + 10);
  text('1', map2(bx, 1, 0)[0] - 3, o[1] + 14);
  return bx;
}

function map2(bx, x, y) {
  return [
    bx.x + (x - bx.xmin) / (bx.xmax - bx.xmin) * bx.w,
    bx.y + bx.h - (y - bx.ymin) / (bx.ymax - bx.ymin) * bx.h
  ];
}

function drawCurve(bx, f, from, to, col) {
  stroke(col[0], col[1], col[2]); strokeWeight(2.5); noFill();
  var prev = null, n = 200;
  for (var i = 0; i <= n; i++) {
    var x = from + (to - from) * i / n;
    var y = f(x);
    if (y < bx.ymin || y > bx.ymax) { prev = null; continue; }
    var pt = map2(bx, x, y);
    if (prev) { line(prev[0], prev[1], pt[0], pt[1]); }
    prev = pt;
  }
  noStroke();
}

function piece(bx, a, b) {
  drawCurve(bx, function (x) { return a * x + b; }, 0, 1, [31, 94, 255]);
  drawCurve(bx, function (x) { return x * x * x + x * x + 1; }, 1, 1.7, [180, 90, 31]);
  var pt = map2(bx, 1, a + b);
  noStroke(); fill(20, 107, 74); circle(pt[0], pt[1], 8);
}

function tangents(bx, slopeLeft, slopeRight, at) {
  var y = at * at * at + at * at + 1;
  seg(bx, at, y, slopeLeft, -1, [31, 94, 255]);
  seg(bx, at, y, slopeRight, 1, [180, 90, 31]);
}

function seg(bx, x0, y0, m, dir, col) {
  var len = 0.28;
  var x1 = x0 + dir * len;
  var y1 = y0 + m * dir * len;
  var p1 = map2(bx, x0, y0), p2 = map2(bx, x1, y1);
  stroke(col[0], col[1], col[2]); strokeWeight(1.5);
  line(p1[0], p1[1], p2[0], p2[1]);
  noStroke();
}

function tag(bx, x, y, txt, col) {
  var pt = map2(bx, x, y);
  noStroke(); fill(col[0], col[1], col[2]); textSize(12.5);
  text(txt, pt[0] + 10, pt[1] - 10);
}

function equation(x, y, label, lhs, rhs) {
  noStroke(); fill(232, 238, 255);
  rect(x, y, Math.min(width - 2 * x, 470), 72, 8);
  fill(31, 94, 255); textSize(13); textStyle(BOLD); text(label, x + 12, y + 22);
  textStyle(NORMAL); fill(70, 80, 98); textSize(12.5);
  text(lhs, x + 12, y + 42);
  fill(20, 107, 74); textSize(14); textStyle(BOLD);
  text(rhs, x + 12, y + 62);
  textStyle(NORMAL);
}
