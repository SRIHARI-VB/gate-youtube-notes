/* From a shift register to the Johnson cycle.

   Four D flip-flops in a chain, with the complement of the last output fed back to
   the first input:

       D0 = Q3',  D1 = Q0,  D2 = Q1,  D3 = Q2

   Starting from 0000 the register walks the eight states

       0000 -> 1000 -> 1100 -> 1110 -> 1111 -> 0111 -> 0011 -> 0001 -> 0000

   which read as decimal 0, 8, 12, 14, 15, 7, 3, 1 and back. That is 2n states for
   n flip-flops, against n for the same register with a straight feedback wire.

   Two verified GATE CSE questions are this circuit: 2015 Set 1 Q.20 asks for the
   sequence and 2025 Set 1 Q.50 asks for the number of distinct states.

   Every state, count and cycle length shown here is recomputed in
   scripts/validate.py (check_sequential_circuits), not copied from this file. */

/* p5 alignment constants. p5 defines these itself; the fallbacks keep the lesson drawing
   where p5 is stubbed (the headless sketch test), and they carry p5's own values. */
if (typeof LEFT === 'undefined') { var LEFT = 'left'; }
if (typeof RIGHT === 'undefined') { var RIGHT = 'right'; }
if (typeof TOP === 'undefined') { var TOP = 'top'; }
if (typeof BOTTOM === 'undefined') { var BOTTOM = 'bottom'; }
if (typeof CENTER === 'undefined') { var CENTER = 'center'; }
if (typeof BOLD === 'undefined') { var BOLD = 'bold'; }
if (typeof NORMAL === 'undefined') { var NORMAL = 'normal'; }

var INK = [38, 44, 54];
var SOFT = [106, 116, 132];
var LINE = [206, 212, 222];
var ONE = [40, 122, 92];
var SEL = [176, 98, 30];
var MUTED = [148, 156, 168];

/* The eight states of the cycle, most significant bit first, plus the ninth entry which
   is the return to the start. */
var CYCLE = [
  [0, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0],
  [1, 1, 1, 1], [0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1], [0, 0, 0, 0]
];
var CYCLE_DECIMAL = [0, 8, 12, 14, 15, 7, 3, 1];

/* The second cycle, reached from any state outside the first one. Shown in the last step
   to explain why a Johnson counter needs a reset. */
var CYCLE_B = [
  [0, 0, 1, 0], [1, 0, 0, 1], [0, 1, 0, 0], [1, 0, 1, 0],
  [1, 1, 0, 1], [0, 1, 1, 0], [1, 0, 1, 1], [0, 1, 0, 1]
];

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

/* Four flip-flop boxes in a row, with the shift arrows above and the feedback wire below.
   `state` is the four bits after the clock edge; `prev` is the state before it, used to
   highlight which bits moved. */
function register(p, w, h, state, prev, opt) {
  opt = opt || {};
  var n = 4;
  var bw = 74, gap = 34;
  var total = n * bw + (n - 1) * gap;
  var x0 = (w - total) / 2;
  var y = 92, bh = 62;
  var i, x, bit, moved;

  /* shift arrows between the stages */
  for (i = 0; i < n - 1; i++) {
    x = x0 + i * (bw + gap) + bw;
    stroke(LINE[0], LINE[1], LINE[2]);
    strokeWeight(1.4);
    line(x + 2, y + bh / 2, x + gap - 2, y + bh / 2);
    line(x + gap - 8, y + bh / 2 - 4, x + gap - 2, y + bh / 2);
    line(x + gap - 8, y + bh / 2 + 4, x + gap - 2, y + bh / 2);
  }

  /* the stages */
  for (i = 0; i < n; i++) {
    x = x0 + i * (bw + gap);
    bit = state[i];
    moved = prev ? (prev[i] !== bit) : false;

    noStroke();
    fill(moved ? 250 : 246, moved ? 243 : 248, moved ? 234 : 251);
    rect(x, y, bw, bh);

    stroke(moved ? SEL[0] : LINE[0], moved ? SEL[1] : LINE[1], moved ? SEL[2] : LINE[2]);
    strokeWeight(moved ? 2.4 : 1.1);
    noFill();
    rect(x, y, bw, bh);

    noStroke();
    fill(SOFT[0], SOFT[1], SOFT[2]);
    textSize(11.5);
    textAlign(CENTER, TOP);
    text('D' + i, x + bw / 2, y + 6);

    noStroke();
    fill(bit ? ONE[0] : MUTED[0], bit ? ONE[1] : MUTED[1], bit ? ONE[2] : MUTED[2]);
    textSize(26);
    textStyle(BOLD);
    textAlign(CENTER, CENTER);
    text(String(bit), x + bw / 2, y + bh / 2 + 6);
    textStyle(NORMAL);
  }

  /* the feedback wire from Q3' back to D0 */
  var leftX = x0 + bw / 2;
  var rightX = x0 + (n - 1) * (bw + gap) + bw / 2;
  var bottomY = y + bh;
  var loopY = bottomY + 46;

  stroke(SEL[0], SEL[1], SEL[2]);
  strokeWeight(1.6);
  line(leftX, bottomY, leftX, loopY);
  line(rightX, bottomY, rightX, loopY);
  line(leftX, loopY, rightX, loopY);

  /* the inverter bubble on the wire */
  noStroke();
  fill(255, 255, 255);
  circle(rightX, loopY, 15);
  stroke(SEL[0], SEL[1], SEL[2]);
  strokeWeight(1.6);
  noFill();
  circle(rightX, loopY, 15);

  noStroke();
  fill(SEL[0], SEL[1], SEL[2]);
  textSize(12);
  textAlign(CENTER, TOP);
  text("Q3' fed back to D0", (leftX + rightX) / 2, loopY + 10);
  textAlign(LEFT, CENTER);
  text('Q3', rightX + 14, bottomY + 12);
}

/* The decimal reading of a state, printed to the right of the register. */
function decimalTag(w, h, value) {
  noStroke();
  fill(INK[0], INK[1], INK[2]);
  textSize(13);
  textAlign(CENTER, TOP);
  text('decimal ' + value, w / 2, 34);
}

/* A row of eight boxes showing how far round the cycle the register has travelled. */
function cycleStrip(w, h, reached, highlight) {
  var n = 8;
  var bw = 52, gap = 8;
  var total = n * bw + (n - 1) * gap;
  var x0 = (w - total) / 2;
  var y = h - 168;
  var i, x, on;

  for (i = 0; i < n; i++) {
    x = x0 + i * (bw + gap);
    on = i < reached;
    noStroke();
    fill(on ? 238 : 250, on ? 246 : 250, on ? 242 : 252);
    rect(x, y, bw, 40);
    stroke(on ? ONE[0] : LINE[0], on ? ONE[1] : LINE[1], on ? ONE[2] : LINE[2]);
    strokeWeight(i === highlight ? 2.4 : 1);
    noFill();
    rect(x, y, bw, 40);

    noStroke();
    fill(on ? INK[0] : MUTED[0], on ? INK[1] : MUTED[1], on ? INK[2] : MUTED[2]);
    textSize(13);
    textStyle(BOLD);
    textAlign(CENTER, CENTER);
    text(String(CYCLE_DECIMAL[i]), x + bw / 2, y + 20);
    textStyle(NORMAL);
  }

  noStroke();
  fill(SOFT[0], SOFT[1], SOFT[2]);
  textSize(11.5);
  textAlign(CENTER, TOP);
  text('the eight states of the cycle, as decimals', w / 2, y + 46);
}

window.LESSON = {
  steps: [
    {
      duration: 4200,
      caption: 'Four D flip-flops in a chain. Each one copies its left neighbour on every clock, so the register shifts. The twist is the feedback: the complement of the last output, not the output itself, is wired back to the first input.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 1: four D flip-flops, with Q3 complement fed back to D0');
        register(p, w, h, CYCLE[0], null, {});
        decimalTag(w, h, 0);
        note(w, h, "A straight wire from Q3 to D0 would make a ring counter; the bubble makes it a Johnson counter.");
      }
    },
    {
      duration: 4200,
      caption: 'Start at 0000. The last bit is 0, so its complement is 1, and that 1 shifts into the first stage while everything else moves one place right. The register now reads 1000, which is 8 in decimal.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 2: clock 1, the first 1 shifts in');
        register(p, w, h, CYCLE[1], CYCLE[0], {});
        decimalTag(w, h, 8);
        cycleStrip(w, h, 2, 1);
        note(w, h, "Each clock shifts one place and inserts the complement of the bit that is about to fall off the end.");
      }
    },
    {
      duration: 3800,
      caption: 'The block of ones keeps growing from the left: 1100 after the second clock, 1110 after the third. The last bit is still 0, so a 1 is still being inserted.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 3: clocks 2 and 3, the ones fill up');
        register(p, w, h, CYCLE[3], CYCLE[2], {});
        decimalTag(w, h, 14);
        cycleStrip(w, h, 4, 3);
        note(w, h, 'Decimal reading 12 then 14: the value climbs as the ones arrive.');
      }
    },
    {
      duration: 4200,
      caption: 'After the fourth clock the register is all ones, 1111, decimal 15. Now the last bit is 1, so its complement is 0 and the next thing inserted is a zero. The register has turned the corner.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 4: clock 4, all ones, and the insertion flips');
        register(p, w, h, CYCLE[4], CYCLE[3], {});
        decimalTag(w, h, 15);
        cycleStrip(w, h, 5, 4);
        note(w, h, 'This is the halfway point: from here the zeros eat into the block of ones.');
      }
    },
    {
      duration: 3800,
      caption: 'Zeros now shift in: 0111, then 0011, then 0001. The block of ones shrinks from the left exactly as it grew.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 5: clocks 5 to 7, the zeros eat the ones');
        register(p, w, h, CYCLE[7], CYCLE[6], {});
        decimalTag(w, h, 1);
        cycleStrip(w, h, 8, 7);
        note(w, h, 'Decimal 7, 3, 1. Each state differs from the previous one in exactly one bit, so the sequence is a Gray code.');
      }
    },
    {
      duration: 4600,
      caption: 'The eighth clock returns the register to 0000 and the cycle closes. Eight distinct states for four flip-flops, that is 2n. A ring counter with the same four flip-flops would have visited only four states.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 6: the cycle closes, 2n = 8 states');
        register(p, w, h, CYCLE[8], CYCLE[7], {});
        decimalTag(w, h, 0);
        cycleStrip(w, h, 8, -1);
        note(w, h, 'Sequence: 0, 8, 12, 14, 15, 7, 3, 1 and back to 0. This is GATE CSE 2015 Set 1 Q.20.');
      }
    },
    {
      duration: 4600,
      caption: 'Four flip-flops hold sixteen patterns, and the cycle uses eight. The other eight are not unreachable: they form a second cycle of their own, entered from any state outside the first one. That is why a Johnson counter needs a reset.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 7: the other eight patterns are a second cycle');
        register(p, w, h, CYCLE_B[0], null, {});
        decimalTag(w, h, 2);
        var y = h - 168;
        noStroke();
        fill(SOFT[0], SOFT[1], SOFT[2]);
        textSize(12);
        textAlign(CENTER, TOP);
        text('from 0010: 0010, 1001, 0100, 1010, 1101, 0110, 1011, 0101, and back to 0010',
             w / 2, y + 4);
        note(w, h, '8 + 8 = 16 patterns. Starting anywhere gives 8 distinct states, but which cycle you get depends on the start.');
      }
    },
    {
      duration: 5200,
      caption: 'So the answer to "how many distinct states" is 8 if you count the initial state and 7 if you exclude it. GATE CSE 2025 Set 1 Q.50 asked exactly this of a drawn four-flip-flop Johnson circuit and accepted both 7 and 8.',
      draw: function (p, w, h) {
        frame(w, h, 'Step 8: 8 including the initial state, 7 excluding it');
        register(p, w, h, CYCLE[0], null, {});
        decimalTag(w, h, 0);
        cycleStrip(w, h, 8, 0);
        note(w, h, 'Read the wording before you answer: 2n states in the cycle, 2n - 1 returns if the initial state is not counted.');
      }
    }
  ]
};
