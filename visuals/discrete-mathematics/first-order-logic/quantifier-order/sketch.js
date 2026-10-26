/* Quantifier order: for all x there exists y versus there exists y for all x.
   Verified on the domain {1, 2, 3}: with R = {(1,2), (2,3), (3,1)} every element has a partner,
   so for all x there exists y R(x, y) holds, while no column is full, so there exists y for all x
   R(x, y) fails. With R = {(1,2), (2,2), (3,2)} one column is full and both hold.
   Recomputed in scripts/validate.py (check_first_order). */
window.LESSON = {
  steps: [
    {
      duration: 2200,
      caption: 'Two claims that look alike. For all x there exists y R(x, y) lets the y depend on x. There exists y for all x R(x, y) needs one fixed y that works for every x.',
      draw: function (p, w, h) {
        ink(); head('Two different claims', 34, 34);
        claimCard(46, 62, 'for all x there exists y  R(x, y)', 'each x may pick its own y', p);
        claimCard(46, 146, 'there exists y for all x  R(x, y)', 'one y must serve every x', p);
        note('Domain {1, 2, 3}. A tick at row x, column y means R(x, y) is true.', 46, h - 26);
      }
    },
    {
      duration: 2600,
      caption: 'Here R is {(1,2), (2,3), (3,1)}. Every row has a tick, so for all x there exists y R(x, y) is true: row 1 picks y = 2, row 2 picks y = 3, row 3 picks y = 1.',
      draw: function (p, w, h) {
        ink(); head('for all x there exists y  -  TRUE', 34, 34);
        grid(64, 60, p, CYCLE, 'row', true);
        note('one tick in every row: each x finds a partner of its own', 64, h - 26);
      }
    },
    {
      duration: 2600,
      caption: 'The same table read the other way asks for a whole column of ticks. No column has three, so there exists y for all x R(x, y) is false: no single y is related to all three elements.',
      draw: function (p, w, h) {
        ink(); head('there exists y for all x  -  FALSE', 34, 34);
        grid(64, 60, p, CYCLE, 'column', true);
        note('no full column: the order of the quantifiers changed the meaning', 64, h - 26);
      }
    },
    {
      duration: 2600,
      caption: 'Change the relation so column 2 is full. Now one fixed y = 2 works for every x, so there exists y for all x is true - and the rows are full too, so the other claim also holds.',
      draw: function (p, w, h) {
        ink(); head('a full column makes both true', 34, 34);
        grid(64, 60, p, COLUMN, 'column', true);
        note('there exists y for all x implies for all x there exists y, never the reverse', 64, h - 26);
      }
    }
  ]
};

var CYCLE = [[0, 1, 0], [0, 0, 1], [1, 0, 0]];
var COLUMN = [[0, 1, 0], [0, 1, 0], [0, 1, 0]];

function ink() {
  var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  background(dark ? color(23, 28, 36) : color(255));
  noStroke(); fill(dark ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}
function head(t, x, y) { textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function note(t, x, y) { textSize(13); fill(90, 100, 116); noStroke(); text(t, x, y); }

function claimCard(x, y, title, sub, prog) {
  var grow = Math.min(1, Math.max(0, prog * 3));
  noStroke(); fill(232, 238, 255);
  rect(x, y, Math.min(width - 2 * x, 420) * grow + 8, 68, 8);
  fill(31, 94, 255); textSize(14); textStyle(BOLD);
  text(title, x + 12, y + 27);
  textStyle(NORMAL); fill(70, 80, 98); textSize(12.5);
  text(sub, x + 12, y + 50);
}

/* A 3x3 truth grid for R(x, y): row = x, column = y. */
function grid(x0, y0, prog, table, mode, showLabels) {
  var cell = 62, pad = 26;
  textSize(13);
  var r, c;
  if (showLabels) {
    fill(70, 80, 98); noStroke();
    for (c = 0; c < 3; c++) { text('y=' + (c + 1), x0 + pad + c * cell + 14, y0 - 8); }
    for (r = 0; r < 3; r++) { text('x=' + (r + 1), x0 + 2, y0 + pad + r * cell + 26); }
  }
  for (r = 0; r < 3; r++) {
    for (c = 0; c < 3; c++) {
      var appear = Math.min(1, Math.max(0, prog * 4 - (r + c) * 0.35));
      if (appear <= 0) { continue; }
      var on = table[r][c] === 1;
      stroke(224, 228, 236); strokeWeight(1);
      fill(on ? color(232, 242, 234) : color(255));
      rect(x0 + pad + c * cell, y0 + pad + r * cell, cell - 6, cell - 6, 6);
      if (on) {
        noStroke(); fill(22, 122, 76);
        textSize(20); textStyle(BOLD);
        text('\u2713', x0 + pad + c * cell + 20, y0 + pad + r * cell + 38);
        textStyle(NORMAL); textSize(13);
      }
    }
  }
  if (mode === 'row') {
    for (r = 0; r < 3; r++) {
      var rp = Math.min(1, Math.max(0, prog * 2.2 - 0.9));
      if (rp <= 0) { continue; }
      noStroke(); fill(31, 94, 255);
      rect(x0 + 4, y0 + pad + r * cell + (cell - 6) / 2 - 1, 14 * rp, 3, 2);
    }
  } else {
    for (c = 0; c < 3; c++) {
      var full = table[0][c] === 1 && table[1][c] === 1 && table[2][c] === 1;
      var cp = Math.min(1, Math.max(0, prog * 2.2 - 0.9));
      if (cp <= 0) { continue; }
      noStroke(); fill(full ? color(22, 122, 76) : color(200, 120, 60));
      rect(x0 + pad + c * cell + (cell - 6) / 2 - 1, y0 + 10, 3, (pad + 3 * cell - 10) * cp, 2);
    }
  }
}
