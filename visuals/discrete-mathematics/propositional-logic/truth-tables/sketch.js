/* Truth tables for implication: p -> q, its equivalent rewrite, and its converse.
   Verified: p -> q is false only at (p, q) = (true, false); q -> p differs from it in
   exactly two rows. Both claims are recomputed in scripts/validate.py. */
window.LESSON = {
  steps: [
    {
      duration: 2000,
      caption: 'Two variables, four interpretations. Every row of a truth table is one interpretation, so a formula in two variables always has exactly 4 rows.',
      draw: function (p, w, h) {
        ink(); head('Two variables, four rows', 34, 34);
        table(60, 70, p, ['p', 'q'], [['T', 'T'], ['T', 'F'], ['F', 'T'], ['F', 'F']], []);
        note('2^2 = 4 interpretations', 60, h - 30);
      }
    },
    {
      duration: 2200,
      caption: 'Fill in p -> q. It is true in three rows and false in exactly one: p true while q is false. That single row is the whole of implication.',
      draw: function (p, w, h) {
        ink(); head('p -> q: one false row', 34, 34);
        table(60, 70, p, ['p', 'q', 'p -> q'],
          [['T', 'T', 'T'], ['T', 'F', 'F'], ['F', 'T', 'T'], ['F', 'F', 'T']], [1]);
        note('false only when p is true and q is false', 60, h - 30);
      }
    },
    {
      duration: 2200,
      caption: 'Now not p or q. The column is identical to p -> q in all four rows, and that is exactly what logical equivalence means.',
      draw: function (p, w, h) {
        ink(); head('not p or q: the same column', 34, 34);
        table(50, 70, p, ['p', 'q', 'p -> q', 'not p or q'],
          [['T', 'T', 'T', 'T'], ['T', 'F', 'F', 'F'], ['F', 'T', 'T', 'T'], ['F', 'F', 'T', 'T']], []);
        note('identical columns = equivalent formulas', 50, h - 30);
      }
    },
    {
      duration: 2400,
      caption: 'The converse q -> p is a different column: it differs in the two rows where p and q disagree. So the converse is not equivalent to the original - the most common mistake in this topic.',
      draw: function (p, w, h) {
        ink(); head('q -> p: a different column', 34, 34);
        table(50, 70, p, ['p', 'q', 'p -> q', 'q -> p'],
          [['T', 'T', 'T', 'T'], ['T', 'F', 'F', 'T'], ['F', 'T', 'T', 'F'], ['F', 'F', 'T', 'T']], [1, 2]);
        note('two differing rows: the converse is not the statement', 50, h - 30);
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
function table(x, y, prog, headers, rows, badRows) {
  var cw = Math.min(120, (width - 2 * x) / headers.length), ch = 42;
  textSize(14);
  for (var c = 0; c < headers.length; c++) {
    noStroke(); fill(60, 70, 88);
    text(headers[c], x + c * cw + 12, y - 10);
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
      text(rows[r][c2], x + c2 * cw + 14, y + r * ch + 27);
    }
  }
  noFill(); stroke(200, 207, 217); strokeWeight(1);
  rect(x, y, cw * headers.length, ch * rows.length, 6);
}
