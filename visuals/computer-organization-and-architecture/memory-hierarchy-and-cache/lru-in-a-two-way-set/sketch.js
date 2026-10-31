/* LRU inside a 2-way set, for the Memory Hierarchy and Cache Mapping topic.

   The picture is fixed for the whole lesson:

     a cache of 2 sets, 2 ways each, so four lines
     block b goes to set b mod 2
     the reference string 0, 1, 2, 3, 0, 4, 0 under LRU

   Every state after every access, the evicted block at each miss, and the
   miss and hit counts are listed in lesson.json and recomputed in
   scripts/validate.py (check_memory_hierarchy_and_cache), not derived here.
   The list order in each set is LRU first, MRU last. */

var SETS = 2, WAYS = 2;
var REF = [0, 1, 2, 3, 0, 4, 0];

/* State after each access: [set0 order LRU..MRU, set1 order LRU..MRU]. */
var STATE = [
  [[0], []],
  [[0], [1]],
  [[0, 2], [1]],
  [[0, 2], [1, 3]],
  [[2, 0], [1, 3]],
  [[0, 4], [1, 3]],
  [[4, 0], [1, 3]]
];
var RESULT = ['miss', 'miss', 'miss', 'miss', 'hit', 'miss', 'hit'];
var EVICT = [null, null, null, null, null, 2, null];

function ink() {
  background(255);
  stroke(210);
  strokeWeight(1);
  fill(40);
}

function head(t) {
  fill(28); textSize(17); textStyle(BOLD); textAlign(LEFT, TOP); text(t, 22, 20); textStyle(NORMAL);
}

function note(t, y) {
  fill(74, 82, 96); textSize(13); textAlign(LEFT, TOP); text(t, 22, y);
}

/* Draw the reference string with the current access highlighted. */
function string(w, cur, y) {
  var left = 22, cw = 44;
  fill(74, 82, 96); textSize(12); textAlign(LEFT, TOP);
  text('reference string', left, y);
  for (var i = 0; i < REF.length; i++) {
    var x = left + i * cw;
    if (i === cur) { fill(198, 216, 240); stroke(80); }
    else if (i < cur) { fill(240); stroke(200); }
    else { fill(252); stroke(220); }
    rect(x, y + 18, cw - 6, 28);
    noStroke();
    fill(40); textSize(13); textAlign(CENTER, CENTER);
    text(String(REF[i]), x + (cw - 6) / 2, y + 32);
    stroke(210);
  }
  noStroke();
}

/* Draw the two sets, each with two ways, LRU on the left. */
function sets(w, state, y) {
  var x0 = 22, rowH = 62, boxW = 120;
  for (var s = 0; s < SETS; s++) {
    var yy = y + s * rowH;
    fill(74, 82, 96); textSize(12); textAlign(LEFT, TOP);
    text('set ' + s, x0, yy + 4);
    text('(blocks with block mod 2 = ' + s + ')', x0, yy + 22);
    for (var wI = 0; wI < WAYS; wI++) {
      var x = x0 + 180 + wI * (boxW + 10);
      var has = wI < state[s].length;
      if (has) { fill(232, 242, 236); stroke(120); }
      else { fill(250); stroke(210); }
      rect(x, yy, boxW, 40);
      noStroke();
      fill(40); textSize(13); textAlign(CENTER, CENTER);
      text(has ? ('block ' + state[s][wI]) : 'empty', x + boxW / 2, yy + 20);
      stroke(210);
      fill(110); textSize(10); textAlign(CENTER, TOP);
      text(wI === 0 ? 'LRU end' : 'MRU end', x + boxW / 2, yy + 42);
    }
  }
  noStroke();
}

function verdict(w, cur, y) {
  var ok = RESULT[cur] === 'hit';
  fill(ok ? 226 : 250, ok ? 240 : 232, ok ? 230 : 228);
  stroke(ok ? 130 : 190);
  rect(22, y, w - 44, 46);
  noStroke();
  fill(40); textSize(13); textAlign(LEFT, TOP);
  var line = 'access ' + (cur + 1) + ': block ' + REF[cur] + ' goes to set ' + (REF[cur] % SETS) + ' - ' + RESULT[cur];
  if (EVICT[cur] !== null) { line += ', evicting block ' + EVICT[cur]; }
  text(line, 34, y + 8);
  var second = ok
    ? 'A hit refreshes the block to the MRU end of its set; nothing is evicted.'
    : (EVICT[cur] !== null
      ? 'The set was full, so LRU chose the block whose last use was furthest back.'
      : 'The set had a free way, so the block simply fills it.');
  text(second, 34, y + 26);
}

window.LESSON = {
  steps: [
    {
      duration: 5000,
      caption: 'A cache of two sets with two ways each, so four lines in all, and a reference string of seven block accesses. Block b always goes to set b mod 2, so the even blocks 0, 2 and 4 share set 0 and the odd blocks 1 and 3 share set 1. Nothing has been accessed yet and every way is empty.',
      draw: function (p, w, h) {
        ink();
        head('Two sets, two ways, seven accesses');
        string(w, -1, 50);
        sets(w, [[], []], 120);
        note('Each set can hold two blocks at a time. When a third block arrives, one of the two must go.', h - 30);
      }
    },
    {
      duration: 4400,
      caption: 'Block 0 is requested. It maps to set 0, both ways there are empty, and it is a compulsory miss: the block is fetched and placed in the first way. Set 0 now holds one block and set 1 is still empty.',
      draw: function (p, w, h) {
        ink();
        head('Access 1: block 0, a compulsory miss');
        string(w, 0, 50);
        sets(w, STATE[0], 120);
        verdict(w, 0, h - 70);
      }
    },
    {
      duration: 4400,
      caption: 'Block 1 is requested and maps to set 1, which is empty, so it fills a way there. Two misses so far, and both are compulsory - the first touch of a block can never be anything else.',
      draw: function (p, w, h) {
        ink();
        head('Access 2: block 1, another compulsory miss');
        string(w, 1, 50);
        sets(w, STATE[1], 120);
        verdict(w, 1, h - 70);
      }
    },
    {
      duration: 4600,
      caption: 'Block 2 maps to set 0, which still has a free way, so it is placed beside block 0 with no eviction. Set 0 is now full: two blocks in two ways. Block 0 is the least recently used of the pair, because block 2 has just been used.',
      draw: function (p, w, h) {
        ink();
        head('Access 3: block 2 fills set 0');
        string(w, 2, 50);
        sets(w, STATE[2], 120);
        verdict(w, 2, h - 70);
      }
    },
    {
      duration: 4400,
      caption: 'Block 3 fills the second way of set 1. Both sets are now full, so every further miss must evict something, and from here the answer depends on the replacement policy - LRU is what this trace follows.',
      draw: function (p, w, h) {
        ink();
        head('Access 4: block 3 fills set 1');
        string(w, 3, 50);
        sets(w, STATE[3], 120);
        verdict(w, 3, h - 70);
      }
    },
    {
      duration: 5000,
      caption: 'Block 0 again. It is still in set 0, so this is a hit - and the important part of a hit under LRU is that block 0 becomes the most recently used block of its set. Block 2 is now the one whose last use is furthest back. That reordering is the step candidates skip when they treat LRU as first-in-first-out.',
      draw: function (p, w, h) {
        ink();
        head('Access 5: block 0 hits, and becomes MRU');
        string(w, 4, 50);
        sets(w, STATE[4], 120);
        verdict(w, 4, h - 70);
        note('After the hit, set 0 is ordered [2, 0]: 2 is LRU, 0 is MRU.', h - 24);
      }
    },
    {
      duration: 5400,
      caption: 'Block 4 arrives at set 0, which is full, so one of its two blocks must go. LRU compares last-use times, not load times: block 0 was used one access ago and block 2 four accesses ago, so block 2 is evicted even though both were loaded at about the same point in the trace. Note what this miss is and is not: block 4 has never been touched before, so the miss is compulsory - the eviction of block 2 is a consequence of set pressure, not the cause of the miss. Set 1 had two free ways the whole time.',
      draw: function (p, w, h) {
        ink();
        head('Access 6: block 4 evicts block 2');
        string(w, 5, 50);
        sets(w, STATE[5], 120);
        verdict(w, 5, h - 70);
      }
    },
    {
      duration: 5200,
      caption: 'Block 0 once more, and it hits again: it survived precisely because it was the more recently used of the two. The trace ends with five misses and two hits, and all five misses are compulsory: blocks 0, 1, 2, 3 and 4 are each touched for the first time exactly once. Not one of them is a conflict or a capacity miss, even though an eviction did happen - an eviction is not a miss, and no cache of any size could have avoided the first touch of a block.',
      draw: function (p, w, h) {
        ink();
        head('Access 7: block 0 hits again - 5 misses, 2 hits');
        string(w, 6, 50);
        sets(w, STATE[6], 120);
        verdict(w, 6, h - 70);
        note('Five compulsory misses and no conflict miss; every hit refreshed the recency order.', h - 24);
      }
    }
  ]
};
