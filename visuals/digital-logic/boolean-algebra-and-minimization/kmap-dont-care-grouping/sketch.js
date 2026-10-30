/* Don't-care grouping on a four-variable Karnaugh map, for the Boolean Algebra and
   Minimization topic.

   The function is GATE CSE 2014 Set 3 Q.7's:

     F(P,Q,R,S) = sum(0, 2, 5, 7, 8, 10, 13, 15), with 2, 7, 8 and 13 as don't cares

   so the required 1s are 0, 5, 10 and 15 - four cells, none adjacent to another.
   With the don't cares available, {0,2,8,10} becomes a quad (Q'S') and {5,7,13,15}
   becomes a quad (QS), and the minimal SOP is Q'S' + QS with four literals.

   The cell numbering, the two quads and both literal counts are recomputed in
   scripts/validate.py (check_boolean_algebra), not copied from here.

   The order of the steps is the lesson: number the map, place the 1s, place the Xs,
   let an X join each quad, read the constant variables, then compare with the cost
   of ignoring the don't cares. */

window.LESSON = {
  steps: [
    {
      duration: 4200,
      caption: 'A four-variable map has sixteen cells and the labels are in Gray code: rows PQ run 00, 01, 11, 10 and columns RS run 00, 01, 11, 10. Read the number inside each cell from those labels, never from the position: the third cell of the first row is minterm 3, and minterm 2 sits to its right.',
      draw: function (p, w, h) {
        inkMap();
        headMap('Step 1: number the cells from the labels', 24, 30);
        mapGrid(w, h, { numbers: 1, values: false });
        panelMap(w, h, [
          'rows PQ: 00 01 11 10',
          'cols RS: 00 01 11 10',
          '',
          'm0  = P0 Q0 R0 S0',
          'm15 = P1 Q1 R1 S1'
        ]);
        noteMap('Two variables change between 00 and 11 only when the order is wrong.', 24, h - 16);
      }
    },
    {
      duration: 4200,
      caption: 'Now place the required 1s: minterms 0, 5, 10 and 15. Look at where they land - m0 is a corner, m5 and m10 are in the middle, m15 is the opposite corner. No two of them share an edge, so without help each 1 is a group of one cell and the expression is the canonical form.',
      draw: function (p, w, h) {
        inkMap();
        headMap('Step 2: the four required 1s', 24, 30);
        mapGrid(w, h, { numbers: 1, values: true, ones: Math.min(1, p * 1.4) });
        panelMap(w, h, [
          'F = 1 at m0, m5, m10, m15',
          '',
          'm0  = 0000',
          'm5  = 0101',
          'm10 = 1010',
          'm15 = 1111'
        ]);
        noteMap('None of the four is adjacent to another: every group would be one cell.', 24, h - 16);
      }
    },
    {
      duration: 4000,
      caption: 'The question gives four don\'t cares as well: minterms 2, 7, 8 and 13, marked X. An X is a row whose output does not matter, so it may be treated as a 1 when that enlarges a group. It is not a 1 that has to be covered - it is an offer, not an obligation.',
      draw: function (p, w, h) {
        inkMap();
        headMap('Step 3: the don\'t cares are offers, not obligations', 24, 30);
        mapGrid(w, h, { numbers: 1, values: true, ones: 1, cares: Math.min(1, p * 1.4) });
        panelMap(w, h, [
          'X at m2, m7, m8, m13',
          '',
          'X = 0 or 1, choose per group',
          '',
          'an X never has to be covered'
        ]);
        noteMap('Mark the Xs before grouping, so that no group is drawn through a 0.', 24, h - 16);
      }
    },
    {
      duration: 4600,
      caption: 'First quad: the four corners, m0, m2, m8 and m10. The corners are adjacent in a Karnaugh map because the map wraps around - the left edge touches the right and the top touches the bottom. Two of the four cells are don\'t cares, and they are exactly what makes this group of four possible.',
      draw: function (p, w, h) {
        inkMap();
        headMap('Step 4: the corners form one quad', 24, 30);
        mapGrid(w, h, { numbers: 1, values: true, ones: 1, cares: 1, groupA: Math.min(1, p * 1.5) });
        panelMap(w, h, [
          'group: m0, m2, m8, m10',
          '',
          'm2 and m8 are X',
          'corners are adjacent',
          '',
          '4 cells -> 2 literals'
        ]);
        noteMap('Wrap-around is not a trick: the two cells differ in one bit, so they are adjacent.', 24, h - 16);
      }
    },
    {
      duration: 4600,
      caption: 'Second quad: m5, m7, m13 and m15. These four sit in the block formed by rows PQ = 01 and 11 and columns RS = 01 and 11, and again two of the cells - m7 and m13 - are don\'t cares. Every required 1 is now inside a group of four.',
      draw: function (p, w, h) {
        inkMap();
        headMap('Step 5: the second quad, and both 1s covered', 24, 30);
        mapGrid(w, h, { numbers: 1, values: true, ones: 1, cares: 1, groupA: 1, groupB: Math.min(1, p * 1.5) });
        panelMap(w, h, [
          'group: m5, m7, m13, m15',
          '',
          'm7 and m13 are X',
          '',
          'm5 and m15 are covered',
          '4 cells -> 2 literals'
        ]);
        noteMap('The X at m7 and the X at m13 are used here and nowhere else.', 24, h - 16);
      }
    },
    {
      duration: 4800,
      caption: 'Read each group by keeping the variables that never change inside it. In the corner quad P and R take both values while Q = 0 and S = 0 throughout, so the term is Q\'S\'. In the second quad P and R again vary while Q = 1 and S = 1, so the term is QS.',
      draw: function (p, w, h) {
        inkMap();
        headMap('Step 6: keep the constants, drop the rest', 24, 30);
        mapGrid(w, h, { numbers: 1, values: true, ones: 1, cares: 1, groupA: 1, groupB: 1 });
        panelMap(w, h, [
          'corners: Q=0, S=0 -> Q\'S\'',
          'block:   Q=1, S=1 -> QS',
          '',
          'P and R change in both',
          'so both are dropped'
        ]);
        noteMap('A variable that takes both values inside a group cannot appear in the term.', 24, h - 16);
      }
    },
    {
      duration: 4800,
      caption: 'The minimal sum of products is Q\'S\' + QS, which is Q XNOR S - four literals. Ignore the don\'t cares and the same function needs four 4-literal minterms, sixteen literals. That difference is the whole value of a don\'t care, and it is why an X must never be counted as a required 1.',
      draw: function (p, w, h) {
        inkMap();
        headMap('Step 7: four literals against sixteen', 24, 30);
        mapGrid(w, h, { numbers: 0, values: true, ones: 1, cares: 1, groupA: 1, groupB: 1 });
        panelMap(w, h, [
          'F = Q\'S\' + QS',
          '  = Q XNOR S',
          '',
          '4 literals, 2 terms',
          'canonical: 4 terms x 4',
          '= 16 literals'
        ]);
        noteMap('The Xs were included in the groups and excluded from the required 1s.', 24, h - 16);
      }
    }
  ]
};

/* ---------------------------------------------------------------- helpers */
function inkMap() {
  var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  background(dark ? color(23, 28, 36) : color(255));
  noStroke();
  fill(dark ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}
function headMap(t, x, y) { textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function noteMap(t, x, y) { textSize(12.5); fill(90, 100, 116); noStroke(); text(t, x, y); }

var ROWS = ['00', '01', '11', '10'];
var COLS = ['00', '01', '11', '10'];
var CELLS = [[0, 1, 3, 2], [4, 5, 7, 6], [12, 13, 15, 14], [8, 9, 11, 10]];
var ONES = [0, 5, 10, 15];
var CARES = [2, 7, 8, 13];
var QUAD_A = [0, 2, 8, 10];
var QUAD_B = [5, 7, 13, 15];

function geom(w, h) {
  var cell = Math.max(26, Math.min(46, (w - 150) / 4.6, (h - 120) / 4.6));
  return { cell: cell, x0: 62, y0: 62 };
}

function cellBox(w, h, r, c) {
  var g = geom(w, h);
  return { x: g.x0 + c * g.cell, y: g.y0 + r * g.cell, s: g.cell };
}

function indexOfCell(m) {
  for (var r = 0; r < 4; r++) {
    for (var c = 0; c < 4; c++) {
      if (CELLS[r][c] === m) { return { r: r, c: c }; }
    }
  }
  return null;
}

function mapGrid(w, h, opt) {
  var g = geom(w, h);
  var showNumbers = opt.numbers === undefined ? 1 : opt.numbers;
  var i, j;

  /* axis labels */
  noStroke(); fill(90, 100, 116); textSize(11.5);
  textAlign(CENTER, CENTER);
  for (j = 0; j < 4; j++) {
    var bx = g.x0 + j * g.cell;
    text(COLS[j], bx + g.cell / 2, g.y0 - 14);
  }
  for (i = 0; i < 4; i++) {
    var by = g.y0 + i * g.cell;
    text(ROWS[i], g.x0 - 18, by + g.cell / 2);
  }
  textAlign('left', 'baseline');
  fill(31, 94, 255); textSize(11.5);
  text('RS', g.x0 + 2 * g.cell - 6, g.y0 - 30);
  text('PQ', g.x0 - 34, g.y0 + 2 * g.cell + 2);

  /* cells */
  for (i = 0; i < 4; i++) {
    for (j = 0; j < 4; j++) {
      var b = cellBox(w, h, i, j);
      var m = CELLS[i][j];
      var isOne = ONES.indexOf(m) >= 0;
      var isCare = CARES.indexOf(m) >= 0;

      noStroke();
      fill(247, 248, 251);
      stroke(206, 212, 222); strokeWeight(1);
      rect(b.x, b.y, b.s - 2, b.s - 2, 4);

      /* the value */
      if (opt.values) {
        var shown = 0;
        if (isOne) { shown = opt.ones === undefined ? 1 : opt.ones; }
        else if (isCare) { shown = opt.cares === undefined ? 1 : opt.cares; }
        if (isOne && shown > 0) {
          noStroke(); fill(20, 24, 31);
          textSize(Math.max(13, b.s * 0.42)); textAlign(CENTER, CENTER);
          text('1', b.x + (b.s - 2) / 2, b.y + (b.s - 2) / 2 - (showNumbers ? 5 : 0));
          textAlign('left', 'baseline');
        } else if (isCare && shown > 0) {
          noStroke(); fill(200, 120, 20);
          textSize(Math.max(13, b.s * 0.42)); textAlign(CENTER, CENTER);
          text('X', b.x + (b.s - 2) / 2, b.y + (b.s - 2) / 2 - (showNumbers ? 5 : 0));
          textAlign('left', 'baseline');
        }
      }

      /* the minterm number */
      if (showNumbers > 0) {
        noStroke(); fill(150, 160, 176); textSize(Math.max(8, b.s * 0.24));
        text(String(m), b.x + 4, b.y + 12);
      }
    }
  }

  /* groups */
  if (opt.groupA) { quadRing(w, h, QUAD_A, opt.groupA, 31, 94, 255); }
  if (opt.groupB) { quadRing(w, h, QUAD_B, opt.groupB, 22, 140, 90); }
}

/* A rounded ring around a set of four cells, drawn so that wrap-around groups
   still look like one group: each cell gets a thick inset border. */
function quadRing(w, h, cells, t, r, gch, b) {
  noFill();
  for (var k = 0; k < cells.length; k++) {
    var pos = indexOfCell(cells[k]);
    if (!pos) { continue; }
    var box = cellBox(w, h, pos.r, pos.c);
    var inset = 3 + (1 - t) * 10;
    stroke(r, gch, b, 230 * t);
    strokeWeight(3);
    rect(box.x + inset, box.y + inset, box.s - 2 - 2 * inset, box.s - 2 - 2 * inset, 5);
  }
  noStroke();
}

function panelMap(w, h, lines) {
  var x = Math.max(w * 0.56, 300);
  var y = 66;
  noStroke();
  for (var i = 0; i < lines.length; i++) {
    fill(i === 0 ? color(20, 24, 31) : color(70, 80, 96));
    textSize(i === 0 ? 13 : 12);
    text(lines[i], x, y + i * 18);
  }
}
