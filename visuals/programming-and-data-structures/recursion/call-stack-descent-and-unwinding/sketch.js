/* Call stack: descent and unwinding.
   The program is GATE CSE 2024 Set 1 Q.19:
     void fX(){ char a; if ((a = getchar()) != '\n') fX(); if (a != '\n') putchar(a); }
   Every character of the input 1234 (then a newline) is read by one activation into its own local a,
   so five frames exist at the deepest point and the characters print on the way back up: 4321.
   The counts are recomputed in scripts/validate.py (check_recursion). */
window.LESSON = {
  steps: [
    {
      duration: 3000,
      caption: 'One function, four characters and a newline. Each call reads exactly one character into its own local a, and nothing is printed yet - the putchar sits after the recursive call.',
      draw: function (p, w, h) {
        ink();
        head('fX reads one character per call', 28, 34);
        textSize(12.5); fill(90, 100, 116); noStroke();
        text("void fX(){ char a; if ((a = getchar()) != '\\n') fX(); if (a != '\\n') putchar(a); }", 28, 60);
        inputRow(w, 120, -1);
        note('The input is 1234 followed by a newline. Four calls will recurse; the fifth reads the newline and stops.', 28, h - 30);
      }
    },
    {
      duration: 2600,
      caption: 'The first call pushes its frame and reads 1. Because 1 is not a newline, it calls fX again before it can reach its putchar, so its frame stays on the stack.',
      draw: function (p, w, h) {
        ink();
        head('Frame 1 reads 1 and calls again', 28, 34);
        stack(w, h, 1, -1, 0);
        output(w, '');
        note('A frame holds the local a, the return address and the saved registers. Frame 1 holds a = 1 and is waiting.', 28, h - 30);
      }
    },
    {
      duration: 3600,
      caption: 'Each new call pushes one more frame: a = 2, then a = 3, then a = 4. Four frames are now alive at once, each holding a different character, and none has printed anything.',
      draw: function (p, w, h) {
        ink();
        head('Four frames alive, one character each', 28, 34);
        var k = 1 + Math.min(3, Math.floor(Math.min(1, Math.max(0, p)) * 3 + 0.0001));
        stack(w, h, k, -1, 0);
        output(w, '');
        note('Depth grows with every call: ' + k + ' frame(s) on the stack, ' + k + ' character(s) remembered.', 28, h - 30);
      }
    },
    {
      duration: 3200,
      caption: 'The fifth call reads the newline. Both tests fail, so it neither recurses nor prints: it returns immediately and its frame is popped. This is the base case.',
      draw: function (p, w, h) {
        ink();
        head('Frame 5 reads the newline and returns', 28, 34);
        stack(w, h, 5, 4, 0);
        output(w, '');
        textSize(12.5); fill(180, 90, 31); noStroke();
        text('a = newline: no recursive call, no putchar', 28, h - 52);
        note('Four frames are still waiting behind it, each holding a character it has not printed yet.', 28, h - 30);
      }
    },
    {
      duration: 2600,
      caption: 'Now the unwinding starts. The frame that read 4 resumes after its recursive call, its second test passes, and it prints 4. Then it is popped.',
      draw: function (p, w, h) {
        ink();
        head('Unwinding: frame 4 prints 4', 28, 34);
        stack(w, h, 4, 3, 0);
        output(w, '4');
        note('The deepest frame with a character is the first to print, which is why the output starts with the last input character.', 28, h - 30);
      }
    },
    {
      duration: 3000,
      caption: 'Frame 3 prints 3 and frame 2 prints 2, in that order. Each frame still holds its own a, so each prints the character it read - the stack is doing the remembering.',
      draw: function (p, w, h) {
        ink();
        head('Frames 3 and 2 print on their way out', 28, 34);
        var k = Math.min(1, Math.max(0, p)) < 0.5 ? 3 : 2;
        stack(w, h, k, k - 1, 0);
        output(w, k === 3 ? '43' : '432');
        note('Order of the pops: 4, then 3, then 2, then 1 - the reverse of the order of the calls.', 28, h - 30);
      }
    },
    {
      duration: 2800,
      caption: 'The first frame finally prints 1 and the stack is empty. Five calls, four prints: the answer to the paper question is 4321, not 1234.',
      draw: function (p, w, h) {
        ink();
        head('All frames popped: the output is 4321', 28, 34);
        stack(w, h, 0, -1, 0);
        output(w, '4321');
        textSize(13); fill(31, 94, 255); noStroke();
        text('5 invocations, 4 putchar calls, output 4321', 28, h - 52);
        note('The frame that read the newline printed nothing, which is why the counts differ by one.', 28, h - 30);
      }
    },
    {
      duration: 3400,
      caption: 'Move the putchar before the recursive call and the same five calls print 1234 instead: the work now happens on the descent. One line decides the whole answer.',
      draw: function (p, w, h) {
        ink();
        head('Print before the call: 1234', 28, 34);
        textSize(12.5); fill(90, 100, 116); noStroke();
        text("if ((a = getchar()) != '\\n') { if (a != '\\n') putchar(a); fX(); }", 28, 60);
        inputRow(w, 120, -1);
        output(w, '1234');
        textSize(12.5); fill(20, 24, 31); noStroke();
        text('Same recursion, same depth, opposite output order.', 28, h - 52);
        note('GATE offers both orders as options, so the position of the print is the question.', 28, h - 30);
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
function head(t, x, y) { textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function note(t, x, y) { textSize(12.5); fill(90, 100, 116); noStroke(); text(t, x, y); }

var CHARS = ['1', '2', '3', '4', 'newline'];

/* A row of the five input characters; hi marks the character just read. */
function inputRow(w, y, hi) {
  var n = 5, cw = 56, gap = 10;
  var total = n * cw + (n - 1) * gap;
  var x0 = 28;
  for (var i = 0; i < n; i++) {
    var x = x0 + i * (cw + gap);
    var on = i === hi;
    stroke(on ? color(31, 94, 255) : color(214, 220, 230));
    strokeWeight(on ? 2.5 : 1);
    fill(on ? color(232, 238, 255) : color(250, 251, 253));
    rect(x, y, cw, 44, 7);
    noStroke(); fill(20, 24, 31); textSize(13);
    text(CHARS[i], x + 8, y + 27);
  }
  noStroke(); fill(120, 128, 140); textSize(11);
  text('input', x0, y - 8);
}

/* The stack: frame i is drawn bottom-up, so frame 1 is the lowest box. */
function stack(w, h, count, justPopped, justPushed) {
  var x = 28, bw = Math.min(300, w - 360), bh = 40, gap = 8;
  var baseY = h - 90;
  textSize(11); fill(120, 128, 140); noStroke();
  text('call stack', x, baseY - count * (bh + gap) - 14);
  for (var i = 0; i < count; i++) {
    var y = baseY - (i + 1) * (bh + gap);
    var on = i === justPushed;
    stroke(on ? color(31, 94, 255) : color(214, 220, 230));
    strokeWeight(on ? 2.5 : 1);
    fill(on ? color(232, 238, 255) : color(250, 251, 253));
    rect(x, y, bw, bh, 7);
    noStroke(); fill(20, 24, 31); textSize(12.5);
    text('frame ' + (i + 1) + '   a = ' + CHARS[i], x + 12, y + 25);
  }
  if (count === 0) {
    stroke(color(214, 220, 230)); strokeWeight(1);
    line(x, baseY, x + bw, baseY);
    noStroke(); fill(120, 128, 140); textSize(12);
    text('empty', x + 8, baseY - 8);
  }
  textSize(11.5); fill(90, 100, 116); noStroke();
  text('frames alive: ' + count, x, baseY + 22);
}

/* The output so far, drawn as characters in the order they were printed. */
function output(w, s) {
  var x = Math.min(360, w - 250), y = 120, cw = 40, gap = 6;
  textSize(11); fill(120, 128, 140); noStroke();
  text('output', x, y - 10);
  for (var i = 0; i < s.length; i++) {
    var bx = x + i * (cw + gap);
    stroke(color(31, 94, 255)); strokeWeight(2);
    fill(color(232, 238, 255));
    rect(bx, y, cw, 44, 7);
    noStroke(); fill(20, 24, 31); textSize(15);
    text(s.charAt(i), bx + 14, y + 28);
  }
  if (s.length === 0) {
    textSize(12); fill(120, 128, 140); noStroke();
    text('nothing printed yet', x, y + 28);
  }
  textSize(11.5); fill(90, 100, 116); noStroke();
  text('printed: ' + s.length + ' of 4', x, y + 68);
}
