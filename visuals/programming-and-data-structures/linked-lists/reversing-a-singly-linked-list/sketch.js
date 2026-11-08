/* Reversing a singly linked list in place with three pointers.
   The list is 1 -> 2 -> 3 -> 4 -> NULL and the loop is
     while (curr) { next = curr->next; curr->next = prev; prev = curr; curr = next; }
   Every node's next field is written exactly once, so the loop makes n writes for n nodes:
   Theta(n) time and O(1) extra space, which is GATE CSE 2022 Q.5.
   The write count, the final order and the step count are recomputed in scripts/validate.py
   (check_linked_lists). */

var VALUES = [1, 2, 3, 4];
var N = VALUES.length;

window.LESSON = {
  steps: [
    {
      duration: 3200,
      caption: 'Four nodes, linked left to right. prev is NULL and curr is the head, node 1. Nothing has been relinked yet, so every arrow still points forward.',
      draw: function (p, w, h) {
        picture(w, h, 0, { prev: 0, curr: 0, next: -2 }, 'prev = NULL, curr = head', 0);
      }
    },
    {
      duration: 3600,
      caption: 'Iteration 1. next is saved as node 2 first, because curr->next is about to be overwritten. Then node 1 points at prev, which is NULL: node 1 becomes the tail of the reversed part. prev moves to 1 and curr to 2.',
      draw: function (p, w, h) {
        picture(w, h, 1, { prev: 0, curr: 1, next: 1 }, 'one node reversed, one write', p);
      }
    },
    {
      duration: 3400,
      caption: 'Iteration 2. next becomes node 3, node 2 points back at node 1, prev moves to 2 and curr to 3. Two of the four links are now reversed, and the reversed part grows from the left.',
      draw: function (p, w, h) {
        picture(w, h, 2, { prev: 1, curr: 2, next: 2 }, 'two nodes reversed, two writes', p);
      }
    },
    {
      duration: 3400,
      caption: 'Iteration 3. next becomes node 4, node 3 points back at node 2, prev moves to 3 and curr to 4. Only the link from 4 is still forward.',
      draw: function (p, w, h) {
        picture(w, h, 3, { prev: 2, curr: 3, next: 3 }, 'three nodes reversed, three writes', p);
      }
    },
    {
      duration: 3400,
      caption: 'Iteration 4. next becomes NULL, node 4 points back at node 3, prev moves to 4 and curr becomes NULL. curr is NULL, so the loop stops: four nodes, four writes.',
      draw: function (p, w, h) {
        picture(w, h, 4, { prev: 3, curr: -1, next: -1, nextNull: true }, 'four nodes reversed, four writes', p);
      }
    },
    {
      duration: 3600,
      caption: 'The function returns prev, which is node 4, as the new head. The list reads 4, 3, 2, 1 with NULL at the end. Every node was visited once and only two local pointers were added, so the cost is Theta(n) time and O(1) space.',
      draw: function (p, w, h) {
        picture(w, h, 4, { prev: 3, curr: -1, next: -1, nextNull: true, head: true }, 'done: head = 4', 1);
      }
    }
  ]
};

/* ------------------------------------------------------------------ drawing */
function ink() {
  var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  background(dark ? color(23, 28, 36) : color(255));
  noStroke();
  fill(dark ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}
function head(t, x, y) { textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function note(t, x, y) { textSize(12.5); fill(90, 100, 116); noStroke(); text(t, x, y); }

function picture(w, h, k, marks, status, progress) {
  ink();
  head('Reverse 1 -> 2 -> 3 -> 4 with prev, curr and next', 26, 34);
  note('Reversed part grows from the left; arrows below the boxes point backwards.', 26, 56);

  var bw = Math.min(96, Math.floor((w - 120) / N) - 22);
  var bh = 52;
  var gap = 54;
  var total = N * bw + (N - 1) * gap;
  var x0 = Math.max(40, Math.floor((w - total) / 2));
  var y = Math.floor(h * 0.42);

  /* the boxes */
  for (var i = 0; i < N; i++) {
    var x = x0 + i * (bw + gap);
    var reversed = i < k;
    stroke(reversed ? color(31, 94, 255) : color(206, 213, 224));
    strokeWeight(reversed ? 2.5 : 1.4);
    fill(reversed ? color(232, 238, 255) : color(249, 250, 252));
    rect(x, y, bw, bh, 9);
    noStroke();
    fill(20, 24, 31); textSize(17); textAlign('center', 'center');
    text(String(VALUES[i]), x + bw / 2, y + bh / 2 - 5);
    textSize(9.5); fill(120, 128, 140);
    text('node ' + (i + 1), x + bw / 2, y + bh - 11);
    textAlign('left', 'baseline');
  }

  /* forward links, still to be reversed: i -> i+1 exists while i > k */
  for (var i = 0; i < N - 1; i++) {
    if (i > k) {
      var xa = x0 + i * (bw + gap) + bw;
      arrowRight(xa + 6, y - 26, gap - 12, color(150, 158, 172), 1);
    }
  }
  /* backwards links already made: i+1 -> i exists while i < k */
  for (var j = 0; j < N - 1; j++) {
    if (j < k) {
      var grow = (k === j + 1) ? progress : 1;
      var xb = x0 + (j + 1) * (bw + gap);
      arrowLeft(xb - 6, y + bh + 26, (gap - 12) * Math.max(0.15, grow), color(31, 94, 255), 2.2);
    }
  }

  /* NULL tags at the two open ends */
  if (k >= 1) {
    noStroke(); fill(180, 90, 31); textSize(12);
    text('NULL', x0 - 46, y + bh / 2 + 4);
  }
  if (k < N) {
    noStroke(); fill(180, 90, 31); textSize(12);
    text('NULL', x0 + (N - 1) * (bw + gap) + bw + 12, y + bh / 2 + 4);
  }

  /* pointer markers */
  marker('prev', marks.prev, marks.prev >= 0, x0, y, bw, gap, bh, color(31, 94, 255), true);
  marker('curr', marks.curr, marks.curr >= 0, x0, y, bw, gap, bh, color(15, 128, 96), false);
  if (marks.next >= 0) {
    marker('next', marks.next, true, x0, y, bw, gap, bh, color(168, 96, 12), true);
  } else if (marks.nextNull) {
    noStroke(); fill(168, 96, 12); textSize(12);
    text('next = NULL', x0 + (N - 1) * (bw + gap) + bw + 12, y + bh + 52);
  }

  note('List state: ' + status + '.', 26, h - 46);
  if (marks.head) {
    noStroke(); fill(31, 94, 255); textSize(13); textStyle(BOLD);
    text('head = node 4, the old tail', x0, y - 62);
    textStyle(NORMAL);
  } else if (marks.curr < 0) {
    noStroke(); fill(15, 128, 96); textSize(12);
    text('curr = NULL, loop ends', x0 + (N - 1) * (bw + gap) + bw + 12, y + bh + 70);
  }
}

/* A pointer label with a line to the top or bottom edge of its node. */
function marker(label, idx, on, x0, y, bw, gap, bh, col, above) {
  if (!on) { return; }
  var x = x0 + idx * (bw + gap) + bw / 2;
  var yEdge = above ? y - 6 : y + bh + 6;
  var yLabel = above ? y - 42 : y + bh + 44;
  stroke(col); strokeWeight(1.6);
  line(x, yLabel + 4, x, yEdge);
  noStroke(); fill(col); textSize(12); textAlign('center', 'baseline');
  text(label, x, yLabel);
  textAlign('left', 'baseline');
}

function arrowRight(x, y, len, col, wt) {
  stroke(col); strokeWeight(wt); fill(col);
  line(x, y, x + len, y);
  line(x + len, y, x + len - 8, y - 5);
  line(x + len, y, x + len - 8, y + 5);
}

function arrowLeft(x, y, len, col, wt) {
  stroke(col); strokeWeight(wt); fill(col);
  line(x, y, x - len, y);
  line(x - len, y, x - len + 8, y - 5);
  line(x - len, y, x - len + 8, y + 5);
}
