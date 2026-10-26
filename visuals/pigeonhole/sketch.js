/* Pigeonhole principle: guarantee, not probability.
   Verified example: 4 suits, force 3 of a suit -> 4*(3-1)+1 = 9 cards. */
window.LESSON = {
  steps: [
    {
      duration: 1500,
      caption: 'Four suits are four boxes. The question is not "how likely" - it is "how many cards force three of one suit".',
      draw: function (p, w, h) {
        ink(); title('Four suits, four boxes', 40, 40);
        var names = ['C', 'H', 'S', 'D'];
        for (var i = 0; i < 4; i++) suitPanel(70 + i * 120, 110, 100, 150, names[i], 0, p);
        label('worst case is what decides a guarantee', 40, h - 40);
      }
    },
    {
      duration: 1800,
      caption: 'Worst case: two cards in every suit. That is 8 cards and still no suit holds three.',
      draw: function (p, w, h) {
        ink(); title('Worst case: 2 per suit = 8 cards', 40, 40);
        var names = ['C', 'H', 'S', 'D'];
        for (var i = 0; i < 4; i++) {
          var shown = Math.min(2, Math.floor(p * 8 - i * 2) + 1);
          suitPanel(70 + i * 120, 110, 100, 150, names[i], Math.max(0, Math.min(2, shown)), 1);
        }
        label('8 cards, no suit at three - so 8 is not enough', 40, h - 40);
      }
    },
    {
      duration: 1600,
      caption: 'The ninth card must join one of the four suits, and that suit already has two. So 9 is the answer: k(r-1) + 1 = 4 x 2 + 1.',
      draw: function (p, w, h) {
        ink(); title('The ninth card forces it', 40, 40);
        var names = ['C', 'H', 'S', 'D'];
        for (var i = 0; i < 4; i++) suitPanel(70 + i * 120, 110, 100, 150, names[i], 2, 1);
        if (p > 0.15) {
          stroke(180, 69, 31); strokeWeight(3); noFill();
          rect(66 + 1 * 120, 106, 108, 158, 10);
          noStroke(); fill(180, 69, 31); textSize(13);
          text('this suit now holds 3', 80 + 120, 290);
        }
        textSize(18); fill(20, 107, 74); noStroke();
        text('k(r - 1) + 1 = 4 x 2 + 1 = 9', 70, h - 40);
      }
    },
    {
      duration: 1800,
      caption: 'Why 8 fails and 9 works is the whole principle: the guarantee comes from the worst arrangement, never from an average or a probability.',
      draw: function (p, w, h) {
        ink(); title('Guarantee vs probability', 40, 40);
        textSize(15); fill(74, 82, 96); noStroke();
        text('With 8 cards: the split 2,2,2,2 is realisable, so three-of-a-suit is NOT guaranteed.', 60, 100);
        text('With 9 cards: every split of 9 into 4 parts has some part >= ceil(9/4) = 3.', 60, 132);
        text('Generalised form: N objects in k boxes forces ceil(N/k) in some box.', 60, 176);
        text('"Exactly 3" is a different claim and is generally false.', 60, 208);
        textSize(18); fill(20, 107, 74);
        text('Minimum to guarantee r in some box:  k(r - 1) + 1', 60, 260);
      }
    }
  ]
};

function ink() { background(255); }
function title(t, x, y) { noStroke(); fill(20, 24, 31); textSize(18); textStyle(BOLD); text(t, x, y); textStyle(NORMAL); }
function label(t, x, y) { noStroke(); fill(90, 99, 114); textSize(14); text(t, x, y); }
function suitPanel(x, y, w, h, tag, cards, p) {
  stroke(200, 206, 216); strokeWeight(1.4); fill(246, 247, 249); rect(x, y, w, h, 10);
  noStroke(); fill(120, 130, 145); textSize(13); text(tag, x + 8, y + h - 8);
  for (var i = 0; i < cards; i++) {
    stroke(31, 94, 255); strokeWeight(1.4); fill(255);
    rect(x + 12 + (i % 2) * 40, y + 16 + Math.floor(i / 2) * 54, 32, 46, 4);
  }
}
