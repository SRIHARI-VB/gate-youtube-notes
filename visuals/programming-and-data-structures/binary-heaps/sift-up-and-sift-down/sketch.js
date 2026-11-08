/* One max-heap, two repairs: a key climbs after an insert, then a key sinks after an extract.
   The heap starts as [9,7,8,4,6,5] (1-based):
        9
      /   \
     7     8
    / \   /
   4   6 5
   Insert 10: append at index 7, climb past 8 then past 9 -> [10,7,9,4,6,5,8]
   Extract the maximum: 10 out, the last key 8 to the root, size 6 -> [8,7,9,4,6,5]
   Sink 8: swap with the larger child 9 -> [9,7,8,4,6,5]
   Two swaps up, one swap down, and the height of the heap is 2, so both repairs are
   bounded by the height. Every array in these steps is recomputed in
   scripts/validate.py (check_binary_heaps). */

var POS = {
  1: [0.50, 0.14], 2: [0.27, 0.40], 3: [0.73, 0.40],
  4: [0.14, 0.66], 5: [0.40, 0.66], 6: [0.60, 0.66], 7: [0.84, 0.66]
};
var EDGES = [[1, 2], [1, 3], [2, 4], [2, 5], [3, 6], [3, 7]];

/* Each step: the array, how many cells are inside the heap, the indices to mark, a title. */
var FRAMES = [
  { a: [9, 7, 8, 4, 6, 5], size: 6, mark: [], title: 'The heap: [9,7,8,4,6,5]' },
  { a: [9, 7, 8, 4, 6, 5, 10], size: 7, mark: [7, 3], title: 'Insert 10: appended at index 7' },
  { a: [9, 7, 10, 4, 6, 5, 8], size: 7, mark: [3, 1], title: '10 beats its parent 8: one swap' },
  { a: [10, 7, 9, 4, 6, 5, 8], size: 7, mark: [1], title: '10 beats the root 9: it is the root' },
  { a: [8, 7, 9, 4, 6, 5], size: 6, mark: [1], title: 'Extract: 10 out, last key 8 to the root' },
  { a: [9, 7, 8, 4, 6, 5], size: 6, mark: [1, 3], title: 'Sink 8: swap with the larger child 9' },
  { a: [9, 7, 8, 4, 6, 5], size: 6, mark: [], title: 'Two swaps up, one swap down' }
];

window.LESSON = {
  steps: [
    {
      duration: 3200,
      caption: 'A max-heap of six keys, 9 at the root, 7 and 8 below it, and 4, 6, 5 on the last level. Every parent is at least its children: 9 beats 7 and 8, 7 beats 4 and 6, 8 beats 5. The array underneath is the same tree in level order, which is why no pointers are needed.',
      draw: function (t, w, h) { picture(w, h, FRAMES[0], 1); }
    },
    {
      duration: 3400,
      caption: 'Insert 10. The first move is not a comparison: 10 is appended at index 7, the left child of 8. That single append is what keeps the tree complete, and it is the reason the array indices still work afterwards. Only the new edge can now be wrong.',
      draw: function (t, w, h) { picture(w, h, FRAMES[1], 1); }
    },
    {
      duration: 3400,
      caption: 'Compare 10 with its parent, index 3 holding 8. Ten is larger, so they swap: index 3 now holds 10 and index 7 holds 8. The repair moves upward, one level per swap, and nothing else in the tree is touched.',
      draw: function (t, w, h) { picture(w, h, FRAMES[2], 1); }
    },
    {
      duration: 3400,
      caption: 'Compare 10 with its new parent, the root, holding 9. Ten wins again, so they swap and 10 becomes the root: [10,7,9,4,6,5,8]. There is no parent above index 1, so the climb ends. Two swaps, which is the height of this heap, and the worst case for any heap is floor(log2 n) swaps.',
      draw: function (t, w, h) { picture(w, h, FRAMES[3], 1); }
    },
    {
      duration: 3400,
      caption: 'Now the other direction. Extract the maximum: 10 leaves, and the last key, 8, is moved into the root and the heap shrinks to six cells. The shape is still complete, but the root is now smaller than both of its children, so the order is broken at the top.',
      draw: function (t, w, h) { picture(w, h, FRAMES[4], 1); }
    },
    {
      duration: 3600,
      caption: 'Sink 8. Its children are 7 at index 2 and 9 at index 3, and the larger is 9, so 8 swaps with 9 and not with 7: [9,7,8,4,6,5]. Swapping with the smaller child would leave 9 above a parent of 7 and the heap still broken, which is the mistake this step exists to show.',
      draw: function (t, w, h) { picture(w, h, FRAMES[5], 1); }
    },
    {
      duration: 3600,
      caption: 'Done: two swaps while climbing, one while sinking, and the heap is back to [9,7,8,4,6,5]. Both repairs cost at most the height, floor(log2 n), because each swap moves one level. Insert repairs upward and delete repairs downward, and mixing them up is the commonest error in these questions.',
      draw: function (t, w, h) { picture(w, h, FRAMES[6], 1); }
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

function head(t, x, y) { textSize(15.5); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function note(t, x, y) { textSize(12); fill(90, 100, 116); noStroke(); text(t, x, y); }

function picture(w, h, frame, progress) {
  ink();
  head(frame.title, 26, 32);
  note('Index in the array sits under each box; the row below the tree is that array.', 26, 52);

  var bw = 42, bh = 38;
  var top = Math.floor(h * 0.12);
  var spanY = h * 0.56;

  var e, a, b;
  for (e = 0; e < EDGES.length; e++) {
    a = EDGES[e][0]; b = EDGES[e][1];
    if (b > frame.size) { continue; }
    stroke(196, 203, 214); strokeWeight(1.6);
    line(POS[a][0] * w, top + POS[a][1] * spanY + bh / 2,
         POS[b][0] * w, top + POS[b][1] * spanY - bh / 2);
  }

  for (var i = 1; i <= 7; i++) {
    var pos = POS[i];
    var x = pos[0] * w, y = top + pos[1] * spanY;
    var inside = i <= frame.size;
    var marked = frame.mark.indexOf(i) >= 0;
    stroke(marked ? color(31, 94, 255) : color(206, 213, 224));
    strokeWeight(marked ? 2.5 : 1.4);
    fill(inside ? (marked ? color(240, 244, 255) : color(249, 250, 252)) : color(246, 247, 249));
    rect(x - bw / 2, y - bh / 2, bw, bh, 9);
    noStroke();
    if (inside) {
      fill(20, 24, 31); textSize(16); textAlign('center', 'center');
      text(String(frame.a[i - 1]), x, y - 1);
      textAlign('left', 'baseline');
    }
    fill(marked ? color(31, 94, 255) : color(120, 128, 140));
    textSize(11.5); textAlign('center', 'baseline');
    text(String(i), x, y + bh / 2 + 15);
    textAlign('left', 'baseline');
  }

  /* the array row */
  var cells = 7, cw = Math.min(52, (w - 60) / cells), ch = 34;
  var x0 = 30, y0 = h - 92;
  note('Array, 1-based:', x0, y0 - 10);
  for (var j = 0; j < cells; j++) {
    var cx = x0 + j * cw;
    var inHeap = (j + 1) <= frame.size;
    var hi = frame.mark.indexOf(j + 1) >= 0;
    stroke(hi ? color(31, 94, 255) : color(214, 220, 229));
    strokeWeight(hi ? 2.2 : 1.2);
    fill(inHeap ? color(252, 253, 255) : color(243, 244, 246));
    rect(cx, y0, cw - 6, ch, 6);
    noStroke();
    if (inHeap) {
      fill(20, 24, 31); textSize(14); textAlign('center', 'center');
      text(String(frame.a[j]), cx + (cw - 6) / 2, y0 + ch / 2);
      textAlign('left', 'baseline');
    }
    fill(130, 138, 150); textSize(10.5); textAlign('center', 'baseline');
    text(String(j + 1), cx + (cw - 6) / 2, y0 + ch + 13);
    textAlign('left', 'baseline');
  }
  note('Shaded cells are outside the heap after the extract.', x0, h - 22);
}
