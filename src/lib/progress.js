/* Progress store used by app.js. Kept separate so content never mixes with learner state. */
window.ProgressStore = {
  key: 'gate-revision-progress-v1',
  read() { try { return JSON.parse(localStorage.getItem(this.key) || '{}'); } catch (e) { return {}; } },
  write(s) { try { localStorage.setItem(this.key, JSON.stringify(s)); } catch (e) {} },
  toggle(id) { const s = this.read(); if (s[id]) delete s[id]; else s[id] = new Date().toISOString(); this.write(s); return !!s[id]; }
};
