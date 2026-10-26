/* Smoke test for the p5 lessons without a browser: stub the p5 globals, load each sketch,
   then draw every step at p = 0, 0.5 and 1. Catches reference errors and non-finite geometry.

   Lessons are discovered by walking visuals/ for lesson.json files, so a lesson nested
   under visuals/<subject>/<topic>/<subtopic>/ is tested automatically.

   Run: node tests/visual-lessons.js
*/
const fs = require('fs'), vm = require('vm'), path = require('path');
const ROOT = path.join(__dirname, '..', 'visuals');

function findLessons(dir, out) {
  for (const name of fs.readdirSync(dir).sort()) {
    const p = path.join(dir, name);
    const st = fs.statSync(p);
    if (st.isDirectory()) { findLessons(p, out); }
    else if (name === 'lesson.json') { out.push(path.dirname(p)); }
  }
  return out;
}

const lessons = findLessons(ROOT, []).filter(d => {
  const meta = JSON.parse(fs.readFileSync(path.join(d, 'lesson.json'), 'utf8'));
  return meta.engine === 'p5.js';
});
let failures = 0, calls = 0;

for (const dir of lessons) {
  const slug = path.relative(ROOT, dir).split(path.sep).join('/');
  const ctx = {
    console,
    createCanvas: () => ({ parent: () => {} }),
    background: () => calls++, fill: () => calls++, noFill: () => calls++, stroke: () => calls++,
    noStroke: () => calls++, strokeWeight: () => calls++, strokeCap: () => calls++,
    rect: () => calls++, circle: () => calls++, line: () => calls++, ellipse: () => calls++,
    color: (r, g, b) => 'rgb(' + r + ',' + g + ',' + b + ')',
    textFont: () => calls++, textWidth: () => 40,
    text: (t, x, y) => {
      calls++;
      if (typeof t !== 'string' && typeof t !== 'number') throw new Error('text() got ' + typeof t);
      if (!isFinite(x) || !isFinite(y)) throw new Error('text() at non-finite position: ' + t);
    },
    textSize: () => calls++, textStyle: () => calls++, textAlign: () => calls++,
    beginShape: () => calls++,
    vertex: (x, y) => { calls++; if (!isFinite(x) || !isFinite(y)) throw new Error('vertex NaN'); },
    endShape: () => calls++, lerp: (a, b, t) => a + (b - a) * t,
    millis: () => 0, loop: () => {}, noLoop: () => {}, redraw: () => {},
    CLOSE: 'close', BOLD: 'bold', NORMAL: 'normal', CENTER: 'center', ROUND: 'round',
    SQUARE: 'butt', PROJECT: 'square', Math, isFinite, parseFloat, width: 800, height: 500
  };
  ctx.window = ctx;
  ctx.window.matchMedia = () => ({ matches: false });
  vm.createContext(ctx);
  try {
    vm.runInContext(fs.readFileSync(path.join(dir, 'sketch.js'), 'utf8'), ctx);
  } catch (e) {
    console.log('FAIL ' + slug + ': load error ' + e.message); failures++; continue;
  }
  const L = ctx.window.LESSON;
  if (!L || !Array.isArray(L.steps) || !L.steps.length) {
    console.log('FAIL ' + slug + ': no steps'); failures++; continue;
  }
  L.steps.forEach((s, i) => {
    for (const p of [0, 0.5, 1]) {
      try { s.draw(p, 800, 500); }
      catch (e) { console.log('FAIL ' + slug + ' step ' + (i + 1) + ' at p=' + p + ': ' + e.message); failures++; }
    }
    if (!s.caption || s.caption.length < 20) { console.log('FAIL ' + slug + ' step ' + (i + 1) + ': caption too short'); failures++; }
    if (!s.duration) { console.log('FAIL ' + slug + ' step ' + (i + 1) + ': no duration'); failures++; }
  });
  console.log('ok   ' + slug + ': ' + L.steps.length + ' steps drew without error');
}
console.log(failures === 0 ? 'ALL SKETCH CHECKS PASSED' : failures + ' sketch failures');
process.exit(failures ? 1 : 0);
