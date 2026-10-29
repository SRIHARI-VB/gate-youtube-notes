/* One-sided limits and the hole: what a limit is not.
   Values used here, all recomputed in scripts/validate.py (check_limits_continuity_differentiability):
     f(x) = (x^2 - 1)/(x - 1) = x + 1 away from x = 1, so f(0.9) = 1.9, f(0.99) = 1.99,
     f(1.1) = 2.1, f(1.01) = 2.01, and the limit at 1 is 2 although f(1) is undefined;
     g(x) = |x|/x has left limit -1 and right limit +1 at 0, so the limit does not exist;
     h(x) = 2x + 1 for x < 3 and 3x - 2 for x >= 3 has both one-sided limits 7 at x = 3,
     so h is continuous at 3 with h(3) = 7. */
window.LESSON = {
  steps: [
    {
      duration: 2400,
      caption: 'Two different questions about one point. What is f(1)? And where does f(x) head as x approaches 1? The second question is the limit, and it does not look at f(1) at all.',
      draw: function (p, w, h) {
        ink();
        head('Two questions, one point', 30, 34);
        rowCard(30, 62, 'f(1)', 'the value at the point', 'may be undefined, may be anything');
        rowCard(30, 132, 'lim(x -> 1) f(x)', 'where the values head', 'decided only by nearby x');
        note('A limit is about approach, not arrival.', 30, h - 24);
      }
    },
    {
      duration: 3200,
      caption: 'Take f(x) = (x^2 - 1)/(x - 1). Coming from the left, x = 0.9 gives 1.9, x = 0.99 gives 1.99, x = 0.999 gives 1.999. Coming from the right, x = 1.1 gives 2.1, x = 1.01 gives 2.01, x = 1.001 gives 2.001.',
      draw: function (p, w, h) {
        ink();
        head('Approaching 1 from both sides', 30, 34);
        table(30, 58, w - 60, [
          ['x', '0.9', '0.99', '0.999', '1.001', '1.01', '1.1'],
          ['f(x)', '1.9', '1.99', '1.999', '2.001', '2.01', '2.1']
        ]);
        note('Both columns are closing in on 2. Nothing here used f(1).', 30, h - 24);
      }
    },
    {
      duration: 3000,
      caption: 'The graph is the line y = x + 1 with a single point removed at (1, 2). The hole is where f is undefined, and the limit is exactly the height the hole sits at: 2.',
      draw: function (p, w, h, prog) {
        ink();
        head('A hole at (1, 2): the limit is still 2', 30, 34);
        var box = { x: 60, y: 60, w: w - 120, h: h - 120, xmin: 0, xmax: 2.4, ymin: 0.6, ymax: 3.4 };
        axes(box);
        plot(box, function (x) { return x + 1; }, 0, 2.4, [31, 94, 255]);
        var pt = map2(box, 1, 2);
        noStroke(); fill(255); circle(pt[0], pt[1], 13);
        stroke(31, 94, 255); strokeWeight(2); noFill(); circle(pt[0], pt[1], 13); noStroke();
        var grow = Math.min(1, Math.max(0, (prog - 0.4) * 3));
        if (grow > 0) {
          stroke(180, 90, 31); strokeWeight(1.5);
          var a = map2(box, 0.55, 2), b = map2(box, 0.98, 2);
          line(a[0], a[1], a[0] + (b[0] - a[0]) * grow, b[1]);
          var c = map2(box, 1.02, 2), d = map2(box, 1.45, 2);
          line(c[0], c[1], c[0] + (d[0] - c[0]) * grow, d[1]);
          textSize(12.5); fill(180, 90, 31);
          text('both sides rise to 2', map2(box, 1.02, 2)[0] + 4, map2(box, 1.45, 2)[1] + 4);
        }
        note('f(1) is undefined. The limit at 1 exists and equals 2.', 30, h - 24);
      }
    },
    {
      duration: 3000,
      caption: 'A limit can fail. For g(x) = |x|/x the left-hand limit is -1 and the right-hand limit is +1. The two one-sided limits disagree, so lim(x -> 0) g(x) does not exist.',
      draw: function (p, w, h) {
        ink();
        head('A jump: the one-sided limits disagree', 30, 34);
        var box = { x: 60, y: 66, w: w - 120, h: h - 130, xmin: -1.6, xmax: 1.6, ymin: -1.8, ymax: 1.8 };
        axes(box);
        var l1 = map2(box, -1.5, -1), l2 = map2(box, 0, -1);
        var r1 = map2(box, 0, 1), r2 = map2(box, 1.5, 1);
        stroke(31, 94, 255); strokeWeight(2.5);
        line(l1[0], l1[1], l2[0], l2[1]);
        line(r1[0], r1[1], r2[0], r2[1]);
        noStroke(); fill(255); circle(l2[0], l2[1], 11);
        stroke(31, 94, 255); strokeWeight(2); noFill(); circle(l2[0], l2[1], 11);
        noStroke(); fill(255); circle(r1[0], r1[1], 11);
        stroke(31, 94, 255); strokeWeight(2); noFill(); circle(r1[0], r1[1], 11);
        noStroke(); textSize(13); fill(31, 94, 255);
        text('LHL = -1', map2(box, -1.5, -1)[0], map2(box, -1.5, -1)[1] - 8);
        fill(180, 90, 31);
        text('RHL = +1', map2(box, 0.75, 1)[0], map2(box, 0.75, 1)[1] - 8);
        note('-1 is not +1, so the two-sided limit does not exist.', 30, h - 24);
      }
    },
    {
      duration: 3000,
      caption: 'When the one-sided limits do agree, the limit exists - and if it also equals the value, the function is continuous. For h(x) = 2x + 1 below 3 and 3x - 2 from 3 up, both sides give 7 and h(3) = 7, so h is continuous at 3.',
      draw: function (p, w, h) {
        ink();
        head('Agreement gives continuity', 30, 34);
        var box = { x: 60, y: 66, w: w - 120, h: h - 130, xmin: 1, xmax: 5, ymin: 2, ymax: 14 };
        axes(box);
        plot(box, function (x) { return 2 * x + 1; }, 1, 3, [31, 94, 255]);
        plot(box, function (x) { return 3 * x - 2; }, 3, 5, [180, 90, 31]);
        var pt = map2(box, 3, 7);
        noStroke(); fill(20, 107, 74); circle(pt[0], pt[1], 9);
        textSize(12.5); fill(20, 107, 74);
        text('(3, 7)', pt[0] + 8, pt[1] - 8);
        note('LHL = 7, RHL = 7, h(3) = 7: continuous at the join.', 30, h - 24);
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

function rowCard(x, y, title, sub, third) {
  noStroke(); fill(232, 238, 255);
  rect(x, y, Math.min(width - 2 * x, 460), 56, 8);
  fill(31, 94, 255); textSize(14); textStyle(BOLD); text(title, x + 12, y + 22);
  textStyle(NORMAL); fill(70, 80, 98); textSize(12);
  text(sub, x + 12, y + 40);
  fill(120, 128, 140); textSize(11.5); text(third, x + 150, y + 40);
}

function table(x, y, w, rows) {
  var cw = w / rows[0].length, rh = 40;
  for (var r = 0; r < rows.length; r++) {
    for (var c = 0; c < rows[r].length; c++) {
      stroke(224, 228, 236); strokeWeight(1);
      fill(r === 0 ? color(243, 246, 251) : color(255));
      rect(x + c * cw, y + r * rh, cw - 4, rh - 4, 4);
      noStroke(); fill(30, 38, 50); textSize(13);
      textAlign('center', 'center');
      text(rows[r][c], x + c * cw + (cw - 4) / 2, y + r * rh + (rh - 4) / 2);
      textAlign('left', 'baseline');
    }
  }
}

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

function plot(box, f, from, to, col) {
  stroke(col[0], col[1], col[2]); strokeWeight(2.5); noFill();
  var prev = null, n = 220;
  for (var i = 0; i <= n; i++) {
    var x = from + (to - from) * i / n;
    var y = f(x);
    if (y < box.ymin - 2 || y > box.ymax + 2) { prev = null; continue; }
    var pt = map2(box, x, y);
    if (prev) { line(prev[0], prev[1], pt[0], pt[1]); }
    prev = pt;
  }
  noStroke();
}
