# Layout Archetypes

Every slide gets ONE archetype. **Never put two of the same back-to-back.** All
the CSS lives in `deck.css`; here is when to use each and its markup. Put the
archetype class on the `<section class="slide ...">`. Surfaces: add `section`
(signature gradient), `ink` (brand-colour dark), or `tint` (light grey); plain =
white.

A slide shell:
```html
<section class="slide ARCHETYPE [section|ink|tint]">
  <div class="slide-inner"> ...content... </div>
  <div class="snote" hidden><ul class="cue"><li>presenter notes</li></ul></div>
</section>
```

## cover
Opening. Brand framing + one line. `section` (gradient).
```html
<div class="slide-inner">
  <span class="eyebrow">A proposal to [Audience]</span>
  <h1>[The one-line framing].</h1>
  <p class="sub">[Sub-tagline].</p>
  <div class="credit"><span>[Client]</span><span class="dot"></span><span>[Date]</span></div>
</div>
```

## statement
One huge line. The moment / the bet / the close. Often `ink`. Add `center` to centre.
```html
<div class="slide-inner"><span class="eyebrow">The moment</span>
  <h1>[Big claim in one line.]</h1><p class="sub">[One supporting line.]</p></div>
```

## stat (stat-contrast)
Two big numbers with a verdict. The problem slide loves this.
```html
<span class="eyebrow accent-coral">Where we stand</span><h1>[claim]</h1>
<div class="statrow stagger">
  <div class="statcol them"><div class="num">44M</div><div class="lab">[them]</div></div>
  <div class="statvs">vs</div>
  <div class="statcol us"><div class="num">6M</div><div class="lab">[us]</div></div>
</div>
<p class="verdict">[one-line verdict].</p>
```

## transform (from → to)
The bet's "old constraint → new constraint". Usually `ink`.
```html
<div class="tpair stagger">
  <div class="tpanel from"><div class="lbl">Was</div><div class="big">[before]</div></div>
  <div class="tarrow">&rarr;</div>
  <div class="tpanel to"><div class="lbl">Now</div><div class="big">[after]</div></div>
</div>
```

## dhero (diagram-hero)
The animation IS the slide. The outcome/flywheel beat. Centre, big diagram.
```html
<div class="slide-inner"><span class="eyebrow accent">The outcome</span>
  <h1>[claim]</h1>
  <div class="viz"><div class="module-slot" data-visual="ID"></div></div>
  <p class="cap">[one caption line].</p></div>
```

## grid (N-worlds)
The solution map: N cards. Reuses `.regions/.region-card`. `section` or `tint`.
```html
<div class="regions stagger">
  <div class="region-card supply"><span class="kicker">Supply</span><h3>[name]</h3><p class="one">[one line]</p></div>
  ... demand / engine / workforce (rails: supply teal, demand coral, engine navy, workforce blue)
</div>
```

## flank  (the workhorse for "a world" slides)
Diagram centred, ~3 concise points either side. Add `featured` to get a chip
strip ("full surface") underneath. Set `--accent` per slide for the markers.
```html
<section class="slide flank featured">
 <div class="slide-inner" style="--accent: var(--coral-deep)">
  <div class="head"><span class="eyebrow accent-coral">Demand</span><h1>[claim]</h1></div>
  <ul class="fpoints col-l"><li>[point]</li><li>[point]</li><li>[point]</li></ul>
  <div class="viz"><div class="module-slot" data-visual="ID"></div></div>
  <ul class="fpoints col-r"><li>[point]</li><li>[point]</li><li>[point]</li></ul>
  <div class="fset"><span class="lbl">The full surface</span>
    <span class="chip soc">[highlighted item]</span><span class="chip">[item]</span> ...
  </div>
 </div>
</section>
```
`.chip.soc` = highlighted (the standout / "social" features). A flank point may
use `<span class="chan">web, mobile, WhatsApp, voice</span>` for accent-coloured runs.

## wfmenu (capability menu — "go broad")
When a slide must show BREADTH (a whole team / feature set), not depth. A signal
banner + 3 columns of named items + an optional hub graphic with animated wires.
```html
<div class="head"><span class="eyebrow">[area]</span><h1>[claim]</h1></div>
<div class="signal"><span class="slbl">[hero idea] &rarr; three plays:</span>
  <span class="play"><b>[trigger]?</b> [play].</span> ...</div>
<div class="wftop"><span class="wfhub">[Hub label]</span>
  <svg class="wfwires" preserveAspectRatio="none">
    <line class="w1" x1="50%" y1="0" x2="17%" y2="100%"/>
    <line class="w2" x1="50%" y1="0" x2="50%" y2="100%"/>
    <line class="w3" x1="50%" y1="0" x2="83%" y2="100%"/></svg></div>
<div class="cols">
  <div class="oscard nb"><span class="kicker">[col]</span><h3>[title]</h3>
    <div class="agents"><div class="agent"><b>[Name]:</b> [short role]</div> ...</div></div>
  ... .am (coral) / .mk (blue)
</div>
```

## proof
Big quote + validation chips + a punch line. Usually `ink`.
```html
<span class="eyebrow">The proof</span>
<p class="bigquote">"[short quote] <span class="accent">[emphasis]</span>"</p>
<p class="qattr">[attribution].</p>
<div class="validrow stagger">
  <div class="vchip"><div class="who">[Name]</div><div class="what">[what they prove]</div></div> ...
</div>
<p class="punch">[the takeaway] <span class="accent">[the edge]</span></p>
```

## steps
Horizontal numbered path. The "how, safely" slide. `tint` or `section`.
```html
<div class="steprow stagger">
  <div class="step s1"><div class="n">Step 1</div><div class="t">[title]</div><div class="d">[one line]</div></div>
  ... s2 / s3
</div>
```

## Entrance animation
Add `stagger` to a row container (`.statrow`, `.regions`, `.steprow`,
`.validrow`, `.tpair`, `.cols`) to make its children rise in sequence. The whole
`.slide-inner` already rises on activation.
