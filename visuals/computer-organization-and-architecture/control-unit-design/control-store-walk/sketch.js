/* From opcode to microprogram: walking a control store, for the Control Unit topic.

   The picture is fixed for the whole lesson:

     a control store of 8 visible words, each 10 bits wide
     word 0 and 1 hold the shared fetch routine, word 2 is its END
     word 4 and 5 hold the ADD routine, word 5 is its END
     the ten bits drive ten named control signals

   The ten signals, in bit order, are
     0 PCout   1 MARin   2 MEMread   3 MDRout   4 IRin
     5 PCinc   6 R2out   7 R1in      8 ALUadd   9 END

   Every bit pattern, width and address shown here is listed in lesson.json
   and recomputed in scripts/validate.py (check_control_unit_design),
   not copied from this file. */

var SIG = ['PCout', 'MARin', 'MEMread', 'MDRout', 'IRin', 'PCinc', 'R2out', 'R1in', 'ALUadd', 'END'];

var WORDS = {
  0: { bits: '1110000000', action: 'MAR <- PC, and the memory is told to read' },
  1: { bits: '0001110000', action: 'IR <- MDR, and PC <- PC + 1' },
  2: { bits: '0000000001', action: 'END: jump to the address the opcode maps to' },
  4: { bits: '0000001110', action: 'R1 <- R1 + R2' },
  5: { bits: '0000000001', action: 'END: branch back to fetch at address 0' }
};

var VERT = {
  0: '01 01 01 0 0',
  1: '10 10 00 1 0',
  2: '00 00 00 0 1',
  4: '11 11 10 0 0',
  5: '00 00 00 0 1'
};

window.LESSON = {
  steps: [
    {
      duration: 5600,
      caption: 'A microprogrammed control unit replaces the signal trees with a memory. Each word of the control store holds one control word: the bits of that word are the control signals for one micro-operation. Here the store is eight words of ten bits, the fetch routine sits in words 0 to 2, and the ADD routine in words 4 and 5. Nothing has been read yet.',
      draw: function (p, w, h) {
        ink();
        head('A control store is a memory of control words', 22, 28);
        store(w, h, -1, 1);
        note('Each row is one microinstruction; each column of the row is one control signal.', 22, h - 14);
      }
    },
    {
      duration: 5200,
      caption: 'The control address register points at word 0 and the word is read out. Its bits are 1, 1, 1 in the first three positions, so PCout, MARin and MEMread are asserted: the program counter is copied to the memory address register and the memory is told to read. The other seven signals stay at 0, which is what leaves the rest of the datapath alone.',
      draw: function (p, w, h) {
        ink();
        head('Word 0: MAR <- PC, and a memory read', 22, 28);
        store(w, h, 0, 1);
        signals(w, h, 0, 1);
        note(WORDS[0].action, 22, h - 14);
      }
    },
    {
      duration: 5000,
      caption: 'The address register increments to word 1. Now MDRout, IRin and PCinc are asserted: the word fetched from memory goes into the instruction register and the program counter advances past it. These two words are the whole fetch, and they are the same for every instruction, because no opcode has been looked at yet.',
      draw: function (p, w, h) {
        ink();
        head('Word 1: IR <- MDR, and PC <- PC + 1', 22, 28);
        store(w, h, 1, 1);
        signals(w, h, 1, 1);
        note(WORDS[1].action, 22, h - 14);
      }
    },
    {
      duration: 6000,
      caption: 'Word 2 holds only the END bit. That bit says the next address is not the next word: the opcode now in the instruction register is mapped to the start of its routine. A 4-bit opcode with two zero bits inserted below it gives 4 times the opcode, so opcode 0001 maps to address 4. The jump is wiring, not a lookup table.',
      draw: function (p, w, h) {
        ink();
        head('Word 2: END, and the opcode maps to address 4', 22, 28);
        store(w, h, 2, 1);
        signals(w, h, 2, 1);
        mapping(w, h, Math.min(1, p * 1.3));
        note('start address = 4 x opcode, so opcode 0001 enters its routine at word 4.', 22, h - 14);
      }
    },
    {
      duration: 5000,
      caption: 'The ADD routine runs. Word 4 asserts R2out, ALUadd and R1in: the second operand is put on the bus, the ALU adds, and the result is written back to the first register. The routine has no idea that it is an ADD microprogram - it is only a word whose bits happen to name those three signals.',
      draw: function (p, w, h) {
        ink();
        head('Word 4: the ADD routine, R1 <- R1 + R2', 22, 28);
        store(w, h, 4, 1);
        signals(w, h, 4, 1);
        note(WORDS[4].action, 22, h - 14);
      }
    },
    {
      duration: 4800,
      caption: 'Word 5 is an END again, this time branching back to address 0. That closes the loop: the next instruction is fetched by the same two words, so one copy of the fetch serves the whole instruction set. A store of 8 words and 10 bits is 80 bits of control, and the same hardware executes every instruction the store describes.',
      draw: function (p, w, h) {
        ink();
        head('Word 5: END, back to fetch at 0', 22, h * 0.02 + 28);
        store(w, h, 5, 1);
        backArrow(w, h, Math.min(1, p * 1.3));
        note('The fetch is shared, so 16 instructions would cost 3 words of fetch, not 48.', 22, h - 14);
      }
    },
    {
      duration: 6200,
      caption: 'The same two fetch words, written vertically. The three bus sources share one 2-bit field, the three destinations share another, memory-read and ALU-add share a third, and only PCinc and END keep a bit each: eight bits instead of ten. The saving is real but small, and it costs a decoder in the path of every encoded field - which is exactly the horizontal against vertical trade.',
      draw: function (p, w, h) {
        ink();
        head('The same words written vertically: 8 bits, not 10', 22, 28);
        vertical(w, h, Math.min(1, p * 1.3));
        note('Two bits saved, one decoder added: the whole horizontal-against-vertical trade in one row.', 22, h - 14);
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

function cell(x, y, w, h, label, hot) {
  if (hot) { fill(31, 94, 255, 46); stroke(31, 94, 255); }
  else { fill(245, 247, 251); stroke(206, 212, 222); }
  strokeWeight(1);
  rect(x, y, w, h, 3);
  noStroke(); fill(20, 24, 31); textSize(12);
  text(label, x + 6, y + h / 2 + 4);
}

function store(w, h, active, t) {
  var x = 22, y = 46, rowH = 34, cw = 19;
  noStroke(); fill(90, 100, 116); textSize(11);
  text('control store', x, y - 6);
  text('address', x + 4, y - 6);
  var addrs = [0, 1, 2, 3, 4, 5, 6, 7];
  for (var i = 0; i < addrs.length; i++) {
    var a = addrs[i];
    var ry = y + i * rowH;
    var word = WORDS[a];
    var hot = (a === active);
    fill(hot ? color(31, 94, 255, 30) : color(250, 251, 253));
    stroke(hot ? color(31, 94, 255) : color(226, 230, 238));
    strokeWeight(1);
    rect(x, ry, 336, rowH - 4, 3);
    noStroke(); fill(20, 24, 31); textSize(12);
    text(String(a), x + 8, ry + 19);
    for (var b = 0; b < 10; b++) {
      var bit = word ? word.bits.charAt(b) : '0';
      var bx = x + 34 + b * cw;
      fill(bit === '1' ? color(31, 94, 255) : color(120, 130, 146));
      text(bit, bx, ry + 19);
    }
    fill(70, 80, 96); textSize(10.5);
    var tag = word ? (a <= 2 ? 'fetch' : 'ADD') : 'spare';
    text(tag, x + 246, ry + 19);
  }
  noStroke(); fill(90, 100, 116); textSize(10.5);
  text('bit order: ' + SIG.join(' '), x, y + addrs.length * rowH + 12);
}

function signals(w, h, addr, t) {
  var word = WORDS[addr];
  if (!word) { return; }
  var x = 392, y = 46, dy = 30, cw = 196;
  noStroke(); fill(90, 100, 116); textSize(11);
  text('the bits of word ' + addr + ' on the control lines', x, y - 6);
  for (var i = 0; i < 10; i++) {
    var bit = word.bits.charAt(i);
    var col = i < 5 ? 0 : 1;
    var row = i % 5;
    var bx = x + col * cw;
    var by = y + row * dy;
    if (bit === '1') {
      fill(31, 94, 255, 46); stroke(31, 94, 255);
    } else {
      fill(245, 247, 251); stroke(206, 212, 222);
    }
    strokeWeight(1);
    rect(bx, by, 176, dy - 8, 3);
    noStroke(); fill(20, 24, 31); textSize(11.5);
    text(SIG[i] + ' = ' + bit, bx + 8, by + 15);
  }
  noStroke(); fill(90, 100, 116); textSize(11);
  text('the asserted signals:', x, y + 5 * dy + 4);
  fill(31, 94, 255); textSize(12.5);
  text(word.action, x, y + 5 * dy + 22);
}

function mapping(w, h, t) {
  var x = 392, y = 236;
  noStroke(); fill(90, 100, 116); textSize(11);
  text('opcode 0001 in the IR, mapped to an address', x, y);
  if (t > 0.2) {
    fill(20, 24, 31); textSize(13);
    text('opcode = 0001 = 1', x, y + 22);
  }
  if (t > 0.5) {
    text('insert two 0 bits below it', x, y + 44);
    fill(31, 94, 255); textSize(15);
    text('0001 00 = 4', x, y + 70);
  }
  if (t > 0.8) {
    noStroke(); fill(70, 80, 96); textSize(11.5);
    text('so each routine owns 4 words: 0, 4, 8, 12, ...', x, y + 94);
  }
}

function backArrow(w, h, t) {
  var x = 380, y = 46 + 5 * 34 + 18;
  stroke(31, 94, 255); strokeWeight(2);
  line(x + 40, y, x + 40 - 20 * t, y);
  noStroke(); fill(31, 94, 255); textSize(11.5);
  text('END branches back to address 0', x - 40, y - 8);
}

function vertical(w, h, t) {
  var x = 22, y = 58, rowH = 40;
  var heads = ['sources', 'destinations', 'MEMread / ALUadd', 'PCinc', 'END'];
  var widths = [2, 2, 2, 1, 1];
  noStroke(); fill(90, 100, 116); textSize(11);
  text('address', x, y - 8);
  var cx = x + 56;
  for (var f = 0; f < widths.length; f++) {
    text(heads[f], cx, y - 8);
    cx += widths[f] * 22 + 16;
  }
  var addrs = [0, 1, 2, 4, 5];
  for (var i = 0; i < addrs.length; i++) {
    var a = addrs[i];
    var ry = y + i * rowH;
    fill(250, 251, 253); stroke(226, 230, 238); strokeWeight(1);
    rect(x, ry, Math.min(620, w - 44), rowH - 6, 3);
    noStroke(); fill(20, 24, 31); textSize(12);
    text(String(a), x + 10, ry + 22);
    var parts = VERT[a].split(' ');
    var bx = x + 56;
    for (var k = 0; k < parts.length; k++) {
      var bw = (k < 3 ? 2 : 1) * 22;
      fill(31, 94, 255, 34); stroke(31, 94, 255); strokeWeight(1);
      rect(bx, ry + 6, bw, rowH - 18, 3);
      noStroke(); fill(20, 24, 31); textSize(12);
      text(parts[k], bx + 4, ry + 22);
      bx += bw + 16;
    }
  }
  if (t > 0.6) {
    noStroke(); fill(70, 80, 96); textSize(11.5);
    text('field widths: 2 + 2 + 2 + 1 + 1 = 8 bits, against 10 for the horizontal word.', x, y + addrs.length * rowH + 8);
    text('each encoded field needs a decoder, and can name only one of its signals at a time.', x, y + addrs.length * rowH + 26);
  }
}
