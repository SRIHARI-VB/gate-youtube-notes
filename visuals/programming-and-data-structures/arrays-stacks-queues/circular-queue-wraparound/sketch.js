/* Circular queue in an array of n = 5 slots, capacity n - 1 = 4.
   Convention: both indices start at 0, rear is the index of the next free slot, one slot is
   sacrificed, empty is front == rear, full is (rear + 1) % n == front, and the element count is
   (rear - front + n) % n. This is the convention of GATE CSE 2012 Q.35 (option A).

   The six operations animated here are
     enqueue 10, 20, 30, 40 | dequeue twice | enqueue 50, 60
   and every index, count and full/empty test below is recomputed in scripts/validate.py. */
window.LESSON = {
  steps: [
    {
      duration: 2600,
      caption: 'Five slots, indices 0 to 4, so the capacity is n - 1 = 4. Both indices start at 0: front == rear means empty, and no value has been written yet.',
      draw: function (p, w, h) {
        state(w, h, { cells: [null, null, null, null, null], front: 0, rear: 0 },
          'empty: front == rear == 0', -1);
        note('The queue can never hold 5 elements here: one slot is sacrificed so that full and empty stay distinguishable.', 24, h - 26);
      }
    },
    {
      duration: 2400,
      caption: 'Enqueue 10 writes at rear and then advances rear: rear = (0 + 1) mod 5 = 1. The count is 1.',
      draw: function (p, w, h) {
        state(w, h, { cells: [10, null, null, null, null], front: 0, rear: 1 },
          'count = (1 - 0 + 5) mod 5 = 1', 0);
        note('Writing happens at the old rear; the index moves after the write. Reading this order backwards is the usual first mistake.', 24, h - 26);
      }
    },
    {
      duration: 3400,
      caption: 'Three more enqueues put 20, 30 and 40 in slots 1, 2 and 3, and rear reaches 4. Now (rear + 1) mod 5 = 0 = front, so the queue is full with four elements - the capacity n - 1.',
      draw: function (p, w, h) {
        var k = 2 + Math.floor(Math.min(1, Math.max(0, p)) * 2.999);
        var cells = [10, k >= 2 ? 20 : null, k >= 3 ? 30 : null, k >= 4 ? 40 : null, null];
        state(w, h, { cells: cells, front: 0, rear: k }, k >= 4 ? 'full: (4 + 1) mod 5 = 0 = front' : 'filling: rear advancing', k >= 4 ? -1 : k - 1);
        note('The full test is checked before the write: a push would move rear onto front, which is the empty signature.', 24, h - 26);
      }
    },
    {
      duration: 3000,
      caption: 'Two dequeues read slots 0 and 1 and advance front to 2. Slots 0 and 1 are now free, and a linear queue would never use them again.',
      draw: function (p, w, h) {
        var done = Math.min(1, Math.max(0, p)) >= 0.5 ? 2 : 1;
        var cells = [null, null, 30, 40, null];
        state(w, h, { cells: cells, front: 1 + done, rear: 4 }, 'count = (4 - ' + (1 + done) + ' + 5) mod 5 = ' + (4 - (1 + done)), -1);
        note('The live elements are 30 and 40. Nothing is copied: only front moves, which is why dequeue is O(1).', 24, h - 26);
      }
    },
    {
      duration: 2800,
      caption: 'Enqueue 50 writes at rear = 4 and then wraps: rear = (4 + 1) mod 5 = 0. The index has come back to the start of the array, so the next write reuses a slot freed by a dequeue; the queue holds 30, 40, 50 with count 3.',
      draw: function (p, w, h) {
        state(w, h, { cells: [null, null, 30, 40, 50], front: 2, rear: 0 },
          'rear wrapped: (4 + 1) mod 5 = 0', 4);
        note('This single wrap is the whole difference from a linear queue: the slot behind the front is reachable again.', 24, h - 26);
      }
    },
    {
      duration: 2800,
      caption: 'Enqueue 60 writes at rear = 0 - the first slot, reused - and sets rear = 1. Now (1 + 1) mod 5 = 2 = front, so the queue is full again, this time across the wrap.',
      draw: function (p, w, h) {
        state(w, h, { cells: [60, null, 30, 40, 50], front: 2, rear: 1 },
          'full: (1 + 1) mod 5 = 2 = front', 0);
        note('The four elements sit in slots 2, 3, 4 and 0 - the live region wraps around the end of the array, and slot 1 is the sacrificed one.', 24, h - 26);
      }
    },
    {
      duration: 3000,
      caption: 'The count formula reads the queue in one line: (rear - front + n) mod n = (1 - 2 + 5) mod 5 = 4. The order of the elements is front, then forward, wrapping as needed.',
      draw: function (p, w, h) {
        state(w, h, { cells: [60, null, 30, 40, 50], front: 2, rear: 1 },
          '(1 - 2 + 5) mod 5 = 4 elements', -1);
        order(w, h, ['30', '40', '50', '60']);
        note('Reading order starts at front = 2: 30, 40, 50, then wrap to 0: 60. The oldest element is 30.', 24, h - 26);
      }
    },
    {
      duration: 3200,
      caption: 'Had all five slots been used, a queue holding five elements would have rear == front, exactly the empty signature. Sacrificing one slot - or keeping a count variable - is what keeps the two states apart.',
      draw: function (p, w, h) {
        state(w, h, { cells: [60, 70, 30, 40, 50], front: 2, rear: 2 },
          'rear == front: full or empty? not decidable', 4);
        textSize(12.5); fill(180, 90, 31); noStroke();
        text('Using slot 1 as well would make rear == front with five elements stored.', 24, h - 62);
        note('Two indices cannot encode three states. Either sacrifice a slot (capacity n - 1) or carry a count (capacity n).', 24, h - 26);
      }
    }
  ]
};

/* ---------------------------------------------------------------- drawing */
var N = 5;

function ink() {
  var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  background(dark ? color(23, 28, 36) : color(255));
  noStroke();
  fill(dark ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}
function head(t, x, y) { textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function note(t, x, y) { textSize(12.5); fill(90, 100, 116); noStroke(); text(t, x, y); }

/* One row of five slots with the values, the two indices and the queue status line. */
function state(w, h, s, status, hi) {
  ink();
  head('Circular queue: array of ' + N + ' slots, capacity ' + (N - 1), 24, 32);

  var cw = Math.min(96, Math.floor((w - 48 - (N - 1) * 10) / N));
  var gap = 10, x0 = 24, y = 74, bh = 58;
  var total = N * cw + (N - 1) * gap;

  textSize(11); fill(120, 128, 140); noStroke();
  text('index', x0, y - 30);

  for (var i = 0; i < N; i++) {
    var x = x0 + i * (cw + gap);
    var on = i === hi;
    stroke(on ? color(31, 94, 255) : color(214, 220, 230));
    strokeWeight(on ? 2.5 : 1);
    fill(s.cells[i] === null ? color(250, 251, 253) : color(232, 238, 255));
    rect(x, y, cw, bh, 8);
    noStroke(); fill(120, 128, 140); textSize(11);
    text(String(i), x + 6, y - 6);
    if (s.cells[i] !== null) {
      fill(20, 24, 31); textSize(15);
      text(String(s.cells[i]), x + 12, y + 36);
    } else {
      fill(170, 178, 190); textSize(12);
      text('free', x + 12, y + 36);
    }
    if (i === s.front) { marker('front', x, y + bh + 16, color(31, 94, 255)); }
    if (i === s.rear) { marker('rear', x, y + bh + 40, color(180, 90, 31)); }
  }

  textSize(12.5); fill(20, 24, 31); noStroke();
  text('front = ' + s.front + '     rear = ' + s.rear + '     ' + status, x0, y + bh + 74);
  var live = 0;
  for (var j = 0; j < N; j++) { if (s.cells[j] !== null) { live++; } }
  textSize(12); fill(90, 100, 116); noStroke();
  text('elements drawn: ' + live + ' of capacity ' + (N - 1), x0, y + bh + 96);
  return total;
}

function marker(label, x, y, col) {
  noStroke(); fill(col); textSize(10.5);
  text(label, x + 4, y);
}

/* The dequeue order, drawn as boxes so the wrap is visible in the reading order. */
function order(w, h, items) {
  var y = h - 120, cw = 54, gap = 8, x = 24;
  textSize(11); fill(120, 128, 140); noStroke();
  text('dequeue order (front first, wrapping)', x, y - 10);
  for (var i = 0; i < items.length; i++) {
    var bx = x + i * (cw + gap);
    stroke(color(31, 94, 255)); strokeWeight(2);
    fill(color(232, 238, 255));
    rect(bx, y, cw, 40, 7);
    noStroke(); fill(20, 24, 31); textSize(14);
    text(items[i], bx + 16, y + 26);
  }
}
