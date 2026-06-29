# Cross-cutting rules for @novosapien packages

These apply to **every** integration of `@novosapien/nova-ui` and `@novosapien/ui`.
Each was learned by shipping the mistake. The two that broke the whole consuming
app are marked ⛔.

---

## ⛔ Rule 1 — Never ship/import a global utility stylesheet from a library

**The failure.** nova-ui v1's prebuilt `dist/styles.css` shipped **global,
unscoped Tailwind utilities** (`.flex`, `.border`, `.rounded-lg`, `.bg-card`,
`.p-4`, `.text-foreground`, …) plus a global `:root,:host{}`. Imported in the
app's root `layout.tsx`, those **duplicated and collided** with the app's own
Tailwind utilities → every page's spacing, borders, radii, and colors shifted
app-wide. All reviews + snapshot tests passed it (none rendered the consuming
app); only real-app manual QA caught it.

**The rule.** A library must not emit global utility classes to a Tailwind v4
consumer. Instead:

- The **consumer's** Tailwind generates the package's classes by adding the
  package dist as a source:
  ```css
  @source "<rel>/node_modules/@novosapien/nova-ui/dist";
  /* @novosapien/ui points at the compiled JS where class strings land: */
  @source "<rel>/node_modules/@novosapien/ui/dist/**/*.js";
  ```
  The `@source` path is **relative to the CSS file** (e.g. `src/app/globals.css`
  → `../../node_modules/...`).
- The package ships **only** CSS-var tokens + a **scoped** base reset
  (nova-ui: `.nova-ui-root`-scoped, inside `@layer base`; `@novosapien/ui`'s
  `theme.css`: tokens + `@theme` only, no preflight/utilities).

**The verification (do this, don't eyeball).** Compile the consumer's CSS **with
vs without** the package import → the diff must be **additions only; zero existing
rules change**. nova-ui 0.1.2 was proven this way (probe app: only +227B of
scoped base, 0 utility rules changed).

---

## ⛔ Rule 2 — A CSS file you only copy / read-as-text is never *validated*

**The failure.** `@novosapien/ui`'s `theme.css` header **comment** contained a
`@source ".../dist/**/*.js"` example. The `**/` embeds the sequence `*/`, which
**closed the CSS block comment early** → everything after parsed as raw CSS →
`CssSyntaxError: Unterminated string: ";"` at `theme.css:16`. Every Tailwind v4
consumer that did `@import "@novosapien/ui/theme.css"` failed to compile → **every
page 500'd**. It surfaced **only under `next dev` (Turbopack → `@tailwindcss/postcss`,
the strict parser)**; `next build --webpack` was GREEN (it tolerated it). The
package's own gates missed it because nothing ever CSS-*parsed* `theme.css` —
`tsup` only *copies* it and the token guard read it as *text*.

**The rules this burned in:**

- A shipped CSS file must be **compiled through the real engine in CI**
  (`@tailwindcss/cli`), not just copied or text-scanned. (`@novosapien/ui` added
  `scripts/check-theme.mjs` for exactly this.)
- A CSS **comment must never contain `*/`** — and a dist glob (`**/*.js`) does.
- Use **`@novosapien/ui ≥ 1.1.1`** (the version with the fix).

---

## ⛔ Rule 3 — Parity is only provable by running the real app under its real bundler

Code review passed. Snapshot tests passed. `next build --webpack` passed. The app
was still broken — twice (Rule 1's CSS collision, Rule 2's Turbopack parse error).

**Gate visual / integration parity on `next dev` (Turbopack / `@tailwindcss/postcss`)
in the actual consuming app** — not on a green build, not on code review. For a
verbatim extraction, also diff the extracted files vs source (import-paths-only)
and the re-pointed app vs its pre-point state (**empty diff** = provable zero
regression).

---

## Rule 4 — Settle distribution + auth early (one @novosapien story)

Private GitHub Packages. One `read:packages` scope covers **both**
`@novosapien/ui` and `@novosapien/nova-ui`.

**Committed `.npmrc`** (repo root):
```ini
@novosapien:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
always-auth=true
```

**Token wiring:**
- **Local dev:** `gh auth refresh -s read:packages` → `export NODE_AUTH_TOKEN=$(gh auth token)`.
- **CI (GitHub Actions):** a repo/Environment secret in `NODE_AUTH_TOKEN`.
- **Docker:** BuildKit `--mount=type=secret` — **never** bake the token into an
  `ENV`/`ARG` layer.

> The in-package `consume-nova-ui` guide shows an older `${GITHUB_TOKEN}` form
> without `always-auth`. **Prefer the `NODE_AUTH_TOKEN` + `always-auth=true` form
> above** — it's the canonical, CI/Docker-correct version.

**Dev fallback (not CI-installable):** a local tarball
(`"@novosapien/nova-ui": "file:../../nova-ui/novosapien-nova-ui-0.1.2.tgz"`) or a
git dep (`"github:Novosapien/nova-ui#<tag>"`). Fine for local QA; a branch using
either is **not pushable/deployable** until swapped to a registry range
(`"^0.1.2"`) with the auth above wired into CI.

---

## Rule 5 — RGB-channel tokens can't carry alpha

The token contracts store colors as **space-separated RGB channels**
(`--primary: 161 188 209`) so Tailwind can do `rgb(var(--primary))` →
`bg-primary`. But `rgb(var(--token))` **cannot** reproduce translucency
(`rgba(…, 0.3)`). Anything that needs alpha — generative status-badge fills,
`--sidebar-active` — must ship as **`rgba()` / hex / slash-alpha**
(`161 188 209 / 0.2`), not a bare channel triplet. Design the contract for this
up front if the brand uses translucent fills. (nova-ui's dark-mode badge is a
known solid-vs-translucent divergence because of this.)

---

## Rule 6 — Pin one icon set and make it injectable

`@novosapien/ui` is **hugeicons** (`@hugeicons/*`), zero lucide.
`@novosapien/nova-ui` **defaults to lucide** but accepts injected icons via
`<NovaChat icons={…} />`. To match an app exactly, inject your icon set. The 5
swap-primitives are icon-agnostic (clean swap), but broader primitive adoption
hits the set difference — align on hugeicons or inject.

---

## Rule 7 — Defaults must match the reference app

A drop-in replacement keeps the reference's **exact** defaults. "Reasonable but
different" is a regression. Concretely:

- The house-style **`Button`** default variant is a **card surface**
  (`bg-card` + border, `hover:!border-primary`) — **not** `bg-primary`. Do not
  "fix" it to a solid fill.
- Icons = hugeicons, not lucide (Rule 6).
- Token **values** rebrand the system; never fork primitives or rename tokens.

---

## The recurring meta-lesson

Two distinct surface bugs (composer slot, tool-call labels) and the CSS defect all
traced to the **same** root: a domain-free extraction that dropped an app-specific
behavior **without** adding a surface to restore it, and a "PASS" that was never
checked against the real running consumer. When extracting or consuming:
**strip → add an injection point (Rule 2 of SKILL.md) → verify in the real app
under Turbopack (Rule 3 here).**
