/* Floating-point addition, aligned step by step, for the Computer Arithmetic topic.

   The two operands are the ones in GATE CSE 2026 Set 1 Q.26:

     X = 0x35C00000 = 0011 0101 1100 0000 0000 0000 0000 0000
     Y = 0x34A00000 = 0011 0100 1010 0000 0000 0000 0000 0000

   Fields (1 sign | 8 exponent | 23 fraction):

     X   s=0   E=01101011=107  e=-20   F=1000...  ->  X = 1.1      x 2^-20
     Y   s=0   E=01101001=105  e=-22   F=0100...  ->  Y = 1.01     x 2^-22

     align   Y -> 0.0101 x 2^-20        (two places right)
     add     1.1000 + 0.0101 = 1.1101   (already in [1,2))
     encode  s=0 E=107 F=1101000...  ->  0x35E80000

   Every number above is recomputed from the bits in scripts/validate.py
   (check_computer_arithmetic), not copied from this file. The closing steps
   show the two cases the alignment step must handle and the addend that
   disappears entirely. */

window.LESSON = {
  steps: [
    {
      duration: 4200,
      caption: 'Two IEEE 754 single-precision words, X = 0x35C00000 and Y = 0x34A00000. Each is one sign bit, eight exponent bits and twenty-three fraction bits, cut from the left. Adding them is not adding two integers: the two numbers carry their binary points at different places, so the fields have to be read before anything can be added.',
      draw: function (p, w, h) {
        inkFp();
        headFp('Step 1: two words, cut as 1 + 8 + 23', 22, 28);
        wordRow(w, h, 'X = 0x35C00000', '00110101110000000000000000000000', Math.min(1, p * 1.8));
        wordRow(w, h, 'Y = 0x34A00000', '00110100101000000000000000000000', Math.min(1, p * 1.8), 1);
        panelFp(w, h, [
          'X = 0x35C00000',
          'Y = 0x34A00000',
          '',
          'sign   1 bit',
          'exponent 8 bits',
          'fraction 23 bits'
        ]);
        noteFp('The same cut every time: the fields live in fixed positions.', 22, h - 14);
      }
    },
    {
      duration: 4600,
      caption: 'Read the exponent fields first. X has 0110 1011, which is 107, and Y has 0110 1001, which is 105. Both carry the bias of 127, so the exponents in the values are -20 and -22. They differ by two, which is the whole reason the significands cannot simply be added as they stand.',
      draw: function (p, w, h) {
        inkFp();
        headFp('Step 2: the exponent fields, and the bias', 22, 28);
        wordRow(w, h, 'X', '00110101110000000000000000000000', 1, 0, { exp: true });
        wordRow(w, h, 'Y', '00110100101000000000000000000000', 1, 1, { exp: true });
        panelFp(w, h, [
          'E(X) = 01101011 = 107',
          'E(Y) = 01101001 = 105',
          '',
          'e(X) = 107 - 127 = -20',
          'e(Y) = 105 - 127 = -22',
          '',
          'difference = 2'
        ]);
        noteFp('The stored exponent is not the exponent of the value: subtract the bias.', 22, h - 14);
      }
    },
    {
      duration: 5000,
      caption: 'Align by shifting the smaller-exponent significand right by the difference. Y = 1.0100 at 2^-22 becomes 0.0101 at 2^-20: two places right, and its exponent raised by two. Only the smaller one is shifted, and only to the right, because a left shift would need bits the format never stored.',
      draw: function (p, w, h) {
        inkFp();
        headFp('Step 3: shift Y right two places', 22, 28);
        alignDemo(w, h, Math.min(1, p * 1.3));
        panelFp(w, h, [
          'Y = 1.0100 x 2^-22',
          '  = 0.0101 x 2^-20',
          '',
          'shift right 2',
          'exponent -22 -> -20',
          '',
          'X = 1.1000 x 2^-20'
        ]);
        noteFp('Both operands now sit at 2^-20, so the points line up.', 22, h - 14);
      }
    },
    {
      duration: 4400,
      caption: 'Now add the significands as ordinary binary fractions at the common exponent: 1.1000 + 0.0101 = 1.1101, with the exponent staying at -20. Nothing has been rounded yet and no bit has been lost, because the shifted operand was short enough to fit.',
      draw: function (p, w, h) {
        inkFp();
        headFp('Step 4: add the aligned significands', 22, 28);
        addDemo(w, h, Math.min(1, p * 1.5));
        panelFp(w, h, [
          '  1.1000',
          '+ 0.0101',
          '  ------',
          '  1.1101',
          '',
          'exponent stays -20'
        ]);
        noteFp('Column by column, exactly as with integers - the points are aligned.', 22, h - 14);
      }
    },
    {
      duration: 5200,
      caption: 'Check the normal form before encoding. A normalised significand lies in [1, 2), and 1.1101 does, so no shift is needed here. The other two cases are the ones that cost marks: a carry makes the sum reach 2 or more, so it shifts right once and the exponent goes up by one; a cancellation leaves something like 0.0001, which shifts left until a 1 reaches the point.',
      draw: function (p, w, h) {
        inkFp();
        headFp('Step 5: is the sum in [1, 2)?', 22, 28);
        caseDemo(w, h, Math.min(1, p * 1.4));
        panelFp(w, h, [
          'this sum: 1.1101',
          '1 <= 1.1101 < 2',
          'no shift, exponent -20',
          '',
          'carry: 1.1 + 1.1 = 11.0',
          ' -> 1.10, exponent + 1',
          'cancel: 1.0001 - 1.0 = 0.0001',
          ' -> shift left 4'
        ]);
        noteFp('The normal form is a condition on the significand, not a formality.', 22, h - 14);
      }
    },
    {
      duration: 4200,
      caption: 'Encode the result. The sign is 0 because both operands are positive, the exponent field is -20 + 127 = 107 = 0110 1011, and the fraction is 1101 followed by zeros. Concatenating the three fields gives 0x35E80000 - option (C) of the GATE 2026 question.',
      draw: function (p, w, h) {
        inkFp();
        headFp('Step 6: assemble the word', 22, 28);
        wordRow(w, h, 'Z', '00110101111010000000000000000000', Math.min(1, p * 1.6), 0, { exp: true, frac: true });
        panelFp(w, h, [
          's = 0',
          'E = -20 + 127 = 107',
          '   = 0110 1011',
          'F = 1101 000...',
          '',
          '0011 0101 1110 1000',
          '= 0x35E80000'
        ]);
        noteFp('Fields in, fields out: the encoding is a copy, not a calculation.', 22, h - 14);
      }
    },
    {
      duration: 4600,
      caption: 'Decode the answer back to check it. 1.1101 at 2^-20 is 1.8125 x 2^-20, which is 1.7285e-6, and that is 1.4305e-6 plus 2.9802e-7 - exactly X plus Y. A floating-point addition is only right if it can be read back to the sum of the two values.',
      draw: function (p, w, h) {
        inkFp();
        headFp('Step 7: read it back', 22, 28);
        valueDemo(w, h, Math.min(1, p * 1.4));
        panelFp(w, h, [
          '1.1101 x 2^-20',
          '= 1.8125 x 2^-20',
          '= 1.7285e-6',
          '',
          'X = 1.4305e-6',
          'Y = 2.9802e-7',
          'X + Y = 1.7285e-6'
        ]);
        noteFp('If the decode does not match the sum, the encoding is wrong.', 22, h - 14);
      }
    },
    {
      duration: 5200,
      caption: 'The alignment step is where the arithmetic silently loses information. Add 1.0 and 2^-30: the exponent difference is 30 and the significand has only 24 bits, so the addend is shifted right past everything stored and the sum is 1.0 exactly. That is not an approximation - it is the definition of the format, and it is why (a + b) + c need not equal a + (b + c).',
      draw: function (p, w, h) {
        inkFp();
        headFp('Step 8: the addend that disappears', 22, 28);
        absorbDemo(w, h, Math.min(1, p * 1.4));
        panelFp(w, h, [
          '1.0 + 2^-30',
          'difference 30 > 24 bits',
          'addend shifted off the end',
          '',
          'sum = 1.0 exactly',
          '',
          'order of addition matters'
        ]);
        noteFp('A term below half an ulp of the running total vanishes exactly.', 22, h - 14);
      }
    }
  ]
};

/* ---------------------------------------------------------------- helpers */
function inkFp() {
  var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  background(dark ? color(23, 28, 36) : color(255));
  noStroke();
  fill(dark ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}

function headFp(t, x, y) {
  textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL);
}

function noteFp(t, x, y) {
  textSize(12.5); fill(90, 100, 116); noStroke(); text(t, x, y);
}

function panelFp(w, h, lines) {
  var x = Math.max(w * 0.60, 300), y = 66;
  noStroke();
  for (var i = 0; i < lines.length; i++) {
    fill(i === 0 ? color(20, 24, 31) : color(70, 80, 96));
    textSize(i === 0 ? 13 : 12);
    text(lines[i], x, y + i * 17);
  }
}

/* One 32-bit word drawn as cells, with the exponent and fraction optionally highlighted. */
function wordRow(w, h, label, bits, reveal, row, opt) {
  opt = opt || {};
  var left = 22;
  var cellW = Math.max(9, Math.min(18, (w * 0.56 - 40) / 32));
  var top = 52 + (row || 0) * 62;
  var cellH = 22;
  noStroke(); fill(70, 80, 96); textSize(11.5);
  text(label, left, top - 8);
  for (var i = 0; i < 32; i++) {
    var x = left + i * cellW;
    var hot = (opt.exp && i >= 1 && i <= 8) || (opt.frac && i >= 9);
    var on = bits.charAt(i) === '1';
    if (hot && on) { fill(31, 94, 255, 46); stroke(31, 94, 255); }
    else if (hot) { fill(245, 247, 251); stroke(31, 94, 255); }
    else { fill(245, 247, 251); stroke(206, 212, 222); }
    strokeWeight(1);
    rect(x, top, cellW - 2, cellH, 3);
    if (i / 32 < reveal) {
      noStroke(); fill(on ? color(20, 24, 31) : color(120, 130, 146));
      textSize(Math.max(8, Math.min(11, cellW * 0.8)));
      textAlign(CENTER, CENTER);
      text(bits.charAt(i), x + (cellW - 2) / 2, top + cellH / 2);
      textAlign('left', 'baseline');
    }
  }
}

/* The significand, shifted two places right. */
function alignDemo(w, h, t) {
  var x = 22, y = h * 0.34;
  noStroke(); fill(90, 100, 116); textSize(12);
  text('Y, two places right:', x, y - 16);
  fill(20, 24, 31); textSize(17); textStyle(BOLD);
  text('1.0100', x, y + 6);
  textSize(13); textStyle(NORMAL); fill(31, 94, 255);
  text('->', x + 120, y + 6);
  if (t > 0.35) {
    fill(20, 24, 31); textSize(17); textStyle(BOLD);
    text('0.0101', x + 152, y + 6);
    textStyle(NORMAL);
  }
  noStroke(); fill(90, 100, 116); textSize(12);
  text('1.0100 x 2^-22  =  0.0101 x 2^-20', x, y + 36);
}

/* The column addition of the two aligned significands. */
function addDemo(w, h, t) {
  var x = 26, y = h * 0.30, dy = 26;
  noStroke(); fill(20, 24, 31); textSize(17);
  text('1.1000', x, y);
  if (t > 0.3) { text('+ 0.0101', x, y + dy); }
  if (t > 0.55) {
    stroke(150, 160, 176); strokeWeight(1);
    line(x, y + dy + 8, x + 118, y + dy + 8);
  }
  if (t > 0.75) {
    noStroke(); fill(31, 94, 255); textStyle(BOLD);
    text('1.1101', x, y + 2 * dy);
    textStyle(NORMAL);
  }
}

/* The three normal-form cases, drawn as a small band. */
function caseDemo(w, h, t) {
  var x = 22, y = h * 0.36, dy = 24;
  var rows = [
    ['this sum', '1.1101', 'in [1,2): encode'],
    ['carry', '11.0', '-> 1.10, exponent +1'],
    ['cancel', '0.0001', '-> shift left 4']
  ];
  noStroke(); fill(90, 100, 116); textSize(11.5);
  text('case        raw sum        what happens', x, y - 16);
  for (var i = 0; i < rows.length; i++) {
    if (i / rows.length > t + 0.2) { continue; }
    var ry = y + i * (dy + 6);
    fill(245, 247, 251); stroke(206, 212, 222); strokeWeight(1);
    rect(x, ry - 13, Math.min(300, w * 0.52), dy, 4);
    noStroke(); fill(20, 24, 31); textSize(12);
    text(rows[i][0], x + 8, ry + 3);
    fill(31, 94, 255);
    text(rows[i][1], x + 78, ry + 3);
    fill(70, 80, 96);
    text(rows[i][2], x + 150, ry + 3);
  }
}

/* The decoded value, and the two operands it came from. */
function valueDemo(w, h, t) {
  var x = 22, y = h * 0.34, dy = 22;
  var rows = ['1.1101 x 2^-20', '= 1.8125 x 2^-20', '= 1.7285e-6'];
  noStroke();
  for (var i = 0; i < rows.length; i++) {
    if (i / rows.length > t + 0.25) { continue; }
    fill(i === 2 ? color(31, 94, 255) : color(20, 24, 31));
    textSize(i === 2 ? 15 : 14);
    text(rows[i], x, y + i * dy);
  }
  noStroke(); fill(90, 100, 116); textSize(12);
  text('X = 1.4305e-6', x, y + 3.4 * dy);
  text('Y = 2.9802e-7', x, y + 3.4 * dy + 18);
}

/* The addend that falls off the end of the significand. */
function absorbDemo(w, h, t) {
  var x = 22, y = h * 0.34;
  noStroke(); fill(90, 100, 116); textSize(12);
  text('1.000000000000000000000000  +  0.000000000000000000000000000001', x, y - 18);
  noStroke(); fill(20, 24, 31); textSize(14);
  text('the addend starts 30 places to the right', x, y + 6);
  if (t > 0.4) {
    fill(31, 94, 255); textSize(15); textStyle(BOLD);
    text('= 1.0', x, y + 34);
    textStyle(NORMAL);
  }
  if (t > 0.7) {
    noStroke(); fill(90, 100, 116); textSize(12);
    text('all 24 stored bits are unchanged', x, y + 56);
  }
}
