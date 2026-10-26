/* Implication, converse, inverse and contrapositive.
   Verified: p -> q and not q -> not p have identical columns; q -> p and not p -> not q
   each differ from p -> q in exactly two rows. Recomputed in scripts/validate.py. */
window.LESSON = {
  steps: [
    {
      duration: 2000,
      caption: 'The statement is "if it is raining then the ground is wet", written p -> q. p is the antecedent (the condition), q the consequent.',
      draw: function (p, w, h) {
        ink(); head('The statement: p -> q', 34, 34);
        bubble(70, 60, 'p: it is raining', p);
        bubble(120, 60, 'q: the ground is wet', p);
        note('p -> q reads: whenever p holds, q holds', 60, h - 30);
      }
    },
    {
      duration: 2200,
      caption: 'The contrapositive flips and negates both parts: not q -> not p, "if the ground is not wet then it is not raining". Its column is identical, so it says exactly the same thing.',
      draw: function (p, w, h) {
        ink(); head('Contrapositive: identical column', 34, 34);
        table(50, 70, p, ['p', 'q', 'p -> q', 'not q -> not p'],
          [['T', 'T', 'T', 'T'], ['T', 'F', 'F', 'F'], ['F', 'T', 'T', 'T'], ['F', 'F', 'T', 'T']], []);
        note('same four values: equivalent statements', 50, h - 30);
      }
    },
    {
      duration: 2400,
      caption: 'The converse swaps without negating: q -> p, "if the ground is wet then it is raining". Two rows now disagree, so the converse is a different claim - a wet ground can have other causes.',
      draw: function (p, w, h) {
        ink(); head('Converse: two rows disagree', 34, 34);
        table(50, 70, p, ['p', 'q', 'p -> q', 'q -> p'],
          [['T', 'T', 'T', 'T'], ['T', 'F', 'F', 'T'], ['F', 'T', 'T', 'F'], ['F', 'F', 'T', 'T']], [1, 2]);
        note('converse and inverse match each other, never the original', 50, h - 30);
      }
    },
    {
      duration: 2200,
      caption: 'The inverse not p -> not q fails in the same two rows as the converse, because each is the contrapositive of the other. Only the contrapositive survives swap-and-negate unchanged.',
      draw: function (p, w, h) {
        ink(); head('Inverse: same failures as the converse', 34, 34);
        table(50, 70, p, ['p', 'q', 'p -> q', 'not p -> not q'],
          [['T', 'T', 'T', 'T'], ['T', 'F', 'F', 'T'], ['F', 'T', 'T', 'F'], ['F', 'F', 'T', 'T']], [1, 2]);
        note('only the contrapositive is equivalent to the original', 50, h - 30);
      }
    }
  ]
};

function ink() {
  var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  background(dark ? color(23, 28, 36) : color(255));
  noStroke(); fill(dark ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}
function head(t, x, y) { textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function note(t, x, y) { textSize(13); fill(90, 100, 116); noStroke(); text(t, x, y); }
function bubble(y, x, t, prog) {
  noStroke(); fill(232, 238, 255);
  rect(x, y, Math.min(width - 2 * x, 320), 34, 8);
  fill(31, 94, 255); textSize(14);
  text(t, x + 12, y + 22);
}
function table(x, y, prog, headers, rows, badRows) {
  var cw = Math.min(120, (width - 2 * x) / headers.length), ch = 42;
  textSize(14);
  for (var c = 0; c < headers.length; c++) {
    noStroke(); fill(60, 70, 88);
    text(headers[c], x + c * cw + 10, y - 10);
  }
  for (var r = 0; r < rows.length; r++) {
    var appear = Math.min(1, Math.max(0, prog * 5 - r * 0.7));
    if (appear <= 0) { continue; }
    for (var c2 = 0; c2 < rows[r].length; c2++) {
      var bad = badRows.indexOf(r) >= 0 && c2 >= 2;
      noStroke(); fill(bad ? color(253, 240, 234) : color(255));
      stroke(226, 230, 236); strokeWeight(1);
      rect(x + c2 * cw, y + r * ch, cw, ch, 4);
      noStroke(); fill(bad ? color(180, 69, 31) : color(30, 36, 48));
      text(rows[r][c2], x + c2 * cw + 12, y + r * ch + 27);
    }
  }
  noFill(); stroke(200, 207, 217); strokeWeight(1);
  rect(x, y, cw * headers.length, ch * rows.length, 6);
}
