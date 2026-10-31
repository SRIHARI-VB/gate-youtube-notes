/* One 5-stage pipeline, four situations, drawn as a space-time diagram.

   The picture is fixed for the whole lesson, and every figure is listed in
   lesson.json and recomputed in scripts/validate.py
   (check_instruction_pipelining_and_hazards) rather than derived from this file:

     stages IF OF EX MA RW, one cell per cycle
     four instructions, nothing in their way           : 8 columns  (5 + 4 - 1)
     a RAW pair with no forwarding, two bubbles        : 10 columns (8 + 2)
     the same four with EX-to-EX forwarding            : 8 columns
     LOAD R1,[A] then ADD R2,R1,R3, one bubble         : 7 columns  (5 + 2 - 1 + 1)
     I1 I2 I3(branch to I6) I4 I5 I6, taken, 2 flushed : 10 columns
     three instructions, one load-use bubble           : 8 columns  (5 + 3 - 1 + 1)

   The cells are written out by hand so that the drawing cannot silently
   disagree with the arithmetic: each row is an explicit list of what that
   instruction is doing in each cycle. */

var STAGES = ['IF', 'OF', 'EX', 'MA', 'RW'];
var COLS = 10;

var C_IF = [206, 220, 238];
var C_OF = [188, 208, 232];
var C_EX = [198, 216, 240];
var C_MA = [214, 232, 214];
var C_RW = [226, 236, 226];
var C_STALL = [246, 214, 156];
var C_FLUSH = [240, 200, 200];
var C_DEAD = [240, 240, 240];

function ink() {
  background(255);
  stroke(210);
  strokeWeight(1);
  fill(40);
}

function head(t) { fill(28); textSize(16); textStyle(BOLD); textAlign(LEFT, TOP); text(t, 20, 14); textStyle(NORMAL); }

function note(t, y) { fill(74, 82, 96); textSize(12.5); textAlign(LEFT, TOP); text(t, 20, y); }

function stageColour(name) {
  if (name === 'IF') { return C_IF; }
  if (name === 'OF') { return C_OF; }
  if (name === 'EX') { return C_EX; }
  if (name === 'MA') { return C_MA; }
  if (name === 'RW') { return C_RW; }
  return C_STALL;
}

function geom(w, rows) {
  var left = 96;
  var top = 56;
  var cw = (w - left - 18) / COLS;
  var rh = Math.min(25, (236 - top) / Math.max(rows, 1));
  return { left: left, top: top, cw: cw, rh: rh };
}

function grid(g, names, cols) {
  var r, c;
  fill(96); textSize(10.5); textAlign(LEFT, TOP);
  for (c = 0; c < cols; c++) {
    text(String(c + 1), g.left + c * g.cw + 2, g.top - 15);
  }
  for (r = 0; r < names.length; r++) {
    var y = g.top + r * g.rh;
    fill(58); textSize(11); textAlign(LEFT, TOP);
    text(names[r], 4, y + 3);
    for (c = 0; c < cols; c++) {
      stroke(216); strokeWeight(1); noFill();
      rect(g.left + c * g.cw, y, g.cw, g.rh);
      noStroke();
    }
  }
  stroke(216);
}

/* cells: one entry per cycle, from the instruction's first cycle. Each entry is
   a stage name, 'stall', 'flush' or 'dead'. Cycles before the start stay empty. */
function row(g, r, start, cells) {
  var y = g.top + r * g.rh;
  for (var i = 0; i < cells.length; i++) {
    var c = start + i;
    if (c >= COLS) { break; }
    var x = g.left + c * g.cw;
    var cell = cells[i];
    if (cell === 'flush') {
      noStroke(); fill(C_FLUSH[0], C_FLUSH[1], C_FLUSH[2]);
      rect(x, y, g.cw, g.rh);
      stroke(178, 96, 96); strokeWeight(1);
      line(x + 3, y + 3, x + g.cw - 3, y + g.rh - 3);
      noStroke();
    } else if (cell === 'dead') {
      noStroke(); fill(C_DEAD[0], C_DEAD[1], C_DEAD[2]);
      rect(x, y, g.cw, g.rh);
    } else {
      var col = stageColour(cell);
      noStroke(); fill(col[0], col[1], col[2]);
      rect(x, y, g.cw, g.rh);
      fill(56); textSize(10); textAlign(LEFT, TOP);
      text(cell === 'stall' ? 'stall' : cell, x + 2, y + 4);
      noStroke();
    }
  }
  stroke(216);
}

function arrow(g, r1, c1, r2, c2, colour) {
  var x1 = g.left + (c1 + 0.5) * g.cw, y1 = g.top + (r1 + 0.5) * g.rh;
  var x2 = g.left + (c2 + 0.5) * g.cw, y2 = g.top + (r2 + 0.5) * g.rh;
  stroke(colour[0], colour[1], colour[2]); strokeWeight(1.5);
  line(x1, y1, x2, y2);
  var a = Math.atan2(y2 - y1, x2 - x1);
  var hx = x2 - 7 * Math.cos(a), hy = y2 - 7 * Math.sin(a);
  noStroke(); fill(colour[0], colour[1], colour[2]);
  beginShape();
  vertex(x2, y2);
  vertex(hx - 3 * Math.sin(a), hy + 3 * Math.cos(a));
  vertex(hx + 3 * Math.sin(a), hy - 3 * Math.cos(a));
  endShape(CLOSE);
  stroke(216);
}

function legend(y) {
  var items = [['IF', C_IF], ['OF', C_OF], ['EX', C_EX], ['MA', C_MA], ['RW', C_RW],
               ['bubble', C_STALL], ['flushed', C_FLUSH]];
  var x = 20;
  for (var i = 0; i < items.length; i++) {
    noStroke(); fill(items[i][1][0], items[i][1][1], items[i][1][2]);
    rect(x, y, 10, 10);
    fill(70); textSize(10.5); textAlign(LEFT, TOP);
    text(items[i][0], x + 13, y);
    x += 15 + textWidth(items[i][0]);
    stroke(216);
  }
}

var FULL = ['IF', 'OF', 'EX', 'MA', 'RW'];

window.LESSON = {
  steps: [
    {
      duration: 5000,
      caption: 'The grid is the whole topic. Each row is one instruction, each column one clock cycle, and an instruction shifts one column right as it moves one stage down. Four instructions on the five stages with nothing in their way need 5 + 4 - 1 = 8 columns: the first finishes at the end of cycle 5 and one more finishes every cycle after that.',
      draw: function (p, w, h) {
        ink();
        head('Four instructions, five stages, no hazards: 8 columns');
        var g = geom(w, 4);
        grid(g, ['I1', 'I2', 'I3', 'I4'], 8);
        for (var r = 0; r < 4; r++) { row(g, r, r, FULL); }
        legend(200);
        note('The first five cycles are the fill: only I1 is complete at the end of cycle 5.', 224);
        note('Columns = k + n - 1 = 5 + 4 - 1 = 8. Time = columns x cycle time.', 246);
      }
    },
    {
      duration: 5200,
      caption: 'Now a real dependence. ADD R1, R2, R3 writes R1 at the end of its RW stage, cycle 5. SUB R4, R1, R5 wants to read R1 in its OF stage, cycle 3 - two cycles before the value exists. The arrow points backwards in time, and that is exactly what a data hazard is: the possibility of executing an instruction with the wrong data.',
      draw: function (p, w, h) {
        ink();
        head('A RAW hazard: the reader wants the value before it exists');
        var g = geom(w, 3);
        grid(g, ['ADD R1', 'SUB R1', 'I3'], 8);
        row(g, 0, 0, FULL);
        row(g, 1, 1, FULL);
        row(g, 2, 2, FULL);
        arrow(g, 1, 2, 0, 4, [190, 90, 90]);
        legend(200);
        note('ADD writes R1 in cycle 5; SUB reads R1 in cycle 3. The arrow runs right to left.', 224);
        note('Nothing can move a value backwards in time, so something has to give.', 246);
      }
    },
    {
      duration: 5400,
      caption: 'The cheapest repair is to wait. The interlock holds the front of the pipeline and inserts two bubbles, so the SUB reaches its EX stage in cycle 6, after the value has been written in cycle 5. The four instructions now need 10 columns instead of 8: two cycles of throughput paid for one dependence.',
      draw: function (p, w, h) {
        ink();
        head('Without forwarding: two bubbles, 8 columns become 10');
        var g = geom(w, 4);
        grid(g, ['ADD R1', 'SUB R1', 'I3', 'I4'], 10);
        row(g, 0, 0, FULL);
        row(g, 1, 1, ['IF', 'OF', 'stall', 'stall', 'EX', 'MA', 'RW']);
        row(g, 2, 2, ['IF', 'OF', 'stall', 'stall', 'EX', 'MA', 'RW']);
        row(g, 3, 3, ['IF', 'OF', 'stall', 'stall', 'EX', 'MA', 'RW']);
        legend(222);
        note('Two amber cells in each later row: the bubbles the interlock inserts while R1 is written.', 246);
        note('A bubble writes no register and touches no memory, so the answer is still correct.', 268);
      }
    },
    {
      duration: 5200,
      caption: 'Forwarding removes both bubbles. The ALU result is ready at the end of the ADD stage EX in cycle 3, and the SUB needs it at the start of its own EX, also cycle 3. A wire from the EX/MEM register to the EX input carries it across, so the diagram is back to 8 columns with no stall at all.',
      draw: function (p, w, h) {
        ink();
        head('With EX-to-EX forwarding: zero bubbles, 8 columns');
        var g = geom(w, 4);
        grid(g, ['ADD R1', 'SUB R1', 'I3', 'I4'], 8);
        for (var r = 0; r < 4; r++) { row(g, r, r, FULL); }
        arrow(g, 0, 2, 1, 2, [70, 130, 90]);
        legend(200);
        note('Both instructions are in EX in cycle 3, so the value is passed sideways from one to the other.', 224);
        note('The forwarding unit compares the destination register in EX/MEM with the sources in EX.', 246);
      }
    },
    {
      duration: 5600,
      caption: 'One pair survives forwarding. LOAD R1, [A] produces its word at the end of its MA stage, cycle 4, but the ADD behind it would need the word at the start of its EX stage in cycle 4. The wire exists and still cannot help, because the word is not there yet. One bubble is inserted, the ADD executes in cycle 5, and the pair takes 7 columns. That single stall is the only one forwarding leaves behind.',
      draw: function (p, w, h) {
        ink();
        head('The load-use pair: exactly one bubble, 7 columns');
        var g = geom(w, 2);
        grid(g, ['LOAD R1', 'ADD R1'], 8);
        row(g, 0, 0, FULL);
        row(g, 1, 1, ['IF', 'OF', 'stall', 'EX', 'MA', 'RW']);
        arrow(g, 0, 3, 1, 3, [70, 130, 90]);
        legend(170);
        note('The MA stage of the load ends in cycle 4, which is the cycle the consumer wanted the word.', 194);
        note('Two instructions plus one bubble: 5 + 2 - 1 + 1 = 7 columns.', 216);
        note('The MEM-to-EX path still saves the second bubble that a register-file read would have cost.', 238);
      }
    },
    {
      duration: 5600,
      caption: 'Control hazards are worse, because they waste whole instructions. I3 is a branch to I6. While I3 passes through OF and EX the fetch unit has already brought in I4 and I5, and both are wrong. They are crossed out in red, the fetch of I6 starts in cycle 6, and the program ends in cycle 10 instead of the 8 that four useful instructions would need.',
      draw: function (p, w, h) {
        ink();
        head('A taken branch: two fetched instructions are flushed');
        var g = geom(w, 6);
        grid(g, ['I1', 'I2', 'I3 br', 'I4', 'I5', 'I6'], 10);
        row(g, 0, 0, FULL);
        row(g, 1, 1, FULL);
        row(g, 2, 2, FULL);
        row(g, 3, 3, ['flush', 'flush']);
        row(g, 4, 4, ['flush']);
        row(g, 5, 5, FULL);
        legend(262);
        note('The branch resolves at the end of I3 stage EX in cycle 5, so the two behind it are cancelled.', 286);
        note('Penalty = 2 cycles here; more than 20 at modern pipeline depths.', 308);
      }
    },
    {
      duration: 5400,
      caption: 'Every number in the lesson is a column count, and every GATE question in this topic is that count. Four instructions with no hazard: 8 columns. The same four with a two-bubble RAW pair: 10. A load-use pair: 7. A six-instruction program with a taken branch: 10. Convert columns to time by multiplying by the cycle time, which is the slowest stage plus one latch delay.',
      draw: function (p, w, h) {
        ink();
        head('The counts, and the CPI model built on them');
        var rows = [
          ['4 instructions, 5 stages, no hazard', '5 + 4 - 1 = 8 columns'],
          ['the same 4 with a 2-bubble RAW pair', '8 + 2 = 10 columns'],
          ['LOAD R1, [A] then ADD R2, R1, R3', '5 + 2 - 1 + 1 = 7 columns'],
          ['I1 I2 I3(br to I6) I4 I5 I6, taken', '10 columns, 2 flushed'],
          ['CPI with stalls', 'CPI = 1 + stall rate x stall penalty'],
          ['speed-up at one clock', 'ratio of the two CPIs']
        ];
        for (var i = 0; i < rows.length; i++) {
          var y = 54 + i * 32;
          fill(60); textSize(12); textAlign(LEFT, TOP);
          text(rows[i][0], 20, y);
          fill(30); textSize(12); textAlign(LEFT, TOP);
          text(rows[i][1], 322, y);
          stroke(228); strokeWeight(1);
          line(20, y + 25, 460, y + 25);
          noStroke();
        }
        note('Cycle time = max(stage delay) + latch delay, so time = columns x cycle time.', 260);
        note('2021 Set 1 Q.53 is 104 columns of 165 ns; 2013 Q.45 is 15 columns of 11 ns.', 282);
      }
    },
    {
      duration: 5200,
      caption: 'The exam rarely asks for the formula; it asks for a number the diagram produces. Read the stage in which the branch or the dependence is decided, count how many instructions were already in flight behind it, and count the columns. Then multiply by the cycle time, or convert to CPI with 1 + stall rate x stall penalty.',
      draw: function (p, w, h) {
        ink();
        head('The three steps that answer every question in this topic');
        var rows = [
          ['1', 'Find the cycle in which the value is produced or the branch is decided.'],
          ['2', 'Count the instructions already in flight behind that point: those are the wasted cycles.'],
          ['3', 'Count the columns of the diagram and multiply by the cycle time.'],
          ['', ''],
          ['Forwarding', 'moves the value, not the instruction: it removes the bubbles, never the dependence.'],
          ['Prediction', 'removes the flush when it is right and pays the full penalty when it is wrong.']
        ];
        for (var i = 0; i < rows.length; i++) {
          var y = 52 + i * 34;
          fill(150); textSize(13); textAlign(LEFT, TOP);
          text(rows[i][0], 20, y);
          fill(50); textSize(12); textAlign(LEFT, TOP);
          text(rows[i][1], 46, y);
        }
        note('Cycle time = max(stage delay) + latch delay. Stalls add to the column count, one per bubble.', 272);
      }
    }
  ]
};
