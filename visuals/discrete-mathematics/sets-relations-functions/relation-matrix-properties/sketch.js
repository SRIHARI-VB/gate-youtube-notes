/* Relation as a matrix: reflexive, symmetric, antisymmetric, transitive and equivalence, read off one 3x3 grid.
   Every number shown here is recomputed in scripts/validate.py (check_sets_relations_functions), which
   enumerates all 512 relations on a 3-element set and tallies each property. */
window.LESSON = {
  steps: [
    {
      duration: 2400,
      caption: 'A relation on {1, 2, 3} is a subset of the 3 by 3 grid of ordered pairs. A tick means the pair is in the relation. Nine cells, each in or out, so there are 2 to the 9 = 512 relations.',
      draw: function (p, w, h) {
        ink(); head('A relation is a set of ticks', 34, 34);
        grid(40, 66, p, SAMPLE, {});
        panel(360, 70, ['9 cells', 'each cell: in or out', '2^9 = 512 relations'], p);
        note('row = first coordinate, column = second coordinate', 40, h - 26);
      }
    },
    {
      duration: 2600,
      caption: 'Reflexive: every element must be related to itself, so all three diagonal cells are ticked. The six off-diagonal cells stay free, giving 2 to the 6 = 64 reflexive relations.',
      draw: function (p, w, h) {
        ink(); head('Reflexive - the diagonal is full', 34, 34);
        grid(40, 66, p, DIAG, { diag: true });
        panel(360, 70, ['diagonal forced on', '6 free cells', '2^6 = 64 reflexive'], p);
        note('irreflexive is the mirror case: the diagonal is empty, also 2^6 = 64', 40, h - 26);
      }
    },
    {
      duration: 2800,
      caption: 'Symmetric: whenever (a, b) is ticked, (b, a) must be ticked too. Each of the three mirror pairs is all-or-nothing, and the three diagonal cells are free, so 2 to the 6 = 64 symmetric relations.',
      draw: function (p, w, h) {
        ink(); head('Symmetric - mirror pairs agree', 34, 34);
        grid(40, 66, p, MIRROR, { pairs: true });
        panel(360, 70, ['3 mirror pairs, all or nothing', '3 free diagonal cells', '2^6 = 64 symmetric'], p);
        note('a pair may be absent from both cells: symmetric does not mean every pair is related', 40, h - 26);
      }
    },
    {
      duration: 2800,
      caption: 'Antisymmetric: for two different elements you may tick (a, b) or (b, a) but never both. Each mirror pair has three states - neither, one way, the other way - and the diagonal is free: 2^3 times 3^3 = 216.',
      draw: function (p, w, h) {
        ink(); head('Antisymmetric - never both ways', 34, 34);
        grid(40, 66, p, ANTISYM, { pairs: true, forbid: true });
        panel(360, 70, ['each pair: 3 states', 'diagonal free: 2^3', '2^3 x 3^3 = 216'], p);
        note('antisymmetric is not the opposite of symmetric: the identity relation is both', 40, h - 26);
      }
    },
    {
      duration: 3000,
      caption: 'Transitive: if (1,2) and (2,3) are ticked then (1,3) must be ticked. Here it is missing, so the relation is not transitive. Adding it gives the transitive closure of this relation.',
      draw: function (p, w, h) {
        ink(); head('Transitive - the missing shortcut', 34, 34);
        grid(40, 66, p, CHAIN, { chain: true, progress: p });
        panel(360, 70, ['(1,2) and (2,3) ticked', '(1,3) missing: not transitive', 'closure adds (1,3)'], p);
        note('one missing shortcut is enough to refute transitivity', 40, h - 26);
      }
    },
    {
      duration: 3000,
      caption: 'Reflexive, symmetric and transitive together give an equivalence relation. The ticks then sit in square blocks on the diagonal, and each block is an equivalence class: here {1, 2} and {3}. A 3-element set has 5 equivalence relations, a 4-element set has 15.',
      draw: function (p, w, h) {
        ink(); head('Equivalence - blocks on the diagonal', 34, 34);
        grid(40, 66, p, EQUIV, { blocks: true });
        panel(360, 70, ['classes {1, 2} and {3}', 'blocks never overlap', 'B(3) = 5, B(4) = 15'], p);
        note('an equivalence relation and a partition are the same object, seen twice', 40, h - 26);
      }
    }
  ]
};

var SAMPLE = [[1, 1, 0], [0, 0, 1], [0, 0, 0]];
var DIAG = [[1, 0, 0], [0, 1, 1], [0, 0, 1]];
var MIRROR = [[0, 1, 0], [1, 0, 1], [0, 1, 0]];
var ANTISYM = [[1, 1, 0], [0, 0, 1], [0, 0, 0]];
var CHAIN = [[0, 1, 0], [0, 0, 1], [0, 0, 0]];
var EQUIV = [[1, 1, 0], [1, 1, 0], [0, 0, 1]];

function ink() {
  var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  background(dark ? color(23, 28, 36) : color(255));
  noStroke(); fill(dark ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}
function head(t, x, y) { textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function note(t, x, y) { textSize(12.5); fill(90, 100, 116); noStroke(); text(t, x, y); }

function panel(x, y, lines, prog) {
  var grow = Math.min(1, Math.max(0, prog * 3));
  noStroke(); fill(232, 238, 255);
  rect(x, y, Math.min(width - x - 20, 380), 24 + lines.length * 22, 8);
  fill(31, 94, 255); textSize(13); textStyle(BOLD);
  if (grow > 0) { text('what the grid shows', x + 12, y + 22); }
  textStyle(NORMAL); fill(70, 80, 98); textSize(12.5);
  for (var i = 0; i < lines.length; i++) {
    if (Math.min(1, Math.max(0, prog * 3 - 0.25 * (i + 1))) <= 0) { continue; }
    text(lines[i], x + 12, y + 44 + i * 22);
  }
}

/* Draw the 3x3 grid of pairs for the relation `table`. Row = first coordinate, column = second. */
function grid(x0, y0, prog, table, opts) {
  var cell = 74, pad = 30;
  textSize(12.5);
  fill(70, 80, 98); noStroke();
  var c, r;
  for (c = 0; c < 3; c++) { text('b=' + (c + 1), x0 + pad + c * cell + 20, y0 - 8); }
  for (r = 0; r < 3; r++) { text('a=' + (r + 1), x0 + 2, y0 + pad + r * cell + 34); }

  for (r = 0; r < 3; r++) {
    for (c = 0; c < 3; c++) {
      var appear = Math.min(1, Math.max(0, prog * 4 - (r + c) * 0.3));
      if (appear <= 0) { continue; }
      var on = table[r][c] === 1;
      var extra = false;
      if (opts.chain && r === 0 && c === 2) { extra = prog > 0.55; }
      stroke(224, 228, 236); strokeWeight(1);
      fill(on ? color(232, 242, 234) : (extra ? color(255, 244, 226) : color(255)));
      rect(x0 + pad + c * cell, y0 + pad + r * cell, cell - 8, cell - 8, 6);
      if (on || extra) {
        noStroke(); fill(on ? color(22, 122, 76) : color(200, 120, 60));
        textSize(20); textStyle(BOLD);
        text('\u2713', x0 + pad + c * cell + 24, y0 + pad + r * cell + 44);
        textStyle(NORMAL); textSize(12.5);
      }
      if (extra && on === false) {
        noStroke(); fill(200, 120, 60); textSize(11);
        text('added', x0 + pad + c * cell + 12, y0 + pad + r * cell + 62);
      }
    }
  }

  if (opts.diag) {
    for (var d = 0; d < 3; d++) {
      var dp = Math.min(1, Math.max(0, prog * 2 - 0.4));
      if (dp <= 0) { continue; }
      noStroke(); fill(31, 94, 255);
      rect(x0 + pad + d * cell + (cell - 8) / 2 - 2, y0 + pad + d * cell + (cell - 8) / 2 - 2,
           2, 0);
      circle(x0 + pad + d * cell + (cell - 8) / 2, y0 + pad + d * cell + (cell - 8) / 2, 8 * dp);
    }
  }
  if (opts.pairs) {
    var pairList = [[0, 1], [0, 2], [1, 2]];
    for (var i = 0; i < pairList.length; i++) {
      var a = pairList[i][0], b = pairList[i][1];
      var pp = Math.min(1, Math.max(0, prog * 2 - 0.3 - i * 0.15));
      if (pp <= 0) { continue; }
      var x1 = x0 + pad + b * cell + (cell - 8) / 2, y1 = y0 + pad + a * cell + (cell - 8) / 2;
      var x2 = x0 + pad + a * cell + (cell - 8) / 2, y2 = y0 + pad + b * cell + (cell - 8) / 2;
      stroke(opts.forbid ? color(200, 120, 60) : color(31, 94, 255)); strokeWeight(1.6);
      line(x1, y1, x2, y2);
      noStroke();
    }
  }
  if (opts.blocks) {
    var bp = Math.min(1, Math.max(0, prog * 2 - 0.5));
    if (bp > 0) {
      noFill(); stroke(31, 94, 255); strokeWeight(2);
      rect(x0 + pad - 4, y0 + pad - 4, 2 * cell, 2 * cell, 8);
      rect(x0 + pad + 2 * cell - 4, y0 + pad + 2 * cell - 4, cell, cell, 8);
      noStroke();
    }
  }
}
