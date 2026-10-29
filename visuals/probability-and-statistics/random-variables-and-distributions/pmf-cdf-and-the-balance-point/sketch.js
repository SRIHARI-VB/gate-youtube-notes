/* PMF, CDF and the balance point, for the Random Variables and Distributions topic.
   The distribution used is the one in GATE CSE 2026 Set 1 Q.48:
     values 1..8, with P(1) = P(2) = P(5) = P(7) = 1/6 and P(3) = P(4) = P(6) = P(8) = 1/12.
   Every number drawn here is recomputed in scripts/validate.py
   (check_probability_and_statistics):
     the probabilities sum to 1;
     E[X] = (1+2+5+7)/6 + (3+4+6+8)/12 = 51/12 = 4.25;
     E[X^2] = (1+4+25+49)/6 + (9+16+36+64)/12 = 283/12 = 23.58333;
     Var(X) = 283/12 - (51/12)^2 = 265/48 = 5.520833, sd = 2.349645;
     the CDF is 1/6, 1/3, 5/12, 1/2, 2/3, 3/4, 11/12, 1 at x = 1..8;
     the discrete uniform on {1..8} has mean 4.5 and variance 63/12 = 5.25. */
window.LESSON = {
  steps: [
    {
      duration: 3600,
      caption: 'The probability mass function of X: a bar for every value, whose height is the probability of that value. Values 1, 2, 5 and 7 carry 1/6 each; values 3, 4, 6 and 8 carry 1/12 each, so the bars are not all the same height.',
      draw: function (p, w, h) {
        ink();
        head('The probability mass function', 30, 34);
        var box = plotBox(w, h);
        axis(box);
        var t = Math.min(1, Math.max(0, p));
        bars(box, t, null);
        noStroke(); fill(30, 38, 50); textSize(13);
        text('P(X = 1) = 1/6 = 0.1667 and P(X = 3) = 1/12 = 0.0833', 34, 58);
        note('A mass function gives the probability of each single value, and only of values X can take.', 30, h - 24);
      }
    },
    {
      duration: 3400,
      caption: 'The heights add up to one: four bars of 1/6 and four of 1/12 give 4/6 + 4/12, which is two thirds plus one third. A table whose probabilities do not total one is not a distribution, and averaging over it is meaningless.',
      draw: function (p, w, h) {
        ink();
        head('The total is exactly 1', 30, 34);
        var box = plotBox(w, h);
        axis(box);
        var t = Math.min(1, Math.max(0, p));
        var run = 0;
        for (var i = 0; i < P.length; i++) {
          var reach = Math.min(1, Math.max(0, t * P.length - i));
          var pp = map2(box, VALS[i], 0);
          var qq = map2(box, VALS[i], P[i] * reach);
          fill(31, 94, 255, 150); noStroke();
          rect(pp[0] - barW(box) / 2, qq[1], barW(box), pp[1] - qq[1], 3);
          run += P[i] * reach;
        }
        noStroke(); fill(30, 38, 50); textSize(13);
        text('running total = ' + run.toFixed(4) + '  (the whole table is 1)', 34, 58);
        note('This is the check to run before computing any expectation or variance.', 30, h - 24);
      }
    },
    {
      duration: 3600,
      caption: 'The cumulative distribution function is the running sum: F(x) = P(X <= x). It is a staircase, flat between values and jumping by exactly the mass at each value. At x = 4 it is 1/6 + 1/6 + 1/12 + 1/12 = 1/2.',
      draw: function (p, w, h) {
        ink();
        head('The CDF is the running sum', 30, 34);
        var box = plotBox(w, h);
        axis(box);
        var t = Math.min(1, Math.max(0, p));
        var shown = Math.min(P.length, Math.floor(t * P.length) + 1);
        var acc = 0, prev = map2(box, 0.4, 0);
        stroke(20, 107, 74); strokeWeight(2.5); noFill();
        for (var i = 0; i < shown; i++) {
          var a = map2(box, VALS[i] - 0.5, acc);
          line(prev[0], prev[1], a[0], a[1]);
          acc += P[i];
          var b = map2(box, VALS[i] + 0.5, acc);
          line(a[0], a[1], b[0], b[1]);
          prev = b;
        }
        stroke(224, 228, 236); strokeWeight(1);
        var half = map2(box, 0, 0.5);
        line(box.x, half[1], box.x + box.w, half[1]);
        noStroke(); fill(30, 38, 50); textSize(12.5);
        text('F(4) = 0.5 (the dotted line is one half)', box.x + 6, half[1] - 8);
        note('Between values the CDF is flat; the jump at a value is that value\'s probability.', 30, h - 24);
      }
    },
    {
      duration: 3800,
      caption: 'Expectation is the balance point of the bars. Weight each value by its probability and add: the four 1/6 values contribute 15/6, the four 1/12 values contribute 21/12, and the total is 4.25. The unweighted average of 1 to 8 is 4.5, which is a different question.',
      draw: function (p, w, h) {
        ink();
        head('The balance point: E[X] = 4.25', 30, 34);
        var box = plotBox(w, h);
        axis(box);
        var t = Math.min(1, Math.max(0, p));
        var acc = 0;
        for (var i = 0; i < P.length; i++) {
          var step = Math.min(1, Math.max(0, t * P.length - i));
          acc += VALS[i] * P[i] * step;
          var pt = map2(box, VALS[i], 0);
          noStroke(); fill(31, 94, 255, 90);
          circle(pt[0], pt[1] - 14, 8 + 60 * P[i] * step);
        }
        var e = map2(box, E, 0);
        stroke(196, 74, 74); strokeWeight(2.5); noFill();
        line(e[0], box.y, e[0], box.y + box.h);
        noStroke(); fill(196, 74, 74); textSize(13);
        text('E[X] = ' + acc.toFixed(2), e[0] + 6, box.y + 16);
        note('Bigger circles are heavier weights, so the balance point sits left of the midpoint 4.5.', 30, h - 24);
      }
    },
    {
      duration: 3600,
      caption: 'Variance is the probability-weighted average of the squared distance from the balance point. Each squared gap is 4.25 minus the value, squared; weighting and adding gives 265/48, about 5.52, so the standard deviation is about 2.35.',
      draw: function (p, w, h) {
        ink();
        head('Variance: squared gaps, weighted', 30, 34);
        var box = plotBox(w, h);
        axis(box);
        var t = Math.min(1, Math.max(0, p));
        var total = 0, top = 0;
        for (var i = 0; i < P.length; i++) {
          top = Math.max(top, P[i] * (VALS[i] - E) * (VALS[i] - E));
        }
        for (var j = 0; j < P.length; j++) {
          var piece = P[j] * (VALS[j] - E) * (VALS[j] - E);
          var step2 = Math.min(1, Math.max(0, t * P.length - j));
          total += piece * step2;
          var pp = map2(box, VALS[j], 0);
          var qq = map2(box, VALS[j], piece / top * 0.16);
          fill(196, 74, 74, 150); noStroke();
          rect(pp[0] - barW(box) / 2, qq[1], barW(box), pp[1] - qq[1], 3);
        }
        noStroke(); fill(30, 38, 50); textSize(13);
        text('weighted squared gaps total = ' + total.toFixed(4) + '  (265/48 = 5.5208)', 34, 58);
        note('The variance is in squared units, so the square root - about 2.35 - is the width in units of X.', 30, h - 24);
      }
    },
    {
      duration: 3400,
      caption: 'Same eight values, different distribution. If the eight values were equally likely the mean would be 4.5 and the variance 63/12, which is 5.25. So the support alone never fixes the answer: the probabilities do.',
      draw: function (p, w, h) {
        ink();
        head('Same support, different distribution', 30, 34);
        var t = Math.min(1, Math.max(0, p));
        var halfW = (w - 100) / 2;
        var left = { x: 40, y: 70, w: halfW, h: h - 170, xmin: 0.4, xmax: 8.6, ymin: 0, ymax: 0.2 };
        var right = { x: 60 + halfW, y: 70, w: halfW, h: h - 170, xmin: 0.4, xmax: 8.6, ymin: 0, ymax: 0.2 };
        axis(left); axis(right);
        for (var i = 0; i < P.length; i++) {
          var a = map2(left, VALS[i], 0), b = map2(left, VALS[i], P[i] * t);
          fill(31, 94, 255, 150); noStroke();
          rect(a[0] - barW(left) / 2, b[1], barW(left), a[1] - b[1], 3);
          var c = map2(right, VALS[i], 0), d = map2(right, VALS[i], 0.125 * t);
          fill(20, 107, 74, 150); noStroke();
          rect(c[0] - barW(right) / 2, d[1], barW(right), c[1] - d[1], 3);
        }
        noStroke(); fill(30, 38, 50); textSize(12.5);
        text('this question: mean 4.25, variance 5.5208', left.x + 4, left.y - 8);
        text('uniform on 1..8: mean 4.5, variance 5.25', right.x + 4, right.y - 8);
        note('The uniform bars are all 1/8 = 0.125, so the shape, the mean and the variance all change.', 30, h - 24);
      }
    },
    {
      duration: 3000,
      caption: 'Quick check. The probabilities sum to 1, the mean is 4.25, the CDF at 4 is 0.5, the variance is 5.5208 and the standard deviation 2.3496. Each of these is one line of arithmetic from the table, and each is recomputed in the validator.',
      draw: function (p, w, h) {
        ink();
        head('Quick check', 30, 34);
        var rows = [
          ['quantity', 'value'],
          ['sum of the probabilities', '1'],
          ['E[X]', '51/12 = 4.25'],
          ['F(4) = P(X <= 4)', '0.5'],
          ['E[X^2]', '283/12 = 23.5833'],
          ['Var(X) = E[X^2] - (E[X])^2', '265/48 = 5.5208'],
          ['standard deviation', '2.3496']
        ];
        table(30, 62, Math.min(w - 60, 560), rows);
        noStroke(); fill(30, 38, 50); textSize(13);
        text('Variance is not E[X^2] - E[X]: that would give 19.33 here.', 34, 320);
        note('Every number in this table is recomputed in scripts/validate.py.', 30, h - 24);
      }
    }
  ]
};

/* ---------------------------------------------------------------- maths */
var VALS = [1, 2, 3, 4, 5, 6, 7, 8];
var P = [1 / 6, 1 / 6, 1 / 12, 1 / 12, 1 / 6, 1 / 12, 1 / 6, 1 / 12];
var E = 4.25;

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

function plotBox(w, h) {
  return { x: 66, y: 80, w: w - 132, h: h - 190, xmin: 0.4, xmax: 8.6, ymin: 0, ymax: 0.2 };
}

function map2(box, x, y) {
  var px = box.x + (x - box.xmin) / (box.xmax - box.xmin) * box.w;
  var py = box.y + box.h - (y - box.ymin) / (box.ymax - box.ymin) * box.h;
  return [px, py];
}

function barW(box) {
  return (box.w / (box.xmax - box.xmin)) * 0.62;
}

function axis(box) {
  stroke(206, 212, 222); strokeWeight(1);
  var base = map2(box, box.xmin, 0);
  line(box.x, base[1], box.x + box.w, base[1]);
  noStroke(); fill(140, 148, 160); textSize(11);
  for (var i = 0; i < VALS.length; i++) {
    var pt = map2(box, VALS[i], 0);
    text(String(VALS[i]), pt[0] - 4, base[1] + 16);
  }
  text('value of X', box.x + box.w - 66, base[1] + 30);
}

/* Draw the bars up to fraction t of the way through the table. */
function bars(box, t, unused) {
  var n = P.length;
  for (var i = 0; i < n; i++) {
    var step = Math.min(1, Math.max(0, t * n - i));
    if (step <= 0) { continue; }
    var a = map2(box, VALS[i], 0);
    var b = map2(box, VALS[i], P[i] * step);
    fill(31, 94, 255, 150); noStroke();
    rect(a[0] - barW(box) / 2, b[1], barW(box), a[1] - b[1], 3);
    fill(30, 38, 50); textSize(11);
    text(P[i].toFixed(3), a[0] - 14, b[1] - 6);
  }
}

function table(x, y, w, rows) {
  var cw = w / rows[0].length, rh = 34;
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
