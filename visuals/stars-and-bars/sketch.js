/* Stars and bars: n identical objects into k distinct boxes.
   Mathematics: number of arrangements of n stars and (k-1) bars is C(n+k-1, k-1).
   Verified example: n = 5, k = 3  ->  C(7,2) = 21. */
var N = 5, K = 3;
var EXAMPLES = [
  { stars: [2, 3, 0], note: '(2, 3, 0)' },
  { stars: [0, 0, 5], note: '(0, 0, 5)' },
  { stars: [1, 2, 2], note: '(1, 2, 2)' }
];

window.LESSON = {
  steps: [
    {
      duration: 1400,
      caption: 'Five identical sweets and three children. Because the sweets are identical, only the counts matter - not which sweet goes where.',
      draw: function (p, w, h) {
        ink(w, h);
        title('5 identical sweets', 40, 46);
        for (var i = 0; i < N; i++) star(80 + i * 46, 110 + Math.sin(p * 6 + i) * 3, 15);
        label('3 children: A, B, C', 40, 180);
        for (var c = 0; c < K; c++) panel(80 + c * 120, 210, 100, 60, String.fromCharCode(65 + c));
      }
    },
    {
      duration: 1600,
      caption: 'Line the sweets up as stars and drop k-1 = 2 bars between them. The bars are the boundaries between children.',
      draw: function (p, w, h) {
        ink(w, h);
        title('Stars and bars', 40, 46);
        for (var i = 0; i < N; i++) star(80 + i * 46, 100, 15);
        // two bars animate in
        barPositions(p, function (x) { bar(x, 100); });
        label('each arrangement of 5 stars and 2 bars = one distribution', 40, 190);
        var ex = EXAMPLES[0];
        label('here: ' + ex.note + '  ->  A gets 2, B gets 3, C gets 0', 40, 220);
      }
    },
    {
      duration: 1600,
      caption: 'A different bar placement is a different distribution. These three all use the same five sweets.',
      draw: function (p, w, h) {
        ink(w, h);
        title('Same stars, different bars', 40, 46);
        for (var e = 0; e < EXAMPLES.length; e++) {
          var y = 100 + e * 80;
          var shown = Math.min(1, Math.max(0, p * 3 - e));
          if (shown <= 0) continue;
          drawRow(EXAMPLES[e].stars, y);
          label(EXAMPLES[e].note, 480, y + 6);
        }
        label('three of the twenty-one possible distributions', 40, 350);
      }
    },
    {
      duration: 1800,
      caption: 'Counting: 5 + 2 = 7 positions in total, and we choose which 2 of them hold bars. That is C(7,2) = 21.',
      draw: function (p, w, h) {
        ink(w, h);
        title('Count the positions', 40, 46);
        var total = N + (K - 1);
        for (var i = 0; i < total; i++) {
          var x = 70 + i * 60;
          var isBar = (i === 1 || i === 5);
          noFill(); stroke(140); strokeWeight(1.2); rect(x - 20, 78, 44, 44, 8);
          if (isBar) bar(x + 2, 100); else star(x + 2, 100, 13);
        }
        label('choose 2 of 7 slots for the bars:', 40, 170);
        textSize(22); fill(31, 94, 255); noStroke();
        text('C(7, 2) = 21', 70, 210);
        label('the other 5 slots are forced to be stars', 40, 240);
      }
    },
    {
      duration: 1800,
      caption: 'General rule: n identical objects into k distinct boxes, empty boxes allowed, is C(n+k-1, k-1). Every "at least one" question first gives one object to each box.',
      draw: function (p, w, h) {
        ink(w, h);
        title('The general rule', 40, 46);
        textSize(24); fill(31, 94, 255); noStroke();
        text('C(n + k - 1, k - 1)', 70, 100);
        textSize(16); fill(74, 82, 96);
        text('n = ' + N + ', k = ' + K + '   ->   C(7, 2) = 21', 70, 134);
        text('each box needs at least one:  C(n - 1, k - 1) = C(4, 2) = 6', 70, 170);
        label('Quick check: 5 identical sweets, 3 children, every child gets at least one?', 40, 220);
        textSize(18); fill(20, 107, 74); noStroke();
        text('Answer: 6   (2,2,1), (2,1,2), (1,2,2), (3,1,1), (1,3,1), (1,1,3)', 70, 250);
      }
    }
  ]
};

function ink(w, h) { background(255); }
function title(t, x, y) { noStroke(); fill(20, 24, 31); textSize(18); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function label(t, x, y) { noStroke(); fill(90, 99, 114); textSize(14); text(t, x, y); }
function star(x, y, r) {
  fill(31, 94, 255); noStroke(); beginShape();
  for (var i = 0; i < 10; i++) {
    var a = -Math.PI / 2 + i * Math.PI / 5;
    var rr = i % 2 === 0 ? r : r * 0.44;
    vertex(x + rr * Math.cos(a), y + rr * Math.sin(a));
  }
  endShape(CLOSE);
}
function bar(x, y) { stroke(180, 69, 31); strokeWeight(5); strokeCap(ROUND); line(x, y - 22, x, y + 22); noStroke(); }
function panel(x, y, w, h, tag) {
  stroke(200, 206, 216); strokeWeight(1.4); fill(246, 247, 249); rect(x, y, w, h, 10);
  noStroke(); fill(120, 130, 145); textSize(13); text(tag, x + 8, y + h - 8);
}
function barPositions(p, drawBar) {
  // two bars drop into the gaps after the 2nd and the 5th star
  var targets = [80 + 2 * 46 - 23, 80 + 5 * 46 - 23];
  for (var i = 0; i < targets.length; i++) {
    var local = Math.min(1, Math.max(0, p * 2 - i));
    if (local > 0) {
      var y = lerp(10, 100, local);
      bar(targets[i], y);
    }
  }
}
function drawRow(counts, y) {
  var x = 80;
  for (var b = 0; b < counts.length; b++) {
    for (var s = 0; s < counts[b]; s++) { star(x, y, 12); x += 34; }
    if (b < counts.length - 1) { bar(x - 12, y); }
    x += 16;
  }
}
