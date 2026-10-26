(function () {
  var D = window.GATE_DATA || {};
  var topics = D.topics || [], pyqs = D.pyqs || [], videos = D.videos || [];
  var playlist = D.playlist || {}, syllabus = D.syllabus || {}, formulas = D.formulas || [];
  var byId = {}; topics.forEach(function (t) { byId[t.id] = t; });
  var pyqById = {}; pyqs.forEach(function (p) { pyqById[p.id] = p; });
  var vidById = {}; videos.forEach(function (v) { vidById[v.video_id] = v; });

  var store = {
    key: 'gate-revision-progress-v1',
    read: function () { try { return JSON.parse(localStorage.getItem(this.key) || '{}'); } catch (e) { return {}; } },
    isRevised: function (id) { return !!this.read()[id]; },
    toggle: function (id) {
      var s = this.read(); if (s[id]) { delete s[id]; } else { s[id] = new Date().toISOString(); }
      try { localStorage.setItem(this.key, JSON.stringify(s)); } catch (e) {}
      return !!s[id];
    }
  };

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
  function math(tex, display) {
    if (window.katex && tex) {
      try { return window.katex.renderToString(tex, { throwOnError: false, displayMode: !!display }); } catch (e) {}
    }
    return '<span class="katex-fallback">' + esc(tex) + '</span>';
  }
  function h(html) { return html; }
  function qs(name) {
    var m = new RegExp('[?&]' + name + '=([^&#]*)').exec(location.hash || '');
    return m ? decodeURIComponent(m[1].replace(/\+/g, ' ')) : '';
  }
  function prio(p) { return '<span class="badge ' + (p || 'p3').toLowerCase() + '">' + esc(p) + '</span>'; }
  function label(text) { return '<div class="field-label">' + esc(text) + '</div>'; }
  function field(name, bodyHtml, cls) {
    return '<div class="field">' + label(name) + '<div class="field-body ' + (cls || '') + '">' + bodyHtml + '</div></div>';
  }
  function list(items) {
    return '<ul class="tight">' + items.map(function (i) { return '<li>' + i + '</li>'; }).join('') + '</ul>';
  }

  /* ---------------- views ---------------- */
  function viewDashboard() {
    var revised = store.read();
    var done = topics.filter(function (t) { return revised[t.id]; }).length;
    var verified = pyqs.filter(function (p) { return p.verification === 'OFFICIAL_KEY' || p.verification === 'SOURCED'; }).length;
    var p1 = topics.filter(function (t) { return t.priority === 'P1'; });
    return h(
      '<h1>GATE CSE revision dashboard</h1>' +
      '<p class="lead">Built from ' + (D.playlists && D.playlists.length ? D.playlists.length + ' GO Classes playlists' : 'the GO Classes playlist') + ', mapped to the GATE CSE syllabus line: ' +
      '<em>' + esc(syllabus.line) + '</em> These are recall cards, not a textbook.</p>' +
      '<div class="grid cols-3" style="margin:18px 0 6px">' +
        statCard(topics.length, 'revision topics') +
        statCard(verified, 'verified PYQs') +
        statCard(videos.length, 'videos in playlist') +
        statCard(done + '/' + topics.length, 'marked revised') +
      '</div>' +
      '<h2>Start here</h2>' +
      '<div class="grid cols-2">' +
        '<div class="card"><h3>P1 topics first</h3><p class="muted">These carry the highest exam value and everything else depends on them.</p>' +
          '<ul class="tight">' + p1.map(function (t) {
            return '<li><a href="#/topic/' + t.id + '">' + esc(t.title) + '</a></li>';
          }).join('') + '</ul></div>' +
        '<div class="card"><h3>Last-minute sheet</h3><p class="muted">Every formula in one screen, grouped by the decision you are actually making.</p>' +
          '<div class="link-row"><a href="#/last-minute">Open formula sheet</a><a href="#/pyqs">Browse PYQs</a><a href="#/visuals">Visual lessons</a></div></div>' +
      '</div>' +
      '<h2>How this is organised</h2>' +
      '<div class="card"><p style="margin-bottom:8px">Each topic is one card: a five-second idea, what to remember, a tiny example, the GATE angle, a trap, and a quick check with its answer. ' +
      'Previous-year questions are kept separate from original practice and from predicted variations, and each one names its year, question reference and source.</p>' +
      '<p class="muted" style="margin:0">Playlist: <a href="' + esc(playlist.url) + '" target="_blank" rel="noopener">' + esc(playlist.title) + '</a> - ' + esc(playlist.channel) + '</p></div>'
    );
  }
  function statCard(n, l) { return '<div class="card tight"><div class="stat">' + esc(n) + '</div><div class="stat-label">' + esc(l) + '</div></div>'; }

  function viewTopics() {
    var rows = topics.slice().sort(function (a, b) { return a.order - b.order; });
    var html = '<h1>Topics</h1><p class="lead">' + topics.length + ' canonical topic cards. Videos map into these; the notes live here once, not once per video.</p>';
    html += '<div class="pill-row" id="topicFilter">' +
      ['all', 'P1', 'P2', 'P3'].map(function (p) {
        return '<button class="chip" data-p="' + p + '" aria-pressed="' + (p === 'all') + '">' + p + '</button>';
      }).join('') + '</div>';
    html += '<div id="topicList">' + rows.map(topicRow).join('') + '</div>';
    return h(html);
  }
  function topicRow(t) {
    var revised = store.isRevised(t.id);
    return '<div class="card tight" data-prio="' + t.priority + '" style="margin-bottom:10px">' +
      '<div class="card-head"><div><a href="#/topic/' + t.id + '"><strong>' + esc(t.title) + '</strong></a>' +
      (revised ? ' <span class="revised">&#10003; revised</span>' : '') + '</div>' + prio(t.priority) + '</div>' +
      '<div class="muted" style="margin-top:4px">' + esc(t.quickIdea) + '</div></div>';
  }

  function viewTopic(id) {
    var t = byId[id];
    if (!t) { return h('<div class="empty">Unknown topic.</div>'); }
    var revised = store.isRevised(t.id);
    var html = '<div class="crumbs"><a href="#/topics">Topics</a> / ' + esc(t.unit) + '</div>';
    html += '<h1>' + esc(t.title) + ' ' + prio(t.priority) + '</h1>';
    html += '<p class="lead">' + esc(t.unit) + (t.prereqs && t.prereqs.length ? ' &middot; builds on ' + esc(t.prereqs.map(function (p) { var pt = byId[p]; return pt ? pt.title : p; }).join(', ')) : '') + '</p>';
    html += '<div class="pill-row"><button class="chip" id="markRevised" aria-pressed="' + (revised ? 'true' : 'false') + '">' +
      (revised ? 'Marked revised' : 'Mark as revised') + '</button></div>';

    html += '<div class="card notecard">';
    html += field('5-second idea', esc(t.quickIdea));
    html += field('Remember', list(t.remember));
    html += '<div class="field">' + label('Tiny example') + '<div class="example">' +
      '<div style="margin-bottom:6px"><strong>' + esc(t.example.prompt) + '</strong></div>' +
      '<div class="muted" style="margin-bottom:6px">' + esc(t.example.work) + '</div>' +
      '<div class="answer-line">' + esc(t.example.answer) + '</div></div></div>';
    html += field('GATE angle', esc(t.gateAngle));
    if (t.variations && t.variations.length) {
      html += '<div class="field">' + label('Variations') + '<div class="field-body">' +
        t.variations.map(function (v) {
          return '<div class="q"><div class="q-meta"><span class="badge accent">' + esc(v.label) + '</span></div>' +
            '<div class="q-text">' + esc(v.question) + '</div>' +
            '<div class="answer-line">Answer: ' + esc(v.answer) + '</div>' +
            '<div class="solution" style="margin-top:6px">' + esc(v.why) + '</div></div>';
        }).join('') + '</div></div>';
    }
    html += '<div class="trap">' + label('Trap alert') +
      '<div style="font-weight:650;margin-bottom:4px">' + esc(t.trap.what) + '</div>' +
      '<div style="margin-bottom:6px">' + esc(t.trap.why) + '</div>' +
      '<div class="muted"><strong>Counterexample:</strong> ' + esc(t.trap.counterexample) + '</div></div>';
    html += '<div class="field" style="margin-top:16px">' + label('Quick check') +
      '<div class="q"><div class="q-text">' + esc(t.check.question) + '</div>' +
      '<details><summary>Show answer</summary><div class="answer-line">' + esc(t.check.answer) + '</div>' +
      '<div class="solution">' + esc(t.check.explanation) + '</div></details></div></div>';
    html += '</div>';

    if (t.pyqIds && t.pyqIds.length) {
      html += '<h2>Linked verified PYQs</h2>';
      html += t.pyqIds.map(function (pid) { return pyqCard(pyqById[pid]); }).join('');
    }
    if (t.videoRefs && t.videoRefs.length) {
      html += '<h2>Where this is taught</h2><div class="card">' + t.videoRefs.map(function (vid) {
        var v = vidById[vid];
        if (!v) { return ''; }
        return '<div style="margin-bottom:10px"><a href="' + esc(v.url) + '" target="_blank" rel="noopener">' + esc(v.title) + '</a>' +
          '<div class="muted">' + esc(v.transcript_status) + '</div></div>';
      }).join('') + '</div>';
    }
    if (t.prereqs && t.prereqs.length) {
      html += '<h2>Prerequisites</h2><div class="link-row">' + t.prereqs.map(function (p) {
        var pt = byId[p]; return pt ? '<a href="#/topic/' + p + '">' + esc(pt.title) + '</a>' : '';
      }).join('') + '</div>';
    }
    if (t.visual) {
      html += '<h2>Visual lesson</h2><div class="card"><p style="margin-bottom:10px">Animated walkthrough for this topic.</p>' +
        '<a href="visuals/' + t.visual + '/index.html" target="_blank" rel="noopener">Open the lesson &#8599;</a></div>';
    }
    return h(html);
  }

  function pyqCard(p) {
    if (!p) { return ''; }
    var badge = p.verification === 'OFFICIAL_KEY'
      ? '<span class="badge ok">VERIFIED PYQ - official key</span>'
      : '<span class="badge ok">VERIFIED PYQ - sourced solution</span>';
    var opts = (p.options && p.options.length)
      ? '<ol class="options" type="A">' + p.options.map(function (o) { return '<li>' + esc(o) + '</li>'; }).join('') + '</ol>' : '';
    return '<div class="q" id="pyq-' + esc(p.id) + '">' +
      '<div class="q-meta"><span class="badge accent">' + esc(p.paper) + '</span>' +
      '<span class="badge">' + esc(p.question_ref) + '</span>' +
      '<span class="badge">' + esc(p.type) + (p.marks ? ' &middot; ' + esc(p.marks) + ' mark(s)' : '') + '</span>' + badge + '</div>' +
      '<div class="q-text">' + esc(p.text) + '</div>' + opts +
      '<details><summary>Answer and solution</summary>' +
      '<div class="answer-line">' + esc(p.answer) + '</div>' +
      '<div class="solution">' + esc(p.solution) + '</div>' +
      '<div class="verify-note">Source: <a href="' + esc(p.source_url) + '" target="_blank" rel="noopener">' + esc(p.source_label) + '</a></div>' +
      '</details></div>';
  }

  function viewPyqs() {
    var years = Array.from(new Set(pyqs.map(function (p) { return p.year; }))).sort();
    var html = '<h1>Verified previous-year questions</h1>' +
      '<p class="lead">Every question here carries its paper, question reference, answer and a source link. ' +
      'Questions that could not be checked against a paper or a named solution set are not listed as PYQs anywhere in this repository.</p>';
    html += '<div class="pill-row" id="yearFilter">' +
      '<button class="chip" data-year="all" aria-pressed="true">All years</button>' +
      years.map(function (y) { return '<button class="chip" data-year="' + y + '" aria-pressed="false">' + y + '</button>'; }).join('') +
      '</div><div id="pyqList">' + pyqs.map(pyqCard).join('') + '</div>';
    return h(html);
  }

  function viewPlaylist() {
    var pls = (D.playlists && D.playlists.length) ? D.playlists : [playlist];
    var html = '<h1>Playlist inventory</h1>' +
      '<p class="lead">' + pls.map(function (p) { return esc(p.title) + ' - ' + esc(p.channel); }).join(' &middot; ') + '. ' +
      'Every video has an explicit processing status. Where only the opening of a lecture was retrievable, that is stated instead of being hidden.</p>';
    html += '<div class="card"><table><thead><tr><th>#</th><th>Video</th><th>Length</th><th>Status</th><th>Topics</th></tr></thead><tbody>';
    videos.forEach(function (v) {
      html += '<tr><td>' + v.position + '</td>' +
        '<td><a href="' + esc(v.url) + '" target="_blank" rel="noopener">' + esc(v.title) + '</a>' +
        '<div class="muted" style="margin-top:4px">' + esc(v.coverage_note) + '</div></td>' +
        '<td class="muted">' + fmtDur(v.duration_seconds) + '</td>' +
        '<td><span class="badge warn">' + esc(v.transcript_status.split(' - ')[0]) + '</span></td>' +
        '<td class="muted">' + (v.topics || []).map(function (tid) {
          var t = byId[tid]; return t ? '<a href="#/topic/' + tid + '">' + esc(t.title) + '</a>' : esc(tid);
        }).join('<br>') + '</td></tr>';
    });
    html += '</tbody></table></div>';
    return h(html);
  }
  function fmtDur(s) {
    var hh = Math.floor(s / 3600), mm = Math.round((s % 3600) / 60);
    return hh ? hh + 'h ' + mm + 'm' : mm + 'm';
  }

  function viewVisuals() {
    var vids = [
      { slug: 'stars-and-bars', title: 'Stars and Bars (IODB)', why: 'See why n identical objects in k distinct boxes is C(n+k-1, k-1), and what the bars actually are.' },
      { slug: 'inclusion-exclusion', title: 'Inclusion-Exclusion and Derangements', why: 'Watch the alternating add/subtract pattern fix double counting, then count derangements with it.' },
      { slug: 'pigeonhole', title: 'Pigeonhole: Guarantees, not Odds', why: 'The worst-case construction that turns "probably" into "must".' },
      { slug: 'distribution-grid', title: 'The 2x2 Distribution Grid', why: 'Decide between DODB, IODB, DOIB and IOIB before you write a single formula.' },
      { slug: 'discrete-mathematics/propositional-logic/truth-tables', title: 'Truth Tables: Implication and Its Converse', why: 'See why p -> q is false in exactly one row, and why the converse is a different column.' },
      { slug: 'discrete-mathematics/propositional-logic/implication-contrapositive', title: 'Converse, Inverse and Contrapositive', why: 'Three rewrites of p -> q, and the only one that is actually equivalent.' }
    ];
    return h('<h1>Visual lessons</h1><p class="lead">Each lesson runs in the browser with play, pause, step and speed controls, and a static explanation underneath so it is still useful with animation off.</p>' +
      '<div class="grid cols-2">' + vids.map(function (v) {
        return '<div class="card"><h3>' + esc(v.title) + '</h3><p class="muted">' + esc(v.why) + '</p>' +
          '<a href="visuals/' + v.slug + '/index.html" target="_blank" rel="noopener">Open lesson &#8599;</a></div>';
      }).join('') + '</div>');
  }

  function viewLastMinute() {
    var html = '<h1>Last-minute sheet</h1><p class="lead">Only what you need in the final hour: formulas grouped by the decision they belong to.</p>';
    formulas.forEach(function (g) {
      html += '<h2>' + esc(g.group) + '</h2><div class="card"><table><tbody>';
      g.items.forEach(function (it) {
        html += '<tr><td style="width:34%"><strong>' + esc(it.name) + '</strong></td>' +
          '<td>' + math(it.latex) + '</td><td class="muted" style="width:26%">' + esc(it.note || '') + '</td></tr>';
      });
      html += '</tbody></table></div>';
    });
    html += '<h2>Traps worth one more look</h2><div class="card">' + list(topics.filter(function (t) { return t.priority === 'P1'; })
      .map(function (t) { return '<a href="#/topic/' + t.id + '">' + esc(t.title) + '</a>: ' + esc(t.trap.what); })) + '</div>';
    return h(html);
  }

  function viewSearch(q) {
    var term = (q || '').toLowerCase();
    if (!term) { return h('<h1>Search</h1><div class="empty">Type in the search box above.</div>'); }
    function hit(text) { return String(text || '').toLowerCase().indexOf(term) >= 0; }
    var tHits = topics.filter(function (t) {
      return hit(t.title) || hit(t.quickIdea) || (t.remember || []).some(hit) || hit(t.gateAngle);
    });
    var pHits = pyqs.filter(function (p) { return hit(p.text) || hit(p.paper) || hit(p.solution); });
    var html = '<h1>Results for "' + esc(q) + '"</h1>';
    html += '<h2>Topics (' + tHits.length + ')</h2>' + (tHits.length ? tHits.map(topicRow).join('') : '<div class="empty">No topic matched.</div>');
    html += '<h2>PYQs (' + pHits.length + ')</h2>' + (pHits.length ? pHits.map(pyqCard).join('') : '<div class="empty">No PYQ matched.</div>');
    return h(html);
  }

  /* ---------------- router ---------------- */
  function route() {
    var hash = location.hash.replace(/^#/, '') || '/';
    var main = document.getElementById('view');
    var title = 'Combinatorics revision';
    var out;
    if (hash === '/' || hash === '') { out = viewDashboard(); }
    else if (hash.indexOf('/topics') === 0) { out = viewTopics(); title = 'Topics'; }
    else if (hash.indexOf('/topic/') === 0) {
      var id = hash.slice(7); out = viewTopic(id);
      title = (byId[id] ? byId[id].title : 'Topic');
    }
    else if (hash.indexOf('/pyqs') === 0) { out = viewPyqs(); title = 'PYQs'; }
    else if (hash.indexOf('/playlist') === 0) { out = viewPlaylist(); title = 'Playlist'; }
    else if (hash.indexOf('/visuals') === 0) { out = viewVisuals(); title = 'Visual lessons'; }
    else if (hash.indexOf('/last-minute') === 0) { out = viewLastMinute(); title = 'Last-minute sheet'; }
    else if (hash.indexOf('/search') === 0) { out = viewSearch(qs('q')); title = 'Search'; }
    else { out = h('<div class="empty">Not found. <a href="#/">Go to dashboard</a></div>'); }
    main.innerHTML = out;
    document.title = title + ' - Combinatorics revision';
    document.querySelectorAll('.nav a').forEach(function (a) {
      var target = a.getAttribute('href').replace('#', '');
      a.classList.toggle('active', target === hash || (target !== '/' && hash.indexOf(target) === 0));
    });
    document.body.classList.remove('nav-open');
    var navCount = document.getElementById('navTopicCount');
    if (navCount) { navCount.textContent = String(topics.length); }
    bindViewEvents(hash);
    window.scrollTo(0, 0);
  }

  function bindViewEvents(hash) {
    var mr = document.getElementById('markRevised');
    if (mr) {
      mr.addEventListener('click', function () {
        var id = hash.slice(7);
        var on = store.toggle(id);
        mr.setAttribute('aria-pressed', on ? 'true' : 'false');
        mr.textContent = on ? 'Marked revised' : 'Mark as revised';
      });
    }
    var tf = document.getElementById('topicFilter');
    if (tf) {
      tf.addEventListener('click', function (e) {
        var b = e.target.closest('.chip'); if (!b) { return; }
        var p = b.getAttribute('data-p');
        tf.querySelectorAll('.chip').forEach(function (c) { c.setAttribute('aria-pressed', String(c === b)); });
        document.querySelectorAll('#topicList .card').forEach(function (card) {
          card.style.display = (p === 'all' || card.getAttribute('data-prio') === p) ? '' : 'none';
        });
      });
    }
    var yf = document.getElementById('yearFilter');
    if (yf) {
      yf.addEventListener('click', function (e) {
        var b = e.target.closest('.chip'); if (!b) { return; }
        var y = b.getAttribute('data-year');
        yf.querySelectorAll('.chip').forEach(function (c) { c.setAttribute('aria-pressed', String(c === b)); });
        var i = 0;
        document.querySelectorAll('#pyqList .q').forEach(function (card) {
          var p = pyqs[i++]; if (!p) { return; }
          card.style.display = (y === 'all' || p.year === y) ? '' : 'none';
        });
      });
    }
  }

  window.addEventListener('hashchange', route);
  document.addEventListener('DOMContentLoaded', function () {
    var input = document.getElementById('searchInput');
    if (input) {
      input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { location.hash = '/search?q=' + encodeURIComponent(input.value.trim()); }
      });
    }
    var mb = document.getElementById('menuBtn');
    if (mb) { mb.addEventListener('click', function () { document.body.classList.toggle('nav-open'); }); }
    route();
  });
})();
