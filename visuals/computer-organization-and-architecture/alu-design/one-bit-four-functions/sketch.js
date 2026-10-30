/* One bit slice of an ALU, its function code and its flags, for the ALU Design topic.

   The picture is fixed for the whole lesson:

     operand bits A = 1, B = 1   (the slice under the microscope)
     the slice holds a full adder, an AND gate and an OR gate
     a 4-to-1 multiplexer selects between AND, OR, ADD and SUB
     the code is two select bits S1 S0: 00 AND, 01 OR, 10 ADD, 11 SUB

   Each step runs the slice with A = 1, B = 1 and the carry in from below,
   and shows the result bit, the carry out and the flags.

   Every number shown here is recomputed in scripts/validate.py
   (check_alu_design), not copied from this file. */

var A_BIT = 1, B_BIT = 1, CIN = 1;

var OPS = [
  { code: '00', name: 'AND', out: 1, cout: 0, z: 0, n: 0, c: 0, v: 0,
    why: 'A AND B = 1 AND 1 = 1. No carry is produced, so C = 0.' },
  { code: '01', name: 'OR', out: 1, cout: 0, z: 0, n: 0, c: 0, v: 0,
    why: 'A OR B = 1 OR 1 = 1. Again no carry, so C = 0.' },
  { code: '10', name: 'ADD', out: 1, cout: 1, z: 0, n: 1, c: 1, v: 0,
    why: 'A + B + carry-in = 1 + 1 + 1 = 3, so the sum bit is 1 and the carry out is 1.' },
  { code: '11', name: 'SUB', out: 0, cout: 1, z: 1, n: 0, c: 1, v: 0,
    why: 'SUB inverts B before the adder, so the slice adds A + NOT B + 1 = 1 + 0 + 1 = 2: sum bit 0, carry out 1, so Z = 1.' }
];

window.LESSON = {
  steps: [
    {
      duration: 5200,
      caption: 'One bit of an ALU. The two operand bits A = 1 and B = 1 arrive, and inside the slice three things happen at once: a full adder computes a sum and a carry, an AND gate computes A AND B, and an OR gate computes A OR B. All three answers exist simultaneously; nothing has been selected yet.',
      draw: function (p, w, h) {
        ink();
        head('One slice, three candidate answers', 22, 28);
        inputs(w, h, 1);
        gates(w, h, 1, null);
        mux(w, h, 1, null);
        note('A full adder, an AND gate and an OR gate, all fed by the same two operand bits.', 22, h - 14);
      }
    },
    {
      duration: 4600,
      caption: 'The function code arrives as two select bits, S1 S0. Two bits name four codes, so this slice can be given four functions. Code 00 selects the AND gate: the result bit is 1, and no carry is produced.',
      draw: function (p, w, h) {
        ink();
        head('Code 00: AND selected, result 1, no carry', 22, 28);
        inputs(w, h, 1);
        gates(w, h, 1, 'AND');
        mux(w, h, 1, OPS[0]);
        flags(w, h, OPS[0]);
        note(OPS[0].why, 22, h - 14);
      }
    },
    {
      duration: 4200,
      caption: 'Code 01 selects the OR gate. The result is 1 again, which is exactly why a single test case cannot tell two functions apart: the operands 1 and 1 give the same answer under AND and under OR. The code, not the data, decides what the ALU computes.',
      draw: function (p, w, h) {
        ink();
        head('Code 01: OR selected, result 1, no carry', 22, 28);
        inputs(w, h, 1);
        gates(w, h, 1, 'OR');
        mux(w, h, 1, OPS[1]);
        flags(w, h, OPS[1]);
        note(OPS[1].why, 22, h - 14);
      }
    },
    {
      duration: 5400,
      caption: 'Code 10 selects the adder, with the carry in from the slice below set to 1. One plus one plus one is three, so the sum bit is 1 and a carry leaves the slice for the next one. This carry is the only signal that crosses slices, and it is what makes addition the slowest function.',
      draw: function (p, w, h) {
        ink();
        head('Code 10: ADD selected, sum 1, carry out 1', 22, 28);
        inputs(w, h, 1);
        gates(w, h, 1, 'ADD');
        mux(w, h, 1, OPS[2]);
        flags(w, h, OPS[2]);
        carryArrow(w, h, Math.min(1, p * 1.4));
        note(OPS[2].why, 22, h - 14);
      }
    },
    {
      duration: 5400,
      caption: 'Code 11 selects subtraction. Nothing new is built: the same adder is used with B inverted and the carry in held at 1, which is the two\u2019s complement of B. That is why subtraction costs one mode bit and an inverter bank rather than a second adder.',
      draw: function (p, w, h) {
        ink();
        head('Code 11: SUB selected, the same adder with B inverted', 22, 28);
        inputs(w, h, 1);
        gates(w, h, 1, 'SUB');
        mux(w, h, 1, OPS[3]);
        flags(w, h, OPS[3]);
        invertMark(w, h, Math.min(1, p * 1.5));
        note(OPS[3].why, 22, h - 14);
      }
    },
    {
      duration: 5200,
      caption: 'The flags leave the slice with the result. Z is 1 only when every result bit is 0, N is the result\u2019s top bit, C is the carry out of the top slice and V is the exclusive-or of the carry into and out of the sign column. The control unit latches them and a later branch instruction reads them.',
      draw: function (p, w, h) {
        ink();
        head('The four flags, and who reads them', 22, 28);
        flagTable(w, h, Math.min(1, p * 1.3));
        note('A branch does not look at the result; it looks at these bits.', 22, h - 14);
      }
    },
    {
      duration: 5000,
      caption: 'Four codes, four functions, one slice. Widen the slice to n bits, chain the carry from bit to bit, and the same four codes give an n-bit AND, OR, add and subtract. The code is a ceiling: three select bits would buy eight functions, and one code is usually spent on doing nothing so the ALU can leave a shared bus alone.',
      draw: function (p, w, h) {
        ink();
        head('Four codes, four functions, and what a wider code buys', 22, 28);
        summary(w, h, Math.min(1, p * 1.4));
        note('k select bits give at most 2^k functions; 2 bits give 4, 3 bits give 8.', 22, h - 14);
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

function head(t, x, y) {
  textSize(15.5); textStyle(BOLD); text(t, x, y); textStyle(NORMAL);
}

function note(t, x, y) {
  textSize(12); fill(90, 100, 116); noStroke(); text(t, x, y);
}

function box(x, y, w, h, label, hot) {
  if (hot) { fill(31, 94, 255, 46); stroke(31, 94, 255); }
  else { fill(245, 247, 251); stroke(206, 212, 222); }
  strokeWeight(1);
  rect(x, y, w, h, 4);
  noStroke(); fill(20, 24, 31); textSize(12);
  text(label, x + 8, y + h / 2 + 4);
}

function inputs(w, h, t) {
  noStroke(); fill(90, 100, 116); textSize(11.5);
  text('operand bits into this slice', 22, 48);
  box(22, 56, 90, 26, 'A = ' + A_BIT, true);
  box(22, 92, 90, 26, 'B = ' + B_BIT, true);
  box(22, 128, 90, 26, 'Cin = ' + CIN, false);
}

function gates(w, h, t, active) {
  var x = 150, y = 52;
  box(x, y, 130, 26, 'full adder', active === 'ADD' || active === 'SUB');
  box(x, y + 36, 130, 26, 'AND gate', active === 'AND');
  box(x, y + 72, 130, 26, 'OR gate', active === 'OR');
  if (t > 0.4 && active) {
    noStroke(); fill(31, 94, 255); textSize(11.5);
    text('this gate is the selected source', x, y + 116);
  }
}

function mux(w, h, t, op) {
  var x = 320, y = 52;
  noStroke(); fill(90, 100, 116); textSize(11.5);
  text('output multiplexer', x, y - 8);
  box(x, y, 120, 60, '4-to-1 MUX', !!op);
  if (op) {
    noStroke(); fill(31, 94, 255); textSize(12);
    text('S1 S0 = ' + op.code, x + 8, y + 78);
    text(op.name, x + 8, y + 96);
    textSize(13);
    text('result bit = ' + op.out, x + 8, y + 118);
  }
}

function flags(w, h, op) {
  if (!op) { return; }
  var x = 470, y = 52;
  noStroke(); fill(90, 100, 116); textSize(11.5);
  text('status out', x, y - 8);
  var names = ['Z', 'N', 'C', 'V'];
  var vals = [op.z, op.n, op.c, op.v];
  for (var i = 0; i < names.length; i++) {
    box(x, y + i * 32, 96, 26, names[i] + ' = ' + vals[i], vals[i] === 1);
  }
}

function carryArrow(w, h, t) {
  var x = 320, y = 150;
  stroke(31, 94, 255); strokeWeight(2);
  line(x, y, x + 100 * t, y);
  noStroke(); fill(31, 94, 255); textSize(11.5);
  text('carry out = 1, to the next slice', x, y + 18);
}

function invertMark(w, h, t) {
  var x = 150, y = 176;
  noStroke(); fill(31, 94, 255); textSize(11.5);
  text('B is inverted and the carry in is held at 1', x, y);
  if (t > 0.6) {
    fill(90, 100, 116);
    text('so the adder computes A + NOT B + 1, which is A - B', x, y + 18);
  }
}

function flagTable(w, h, t) {
  var rows = [
    ['Z', 'every result bit is 0', 'set by a compare, read by a branch on equal'],
    ['N', 'the result top bit', 'the sign, but only for signed values'],
    ['C', 'the carry out of the top bit', 'unsigned range; for A - B, 1 means no borrow'],
    ['V', 'carry into XOR carry out of the sign column', 'signed range only']
  ];
  var x = 22, y = 62, dy = 34;
  noStroke(); fill(90, 100, 116); textSize(11);
  text('flag   what it is                              what it answers', x, y - 8);
  for (var i = 0; i < rows.length; i++) {
    if (i / rows.length > t + 0.25) { continue; }
    var ry = y + i * dy;
    fill(245, 247, 251); stroke(206, 212, 222); strokeWeight(1);
    rect(x, ry, Math.min(520, w - 44), dy - 8, 3);
    noStroke(); fill(31, 94, 255); textSize(12.5);
    text(rows[i][0], x + 8, ry + 18);
    fill(20, 24, 31); textSize(11.5);
    text(rows[i][1], x + 44, ry + 18);
    fill(70, 80, 96); textSize(11);
    text(rows[i][2], x + 44, ry + 30);
  }
}

function summary(w, h, t) {
  var rows = [
    ['00', 'AND', '1', '0'],
    ['01', 'OR', '1', '0'],
    ['10', 'ADD', '1', '1'],
    ['11', 'SUB', '0', '1']
  ];
  var x = 22, y = 66, dy = 30;
  noStroke(); fill(90, 100, 116); textSize(11);
  text('S1 S0   function   result bit   carry out', x, y - 8);
  for (var i = 0; i < rows.length; i++) {
    if (i / rows.length > t + 0.25) { continue; }
    var ry = y + i * dy;
    fill(i === 3 ? color(31, 94, 255, 40) : color(245, 247, 251));
    stroke(i === 3 ? color(31, 94, 255) : color(206, 212, 222));
    strokeWeight(1);
    rect(x, ry, Math.min(360, w - 44), dy - 8, 3);
    noStroke(); fill(20, 24, 31); textSize(12);
    text(rows[i][0], x + 8, ry + 16);
    text(rows[i][1], x + 66, ry + 16);
    fill(70, 80, 96);
    text(rows[i][2], x + 176, ry + 16);
    text(rows[i][3], x + 276, ry + 16);
  }
  if (t > 0.5) {
    noStroke(); fill(90, 100, 116); textSize(11.5);
    text('two select bits, four functions; the fourth is subtraction,', x, y + 4 * dy + 10);
    text('built from the adder rather than from a new unit.', x, y + 4 * dy + 26);
  }
}
