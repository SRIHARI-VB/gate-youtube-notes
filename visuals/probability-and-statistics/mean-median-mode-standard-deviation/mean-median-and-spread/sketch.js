/* Mean, median and spread under a shift and a scale, for the Mean, Median, Mode and
   Standard Deviation topic. One data set is followed through four versions of itself:

     base     2, 3, 3, 4, 9        mean 4.2   median 3   mode 3   var 6.16    sd 2.4819
     outlier  2, 3, 3, 4, 19       mean 6.2   median 3   mode 3   var 41.36   sd 6.4312
     shifted  12, 13, 13, 14, 29   mean 16.2  median 13  mode 13  var 41.36   sd 6.4312
     doubled  4, 6, 6, 8, 38       mean 12.4  median 6   mode 6   var 165.44  sd 12.8624

   Every one of those numbers is recomputed in scripts/validate.py
   (check_mean_median_mode) from the lists themselves, not copied from here:
     the signed deviations sum to zero in every version;
     the shifted version has the same variance as the version it came from;
     the doubled version has four times that variance and twice the standard deviation;
     the doubled mean is twice the mean and the doubled median is twice the median. */

var SETS = [
  { data: [2, 3, 3, 4, 9] },
  { data: [2, 3, 3, 4, 9] },
  { data: [2, 3, 3, 4, 9] },
  { data: [2, 3, 3, 4, 19] },
  { data: [12, 13, 13, 14, 29] },
  { data: [4, 6, 6, 8, 38] }
];

var BOX = { xmin: 0, xmax: 40 };

window.LESSON = {
  steps: [
    {
      duration: 3600,
      caption: 'Five values on a number line: 2, 3, 3, 4 and 9. The mean is 4.2, and it is the balance point - the values to its left are exactly balanced by the values to its right, so the signed deviations add up to zero.',
      draw: function (p, w, h) {
        ink();
        head('The mean is the balance point', 30, 34);
        var box = plotBox(w, h);
        axis(box);
        var d = at(0, p);
        points(box, d, w, h);
        mark(box, stat(d).mean, 'mean 4.2', 31, 94, 255, h);
        readout(w, h, d, 'the signed deviations sum to 0');
        note('The mean uses the sizes of the values, which is why it can be dragged.', 30, h - 24);
      }
    },
    {
      duration: 3800,
      caption: 'The same five values, now with each deviation drawn as a bar from the mean. Squaring the bars, averaging them and taking the square root gives the standard deviation 2.4819: a root-mean-square distance, not an ordinary distance.',
      draw: function (p, w, h) {
        ink();
        head('The standard deviation is a root mean square', 30, 34);
        var box = plotBox(w, h);
        axis(box);
        var d = at(1, p);
        var s = stat(d);
        bars(box, d, s.mean, Math.min(1, Math.max(0, p)), h);
        points(box, d, w, h);
        mark(box, s.mean, 'mean ' + fmt(s.mean), 31, 94, 255, h);
        noStroke(); fill(30, 38, 50); textSize(13);
        text('mean of the squared deviations = ' + s.vary.toFixed(2), 34, 58);
        text('standard deviation = ' + s.sd.toFixed(4), 34, 76);
        note('The 9 is 4.8 away from the mean and contributes 23.04 of the 30.8 total.', 30, h - 24);
      }
    },
    {
      duration: 3600,
      caption: 'Now the other two summaries. Sorting the values gives 2, 3, 3, 4, 9, so the middle one is the median, 3. The mode is the most frequent value, also 3. The mean 4.2 sits to the right of both, because the 9 is pulling it.',
      draw: function (p, w, h) {
        ink();
        head('Median 3 and mode 3, mean 4.2', 30, 34);
        var box = plotBox(w, h);
        axis(box);
        var d = at(2, p);
        var s = stat(d);
        points(box, d, w, h);
        mark(box, s.mode, 'mode 3', 20, 107, 74, h);
        mark(box, s.median, 'median 3', 176, 108, 24, h);
        mark(box, s.mean, 'mean 4.2', 31, 94, 255, h);
        readout(w, h, d, 'the 9 alone separates the mean from the other two');
        note('A value can be both the median and the mode, as 3 is here.', 30, h - 24);
      }
    },
    {
      duration: 3800,
      caption: 'One value is replaced: 9 becomes 19. The mean jumps from 4.2 to 6.2 and the standard deviation from 2.4819 to 6.4312, while the median and the mode do not move at all. This is what robustness means.',
      draw: function (p, w, h) {
        ink();
        head('One outlier: the mean moves, the median does not', 30, 34);
        var box = plotBox(w, h);
        axis(box);
        var d = at(3, p);
        var s = stat(d);
        points(box, d, w, h);
        mark(box, s.mode, 'mode 3', 20, 107, 74, h);
        mark(box, s.median, 'median 3', 176, 108, 24, h);
        mark(box, s.mean, 'mean ' + fmt(s.mean), 31, 94, 255, h);
        readout(w, h, d, 'sd is now ' + s.sd.toFixed(4) + ', up from 2.4819');
        note('The median only counts ranks; the mean and the standard deviation use sizes.', 30, h - 24);
      }
    },
    {
      duration: 3800,
      caption: 'Add 10 to every value. The mean moves from 6.2 to 16.2 and the median from 3 to 13, but the standard deviation is still 6.4312 and the variance is unchanged. A shift cannot widen or narrow a spread.',
      draw: function (p, w, h) {
        ink();
        head('A shift moves the centre and nothing else', 30, 34);
        var box = plotBox(w, h);
        axis(box);
        var d = at(4, p);
        var s = stat(d);
        points(box, d, w, h);
        mark(box, s.median, 'median ' + fmt(s.median), 176, 108, 24, h);
        mark(box, s.mean, 'mean ' + fmt(s.mean), 31, 94, 255, h);
        readout(w, h, d, 'sd is still ' + s.sd.toFixed(4));
        note('Deviations are measured from the mean, and the mean moved by the same 10.', 30, h - 24);
      }
    },
    {
      duration: 4000,
      caption: 'Now double every value instead. The mean doubles from 6.2 to 12.4, the median doubles from 3 to 6, and the standard deviation doubles from 6.4312 to 12.8624 - the variance multiplies by four. A scale multiplies a spread; a shift never does.',
      draw: function (p, w, h) {
        ink();
        head('A scale multiplies the spread', 30, 34);
        var box = plotBox(w, h);
        axis(box);
        var d = at(5, p);
        var s = stat(d);
        points(box, d, w, h);
        mark(box, s.median, 'median ' + fmt(s.median), 176, 108, 24, h);
        mark(box, s.mean, 'mean ' + fmt(s.mean), 31, 94, 255, h);
        readout(w, h, d, 'sd is now ' + s.sd.toFixed(4) + ' = 2 x 6.4312');
        note('sd(aX + b) = |a| x sd(X); the b has nowhere to enter.', 30, h - 24);
      }
    }
  ],
  example: {
    base: { data: [2, 3, 3, 4, 9], mean: 4.2, median: 3, mode: 3, variance: 6.16, sd: 2.4819 },
    outlier: { data: [2, 3, 3, 4, 19], mean: 6.2, median: 3, mode: 3, variance: 41.36, sd: 6.4312 },
    shifted: { data: [12, 13, 13, 14, 29], mean: 16.2, median: 13, mode: 13, variance: 41.36, sd: 6.4312 },
    doubled: { data: [4, 6, 6, 8, 38], mean: 12.4, median: 6, mode: 6, variance: 165.44, sd: 12.8624 },
    quick_check: {
      question: 'The base data has standard deviation 2.4819. What is the standard deviation of 3X - 7?',
      answer: 7.4457,
      note: 'sd(3X - 7) = |3| x 2.4819 = 7.4457; the -7 shifts every value and every mean equally, so it leaves the spread alone.'
    }
  }
};

/* ---------------------------------------------------------------- statistics */
function stat(d) {
  var n = d.length, sum = 0, i;
  for (i = 0; i < n; i++) { sum += d[i]; }
  var mean = sum / n;
  var sq = 0;
  for (i = 0; i < n; i++) { sq += (d[i] - mean) * (d[i] - mean); }
  var sorted = d.slice().sort(function (a, b) { return a - b; });
  var median = n % 2 ? sorted[(n - 1) / 2] : (sorted[n / 2 - 1] + sorted[n / 2]) / 2;
  var counts = {}, best = 0, mode = sorted[0];
  for (i = 0; i < n; i++) {
    counts[d[i]] = (counts[d[i]] || 0) + 1;
    if (counts[d[i]] > best) { best = counts[d[i]]; mode = d[i]; }
  }
  return { mean: mean, median: median, mode: mode, vary: sq / n, sd: Math.sqrt(sq / n) };
}

/* The data of step i, interpolated from the previous step's data so the points travel. */
function at(i, p) {
  var to = SETS[i].data;
  var from = i === 0 ? to : SETS[i - 1].data;
  var t = Math.min(1, Math.max(0, p));
  var out = [];
  for (var k = 0; k < to.length; k++) { out.push(from[k] + (to[k] - from[k]) * t); }
  return out;
}

function fmt(x) {
  return (Math.round(x * 100) / 100).toFixed(2).replace(/\.00$/, '');
}

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
  return { x: 62, y: 120, w: w - 124, h: h - 250, xmin: BOX.xmin, xmax: BOX.xmax };
}

function map2(box, x) {
  var px = box.x + (x - box.xmin) / (box.xmax - box.xmin) * box.w;
  return px;
}

function axis(box) {
  var base = box.y + box.h;
  stroke(206, 212, 222); strokeWeight(1);
  line(box.x, base, box.x + box.w, base);
  noStroke(); fill(140, 148, 160); textSize(11);
  for (var v = 0; v <= 40; v += 5) {
    var px = map2(box, v);
    line(px, base - 4, px, base + 4);
    text(String(v), px - 5, base + 18);
  }
  text('value', box.x + box.w - 30, base + 34);
}

/* One dot per value; equal values are stacked upward so they can be counted. */
function points(box, d, w, h) {
  var base = box.y + box.h;
  var seen = {};
  for (var i = 0; i < d.length; i++) {
    var key = String(Math.round(d[i] * 1000));
    seen[key] = (seen[key] || 0) + 1;
    var px = map2(box, d[i]);
    var py = base - 12 - (seen[key] - 1) * 16;
    fill(31, 94, 255); noStroke();
    circle(px, py, 11);
    fill(30, 38, 50); textSize(11);
    text(String(Math.round(d[i] * 10) / 10), px - 6, py - 9);
  }
}

/* A vertical marker with a label at the top of the plot area. */
function mark(box, value, label, r, g, b, h) {
  var px = map2(box, value);
  var base = box.y + box.h;
  stroke(r, g, b); strokeWeight(2);
  line(px, box.y - 4, px, base);
  noStroke(); fill(r, g, b); textSize(12);
  text(label, px + 5, box.y - 8);
}

/* Bars from the mean to each value, drawn to fraction t of their length. */
function bars(box, d, mean, t, h) {
  var base = box.y + box.h;
  var mx = map2(box, mean);
  for (var i = 0; i < d.length; i++) {
    var px = map2(box, d[i]);
    var py = base - 12;
    var reach = px + (d[i] > mean ? -1 : 1) * 0;
    stroke(d[i] > mean ? color(196, 74, 42) : color(20, 107, 74));
    strokeWeight(3);
    line(mx, py - i * 0.5, mx + (px - mx) * t, py - i * 0.5);
  }
  noStroke();
}

function readout(w, h, d, extra) {
  var s = stat(d);
  noStroke(); fill(30, 38, 50); textSize(13);
  text('mean ' + s.mean.toFixed(2) + '   median ' + fmt(s.median) + '   mode ' + fmt(s.mode) +
       '   variance ' + s.vary.toFixed(2) + '   sd ' + s.sd.toFixed(4), 34, 58);
  fill(90, 100, 116); textSize(12.5);
  text(extra, 34, 78);
}
