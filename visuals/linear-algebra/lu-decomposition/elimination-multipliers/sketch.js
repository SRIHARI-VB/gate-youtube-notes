/* Watching Gaussian elimination record itself. Each row operation that clears an entry leaves a
   multiplier behind, and those multipliers are the entries of L, so the factorization A = LU is
   written down as the elimination runs rather than solved for afterwards.

   A = [[2,3,1],[4,7,7],[-2,4,5]], L = [[1,0,0],[2,1,0],[-1,7,1]], U = [[2,3,1],[0,1,5],[0,0,-29]],
   the multipliers 2, -1 and 7, the pivots 2, 1 and -29, the determinant -58, the dot-product check
   that gives the (3,2) entry 4, and the pivoting example [[0,2],[1,3]] with det(A) = -2 are all
   recomputed in scripts/validate.py (check_lu_decomposition). Nothing is drawn from an unchecked
   value. */

var A = [[2, 3, 1], [4, 7, 7], [-2, 4, 5]];
var AFTER1 = [[2, 3, 1], [0, 1, 5], [0, 7, 6]];
var AFTER2 = [[2, 3, 1], [0, 1, 5], [0, 0, -29]];
var L = [[1, 0, 0], [2, 1, 0], [-1, 7, 1]];
var U = [[2, 3, 1], [0, 1, 5], [0, 0, -29]];

var BLUE = [31, 94, 255], ORANGE = [180, 90, 31], GREEN = [20, 107, 74], RED = [170, 40, 45];

function darkMode() {
  return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
}

function inkBg() {
  var d = darkMode();
  background(d ? color(23, 28, 36) : color(255));
  noStroke();
  fill(d ? color(238, 241, 245) : color(20, 24, 31));
  textFont('ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial');
}

function faintInk() { return darkMode() ? color(120, 128, 142) : color(150, 156, 166); }
function softInk() { return darkMode() ? color(170, 178, 190) : color(120, 128, 140); }
function strongInk() { return darkMode() ? color(238, 241, 245) : color(20, 24, 31); }
function cellFill(active) {
  if (active) { return darkMode() ? color(52, 62, 84) : color(226, 234, 255); }
  return darkMode() ? color(33, 39, 49) : color(246, 248, 251);
}
function cellEdge() { return darkMode() ? color(74, 82, 96) : color(214, 220, 228); }

function fmt(x) {
  if (x === Math.round(x)) { return String(x); }
  return String(Math.round(x * 100) / 100);
}

/* One matrix drawn as a grid of cells. mark(i, j) returns true for a highlighted cell. */
function grid(x, y, cw, ch, entries, mark, tint) {
  var n = entries.length, m = entries[0].length;
  stroke(cellEdge());
  strokeWeight(1);
  for (var i = 0; i < n; i++) {
    for (var j = 0; j < m; j++) {
      fill(cellFill(mark ? mark(i, j) : false));
      rect(x + j * cw, y + i * ch, cw, ch, 4);
    }
  }
  noStroke();
  textAlign('center', 'center');
  textSize(Math.max(11, Math.min(17, ch * 0.42)));
  for (var a = 0; a < n; a++) {
    for (var b = 0; b < m; b++) {
      var on = mark ? mark(a, b) : false;
      if (on && tint) { fill(tint[0], tint[1], tint[2]); } else { fill(strongInk()); }
      text(fmt(entries[a][b]), x + b * cw + cw / 2, y + a * ch + ch / 2);
    }
  }
  textAlign('left', 'baseline');
}

function label(txt, x, y, size, col) {
  noStroke();
  fill(col || softInk());
  textSize(size || 12);
  text(txt, x, y);
}

/* The working matrix on the left, and a slot on the right for L, U or a note. */
function layout(w, h) {
  var pad = 16;
  var right = (w >= 640) ? Math.min(300, w * 0.42) : 0;
  var left = w - right - 2 * pad;
  var cw = Math.min(56, left / 3.6);
  var ch = Math.min(46, (h - 90) / 3.6);
  return {
    w: w, h: h, pad: pad, right: right,
    cw: cw, ch: ch,
    mx: pad + cw * 0.3, my: 44,
    rx: w - right + 6, ry: 44
  };
}

/* A small arrow from one cell to another, used for the multiplier of a row operation. */
function arrow(x1, y1, x2, y2, col, p) {
  var ex = x1 + (x2 - x1) * p, ey = y1 + (y2 - y1) * p;
  stroke(col[0], col[1], col[2]);
  strokeWeight(1.6);
  line(x1, y1, ex, ey);
  var ang = Math.atan2(ey - y1, ex - x1);
  var s = 6;
  line(ex, ey, ex - s * Math.cos(ang - 0.4), ey - s * Math.sin(ang - 0.4));
  line(ex, ey, ex - s * Math.cos(ang + 0.4), ey - s * Math.sin(ang + 0.4));
  noStroke();
}

function cellCenter(f, i, j) {
  return [f.mx + j * f.cw + f.cw / 2, f.my + i * f.ch + f.ch / 2];
}

var LESSON = {
  steps: [
    {
      duration: 900,
      caption: "Start with A = [[2,3,1],[4,7,7],[-2,4,5]]. LU decomposition says this matrix is a lower triangular L times an upper triangular U. Nothing new is being computed here: elimination already produces U, and the multipliers it uses are the entries of L. The next three steps do the elimination and write L down as we go.",
      draw: function (p, w, h) {
        inkBg();
        var f = layout(w, h);
        label("A, the matrix to factor", f.mx, f.my - 14, 12.5);
        grid(f.mx, f.my, f.cw, f.ch, A, null, null);
        label("Three columns to clear, in order:", f.mx, f.my + 3 * f.ch + 24, 12.5);
        label("column 1 first, then column 2.", f.mx, f.my + 3 * f.ch + 42, 12.5);
        if (f.right > 0) {
          label("Goal: A = L U", f.rx, f.my - 14, 12.5, strongInk());
          label("L lower triangular,", f.rx, f.my + 8, 12);
          label("U upper triangular.", f.rx, f.my + 26, 12);
          label("Both square, both order 3.", f.rx, f.my + 44, 12);
        }
      }
    },
    {
      duration: 1400,
      caption: "Column 1. The pivot is the 2 in position (1,1). To clear the 4 below it we subtract 2 times row 1, and to clear the -2 we add 1 times row 1. Those two numbers, 2 and -1, are the first multipliers, and they go straight into L.",
      draw: function (p, w, h) {
        inkBg();
        var f = layout(w, h);
        label("Column 1: pivot 2, multipliers 4/2 = 2 and -2/2 = -1", f.mx, f.my - 14, 12.5);
        var piv = cellCenter(f, 0, 0);
        grid(f.mx, f.my, f.cw, f.ch, A, function (i, j) {
          return j === 0 && i > 0 ? true : (i === 0 && j === 0);
        }, ORANGE);
        var c1 = cellCenter(f, 1, 0), c2 = cellCenter(f, 2, 0);
        arrow(c1[0], c1[1], piv[0], piv[1], BLUE, p);
        arrow(c2[0], c2[1], piv[0], piv[1], BLUE, p);
        label("L will hold", f.mx, f.my + 3 * f.ch + 24, 12.5);
        label("l21 = 2  and  l31 = -1", f.mx, f.my + 3 * f.ch + 42, 12.5, BLUE);
      }
    },
    {
      duration: 1200,
      caption: "After column 1 the working matrix is [[2,3,1],[0,1,5],[0,7,6]], and L already contains the two multipliers 2 and -1 in its first column. This is the whole trick: L is not solved for afterwards, it is the record of the operations just performed.",
      draw: function (p, w, h) {
        inkBg();
        var f = layout(w, h);
        label("After column 1: the first column is cleared", f.mx, f.my - 14, 12.5);
        grid(f.mx, f.my, f.cw, f.ch, AFTER1, function (i, j) {
          return j === 0 && i > 0;
        }, GREEN);
        if (f.right > 0) {
          label("L so far", f.rx, f.my - 14, 12.5, strongInk());
          grid(f.rx, f.my, f.cw * 0.78, f.ch * 0.78, [[1, 0, 0], [2, 1, 0], [0, 0, 1]],
            function (i, j) { return (i === 1 && j === 0) || (i === 2 && j === 0); }, BLUE);
          label("2 and -1 are the multipliers", f.rx, f.my + 3 * f.ch * 0.78 + 22, 11.5);
        }
      }
    },
    {
      duration: 1400,
      caption: "Column 2. The pivot is now 1, and the 7 below it is cleared by subtracting 7 times row 2, so l32 = 7. The last entry becomes 6 - 7*5 = -29, which is the final pivot. Three multipliers, three row operations, and L is complete.",
      draw: function (p, w, h) {
        inkBg();
        var f = layout(w, h);
        label("Column 2: pivot 1, multiplier 7/1 = 7", f.mx, f.my - 14, 12.5);
        grid(f.mx, f.my, f.cw, f.ch, AFTER1, function (i, j) {
          return (i === 1 && j === 1) || (i === 2 && j === 1);
        }, ORANGE);
        var piv = cellCenter(f, 1, 1), low = cellCenter(f, 2, 1);
        arrow(low[0], low[1], piv[0], piv[1], BLUE, p);
        label("l32 = 7", f.mx, f.my + 3 * f.ch + 24, 12.5, BLUE);
        label("last entry: 6 - 7*5 = -29", f.mx, f.my + 3 * f.ch + 42, 12.5);
      }
    },
    {
      duration: 900,
      caption: "The factorization is finished: L = [[1,0,0],[2,1,0],[-1,7,1]] and U = [[2,3,1],[0,1,5],[0,0,-29]]. U is the matrix elimination produced, and L is unit lower triangular because the diagonal is never a multiplier - the pivots stay on U's diagonal. This is the Doolittle convention.",
      draw: function (p, w, h) {
        inkBg();
        var f = layout(w, h);
        label("L, the multipliers", f.mx, f.my - 14, 12.5, strongInk());
        grid(f.mx, f.my, f.cw * 0.82, f.ch * 0.82, L, function (i, j) {
          return i > j;
        }, BLUE);
        if (f.right > 0) {
          label("U, the pivots", f.rx, f.my - 14, 12.5, strongInk());
          grid(f.rx, f.my, f.cw * 0.82, f.ch * 0.82, U, function (i, j) {
            return i === j;
          }, GREEN);
          label("the diagonal of L is all 1s", f.mx, f.my + 3 * f.ch * 0.82 + 24, 11.5);
        } else {
          label("U = [[2,3,1],[0,1,5],[0,0,-29]]", f.mx, f.my + 3 * f.ch * 0.82 + 24, 11.5);
        }
      }
    },
    {
      duration: 1200,
      caption: "Check one entry rather than the whole product. Entry (3,2) of A should be row 3 of L times column 2 of U: (-1)(3) + (7)(1) + (1)(0) = 4, and the (3,2) entry of A is indeed 4. One dot product per entry is the fastest way to catch a sign error in a multiplier.",
      draw: function (p, w, h) {
        inkBg();
        var f = layout(w, h);
        label("Row 3 of L  times  column 2 of U", f.mx, f.my - 14, 12.5);
        var i;
        for (i = 0; i < 3; i++) {
          var cL = cellCenter(f, 2, i);
          noStroke();
          fill(cellFill(true));
          stroke(cellEdge());
          rect(f.mx + i * f.cw, f.my + 2 * f.ch, f.cw, f.ch, 4);
          noStroke();
          textAlign('center', 'center');
          textSize(Math.max(11, Math.min(17, f.ch * 0.42)));
          fill(BLUE[0], BLUE[1], BLUE[2]);
          text(fmt(L[2][i]), cL[0], cL[1]);
        }
        textAlign('left', 'baseline');
        label("(-1)(3) + (7)(1) + (1)(0) = 4", f.mx, f.my + 3 * f.ch + 26, 12.5, strongInk());
        label("and A[3][2] = 4", f.mx, f.my + 3 * f.ch + 44, 12.5, GREEN);
        if (f.right > 0) {
          label("column 2 of U", f.rx, f.my - 14, 12.5, strongInk());
          label("3", f.rx, f.my + 6, 13, strongInk());
          label("1", f.rx, f.my + 26, 13, strongInk());
          label("0", f.rx, f.my + 46, 13, strongInk());
        }
      }
    },
    {
      duration: 1000,
      caption: "The determinant comes free from the pivots: det(A) = 2 * 1 * (-29) = -58, and the direct determinant of A is also -58. A triangular determinant is the product of its diagonal, L has determinant 1, so only U carries the value - and no row was swapped here, so there is no sign to correct.",
      draw: function (p, w, h) {
        inkBg();
        var f = layout(w, h);
        label("det(A) = product of the pivots", f.mx, f.my - 14, 12.5, strongInk());
        grid(f.rx > 0 ? f.mx : f.mx, f.my, f.cw * 0.82, f.ch * 0.82, U, function (i, j) {
          return i === j;
        }, GREEN);
        label("2 * 1 * (-29) = -58", f.mx, f.my + 3 * f.ch * 0.82 + 24, 13, strongInk());
        label("det(L) = 1, no row swap, so det(A) = det(U)", f.mx, f.my + 3 * f.ch * 0.82 + 44, 11.5);
      }
    },
    {
      duration: 900,
      caption: "One last case, because it is where elimination fails. For A = [[0,2],[1,3]] the first pivot is 0 and no multiplier can clear the 1 with it. Swap the rows instead: P records the swap, PA = [[1,3],[0,2]] is already upper triangular, L = I, and det(A) = (-1)(2) = -2. With a permutation the factorization always exists.",
      draw: function (p, w, h) {
        inkBg();
        var f = layout(w, h);
        label("Zero pivot: swap, and write PA = LU", f.mx, f.my - 14, 12.5, strongInk());
        grid(f.mx, f.my, f.cw * 0.8, f.ch * 0.8, [[0, 2], [1, 3]], function (i, j) {
          return j === 0;
        }, RED);
        label("A", f.mx + 2 * f.cw * 0.8 + 10, f.my + f.ch * 0.8, 12.5);
        if (f.right > 0) {
          grid(f.rx, f.my, f.cw * 0.8, f.ch * 0.8, [[1, 3], [0, 2]], function (i, j) {
            return i === j;
          }, GREEN);
          label("PA = LU, with L = I", f.rx, f.my + 2 * f.ch * 0.8 + 22, 11.5);
          label("det(P) = -1, det(A) = -2", f.rx, f.my + 2 * f.ch * 0.8 + 40, 11.5);
        } else {
          label("PA = [[1,3],[0,2]], det(A) = -2", f.mx, f.my + 2 * f.ch * 0.8 + 24, 11.5);
        }
      }
    }
  ]
};

window.LESSON = LESSON;
