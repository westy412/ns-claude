/* =========================================================================
   NovoSapien pitch deck - slide controller (client-agnostic).
   One slide at a time; live brand diagrams are mounted only on the visible
   slide (and disposed on leave) so just one animation runs at once. Reuses
   window.TJVisuals (mountAll / disposeAll) from ../assets/js/visuals-core.js.
   ========================================================================= */
(function () {
  'use strict';

  const deck     = document.getElementById('deck');
  const slides   = Array.from(deck.querySelectorAll('.slide'));
  const counter  = document.getElementById('counter');
  const progress = document.getElementById('progress');
  const scrub    = document.getElementById('scrub');
  const prevBtn  = document.getElementById('prev');
  const nextBtn  = document.getElementById('next');
  const notes    = document.getElementById('notes');
  const notesBody= document.getElementById('notesBody');
  const notesLabel=document.getElementById('notesLabel');
  const TJV      = window.TJVisuals;
  const N        = slides.length;

  const pad = n => String(n + 1).padStart(2, '0');

  // build progress dots
  slides.forEach((_, i) => {
    const b = document.createElement('button');
    b.className = 'dot';
    b.type = 'button';
    b.setAttribute('aria-label', 'Go to slide ' + (i + 1));
    b.addEventListener('click', () => go(i));
    progress.appendChild(b);
  });
  const dots = Array.from(progress.children);

  let current = -1;

  function go(i) {
    i = Math.max(0, Math.min(N - 1, i));
    if (i === current) return;

    // tear down the outgoing slide's animations (only the active one is ever mounted)
    if (TJV) TJV.disposeAll();

    slides.forEach((s, k) => s.classList.toggle('active', k === i));
    current = i;
    const slide = slides[i];

    // mount this slide's diagrams once it's the visible (laid-out) slide
    if (TJV) requestAnimationFrame(() => { if (current === i) TJV.mountAll(slide); });

    // chrome
    counter.textContent = pad(i) + ' / ' + N;
    dots.forEach((d, k) => d.classList.toggle('on', k === i));
    scrub.style.width = (((i + 1) / N) * 100) + '%';
    prevBtn.disabled = i === 0;
    nextBtn.disabled = i === N - 1;

    // flip the top/bottom bar for dark slides
    const onInk = slide.classList.contains('ink');
    deck.classList.toggle('on-ink', onInk);
    scrub.classList.toggle('on-ink', onInk);

    // speaker notes for this slide (cue card for the presenter)
    const note = slide.querySelector('.snote');
    notesBody.innerHTML = note ? note.innerHTML : '<ul class="cue"><li>No notes for this slide.</li></ul>';
    const h = slide.querySelector('h1');
    notesLabel.textContent = h ? ('Slide ' + (i + 1) + ' - ' + h.textContent.trim()) : ('Slide ' + (i + 1));

    if (history.replaceState) history.replaceState(null, '', '#' + (i + 1));
  }

  const next = () => go(current + 1);
  const prev = () => go(current - 1);

  nextBtn.addEventListener('click', next);
  prevBtn.addEventListener('click', prev);

  // ------- keyboard -------
  document.addEventListener('keydown', e => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    switch (e.key) {
      case 'ArrowRight': case 'PageDown': case ' ': case 'l':
        e.preventDefault(); next(); break;
      case 'ArrowLeft': case 'PageUp': case 'h':
        e.preventDefault(); prev(); break;
      case 'Home': e.preventDefault(); go(0); break;
      case 'End':  e.preventDefault(); go(N - 1); break;
      case 'n': case 'N': case 's': case 'S':
        notes.classList.toggle('show'); break;
      case 'f': case 'F':
        if (!document.fullscreenElement) document.documentElement.requestFullscreen && document.documentElement.requestFullscreen();
        else document.exitFullscreen && document.exitFullscreen();
        break;
      case 'Escape':
        notes.classList.remove('show'); break;
    }
  });

  // ------- touch swipe -------
  let tx = 0, ty = 0;
  deck.addEventListener('touchstart', e => { tx = e.changedTouches[0].clientX; ty = e.changedTouches[0].clientY; }, { passive: true });
  deck.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - tx;
    const dy = e.changedTouches[0].clientY - ty;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) (dx < 0 ? next : prev)();
  }, { passive: true });

  // ------- start (honour a #n deep link) -------
  const fromHash = parseInt((location.hash || '').replace('#', ''), 10);
  go(Number.isFinite(fromHash) && fromHash >= 1 ? fromHash - 1 : 0);

  window.addEventListener('hashchange', () => {
    const h = parseInt((location.hash || '').replace('#', ''), 10);
    if (Number.isFinite(h) && h - 1 !== current) go(h - 1);
  });
})();
