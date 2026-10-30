/* Bayes on a tree, for the Conditional Probability and Bayes Theorem topic.
   One factory, two machines, one defect report:

     machine A   prior 3/5 = 0.6    P(defective | A) = 2/100 = 0.02   branch 0.012
     machine B   prior 2/5 = 0.4    P(defective | B) = 5/100 = 0.05   branch 0.020
     evidence P(defective) = 0.012 + 0.020 = 0.032
     posterior P(B | defective) = 0.020 / 0.032 = 5/8 = 0.625
     posterior P(A | defective) = 0.012 / 0.032 = 3/8 = 0.375

   Two contrasts are drawn at the end:
     equal priors 1/2 and 1/2      -> posterior B = 0.025 / 0.035 = 5/7 = 0.7143
     B supplies 90 per cent        -> posterior B = 0.045 / 0.047 = 0.9574

   Every one of those numbers is recomputed from the priors and the defect rates in
   scripts/validate.py (check_conditional_probability), not copied from here. */

window.LESSON = {
  steps: [
    {
      duration: 3800,
      caption: 'The tree starts with the cause: which machine made the item. Machine A supplies 3/5 of the output and machine B supplies 2/5, so the two branches leaving the root carry 0.6 and 0.4. They are a partition - every item comes from exactly one of them - so the two numbers add to 1.',
      draw: function (p, w, h) {
        ink();
        head('Step 1: the causes, and their shares', 24, 32);
        var g = geo(w, h);
        rootNode(g, 1);
        edge(g, g.root, g.a, 0.6, Math.min(1, p * 2));
        edge(g, g.root, g.b, 0.4, Math.min(1, Math.max(0, p * 2 - 1)));
        causeNode(g, g.a, 'Machine A', '0.6');
        causeNode(g, g.b, 'Machine B', '0.4');
        panel(w, h, [
          'prior P(A) = 0.6',
          'prior P(B) = 0.4',
          '',
          '0.6 + 0.4 = 1',
          'a partition of the output'
        ]);
        note('The first level is what we do not observe. It is the prior.', 24, h - 20);
      }
    },
    {
      duration: 4000,
      caption: 'The second level is what we do observe: whether the item is defective. Machine A makes 2 per cent defective items and machine B makes 5 per cent, so the lower branch from each cause is labelled with that likelihood. The upper branches, the items that are fine, are not needed for this question.',
      draw: function (p, w, h) {
        ink();
        head('Step 2: the evidence, given each cause', 24, 32);
        var g = geo(w, h);
        rootNode(g, 1);
        edge(g, g.root, g.a, 0.6, 1);
        edge(g, g.root, g.b, 0.4, 1);
        causeNode(g, g.a, 'Machine A', '0.6');
        causeNode(g, g.b, 'Machine B', '0.4');
        var t = Math.min(1, p * 1.6);
        edge(g, g.a, g.ad, 0.02, t);
        edge(g, g.a, g.ao, 0.98, Math.min(1, Math.max(0, p * 1.6 - 0.6)));
        edge(g, g.b, g.bd, 0.05, t);
        edge(g, g.b, g.bo, 0.95, Math.min(1, Math.max(0, p * 1.6 - 0.6)));
        leafNode(g, g.ad, 'defective', '0.02', true);
        leafNode(g, g.ao, 'fine', '0.98', false);
        leafNode(g, g.bd, 'defective', '0.05', true);
        leafNode(g, g.bo, 'fine', '0.95', false);
        panel(w, h, [
          'P(defective | A) = 0.02',
          'P(defective | B) = 0.05',
          '',
          'The two edges from each node',
          'add to 1: 0.02 + 0.98.'
        ]);
        note('The second level is a conditional probability. The question reverses it.', 24, h - 20);
      }
    },
    {
      duration: 4200,
      caption: 'Multiply along each branch. Machine A and defective is 0.6 times 0.02, which is 0.012. Machine B and defective is 0.4 times 0.05, which is 0.020. These two products are the joint probabilities, and they are the only branches that end in the observation, so they are the only ones the answer uses.',
      draw: function (p, w, h) {
        ink();
        head('Step 3: multiply along the branch', 24, 32);
        var g = geo(w, h);
        rootNode(g, 1);
        edge(g, g.root, g.a, 0.6, 1);
        edge(g, g.root, g.b, 0.4, 1);
        causeNode(g, g.a, 'Machine A', '0.6');
        causeNode(g, g.b, 'Machine B', '0.4');
        edge(g, g.a, g.ad, 0.02, 1);
        edge(g, g.b, g.bd, 0.05, 1);
        leafNode(g, g.ad, 'defective', '0.02', true);
        leafNode(g, g.bd, 'defective', '0.05', true);
        var t = Math.min(1, p * 1.4);
        productLabel(g, g.ad, '0.6 x 0.02 = 0.012', t);
        productLabel(g, g.bd, '0.4 x 0.05 = 0.020', Math.min(1, Math.max(0, p * 1.4 - 0.4)));
        panel(w, h, [
          'P(A and defective) = 0.012',
          'P(B and defective) = 0.020',
          '',
          '0.012 + 0.020 = 0.032',
          'the probability of the evidence'
        ]);
        note('Along a branch: multiply. Across the branches ending in the evidence: add.', 24, h - 20);
      }
    },
    {
      duration: 4200,
      caption: 'The evidence is the total of those two branches, 0.032. That is the total probability theorem, and it is the denominator of Bayes. The bar shows the same fact: the defective items are not shared equally, because machine B contributes 0.020 of the 0.032 even though it supplies fewer items.',
      draw: function (p, w, h) {
        ink();
        head('Step 4: the evidence is the denominator', 24, 32);
        var g = geo(w, h);
        rootNode(g, 1);
        edge(g, g.root, g.a, 0.6, 1);
        edge(g, g.root, g.b, 0.4, 1);
        causeNode(g, g.a, 'Machine A', '0.6');
        causeNode(g, g.b, 'Machine B', '0.4');
        edge(g, g.a, g.ad, 0.02, 1);
        edge(g, g.b, g.bd, 0.05, 1);
        leafNode(g, g.ad, 'defective', '0.012', true);
        leafNode(g, g.bd, 'defective', '0.020', true);
        var t = Math.min(1, p * 1.3);
        splitBar(w, h, t);
        panel(w, h, [
          'evidence = 0.032',
          '',
          'A holds 0.012 / 0.032 = 0.375',
          'B holds 0.020 / 0.032 = 0.625'
        ]);
        note('The two shares add to 1, which is the check that the arithmetic is right.', 24, h - 20);
      }
    },
    {
      duration: 4200,
      caption: 'Divide the branch by the evidence and the tree reverses its direction. The probability that the defective item came from machine B is 0.020 divided by 0.032, which is 5/8, or 0.625. Reporting 0.05 - the defect rate of machine B - would answer the opposite question, P(defective given B).',
      draw: function (p, w, h) {
        ink();
        head('Step 5: the posterior, B given defective', 24, 32);
        var g = geo(w, h);
        rootNode(g, 1);
        edge(g, g.root, g.a, 0.6, 1);
        edge(g, g.root, g.b, 0.4, 1);
        causeNode(g, g.a, 'Machine A', '0.6');
        causeNode(g, g.b, 'Machine B', '0.4');
        edge(g, g.a, g.ad, 0.02, 1);
        edge(g, g.b, g.bd, 0.05, 1);
        leafNode(g, g.ad, '0.375 of the defectives', '0.012', false);
        leafNode(g, g.bd, '0.625 of the defectives', '0.020', true);
        splitBar(w, h, 1);
        var t = Math.min(1, p * 1.5);
        noStroke(); fill(20, 24, 31); textSize(15); textStyle(BOLD);
        text('P(B | defective) = ' + (0.625 * t).toFixed(3), w - 250, h - 96);
        textStyle(NORMAL);
        panel(w, h, [
          'P(B | defective) = 0.020 / 0.032',
          '               = 5/8 = 0.625',
          '',
          'the trap: 0.05 is P(defective | B)'
        ]);
        note('Bayes turns a share of a machine into a share of the defectives.', 24, h - 20);
      }
    },
    {
      duration: 4600,
      caption: 'Now change only the priors: machine B supplies 90 per cent of the output and machine A 10 per cent, with the same defect rates. The branches become 0.002 and 0.045, the evidence 0.047, and the posterior for B jumps to 0.957. The machines did not improve; the population changed, and that is why the prior has to be in the calculation.',
      draw: function (p, w, h) {
        ink();
        head('Step 6: same rates, different priors', 24, 32);
        var g = geo(w, h);
        rootNode(g, 1);
        edge(g, g.root, g.a, 0.1, 1);
        edge(g, g.root, g.b, 0.9, 1);
        causeNode(g, g.a, 'Machine A', '0.1');
        causeNode(g, g.b, 'Machine B', '0.9');
        edge(g, g.a, g.ad, 0.02, 1);
        edge(g, g.b, g.bd, 0.05, 1);
        leafNode(g, g.ad, 'defective', '0.002', false);
        leafNode(g, g.bd, 'defective', '0.045', true);
        var t = Math.min(1, p * 1.4);
        barPair(w, h, t);
        noStroke(); fill(20, 24, 31); textSize(15); textStyle(BOLD);
        text('P(B | defective) = ' + (0.9574 * t).toFixed(3), w - 250, h - 96);
        textStyle(NORMAL);
        panel(w, h, [
          '0.1 x 0.02 = 0.002',
          '0.9 x 0.05 = 0.045',
          'evidence  = 0.047',
          '0.045 / 0.047 = 0.957'
        ]);
        note('A rare cause stays rare, and a common cause becomes near-certain.', 24, h - 20);
      }
    }
  ]
};

/* ---------------------------------------------------------------- geometry */
function geo(w, h) {
  var left = 26, top = 58;
  return {
    root: [left + 0.02 * w, top + 0.42 * h],
    a: [left + 0.22 * w, top + 0.16 * h],
    b: [left + 0.22 * w, top + 0.70 * h],
    ad: [left + 0.44 * w, top + 0.04 * h],
    ao: [left + 0.44 * w, top + 0.30 * h],
    bd: [left + 0.44 * w, top + 0.58 * h],
    bo: [left + 0.44 * w, top + 0.86 * h]
  };
}

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

function box(x, y, wd, ht, label, sub, hot) {
  if (hot) { fill(31, 94, 255, 32); stroke(31, 94, 255); }
  else { fill(245, 247, 251); stroke(206, 212, 222); }
  strokeWeight(1);
  rect(x - wd / 2, y - ht / 2, wd, ht, 6);
  noStroke(); fill(30, 38, 50); textSize(12); textAlign(CENTER, CENTER);
  text(label, x, y - (sub ? 6 : 0));
  if (sub) { textSize(11); fill(90, 100, 116); text(sub, x, y + 9); }
  textAlign('left', 'baseline');
}

function rootNode(g) { box(g.root[0], g.root[1], 84, 34, 'factory', null, false); }
function causeNode(g, at, label, sub) { box(at[0], at[1], 92, 34, label, sub, false); }
function leafNode(g, at, label, sub, hot) { box(at[0], at[1], 118, 34, label, sub, hot); }

function edge(g, from, to, prob, t) {
  if (t <= 0) { return; }
  var ex = from[0] + (to[0] - from[0]) * t;
  var ey = from[1] + (to[1] - from[1]) * t;
  stroke(198, 206, 218); strokeWeight(1.5);
  line(from[0] + 30, from[1], ex, ey);
  var mx = (from[0] + to[0]) / 2, my = (from[1] + to[1]) / 2;
  noStroke(); fill(31, 94, 255); textSize(11.5);
  text(String(prob), mx - 8, my - 5);
}

function productLabel(g, at, textValue, t) {
  if (t <= 0) { return; }
  noStroke(); fill(31, 94, 255); textSize(11.5);
  text(textValue, at[0] + 66, at[1] + 4);
}

function splitBar(w, h, t) {
  var x = w - 250, y = h - 132, wd = 226, ht = 26;
  var fa = 0.375 * t, fb = 0.625 * t;
  stroke(206, 212, 222); strokeWeight(1);
  rect(x, y, wd, ht, 4);
  noStroke();
  fill(120, 160, 240, 190);
  rect(x + 1, y + 1, Math.max(0, (wd - 2) * fa), ht - 2, 3);
  fill(31, 94, 255, 200);
  rect(x + 1 + (wd - 2) * fa, y + 1, Math.max(0, (wd - 2) * fb), ht - 2, 3);
  fill(30, 38, 50); textSize(11);
  text('A 0.375', x, y - 6);
  text('B 0.625', x + wd - 52, y - 6);
  text('the defective items, split by machine', x, y + ht + 16);
}

function barPair(w, h, t) {
  var x = w - 250, y = h - 132, wd = 226, ht = 26;
  var fa = 0.002 / 0.047, fb = 0.045 / 0.047;
  stroke(206, 212, 222); strokeWeight(1);
  rect(x, y, wd, ht, 4);
  noStroke();
  fill(120, 160, 240, 190);
  rect(x + 1, y + 1, Math.max(0, (wd - 2) * fa * t), ht - 2, 3);
  fill(31, 94, 255, 200);
  rect(x + 1 + (wd - 2) * fa, y + 1, Math.max(0, (wd - 2) * fb * t), ht - 2, 3);
  fill(30, 38, 50); textSize(11);
  text('A 0.043', x, y - 6);
  text('B 0.957', x + wd - 52, y - 6);
  text('the defective items, split by machine', x, y + ht + 16);
}

function panel(w, h, lines) {
  var x = w - 250, y = 66;
  noStroke();
  for (var i = 0; i < lines.length; i++) {
    fill(i === 0 ? color(20, 24, 31) : color(70, 80, 96));
    textSize(i === 0 ? 12.5 : 12);
    text(lines[i], x, y + i * 17);
  }
}
