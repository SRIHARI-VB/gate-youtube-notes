/* Shared lesson harness: step navigation, captions, play/pause, speed, reduced motion. */
(function () {
  var L = null;
  var state = { step: 0, playing: false, speed: 1, stepStart: 0, progress: 0 };
  var els = {};

  function fmt(i) { return (i + 1) + ' / ' + L.steps.length; }
  function current() { return L.steps[state.step]; }

  window.setup = function () {
    L = window.LESSON;
    var w = Math.min(document.querySelector('.canvas-wrap').clientWidth, 860);
    var c = createCanvas(w, Math.round(w * 0.62));
    c.parent('canvas-holder');
    noLoop();
    bindUI();
    applyStep(0);
  };

  window.draw = function () {
    background(getComputedStyle(document.body).getPropertyValue('--surface').trim() || '#fff');
    var step = current();
    if (state.playing && step.duration) {
      state.progress = Math.min(1, (millis() - state.stepStart) / (step.duration / state.speed));
      if (state.progress >= 1) { advance(true); return; }
    }
    // When paused, show the finished frame of the current step rather than an empty canvas.
    step.draw(state.playing ? state.progress : 1, width, height);
  };

  function applyStep(i) {
    state.step = Math.max(0, Math.min(L.steps.length - 1, i));
    state.stepStart = millis();
    state.progress = 0;
    els.caption.innerHTML = current().caption;
    els.counter.textContent = fmt(state.step);
    els.prev.disabled = state.step === 0;
    els.next.disabled = state.step === L.steps.length - 1;
    if (state.playing) { loop(); } else { redraw(); }
  }

  function advance(auto) {
    if (state.step < L.steps.length - 1) {
      applyStep(state.step + 1);
      if (!auto) { state.playing = false; els.play.textContent = 'Play'; noLoop(); }
    } else {
      state.playing = false;
      els.play.textContent = 'Replay';
      noLoop();
      redraw();
    }
  }

  function bindUI() {
    els.caption = document.getElementById('caption');
    els.counter = document.getElementById('counter');
    els.play = document.getElementById('play');
    els.prev = document.getElementById('prev');
    els.next = document.getElementById('next');
    els.restart = document.getElementById('restart');
    els.speed = document.getElementById('speed');

    els.play.addEventListener('click', function () {
      if (state.playing) {
        state.playing = false; els.play.textContent = 'Play'; noLoop(); redraw();
      } else {
        if (state.step === L.steps.length - 1 && state.progress >= 1) { applyStep(0); }
        state.playing = true; els.play.textContent = 'Pause'; state.stepStart = millis(); loop();
      }
    });
    els.prev.addEventListener('click', function () { state.playing = false; els.play.textContent = 'Play'; applyStep(state.step - 1); noLoop(); });
    els.next.addEventListener('click', function () { state.playing = false; els.play.textContent = 'Play'; applyStep(state.step + 1); noLoop(); });
    els.restart.addEventListener('click', function () { state.playing = false; els.play.textContent = 'Play'; applyStep(0); noLoop(); });
    els.speed.addEventListener('input', function () {
      state.speed = parseFloat(els.speed.value);
      document.getElementById('speedLabel').textContent = state.speed.toFixed(2) + 'x';
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { els.next.click(); }
      if (e.key === 'ArrowLeft') { els.prev.click(); }
      if (e.key === ' ') { e.preventDefault(); els.play.click(); }
    });
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) { state.speed = 0.35; }
  }
})();
