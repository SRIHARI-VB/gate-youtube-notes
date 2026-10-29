/* The sign chart of the derivative: why f'(x) = 0 gives candidates, not verdicts.
   Values used here, all recomputed in scripts/validate.py (check_maxima_and_minima):
     f(x) = 3x^4 - 16x^3 + 24x^2 + 37, so f'(x) = 12x(x - 2)^2 with zeros at 0 and 2;
     f(-1) = 80, f(0) = 37, f(2) = 53, f(4) = 165;
     f'(-0.5) = -37.5, f'(1) = 12, f'(3) = 36, so the sign changes at 0 and not at 2;
     f''(x) = 36x^2 - 96x + 48, f''(0) = 48, f''(2) = 0, f'''(2) = 48 (odd order). */
window.LESSON = {
  steps: [
    {
      duration: 2600,
      caption: 'Two different questions. Where does f prime vanish? And where does f prime change sign? The first gives candidates; only the second gives verdicts.',
      draw: function (p, w, h) {
        ink();
        head('Two questions about a critical point', 30, 34);
        rowCard(30, 62, "f'(c) = 0", 'the tangent is horizontal', 'a candidate only');
        rowCard(30, 132, "f' changes sign at c", 'the function turns around', 'the verdict');
        note('A candidate list without a sign check can be twice the right size.', 30, h - 24);
      }
    },
    {
      duration: 3000,
      caption: 'The function is f(x) = 3x^4 - 16x^3 + 24x^2 + 37. Its derivative is f prime of x = 12x(x - 2) squared, which is zero at x = 0 and at x = 2. Nothing else is a candidate.',
      draw: function (p, w, h) {
        ink();
        head('The derivative, factored', 30, 34);
        textSize(14); noStroke(); fill(30, 38, 50);
        text('f(x)  = 3x^4 - 16x^3 + 24x^2 + 37', 34, 74);
        text("f'(x) = 12x^3 - 48x^2 + 48x = 12x(x - 2)^2", 34, 102);
        table(30, 124, Math.min(w - 60, 520), [
          ['zero of f prime', 'multiplicity', 'sign change?'],
          ['x = 0', '1 (odd)', 'yes'],
          ['x = 2', '2 (even)', 'no']
        ]);
        note('An even multiplicity means the sign survives the zero.', 30, h - 24);
      }
    },
    {
      duration: 3400,
      caption: 'Here is the curve. At x = 0 the value is 37, the lowest point shown. At x = 2 the value is 53 - higher than 37, and the curve flattens there but does not turn.',
      draw: function (p, w, h, prog) {
        ink();
        head('The curve, with both stationary points', 30, 34);
        var box = { x: 64, y: 62, w: w - 128, h: h - 128, xmin: -1.2, xmax: 4.2, ymin: 20, ymax: 175 };
        axes(box);
        plot(box, f, -1.2, 4.2, [31, 94, 255]);
        mark(box, 0, 37, 'x = 0, f = 37');
        var grow = Math.min(1, Math.max(0, (prog - 0.35) * 3));
        if (grow > 0) {
          stroke(180, 90, 31); strokeWeight(1.5); noFill();
          var c = map2(box, 2, 53);
          circle(c[0], c[1], 9 + 12 * grow);
          noStroke(); fill(180, 90, 31); textSize(12.5);
          text('x = 2, f = 53', c[0] + 12, c[1] - 10);
        }
        note('Two stationary points. Only one of them is a turning point.', 30, h - 24);
      }
    },
    {
      duration: 3600,
      caption: 'The sign chart decides. Left of 0 the derivative is negative - f prime of minus 0.5 is minus 37.5 - so f falls. Between 0 and 2 it is positive - f prime of 1 is 12 - so f rises. Above 2 it is still positive - f prime of 3 is 36 - so f keeps rising.',
      draw: function (p, w, h) {
        ink();
        head('Sign chart of f prime', 30, 34);
        var y = 66, left = 30, wid = Math.min(w - 60, 620), cell = wid / 3;
        var signs = [
          { label: 'x < 0', sign: 'f prime < 0', arrow: 'falling', col: [180, 90, 31], val: "f'(-0.5) = -37.5" },
          { label: '0 < x < 2', sign: 'f prime > 0', arrow: 'rising', col: [20, 107, 74], val: "f'(1) = 12" },
          { label: 'x > 2', sign: 'f prime > 0', arrow: 'rising', col: [20, 107, 74], val: "f'(3) = 36" }
        ];
        for (var i = 0; i < 3; i++) {
          var s = signs[i];
          noStroke(); fill(243, 246, 251);
          rect(left + i * cell + 3, y, cell - 6, 96, 8);
          fill(70, 80, 98); textSize(12.5);
          text(s.label, left + i * cell + 14, y + 22);
          fill(s.col[0], s.col[1], s.col[2]); textSize(14); textStyle(BOLD);
          text(s.sign, left + i * cell + 14, y + 46);
          textStyle(NORMAL); textSize(12.5);
          text(s.arrow, left + i * cell + 14, y + 68);
          fill(120, 128, 140); textSize(11.5);
          text(s.val, left + i * cell + 14, y + 88);
        }
        noStroke(); fill(30, 38, 50); textSize(13);
        text('at x = 0: minus to plus, so a local minimum', left + 4, y + 128);
        text('at x = 2: plus to plus, so not an extremum', left + 4, y + 152);
        note('Same sign on both sides: the function flattens and carries on.', 30, h - 24);
      }
    },
    {
      duration: 3200,
      caption: 'The second-derivative test is silent here. f double prime of 0 is 48, positive, so x = 0 is a minimum. But f double prime of 2 is 0, so the test cannot classify x = 2 - and the third derivative, 48, is of odd order, which settles it as neither.',
      draw: function (p, w, h) {
        ink();
        head('Why the second-derivative test fails at x = 2', 30, 34);
        table(30, 62, Math.min(w - 60, 560), [
          ['point', "f''", 'order of first nonzero', 'verdict'],
          ['x = 0', '48', '2 (even)', 'local minimum'],
          ['x = 2', '0', '3 (odd)', 'not an extremum']
        ]);
        textSize(13); noStroke(); fill(70, 80, 98);
        text("f''(x) = 36x^2 - 96x + 48, so f''(0) = 48 and f''(2) = 144 - 192 + 48 = 0.", 30, 172);
        text("f'''(x) = 72x - 96, so f'''(2) = 144 - 96 = 48, and its order 3 is odd.", 30, 196);
        note('A zero second derivative is not a verdict; it is a request for more work.', 30, h - 24);
      }
    },
    {
      duration: 3400,
      caption: 'On a closed interval the derivative cannot find the ends. On [-1, 4] the values at the stationary points are 37 and 53, but the endpoints give 80 at x = -1 and 165 at x = 4. The absolute maximum on that interval is 165, at the right endpoint.',
      draw: function (p, w, h, prog) {
        ink();
        head('Closed interval: the endpoints are candidates too', 30, 34);
        var box = { x: 64, y: 62, w: w - 128, h: h - 128, xmin: -1.2, xmax: 4.2, ymin: 20, ymax: 175 };
        axes(box);
        plot(box, f, -1.2, 4.2, [31, 94, 255]);
        mark(box, 0, 37, '37');
        mark(box, 2, 53, '53');
        var grow = Math.min(1, Math.max(0, (prog - 0.3) * 2.5));
        if (grow > 0) {
          stroke(180, 90, 31); strokeWeight(1.5); noFill();
          var a = map2(box, -1, 80), b = map2(box, 4, 165);
          circle(a[0], a[1], 8 + 10 * grow);
          circle(b[0], b[1], 8 + 10 * grow);
          noStroke(); fill(180, 90, 31); textSize(12.5);
          text('f(-1) = 80', a[0] + 8, a[1] - 8);
          text('f(4) = 165', b[0] - 74, b[1] + 18);
        }
        note('Absolute maximum 165 at x = 4; absolute minimum 37 at x = 0.', 30, h - 24);
      }
    }
  ]
};

/* ---------------------------------------------------------------- helpers */
function f(x) { return 3 * Math.pow(x, 4) - 16 * Math.pow(x, 3) + 24 * x * x + 37; }

function ink() {
  var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  background(dark ? color(23, 28, 36) : color(255));
  noStroke();
  fill(dark ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}
function head(t, x, y) { textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function note(t, x, y) { textSize(12.5); fill(90, 100, 116); noStroke(); text(t, x, y); }

function rowCard(x, y, title, sub, third) {
  noStroke(); fill(232, 238, 255);
  rect(x, y, Math.min(width - 2 * x, 520), 56, 8);
  fill(31, 94, 255); textSize(14); textStyle(BOLD); text(title, x + 12, y + 22);
  textStyle(NORMAL); fill(70, 80, 98); textSize(12);
  text(sub, x + 12, y + 40);
  fill(120, 128, 140); textSize(11.5); text(third, x + 210, y + 40);
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

function mark(box, x, y, label) {
  var pt = map2(box, x, y);
  noStroke(); fill(20, 107, 74); circle(pt[0], pt[1], 9);
  fill(20, 107, 74); textSize(12.5); text(label, pt[0] + 8, pt[1] + 16);
}

function axes(box) {
  stroke(206, 212, 222); strokeWeight(1);
  var o = map2(box, 0, 0);
  line(box.x, o[1], box.x + box.w, o[1]);
  line(o[0], box.y, o[0], box.y + box.h);
  noStroke(); fill(140, 148, 160); textSize(11);
  text('x', box.x + box.w - 10, o[1] - 6);
  text('y', o[0] + 6, box.y + 10);
  text('0', o[0] - 10, o[1] + 13);
}

function map2(box, x, y) {
  var px = box.x + (x - box.xmin) / (box.xmax - box.xmin) * box.w;
  var py = box.y + box.h - (y - box.ymin) / (box.ymax - box.ymin) * box.h;
  return [px, py];
}

function plot(box, fn, from, to, col) {
  stroke(col[0], col[1], col[2]); strokeWeight(2.5); noFill();
  var prev = null, n = 240;
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
