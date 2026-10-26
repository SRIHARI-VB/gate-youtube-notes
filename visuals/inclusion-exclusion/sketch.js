/* Inclusion-exclusion, then derangements.
   Verified numbers: |A|=6, |B|=5, |A n B|=2  ->  |A u B| = 9.
   Derangements of ABC: 6 permutations, 2 derangements (BCA, CAB). */
window.LESSON = {
  steps: [
    {
      duration: 1400,
      caption: 'Two overlapping sets. The shaded lens is |A intersect B| = 2, so |A| = 6 and |B| = 5.',
      draw: function (p, w, h) {
        ink(); title('Two sets', 40, 40);
        circles(1);
        label('|A| = 6', 70, h - 40); label('|B| = 5', 300, h - 40); label('|A n B| = 2', 200, h - 64);
      }
    },
    {
      duration: 1600,
      caption: 'Add |A| + |B| = 11. Every element of the lens has now been counted twice.',
      draw: function (p, w, h) {
        ink(); title('Add both sets: 6 + 5 = 11', 40, 40);
        circles(2);
        noStroke(); fill(180, 69, 31, 120); ellipse(255, 170, 96 * p + 10, 130 * p + 10);
        label('the lens is counted twice', 40, h - 40);
      }
    },
    {
      duration: 1600,
      caption: 'Subtract the lens once: 6 + 5 - 2 = 9. Every element is now counted exactly once.',
      draw: function (p, w, h) {
        ink(); title('Subtract it once: 6 + 5 - 2 = 9', 40, 40);
        circles(1);
        noStroke(); fill(20, 107, 74, 150); ellipse(255, 170, 90, 126);
        textSize(22); fill(20, 107, 74); noStroke(); text('9', 246, 178);
        label('|A u B| = |A| + |B| - |A n B|', 40, h - 40);
      }
    },
    {
      duration: 1800,
      caption: 'With three sets the signs alternate: add singles, subtract pairs, add the triple back. Elements in all three were added 3 times and subtracted 3 times, so they need one more add.',
      draw: function (p, w, h) {
        ink(); title('Three sets: + - +', 40, 40);
        var cx = 250, cy = 170, r = 78;
        stroke(160); noFill();
        circle(cx - 40, cy - 26, r * 2); circle(cx + 40, cy - 26, r * 2); circle(cx, cy + 34, r * 2);
        noStroke(); fill(31, 94, 255, 40); circle(cx - 40, cy - 26, r * 2);
        fill(180, 69, 31, 40); circle(cx + 40, cy - 26, r * 2);
        fill(20, 107, 74, 40); circle(cx, cy + 34, r * 2);
        textSize(15); fill(74, 82, 96); noStroke();
        text('|A u B u C| = sum singles - sum pairs + triple', 40, h - 40);
      }
    },
    {
      duration: 2000,
      caption: 'Derangements are inclusion-exclusion in disguise. Of the six permutations of ABC, cross out every one with a fixed point: only BCA and CAB survive, so !3 = 2.',
      draw: function (p, w, h) {
        ink(); title('Derangements of ABC', 40, 40);
        var perms = [['A','B','C',0],['A','C','B',1],['B','A','C',1],['B','C','A',0],['C','A','B',1],['C','B','A',1]];
        for (var i = 0; i < perms.length; i++) {
          var x = 60 + (i % 3) * 160, y = 110 + Math.floor(i / 3) * 90;
          var pm = perms[i];
          var shown = Math.min(1, Math.max(0, p * 2 - i * 0.12));
          if (shown <= 0) continue;
          stroke(200); fill(246, 247, 249); rect(x, y - 26, 118, 52, 8);
          noStroke(); fill(20, 24, 31); textSize(20);
          text(pm[0] + pm[1] + pm[2], x + 14, y + 7);
          if (pm[3] === 1) {
            stroke(180, 69, 31); strokeWeight(3);
            line(x + 6, y - 30, x + 112, y + 30); noStroke();
            fill(180, 69, 31); textSize(11); text('fixed point', x + 18, y + 40);
          } else {
            fill(20, 107, 74); textSize(11); text('derangement', x + 18, y + 40);
          }
        }
        textSize(16); fill(74, 82, 96); noStroke();
        text('!3 = 6 - 3 + 0 = 2   (nearest integer to 3!/e)', 60, h - 26);
      }
    }
  ]
};

function ink() { background(255); }
function title(t, x, y) { noStroke(); fill(20, 24, 31); textSize(18); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function label(t, x, y) { noStroke(); fill(90, 99, 114); textSize(14); text(t, x, y); }
function circles(lensOn) {
  stroke(31, 94, 255); strokeWeight(2); noFill();
  circle(180, 170, 210);
  stroke(180, 69, 31);
  circle(330, 170, 180);
  noStroke();
}
