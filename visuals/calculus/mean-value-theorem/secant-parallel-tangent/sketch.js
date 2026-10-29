/* The secant and the parallel tangent: where the mean value theorem point comes from.
   Values used here, all recomputed in scripts/validate.py (check_mean_value_theorem):
     f(x) = x^3 on [0, 2], chord slope (8 - 0)/(2 - 0) = 4;
     f'(x) = 3x^2, so f'(0) = 0, f'(1) = 3, f'(2) = 12, and 3c^2 = 4 gives c = 2/sqrt(3) = 1.1547;
     f(c) = 8/(3 sqrt(3)) = 1.5396, and f'(c) = 4 exactly;
     Rolle case g(x) = x^3 - 4x on [-2, 2]: g(-2) = g(2) = 0, g'(x) = 3x^2 - 4, zeros at plus and minus 1.1547;
     failure case |x| on [-1, 1]: f(-1) = f(1) = 1, slope -1 on the left, +1 on the right, no zero slope. */
window.LESSON = {
  steps: [
    {
      duration: 2800,
      caption: 'Two averages. The chord from (0, 0) to (2, 8) has slope 4: that is the average rate of change of x cubed over [0, 2].',
      draw: function (p, w, h) {
        ink();
        head('The chord gives the average slope', 30, 34);
        var box = { x: 66, y: 62, w: w - 132, h: h - 130, xmin: -0.25, xmax: 2.25, ymin: -0.6, ymax: 8.6 };
        axes(box);
        plot(box, f, 0, 2, [31, 94, 255]);
        var a = map2(box, 0, 0), b = map2(box, 2, 8);
        stroke(180, 90, 31); strokeWeight(2); noFill();
        line(a[0], a[1], b[0], b[1]);
        mark(box, 0, 0, '(0, 0)');
        mark(box, 2, 8, '(2, 8)');
        noStroke(); fill(180, 90, 31); textSize(13);
        text('slope = (8 - 0) / (2 - 0) = 4', 34, 62);
        note('The chord slope is the average rate of change over the whole interval.', 30, h - 24);
      }
    },
    {
      duration: 3400,
      caption: 'Now slide a tangent along the curve. At x = 0 its slope is 0, at x = 1 it is 3, at x = 2 it is 12. Somewhere between 0 and 1 it must pass through 4.',
      draw: function (p, w, h, prog) {
        ink();
        head('The tangent slope rises from 0 to 12', 30, 34);
        var box = { x: 66, y: 62, w: w - 132, h: h - 130, xmin: -0.25, xmax: 2.25, ymin: -0.6, ymax: 8.6 };
        axes(box);
        plot(box, f, 0, 2, [31, 94, 255]);
        var a = map2(box, 0, 0), b = map2(box, 2, 8);
        stroke(180, 90, 31); strokeWeight(1.5); noFill();
        line(a[0], a[1], b[0], b[1]);
        var t = Math.min(1, Math.max(0, prog));
        var x0 = 2 * t;
        tangent(box, f, x0, 3 * x0 * x0);
        noStroke(); fill(20, 107, 74); textSize(13);
        text("at x = " + x0.toFixed(2) + ", slope = " + (3 * x0 * x0).toFixed(2), 34, 62);
        note('The tangent slope climbs from 0 to 12, so it takes the value 4 on the way.', 30, h - 24);
      }
    },
    {
      duration: 3400,
      caption: 'Solve 3c squared = 4 and c is 2 over root 3, about 1.155. There the tangent has slope exactly 4, parallel to the chord - that is the point the theorem promises.',
      draw: function (p, w, h) {
        ink();
        head('The parallel tangent, at c = 2/sqrt(3)', 30, 34);
        var box = { x: 66, y: 62, w: w - 132, h: h - 130, xmin: -0.25, xmax: 2.25, ymin: -0.6, ymax: 8.6 };
        axes(box);
        plot(box, f, 0, 2, [31, 94, 255]);
        var a = map2(box, 0, 0), b = map2(box, 2, 8);
        stroke(180, 90, 31); strokeWeight(1.5); noFill();
        line(a[0], a[1], b[0], b[1]);
        tangent(box, f, C, 4);
        mark(box, C, f(C), 'c = 1.1547, f(c) = 1.5396');
        noStroke(); fill(20, 107, 74); textSize(13);
        text("f'(c) = 3c^2 = 4, so c = 2/sqrt(3)", 34, 62);
        note('Tangent slope 4 equals chord slope 4: the two lines are parallel.', 30, h - 24);
      }
    },
    {
      duration: 3200,
      caption: 'Rolle is the same picture with a flat chord. For x cubed minus 4x on [-2, 2] the endpoints both sit at 0, and the derivative 3x squared minus 4 vanishes twice, at plus and minus 1.155.',
      draw: function (p, w, h) {
        ink();
        head('Flat chord: two horizontal tangents', 30, 34);
        var box = { x: 66, y: 62, w: w - 132, h: h - 130, xmin: -2.3, xmax: 2.3, ymin: -4.2, ymax: 4.2 };
        axes(box);
        plot(box, g, -2, 2, [31, 94, 255]);
        var a = map2(box, -2, 0), b = map2(box, 2, 0);
        stroke(180, 90, 31); strokeWeight(1.5); noFill();
        line(a[0], a[1], b[0], b[1]);
        tangent(box, g, C, 0);
        tangent(box, g, -C, 0);
        mark(box, C, g(C), 'c = 1.1547');
        mark(box, -C, g(-C), 'c = -1.1547');
        noStroke(); fill(20, 107, 74); textSize(13);
        text('g(-2) = g(2) = 0, so the average slope is 0', 34, 62);
        note('Two points satisfy Rolle here: the theorem promises at least one.', 30, h - 24);
      }
    },
    {
      duration: 3200,
      caption: 'Take away differentiability and the guarantee dies. Modulus of x on [-1, 1] has equal endpoint values and a flat chord, but its slope is minus 1 and then plus 1, and it never reaches 0.',
      draw: function (p, w, h) {
        ink();
        head('Why the hypothesis is needed', 30, 34);
        var box = { x: 66, y: 62, w: w - 132, h: h - 130, xmin: -1.3, xmax: 1.3, ymin: -0.4, ymax: 1.5 };
        axes(box);
        plot(box, absf, -1, 0, [31, 94, 255]);
        plot(box, absf, 0, 1, [31, 94, 255]);
        var a = map2(box, -1, 1), b = map2(box, 1, 1);
        stroke(180, 90, 31); strokeWeight(1.5); noFill();
        line(a[0], a[1], b[0], b[1]);
        var corner = map2(box, 0, 0);
        noStroke(); fill(180, 90, 31); circle(corner[0], corner[1], 9);
        fill(180, 90, 31); textSize(12.5);
        text('corner: no derivative at 0', corner[0] + 10, corner[1] - 10);
        textSize(13); fill(20, 107, 74);
        text('slope -1 on (-1, 0), +1 on (0, 1), never 0', 34, 62);
        note('A single point without a derivative breaks the theorem completely.', 30, h - 24);
      }
    },
    {
      duration: 2600,
      caption: 'Quick check. For f of x = x cubed minus 3x on [0, 2], the average slope is 1 and the derivative is 3x squared minus 3, so c is again 2 over root 3.',
      draw: function (p, w, h) {
        ink();
        head('Quick check', 30, 34);
        var rows = [
          ['quantity', 'value'],
          ['f(2) - f(0)', '2 - 0 = 2'],
          ['average slope', '2 / 2 = 1'],
          ["f'(c) = 3c^2 - 3", '1, so c^2 = 4/3'],
          ['c', '2/sqrt(3) = 1.1547']
        ];
        table(30, 62, Math.min(w - 60, 520), rows);
        noStroke(); fill(30, 38, 50); textSize(13);
        text('Is the answer the midpoint x = 1? No: f\'(1) = 0, not 1.', 34, 246);
        note('The point is the midpoint only for a quadratic.', 30, h - 24);
      }
    }
  ]
};

/* ---------------------------------------------------------------- maths */
var C = 2 / Math.sqrt(3);          /* 1.1547005..., the mean value theorem point */
function f(x) { return x * x * x; }
function g(x) { return x * x * x - 4 * x; }
function absf(x) { return Math.abs(x); }

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

/* The tangent to the curve fn at x0, drawn short enough to stay inside the box. */
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
