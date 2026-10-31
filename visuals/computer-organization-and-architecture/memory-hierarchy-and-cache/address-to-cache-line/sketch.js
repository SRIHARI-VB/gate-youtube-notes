/* One address, three caches: how tag, index and offset split, for the
   Memory Hierarchy and Cache Mapping topic.

   The picture is fixed for the whole lesson:

     one 32-bit byte address, 0xA248
     one cache of 2 KB of data with 64 B blocks, so 32 lines
     three organisations of that same cache: direct (1 way), 4-way, fully associative

   The three field widths, the three tag values and the line and set the address
   lands in are listed in lesson.json and recomputed in scripts/validate.py
   (check_memory_hierarchy_and_cache), not derived from this file. */

var ADDR_HEX = '0xA248';
var ADDR = 0xA248;
var W = 32;                      // address width in bits

var ORG = [
  { name: 'direct mapped', ways: 1,  sets: 32, indexBits: 5, tagBits: 21, tag: 20,  index: 9, offset: 8,
    where: 'line 9', comps: 'one 21-bit comparator', note: 'one line, so the index is the whole line number' },
  { name: '4-way set associative', ways: 4, sets: 8, indexBits: 3, tagBits: 23, tag: 81, index: 1, offset: 8,
    where: 'set 1', comps: 'four 23-bit comparators', note: 'the index names a set of four lines' },
  { name: 'fully associative', ways: 32, sets: 1, indexBits: 0, tagBits: 26, tag: 649, index: 0, offset: 8,
    where: 'the single set', comps: 'thirty-two 26-bit comparators', note: 'one set, so there is no index field at all' }
];

var C_OFF = [214, 232, 214];     // offset: green
var C_IDX = [246, 214, 156];     // index: amber
var C_TAG = [198, 216, 240];     // tag: blue

function ink() {
  background(255);
  stroke(210);
  strokeWeight(1);
  fill(40);
}

function head(t) { fill(28); textSize(17); textStyle(BOLD); textAlign(LEFT, TOP); text(t, 22, 20); textStyle(NORMAL); }

function note(t, y) {
  fill(74, 82, 96);
  textSize(13);
  textAlign(LEFT, TOP);
  text(t, 22, y);
}

function bin(n, width) {
  var s = '';
  for (var i = width - 1; i >= 0; i--) { s += ((n >> i) & 1) ? '1' : '0'; }
  return s;
}

/* Draw the 32 address bits as cells coloured by the field they belong to. */
function strip(w, o, y) {
  var left = 22, avail = w - 44, cw = avail / W;
  var b = bin(ADDR, W);
  for (var i = 0; i < W; i++) {
    var fromMSB = i;                       // 0 is the most significant bit
    var posFromLSB = W - 1 - i;
    var c = C_TAG;
    if (posFromLSB < 6) { c = C_OFF; }
    else if (posFromLSB < 6 + o.indexBits) { c = C_IDX; }
    fill(c[0], c[1], c[2]);
    stroke(255);
    rect(left + i * cw, y, cw, 26);
    fill(60);
    noStroke();
    if (cw > 12) { textSize(11); textAlign(CENTER, CENTER); text(b[i], left + i * cw + cw / 2, y + 13); }
    stroke(255);
  }
  noStroke();
  // field brackets
  var fields = [
    { label: 'TAG ' + o.tagBits, bits: o.tagBits, c: C_TAG },
    { label: 'INDEX ' + o.indexBits, bits: o.indexBits, c: C_IDX },
    { label: 'OFFSET 6', bits: 6, c: C_OFF }
  ];
  var at = left;
  for (var f = 0; f < fields.length; f++) {
    var fw = fields[f].bits * cw;
    if (fw > 0) {
      stroke(120); strokeWeight(1);
      line(at, y - 6, at + fw, y - 6);
      line(at, y - 9, at, y - 3);
      line(at + fw, y - 9, at + fw, y - 3);
      noStroke();
      fill(74, 82, 96); textSize(11); textAlign(CENTER, BOTTOM);
      if (fw > 34) { text(fields[f].label, at + fw / 2, y - 10); }
      at += fw;
    }
  }
}

/* The decoded values for one organisation. */
function decode(w, o, y) {
  var rows = [
    ['tag = ' + o.tag, 'index = ' + o.index, 'offset = ' + o.offset],
    ['lands in ' + o.where, o.comps, 'block 64 B, 32 lines in all']
  ];
  fill(40); textSize(13); textAlign(LEFT, TOP);
  for (var r = 0; r < rows.length; r++) {
    text(rows[r][0], 22, y + r * 24);
    text(rows[r][1], 250, y + r * 24);
    text(rows[r][2], 470, y + r * 24);
  }
}

/* A small schematic: the set the address lands in, with its comparators. */
function hardware(w, o, y) {
  var boxW = Math.min(120, (w - 120) / Math.max(1, o.ways));
  var x0 = 22;
  fill(250); stroke(150);
  rect(x0, y, Math.min(o.sets, 4) * (boxW + 6) + 6, 54);
  noStroke();
  fill(74, 82, 96); textSize(11); textAlign(LEFT, TOP);
  text(o.sets + ' set' + (o.sets === 1 ? '' : 's') + ', ' + o.ways + ' way' + (o.ways === 1 ? '' : 's'), x0 + 8, y + 6);
  var shown = Math.min(o.ways, 8);
  for (var i = 0; i < shown; i++) {
    fill(i === (o.index % Math.max(1, shown)) ? 214 : 236, 236, 246);
    stroke(150);
    rect(x0 + 8 + i * (boxW * 0.9 + 4), y + 24, boxW * 0.9, 22);
  }
  noStroke();
}

window.LESSON = {
  steps: [
    {
      duration: 5200,
      caption: 'One 32-bit byte address, 0xA248, and one cache of 2 KB of data with 64 B blocks. The cache therefore has 32 lines. Which bits of the address mean what depends entirely on how those 32 lines are organised, and that is what the next three steps change.',
      draw: function (p, w, h) {
        ink();
        head('One address, one cache, three organisations');
        fill(40); textSize(14); textAlign(LEFT, TOP);
        text('address ' + ADDR_HEX + '  =  ' + bin(ADDR, W) + '  (byte addressable)', 22, 52);
        note('2 KB of data in 64 B blocks gives 32 lines, so the offset is always log2 64 = 6 bits.', 84);
        note('The remaining 26 bits are split between tag and index - and the split is the design decision.', 106);
        hardware(w, ORG[0], 140);
        note('Thirty-two lines can be organised as 32 sets of one line, as 8 sets of four, or as one set of thirty-two.', 208);
      }
    },
    {
      duration: 5600,
      caption: 'Direct mapped: 32 lines means 32 sets of one line each, so the index is 5 bits and the tag is 21. The index bits of 0xA248 are 01001, which is 9, and the tag is 20. One comparator of 21 bits decides the hit, and the block lives in line 9 and nowhere else.',
      draw: function (p, w, h) {
        ink();
        head('Direct mapped: tag 21, index 5, offset 6');
        strip(w, ORG[0], 56);
        decode(w, ORG[0], 110);
        hardware(w, ORG[0], 170);
        note('Line number = block number mod 32, which is exactly the 5 index bits.', h - 30);
      }
    },
    {
      duration: 5600,
      caption: 'Now the same 32 lines as 4-way set associative: 8 sets of four lines. The index shrinks to 3 bits because it now names a set, and those two freed bits move into the tag, which becomes 23 bits. The index bits are 001, so the block lands in set 1, and four comparators run in parallel inside that set.',
      draw: function (p, w, h) {
        ink();
        head('4-way: tag 23, index 3, offset 6');
        strip(w, ORG[1], 56);
        decode(w, ORG[1], 110);
        hardware(w, ORG[1], 170);
        note('Two index bits became tag bits: 21 + 2 = 23, and 5 - 2 = 3. The offset never moves.', h - 30);
      }
    },
    {
      duration: 5400,
      caption: 'Fully associative: one set holding all 32 lines. There is no index field, so the tag takes everything above the offset - 26 bits - and all 32 comparators fire at once. Nothing can conflict, because nothing has a home line, and that is also why this organisation is used only for small structures.',
      draw: function (p, w, h) {
        ink();
        head('Fully associative: tag 26, index 0, offset 6');
        strip(w, ORG[2], 56);
        decode(w, ORG[2], 110);
        hardware(w, ORG[2], 170);
        note('Index = 0 bits: writing log2(32) = 5 index bits here is the commonest error in the topic.', h - 30);
      }
    },
    {
      duration: 6000,
      caption: 'The three splits side by side. Every row sums to 32 bits and every row keeps the 6-bit offset; only the boundary between tag and index moves. The block is the same 64 B block of memory in all three - what changes is how many comparators must agree before it can be found.',
      draw: function (p, w, h) {
        ink();
        head('The same 32 bits, cut three ways');
        fill(40); textSize(13); textAlign(LEFT, TOP);
        for (var i = 0; i < ORG.length; i++) {
          var o = ORG[i], y = 56 + i * 46;
          text(o.name, 22, y);
          text('tag ' + o.tagBits + '  |  index ' + o.indexBits + '  |  offset 6', 210, y);
          text('= 32 bits', 430, y);
          text(o.comps, 530, y);
          fill(o.indexBits ? C_IDX[0] : 236, o.indexBits ? C_IDX[1] : 236, o.indexBits ? C_IDX[2] : 236);
          rect(196, y + 2, 6, 12);
          fill(40);
        }
        note('A wider index means more lines to choose from cheaply; a wider tag means more comparators that must all be right.', 210);
        note('Tag width also fixes how many memory blocks share one line: 2^tagBits of them.', 232);
      }
    },
    {
      duration: 5400,
      caption: 'The consequence, in one number: a 21-bit tag means each direct-mapped line stands for 2^21 memory blocks and any two of them that differ by a multiple of 32 lines will evict each other. With 23 bits of tag and four ways the thrashing is much rarer, and with full associativity it cannot happen at all - which is what the three organisations are really buying and paying for.',
      draw: function (p, w, h) {
        ink();
        head('What the tag width buys, and what it costs');
        fill(40); textSize(13); textAlign(LEFT, TOP);
        var rows = [
          ['direct', '2^21 blocks per line', 'conflict misses easy', 'one comparator'],
          ['4-way', '2^23 blocks per set of 4', 'conflict misses rare', 'four comparators'],
          ['fully assoc', '2^26 blocks per set', 'no conflict misses', 'thirty-two comparators']
        ];
        for (var i = 0; i < rows.length; i++) {
          var y = 60 + i * 34;
          text(rows[i][0], 22, y);
          text(rows[i][1], 140, y);
          text(rows[i][2], 330, y);
          text(rows[i][3], 540, y);
        }
        note('More associativity moves bits from the index into the tag and buys comparators with them.', 180);
        note('The 6-bit offset is the only field that never changes when the organisation does.', 202);
      }
    }
  ]
};
