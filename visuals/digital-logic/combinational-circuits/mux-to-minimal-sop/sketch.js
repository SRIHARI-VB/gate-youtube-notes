/* From a 4-to-1 multiplexer to a minimal sum of products.

   The circuit is GATE CSE 2014 Set 1 Q.45: select lines S1 = P and S0 = Q, data
   inputs I0 = 0, I1 = 1, I2 = R, I3 = R'.

     F = P'Q'I0 + P'Q I1 + PQ'I2 + PQ I3
       = 0 + P'Q + PQ'R + PQR'

   whose minterms over (P, Q, R) are 2, 3, 5 and 6, and whose minimal form is
   P'Q + QR' + PQ'R - three terms, seven literals, against four terms and twelve
   literals in canonical form.

   Every number shown here is recomputed in scripts/validate.py
   (check_combinational_circuits), not copied from this file.

   The order of the steps is the lesson: read the select codes, substitute the data
   inputs, expand to minterms, place them on the map, group them, then read the term
   off each group and count the literals. */

/* p5 alignment constants. p5 defines these itself; the fallbacks keep the lesson drawing
   where p5 is stubbed (the headless sketch test), and they carry p5's own values. */
if (typeof LEFT === 'undefined') { var LEFT = 'left'; }
if (typeof RIGHT === 'undefined') { var RIGHT = 'right'; }
if (typeof TOP === 'undefined') { var TOP = 'top'; }
if (typeof BOTTOM === 'undefined') { var BOTTOM = 'bottom'; }

window.LESSON = {
  steps: [
    {
      duration: 4200,
      caption: 'A 4-to-1 multiplexer has four data inputs, one output and two select lines. Here S1 is P and S0 is Q. The select code decides which of the four data inputs reaches the output, and the other three are ignored.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 1: one output, four data inputs, two select lines');
        muxBlock(p, w, h, { select: -1 });
        panel(w, h, [
          'S1 = P, S0 = Q',
          '',
          '2 select lines',
          '-> 2^2 = 4 data inputs',
          '',
          'the select code picks',
          'exactly one of them'
        ]);
        note(w, h, 'The multiplexer is a data selector: four wires in, one wire out.');
      }
    },
    {
      duration: 4600,
      caption: 'Write the output equation and read it as a table. Each select code owns one data input: 00 owns I0, 01 owns I1, 10 owns I2 and 11 owns I3. Only the term whose select code is true can be 1, so the four terms never compete.',
      draw: function (p, w, h) {
        var lit = Math.min(3, Math.floor(p * 4.2));
        frame(w, h, 'Step 2: the select code of each data input');
        muxBlock(p, w, h, { select: lit, code: true });
        panel(w, h, [
          'Y = S1\'S0\' I0',
          '  + S1\'S0  I1',
          '  + S1 S0\' I2',
          '  + S1 S0  I3',
          '',
          '00 -> I0   01 -> I1',
          '10 -> I2   11 -> I3'
        ]);
        note(w, h, 'S1 is the more significant select bit: it chooses the upper or lower half.');
      }
    },
    {
      duration: 4600,
      caption: 'Now substitute the data inputs this question gives: I0 = 0, I1 = 1, I2 = R and I3 = not R. The first term dies because 0 times anything is 0. The other three survive, and two of them carry the third variable R.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 3: substitute the data inputs');
        muxBlock(p, w, h, { select: -1, values: true, fade: p });
        panel(w, h, [
          'I0 = 0    I1 = 1',
          'I2 = R    I3 = R\'',
          '',
          'F = P\'Q\' . 0',
          '  + P\'Q  . 1',
          '  + PQ\' . R',
          '  + PQ  . R\''
        ]);
        note(w, h, 'The data inputs are not all constants: two of them are the variable R.');
      }
    },
    {
      duration: 4800,
      caption: 'Expand what is left. P-prime Q is two minterms, because R can be 0 or 1: that is minterm 2 and minterm 3. P Q-prime R is minterm 5 and P Q R-prime is minterm 6. So the function is 1 at exactly four of the eight rows: 2, 3, 5 and 6.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 4: four minterms out of eight rows');
        mintermTable(p, w, h);
        panel(w, h, [
          'P\'Q  -> m2, m3',
          'PQ\'R -> m5',
          'PQR\' -> m6',
          '',
          'F = sum(2, 3, 5, 6)',
          '',
          'canonical: 4 terms',
          '12 literals'
        ]);
        note(w, h, 'Minterm index = 4P + 2Q + R, with P the most significant bit.');
      }
    },
    {
      duration: 4600,
      caption: 'Place those four 1s on a three-variable Karnaugh map. The columns are Q R in Gray order 00, 01, 11, 10 and the rows are P. Number each cell from its labels, never from its position: the third cell of the top row is minterm 3 and minterm 2 sits to its right.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 5: place the 1s on the map');
        kmap(p, w, h, { ones: Math.min(1, p * 1.5) });
        panel(w, h, [
          'columns QR: 00 01 11 10',
          'rows P: 0 then 1',
          '',
          '1s at m2, m3, m5, m6',
          '',
          'm3 is top row, third cell',
          'm2 is top row, fourth cell'
        ]);
        note(w, h, 'Gray order makes neighbours differ in one bit, which is what grouping needs.');
      }
    },
    {
      duration: 5000,
      caption: 'Group them, largest groups first. Minterms 2 and 3 are neighbours and give P-prime Q. Minterms 2 and 6 are neighbours vertically and give Q R-prime. Minterm 5 has no neighbour left, so it stays a group of one: P Q-prime R. Every 1 is covered.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 6: two pairs and one single');
        kmap(p, w, h, {
          ones: 1,
          groupA: Math.min(1, p * 2),
          groupB: Math.min(1, Math.max(0, p * 2 - 0.6)),
          groupC: Math.min(1, Math.max(0, p * 2 - 1.2))
        });
        panel(w, h, [
          'm2 + m3 -> P\'Q',
          'm2 + m6 -> QR\'',
          'm5 alone -> PQ\'R',
          '',
          '4 cells -> 2 literals',
          '2 cells -> 1 literal',
          '',
          'all four 1s covered'
        ]);
        note(w, h, 'Group size doubles the saving: a pair drops one variable, a quad drops two.');
      }
    },
    {
      duration: 5200,
      caption: 'Read the answer off the groups: P-prime Q plus Q R-prime plus P Q-prime R. That is three terms and seven literals, against four terms and twelve literals for the canonical form. Option (A) of the paper, and the reason the map is worth drawing even when the equation looks short.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 7: the minimal sum of products');
        kmap(p, w, h, { ones: 1, groupA: 1, groupB: 1, groupC: 1, answer: Math.min(1, p * 1.6) });
        panel(w, h, [
          'F = P\'Q + QR\' + PQ\'R',
          '',
          '3 terms, 7 literals',
          '',
          'canonical form:',
          '4 terms, 12 literals',
          '',
          'option (A)'
        ]);
        note(w, h, 'The multiplexer gave the minterms; the map gave the minimum. Both are needed.');
      }
    }
  ]
};

/* ---------------------------------------------------------------- drawing helpers */

var INK = [38, 44, 54];
var SOFT = [106, 116, 132];
var LINE = [206, 212, 222];
var ONE = [40, 122, 92];
var SEL = [176, 98, 30];
var MUTED = [148, 156, 168];

function frame(w, h, title) {
  noStroke();
  fill(255, 255, 255);
  rect(0, 0, w, h);
  noStroke();
  fill(INK[0], INK[1], INK[2]);
  textSize(15);
  textStyle(BOLD);
  textAlign(LEFT, TOP);
  text(title, 24, 18);
  textStyle(NORMAL);
}

function note(w, h, s) {
  noStroke();
  fill(SOFT[0], SOFT[1], SOFT[2]);
  textSize(12.5);
  textAlign(LEFT, BOTTOM);
  text(s, 24, h - 12);
}

function muxBlock(p, w, h, opt) {
  var x = 70, y = 96, bw = 176, bh = 196;
  var names = ['I0', 'I1', 'I2', 'I3'];
  var vals = ['0', '1', 'R', "R'"];
  var codes = ['00', '01', '10', '11'];
  var i, iy;

  noStroke();
  fill(246, 248, 251);
  rect(x, y, bw, bh);

  stroke(LINE[0], LINE[1], LINE[2]);
  strokeWeight(1);
  noFill();
  rect(x, y, bw, bh);

  noStroke();
  fill(SOFT[0], SOFT[1], SOFT[2]);
  textSize(12);
  textAlign(CENTER, TOP);
  text('4-to-1 MUX', x + bw / 2, y + bh / 2 - 22);

  for (i = 0; i < 4; i++) {
    iy = y + 26 + i * 40;
    var active = (opt.select === i);
    stroke(active ? SEL[0] : LINE[0], active ? SEL[1] : LINE[1], active ? SEL[2] : LINE[2]);
    strokeWeight(active ? 2.6 : 1.2);
    line(x - 40, iy, x, iy);

    noStroke();
    fill(active ? SEL[0] : INK[0], active ? SEL[1] : INK[1], active ? SEL[2] : INK[2]);
    textSize(13);
    textAlign(RIGHT, CENTER);
    text(names[i], x - 46, iy);

    if (opt.code) {
      noStroke();
      fill(active ? SEL[0] : MUTED[0], active ? SEL[1] : MUTED[1], active ? SEL[2] : MUTED[2]);
      textSize(11.5);
      textAlign(LEFT, CENTER);
      text(codes[i], x + 8, iy);
    }
    if (opt.values) {
      noStroke();
      fill(INK[0], INK[1], INK[2]);
      textSize(13);
      textAlign(CENTER, CENTER);
      text(vals[i], x - 20, iy - 11);
    }
  }

  /* output line */
  stroke(LINE[0], LINE[1], LINE[2]);
  strokeWeight(1.2);
  line(x + bw, y + bh / 2, x + bw + 40, y + bh / 2);
  noStroke();
  fill(INK[0], INK[1], INK[2]);
  textSize(13);
  textAlign(LEFT, CENTER);
  text('F', x + bw + 46, y + bh / 2);

  /* select lines entering from below */
  var sx = x + 40;
  stroke(SEL[0], SEL[1], SEL[2]);
  strokeWeight(1.2);
  line(sx, y + bh, sx, y + bh + 30);
  line(sx + 60, y + bh, sx + 60, y + bh + 30);
  noStroke();
  fill(SEL[0], SEL[1], SEL[2]);
  textSize(12);
  textAlign(CENTER, TOP);
  text('S1 = P', sx, y + bh + 34);
  text('S0 = Q', sx + 60, y + bh + 34);
}

function panel(w, h, lines) {
  var x = 400, y = 74, i;
  noStroke();
  fill(248, 249, 252);
  rect(x - 10, y - 10, w - x - 14, 300);
  fill(INK[0], INK[1], INK[2]);
  textSize(13);
  textAlign(LEFT, TOP);
  for (i = 0; i < lines.length; i++) {
    text(lines[i], x, y + i * 21);
  }
}

function mintermTable(p, w, h) {
  var x = 70, y = 96, rows = 8, i;
  var pw = 176, rh = 24;
  noStroke();
  fill(246, 248, 251);
  rect(x, y, pw + 70, rows * rh + 8);

  for (i = 0; i < rows; i++) {
    var isOne = (i === 2 || i === 3 || i === 5 || i === 6);
    var yy = y + 4 + i * rh;
    if (isOne) {
      noStroke();
      fill(226, 242, 234);
      rect(x + 2, yy, pw + 66, rh - 2);
    }
    noStroke();
    fill(isOne ? ONE[0] : MUTED[0], isOne ? ONE[1] : MUTED[1], isOne ? ONE[2] : MUTED[2]);
    textSize(12.5);
    textAlign(LEFT, CENTER);
    var bits = '' + Math.floor(i / 4) + '' + (Math.floor(i / 2) % 2) + '' + (i % 2);
    text('m' + i + '   ' + bits, x + 12, yy + rh / 2);
    textAlign(RIGHT, CENTER);
    text(isOne ? '1' : '0', x + pw + 58, yy + rh / 2);
  }
}

/* three-variable map: rows P, columns QR in Gray order */
function kmap(p, w, h, opt) {
  var x = 84, y = 118, cw = 62, ch = 62;
  var cols = ['00', '01', '11', '10'];
  var cells = [[0, 1, 3, 2], [4, 5, 7, 6]];
  var i, j;

  noStroke();
  fill(255, 255, 255);
  rect(x - 40, y - 34, cw * 4 + 50, ch * 2 + 44);

  noStroke();
  fill(SOFT[0], SOFT[1], SOFT[2]);
  textSize(11.5);
  textAlign(CENTER, BOTTOM);
  text('QR', x + cw * 2, y - 20);
  for (j = 0; j < 4; j++) {
    text(cols[j], x + j * cw + cw / 2, y - 4);
  }
  textAlign(RIGHT, CENTER);
  text('P = 0', x - 8, y + ch / 2);
  text('P = 1', x - 8, y + ch + ch / 2);

  for (i = 0; i < 2; i++) {
    for (j = 0; j < 4; j++) {
      var cx = x + j * cw, cy = y + i * ch, m = cells[i][j];
      var isOne = (m === 2 || m === 3 || m === 5 || m === 6);
      stroke(LINE[0], LINE[1], LINE[2]);
      strokeWeight(1);
      noFill();
      rect(cx, cy, cw, ch);

      noStroke();
      fill(MUTED[0], MUTED[1], MUTED[2]);
      textSize(10.5);
      textAlign(LEFT, TOP);
      text('m' + m, cx + 5, cy + 4);

      if (isOne) {
        fill(ONE[0], ONE[1], ONE[2], 255 * (opt.ones === undefined ? 1 : opt.ones));
        textSize(20);
        textStyle(BOLD);
        textAlign(CENTER, CENTER);
        text('1', cx + cw / 2, cy + ch / 2 + 3);
        textStyle(NORMAL);
      }
    }
  }

  /* group P'Q: top row, last two columns (m3 and m2) */
  if (opt.groupA) {
    stroke(SEL[0], SEL[1], SEL[2], 255 * opt.groupA);
    strokeWeight(3);
    noFill();
    rect(x + 2 * cw + 3, y + 3, 2 * cw - 6, ch - 6, 8);
  }
  /* group QR': last column, both rows (m2 and m6) */
  if (opt.groupB) {
    stroke(58, 96, 168, 255 * opt.groupB);
    strokeWeight(3);
    noFill();
    rect(x + 3 * cw + 4, y + 4, cw - 8, 2 * ch - 8, 8);
  }
  /* group PQ'R: bottom row, column QR = 01 (m5) */
  if (opt.groupC) {
    stroke(122, 62, 148, 255 * opt.groupC);
    strokeWeight(3);
    noFill();
    rect(x + cw + 6, y + ch + 6, cw - 12, ch - 12, 8);
  }

  if (opt.answer) {
    noStroke();
    fill(INK[0], INK[1], INK[2], 255 * opt.answer);
    textSize(15);
    textStyle(BOLD);
    textAlign(CENTER, TOP);
    text("F = P'Q + QR' + PQ'R", x + cw * 2, y + 2 * ch + 18);
    textStyle(NORMAL);
  }
}
