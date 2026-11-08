/* Build-max-heap, bottom up, on the array [4,1,3,2,16,9,10,14,8,7].
   The loop runs heapify(i) for i = floor(n/2) = 5 down to 1; the leaves are already heaps.
     i = 5 (16): child 7, no swap
     i = 4 (2) : one swap with 14
     i = 3 (3) : one swap with 10
     i = 2 (1) : two swaps, past 16 then past 7
     i = 1 (4) : three swaps, past 16, 14 then 8
   Result [16,14,10,8,7,9,3,2,4,1]: seven swaps in five calls, and the cost is Theta(n),
   not Theta(n log n), because a node at height h sinks at most h steps and there are only
   about n/2^(h+1) nodes at that height. Every array and every swap here is recomputed in
   scripts/validate.py (check_binary_heaps). */

var POS = {
  1: [0.50, 0.12],
  2: [0.27, 0.34], 3: [0.73, 0.34],
  4: [0.16, 0.56], 5: [0.42, 0.56], 6: [0.62, 0.56], 7: [0.86, 0.56],
  8: [0.09, 0.78], 9: [0.23, 0.78], 10: [0.35, 0.78]
};
var EDGES = [[1, 2], [1, 3], [2, 4], [2, 5], [3, 6], [3, 7], [4, 8], [4, 9], [5, 10]];

var FRAMES = [
  { a: [4, 1, 3, 2, 16, 9, 10, 14, 8, 7], mark: [], title: 'An array of ten keys: not a heap yet' },
  { a: [4, 1, 3, 2, 16, 9, 10, 14, 8, 7], mark: [5, 10], title: 'i = 5: 16 beats its child 7, no swap' },
  { a: [4, 1, 3, 14, 16, 9, 10, 2, 8, 7], mark: [4, 8], title: 'i = 4: 2 sinks past 14' },
  { a: [4, 1, 10, 14, 16, 9, 3, 2, 8, 7], mark: [3, 7], title: 'i = 3: 3 sinks past 10' },
  { a: [4, 16, 10, 14, 7, 9, 3, 2, 8, 1], mark: [2, 5, 10], title: 'i = 2: 1 sinks two levels' },
  { a: [16, 14, 10, 8, 7, 9, 3, 2, 4, 1], mark: [1], title: 'i = 1: 4 sinks three levels' },
  { a: [16, 14, 10, 8, 7, 9, 3, 2, 4, 1], mark: [], title: 'A max-heap after seven swaps' }
];

window.LESSON = {
  steps: [
    {
      duration: 3200,
      caption: 'Ten keys in an array, read as a complete tree: index 1 at the root, indices 2 and 3 below it, and so on. The shape is already correct because any array is a complete tree in level order. What is wrong is the order: 4 is the root while 16 sits below it.',
      draw: function (t, w, h) { picture(w, h, FRAMES[0], 1); }
    },
    {
      duration: 3400,
      caption: 'Start at i = floor(10/2) = 5, the last node that has a child. Its only child is 7 at index 10, and 16 beats it, so nothing happens. Every index above 5 is a leaf and is already a heap on its own, which is why the loop skips half the array.',
      draw: function (t, w, h) { picture(w, h, FRAMES[1], 1); }
    },
    {
      duration: 3400,
      caption: 'i = 4: the key 2 has children 14 and 8. It swaps with the larger, 14, and lands at index 8 where it has no children. One swap, one level. Both subtrees it joined were already heaps, so this call only had to fix the root of that subtree.',
      draw: function (t, w, h) { picture(w, h, FRAMES[2], 1); }
    },
    {
      duration: 3400,
      caption: 'i = 3: the key 3 has children 9 and 10, so it swaps with 10 and stops at index 7. One swap again. Notice the pattern: the nodes near the bottom of the array sink one step, and each of them is cheap.',
      draw: function (t, w, h) { picture(w, h, FRAMES[3], 1); }
    },
    {
      duration: 3800,
      caption: 'i = 2: the key 1 has children 16 and 9. It swaps with 16, then at index 5 it faces 8 and 7 and swaps with 7. Two swaps. This is what a sink really is: it does not stop after one swap, it keeps going while a child wins.',
      draw: function (t, w, h) { picture(w, h, FRAMES[4], 1); }
    },
    {
      duration: 3800,
      caption: 'i = 1: the key 4 has children 16 and 10, swaps with 16; at index 2 it faces 14 and 7, swaps with 14; at index 4 it faces 8 and 1, swaps with 8. Three swaps, the deepest sink in the array, and the only node that can sink the full height.',
      draw: function (t, w, h) { picture(w, h, FRAMES[5], 1); }
    },
    {
      duration: 3800,
      caption: 'Seven swaps in five calls, and the array is a max-heap: [16,14,10,8,7,9,3,2,4,1]. The cost is the sum over nodes of their heights, not n times log n: half the nodes are leaves and sink nothing, a quarter sink one step, and the total stays below 2n. That is why build-heap is Theta(n).',
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
  head(frame.title, 26, 30);
  note('Each box carries its array index underneath. The row at the bottom is the array itself.', 26, 50);

  var bw = 38, bh = 32;
  var top = Math.floor(h * 0.10);
  var spanY = h * 0.62;

  for (var e = 0; e < EDGES.length; e++) {
    var a = EDGES[e][0], b = EDGES[e][1];
    stroke(196, 203, 214); strokeWeight(1.5);
    line(POS[a][0] * w, top + POS[a][1] * spanY + bh / 2,
         POS[b][0] * w, top + POS[b][1] * spanY - bh / 2);
  }

  for (var i = 1; i <= 10; i++) {
    var pos = POS[i];
    var x = pos[0] * w, y = top + pos[1] * spanY;
    var marked = frame.mark.indexOf(i) >= 0;
    stroke(marked ? color(31, 94, 255) : color(206, 213, 224));
    strokeWeight(marked ? 2.5 : 1.4);
    fill(marked ? color(240, 244, 255) : color(249, 250, 252));
    rect(x - bw / 2, y - bh / 2, bw, bh, 8);
    noStroke();
    fill(20, 24, 31); textSize(14.5); textAlign('center', 'center');
    text(String(frame.a[i - 1]), x, y - 1);
    textAlign('left', 'baseline');
    fill(marked ? color(31, 94, 255) : color(120, 128, 140));
    textSize(10.5); textAlign('center', 'baseline');
    text(String(i), x, y + bh / 2 + 13);
    textAlign('left', 'baseline');
  }

  var cells = 10, cw = Math.min(56, (w - 60) / cells), ch = 30;
  var x0 = 30, y0 = h - 84;
  note('Array, 1-based:', x0, y0 - 8);
  for (var j = 0; j < cells; j++) {
    var cx = x0 + j * cw;
    var hi = frame.mark.indexOf(j + 1) >= 0;
    stroke(hi ? color(31, 94, 255) : color(214, 220, 229));
    strokeWeight(hi ? 2.2 : 1.2);
    fill(color(252, 253, 255));
    rect(cx, y0, cw - 5, ch, 6);
    noStroke();
    fill(20, 24, 31); textSize(13); textAlign('center', 'center');
    text(String(frame.a[j]), cx + (cw - 5) / 2, y0 + ch / 2);
    textAlign('left', 'baseline');
    fill(130, 138, 150); textSize(10); textAlign('center', 'baseline');
    text(String(j + 1), cx + (cw - 5) / 2, y0 + ch + 12);
    textAlign('left', 'baseline');
  }
  note('Indices 6 to 10 are leaves: the loop starts at 5 and works back to 1.', x0, h - 20);
}
