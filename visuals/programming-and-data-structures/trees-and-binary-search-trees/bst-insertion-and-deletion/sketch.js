/* Insertion and the two-child deletion on one binary search tree.
   Inserting 10, -4, 15, 30, 20, 5, 60, 19 gives
          10
        /    \
      -4      15
        \       \
         5       30
                /  \
              20    60
             /
           19
   The path to 19 is 10, 15, 30, 20, 19: four edges, five nodes (GATE CSE 2025 Set 2 Q.25).
   Deleting 30, which has two children, replaces its key with its inorder successor 60 and
   removes the node 60. Every position, path length and inorder list is recomputed in
   scripts/validate.py (check_trees_and_bsts). */

var POS = {
  10: [0.44, 0.10], '-4': [0.16, 0.32], 15: [0.72, 0.32],
  5: [0.26, 0.56], 30: [0.88, 0.56], 20: [0.74, 0.78], 60: [0.96, 0.78], 19: [0.62, 0.96]
};
var POS_B = {
  10: [0.44, 0.10], '-4': [0.16, 0.32], 15: [0.72, 0.32],
  5: [0.26, 0.56], 60: [0.88, 0.56], 20: [0.74, 0.78], 19: [0.62, 0.96]
};
var EDGES = [[10, '-4'], [10, 15], ['-4', 5], [15, 30], [30, 20], [30, 60], [20, 19]];
var EDGES_B = [[10, '-4'], [10, 15], ['-4', 5], [15, 60], [60, 20], [20, 19]];
var PATH = [10, 15, 30, 20, 19];

window.LESSON = {
  steps: [
    {
      duration: 2800,
      caption: 'An empty tree, then insert 10. The first key becomes the root and nothing is compared.',
      draw: function (p, w, h) { drawTree(w, h, 'Insert 10: it becomes the root', POS, EDGES, [10], 'new', 'One node, height 0.'); }
    },
    {
      duration: 3000,
      caption: 'Insert -4 and 15. Each is compared with 10 once: -4 is smaller and goes left, 15 is larger and goes right. Both become leaves.',
      draw: function (p, w, h) { drawTree(w, h, 'Insert -4 and 15: one comparison each', POS, EDGES, [10, '-4', 15], 'new', 'Three nodes, height 1.'); }
    },
    {
      duration: 3200,
      caption: 'Insert 30, 20 and 5. 30 is larger than 10 and than 15, so it becomes the right child of 15. 20 is larger than 10 and 15 but smaller than 30, so it becomes the left child of 30. 5 is smaller than 10 but larger than -4, so it becomes the right child of -4.',
      draw: function (p, w, h) { drawTree(w, h, 'Insert 30, 20 and 5: each follows its search path', POS, EDGES, [5, 20, 30], 'new', 'Six nodes, height 3.'); }
    },
    {
      duration: 3600,
      caption: 'Insert 60, then 19. 19 is compared with 10, 15, 30 and 20 before it lands as the left child of 20: the path is 10, 15, 30, 20, 19, which is four edges and five nodes. That four is the answer to GATE CSE 2025 Set 2 Q.25.',
      draw: function (p, w, h) { drawTree(w, h, 'Path to 19: 4 edges, 5 nodes', POS, EDGES, PATH, 'path', 'Nineteen sits four edges below the root.'); }
    },
    {
      duration: 3200,
      caption: 'Now delete 30. It has two children, 20 and 60, so it cannot be spliced out: one pointer cannot receive two subtrees.',
      draw: function (p, w, h) { drawTree(w, h, 'Delete 30: it has two children', POS, EDGES, [30], 'target', 'Two-child case: the key must be replaced.'); }
    },
    {
      duration: 3400,
      caption: 'Find the inorder successor of 30: the minimum of its right subtree. Descend right to 60, and 60 has no left child, so 60 is the successor. It is the next key after 30 in sorted order.',
      draw: function (p, w, h) { drawTree(w, h, 'Successor of 30 is 60', POS, EDGES, [30, 60], 'successor', 'The leftmost node of the right subtree.'); }
    },
    {
      duration: 3600,
      caption: 'Overwrite 30 with 60, then remove the node that held 60, which is a leaf. The inorder 19, 20, 60 is still sorted and the search-tree rule still holds: one key write and one pointer change, no node moved.',
      draw: function (p, w, h) { drawTree(w, h, 'After the delete: 60 took 30\'s place', POS_B, EDGES_B, [60], 'done', 'Inorder: -4, 5, 10, 15, 19, 20, 60.'); }
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

var MODES = {
  new: [15, 128, 96], path: [31, 94, 255], target: [188, 60, 44],
  successor: [168, 96, 12], done: [15, 128, 96]
};

function drawTree(w, h, title, pos, edges, marks, mode, footer) {
  ink();
  head(title, 26, 32);
  note('Each insertion is compared from the root, so a key always lands at a leaf.', 26, 54);

  var bw = 46, bh = 40;
  var top = Math.floor(h * 0.11);
  var spanY = h - top - 104;
  var col = MODES[mode] || [120, 128, 140];

  for (var e = 0; e < edges.length; e++) {
    var a = pos[edges[e][0]], b = pos[edges[e][1]];
    if (!a || !b) { continue; }
    stroke(196, 203, 214); strokeWeight(1.6);
    line(a[0] * w, top + a[1] * spanY + bh / 2, b[0] * w, top + b[1] * spanY - bh / 2);
  }

  var keys = [];
  for (var k in pos) { if (pos.hasOwnProperty(k)) { keys.push(k); } }
  for (var i = 0; i < keys.length; i++) {
    var key = keys[i], p = pos[key];
    var x = p[0] * w, y = top + p[1] * spanY;
    var marked = marks.indexOf(Number(key)) >= 0;
    stroke(marked ? color(col[0], col[1], col[2]) : color(206, 213, 224));
    strokeWeight(marked ? 2.6 : 1.4);
    fill(marked ? color(242, 245, 255) : color(249, 250, 252));
    rect(x - bw / 2, y - bh / 2, bw, bh, 9);
    noStroke(); fill(20, 24, 31); textSize(16); textAlign('center', 'center');
    text(key, x, y - 1);
    textAlign('left', 'baseline');
  }

  noStroke(); fill(col[0], col[1], col[2]); textSize(13.5); textStyle(BOLD);
  text(footer, 26, h - 44);
  textStyle(NORMAL);
  note('A key is always compared with every node above it, so its depth is the length of its search path.', 26, h - 22);
}
