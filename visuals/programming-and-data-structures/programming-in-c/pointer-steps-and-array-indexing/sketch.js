/* Pointer steps and array indexing.
   Every number here is recomputed in scripts/validate.py (check_c_programming):
     int a[5] = {10, 20, 30, 40, 50} with sizeof(int) = 4 and a at address 2000,
     so a[0]..a[4] occupy 2000, 2004, 2008, 2012, 2016 and each element is 4 bytes wide;
     *(a + 2) is a[2] = 30 and 2[a] is the same object;
     with p = a + 3 and q = a + 1, p - q = 2 elements although the addresses differ by 8 bytes. */
window.LESSON = {
  steps: [
    {
      duration: 2600,
      caption: 'Five ints live in one contiguous block. With 4-byte ints and the array starting at address 2000, the elements sit at 2000, 2004, 2008, 2012 and 2016 - four bytes apart, not one.',
      draw: function (p, w, h) {
        ink();
        head('An array is one block of equal cells', 30, 34);
        cells(w, 150, -1, null);
        note('Each cell is sizeof(int) = 4 bytes. The last byte of a[0] is 2003, so a[1] starts at 2004.', 30, h - 26);
      }
    },
    {
      duration: 2600,
      caption: 'A pointer holds one of those addresses. p = a copies the address of the first element into p, because an array name decays to &a[0] in an expression.',
      draw: function (p, w, h) {
        ink();
        head('p = a: the pointer holds 2000', 30, 34);
        var g = cells(w, 150, 0, null);
        ptrBox(g, 'p', '2000', 0);
        arrow(g.x[0] + g.cw / 2, g.y - 20, g.x[0] + g.cw / 2, g.y - 4);
        note('The arrow is the stored address. Following it once is *p, which is a[0] = 10.', 30, h - 26);
      }
    },
    {
      duration: 3200,
      caption: 'p + 1 does not add one byte. The compiler scales the step by the size of what p points at, so p + 1 adds 4 bytes and lands on a[1], the second element.',
      draw: function (p, w, h) {
        ink();
        head('p + 1 adds sizeof(int) bytes', 30, 34);
        var g = cells(w, 150, 1, null);
        var step = Math.min(1, Math.max(0, p));
        var from = g.x[0] + g.cw / 2, to = g.x[1] + g.cw / 2;
        var at = from + (to - from) * step;
        ptrBox(g, 'p', step < 0.5 ? '2000' : '2004', 0);
        arrow(at, g.y - 20, at, g.y - 4);
        textSize(12.5); fill(180, 90, 31); noStroke();
        text('+4 bytes, not +1', from + 8, g.y - 26);
        ruler(g);
        note('Bytes 2001, 2002 and 2003 belong to the same int as 2000. Adding 1 to a byte address would land inside an int.', 30, h - 26);
      }
    },
    {
      duration: 4200,
      caption: 'Walk the pointer instead of indexing. Starting at a, each p++ moves 4 bytes and *p reads the next value: 10, then 20, 30, 40, 50. Five steps of 4 bytes cover the whole array.',
      draw: function (p, w, h) {
        ink();
        head('Walking with p reads 10, 20, 30, 40, 50', 30, 34);
        var k = Math.min(4, Math.floor(Math.min(1, Math.max(0, p)) * 5));
        var g = cells(w, 150, k, null);
        ptrBox(g, 'p', String(2000 + 4 * k), 0);
        arrow(g.x[k] + g.cw / 2, g.y - 20, g.x[k] + g.cw / 2, g.y - 4);
        textSize(13); fill(20, 24, 31); noStroke();
        text('*p = ' + [10, 20, 30, 40, 50][k], 30, g.y + g.ch + 64);
        note('p has moved ' + (4 * k) + ' bytes from 2000, which is ' + k + ' element(s) of 4 bytes.', 30, h - 26);
      }
    },
    {
      duration: 3400,
      caption: 'a[i] is defined as *(a + i), so the index form and the pointer form name the same object. a[2], *(a + 2) and even 2[a] all reach the box holding 30.',
      draw: function (p, w, h) {
        ink();
        head('a[i] and *(a + i) are one object', 30, 34);
        var g = cells(w, 190, 2, null);
        textSize(13.5); fill(31, 94, 255); noStroke();
        text('a[2]', g.x[2], g.y - 64);
        text('*(a + 2)', g.x[2] + 50, g.y - 64);
        text('2[a]', g.x[2] + 128, g.y - 64);
        arrow(g.x[2] + 12, g.y - 56, g.x[2] + 12, g.y - 4);
        arrow(g.x[2] + 66, g.y - 56, g.x[2] + 66, g.y - 4);
        arrow(g.x[2] + 138, g.y - 56, g.x[2] + 138, g.y - 4);
        note('Both expand to *(a + 2): the subscript operator is defined that way, and integer plus pointer is commutative.', 30, h - 26);
      }
    },
    {
      duration: 3600,
      caption: 'Subtracting two pointers counts elements, not bytes. p sits at a[3] and q at a[1], so p - q is 2 even though the addresses 2012 and 2004 differ by 8.',
      draw: function (p, w, h) {
        ink();
        head('p - q is 2, although the addresses differ by 8', 30, 34);
        var g = cells(w, 200, -1, [1, 3]);
        ptrBox(g, 'q', '2004', 0);
        ptrBox(g, 'p', '2012', 1);
        arrow(g.x[1] + g.cw / 2, g.y - 20, g.x[1] + g.cw / 2, g.y - 4);
        arrow(g.x[3] + g.cw / 2, g.y - 58, g.x[3] + g.cw / 2, g.y - 4);
        textSize(13); fill(180, 90, 31); noStroke();
        text('2012 - 2004 = 8 bytes, divided by sizeof(int) = 4, gives 2 elements', 30, g.y + g.ch + 64);
        note('This is why (int)(q - p) is 1 in GATE CSE 2024 Set 2 Q.26, where the elements are 8-byte doubles.', 30, h - 26);
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

function geometry(w) {
  var n = 5, gap = 12, cw = Math.min(112, (w - 120 - 4 * gap) / n), ch = 66;
  var total = n * cw + (n - 1) * gap;
  var x0 = (w - total) / 2 + 30;
  var xs = [];
  for (var i = 0; i < n; i++) { xs.push(x0 + i * (cw + gap)); }
  return { n: n, cw: cw, ch: ch, x: xs, y: 150 };
}

function cells(w, y, hi, also) {
  var g = geometry(w);
  g.y = y;
  var vals = [10, 20, 30, 40, 50];
  for (var i = 0; i < g.n; i++) {
    var on = (i === hi) || (also && also.indexOf(i) >= 0);
    stroke(on ? color(31, 94, 255) : color(214, 220, 230));
    strokeWeight(on ? 2.5 : 1);
    fill(on ? color(232, 238, 255) : color(250, 251, 253));
    rect(g.x[i], g.y, g.cw, g.ch, 8);
    noStroke(); fill(20, 24, 31); textSize(15); textAlign('center', 'center');
    text(String(vals[i]), g.x[i] + g.cw / 2, g.y + g.ch / 2 - 8);
    fill(120, 128, 140); textSize(11);
    text('a[' + i + ']', g.x[i] + g.cw / 2, g.y + 14);
    fill(90, 100, 116); textSize(10.5);
    text(String(2000 + 4 * i), g.x[i] + g.cw / 2, g.y + g.ch + 14);
    textAlign('left', 'baseline');
  }
  return g;
}

function ptrBox(g, name, val, row) {
  var bx = 26, bw = 132, bh = 30;
  var by = g.y - 50 - (row || 0) * 38;
  noStroke(); fill(31, 94, 255);
  rect(bx, by, bw, bh, 6);
  fill(255); textSize(12.5);
  text(name + ' = ' + val, bx + 10, by + 20);
}

function arrow(x1, y1, x2, y2) {
  stroke(31, 94, 255); strokeWeight(1.6);
  line(x1, y1, x2, y2);
  line(x2, y2, x2 - 4, y2 - 7);
  line(x2, y2, x2 + 4, y2 - 7);
  noStroke();
}

function ruler(g) {
  var y = g.y + g.ch + 36;
  stroke(206, 212, 222); strokeWeight(1);
  line(g.x[0], y, g.x[1] + g.cw, y);
  noStroke(); fill(120, 128, 140); textSize(10);
  var labels = ['2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007'];
  for (var i = 0; i < labels.length; i++) {
    var x = g.x[0] + (i + 0.5) * (g.cw / 4);
    stroke(206, 212, 222); strokeWeight(1);
    line(x, y - 4, x, y + 4);
    noStroke(); text(labels[i], x - 12, y + 18);
  }
  stroke(180, 90, 31); strokeWeight(2);
  line(g.x[0], y - 12, g.x[0] + g.cw, y - 12);
  noStroke(); fill(180, 90, 31); textSize(11);
  text('one int: 4 bytes', g.x[0], y - 18);
}
