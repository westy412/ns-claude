# Style System: brand grounding, tokens, gradients, logo

The deck must look like it belongs to the client, not to a template. Ground the
brand in reality, then drive everything off CSS variables in `deck.css`.

## Ground the brand (never guess colours)

1. **Logo.** Get the client's real logo as SVG. Best sources, in order:
   their brand/press kit, an internal repo (`public/*logo*.svg`,
   `brand.config.*`), or the live site. Save **two variants** into
   `assets/img/`: a dark-on-light wordmark (`logo.svg`) and a
   light-on-dark wordmark (`logo-light.svg`). If only one exists, derive the
   other (recolour the wordmark fill to `#fff`).
2. **Colours.** Pull exact hex values, not approximations. The live site's
   design-token JSON or computed styles are ground truth. You need: a primary
   ink/brand-dark, a primary accent, a secondary, a warm accent, and any
   gradient stops. If the site is JS-rendered or bot-protected and the static
   HTML hides them, check an internal `brand.config`/theme file instead.
3. **Font.** Use the client's face if freely licensable; otherwise the closest
   free humanist sans (Hanken Grotesk, Inter) loaded from Google Fonts.

## The token block

`deck.css` opens with a `:root` you edit per client. Keep the **names**; change
the **values**. The archetype CSS references these names, so the deck rebrands by
editing this block alone.

```css
:root {
  /* ---- CLIENT BRAND: replace these per client ---- */
  --navy:      #000050;  /* primary ink / brand dark (headlines, text)   */
  --blue:      #0c2577;  /* secondary brand colour (the "ink" gradient)  */
  --teal:      #005966;  /* primary accent / CTA                         */
  --teal-deep: #003a42;  /* accent hover/depth                           */
  --coral:     #ff9e8c;  /* warm accent                                  */
  --coral-deep:#e3705a;  /* warm accent that holds on a light bg         */
  --amber:     #f5a623;  /* attention / "flag" in notes                 */
  --grad: linear-gradient(152deg,#c3e0d6 0%,#d9e2dc 38%,#ece4db 60%,#f7d2c5 100%);
  /* the saturated brand-colour gradient for dark "ink" slides           */
  --grad-ink:
    radial-gradient(95% 95% at 85% 115%, rgba(0,129,148,.40) 0%, transparent 55%),
    radial-gradient(125% 130% at 12% -10%, #1a3aae 0%, var(--blue) 46%, #001A61 100%);
  /* ---- structural (rarely change) ---- */
  --paper:#fff; --paper-2:#f5f7fa; --paper-3:#f1f4f8;
  --border:#d6dbe6; --line:#e6e9f0; --muted:#4e5463; --muted-2:#6c7284;
  --navy-soft:#1b2150;
  --radius:20px; --radius-sm:14px;
  --shadow-card:0 18px 50px -28px rgba(0,0,80,.28);
  --ease:cubic-bezier(.22,.61,.36,1);
  --font:"Hanken Grotesk","Helvetica Neue",Arial,system-ui,sans-serif;
  --deck-pad:clamp(2rem,5.5vw,6rem); --slide-fade:.5s var(--ease);
}
```

## Two gradients, two jobs

- `--grad` — the **signature soft gradient**. Used on `section` slides (cover,
  the four-worlds grid, the path, sometimes the close). Light; navy text + the
  navy logo sit on it.
- `--grad-ink` — the **saturated brand-colour gradient** for `.ink` slides
  (the moment, the bet, proof, close). Dark; white text + the light logo.
  This is the colour that makes the deck feel owned by the brand — build it
  from the client's primary brand colour, not a generic navy.

Aim for ~3 signature-gradient slides and ~4 ink slides across ~14; the rest are
white/tinted so the colour lands when it appears.

## Logo swap by slide

Put both logos in the top bar; CSS shows the right one for the slide's
background. `deck.js` toggles `.deck.on-ink` on dark slides.

```html
<span class="brand">
  <img class="brand-logo on-light" src="assets/img/logo.svg" alt="Client">
  <img class="brand-logo on-dark"  src="assets/img/logo-light.svg" alt="Client">
</span>
```

```css
.brand-logo.on-dark { display:none; }
.deck.on-ink .brand-logo.on-light { display:none; }
.deck.on-ink .brand-logo.on-dark  { display:block; }
```

## A brand-mark fallback

If you genuinely cannot obtain a wordmark, a clean fallback is a small
gradient ring built from the brand gradient stops, beside a text wordmark:

```html
<svg viewBox="0 0 24 24" style="width:1.3em;height:1.3em">
  <defs><linearGradient id="bg" x1="100%" y1="0" x2="0" y2="100%">
    <stop offset="0%" stop-color="#FF9E8C"/><stop offset="50%" stop-color="#F0F0E7"/>
    <stop offset="100%" stop-color="#29D3DF"/></linearGradient></defs>
  <circle cx="12" cy="12" r="10.5" fill="none" stroke="url(#bg)" stroke-width="3"/>
</svg>
```

Prefer the real logo. The ring is a last resort.
