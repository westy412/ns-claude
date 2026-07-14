/* =========================================================================
   Visual mount system — shared core (classic script, loads before everything).
   Domain visual files register builders:
       window.TJVisuals.registry['<componentId>'] = (el) => disposeFn;
   map.js calls TJVisuals.mountAll(root) when a modal opens, disposeAll() on close.

   Shared chrome (used by every builder, opt-in):
       TJVisuals.addSubtitle(el)        — hoist the figure's <figcaption> up under
                                          the diagram title as a .viz-sub line.
       TJVisuals.makeClock(el, opts)    — pausable wait() clock + hover-to-pause +
                                          play/pause control. Drop-in for each
                                          builder's local stopped/timers/wait.
   ========================================================================= */
window.TJVisuals = (function () {
  const registry = {};
  const active = [];
  return {
    registry,
    has(id) { return !!registry[id]; },
    mountAll(root) {
      if (!root) return;
      root.querySelectorAll('.module-slot[data-visual]').forEach(el => {
        const id = el.dataset.visual;
        if (registry[id]) {
          try { const d = registry[id](el); if (d) active.push(d); }
          catch (e) { console.warn('visual failed:', id, e); }
        }
      });
    },
    disposeAll() { active.splice(0).forEach(fn => { try { fn(); } catch (e) {} }); },
  };
})();

/* --- shared chrome styles (subtitle + pause control), injected once --- */
(function () {
  if (document.getElementById('viz-shared-css')) return;
  const st = document.createElement('style');
  st.id = 'viz-shared-css';
  st.textContent = `
    .viz-sub { font-size:.82rem; line-height:1.45; color:var(--muted-2); margin:-.15rem 0 .1rem; max-width:64ch; }
    .comp-fig figcaption.viz-cap-hoisted { display:none; }
    .module-slot.viz-clocked { position:relative; }
    .viz-ctrl { position:absolute; top:8px; right:8px; z-index:5; width:26px; height:26px; padding:0;
      border:1px solid var(--line); border-radius:50%; background:#fff; color:var(--muted-2); cursor:pointer;
      display:flex; align-items:center; justify-content:center; opacity:.5;
      transition:opacity .2s var(--ease), color .2s var(--ease), border-color .2s var(--ease); }
    .viz-ctrl:hover { opacity:1; color:var(--navy); border-color:var(--navy); }
    .module-slot.viz-clocked:hover .viz-ctrl, .module-slot.viz-paused .viz-ctrl { opacity:1; }
    .viz-ptag { position:absolute; top:12px; right:40px; z-index:5; font-size:.58rem; font-weight:700;
      letter-spacing:.1em; text-transform:uppercase; color:var(--muted-2); opacity:0; pointer-events:none;
      transition:opacity .2s var(--ease); }
    .module-slot.viz-paused .viz-ptag { opacity:.85; }
    .viz-ctrl .ic-pause, .viz-ctrl .ic-play { display:none; }
    .viz-ctrl .ic-pause { width:8px; height:9px; border-left:2.5px solid currentColor; border-right:2.5px solid currentColor; }
    .viz-ctrl .ic-play { width:0; height:0; margin-left:2px;
      border-left:8px solid currentColor; border-top:5px solid transparent; border-bottom:5px solid transparent; }
    .module-slot.viz-clocked:not(.viz-paused) .viz-ctrl .ic-pause { display:block; }
    .module-slot.viz-paused .viz-ctrl .ic-play { display:block; }
  `;
  document.head.appendChild(st);
})();

/* Hoist the figure's <figcaption> up under the diagram title as a subtitle.
   No-op when the slot is not inside a <figure> with a caption. Call once,
   after the builder has set el.innerHTML (so el.firstElementChild is the title). */
window.TJVisuals.addSubtitle = function (el) {
  const fig = el.closest('figure');
  const cap = fig && fig.querySelector('figcaption');
  if (!cap || el.querySelector('.viz-sub')) return;
  const text = cap.textContent.trim();
  if (!text) return;
  const sub = document.createElement('div');
  sub.className = 'viz-sub';
  sub.textContent = text;
  const title = el.firstElementChild;            // the *-title div
  if (title) title.insertAdjacentElement('afterend', sub);
  else el.insertBefore(sub, el.firstChild);
  cap.classList.add('viz-cap-hoisted');          // hide the now-duplicated bottom caption
};

/* Pausable clock: a drop-in replacement for a builder's local
   `let stopped; const timers=[]; const wait=…; return dispose`.
   Usage:
     const clk = TJVisuals.makeClock(el, { pace: 1.3, controls: !reduce });
     const wait = clk.wait;
     … await wait(800); if (clk.stopped) return; …
     return function dispose(){ clk.dispose(); el.classList.remove('jp-diagram'); };
   opts.pace      — multiplier on every wait(ms) (1 = normal, >1 = slower).
   opts.controls  — inject the play/pause button (default true).
   opts.hoverPause— also pause while the pointer is over the diagram (default
                    false; it reads as "broken" because looking at a diagram
                    means hovering it, so the button is the primary control). */
window.TJVisuals.makeClock = function (el, opts) {
  opts = opts || {};
  const pace = opts.pace || 1;
  const now = () => (window.performance && window.performance.now) ? window.performance.now() : Date.now();
  const waits = new Set();
  let stopped = false;
  let hovered = false;
  let pinned = false;                // sticky pause toggled by the button; hover stays live alongside it
  let paused = false;
  let btn = null;

  const effPaused = () => hovered || pinned;

  function sync() {
    const want = effPaused();
    if (want === paused) return;
    paused = want;
    const t = now();
    if (paused) {
      waits.forEach(w => {
        if (w.timer) { clearTimeout(w.timer); w.timer = null; }
        w.remaining = Math.max(0, w.remaining - (t - w.startedAt));
      });
    } else {
      waits.forEach(w => {
        w.startedAt = t;
        w.timer = setTimeout(() => { waits.delete(w); w.resolve(); }, w.remaining);
      });
    }
    el.classList.toggle('viz-paused', paused);
  }

  function wait(ms) {
    if (stopped) return Promise.resolve();
    return new Promise(resolve => {
      const w = { remaining: ms * pace, startedAt: now(), timer: null, resolve };
      waits.add(w);
      if (!paused) w.timer = setTimeout(() => { waits.delete(w); resolve(); }, w.remaining);
    });
  }

  const onEnter = () => { hovered = true; sync(); };
  const onLeave = () => { hovered = false; sync(); };

  const hoverPause = !!opts.hoverPause;
  let ptag = null;
  if (opts.controls !== false) {
    el.classList.add('viz-clocked');
    if (hoverPause) {
      el.addEventListener('mouseenter', onEnter);
      el.addEventListener('mouseleave', onLeave);
    }
    ptag = document.createElement('span');     // explicit "paused" signal so a hover-pause never reads as broken
    ptag.className = 'viz-ptag';
    ptag.textContent = 'paused';
    el.appendChild(ptag);
    btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'viz-ctrl';
    btn.setAttribute('aria-label', 'Pause or resume the animation');
    btn.innerHTML = '<span class="ic-pause"></span><span class="ic-play"></span>';
    btn.addEventListener('click', e => {
      e.stopPropagation();
      pinned = !effPaused();   // running -> pin paused; paused -> release the pin (hover still applies)
      sync();
    });
    el.appendChild(btn);
  }

  return {
    wait,
    get stopped() { return stopped; },
    dispose() {
      stopped = true;
      waits.forEach(w => { if (w.timer) clearTimeout(w.timer); });
      waits.clear();
      el.removeEventListener('mouseenter', onEnter);
      el.removeEventListener('mouseleave', onLeave);
      if (btn && btn.parentNode) btn.parentNode.removeChild(btn);
      if (ptag && ptag.parentNode) ptag.parentNode.removeChild(ptag);
      el.classList.remove('viz-clocked', 'viz-paused');
    },
  };
};

/* Content store — domain content files add entries:
   window.TJContent['<componentId>'] = { h, e, body }  (headline, essence, detail HTML) */
window.TJContent = window.TJContent || {};
