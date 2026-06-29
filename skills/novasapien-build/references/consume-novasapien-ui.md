# Consume @novosapien/ui

The NovaSapien design system — the canonical brand theme + reusable UI, extracted
verbatim from `ns-content-workforce-app`. Three layers: the **theme** (a Tailwind
v4 CSS-var token contract = brand source of truth), the **components** (34
shadcn-style `ui/` primitives + `cn` + 9 generic `shared/` components), and a
headless **app shell** (sidebar / page-header). The style + components foundation
new internal tools start from; pairs with `@novosapien/nova-ui` under one
`@novosapien` consumer story.

- **Repo:** `Novosapien/ns-novosapien-ui` → GitHub Packages `@novosapien/ui`.
- **Versions:** `1.0.0` theme+primitives+shared · `1.1.0` added `/app-shell` ·
  **`1.1.1` = the Turbopack `theme.css` fix → use ≥ 1.1.1** (see `cross-cutting-rules.md` Rule 2).
- **Peer deps:** React `19`, react-dom, Tailwind `v4`, the **19** `@radix-ui/*`
  packages; **`next` is an *optional* peer** (only `/app-shell` uses it → the core
  stays pure-React). Direct deps: cva, clsx, tailwind-merge, `@hugeicons/*`,
  recharts, cmdk, sonner, react-day-picker, date-fns, tiptap, react-pdf,
  react-markdown + remark-breaks, turndown.

---

## 1. Install

Same `@novosapien` registry auth as nova-ui (`cross-cutting-rules.md` Rule 4 — one
`read:packages` scope covers both). Then `npm i @novosapien/ui` (pin `^1.1.1`).

---

## 2. CSS (Tailwind v4 entry — order matters)

```css
@import "tailwindcss";
@import "@novosapien/ui/theme.css";                       /* tokens + @theme ONLY */
@source "../node_modules/@novosapien/ui/dist/**/*.js";    /* consumer generates primitives' classes */
```

- `theme.css` ships **only** tokens + `@theme` (no global utilities/resets →
  additions-only, no host clobber).
- `@source` points at the **compiled dist JS** (where the class strings land, not
  the TSX source); path **relative to the CSS file**.
- Coexists cleanly with nova-ui's `@source` + `styles.css` + `--nova-*` (disjoint
  namespaces).
- Wire **Geist** consumer-side so `--font-geist-sans/mono` resolve; toggle dark
  via `html.dark`.

---

## 3. Theme / token contract (the brand source of truth)

Two layers in `theme.css`, mirroring the app's `globals.css`:

- **Layer 1 — semantic CSS vars as space-separated RGB channels** in `:root`
  (light) + `html.dark` (dark): `--primary: 161 188 209` (#A1BCD1),
  `--foreground`/`--primary-foreground` #09142F, `--card` #FBFCFD,
  `--background` #ECF2F6, plus muted/accent/destructive/success/warning/sidebar/
  popover/secondary, the **15-var badge palette**
  (`--badge-{success,warning,info,error,neutral}-{bg,text,border}` — shipped as
  `rgba()`/hex so dark-mode **translucency survives**; RGB channels can't carry
  alpha, see Rule 5), 5 `--chart-*`, shadows, `--radius`.
- **Layer 2 — `@theme inline`** maps channels → utilities
  (`--color-primary: rgb(var(--primary))` → `bg-primary`/`text-primary`/…).
- **`--completion` / `--completion-foreground`** — distinct "completed/published"
  semantic (emerald), alongside `--success`. This is the shared token nova-ui
  references to replace its hardcoded emerald todo color.

**Frozen contract (60 names).** The names are the public brand interface; single
source of truth = `TOKEN_CONTRACT` in `src/tokens.ts`; `scripts/check-tokens.mjs`
fails CI if any frozen name disappears. **Re-brand by overriding the CSS-var
*values*, never by forking primitives or renaming** — renames are breaking,
coordinated with nova-ui. `--primary` is **identical in light & dark** (brand
constancy — do not "fix" it). Full names: the repo's `docs/token-contract.md`.

Helpers via `@novosapien/ui/tokens`: `TOKEN_CONTRACT`, `TokenName`, `tokenVar`,
`tokenRgb`.

---

## 4. Components

```tsx
import { Button, Card, Table, Badge, cn } from '@novosapien/ui'           // primitives, pure-React
import { AppShell, PageHeader, Sidebar } from '@novosapien/ui/app-shell'  // Next-coupled
```

- **`.`** — `cn` + the **34 `ui/` primitives** + the **9 `shared/`**
  (EmptyState, SearchInput, ContextChip, Markdown, InlineMarkdown, RichTextEditor,
  PDFViewer, **DictationTextarea**, TextareaModal). Pure-React, no Next.
  - `DictationTextarea` / `TextareaModal` require a
    **`transcribe(blob) => Promise<string>`** prop — the package owns no
    `/api/transcribe`; wire it to your transcription route.
- **`./app-shell`** *(Next-coupled)* — `AppShell`, `Sidebar`, `MobileSidebar`,
  `MobileSidebarProvider`, `useMobileSidebar`, `useSidebarCollapsed`,
  `SwipeEdgeDetector`, `PageHeader`, `NavItem`. **Slot-based**:
  ```tsx
  <AppShell navItems={…} logo={…} userMenu={<YourAuthMenu/>} footer={…} mobileFooter={…}>
    {children}
  </AppShell>
  ```
  Uses `next/link` + `usePathname` (the optional `next` peer). Package owns
  structure + brand styling; the app supplies auth/routes via slots.
- **`./tokens`**, **`./theme.css`**, **`./docs/*`** (colour palette, styling
  rules, token contract markdown).

### House-style defaults — do NOT "normalize" them (Rule 7)

- The **`Button`** default variant is a **card surface** (`bg-card` + border,
  `hover:!border-primary`) — **NOT `bg-primary`**. Plus a `card` variant + an `md`
  size. A solid fill is a regression.
- **hugeicons only, zero lucide.**

### The nova-ui swap path

All 34 primitives are **byte-identical** to the app's (diff = import paths only).
The **5 swap-primitives — `Card`, `Table`, `Badge`, `Button`, `Skeleton`** — carry
a **frozen public API** (type-level `.d.ts` snapshot, `check-api.mjs`,
union-order-insensitive) and derive from the same shadcn/Radix baseline nova-ui
self-vendored → **nova-ui can later replace its vendored copies with
`@novosapien/ui` via a peer dep (a non-breaking one-line swap).** Caveat: nova-ui
defaults to **lucide**, `@novosapien/ui` is **hugeicons** — the 5 swap-primitives
are icon-agnostic (clean swap); broader adoption hits the icon-set difference
(align on hugeicons / inject).

---

## 5. ⚠️ The Turbopack theme.css bug (fixed in 1.1.1 — use ≥ 1.1.1)

Full story in `cross-cutting-rules.md` Rule 2. Short version: `theme.css`'s header
comment contained a `**/` (from a dist glob example), which closed the CSS comment
early → `CssSyntaxError` → **every Tailwind v4 page 500'd under `next dev`
(Turbopack)** while `next build --webpack` was green. **Pin `^1.1.1`.** When you
make any CSS change to a consumer, verify under **`next dev` (Turbopack)**, not
just `next build --webpack`.

---

## Status / pointers

Published `1.1.1`; app re-point verified working on `feature/novosapien-ui-repoint`
(stacked on nova-ui's `repoint-v2`) — theme + 34 primitives + 9 shared + `/app-shell`
adopted, `git diff` vs pre-verified state = 0. Remaining (non-code): visual QA →
merge to `dev`; deploy needs the `read:packages` token wired into CI.

In-repo depth: `Novosapien/ns-novosapien-ui` → `docs/{colours,styling,token-contract}.md`;
spec `specs/2026-06-25-novosapien-ui-component-library/`.
