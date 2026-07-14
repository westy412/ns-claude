/* =========================================================================
   EXAMPLE DIAGRAM — clone this per client/idea.
   Pattern: inject scoped <style> once -> register a builder on TJVisuals
   -> makeClock for pausability -> async loop with reduced-motion fallback.
   Put one or more of these in a `visuals/` folder and include them in
   index.html BEFORE deck.js. Host with: <div class="module-slot" data-visual="ID">.
   Rules: on-brand (use var(--teal)/--coral-deep/--navy/--amber), labelled,
   concrete numbers, DOM/CSS/SVG only, ALWAYS pausable, ALWAYS a static fallback.
   ========================================================================= */
(function () {
  'use strict';
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 1) scoped styles, injected once. Use a UNIQUE class prefix (ex-) so
        diagrams never collide. Shared chrome (title, pause button) is handled
        by visuals-core.js. */
  if (!document.getElementById('viz-example-css')) {
    const st = document.createElement('style');
    st.id = 'viz-example-css';
    st.textContent = `
      .module-slot.ex-diagram{padding:1.1rem 1.2rem;border:1px solid var(--line);background:#fff;
        display:flex;flex-direction:column;gap:.75rem;min-height:360px;justify-content:center;text-align:left;}
      .ex-dgm-title{font-weight:700;font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted-2);}
      .ex-ring{position:relative;aspect-ratio:1;max-width:230px;margin:.2rem auto;}
      .ex-ring svg{width:100%;height:100%;}
      .ex-track{fill:none;stroke:var(--line);stroke-width:6;}
      .ex-prog{fill:none;stroke:var(--teal);stroke-width:6;stroke-linecap:round;transition:stroke-dashoffset .5s linear;}
      .ex-node{position:absolute;transform:translate(-50%,-50%);font-size:.62rem;font-weight:700;color:var(--muted-2);
        background:var(--paper-2);border:1px solid var(--line);border-radius:20px;padding:.18rem .5rem;white-space:nowrap;transition:all .3s var(--ease);}
      .ex-node.on{color:#fff;background:var(--teal);border-color:var(--teal);}
      .ex-outs{display:flex;gap:.5rem;justify-content:center;}
      .ex-out{flex:1;max-width:33%;border:1px solid var(--line);border-left:3px solid var(--amber);border-radius:0 8px 8px 0;
        padding:.4rem .55rem;font-size:.7rem;font-weight:600;color:var(--navy);opacity:0;transform:translateY(6px);transition:all .4s var(--ease);}
      .ex-out.show{opacity:1;transform:none;} .ex-out small{display:block;color:var(--muted-2);font-weight:500;}
    `;
    document.head.appendChild(st);
  }

  /* 2) register the builder. Use registry.ID for a hero, registry['ID-sub'] for a sub-diagram. */
  window.TJVisuals.registry['example'] = function (el) {
    el.classList.add('ex-diagram');
    const labels = ['[Step 1]', '[Step 2]', '[Step 3]', '[Step 4]'];          // EDIT per client
    const outs = [{ t: '[Outcome A]', s: '[why]' }, { t: '[Outcome B]', s: '[why]' }, { t: '[Outcome C]', s: '[why]' }];
    const R = 78, C = 2 * Math.PI * R;
    el.innerHTML =
      '<div class="ex-dgm-title">[Diagram title]</div>' +
      '<div class="ex-ring"><svg viewBox="0 0 200 200">' +
        '<circle class="ex-track" cx="100" cy="100" r="' + R + '"></circle>' +
        '<circle class="ex-prog" cx="100" cy="100" r="' + R + '" transform="rotate(-90 100 100)" ' +
          'stroke-dasharray="' + C.toFixed(1) + '" stroke-dashoffset="' + C.toFixed(1) + '"></circle>' +
        '</svg>' + labels.map(() => '<span class="ex-node"></span>').join('') + '</div>' +
      '<div class="ex-outs">' + outs.map(o => '<div class="ex-out">' + o.t + '<small>' + o.s + '</small></div>').join('') + '</div>';

    window.TJVisuals.addSubtitle && window.TJVisuals.addSubtitle(el);   // hoists a <figcaption> if present

    const prog = el.querySelector('.ex-prog');
    const nodes = Array.from(el.querySelectorAll('.ex-node'));
    const outEls = Array.from(el.querySelectorAll('.ex-out'));
    nodes.forEach((n, i) => {                                          // lay nodes round the ring
      n.textContent = labels[i];
      const a = (-90 + i * (360 / labels.length)) * Math.PI / 180;
      n.style.left = (50 + 50 * Math.cos(a)) + '%';
      n.style.top  = (50 + 50 * Math.sin(a)) + '%';
    });

    /* 3) the clock makes it pausable (hover + button) and reduced-motion aware. */
    const clk = window.TJVisuals.makeClock(el, { pace: 1.3, controls: !reduce, hoverPause: !reduce });
    const wait = clk.wait;

    if (reduce) {                                                      // 4) static end-state
      prog.style.strokeDashoffset = '0';
      nodes.forEach(n => n.classList.add('on'));
      outEls.forEach(o => o.classList.add('show'));
      return function dispose() { el.classList.remove('ex-diagram'); };
    }

    (async function loop() {                                           // 5) the animated beats
      while (!clk.stopped) {
        prog.style.transition = 'none'; prog.style.strokeDashoffset = C.toFixed(1);
        nodes.forEach(n => n.classList.remove('on')); outEls.forEach(o => o.classList.remove('show'));
        void el.offsetWidth; prog.style.transition = 'stroke-dashoffset .5s linear';
        await wait(700); if (clk.stopped) return;
        for (let i = 0; i < nodes.length && !clk.stopped; i++) {
          nodes[i].classList.add('on');
          prog.style.strokeDashoffset = (C * (1 - (i + 1) / nodes.length)).toFixed(1);
          await wait(820);
        }
        await wait(500); if (clk.stopped) return;
        for (let i = 0; i < outEls.length && !clk.stopped; i++) { outEls[i].classList.add('show'); await wait(520); }
        await wait(2600); if (clk.stopped) return;
      }
    })();

    return function dispose() { clk.dispose(); el.classList.remove('ex-diagram'); };
  };
})();
