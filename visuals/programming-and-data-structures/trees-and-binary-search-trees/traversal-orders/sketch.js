/* The three depth-first traversal orders on one tree.
   The tree is the binary search tree 4 at the root, 2 and 6 below it, then 1, 3, 5, 7:
        4
      /   \
     2     6
    / \   / \
   1   3 5   7
   Preorder N L R = 4 2 1 3 6 5 7
   Inorder  L N R = 1 2 3 4 5 6 7   (sorted, because the tree is a search tree)
   Postorder L R N = 1 3 2 5 7 6 4
   Seven visits, recursion depth height + 1 = 3. Every sequence and the frame count are
   recomputed in scripts/validate.py (check_trees_and_bsts). */

var POS = {
  4: [0.50, 0.16], 2: [0.28, 0.42], 6: [0.72, 0.42],
  1: [0.16, 0.68], 3: [0.40, 0.68], 5: [0.60, 0.68], 7: [0.84, 0.68]
};
var EDGES = [[4, 2], [4, 6], [2, 1], [2, 3], [6, 5], [6, 7]];
var CHAIN = { 1: [0.34, 0.20], 2: [0.52, 0.44], 3: [0.70, 0.68] };
var CHAIN_EDGES = [[1, 2], [2, 3]];

var PRE = [4, 2, 1, 3, 6, 5, 7];
var IN = [1, 2, 3, 4, 5, 6, 7];
var POST = [1, 3, 2, 5, 7, 6, 4];

window.LESSON = {
  steps: [
    {
      duration: 3000,
      caption: 'One tree, seven nodes. 4 is the root, 2 and 6 are its children, and 1, 3, 5, 7 sit on the last level. It is a binary search tree: everything left of a node is smaller, everything right is larger. All three orders will walk exactly these seven nodes.',
      draw: function (p, w, h) { picture(w, h, 'The tree: seven nodes, height 2', null, null, 0); }
    },
    {
      duration: 3200,
      caption: 'Preorder visits a node before its subtrees: N L R. The root 4 is printed first, then the whole left subtree, then the whole right subtree. The small number under each node is its position in the order.',
      draw: function (p, w, h) { picture(w, h, 'Preorder: root, left, right', PRE, 'pre', 0.5); }
    },
    {
      duration: 3200,
      caption: 'The preorder completes as 4, 2, 1, 3, 6, 5, 7. Node 4 comes first because a parent is always printed before its children, which is why a copy or a serialisation uses this order.',
      draw: function (p, w, h) { picture(w, h, 'Preorder: 4 2 1 3 6 5 7', PRE, 'pre', 1); }
    },
    {
      duration: 3600,
      caption: 'Inorder visits the left subtree, then the node, then the right subtree: L N R. On this search tree the result is 1, 2, 3, 4, 5, 6, 7, the sorted keys. The traversal did not sort anything; the search-tree rule had already put every key in sorted position.',
      draw: function (p, w, h) { picture(w, h, 'Inorder: 1 2 3 4 5 6 7 (sorted)', IN, 'in', 1); }
    },
    {
      duration: 3400,
      caption: 'Postorder visits both subtrees before the node: L R N. The root 4 comes last, and the sequence is 1, 3, 2, 5, 7, 6, 4. A node is printed only after everything under it, which is what freeing a tree or evaluating an expression tree needs.',
      draw: function (p, w, h) { picture(w, h, 'Postorder: 1 3 2 5 7 6 4', POST, 'post', 1); }
    },
    {
      duration: 3800,
      caption: 'Now change the shape and keep the rules: a chain 1 - 2 - 3 leaning right. Preorder gives 1 2 3 and inorder gives 1 2 3 as well, because no node has a left subtree, so L is empty everywhere. Postorder gives 3 2 1.',
      draw: function (p, w, h) { chainPicture(w, h, 'Chain 1-2-3: preorder = inorder = 1 2 3', 1); }
    },
    {
      duration: 3600,
      caption: 'Seven nodes, seven visits in every order: Theta(n) time. The recursion is three frames deep on the longest path 4-2-1, which is the height 2 plus one. And since two shapes here share a sequence, no single traversal fixes a tree - the point GATE CSE 2004 Q.35 makes about preorder with postorder.',
      draw: function (p, w, h) { picture(w, h, 'Seven visits per order, three frames deep', POST, 'post', 1); }
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

var COLOURS = { pre: [31, 94, 255], in: [15, 128, 96], post: [168, 96, 12] };

function picture(w, h, title, order, mode, progress) {
  ink();
  head(title, 26, 34);
  note('Positions under each node are that node\'s place in the order being shown.', 26, 56);

  var bw = 44, bh = 44;
  var top = Math.floor(h * 0.10);
  var spanY = h - top - 96;
  var col = COLOURS[mode] || [120, 128, 140];

  /* edges first, so the boxes sit on top */
  for (var e = 0; e < EDGES.length; e++) {
    var a = POS[EDGES[e][0]], b = POS[EDGES[e][1]];
    stroke(196, 203, 214); strokeWeight(1.6);
    line(a[0] * w, top + a[1] * spanY + bh / 2, b[0] * w, top + b[1] * spanY - bh / 2);
  }

  var keys = [4, 2, 6, 1, 3, 5, 7];
  for (var i = 0; i < keys.length; i++) {
    var k = keys[i], pos = POS[k];
    var x = pos[0] * w, y = top + pos[1] * spanY;
    var shown = order ? order.indexOf(k) : -1;
    var marked = order && shown >= 0 && (progress >= 1 || shown < Math.ceil(order.length * progress));
    stroke(marked ? color(col[0], col[1], col[2]) : color(206, 213, 224));
    strokeWeight(marked ? 2.5 : 1.4);
    fill(marked ? color(240, 244, 255) : color(249, 250, 252));
    rect(x - bw / 2, y - bh / 2, bw, bh, 9);
    noStroke(); fill(20, 24, 31); textSize(17); textAlign('center', 'center');
    text(String(k), x, y - 2);
    textAlign('left', 'baseline');
    if (marked) {
      noStroke(); fill(col[0], col[1], col[2]); textSize(12.5); textAlign('center', 'baseline');
      text(String(shown + 1), x, y + bh / 2 + 18);
      textAlign('left', 'baseline');
    }
  }

  if (order) {
    var seq = '';
    for (var j = 0; j < order.length; j++) {
      if (progress >= 1 || j < Math.ceil(order.length * progress)) { seq += order[j] + (j === order.length - 1 ? '' : ' '); }
    }
    noStroke(); fill(col[0], col[1], col[2]); textSize(14); textStyle(BOLD);
    text('Sequence so far: ' + (seq || '-'), 26, h - 46);
    textStyle(NORMAL);
  }
  note('Visits so far: ' + (order ? Math.min(order.length, Math.ceil(order.length * progress)) : 0) + ' of 7.', 26, h - 24);
}

function chainPicture(w, h, title, progress) {
  ink();
  head(title, 26, 34);
  note('A chain has no left child anywhere, so preorder and inorder collapse to the same sequence.', 26, 56);
  var bw = 46, bh = 44;
  var top = Math.floor(h * 0.16), spanY = h - top - 120;
  var order = [1, 2, 3];
  for (var e = 0; e < CHAIN_EDGES.length; e++) {
    var a = CHAIN[CHAIN_EDGES[e][0]], b = CHAIN[CHAIN_EDGES[e][1]];
    stroke(196, 203, 214); strokeWeight(1.6);
    line(a[0] * w, top + a[1] * spanY + bh / 2, b[0] * w, top + b[1] * spanY - bh / 2);
  }
  var keys = [1, 2, 3];
  for (var i = 0; i < keys.length; i++) {
    var k = keys[i], pos = CHAIN[k];
    var x = pos[0] * w, y = top + pos[1] * spanY;
    var marked = i < Math.ceil(order.length * progress);
    stroke(marked ? color(15, 128, 96) : color(206, 213, 224));
    strokeWeight(marked ? 2.5 : 1.4);
    fill(marked ? color(240, 255, 250) : color(249, 250, 252));
    rect(x - bw / 2, y - bh / 2, bw, bh, 9);
    noStroke(); fill(20, 24, 31); textSize(17); textAlign('center', 'center');
    text(String(k), x, y - 2); textAlign('left', 'baseline');
    if (marked) {
      noStroke(); fill(15, 128, 96); textSize(12.5); textAlign('center', 'baseline');
      text(String(i + 1), x, y + bh / 2 + 18); textAlign('left', 'baseline');
    }
  }
  noStroke(); fill(15, 128, 96); textSize(14); textStyle(BOLD);
  text('Preorder and inorder: 1 2 3    Postorder: 3 2 1', 26, h - 46);
  textStyle(NORMAL);
  note('Three nodes, three visits, and the recursion is three frames deep.', 26, h - 24);
}
