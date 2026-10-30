/* IEEE 754 single precision, decoded field by field, for the Number Systems and
   Number Representation topic.

   One word, 0xC2710000:

     hex        C    2    7    1    0    0    0    0
     binary   1100 0010 0111 0001 0000 0000 0000 0000
     fields    1 | 10000100 | 1110001 0000000000000000
     sign      s = 1                       -> negative
     exponent  10000100 = 132, 132 - 127 = 5
     fraction  1110001, so significand 1.1110001 = 1.8828125
     value     -1.8828125 x 2^5 = -1.8828125 x 32 = -60.25

   The word and every number above are recomputed from its bits in
   scripts/validate.py (check_number_representation), not copied from here.
   The two extreme exponent fields are drawn at the end because the largest
   finite number question turns on them. */

window.LESSON = {
  steps: [
    {
      duration: 4000,
      caption: 'The word 0xC2710000 is eight hexadecimal digits, and one hex digit is exactly four bits: C is 1100, 2 is 0010, 7 is 0111, 1 is 0001, and the last four digits are zeros. That is thirty-two bits. Expand the hex before decoding anything - the fields are cut out of the bits, not out of the digits.',
      draw: function (p, w, h) {
        inkBits();
        headBits('Step 1: the word is eight hex digits', 24, 30);
        hexRow(p, w, h);
        bitRow(p, w, h, { showBits: Math.min(1, p * 2) });
        panelBits(w, h, [
          '0xC2710000',
          '= 1100 0010 0111 0001',
          '  0000 0000 0000 0000',
          '',
          '8 hex digits x 4 bits = 32 bits'
        ]);
        noteBits('Each hex digit is four bits, so a byte is two digits.', 24, h - 16);
      }
    },
    {
      duration: 4200,
      caption: 'Single precision cuts those thirty-two bits as one sign bit, eight exponent bits and twenty-three fraction bits, always from the left. The sign is the top bit of the first hex digit, and the exponent field straddles the first two digits, which is why regrouping the hex wrongly is the most common way to lose the question.',
      draw: function (p, w, h) {
        inkBits();
        headBits('Step 2: 1 + 8 + 23, cut from the left', 24, 30);
        bitRow(p, w, h, { showBits: 1, signHot: true, expHot: true, fracHot: true, brackets: Math.min(1, p * 1.6) });
        panelBits(w, h, [
          'sign      1 bit',
          'exponent  8 bits',
          'fraction  23 bits',
          '',
          'total     32 bits'
        ]);
        noteBits('The cut is fixed: the same eight hex digits always split in the same place.', 24, h - 16);
      }
    },
    {
      duration: 3600,
      caption: 'The sign bit is 1, so the number is negative. That is the whole of the sign: it is not a place value and it is not part of the magnitude, so the answer will be -60.25 rather than 60.25 and nothing later in the decode can change it.',
      draw: function (p, w, h) {
        inkBits();
        headBits('Step 3: the sign bit, read alone', 24, 30);
        bitRow(p, w, h, { showBits: 1, signHot: true, brackets: 1 });
        panelBits(w, h, [
          's = 1',
          '',
          'the value is negative',
          '(-1)^1 = -1'
        ]);
        noteBits('0 would have made it positive. The sign bit carries no weight.', 24, h - 16);
      }
    },
    {
      duration: 4400,
      caption: 'Read the exponent field as an unsigned integer: 10000100 is 128 + 4 = 132. The stored exponent is not the exponent used in the value - it carries a bias of 127 - so the true exponent is 132 - 127 = 5. Forgetting the bias would give 2^132, a number far outside the format.',
      draw: function (p, w, h) {
        inkBits();
        headBits('Step 4: the exponent field, and the bias', 24, 30);
        bitRow(p, w, h, { showBits: 1, expHot: true, brackets: 1 });
        panelBits(w, h, [
          'E = 10000100 = 132',
          'bias = 127',
          '',
          'e = 132 - 127 = 5',
          '',
          'normal, because 1 <= E <= 254'
        ]);
        noteBits('A stored exponent of 0 or 255 is not an exponent at all.', 24, h - 16);
      }
    },
    {
      duration: 4600,
      caption: 'The fraction field begins 1110001 and the remaining sixteen bits are zeros. In normal form there is a 1 before the binary point that is never stored, so the significand is 1.1110001: 1 + 0.5 + 0.25 + 0.125 + 0.0078125 = 1.8828125. Drop that hidden 1 and you get 0.8828125, and an answer of 28.25.',
      draw: function (p, w, h) {
        inkBits();
        headBits('Step 5: the fraction, and the hidden 1', 24, 30);
        bitRow(p, w, h, { showBits: 1, fracHot: true, brackets: 1 });
        panelBits(w, h, [
          'F = 1110001 000...',
          '1.F = 1.1110001',
          '',
          '1 + 1/2 + 1/4 + 1/8 + 1/128',
          '= 1.8828125'
        ]);
        noteBits('The leading 1 is implied by the normal form, so it costs no bits.', 24, h - 16);
      }
    },
    {
      duration: 4600,
      caption: 'The value is the significand times two to the true exponent, with the sign applied: 1.8828125 x 32. Equivalently move the binary point five places right, which turns 1.1110001 into 111100.01, and 111100.01 is 32 + 16 + 8 + 4 + 0.25 = 60.25. With the sign bit, the answer is -60.25.',
      draw: function (p, w, h) {
        inkBits();
        headBits('Step 6: assemble the value', 24, 30);
        bitRow(p, w, h, { showBits: 1, signHot: true, expHot: true, fracHot: true, brackets: 1 });
        shiftDemo(p, w, h, Math.min(1, p * 1.4));
        panelBits(w, h, [
          '1.1110001 x 2^5',
          '= 111100.01',
          '',
          '= 60.25',
          'value = -60.25'
        ]);
        noteBits('Move the point right by the true exponent, then apply the sign.', 24, h - 16);
      }
    },
    {
      duration: 4800,
      caption: 'The two extreme exponent fields are reserved, and that is what the largest-number questions test. An all-zero exponent means zero, or a subnormal with no hidden 1; an all-ones exponent means infinity when the fraction is zero and NaN otherwise. So the largest finite single-precision number has exponent 1111 1110, not 1111 1111.',
      draw: function (p, w, h) {
        inkBits();
        headBits('Step 7: the two reserved exponent fields', 24, 30);
        caseRow(w, h);
        panelBits(w, h, [
          'E = 0,   F = 0    zero',
          'E = 0,   F != 0   subnormal',
          'E = 255, F = 0    infinity',
          'E = 255, F != 0   NaN',
          '',
          'largest finite: E = 254'
        ]);
        noteBits('254 is the largest exponent that still denotes a number.', 24, h - 16);
      }
    }
  ]
};

/* ---------------------------------------------------------------- helpers */
function inkBits() {
  var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  background(dark ? color(23, 28, 36) : color(255));
  noStroke();
  fill(dark ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}
function headBits(t, x, y) { textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function noteBits(t, x, y) { textSize(12.5); fill(90, 100, 116); noStroke(); text(t, x, y); }

function bitsOf(hex) {
  var out = '';
  for (var i = 0; i < hex.length; i++) {
    var v = parseInt(hex.charAt(i), 16);
    out += ('000' + v.toString(2)).slice(-4);
  }
  return out;
}

function layout(w, h) {
  var left = 24;
  var cellW = Math.max(12, (w - 60) / 32);
  return { left: left, cellW: cellW, top: h * 0.30, cellH: Math.min(34, h * 0.12) };
}

function hexRow(p, w, h) {
  var hex = 'C2710000';
  var L = layout(w, h);
  var top = h * 0.14;
  for (var i = 0; i < 8; i++) {
    var x = L.left + i * 4 * L.cellW;
    stroke(206, 212, 222); strokeWeight(1);
    noFill(); rect(x, top, 4 * L.cellW - 2, 24, 4);
    noStroke(); fill(31, 94, 255); textSize(13); textAlign(CENTER, CENTER);
    text(hex.charAt(i), x + (4 * L.cellW - 2) / 2, top + 12);
    textAlign('left', 'baseline');
  }
  noStroke(); fill(90, 100, 116); textSize(11.5);
  text('eight hex digits, four bits each', L.left, top - 6);
}

function bitRow(p, w, h, opt) {
  var bits = bitsOf('C2710000');
  var L = layout(w, h);
  var show = opt.showBits === undefined ? 1 : opt.showBits;
  for (var i = 0; i < 32; i++) {
    var x = L.left + i * L.cellW;
    var hot = (opt.signHot && i === 0) || (opt.expHot && i >= 1 && i <= 8) ||
              (opt.fracHot && i >= 9);
    var on = bits.charAt(i) === '1';
    if (hot && on) { fill(31, 94, 255, 46); stroke(31, 94, 255); }
    else if (hot) { fill(245, 247, 251); stroke(31, 94, 255); }
    else { fill(245, 247, 251); stroke(206, 212, 222); }
    strokeWeight(1);
    rect(x, L.top, L.cellW - 2, L.cellH, 3);
    if (i / 32 < show) {
      noStroke(); fill(on ? color(20, 24, 31) : color(120, 130, 146));
      textSize(Math.max(9, Math.min(12, L.cellW * 0.8)));
      textAlign(CENTER, CENTER);
      text(bits.charAt(i), x + (L.cellW - 2) / 2, L.top + L.cellH / 2);
      textAlign('left', 'baseline');
    }
  }
  var t = opt.brackets || 0;
  if (t > 0) {
    var y = L.top - 12;
    noStroke(); fill(31, 94, 255); textSize(11.5);
    text('sign', L.left, y - 8);
    text('exponent (8 bits)', L.left + L.cellW + 4, y - 8);
    text('fraction (23 bits)', L.left + 9 * L.cellW + 4, y - 8);
    stroke(31, 94, 255); strokeWeight(2);
    line(L.left, y, L.left + L.cellW - 2, y);
    line(L.left + L.cellW, y, L.left + 9 * L.cellW - 2, y);
    line(L.left + 9 * L.cellW, y, L.left + 32 * L.cellW - 2, y);
  }
}

/* The significand, its point moved five places right. */
function shiftDemo(p, w, h, t) {
  var x = 24, y = h * 0.62;
  noStroke(); fill(90, 100, 116); textSize(12);
  text('move the binary point 5 places right:', x, y - 18);
  var shown = '1.1110001';
  var moved = '111100.01';
  fill(20, 24, 31); textSize(15); textStyle(BOLD);
  text(shown, x, y + 4);
  textSize(13); textStyle(NORMAL); fill(31, 94, 255);
  text('->', x + 110, y + 4);
  textStyle(BOLD); fill(20, 24, 31); textSize(15);
  text(t > 0.5 ? moved : '', x + 140, y + 4);
  textStyle(NORMAL);
}

/* The four reserved cases, drawn as three-field strips. */
function caseRow(w, h) {
  var rows = [
    ['0', '00000000', '000...0', 'zero'],
    ['0', '00000000', '111...1', 'subnormal'],
    ['0', '11111111', '000...0', 'infinity'],
    ['0', '11111111', '111...1', 'NaN']
  ];
  var x = 24, y = h * 0.16, rowH = Math.min(26, h * 0.06);
  noStroke(); fill(90, 100, 116); textSize(11.5);
  text('sign     exponent      fraction', x, y - 8);
  for (var i = 0; i < rows.length; i++) {
    var ry = y + i * (rowH + 6);
    fill(245, 247, 251); stroke(206, 212, 222); strokeWeight(1);
    rect(x, ry, Math.min(330, w - 60), rowH, 4);
    noStroke(); fill(20, 24, 31); textSize(12);
    text(rows[i][0], x + 10, ry + rowH / 2 + 4);
    fill(31, 94, 255);
    text(rows[i][1], x + 44, ry + rowH / 2 + 4);
    fill(70, 80, 96);
    text(rows[i][2], x + 150, ry + rowH / 2 + 4);
    fill(20, 24, 31);
    text(rows[i][3], x + 240, ry + rowH / 2 + 4);
  }
}

function panelBits(w, h, lines) {
  var x = Math.max(w * 0.56, 300), y = 62;
  noStroke();
  for (var i = 0; i < lines.length; i++) {
    fill(i === 0 ? color(20, 24, 31) : color(70, 80, 96));
    textSize(i === 0 ? 13 : 12);
    text(lines[i], x, y + i * 17);
  }
}
