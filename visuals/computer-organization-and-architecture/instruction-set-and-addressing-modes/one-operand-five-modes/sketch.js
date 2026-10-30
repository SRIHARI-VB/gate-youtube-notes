/* One operand reached six ways from the same address field, for the
   Instruction Set and Addressing Modes topic.

   The picture is fixed for the whole lesson:

     instruction at 100, address field A = 500
     R2 = 1200 (a pointer)     R3 = 700 (an index)     PC = 700
     M[500]  = 1200            M[1200] = 42

     immediate        operand = 500                     0 reads
     direct           EA = 500            operand 1200   1 read
     indirect         EA = M[500] = 1200  operand 42     2 reads
     register ind.    EA = R2 = 1200      operand 42     1 read
     indexed          EA = 500 + 700      operand 42     1 read
     PC-relative      EA = 700 + 500      operand 42     1 read

   Every number above is recomputed in scripts/validate.py
   (check_instruction_set_and_addressing_modes), not copied from this file. */

var FIELD = 500, R2 = 1200, R3 = 700, PC = 700, M500 = 1200, M1200 = 42;

window.LESSON = {
  steps: [
    {
      duration: 5200,
      caption: 'One instruction, one address field holding 500, and a memory with two interesting locations: M[500] holds 1200 and M[1200] holds 42. R2 holds 1200, R3 holds 700 and the program counter holds 700. Nothing changes in the instruction across this lesson - only the rule for reading its field.',
      draw: function (p, w, h) {
        ink();
        head('The instruction, the registers and the memory', 22, 28);
        instrBox(w, h, Math.min(1, p * 1.6));
        memoryStack(w, h, Math.min(1, p * 1.2));
        panel(w, h, ['field A = 500', '', 'R2 = 1200', 'R3 = 700', 'PC = 700', '',
                     'M[500] = 1200', 'M[1200] = 42']);
        note('The same field value is read six different ways from here on.', 22, h - 14);
      }
    },
    {
      duration: 4200,
      caption: 'Immediate mode: the field is the value. The operand is 500, nothing is fetched, and the count of operand memory references is zero. This is the fastest mode and the narrowest, because the value must fit in the field.',
      draw: function (p, w, h) {
        ink();
        head('Immediate: operand = 500, no memory read', 22, 28);
        formula(w, h, Math.min(1, p * 1.3), ['operand = A', '= 500', '', 'memory reads: 0'], 0);
        memoryStack(w, h, 1);
        panel(w, h, ['operand = 500', 'reads = 0', '', 'the value is', 'inside the', 'instruction']);
        note('No effective address is computed, because nothing is addressed.', 22, h - 14);
      }
    },
    {
      duration: 5000,
      caption: 'Direct mode: the field is the address. The effective address is 500 and one read returns M[500], which is 1200. Note carefully that the operand is 1200, not 42 - the number at 1200 is not what a direct operand gives you.',
      draw: function (p, w, h) {
        ink();
        head('Direct: EA = 500, one read, operand 1200', 22, 28);
        formula(w, h, Math.min(1, p * 1.3), ['EA = A', '= 500', '', 'operand = M[500]', '= 1200', '', 'reads = 1'], 1);
        memoryStack(w, h, 1, Math.min(1, p * 1.5), 'direct');
        panel(w, h, ['EA = 500', 'operand = 1200', 'reads = 1', '', 'NOT 42 -', 'direct stops', 'one level up']);
        note('The field names the location; what is there is the operand.', 22, h - 14);
      }
    },
    {
      duration: 5400,
      caption: 'Indirect mode: read the field first, and what you read is the address. M[500] is 1200, so the effective address is 1200, and a second read returns 42. Two operand memory references - the pointer, then the operand.',
      draw: function (p, w, h) {
        ink();
        head('Indirect: EA = M[500] = 1200, two reads', 22, 28);
        formula(w, h, Math.min(1, p * 1.3), ['EA = M[A]', '= M[500]', '= 1200', '', 'operand = M[1200]', '= 42', '', 'reads = 2'], 2);
        memoryStack(w, h, 1, Math.min(1, p * 1.5), 'indirect');
        panel(w, h, ['EA = 1200', 'operand = 42', 'reads = 2', '', 'pointer in', 'memory costs', 'one extra read']);
        note('One level of indirection is exactly one more dependent read.', 22, h - 14);
      }
    },
    {
      duration: 4600,
      caption: 'Register indirect: the pointer is already in a register. R2 holds 1200, so the effective address is 1200 and one read returns 42. Same operand as indirect mode, one read fewer, because the pointer did not have to be fetched.',
      draw: function (p, w, h) {
        ink();
        head('Register indirect: EA = [R2] = 1200, one read', 22, 28);
        formula(w, h, Math.min(1, p * 1.3), ['EA = [R2]', '= 1200', '', 'operand = M[1200]', '= 42', '', 'reads = 1'], 3);
        memoryStack(w, h, 1, Math.min(1, p * 1.5), 'indirect');
        panel(w, h, ['EA = 1200', 'operand = 42', 'reads = 1', '', 'pointer in', 'a register is', 'one read cheaper']);
        note('The reach is now the register width, not the field width.', 22, h - 14);
      }
    },
    {
      duration: 4600,
      caption: 'Indexed mode: the effective address is the field plus an index register. 500 + 700 is 1200, so one read returns 42. This is how an array element is reached: the base is fixed in the instruction and the index moves.',
      draw: function (p, w, h) {
        ink();
        head('Indexed: EA = A + [R3] = 500 + 700 = 1200', 22, 28);
        formula(w, h, Math.min(1, p * 1.3), ['EA = A + [R3]', '= 500 + 700', '= 1200', '', 'operand = M[1200]', '= 42', '', 'reads = 1'], 4);
        memoryStack(w, h, 1, Math.min(1, p * 1.5), 'indirect');
        panel(w, h, ['EA = 1200', 'operand = 42', 'reads = 1', '', 'A[i] with the', 'index in the', 'register']);
        note('The address arithmetic is free of memory traffic.', 22, h - 14);
      }
    },
    {
      duration: 4800,
      caption: 'PC-relative mode is the same arithmetic with the program counter as the register. The PC holds 700, so 700 + 500 is again 1200 and one read returns 42. The offset is signed, and it is measured from the next instruction, which is what makes branches position independent.',
      draw: function (p, w, h) {
        ink();
        head('PC-relative: EA = PC + A = 700 + 500 = 1200', 22, 28);
        formula(w, h, Math.min(1, p * 1.3), ['EA = PC + A', '= 700 + 500', '= 1200', '', 'operand = M[1200]', '= 42', '', 'reads = 1'], 5);
        memoryStack(w, h, 1, Math.min(1, p * 1.5), 'indirect');
        panel(w, h, ['EA = 1200', 'operand = 42', 'reads = 1', '', 'offset is', 'signed, from the', 'NEXT instruction']);
        note('Move the program and this offset still points at the same place.', 22, h - 14);
      }
    },
    {
      duration: 6000,
      caption: 'The six readings of one field. Immediate gives 500 and no read. Direct gives 1200 after one read - the only mode here whose operand is not 42. Indirect gives 42 after two reads; register indirect, indexed and PC-relative each give 42 after one. The address arithmetic costs nothing; only the reads cost.',
      draw: function (p, w, h) {
        ink();
        head('Six modes, one field, six answers', 22, 28);
        table(w, h, Math.min(1, p * 1.4));
        note('Direct is the trap: the operand is what is AT the address, not what that value points to.', 22, h - 14);
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

function panel(w, h, lines) {
  var x = Math.max(w * 0.62, 300), y = 64;
  noStroke();
  for (var i = 0; i < lines.length; i++) {
    fill(i === 0 ? color(20, 24, 31) : color(70, 80, 96));
    textSize(i === 0 ? 13 : 12);
    text(lines[i], x, y + i * 17);
  }
}

/* The instruction word, with the address field highlighted. */
function instrBox(w, h, t) {
  var x = 22, y = 46;
  noStroke(); fill(90, 100, 116); textSize(11.5);
  text('instruction at 100', x, y - 6);
  fill(245, 247, 251); stroke(206, 212, 222); strokeWeight(1);
  rect(x, y, 120, 24, 3);
  noStroke(); fill(20, 24, 31); textSize(12);
  text('opcode', x + 10, y + 16);
  fill(31, 94, 255, 46); stroke(31, 94, 255);
  rect(x + 62, y, 58, 24, 3);
  noStroke(); fill(20, 24, 31); textSize(12);
  text('A = 500', x + 68, y + 16);
  if (t > 0.6) {
    fill(70, 80, 96); textSize(11.5);
    text('the operand field is the only thing that changes meaning', x, y + 42);
  }
}

/* Two memory cells and the registers, with an optional highlight for the
   cells a mode actually reads. */
function memoryStack(w, h, t, reveal, highlight) {
  var x = 22, y = 118, dy = 44;
  noStroke(); fill(90, 100, 116); textSize(11.5);
  text('memory', x, y - 8);
  cell(x, y, 'M[500]', '1200', highlight === 'direct' || highlight === 'indirect');
  cell(x, y + dy, 'M[1200]', '42', highlight === 'indirect');
  noStroke(); fill(90, 100, 116); textSize(11.5);
  text('registers', x + 150, y - 8);
  fill(20, 24, 31); textSize(12);
  text('R2 = 1200', x + 150, y + 16);
  text('R3 = 700', x + 150, y + 36);
  text('PC = 700', x + 150, y + 56);
  if (reveal && reveal > 0.5 && highlight) {
    noStroke(); fill(31, 94, 255); textSize(11.5);
    text(highlight === 'direct' ? 'this one is read' : 'both are read, in order', x + 150, y + 86);
  }
}

function cell(x, y, label, value, hot) {
  if (hot) { fill(31, 94, 255, 46); stroke(31, 94, 255); }
  else { fill(245, 247, 251); stroke(206, 212, 222); }
  strokeWeight(1);
  rect(x, y, 128, 26, 3);
  noStroke(); fill(20, 24, 31); textSize(12);
  text(label, x + 8, y + 17);
  fill(31, 94, 255); text(label === 'M[500]' ? value : value, x + 82, y + 17);
}

/* The mode's formula, revealed line by line. */
function formula(w, h, t, lines, idx) {
  var x = 22, y = 190, dy = 18;
  noStroke();
  for (var i = 0; i < lines.length; i++) {
    if (i / Math.max(1, lines.length) > t + 0.35) { continue; }
    var accent = (lines[i].indexOf('operand') === 0 || lines[i].indexOf('reads') === 0);
    fill(accent ? color(31, 94, 255) : color(20, 24, 31));
    textSize(accent ? 14 : 13);
    text(lines[i], x, y + i * dy);
  }
}

/* The summary table, one row per mode. */
function table(w, h, t) {
  var rows = [
    ['Immediate', 'none', '500', '0'],
    ['Direct', '500', '1200', '1'],
    ['Indirect', '1200', '42', '2'],
    ['Register indirect', '1200', '42', '1'],
    ['Indexed', '1200', '42', '1'],
    ['PC-relative', '1200', '42', '1']
  ];
  var x = 22, y = 66, dy = 26;
  noStroke(); fill(90, 100, 116); textSize(11);
  text('mode                 EA      operand   reads', x, y - 8);
  for (var i = 0; i < rows.length; i++) {
    if (i / rows.length > t + 0.25) { continue; }
    var ry = y + i * dy;
    fill(i === 1 ? color(31, 94, 255, 40) : color(245, 247, 251));
    stroke(i === 1 ? color(31, 94, 255) : color(206, 212, 222));
    strokeWeight(1);
    rect(x, ry, Math.min(340, w * 0.56), dy - 6, 3);
    noStroke(); fill(20, 24, 31); textSize(12);
    text(rows[i][0], x + 8, ry + 14);
    fill(70, 80, 96);
    text(rows[i][1], x + 150, ry + 14);
    fill(rows[i][2] === '42' ? color(31, 94, 255) : color(70, 80, 96));
    text(rows[i][2], x + 210, ry + 14);
    fill(70, 80, 96);
    text(rows[i][3], x + 280, ry + 14);
  }
}
