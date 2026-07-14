# Animated Diagrams

The diagrams are what make the deck feel alive and bespoke. They are
self-contained, on-brand, pausable, and mounted only on the visible slide.

## How the system fits together

- `visuals-core.js` (copy verbatim) provides a tiny registry + `makeClock`
  (a pausable timer with hover-to-pause and a play/pause button).
- Each diagram file registers a builder:
  `window.TJVisuals.registry['ID'] = (el) => disposeFn`.
- A slide hosts a diagram with an empty slot:
  `<div class="module-slot" data-visual="ID"></div>`.
- `deck.js` mounts the **current slide's** slots on navigation and disposes the
  previous slide's, so only one animation runs at a time:
  ```js
  TJV.disposeAll();
  requestAnimationFrame(() => TJV.mountAll(currentSlide));
  ```
- Include the diagram files before `deck.js` in `index.html`.

## Building a diagram (clone `example-diagram.js`)

Each builder:
1. injects its **scoped** `<style>` once (unique class prefix, so diagrams never
   collide), keyed by an `id` you check with `getElementById`;
2. sets `el.innerHTML` (a title via `.dgm-title` + the diagram DOM);
3. gets a clock: `const clk = TJVisuals.makeClock(el, {pace:1.3, controls:!reduce, hoverPause:!reduce})`;
4. runs an async `loop()` using `await clk.wait(ms)` and bailing on `clk.stopped`;
5. returns a `dispose()` that calls `clk.dispose()`.

```js
window.TJVisuals.registry['ID'] = function (el) {
  el.classList.add('xx-diagram');
  el.innerHTML = '<div class="dgm-title">[Title]</div>' + /* ...diagram... */ '';
  const clk = window.TJVisuals.makeClock(el, { pace: 1.3, controls: !reduce, hoverPause: !reduce });
  const wait = clk.wait;
  if (reduce) { /* render the final static state, then return */ return () => {}; }
  (async function loop(){
    while (!clk.stopped) {
      /* ...reveal beats... */ await wait(900); if (clk.stopped) return;
    }
  })();
  return function dispose(){ clk.dispose(); el.classList.remove('xx-diagram'); };
};
```

## Design rules

- **On-brand:** use the brand CSS variables (`var(--teal)`, `var(--coral-deep)`,
  `var(--navy)`, `var(--amber)`). No off-palette colours.
- **Labelled and concrete:** real role names, real numbers ("~300 calls in 5
  min", "92% fit"), a clear left-to-right or round flow. A diagram a CEO can read
  in 3 seconds beats a clever abstract one.
- **DOM / CSS / SVG only.** No WebGL, no heavy libraries. Keep it light.
- **Pausable:** always pass `controls` and `hoverPause`. The presenter can stop a
  diagram mid-beat to talk over it.
- **Reduced motion:** every builder must render a sensible static end-state when
  `prefers-reduced-motion` is set (the `reduce` branch).
- **One idea per diagram.** If it needs a legend paragraph, it's doing too much.

## Where diagrams go (and don't)

- **No diagrams on the opening slides** (cover, the moment, the problem, the
  bet). Earn the attention first; introduce the first animation at the outcome.
- **dhero** = the diagram is the whole slide (the flywheel / the big idea).
- **flank** = a supporting diagram centred between two columns of points.
- **wfmenu** = usually a built graphic (the hub + animated wires), not a JS
  diagram, when the job is breadth.
- Reuse one diagram per domain; 5–6 diagrams across a 14-slide deck is plenty.
  Too many and they stop feeling special.

## Common diagram shapes that work

- **Flywheel / loop** ring that lights beat-by-beat, then resolves into the 2–3
  outcomes (great for the "it compounds" slide).
- **Chat / conversation** that streams messages (give it a FIXED-SIZE window
  with `overflow:hidden` so streaming bubbles fill from the bottom and clip off
  the top, instead of growing and pushing the layout).
- **Score with reasons** (a big % counting up, then reasons that trace to fields).
- **Market / order-book** (a posting, bids arriving, one clearing, settlement).
- **Hub + wires** (an orchestrator dispatching down animated connector lines to
  lanes — pure CSS/SVG, see `wfmenu` in the layout archetypes).
