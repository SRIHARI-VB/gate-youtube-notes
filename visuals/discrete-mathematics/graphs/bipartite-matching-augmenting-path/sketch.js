/* Bipartite matching, augmenting paths and Koenig's theorem.

   The graph, the maximal matching, the maximum matching, the augmenting path and the
   minimum vertex cover shown here are all recomputed in scripts/validate.py
   (check_graphs): the maximal matching of size 2, the maximum matching of size 3, the
   alternating path b-1-a-2-c-3 with free endpoints, and the cover {1, 2, c} of size 3. */

var L_NODES = ["a", "b", "c"];
var R_NODES = ["1", "2", "3"];
var EDGES = [["a", "1"], ["a", "2"], ["b", "1"], ["b", "2"], ["c", "2"], ["c", "3"]];
var MAXIMAL = [["a", "1"], ["c", "2"]];
var MAXIMUM = [["a", "2"], ["b", "1"], ["c", "3"]];
var AUGMENTING = ["b", "1", "a", "2", "c", "3"];
var COVER = ["1", "2", "c"];

var BLUE = [31, 94, 255], GREEN = [20, 107, 74], ORANGE = [180, 90, 31], PURPLE = [96, 55, 168];
var GREY_D = [120, 130, 145], GREY_L = [190, 196, 206];

function dark() {
  return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
}

function ink() {
  var d = dark();
  background(d ? color(23, 28, 36) : color(255));
  noStroke(); fill(d ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}

function head(t, x, y) { textSize(16); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }

function note(t, x, y) {
  textSize(12.5); fill(90, 100, 116); noStroke(); textAlign('left', 'baseline'); text(t, x, y);
}

function panel(x, y, lines, w) {
  noStroke(); fill(232, 238, 255);
  var bw = Math.min(w - x - 12, 232);
  rect(x, y, bw, 22 + lines.length * 20, 8);
  fill(31, 94, 255); textSize(12); textStyle(BOLD); text('what the diagram shows', x + 10, y + 17);
  textStyle(NORMAL); textSize(11.5); fill(31, 60, 140);
  for (var i = 0; i < lines.length; i++) { text(lines[i], x + 10, y + 36 + i * 19); }
}

function nodePos(name, w, h) {
  var i, x, y;
  var li = L_NODES.indexOf(name);
  if (li >= 0) { i = li; x = w * 0.24; }
  else { i = R_NODES.indexOf(name); x = w * 0.62; }
  y = h * (0.30 + 0.22 * i);
  return [x, y];
}

function edgeKey(a, b) { return a < b ? a + "-" + b : b + "-" + a; }

function sameEdge(e, list) {
  for (var i = 0; i < list.length; i++) {
    if (edgeKey(list[i][0], list[i][1]) === edgeKey(e[0], e[1])) { return true; }
  }
  return false;
}

/* Draw the bipartite graph. opts: matched (edge list), pathEdges (list of [u,v] in path order),
   cover (vertex list), colours (map name -> rgb triple), label (string). */
function graph(opt, w, h) {
  var d = dark();
  var i;
  var matched = opt.matched || [];
  var pathEdges = opt.pathEdges || [];
  var cover = opt.cover || [];
  var colours = opt.colours || {};

  for (i = 0; i < EDGES.length; i++) {
    var A = nodePos(EDGES[i][0], w, h), B = nodePos(EDGES[i][1], w, h);
    var onPath = sameEdge(EDGES[i], pathEdges);
    var inMatch = sameEdge(EDGES[i], matched);
    if (onPath) { stroke(ORANGE[0], ORANGE[1], ORANGE[2]); strokeWeight(3.4); }
    else if (inMatch) { stroke(BLUE[0], BLUE[1], BLUE[2]); strokeWeight(3.4); }
    else { stroke(d ? GREY_D[0] : GREY_L[0], d ? GREY_D[1] : GREY_L[1], d ? GREY_D[2] : GREY_L[2]); strokeWeight(1.6); }
    line(A[0], A[1], B[0], B[1]);
  }

  var all = L_NODES.concat(R_NODES);
  for (i = 0; i < all.length; i++) {
    var P = nodePos(all[i], w, h);
    var c = colours[all[i]];
    var inCover = cover.indexOf(all[i]) >= 0;
    if (c) { noStroke(); fill(c[0], c[1], c[2]); }
    else if (inCover) { noStroke(); fill(PURPLE[0], PURPLE[1], PURPLE[2]); }
    else { noStroke(); fill(d ? color(52, 60, 74) : color(238, 241, 246)); }
    circle(P[0], P[1], c || inCover ? 30 : 26);
    if (c || inCover) {
      fill(255); textSize(13); textStyle(BOLD); textAlign('center', 'center');
      text(all[i], P[0], P[1]); textAlign('left', 'baseline'); textStyle(NORMAL);
    } else {
      fill(d ? color(238, 241, 245) : color(20, 24, 31)); textSize(12); textAlign('center', 'center');
      text(all[i], P[0], P[1]); textAlign('left', 'baseline');
    }
  }

  /* side labels */
  textSize(11.5); fill(120, 130, 145); noStroke(); textAlign('center', 'center');
  text('L', w * 0.24, h * 0.18);
  text('R', w * 0.62, h * 0.18);
  textAlign('left', 'baseline');
}

window.LESSON = {
  steps: [
    {
      duration: 2600,
      caption: 'A bipartite graph: a, b, c on the left and 1, 2, 3 on the right, with every edge crossing between the sides. It has 6 edges, and its only cycle is a-1-b-2-a, of length 4. No odd cycle, so the graph is bipartite and its chromatic number is 2.',
      draw: function (p, w, h) {
        ink(); head('A bipartite graph with 6 edges', 30, 32);
        graph({}, w, h);
        panel(w - 262, 60, ['|L| = 3, |R| = 3', 'edges: a-1, a-2, b-1, b-2, c-2, c-3', 'one cycle of length 4', 'no odd cycle, so chromatic number 2'], w);
        note('a matching will pair left vertices with right vertices, each used once', 30, h - 24);
      }
    },
    {
      duration: 2800,
      caption: 'Greedy choice: take a-1, then c-2. Two edges, no shared vertex, so this is a matching of size 2. Nothing forces a greedy algorithm to pick well, and here it stops early.',
      draw: function (p, w, h) {
        ink(); head('A matching of size 2: {a-1, c-2}', 30, 32);
        var shown = 1 + Math.floor(p * 1.99);
        graph({ matched: MAXIMAL.slice(0, shown) }, w, h);
        panel(w - 262, 60, ['M = {a-1, c-2}', '|M| = 2', 'a, 1, c, 2 are saturated', 'b and 3 are free'], w);
        note('a matching is a set of edges with no shared endpoint', 30, h - 24);
      }
    },
    {
      duration: 3000,
      caption: 'Is it maximum? Try to add an edge: a-2 needs a, b-1 needs 1, c-3 needs c, and all of those are already matched. So the matching is maximal, meaning nothing can be added, yet its size is only 2. Maximal and maximum are different words.',
      draw: function (p, w, h) {
        ink(); head('Maximal, but is it maximum?', 30, 32);
        graph({ matched: MAXIMAL }, w, h);
        var rows = ['a-2 blocked: a and 2 matched', 'b-1 blocked: 1 is matched', 'b-2 blocked: 2 is matched', 'c-3 blocked: c is matched'];
        panel(w - 262, 60, rows.slice(0, 1 + Math.floor(p * 3.99)), w);
        note('maximal means no edge can be added; maximum means no matching is larger', 30, h - 24);
      }
    },
    {
      duration: 3200,
      caption: 'The proof that it is not maximum is an augmenting path: start at the free vertex b, use b-1 which is not in M, then 1-a which is in M, then a-2 not in M, then 2-c in M, then c-3 not in M and stop at the free vertex 3. The edges alternate outside and inside M, and both ends are free.',
      draw: function (p, w, h) {
        ink(); head('An augmenting path: b-1-a-2-c-3', 30, 32);
        var seq = AUGMENTING;
        var shown = 2 + Math.floor(p * 4.99);
        var pathEdges = [];
        for (var i = 0; i + 1 < Math.min(shown, seq.length); i++) { pathEdges.push([seq[i], seq[i + 1]]); }
        graph({ matched: MAXIMAL, pathEdges: pathEdges }, w, h);
        panel(w - 262, 60, ['5 edges, alternating', 'odd length, both ends free', 'outside M: b-1, a-2, c-3', 'inside M: 1-a, 2-c'], w);
        note('Berge: a matching is maximum exactly when no augmenting path exists', 30, h - 24);
      }
    },
    {
      duration: 3200,
      caption: 'Flip the path: keep the edges that were outside M and drop the ones that were inside. The matching becomes b-1, a-2, c-3, which has 3 edges and saturates all six vertices. Every flip of an augmenting path adds exactly one edge, which is why the augmenting-path algorithm terminates at a maximum matching.',
      draw: function (p, w, h) {
        ink(); head('After the flip: a perfect matching of size 3', 30, 32);
        var shown = 1 + Math.floor(p * 2.99);
        graph({ matched: MAXIMUM.slice(0, shown), colours: {} }, w, h);
        panel(w - 262, 60, ['M = {b-1, a-2, c-3}', '|M| = 3, up by one', 'all 6 vertices saturated', 'so this is a perfect matching'], w);
        note('symmetric difference with an augmenting path adds exactly one edge', 30, h - 24);
      }
    },
    {
      duration: 3400,
      caption: 'Koenig ties the two sides together: the maximum matching has 3 edges and the smallest vertex cover, here {1, 2, c}, also has 3 vertices, so maximum matching equals minimum vertex cover. Hall agrees: every subset of the left side has at least as many neighbours, for example a and b together see 1 and 2.',
      draw: function (p, w, h) {
        ink(); head('Koenig: matching 3 = vertex cover 3', 30, 32);
        graph({ matched: MAXIMUM, cover: COVER }, w, h);
        var rows = ['maximum matching: 3 edges', 'minimum cover {1, 2, c}: 3 vertices', 'nu = tau because G is bipartite', 'Hall: |N(S)| >= |S| for every S'];
        panel(w - 262, 60, rows.slice(0, 2 + Math.floor(p * 2.99)), w);
        note('purple vertices form a cover: every edge touches one of them', 30, h - 24);
      }
    }
  ]
};
