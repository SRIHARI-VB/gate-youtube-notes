/* Signed area and the running total, for the Integration topic.
   Values used here, all recomputed in scripts/validate.py (check_integration):
     f(x) = x^2 - 1, so f(0) = -1, f(1) = 0, f(2) = 3;
     an antiderivative is F(x) = x^3/3 - x, so F(0) = 0, F(1) = -2/3, F(2) = 2/3;
     the integral from 0 to 1 is -2/3 and the geometric area there is 2/3;
     the integral from 1 to 2 is 4/3, so the integral from 0 to 2 is 2/3 while the area is 2;
     F vanishes again at sqrt(3) = 1.7320508, where (sqrt 3)^3/3 - sqrt 3 = 0;
     F'(x) = x^2 - 1 = f(x), which is the slope check at x = 0, 1 and 2;
     f is even, so the integral from -1 to 1 is twice the integral from 0 to 1 = -4/3. */
window.LESSON = {
  steps: [
    {
      duration: 3600,
      caption: 'Sweep the right-hand boundary from 0 to b. The shaded region is the integral from 0 to b: it grows negative while the curve is below the axis, because a definite integral is net signed area.',
      draw: function (p, w, h) {
        ink();
        head('Sweeping the upper limit', 30, 34);
        var box = { x: 66, y: 62, w: w - 132, h: h - 150, xmin: -0.1, xmax: 2.1, ymin: -1.3, ymax: 3.2 };
        axes(box);
        var b = 2 * Math.min(1, Math.max(0, p));
        shade(box, f, 0, Math.min(b, 1), [196, 74, 74]);
        if (b > 1) { shade(box, f, 1, b, [31, 122, 82]); }
        plot(box, f, 0, 2, [31, 94, 255]);
        var edge = map2(box, b, 0);
        stroke(90, 100, 116); strokeWeight(1.5); noFill();
        line(edge[0], box.y, edge[0], box.y + box.h);
        noStroke(); fill(30, 38, 50); textSize(13);
        text('b = ' + b.toFixed(2) + ',  running total = ' + F(b).toFixed(4), 34, 62);
        note('Below the axis the contribution is negative; above it the contribution is positive.', 30, h - 24);
      }
    },
    {
      duration: 3200,
      caption: 'Stop at b = 1. The curve crosses the axis there, so the whole piece is below it. Its signed value is one third minus one, minus two thirds; the geometric area is the positive two thirds.',
      draw: function (p, w, h) {
        ink();
        head('The piece from 0 to 1: value -2/3, area 2/3', 30, 34);
        var box = { x: 66, y: 62, w: w - 132, h: h - 150, xmin: -0.1, xmax: 2.1, ymin: -1.3, ymax: 3.2 };
        axes(box);
        shade(box, f, 0, 1, [196, 74, 74]);
        plot(box, f, 0, 2, [31, 94, 255]);
        mark(box, 1, 0, 'crossing at x = 1');
        noStroke(); fill(30, 38, 50); textSize(13);
        text('integral of x^2 - 1 from 0 to 1 = 1/3 - 1 = -0.6667', 34, 62);
        note('An integral can be negative. An area cannot, so the two numbers differ by the sign here.', 30, h - 24);
      }
    },
    {
      duration: 3400,
      caption: 'Add the piece from 1 to 2: there the integrand is positive and the value is four thirds. The two pieces give a total of two thirds, while the total area is two - the negative piece is subtracted, not added.',
      draw: function (p, w, h) {
        ink();
        head('Both pieces: total 2/3, area 2', 30, 34);
        var box = { x: 66, y: 62, w: w - 132, h: h - 150, xmin: -0.1, xmax: 2.1, ymin: -1.3, ymax: 3.2 };
        axes(box);
        shade(box, f, 0, 1, [196, 74, 74]);
        shade(box, f, 1, 2, [31, 122, 82]);
        plot(box, f, 0, 2, [31, 94, 255]);
        mark(box, 1, 0, 'x = 1');
        mark(box, 2, 3, '(2, 3)');
        noStroke(); fill(30, 38, 50); textSize(13);
        text('(-2/3) + (4/3) = 2/3', 34, 62);
        note('Signed pieces add; areas add only in absolute value.', 30, h - 24);
      }
    },
    {
      duration: 3600,
      caption: 'Now read the integral as a function of its upper limit. F of x is the integral from 0 to x, drawn here in green: it starts at 0, dips to minus two thirds at x = 1, and comes back to two thirds at x = 2.',
      draw: function (p, w, h) {
        ink();
        head('The running total F(x) = x^3/3 - x', 30, 34);
        var box = { x: 66, y: 62, w: w - 132, h: h - 150, xmin: -0.1, xmax: 2.1, ymin: -1.3, ymax: 3.2 };
        axes(box);
        shade(box, f, 0, 1, [243, 226, 226]);
        shade(box, f, 1, 2, [224, 240, 231]);
        plot(box, f, 0, 2, [31, 94, 255]);
        plot(box, F, 0, 2, [20, 107, 74]);
        mark(box, 1, -2 / 3, 'F(1) = -0.6667');
        mark(box, 2, 2 / 3, 'F(2) = 0.6667');
        mark(box, Math.sqrt(3), 0, 'F = 0 at x = 1.7321');
        noStroke(); fill(30, 38, 50); textSize(13);
        text('green: the running total; blue: the integrand', 34, 62);
        note('The running total is zero again where the two signed pieces cancel exactly.', 30, h - 24);
      }
    },
    {
      duration: 3800,
      caption: 'Differentiate the running total and you get the integrand back. At x = 0 the height of the curve is minus 1 and the slope of F is minus 1; at x = 1 both are 0; at x = 2 the height is 3 and so is the slope. That is part one of the fundamental theorem.',
      draw: function (p, w, h) {
        ink();
        head('Slope of F equals height of f', 30, 34);
        var t = Math.min(1, Math.max(0, p));
        var x0 = 0.2 + 1.7 * t;
        var boxA = { x: 50, y: 62, w: (w - 130) / 2, h: h - 150, xmin: -0.1, xmax: 2.1, ymin: -1.3, ymax: 3.2 };
        var boxB = { x: 50 + (w - 130) / 2 + 30, y: 62, w: (w - 130) / 2, h: h - 150, xmin: -0.1, xmax: 2.1, ymin: -1.3, ymax: 3.2 };
        axes(boxA); axes(boxB);
        plot(boxA, f, 0, 2, [31, 94, 255]);
        plot(boxB, F, 0, 2, [20, 107, 74]);
        var pa = map2(boxA, x0, 0), pb = map2(boxA, x0, f(x0));
        stroke(31, 94, 255); strokeWeight(2); noFill();
        line(pa[0], pa[1], pb[0], pb[1]);
        tangent(boxB, F, x0, f(x0));
        noStroke(); fill(30, 38, 50); textSize(12.5);
        text('height f(' + x0.toFixed(2) + ') = ' + f(x0).toFixed(3), boxA.x + 4, boxA.y + 14);
        text('slope F\'\(' + x0.toFixed(2) + ') = ' + f(x0).toFixed(3), boxB.x + 4, boxB.y + 14);
        note('Same number on both sides: the height of the curve is the slope of the running total.', 30, h - 24);
      }
    },
    {
      duration: 3000,
      caption: 'Quick check. The integrand is even, so the integral from minus 1 to 1 is twice the integral from 0 to 1: twice minus two thirds, which is minus four thirds. The running total table confirms every value.',
      draw: function (p, w, h) {
        ink();
        head('Quick check', 30, 34);
        var rows = [
          ['quantity', 'value'],
          ['integral 0 to 1 of (x^2 - 1)', '-2/3 = -0.6667'],
          ['integral 1 to 2 of (x^2 - 1)', '4/3 = 1.3333'],
          ['integral 0 to 2 of (x^2 - 1)', '2/3 = 0.6667'],
          ['area between curve and axis, 0 to 2', '2'],
          ['integral -1 to 1 (even integrand)', '2 x (-2/3) = -4/3']
        ];
        table(30, 62, Math.min(w - 60, 560), rows);
        noStroke(); fill(30, 38, 50); textSize(13);
        text('The even rule doubles the integral; it does not change its sign.', 34, 300);
        note('Every number in this table is recomputed in scripts/validate.py.', 30, h - 24);
      }
    }
  ]
};

/* ---------------------------------------------------------------- maths */
function f(x) { return x * x - 1; }
function F(x) { return x * x * x / 3 - x; }

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

function axes(box) {
  stroke(206, 212, 222); strokeWeight(1);
  var o = map2(box, 0, 0);
  line(box.x, o[1], box.x + box.w, o[1]);
  line(o[0], box.y, o[0], box.y + box.h);
  noStroke(); fill(140, 148, 160); textSize(11);
  text('x', box.x + box.w - 10, o[1] - 6);
  text('y', o[0] + 6, box.y + 10);
}

function map2(box, x, y) {
  var px = box.x + (x - box.xmin) / (box.xmax - box.xmin) * box.w;
  var py = box.y + box.h - (y - box.ymin) / (box.ymax - box.ymin) * box.h;
  return [px, py];
}

function plot(box, fn, from, to, col) {
  stroke(col[0], col[1], col[2]); strokeWeight(2.5); noFill();
  var prev = null, n = 200;
  for (var i = 0; i <= n; i++) {
    var x = from + (to - from) * i / n;
    var y = fn(x);
    if (y < box.ymin - 2 || y > box.ymax + 2) { prev = null; continue; }
    var pt = map2(box, x, y);
    if (prev) { line(prev[0], prev[1], pt[0], pt[1]); }
    prev = pt;
  }
  noStroke();
}

/* Fill the region between the curve and the axis from a to b, so the sign is visible as a colour. */
function shade(box, fn, from, to, col) {
  if (!(to > from)) { return; }
  fill(col[0], col[1], col[2], 90); noStroke();
  beginShape();
  var start = map2(box, from, 0);
  vertex(start[0], start[1]);
  var n = 80;
  for (var i = 0; i <= n; i++) {
    var x = from + (to - from) * i / n;
    var pt = map2(box, x, fn(x));
    vertex(pt[0], pt[1]);
  }
  var end = map2(box, to, 0);
  vertex(end[0], end[1]);
  endShape(CLOSE);
  noStroke();
}

/* The tangent to fn at x0, drawn short enough to stay inside the box. */
function tangent(box, fn, x0, slope) {
  var y0 = fn(x0);
  var dx = (box.xmax - box.xmin) * 0.16;
  var p1 = map2(box, x0 - dx, y0 - slope * dx);
  var p2 = map2(box, x0 + dx, y0 + slope * dx);
  stroke(20, 107, 74); strokeWeight(2); noFill();
  line(p1[0], p1[1], p2[0], p2[1]);
  noStroke(); fill(20, 107, 74); circle(map2(box, x0, y0)[0], map2(box, x0, y0)[1], 7);
}

function mark(box, x, y, label) {
  var pt = map2(box, x, y);
  noStroke(); fill(20, 107, 74); circle(pt[0], pt[1], 9);
  fill(20, 107, 74); textSize(12.5); text(label, pt[0] + 9, pt[1] + 16);
}

function table(x, y, w, rows) {
  var cw = w / rows[0].length, rh = 36;
  for (var r = 0; r < rows.length; r++) {
    for (var c = 0; c < rows[r].length; c++) {
      stroke(224, 228, 236); strokeWeight(1);
      fill(r === 0 ? color(243, 246, 251) : color(255));
      rect(x + c * cw, y + r * rh, cw - 4, rh - 4, 4);
      noStroke(); fill(30, 38, 50); textSize(12.5);
      textAlign('center', 'center');
      text(rows[r][c], x + c * cw + (cw - 4) / 2, y + r * rh + (rh - 4) / 2);
      textAlign('left', 'baseline');
    }
  }
}
